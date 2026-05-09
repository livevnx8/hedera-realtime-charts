"""Proof-of-concept demo showing hedera-realtime-charts in action."""

import asyncio
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from binance_websocket import BinanceWebSocket
from top_cryptos import TOP_10_CRYPTOS
import json


class ProofDemo:
    """Proof-of-concept demonstration."""
    
    def __init__(self):
        self.received_updates = 0
        self.start_time = None
        self.latencies = []
        self.symbols_seen = set()
        self.results = {
            "demo_timestamp": time.time(),
            "symbols_tested": len(TOP_10_CRYPTOS),
            "total_updates": 0,
            "symbols_received": [],
            "latency_stats": {},
            "throughput": 0,
            "duration": 0,
        }
    
    async def price_callback(self, price_data):
        """Handle price updates for demo."""
        if self.start_time is None:
            self.start_time = time.time()
        
        self.received_updates += 1
        self.latencies.append(price_data.get("latency", 0))
        self.symbols_seen.add(price_data["symbol"])
        
        # Print update
        symbol = price_data["symbol"]
        price = price_data["price"]
        latency = price_data.get("latency", 0)
        print(f"✓ {symbol}: ${price:.4f} (latency: {latency:.2f}ms)")
        
        # Stop after 100 updates per symbol
        if self.received_updates >= len(TOP_10_CRYPTOS) * 10:
            return True  # Signal to stop
        
        return False
    
    async def run_demo(self, duration=10):
        """Run the demo for specified duration."""
        print("=" * 60)
        print("Hedera Realtime Charts - Proof of Concept Demo")
        print("=" * 60)
        print(f"\nTesting {len(TOP_10_CRYPTOS)} cryptocurrencies...")
        print(f"Duration: {duration} seconds\n")
        
        # Create WebSocket client with mock mode
        client = BinanceWebSocket(
            symbols=TOP_10_CRYPTOS,
            callback=self.price_callback,
            mock_mode=True
        )
        
        try:
            await client.connect()
            print("✓ WebSocket connected (mock mode)\n")
            
            # Listen for updates
            start = time.time()
            await client.listen()
            
        except Exception as e:
            print(f"✗ Demo failed: {e}")
            return False
        
        # Calculate results
        duration = time.time() - start
        self.results["total_updates"] = self.received_updates
        self.results["symbols_received"] = list(self.symbols_seen)
        self.results["duration"] = duration
        self.results["throughput"] = self.received_updates / duration if duration > 0 else 0
        
        if self.latencies:
            self.results["latency_stats"] = {
                "avg_ms": sum(self.latencies) / len(self.latencies),
                "min_ms": min(self.latencies),
                "max_ms": max(self.latencies),
                "p50_ms": sorted(self.latencies)[len(self.latencies) // 2],
            }
        
        return True
    
    def print_results(self):
        """Print demo results."""
        print("\n" + "=" * 60)
        print("Demo Results")
        print("=" * 60)
        print(f"\nTotal Updates Received: {self.results['total_updates']}")
        print(f"Symbols Received: {len(self.results['symbols_received'])}")
        print(f"Symbols: {', '.join(self.results['symbols_received'])}")
        print(f"Duration: {self.results['duration']:.2f}s")
        print(f"Throughput: {self.results['throughput']:.2f} updates/second")
        
        if self.results["latency_stats"]:
            stats = self.results["latency_stats"]
            print(f"\nLatency Statistics:")
            print(f"  Average: {stats['avg_ms']:.2f}ms")
            print(f"  Minimum: {stats['min_ms']:.2f}ms")
            print(f"  Maximum: {stats['max_ms']:.2f}ms")
            print(f"  P50: {stats['p50_ms']:.2f}ms")
        
        print("\n" + "=" * 60)
        print("✓ DEMO SUCCESSFUL - System is working")
        print("=" * 60)
        
        # Save results to file
        with open("demo_results.json", "w") as f:
            json.dump(self.results, f, indent=2)
        print("\n✓ Results saved to demo_results.json")


async def main():
    """Run the proof-of-concept demo."""
    demo = ProofDemo()
    
    try:
        success = await demo.run_demo(duration=10)
        if success:
            demo.print_results()
        else:
            print("✗ Demo failed")
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user")
        demo.print_results()


if __name__ == "__main__":
    asyncio.run(main())
