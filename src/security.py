"""Security hardening for hedera-realtime-charts."""

import os
import re
from typing import Optional, List
from functools import wraps
import logging

logger = logging.getLogger(__name__)


class SecurityConfig:
    """Security configuration for the application."""
    
    # WebSocket security
    MAX_WEBSOCKET_MESSAGE_SIZE = 1024 * 1024  # 1MB max message size
    MAX_WEBSOCKET_CONNECTIONS = 1000  # Max concurrent connections
    WEBSOCKET_RATE_LIMIT = 100  # Messages per second per connection
    
    # Data validation
    MAX_SYMBOL_LENGTH = 20
    ALLOWED_SYMBOLS_PATTERN = re.compile(r'^[A-Z]{2,20}USDT$')
    MAX_PRICE = 1_000_000_000  # 1 billion USD
    MIN_PRICE = 0.00000001  # 1 satoshi
    MAX_QUANTITY = 1_000_000_000  # 1 billion units
    MIN_QUANTITY = 0.00000001  # 1 satoshi
    
    # Rate limiting
    RATE_LIMIT_WINDOW = 60  # seconds
    RATE_LIMIT_MAX_REQUESTS = 1000  # requests per window
    
    @classmethod
    def validate_symbol(cls, symbol: str) -> bool:
        """Validate cryptocurrency symbol."""
        if not symbol:
            return False
        if len(symbol) > cls.MAX_SYMBOL_LENGTH:
            return False
        if not cls.ALLOWED_SYMBOLS_PATTERN.match(symbol):
            return False
        return True
    
    @classmethod
    def validate_price(cls, price: float) -> bool:
        """Validate price value."""
        if not isinstance(price, (int, float)):
            return False
        if price < cls.MIN_PRICE or price > cls.MAX_PRICE:
            return False
        if price != price:  # NaN check
            return False
        return True
    
    @classmethod
    def validate_quantity(cls, quantity: float) -> bool:
        """Validate quantity value."""
        if not isinstance(quantity, (int, float)):
            return False
        if quantity < cls.MIN_QUANTITY or quantity > cls.MAX_QUANTITY:
            return False
        if quantity != quantity:  # NaN check
            return False
        return True


class RateLimiter:
    """Simple rate limiter for API requests."""
    
    def __init__(self, max_requests: int = 1000, window: int = 60):
        self.max_requests = max_requests
        self.window = window
        self.requests = []
    
    def is_allowed(self) -> bool:
        """Check if request is allowed under rate limit."""
        import time
        now = time.time()
        
        # Remove old requests outside the window
        self.requests = [r for r in self.requests if now - r < self.window]
        
        # Check if under limit
        if len(self.requests) < self.max_requests:
            self.requests.append(now)
            return True
        
        return False
    
    def get_reset_time(self) -> float:
        """Get time until rate limit resets."""
        import time
        if not self.requests:
            return 0
        return self.requests[0] + self.window - time.time()


def sanitize_input(input_str: str, max_length: int = 1000) -> str:
    """Sanitize user input to prevent injection attacks."""
    if not input_str:
        return ""
    
    # Remove null bytes
    input_str = input_str.replace('\x00', '')
    
    # Truncate to max length
    input_str = input_str[:max_length]
    
    # Remove potential SQL injection patterns
    dangerous_patterns = [
        r';\s*drop',
        r';\s*delete',
        r';\s*insert',
        r';\s*update',
        r';\s*exec',
        r';\s*execute',
        r'<script',
        r'javascript:',
        r'onerror=',
        r'onload=',
    ]
    
    for pattern in dangerous_patterns:
        input_str = re.sub(pattern, '', input_str, flags=re.IGNORECASE)
    
    return input_str.strip()


def validate_websocket_message(message: dict) -> bool:
    """Validate WebSocket message structure."""
    if not isinstance(message, dict):
        return False
    
    # Check required fields
    required_fields = ['symbol', 'price']
    for field in required_fields:
        if field not in message:
            return False
    
    # Validate symbol
    if not SecurityConfig.validate_symbol(message['symbol']):
        return False
    
    # Validate price
    if not SecurityConfig.validate_price(message['price']):
        return False
    
    # Validate optional fields
    if 'quantity' in message:
        if not SecurityConfig.validate_quantity(message['quantity']):
            return False
    
    return True


def log_security_event(event_type: str, details: dict):
    """Log security-related events."""
    logger.warning(f"Security Event: {event_type} - {details}")


def rate_limit_decorator(max_requests: int = 100, window: int = 60):
    """Decorator for rate limiting function calls."""
    def decorator(func):
        rate_limiter = RateLimiter(max_requests, window)
        
        @wraps(func)
        async def wrapper(*args, **kwargs):
            if not rate_limiter.is_allowed():
                reset_time = rate_limiter.get_reset_time()
                raise Exception(f"Rate limit exceeded. Reset in {reset_time:.1f}s")
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator


# Environment variable validation
def validate_environment():
    """Validate required environment variables."""
    required_vars = []
    optional_vars = []
    
    missing_required = []
    for var in required_vars:
        if not os.environ.get(var):
            missing_required.append(var)
    
    if missing_required:
        raise ValueError(f"Missing required environment variables: {missing_required}")
    
    # Log optional vars
    for var in optional_vars:
        value = os.environ.get(var)
        if value:
            logger.info(f"{var} is set")


# Input validation for WebSocket connections
def validate_websocket_headers(headers: dict) -> bool:
    """Validate WebSocket connection headers."""
    # Check for suspicious headers
    suspicious_headers = [
        'x-forwarded-for',
        'x-real-ip',
        'via',
    ]
    
    for header in suspicious_headers:
        if header in headers:
            log_security_event('suspicious_header', {'header': header})
    
    return True
