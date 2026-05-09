"""
Simple example: Real-time price streaming from Binance.

This example shows how to connect to Binance WebSocket and receive
real-time price updates for multiple cryptocurrencies.
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from binance_websocket import BinanceWebSocket


async def price_callback(price_data):
    """Handle incoming price updates."""
    symbol = price_data["symbol"]
    price = price_data["price"]
    latency = price_data["latency"]
    print(f"{symbol}: ${price:.2f} (latency: {latency:.2f}ms)")


async def main():
    """Run the simple price stream example."""
    symbols = ["BTCUSDT", "ETHUSDT", "HBARUSDT", "SOLUSDT"]
    
    print(f"Starting price stream for: {', '.join(symbols)}")
    print("Press Ctrl+C to stop\n")
    
    # Try real connection first, fall back to mock if blocked
    try:
        client = BinanceWebSocket(symbols, price_callback)
        await client.connect()
        await client.listen()
    except Exception as e:
        print(f"Real connection failed: {e}")
        print("Falling back to mock mode...")
        client = BinanceWebSocket(symbols, price_callback, mock_mode=True)
        await client.connect()
        await client.listen()
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
