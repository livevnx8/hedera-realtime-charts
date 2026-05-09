# Library Usage Guide

The `hedera-realtime-charts` library provides an easy-to-use interface for real-time cryptocurrency charting with advanced technical indicators.

## Installation

```bash
pip install hedera-realtime-charts
```

Or install from source:

```bash
git clone https://github.com/livevnx8/hedera-realtime-charts.git
cd hedera-realtime-charts
pip install -e .
```

## Quick Start

### Basic Usage

```python
from hedera_realtime_charts import CryptoCharts
import asyncio

async def main():
    # Initialize with default settings (top 50 cryptos)
    charts = CryptoCharts()
    
    # Start streaming
    await charts.start()
    
    # Get latest price for Bitcoin
    price_data = await charts.get_price("BTCUSDT")
    print(f"BTC Price: ${price_data['price']}")
    
    # Get technical indicators
    indicators = await charts.get_indicators("BTCUSDT")
    print(f"RSI: {indicators['RSI'].values[-1]:.2f}")
    print(f"RSI Signal: {indicators['RSI'].signals[-1]}")
    
    # Stop streaming
    await charts.stop()

asyncio.run(main())
```

### Custom Symbols

```python
from hedera_realtime_charts import CryptoCharts
import asyncio

async def main():
    # Track specific cryptocurrencies
    charts = CryptoCharts(symbols=["BTCUSDT", "ETHUSDT", "HBARUSDT"])
    
    await charts.start()
    
    # Get all prices
    all_prices = await charts.get_all_prices()
    for symbol, data in all_prices.items():
        print(f"{symbol}: ${data['price']}")
    
    await charts.stop()

asyncio.run(main())
```

### Mock Mode for Testing

```python
from hedera_realtime_charts import CryptoCharts
import asyncio

async def main():
    # Use mock data for testing (no network required)
    charts = CryptoCharts(mock_mode=True)
    
    await charts.start()
    
    price = await charts.get_price("BTCUSDT")
    print(f"Mock BTC Price: ${price['price']}")
    
    await charts.stop()

asyncio.run(main())
```

## Convenience Functions

### Get Single Price

```python
from hedera_realtime_charts import get_crypto_price
import asyncio

async def main():
    # Quick one-liner to get a price
    price = await get_crypto_price("BTCUSDT")
    print(f"BTC Price: ${price}")

asyncio.run(main())
```

### Get Technical Indicators

```python
from hedera_realtime_charts import get_crypto_indicators
import asyncio

async def main():
    # Quick one-liner to get indicators
    indicators = await get_crypto_indicators("BTCUSDT")
    
    print(f"RSI: {indicators['RSI'].values[-1]:.2f}")
    print(f"MACD: {indicators['MACD'].values[-1]:.4f}")
    print(f"Stochastic: {indicators['Stochastic'].values[-1]:.2f}")

asyncio.run(main())
```

## Advanced Usage

### Specific Indicators

```python
from hedera_realtime_charts import CryptoCharts
import asyncio

async def main():
    charts = CryptoCharts(symbols=["BTCUSDT"])
    await charts.start()
    
    # Get only specific indicators
    indicators = await charts.get_indicators("BTCUSDT", indicators=["RSI", "MACD"])
    
    print(f"RSI: {indicators['RSI'].values[-1]:.2f}")
    print(f"MACD: {indicators['MACD'].values[-1]:.4f}")
    
    await charts.stop()

asyncio.run(main())
```

### Check Streaming Status

```python
from hedera_realtime_charts import CryptoCharts
import asyncio

async def main():
    charts = CryptoCharts(symbols=["BTCUSDT"])
    await charts.start()
    
    if charts.is_running():
        print("Streaming is active")
        print(f"Tracking {len(charts.get_symbols())} symbols")
    
    await charts.stop()

asyncio.run(main())
```

## Available Indicators

The library provides the following technical indicators:

- **RSI** (Relative Strength Index) - Overbought/oversold detection
- **MACD** (Moving Average Convergence Divergence) - Trend momentum
- **Stochastic** - Momentum oscillator
- **EMA20** (Exponential Moving Average) - 20-period EMA
- **EMA50** (Exponential Moving Average) - 50-period EMA
- **ATR** (Average True Range) - Volatility measurement

Each indicator includes:
- `values`: Array of indicator values
- `signals`: Array of buy/sell/neutral signals
- `parameters`: Configuration parameters used

