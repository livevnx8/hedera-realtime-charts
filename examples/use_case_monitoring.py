"""
Use Case: Real-time Price Monitoring Dashboard

This example shows how to build a simple monitoring dashboard
that tracks multiple cryptocurrencies and displays real-time prices,
latency metrics, and basic statistics.
"""

import asyncio
import time
import sys
from pathlib import Path
from collections import defaultdict, deque

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from binance_websocket import BinanceWebSocket


class PriceMonitor:
    """Simple price monitoring dashboard."""
    
    def __init__(self, symbols):
        self.symbols = symbols
        self.price_history = defaultdict(lambda: deque(maxlen=100))
        self.latency_history = defaultdict(lambda: deque(maxlen=100))
        self.start_time = time.time()
    
    async def price_callback(self, price_data):
        """Handle price updates."""
        symbol = price_data["symbol"]
        price = price_data["price"]
        latency = price_data["latency"]
        
        self.price_history[symbol].append(price)
        self.latency_history[symbol].append(latency)
        
        self.display_dashboard()
    
    def display_dashboard(self):
        """Display the monitoring dashboard."""
        print("\n" + "=" * 80)
        print(f"Price Monitoring Dashboard - Uptime: {time.time() - self.start_time:.0f}s")
        print("=" * 80)
        
        for symbol in self.symbols:
            prices = self.price_history[symbol]
            latencies = self.latency_history[symbol]
            
            if prices:
                current_price = prices[-1]
                min_price = min(prices)
                max_price = max(prices)
                avg_price = sum(prices) / len(prices)
                
                print(f"\n{symbol}:")
                print(f"  Current: ${current_price:.2f}")
                print(f"  Min: ${min_price:.2f} | Max: ${max_price:.2f} | Avg: ${avg_price:.2f}")
                
            if latencies:
                avg_latency = sum(latencies) / len(latencies)
                min_latency = min(latencies)
                max_latency = max(latencies)
                
                print(f"  Latency: {avg_latency:.2f}ms avg ({min_latency:.2f}ms - {max_latency:.2f}ms)")
        
        print("\n" + "=" * 80)


async def main():
    """Run the monitoring dashboard."""
    symbols = ["BTCUSDT", "ETHUSDT", "HBARUSDT", "SOLUSDT"]
    
    monitor = PriceMonitor(symbols)
    
    print(f"Starting monitoring dashboard for: {', '.join(symbols)}")
    print("Press Ctrl+C to stop\n")
    
    client = BinanceWebSocket(symbols, monitor.price_callback)
    
    try:
        await client.connect()
        await client.listen()
    except KeyboardInterrupt:
        print("\nStopping monitoring dashboard...")
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
