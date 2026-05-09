# Architecture

System design and component relationships for the Hedera Realtime Charts infrastructure.

## High-Level Design

```
┌─────────────────────────────────────────────────────────────┐
│                     Data Sources                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Binance    │  │  CoinGecko   │  │   Kraken     │     │
│  │  WebSocket   │  │  REST API    │  │  WebSocket   │     │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘     │
└─────────┼──────────────────┼──────────────────┼─────────────┘
          │                  │                  │
          └──────────────────┼──────────────────┘
                             │
                    ┌────────▼────────┐
                    │  WebSocket      │  (binance_websocket.py)
                    │  Client         │
                    │  • Connection   │
                    │  • Parsing      │
                    │  • Latency Track│
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │  FastAPI Server │  (server.py)
                    │  • WebSocket    │
                    │  • REST API     │
                    │  • Broadcasting │
                    └────────┬────────┘
                             │
          ┌──────────────────┼──────────────────┐
          │                  │                  │
     ┌────▼────┐        ┌────▼────┐        ┌────▼────┐
     │ Streamlit│        │  React  │        │  Plotly │
     │ Frontend │        │ Frontend│        │ Frontend│
     └──────────┘        └─────────┘        └─────────┘
```

## Component Details

### 1. Binance WebSocket Client (`binance_websocket.py`)

**Purpose:** Low-latency WebSocket client for real-time price data from Binance.

**Design decisions:**
- Async WebSocket connection with websockets library
- Connection pooling and keep-alive
- Minimal processing at ingestion
- Latency tracking (time from exchange to reception)
- Automatic reconnection on failure

**Optimizations:**
- TCP_NODELAY and TCP_QUICKACK socket options
- Binary data parsing (minimal JSON overhead)
- Connection reuse for multiple streams

**Dependencies:** `websockets`, `aiohttp`

### 2. FastAPI Server (`server.py`)

**Purpose:** WebSocket server for broadcasting real-time price data to clients.

**Design decisions:**
- FastAPI with WebSocket support
- Connection manager for active clients
- Broadcast to all connected clients
- REST API for historical data
- CORS middleware for frontend integration

**Optimizations:**
- Uvicorn with uvloop for async performance
- Connection pooling
- In-memory price storage (no persistence)
- Sub-10ms broadcast latency target

**Dependencies:** `fastapi`, `uvicorn`, `websockets`

### 3. Serialization Layer (`serialization.py`)

**Purpose:** Binary serialization using MessagePack for minimal data overhead.

**Design decisions:**
- MessagePack for binary encoding (smaller than JSON)
- Use binary types for efficiency
- Fallback to JSON if needed
- Zero-copy deserialization where possible

**Benefits:**
- 30-50% smaller payload than JSON
- Faster serialization/deserialization
- Lower network bandwidth usage

**Dependencies:** `msgpack`

### 4. Socket Optimization (`socket_optimization.py`)

**Purpose:** TCP socket optimization for low-latency networking.

**Design decisions:**
- TCP_NODELAY to disable Nagle's algorithm
- TCP_QUICKACK for faster acknowledgments
- SO_KEEPALIVE for connection health
- Non-blocking mode for async operations

**Benefits:**
- Reduced latency (sub-10ms achievable)
- Better connection reliability
- Faster failure detection

**Dependencies:** Python stdlib only

### 5. GPU Acceleration (`gpu_acceleration.py`)

**Purpose:** GPU-accelerated data processing for faster computation.

**Design decisions:**
- CuPy for CUDA operations (if available)
- Fallback to NumPy if GPU unavailable
- Batch operations for efficiency
- Memory-efficient processing

**Benefits:**
- 10-100x faster for large datasets
- Sub-millisecond processing for aggregation
- Parallel computation for volatility calculations

**Dependencies:** `cupy` (optional), `numpy`

### 6. Streamlit Frontend (`frontend/app.py`)

**Purpose:** Real-time charting dashboard for visualization.

**Design decisions:**
- Streamlit for rapid development
- Plotly for interactive charts
- WebSocket client for real-time updates
- In-memory price history (deque with max length)

**Features:**
- Real-time line charts
- Multiple symbol support
- Dark mode enterprise UI
- Responsive design

**Dependencies:** `streamlit`, `plotly`, `websockets`

## Data Flow

```
1. Binance emits trade event via WebSocket
2. binance_websocket.py receives and parses
3. Latency calculated (exchange time vs reception time)
4. Price data passed to callback
5. FastAPI server broadcasts to all clients
6. Frontend receives update via WebSocket
7. Chart updates in real-time
8. GPU acceleration used for aggregation (if enabled)
```

## Performance Characteristics

| Component | Latency Target | Optimization |
|-----------|---------------|-------------|
| Binance WebSocket | < 10ms | TCP optimization |
| Server broadcast | < 5ms | In-memory storage |
| Serialization | < 1ms | MessagePack |
| GPU processing | < 1ms | CUDA kernels |
| Frontend update | < 50ms | Efficient rendering |

**End-to-end latency:** < 100ms from exchange to chart update (without GPU), < 20ms with GPU acceleration.

## Integration Points

### With hedera-ml-pipeline
- Can use HederaOnChainMetrics for HBAR on-chain data
- Correlate HBAR metrics with external crypto prices
- Combine risk management with real-time trading data

### With External APIs
- Binance WebSocket for real-time prices
- CoinGecko REST API for broader market data
- Kraken WebSocket for additional price feeds
- Custom exchange integrations possible

### With Custom Agents
- WebSocket API for agent consumption
- REST API for historical data
- GPU acceleration for agent inference
- Risk gate integration possible

## Deployment Architecture

### Development
- Local WebSocket server
- Streamlit frontend
- Direct Binance connection

### Production
- Docker containers
- Nginx reverse proxy
- Redis for horizontal scaling (optional)
- Geographic edge deployment (CDN)
- Load balancing with consistent hashing

## Security Considerations

- No private keys or credentials in this infrastructure
- Public data sources only
- Rate limiting on REST API
- CORS configuration for frontend
- WebSocket authentication (optional, future enhancement)

## Future Enhancements

- Add more data sources (Coinbase, Kraken, etc.)
- Implement order book visualization
- Add technical indicators (SMA, EMA, RSI)
- Integrate with hedera-ml-pipeline risk management
- Add alert/notification system
- Implement historical data storage
- Add multi-timeframe support
