"""Binance WebSocket integration for real-time crypto prices."""

import asyncio
import json
import websockets
from typing import Dict, List, Optional, Callable
import time
import random


class BinanceWebSocket:
    """Low-latency Binance WebSocket client for real-time price data."""

    def __init__(self, symbols: List[str], callback: Callable, mock_mode: bool = False):
        """
        Initialize Binance WebSocket client.

        Args:
            symbols: List of trading pairs (e.g., ["BTCUSDT", "ETHUSDT", "HBARUSDT"])
            callback: Async callback function to handle price updates
            mock_mode: If True, use mock data instead of real WebSocket (for testing)
        """
        self.symbols = symbols
        self.callback = callback
        self.mock_mode = mock_mode
        self.ws_url = "wss://stream.binance.com:9443/ws"
        self.websocket: Optional[websockets.WebSocketClientProtocol] = None
        self.running = False

    def _build_stream(self) -> str:
        """Build the Binance stream URL for the given symbols."""
        streams = [f"{symbol.lower()}@trade" for symbol in self.symbols]
        return "/".join(streams)

    async def _generate_mock_data(self):
        """Generate mock price data for testing when real connection is blocked."""
        base_prices = {
            "BTCUSDT": 50000.0,
            "ETHUSDT": 3000.0,
            "HBARUSDT": 0.10,
            "SOLUSDT": 100.0,
            "BNBUSDT": 600.0,
            "XRPUSDT": 0.50,
            "ADAUSDT": 0.50,
            "AVAXUSDT": 35.0,
            "DOGEUSDT": 0.15,
            "DOTUSDT": 7.0,
            "LINKUSDT": 15.0,
            "MATICUSDT": 0.85,
            "SHIBUSDT": 0.000025,
            "LTCUSDT": 75.0,
            "BCHUSDT": 400.0,
            "ATOMUSDT": 8.0,
            "UNIUSDT": 10.0,
            "XLMUSDT": 0.12,
            "ETCUSDT": 20.0,
            "XMRUSDT": 150.0,
            "ALGOUSDT": 0.18,
            "ICPUSDT": 12.0,
            "VETUSDT": 0.02,
            "FILUSDT": 5.5,
            "NEARUSDT": 6.0,
            "APTUSDT": 9.0,
            "QNTUSDT": 100.0,
            "APEUSDT": 1.2,
            "MKRUSDT": 2500.0,
            "COMPUSDT": 55.0,
            "SANDUSDT": 0.50,
            "AAVEUSDT": 90.0,
            "EOSUSDT": 0.60,
            "THETAUSDT": 2.0,
            "MANAUSDT": 0.40,
            "AXSUSDT": 8.0,
            "CRVUSDT": 0.60,
            "GRTUSDT": 0.15,
            "CHZUSDT": 0.12,
            "HOTUSDT": 0.0008,
            "LUNCUSDT": 0.0001,
            "RUNEUSDT": 5.0,
            "ZECUSDT": 35.0,
            "KAVAUSDT": 0.80,
            "CFXUSDT": 0.18,
            "EGLDUSDT": 40.0,
            "GTUSDT": 6.0,
            "FXSUSDT": 5.0,
            "PEPEUSDT": 0.000008,
            "TRXUSDT": 0.12,
        }
        
        while self.running:
            for symbol in self.symbols:
                base = base_prices.get(symbol, 100.0)
                # Add realistic price movement
                price = base * (1 + random.uniform(-0.01, 0.01))  # +/- 1% movement
                quantity = random.uniform(0.1, 10.0)
                
                price_data = {
                    "symbol": symbol,
                    "price": price,
                    "quantity": quantity,
                    "time": int(time.time() * 1000),
                    "latency": random.uniform(5, 50),
                }
                
                await self.callback(price_data)
            
            await asyncio.sleep(0.1)  # Update every 100ms for realistic high-frequency data

    async def connect(self):
        """Connect to Binance WebSocket."""
        if self.mock_mode:
            print("Running in mock mode (no real WebSocket connection)")
            return

        stream = self._build_stream()
        url = f"{self.ws_url}/{stream}"
        
        # Set socket options for low latency
        self.websocket = await websockets.connect(
            url,
            ping_interval=20,
            ping_timeout=20,
            close_timeout=1,
        )
        self.running = True

    async def listen(self):
        """Listen for incoming WebSocket messages."""
        if self.mock_mode:
            self.running = True
            await self._generate_mock_data()
            return
        
        try:
            while self.running:
                message = await self.websocket.recv()
                data = json.loads(message)
                
                # Validate data structure
                if not isinstance(data, dict):
                    continue
                
                if "p" not in data or "s" not in data:
                    continue
                
                # Extract price data
                price_data = {
                    "symbol": data["s"],
                    "price": float(data["p"]),
                    "quantity": float(data.get("q", 0)),
                    "time": int(data.get("T", time.time() * 1000)),
                    "latency": (time.time() * 1000) - int(data.get("T", time.time() * 1000)),
                }
                
                await self.callback(price_data)
        except websockets.exceptions.ConnectionClosed:
            print("WebSocket connection closed")
        except Exception as e:
            print(f"Error in listen: {e}")
            raise

    async def close(self):
        """Close the WebSocket connection."""
        self.running = False
        if self.websocket:
            await self.websocket.close()


async def example_callback(price_data: Dict):
    """Example callback for price updates."""
    print(f"{price_data['symbol']}: ${price_data['price']:.2f} (latency: {price_data['latency']:.2f}ms)")


async def main():
    """Example usage."""
    symbols = ["BTCUSDT", "ETHUSDT", "HBARUSDT", "SOLUSDT"]
    
    # Try real connection first, fall back to mock if blocked
    try:
        client = BinanceWebSocket(symbols, example_callback)
        await client.connect()
        await client.listen()
    except Exception as e:
        print(f"Real connection failed: {e}")
        print("Falling back to mock mode...")
        client = BinanceWebSocket(symbols, example_callback, mock_mode=True)
        await client.connect()
        await client.listen()


if __name__ == "__main__":
    asyncio.run(main())
