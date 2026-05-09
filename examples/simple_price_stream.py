"""
Simple example: Real-time price streaming from Binance.

This example shows how to connect to Binance WebSocket and receive
real-time price updates for multiple cryptocurrencies.
"""

import asyncio
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
    
    client = BinanceWebSocket(symbols, price_callback)
    
    try:
        await client.connect()
        await client.listen()
    except KeyboardInterrupt:
        print("\nStopping price stream...")
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
