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
        }
        
        while self.running:
            for symbol in self.symbols:
                base = base_prices.get(symbol, 100.0)
                price = base + random.uniform(-100, 100)
                quantity = random.uniform(0.1, 10.0)
                
                price_data = {
                    "symbol": symbol,
                    "price": price,
                    "quantity": quantity,
                    "time": int(time.time() * 1000),
                    "latency": random.uniform(5, 50),
                }
                
                await self.callback(price_data)
            
            await asyncio.sleep(1)  # Update every second in mock mode

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
        """Listen for price updates."""
        if self.mock_mode:
            self.running = True
            await self._generate_mock_data()
            return

        if not self.websocket:
            await self.connect()

        try:
            while self.running:
                message = await self.websocket.recv()
                data = json.loads(message)
                
                # Extract relevant data with minimal processing
                if "e" in data and data["e"] == "trade":
                    price_data = {
                        "symbol": data["s"],
                        "price": float(data["p"]),
                        "quantity": float(data["q"]),
                        "time": data["T"],
                        "latency": time.time() * 1000 - data["T"],  # Calculate latency in ms
                    }
                    
                    # Call the callback with the price data
                    await self.callback(price_data)

        except websockets.exceptions.ConnectionClosed:
            print("Binance WebSocket connection closed")
        except Exception as e:
            print(f"Error in Binance WebSocket: {e}")

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