## Signal Interpretation

- **buy**: Indicator suggests buying opportunity
- **sell**: Indicator suggests selling opportunity
- **neutral**: Indicator suggests no action

### RSI Signals
- RSI > 70: Overbought (potential sell)
- RSI < 30: Oversold (potential buy)

### MACD Signals
- Histogram crossing above zero: Bullish (potential buy)
- Histogram crossing below zero: Bearish (potential sell)

### Stochastic Signals
- %K > 80: Overbought (potential sell)
- %K < 20: Oversold (potential buy)

## Error Handling

```python
from hedera_realtime_charts import CryptoCharts
import asyncio

async def main():
    charts = CryptoCharts(symbols=["BTCUSDT"])
    
    try:
        await charts.start()
        price = await charts.get_price("BTCUSDT")
        print(f"Price: ${price['price']}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await charts.stop()

asyncio.run(main())
```

## Performance Tips

1. **Use mock mode** for testing to avoid network latency
2. **Limit symbols** to only what you need for better performance
3. **Cache indicators** if you need them repeatedly
4. **Check streaming status** before making requests
5. **Use convenience functions** for simple one-off requests

## Complete Example

```python
from hedera_realtime_charts import CryptoCharts
import asyncio

async def main():
    """Complete example showing all features."""
    
    # Initialize with custom symbols
    charts = CryptoCharts(
        symbols=["BTCUSDT", "ETHUSDT", "HBARUSDT"],
        mock_mode=True  # Use mock data for demo
    )
    
    print("Starting crypto charts...")
    await charts.start()
    
    # Wait for data to arrive
    await asyncio.sleep(2)
    
    # Get all prices
    print("\n=== Current Prices ===")
    all_prices = await charts.get_all_prices()
    for symbol, data in all_prices.items():
        print(f"{symbol}: ${data['price']:.2f}")
    
    # Get indicators for BTC
    print("\n=== BTC Technical Indicators ===")
    indicators = await charts.get_indicators("BTCUSDT")
    
    print(f"RSI: {indicators['RSI'].values[-1]:.2f} ({indicators['RSI'].signals[-1]})")
    print(f"MACD: {indicators['MACD'].values[-1]:.4f} ({indicators['MACD'].signals[-1]})")
    print(f"Stochastic: {indicators['Stochastic'].values[-1]:.2f} ({indicators['Stochastic'].signals[-1]})")
    print(f"EMA20: ${indicators['EMA20'].values[-1]:.2f}")
    print(f"EMA50: ${indicators['EMA50'].values[-1]:.2f}")
    print(f"ATR: ${indicators['ATR'].values[-1]:.2f}")
    
    # Stop streaming
    await charts.stop()
    print("\nStreaming stopped.")

asyncio.run(main())
```

## Integration with Applications

### Flask Integration

```python
from flask import Flask, jsonify
from hedera_realtime_charts import CryptoCharts
import asyncio

app = Flask(__name__)
charts = CryptoCharts(symbols=["BTCUSDT", "ETHUSDT"])

@app.before_first_request
async def start_charts():
    await charts.start()

@app.route('/api/price/<symbol>')
def get_price(symbol):
    data = asyncio.run(charts.get_price(symbol))
    return jsonify(data)

@app.route('/api/indicators/<symbol>')
def get_indicators(symbol):
    indicators = asyncio.run(charts.get_indicators(symbol))
    return jsonify({k: v.values[-1] for k, v in indicators.items()})
```

### Streamlit Integration

```python
import streamlit as st
from hedera_realtime_charts import CryptoCharts
import asyncio

# Initialize
if 'charts' not in st.session_state:
    st.session_state.charts = CryptoCharts(symbols=["BTCUSDT"])
    asyncio.run(st.session_state.charts.start())

# Get data
price_data = asyncio.run(st.session_state.charts.get_price("BTCUSDT"))
indicators = asyncio.run(st.session_state.charts.get_indicators("BTCUSDT"))

# Display
st.metric("BTC Price", f"${price_data['price']:.2f}")
st.metric("RSI", f"{indicators['RSI'].values[-1]:.2f}")
```

## Support

- GitHub Issues: https://github.com/livevnx8/hedera-realtime-charts/issues
- Documentation: https://github.com/livevnx8/hedera-realtime-charts
