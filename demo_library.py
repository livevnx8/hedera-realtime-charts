"""Demo script for hedera-realtime-charts library.

This script demonstrates the easy-to-use library interface.
Run this to see the library in action, or record it to create a GIF.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src import CryptoCharts, get_crypto_price, get_crypto_indicators
import asyncio


async def demo_basic_usage():
    """Demonstrate basic library usage."""
    print("=" * 70)
    print("🚀 Hedera Realtime Charts - Library Demo")
    print("=" * 70)
    
    print("\n📦 Easy-to-use library interface")
    print("   from hedera_realtime_charts import CryptoCharts")
    
    print("\n🎯 Demo 1: Basic Usage")
    print("-" * 70)
    
    # Initialize
    charts = CryptoCharts(symbols=["BTCUSDT", "ETHUSDT"], mock_mode=True)
    print("✓ Initialized CryptoCharts with BTC and ETH")
    
    # Start streaming
    await charts.start()
    print("✓ Started streaming (mock mode)")
    
    # Wait for data
    await asyncio.sleep(1)
    
    # Get prices
    print("\n💰 Current Prices:")
    prices = await charts.get_all_prices()
    for symbol, data in prices.items():
        print(f"   {symbol}: ${data['price']:.2f}")
    
    # Get indicators
    print("\n📊 Technical Indicators for BTC:")
    indicators = await charts.get_indicators("BTCUSDT")
    
    print(f"   RSI: {indicators['RSI'].values[-1]:.2f} ({indicators['RSI'].signals[-1]})")
    print(f"   MACD: {indicators['MACD'].values[-1]:.4f} ({indicators['MACD'].signals[-1]})")
    print(f"   Stochastic: {indicators['Stochastic'].values[-1]:.2f} ({indicators['Stochastic'].signals[-1]})")
    
    # Stop
    await charts.stop()
    print("✓ Stopped streaming")


async def demo_convenience_functions():
    """Demonstrate convenience functions."""
    print("\n" + "=" * 70)
    print("🎯 Demo 2: Convenience Functions")
    print("-" * 70)
    
    print("\n📦 One-liner functions for quick access")
    print("   from hedera_realtime_charts import get_crypto_price")
    print("   from hedera_realtime_charts import get_crypto_indicators")
    
    # Get price
    price = await get_crypto_price("BTCUSDT", mock_mode=True)
    print(f"\n💰 BTC Price: ${price:.2f}")
    
    # Get indicators
    indicators = await get_crypto_indicators("BTCUSDT", mock_mode=True)
    print(f"\n📊 BTC Indicators:")
    print(f"   RSI: {indicators['RSI'].values[-1]:.2f}")
    print(f"   MACD: {indicators['MACD'].values[-1]:.4f}")


async def demo_signals():
    """Demonstrate buy/sell signals."""
    print("\n" + "=" * 70)
    print("🎯 Demo 3: Buy/Sell Signals")
    print("-" * 70)
    
    print("\n📦 Automatic signal generation")
    
    charts = CryptoCharts(symbols=["BTCUSDT"], mock_mode=True)
    await charts.start()
    await asyncio.sleep(1)
    
    indicators = await charts.get_indicators("BTCUSDT")
    
    print("\n🎯 Current Signals:")
    for name, result in indicators.items():
        if result.signals:
            signal = result.signals[-1]
            emoji = "🟢" if signal == "buy" else "🔴" if signal == "sell" else "⚪"
            print(f"   {emoji} {name:15s}: {signal.upper()}")
    
    await charts.stop()


async def demo_custom_symbols():
    """Demonstrate custom symbol selection."""
    print("\n" + "=" * 70)
    print("🎯 Demo 4: Custom Symbols")
    print("-" * 70)
    
    print("\n📦 Track any cryptocurrencies")
    print("   charts = CryptoCharts(symbols=['BTCUSDT', 'ETHUSDT', 'HBARUSDT'])")
    
    charts = CryptoCharts(
        symbols=["BTCUSDT", "ETHUSDT", "HBARUSDT", "SOLUSDT"],
        mock_mode=True
    )
    await charts.start()
    await asyncio.sleep(1)
    
    print("\n💰 Tracked Symbols:")
    for symbol in charts.get_symbols():
        data = await charts.get_price(symbol)
        print(f"   {symbol}: ${data['price']:.2f}")
    
    await charts.stop()


async def main():
    """Run all demos."""
    print("\n" + "🎬" * 35)
    print("\n")
    
    await demo_basic_usage()
    await demo_convenience_functions()
    await demo_signals()
    await demo_custom_symbols()
    
    print("\n" + "=" * 70)
    print("✨ Demo Complete!")
    print("=" * 70)
    
    print("\n📚 Learn more:")
    print("   - Read LIBRARY_USAGE.md for detailed documentation")
    print("   - Check examples/ directory for more examples")
    print("   - Visit https://github.com/livevnx8/hedera-realtime-charts")
    
    print("\n🎥 To create a GIF:")
    print("   1. Run: python demo_library.py")
    print("   2. Use screen recording software to capture the output")
    print("   3. Convert to GIF using ffmpeg or similar tools")


if __name__ == "__main__":
    asyncio.run(main())
