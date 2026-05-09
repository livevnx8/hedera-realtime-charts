# Examples

This directory contains example code demonstrating how to use the Hedera Realtime Charts infrastructure.

## Quick Examples

### Simple Price Stream
```bash
python examples/simple_price_stream.py
```
Connects to Binance WebSocket and displays real-time price updates for BTC, ETH, HBAR, and SOL.

### Serialization Example
```bash
python examples/serialization_example.py
```
Demonstrates the performance benefits of MessagePack over JSON for data serialization.

### GPU Acceleration Example
```bash
python examples/gpu_acceleration_example.py
```
Shows GPU-accelerated data processing for price aggregation and volatility calculation.

## Use Case Examples

### Price Monitoring Dashboard
```bash
python examples/use_case_monitoring.py
```
Builds a simple monitoring dashboard that tracks multiple cryptocurrencies with real-time prices and latency metrics.

### Research - Correlation Analysis
```bash
python examples/use_case_research.py
```
Collects real-time price data and analyzes correlations between different cryptocurrencies for research purposes.

## Running Benchmarks

```bash
python -m src.benchmark
```
Runs comprehensive benchmarks on WebSocket latency, serialization performance, and GPU acceleration.

## Important Notes

- These examples are for **developer tooling and research purposes only**
- **NOT financial advice** - do not use for trading decisions
- Data is sourced from public APIs with no guarantees
- Rate limits may apply to external APIs
- See [DATA_DISCLAIMER.md](../DATA_DISCLAIMER.md) for full disclaimers

## Requirements

Install the package with dependencies:
```bash
pip install -e ".[dev]"
```

For GPU acceleration examples:
```bash
pip install -e ".[gpu]"
```
