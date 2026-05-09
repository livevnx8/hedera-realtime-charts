# Getting Started

Quick start guide for the Hedera Realtime Charts infrastructure.

## Prerequisites

- Python 3.12+
- pip

## Installation

### Clone the repository

```bash
git clone https://github.com/livevnx8/hedera-realtime-charts.git
cd hedera-realtime-charts
```

### Install dependencies

```bash
# Basic installation
pip install -e ".[dev]"

# With GPU support (if you have NVIDIA CUDA)
pip install -e ".[gpu]"

# With frontend dependencies
pip install -e ".[frontend]"
```

## Quick Start

### 1. Start the WebSocket Server

```bash
python -m src.server
```

The server will start on `http://localhost:8000`

### 2. Start the Frontend

```bash
streamlit run frontend/app.py
```

The frontend will open at `http://localhost:8501`

### 3. Connect to WebSocket

In the frontend sidebar, click "Connect WebSocket" to start receiving real-time price data.

## Testing the WebSocket Server

You can test the WebSocket server without the frontend:

```bash
# Check the server status
curl http://localhost:8000/

# Get latest prices
curl http://localhost:8000/prices
```

## Testing Binance WebSocket Connection

Run the Binance WebSocket client directly:

```bash
python -m src.binance_websocket
```

This will print real-time price updates for BTC, ETH, HBAR, and SOL.

## Configuration

### Change Symbols

Edit `src/server.py` to change the symbols being tracked:

```python
binance_client = BinanceWebSocket(
    symbols=["BTCUSDT", "ETHUSDT", "HBARUSDT", "SOLUSDT"],
    callback=price_callback
)
```

### Enable GPU Acceleration

If you have NVIDIA CUDA, install the GPU dependencies:

```bash
pip install -e ".[gpu]"
```

GPU acceleration will be automatically used when available.

## Troubleshooting

### WebSocket Connection Failed

- Check that the server is running on port 8000
- Verify no firewall is blocking the connection
- Check the server logs for errors

### No Data in Frontend

- Verify the Binance WebSocket is connected
- Check the server logs for connection errors
- Ensure you clicked "Connect WebSocket" in the frontend

### GPU Not Available

- Verify CUDA is installed on your system
- Check that you installed the GPU dependencies
- The system will fall back to CPU processing automatically

## Next Steps

- Read the [Architecture documentation](docs/ARCHITECTURE.md)
- Explore the [source code](src/)
- Customize the frontend for your needs
- Add additional data sources
