"""CoinGecko API client with tier-based support.

Supports different CoinGecko API tiers:
- Free: 10-50 calls/minute, basic data
- Hobby: ~100 calls/minute, more data
- Pro: ~500 calls/minute, advanced features
- Pro+: ~1000+ calls/minute, full features
- Enterprise: Custom limits, all features
"""

import asyncio
import aiohttp
import logging
from dataclasses import dataclass
from enum import Enum
from typing import Optional, Dict, List, Any
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class CoinGeckoTier(Enum):
    """CoinGecko API tiers."""
    FREE = "free"
    HOBBY = "hobby"
    PRO = "pro"
    PRO_PLUS = "pro_plus"
    ENTERPRISE = "enterprise"


@dataclass
class CoinGeckoConfig:
    """CoinGecko API configuration."""
    api_key: Optional[str] = None
    tier: CoinGeckoTier = CoinGeckoTier.FREE
    base_url: str = "https://api.coingecko.com/api/v3"
    pro_base_url: str = "https://pro-api.coingecko.com/api/v3"
    rate_limit_calls: int = 50  # Default free tier
    rate_limit_period: int = 60  # seconds
    enable_cache: bool = True
    cache_ttl: int = 60  # seconds


class CoinGeckoClient:
    """CoinGecko API client with tier-based features and rate limiting."""
    
    def __init__(self, config: CoinGeckoConfig):
        """Initialize CoinGecko client.
        
        Args:
            config: CoinGecko configuration
        """
        self.config = config
        self.session: Optional[aiohttp.ClientSession] = None
        self.cache: Dict[str, tuple] = {}  # key -> (data, timestamp)
        self.call_count = 0
        self.last_call_time = None
        
        # Set rate limits based on tier
        self._set_tier_limits()
    
    def _set_tier_limits(self):
        """Set rate limits based on API tier."""
        tier_limits = {
            CoinGeckoTier.FREE: (50, 60),
            CoinGeckoTier.HOBBY: (100, 60),
            CoinGeckoTier.PRO: (500, 60),
            CoinGeckoTier.PRO_PLUS: (1000, 60),
            CoinGeckoTier.ENTERPRISE: (2000, 60),
        }
        
        if self.config.tier in tier_limits:
            self.config.rate_limit_calls, self.config.rate_limit_period = tier_limits[self.config.tier]
    
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    def _get_base_url(self):
        """Get base URL based on tier."""
        if self.config.tier in [CoinGeckoTier.PRO, CoinGeckoTier.PRO_PLUS, CoinGeckoTier.ENTERPRISE]:
            return self.config.pro_base_url
        return self.config.base_url
    
    def _get_headers(self):
        """Get headers for API request."""
        headers = {
            "Accept": "application/json",
            "User-Agent": "HederaRealtimeCharts/1.0",
        }
        
        # Add API key for paid tiers
        if self.config.api_key and self.config.tier != CoinGeckoTier.FREE:
            headers["x-cg-pro-api-key"] = self.config.api_key
        
        return headers
    
    async def _check_rate_limit(self):
        """Check and enforce rate limiting."""
        now = datetime.now()
        
        if self.last_call_time:
            time_since_last = (now - self.last_call_time).total_seconds()
            if time_since_last < (self.config.rate_limit_period / self.config.rate_limit_calls):
                sleep_time = (self.config.rate_limit_period / self.config.rate_limit_calls) - time_since_last
                await asyncio.sleep(sleep_time)
        
        self.last_call_time = now
        self.call_count += 1
    
    def _get_cache_key(self, endpoint: str, params: dict) -> str:
        """Generate cache key."""
        import json
        return f"{endpoint}:{json.dumps(sorted(params.items()))}"
    
    def _get_cached(self, key: str) -> Optional[Any]:
        """Get cached data if available and not expired."""
        if not self.config.enable_cache:
            return None
        
        if key in self.cache:
            data, timestamp = self.cache[key]
            if datetime.now() - timestamp < timedelta(seconds=self.config.cache_ttl):
                return data
            else:
                del self.cache[key]
        
        return None
    
    def _set_cache(self, key: str, data: Any):
        """Cache data."""
        if self.config.enable_cache:
            self.cache[key] = (data, datetime.now())
    
    async def _make_request(self, endpoint: str, params: dict = None) -> Dict:
        """Make API request with rate limiting and caching.
        
        Args:
            endpoint: API endpoint
            params: Query parameters
        
        Returns:
            JSON response data
        """
        params = params or {}
        
        # Check cache
        cache_key = self._get_cache_key(endpoint, params)
        cached = self._get_cached(cache_key)
        if cached is not None:
            logger.debug(f"Cache hit for {endpoint}")
            return cached
        
        # Check rate limit
        await self._check_rate_limit()
        
        # Make request
        url = f"{self._get_base_url()}{endpoint}"
        headers = self._get_headers()
        
        try:
            async with self.session.get(url, headers=headers, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    self._set_cache(cache_key, data)
                    return data
                elif response.status == 429:
                    logger.warning(f"Rate limit exceeded for {endpoint}")
                    await asyncio.sleep(5)
                    return await self._make_request(endpoint, params)
                else:
                    error_text = await response.text()
                    logger.error(f"API error {response.status}: {error_text}")
                    raise Exception(f"API error {response.status}: {error_text}")
        except Exception as e:
            logger.error(f"Request failed: {e}")
            raise
    
    async def get_price(self, coin_id: str, vs_currency: str = "usd") -> Dict:
        """Get current price for a cryptocurrency.
        
        Args:
            coin_id: Coin identifier (e.g., "bitcoin", "ethereum")
            vs_currency: Currency to convert to (default: "usd")
        
        Returns:
            Price data
        """
        endpoint = "/simple/price"
        params = {
            "ids": coin_id,
            "vs_currencies": vs_currency,
            "include_market_cap": "true",
            "include_24hr_vol": "true",
            "include_24hr_change": "true",
        }
        
        # Add advanced parameters for paid tiers
        if self.config.tier in [CoinGeckoTier.PRO, CoinGeckoTier.PRO_PLUS, CoinGeckoTier.ENTERPRISE]:
            params["include_last_updated_at"] = "true"
        
        return await self._make_request(endpoint, params)
    
    async def get_prices(self, coin_ids: List[str], vs_currency: str = "usd") -> Dict:
        """Get current prices for multiple cryptocurrencies.
        
        Args:
            coin_ids: List of coin identifiers
            vs_currency: Currency to convert to (default: "usd")
        
        Returns:
            Price data for all coins
        """
        endpoint = "/simple/price"
        params = {
            "ids": ",".join(coin_ids),
            "vs_currencies": vs_currency,
            "include_market_cap": "true",
            "include_24hr_vol": "true",
            "include_24hr_change": "true",
        }
        
        # Add advanced parameters for paid tiers
        if self.config.tier in [CoinGeckoTier.PRO, CoinGeckoTier.PRO_PLUS, CoinGeckoTier.ENTERPRISE]:
            params["include_last_updated_at"] = "true"
        
        return await self._make_request(endpoint, params)
    
    async def get_coin_list(self) -> List[Dict]:
        """Get list of all supported coins.
        
        Returns:
            List of coin data
        """
        endpoint = "/coins/list"
        return await self._make_request(endpoint)
    
    async def get_coin_market_data(
        self,
        coin_id: str,
        vs_currency: str = "usd",
        days: int = 1
    ) -> Dict:
        """Get market data for a coin.
        
        Args:
            coin_id: Coin identifier
            vs_currency: Currency to convert to (default: "usd")
            days: Number of days of data (1, 7, 30, etc.)
        
        Returns:
            Market data
        """
        endpoint = f"/coins/{coin_id}/market_chart"
        params = {
            "vs_currency": vs_currency,
            "days": days,
        }
        
        return await self._make_request(endpoint, params)
    
    async def get_top_coins(self, vs_currency: str = "usd", per_page: int = 50) -> List[Dict]:
        """Get top cryptocurrencies by market cap.
        
        Args:
            vs_currency: Currency to convert to (default: "usd")
            per_page: Number of coins per page (max 250 for free, higher for paid)
        
        Returns:
            List of coin data
        """
        endpoint = "/coins/markets"
        params = {
            "vs_currency": vs_currency,
            "order": "market_cap_desc",
            "per_page": min(per_page, 250 if self.config.tier == CoinGeckoTier.FREE else 500),
            "page": 1,
            "sparkline": "false",
        }
        
        # Add advanced parameters for paid tiers
        if self.config.tier in [CoinGeckoTier.PRO, CoinGeckoTier.PRO_PLUS, CoinGeckoTier.ENTERPRISE]:
            params["price_change_percentage"] = "1h,24h,7d"
        
        return await self._make_request(endpoint, params)
    
    async def get_global_data(self) -> Dict:
        """Get global cryptocurrency market data.
        
        Returns:
            Global market data
        """
        endpoint = "/global"
        return await self._make_request(endpoint)
    
    def get_tier_info(self) -> Dict:
        """Get information about current tier configuration.
        
        Returns:
            Tier information
        """
        return {
            "tier": self.config.tier.value,
            "rate_limit_calls": self.config.rate_limit_calls,
            "rate_limit_period": self.config.rate_limit_period,
            "api_key_configured": bool(self.config.api_key),
            "base_url": self._get_base_url(),
            "cache_enabled": self.config.enable_cache,
            "cache_ttl": self.config.cache_ttl,
        }
    
    def get_call_stats(self) -> Dict:
        """Get API call statistics.
        
        Returns:
            Call statistics
        """
        return {
            "total_calls": self.call_count,
            "cache_size": len(self.cache),
        }
