"""Hedera Realtime Charts - Ultra low-latency crypto charting infrastructure.

Easy-to-use library for real-time cryptocurrency charting with advanced technical indicators.

Basic Usage:
    from hedera_realtime_charts import CryptoCharts
    
    # Initialize with default settings
    charts = CryptoCharts()
    
    # Start streaming
    charts.start()
    
    # Get latest price
    price = charts.get_price("BTCUSDT")
    
    # Get technical indicators
    indicators = charts.get_indicators("BTCUSDT")
    
    # Stop streaming
    charts.stop()
"""

from .binance_websocket import BinanceWebSocket
from .technical_indicators import TechnicalIndicators
from .connection_pool import ConnectionPool
from .security import SecurityConfig
from .top_cryptos import TOP_50_CRYPTOS

__version__ = "1.0.0"
__all__ = [
    "CryptoCharts",
    "BinanceWebSocket",
    "TechnicalIndicators",
    "ConnectionPool",
    "SecurityConfig",
    "TOP_50_CRYPTOS",
]


class CryptoCharts:
    """Easy-to-use interface for real-time crypto charting.
    
    This class provides a simple API for accessing real-time cryptocurrency data,
    technical indicators, and charting features without needing to understand
    the underlying infrastructure.
    
    Example:
        from hedera_realtime_charts import CryptoCharts
        
        # Initialize
        charts = CryptoCharts(symbols=["BTCUSDT", "ETHUSDT"])
        
        # Start streaming
        await charts.start()
        
        # Get latest price
        price = await charts.get_price("BTCUSDT")
        
        # Get indicators
        indicators = await charts.get_indicators("BTCUSDT")
        
        # Stop
        await charts.stop()
    """
    
    def __init__(self, symbols=None, mock_mode=False):
        """Initialize CryptoCharts.
        
        Args:
            symbols: List of cryptocurrency symbols (e.g., ["BTCUSDT", "ETHUSDT"])
                    Defaults to TOP_50_CRYPTOS if None
            mock_mode: Use mock data for testing (default: False)
        """
        self.symbols = symbols or TOP_50_CRYPTOS
        self.mock_mode = mock_mode
        self.client = None
        self.price_data = {}
        self.running = False
    
    async def start(self):
        """Start streaming real-time price data."""
        import asyncio
        
        if self.running:
            return
        
        self.running = True
        
        # Create WebSocket client
        self.client = BinanceWebSocket(
            symbols=self.symbols,
            callback=self._price_callback,
            mock_mode=self.mock_mode
        )
        
        # Connect and start listening
        await self.client.connect()
        asyncio.create_task(self.client.listen())
    
    async def stop(self):
        """Stop streaming price data."""
        if self.client:
            await self.client.close()
        self.running = False
    
    async def _price_callback(self, price_data):
        """Internal callback for price updates."""
        symbol = price_data["symbol"]
        self.price_data[symbol] = {
            "price": price_data["price"],
            "quantity": price_data.get("quantity", 0),
            "time": price_data.get("time", 0),
            "latency": price_data.get("latency", 0),
        }
    
    async def get_price(self, symbol):
        """Get latest price for a symbol.
        
        Args:
            symbol: Cryptocurrency symbol (e.g., "BTCUSDT")
        
        Returns:
            Dictionary with price data or None if not available
        """
        return self.price_data.get(symbol)
    
    async def get_all_prices(self):
        """Get prices for all symbols.
        
        Returns:
            Dictionary mapping symbols to price data
        """
        return self.price_data.copy()
    
    async def get_indicators(self, symbol, indicators=None):
        """Get technical indicators for a symbol.
        
        Args:
            symbol: Cryptocurrency symbol (e.g., "BTCUSDT")
            indicators: List of indicators to calculate (default: all)
                      Options: ["RSI", "MACD", "Stochastic", "EMA20", "EMA50", "ATR"]
        
        Returns:
            Dictionary with indicator results
        """
        if symbol not in self.price_data:
            return None
        
        # Get price history (in real implementation, this would come from stored history)
        prices = [self.price_data[symbol]["price"]]
        highs = prices
        lows = prices
        
        # Calculate indicators
        all_indicators = TechnicalIndicators.calculate_all_indicators(prices, highs, lows)
        
        if indicators:
            return {k: v for k, v in all_indicators.items() if k in indicators}
        
        return all_indicators
    
    def is_running(self):
        """Check if streaming is active."""
        return self.running
    
    def get_symbols(self):
        """Get list of symbols being tracked."""
        return self.symbols.copy()


# Convenience functions for quick access
async def get_crypto_price(symbol, mock_mode=False):
    """Quick function to get a single cryptocurrency price.
    
    Args:
        symbol: Cryptocurrency symbol (e.g., "BTCUSDT")
        mock_mode: Use mock data for testing (default: False)
    
    Returns:
        Latest price or None
    """
    charts = CryptoCharts(symbols=[symbol], mock_mode=mock_mode)
    await charts.start()
    
    # Wait a moment for data
    import asyncio
    await asyncio.sleep(1)
    
    price_data = await charts.get_price(symbol)
    await charts.stop()
    
    return price_data["price"] if price_data else None


async def get_crypto_indicators(symbol, mock_mode=False):
    """Quick function to get technical indicators for a cryptocurrency.
    
    Args:
        symbol: Cryptocurrency symbol (e.g., "BTCUSDT")
        mock_mode: Use mock data for testing (default: False)
    
    Returns:
        Dictionary with indicator results
    """
    charts = CryptoCharts(symbols=[symbol], mock_mode=mock_mode)
    await charts.start()
    
    # Wait a moment for data
    import asyncio
    await asyncio.sleep(1)
    
    indicators = await charts.get_indicators(symbol)
    await charts.stop()
    
    return indicators
