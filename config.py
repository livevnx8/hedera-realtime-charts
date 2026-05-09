"""Configuration file for hedera-realtime-charts.

This file contains all configurable parameters for the real-time crypto charting system.
Modify these settings to customize the behavior of the application.
"""

from dataclasses import dataclass
from typing import List, Optional, Dict
from enum import Enum


class CoinGeckoTier(Enum):
    """CoinGecko API tiers."""
    FREE = "free"
    HOBBY = "hobby"
    PRO = "pro"
    PRO_PLUS = "pro_plus"
    ENTERPRISE = "enterprise"


@dataclass
class CoinGeckoConfig:
    """CoinGecko API configuration with tier support."""
    api_key: Optional[str] = None  # Set your CoinGecko API key here
    tier: CoinGeckoTier = CoinGeckoTier.FREE
    base_url: str = "https://api.coingecko.com/api/v3"
    pro_base_url: str = "https://pro-api.coingecko.com/api/v3"
    enable_cache: bool = True
    cache_ttl: int = 60  # seconds


@dataclass
class WebSocketConfig:
    """WebSocket connection configuration."""
    host: str = "0.0.0.0"
    port: int = 8000
    max_connections: int = 1000
    ping_interval: int = 20
    ping_timeout: int = 20
    close_timeout: int = 1
    limit_concurrency: int = 1000
    timeout_keep_alive: int = 30


@dataclass
class DataConfig:
    """Data source configuration."""
    symbols: List[str] = None  # Will use TOP_50_CRYPTOS if None
    mock_mode: bool = False
    update_interval_ms: int = 100  # Mock mode update interval
    max_history_length: int = 1000  # Max price history per symbol
    enable_geographic_fallback: bool = True  # Auto-fallback to mock on HTTP 451


@dataclass
class SecurityConfig:
    """Security configuration."""
    enable_input_validation: bool = True
    enable_rate_limiting: bool = True
    rate_limit_max_requests: int = 1000
    rate_limit_window_seconds: int = 60
    max_message_size_bytes: int = 1024 * 1024  # 1MB
    log_security_events: bool = True


@dataclass
class IndicatorConfig:
    """Technical indicator configuration."""
    rsi_period: int = 14
    macd_fast_period: int = 12
    macd_slow_period: int = 26
    macd_signal_period: int = 9
    ema_short_period: int = 20
    ema_long_period: int = 50
    atr_period: int = 14
    stochastic_k_period: int = 14
    stochastic_d_period: int = 3
    enable_signals: bool = True  # Generate buy/sell signals


@dataclass
class ChartConfig:
    """Chart visualization configuration."""
    default_chart_type: str = "Line"  # Line, Area, Candlestick
    default_timeframe: str = "1m"  # 1m, 5m, 15m, 1h, 4h, 1d
    default_indicators: List[str] = None  # Will use default if None
    enable_crosshair: bool = True
    enable_unified_hover: bool = True
    chart_height: int = 800
    show_volume: bool = True
    show_bollinger_bands: bool = True


@dataclass
class PerformanceConfig:
    """Performance optimization configuration."""
    enable_gpu_acceleration: bool = True
    enable_binary_serialization: bool = True  # MessagePack
    enable_tcp_optimization: bool = True
    enable_batch_processing: bool = True
    connection_pool_size: int = 10
    health_check_interval_seconds: int = 30
    max_reconnect_attempts: int = 5


@dataclass
class LoggingConfig:
    """Logging configuration."""
    log_level: str = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    log_to_file: bool = True
    log_file_path: str = "hedera_charts.log"
    log_rotation: bool = True
    max_log_size_mb: int = 10
    backup_count: int = 5


@dataclass
class AppConfig:
    """Main application configuration."""
    websocket: WebSocketConfig = None
    data: DataConfig = None
    security: SecurityConfig = None
    indicator: IndicatorConfig = None
    chart: ChartConfig = None
    performance: PerformanceConfig = None
    logging: LoggingConfig = None
    coingecko: CoinGeckoConfig = None
    
    def __post_init__(self):
        """Initialize default configurations if not provided."""
        if self.websocket is None:
            self.websocket = WebSocketConfig()
        if self.data is None:
            self.data = DataConfig()
        if self.security is None:
            self.security = SecurityConfig()
        if self.indicator is None:
            self.indicator = IndicatorConfig()
        if self.chart is None:
            self.chart = ChartConfig()
        if self.performance is None:
            self.performance = PerformanceConfig()
        if self.logging is None:
            self.logging = LoggingConfig()
        if self.coingecko is None:
            self.coingecko = CoinGeckoConfig()


# Global configuration instance
config = AppConfig()


def load_config_from_dict(config_dict: dict) -> AppConfig:
    """Load configuration from dictionary."""
    return AppConfig(
        websocket=WebSocketConfig(**config_dict.get("websocket", {})),
        data=DataConfig(**config_dict.get("data", {})),
        security=SecurityConfig(**config_dict.get("security", {})),
        indicator=IndicatorConfig(**config_dict.get("indicator", {})),
        chart=ChartConfig(**config_dict.get("chart", {})),
        performance=PerformanceConfig(**config_dict.get("performance", {})),
        logging=LoggingConfig(**config_dict.get("logging", {})),
        coingecko=CoinGeckoConfig(**config_dict.get("coingecko", {})),
    )


def get_config() -> AppConfig:
    """Get the global configuration instance."""
    return config
