# Hedera Realtime Charts

Ultra low-latency real-time crypto charting infrastructure with sub-10ms data processing, optimized networking, and enterprise-grade visualization capabilities.

## Features

- Sub-10ms latency with software optimization
- Sub-1ms latency with GPU acceleration for processing
- Binary serialization (MessagePack/protobuf)
- TCP socket optimization
- Connection pooling and multiplexing
- SIMD operations via numpy/numba
- GPU-accelerated data aggregation
- Real-time WebSocket streaming
- Enterprise-grade visualization

## Data Sources

- Binance WebSocket API (real-time prices)
- CoinGecko REST API (broader market data)
- Kraken WebSocket API (additional price feeds)
- Hedera Mirror Node (HBAR on-chain metrics via hedera-ml-pipeline)

## Technology Stack

### Backend
- Python 3.12+ with async/await
- FastAPI + websockets (uvicorn with optimized config)
- aiohttp for async HTTP
- Redis (in-memory, persistence disabled)
- pandas/numpy for data processing
- numba for JIT compilation
- ONNX Runtime for optimized inference (if needed)

### GPU Acceleration
- NVIDIA CUDA for parallel processing
- GPU-accelerated data aggregation
- CUDA kernels for custom operations
- ONNX Runtime with TensorRT (if available)

## Installation

```bash
pip install -e ".[dev]"
```

## Quick Start

```bash
# Start the WebSocket server
python -m src.server

# Start the frontend
streamlit run frontend/app.py
```

## Architecture

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for detailed architecture documentation.

## License

MIT
