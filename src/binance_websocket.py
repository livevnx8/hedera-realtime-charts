"""Binance WebSocket integration for real-time crypto prices."""

import asyncio
import json
import websockets
from typing import Dict, List, Optional, Callable
import time


class BinanceWebSocket:
    """Low-latency Binance WebSocket client for real-time price data."""

    def __init__(self, symbols: List[str], callback: Callable):
        """
        Initialize Binance WebSocket client.

        Args:
            symbols: List of trading pairs (e.g., ["BTCUSDT", "ETHUSDT", "HBARUSDT"])
            callback: Async callback function to handle price updates
        """
        self.symbols = symbols
        self.callback = callback
        self.ws_url = "wss://stream.binance.com:9443/ws"
        self.websocket: Optional[websockets.WebSocketClientProtocol] = None
        self.running = False

    def _build_stream(self) -> str:
        """Build the Binance stream URL for the given symbols."""
        streams = [f"{symbol.lower()}@trade" for symbol in self.symbols]
        return "/".join(streams)

    async def connect(self):
        """Connect to Binance WebSocket."""
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
    client = BinanceWebSocket(symbols, example_callback)
    
    try:
        await client.connect()
        await client.listen()
    except KeyboardInterrupt:
        pass
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
