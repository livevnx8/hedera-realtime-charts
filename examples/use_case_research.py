"""
Use Case: Research - Price Correlation Analysis

This example shows how to collect real-time price data and analyze
correlations between different cryptocurrencies for research purposes.
"""

import asyncio
import time
import sys
from pathlib import Path
from collections import defaultdict, deque
import statistics

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from binance_websocket import BinanceWebSocket


class CorrelationAnalyzer:
    """Analyze price correlations between cryptocurrencies."""
    
    def __init__(self, symbols):
        self.symbols = symbols
        self.price_history = defaultdict(lambda: deque(maxlen=1000))
        self.start_time = time.time()
    
    async def price_callback(self, price_data):
        """Handle price updates."""
        symbol = price_data["symbol"]
        price = price_data["price"]
        
        self.price_history[symbol].append(price)
        
        # Analyze correlations every 100 updates
        if len(self.price_history[symbol]) % 100 == 0:
            self.analyze_correlations()
    
    def analyze_correlations(self):
        """Analyze price correlations between symbols."""
        print(f"\n=== Correlation Analysis (t={time.time() - self.start_time:.0f}s) ===")
        
        # Calculate correlations
        correlations = {}
        for i, symbol1 in enumerate(self.symbols):
            for symbol2 in self.symbols[i+1:]:
                if len(self.price_history[symbol1]) > 100 and len(self.price_history[symbol2]) > 100:
                    # Get overlapping data
                    min_len = min(len(self.price_history[symbol1]), len(self.price_history[symbol2]))
                    prices1 = list(self.price_history[symbol1])[-min_len:]
                    prices2 = list(self.price_history[symbol2])[-min_len:]
                    
                    # Calculate correlation
                    correlation = self.calculate_correlation(prices1, prices2)
                    correlations[f"{symbol1}-{symbol2}"] = correlation
        
        # Display correlations
        for pair, corr in correlations.items():
            strength = "Strong" if abs(corr) > 0.7 else "Moderate" if abs(corr) > 0.4 else "Weak"
            print(f"{pair}: {corr:.3f} ({strength})")
    
    def calculate_correlation(self, prices1, prices2):
        """Calculate Pearson correlation coefficient."""
        n = len(prices1)
        if n < 2:
            return 0.0
        
        mean1 = statistics.mean(prices1)
        mean2 = statistics.mean(prices2)
        
        numerator = sum((p1 - mean1) * (p2 - mean2) for p1, p2 in zip(prices1, prices2))
        denominator = (sum((p1 - mean1) ** 2 for p1 in prices1) ** 0.5 *
                      sum((p2 - mean2) ** 2 for p2 in prices2) ** 0.5)
        
        if denominator == 0:
            return 0.0
        
        return numerator / denominator


async def main():
    """Run the correlation analysis."""
    symbols = ["BTCUSDT", "ETHUSDT", "HBARUSDT", "SOLUSDT"]
    
    analyzer = CorrelationAnalyzer(symbols)
    
    print(f"Starting correlation analysis for: {', '.join(symbols)}")
    print("Correlations will be calculated every 100 price updates")
    print("Press Ctrl+C to stop\n")
    
    client = BinanceWebSocket(symbols, analyzer.price_callback)
    
    try:
        await client.connect()
        await client.listen()
    except KeyboardInterrupt:
        print("\nStopping correlation analysis...")
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
