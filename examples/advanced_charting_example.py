"""Advanced charting example with technical indicators.

This example demonstrates how to use the advanced technical indicators
and chart types available in hedera-realtime-charts.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from technical_indicators import TechnicalIndicators
import numpy as np


def generate_sample_data(n=100):
    """Generate sample price data for demonstration."""
    np.random.seed(42)
    
    # Generate realistic price movement
    prices = [50000.0]
    for _ in range(n - 1):
        change = np.random.normal(0, 100)
        prices.append(max(prices[-1] + change, 100))
    
    # Generate highs and lows
    highs = [p + np.random.uniform(0, 50) for p in prices]
    lows = [p - np.random.uniform(0, 50) for p in prices]
    
    return prices, highs, lows


def main():
    """Demonstrate advanced technical indicators."""
    print("=" * 60)
    print("Advanced Technical Indicators Demo")
    print("=" * 60)
    
    # Generate sample data
    prices, highs, lows = generate_sample_data(100)
    print(f"\nGenerated {len(prices)} price points")
    print(f"Price range: ${min(prices):.2f} - ${max(prices):.2f}")
    
    # Calculate all indicators
    print("\n" + "=" * 60)
    print("Calculating Technical Indicators...")
    print("=" * 60)
    
    indicators = TechnicalIndicators.calculate_all_indicators(prices, highs, lows)
    
    # Display RSI
    print("\n--- RSI (Relative Strength Index) ---")
    rsi = indicators["RSI"]
    print(f"Latest RSI: {rsi.values[-1]:.2f}")
    print(f"RSI Signal: {rsi.signals[-1].upper()}")
    print(f"Parameters: period={rsi.parameters['period']}")
    
    # Display MACD
    print("\n--- MACD (Moving Average Convergence Divergence) ---")
    macd = indicators["MACD"]
    print(f"Latest MACD: {macd.values[-1]:.4f}")
    print(f"MACD Signal: {macd.signals[-1].upper()}")
    print(f"Parameters: fast={macd.parameters['fast']}, slow={macd.parameters['slow']}, signal={macd.parameters['signal']}")
    
    # Display Stochastic
    print("\n--- Stochastic Oscillator ---")
    stoch = indicators["Stochastic"]
    print(f"Latest Stochastic: {stoch.values[-1]:.2f}")
    print(f"Stochastic Signal: {stoch.signals[-1].upper()}")
    print(f"Parameters: k_period={stoch.parameters['k_period']}, d_period={stoch.parameters['d_period']}")
    
    # Display EMA
    print("\n--- EMA (Exponential Moving Average) ---")
    ema20 = indicators["EMA20"]
    ema50 = indicators["EMA50"]
    print(f"Latest EMA20: ${ema20.values[-1]:.2f}")
    print(f"Latest EMA50: ${ema50.values[-1]:.2f}")
    print(f"Parameters: period={ema20.parameters['period']}")
    
    # Display ATR
    print("\n--- ATR (Average True Range) ---")
    atr = indicators["ATR"]
    print(f"Latest ATR: ${atr.values[-1]:.2f}")
    print(f"Parameters: period={atr.parameters['period']}")
    
    # Display all signals
    print("\n" + "=" * 60)
    print("Current Signals Summary")
    print("=" * 60)
    
    for name, result in indicators.items():
        if result.signals:
            signal = result.signals[-1]
            symbol = "🟢" if signal == "buy" else "🔴" if signal == "sell" else "⚪"
            print(f"{symbol} {name:15s}: {signal.upper()}")
    
    print("\n" + "=" * 60)
    print("Demo Complete")
    print("=" * 60)
    print("\nTo use these indicators in the Streamlit frontend:")
    print("1. Start the server: python -m src.server")
    print("2. Start the frontend: streamlit run frontend/app.py")
    print("3. Select indicators from the sidebar")
    print("4. View buy/sell signals in real-time")


if __name__ == "__main__":
    main()
