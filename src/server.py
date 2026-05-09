"""WebSocket server for real-time crypto price streaming."""

import asyncio
import json
import sys
from pathlib import Path
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from typing import Set, Dict
import time
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).parent))

from binance_websocket import BinanceWebSocket


app = FastAPI()

# CORS middleware for frontend connections
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store active WebSocket connections
active_connections: Set[WebSocket] = set()

# Store latest price data per symbol
price_data: Dict[str, Dict] = defaultdict(dict)


class ConnectionManager:
    """Manage WebSocket connections."""

    async def connect(self, websocket: WebSocket):
        """Accept a new WebSocket connection."""
        await websocket.accept()
        active_connections.add(websocket)

    def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection."""
        active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        """Broadcast a message to all connected clients."""
        for connection in active_connections:
            try:
                await connection.send_json(message)
            except:
                # Remove dead connections
                self.disconnect(connection)


manager = ConnectionManager()


async def price_callback(price_data: dict):
    """Callback for Binance price updates."""
    # Store the latest price data
    symbol = price_data["symbol"]
    price_data[symbol] = {
        "price": price_data["price"],
        "quantity": price_data["quantity"],
        "time": price_data["time"],
        "latency": price_data["latency"],
    }

    # Broadcast to all connected clients
    await manager.broadcast(price_data)


# Start Binance WebSocket connection
# Try real connection first, fall back to mock if blocked
binance_client = None
try:
    binance_client = BinanceWebSocket(
        symbols=["BTCUSDT", "ETHUSDT", "HBARUSDT", "SOLUSDT"],
        callback=price_callback
    )
except Exception:
    print("Will use mock mode for Binance WebSocket")
    binance_client = BinanceWebSocket(
        symbols=["BTCUSDT", "ETHUSDT", "HBARUSDT", "SOLUSDT"],
        callback=price_callback,
        mock_mode=True
    )


@app.on_event("startup")
async def startup_event():
    """Start the Binance WebSocket connection on startup."""
    try:
        await binance_client.connect()
        asyncio.create_task(binance_client.listen())
    except Exception as e:
        print(f"Connection failed: {e}")
        print("Already using mock mode or will use mock mode")


@app.on_event("shutdown")
async def shutdown_event():
    """Close the Binance WebSocket connection on shutdown."""
    await binance_client.close()


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "status": "running",
        "connections": len(active_connections),
        "symbols": list(price_data.keys()),
    }


@app.get("/prices")
async def get_prices():
    """Get the latest prices for all symbols."""
    return dict(price_data)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time price streaming."""
    await manager.connect(websocket)
    try:
        # Send initial prices
        await websocket.send_json({"type": "init", "data": dict(price_data)})
        
        # Keep connection alive and handle any client messages
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)


if __name__ == "__main__":
    import uvicorn
    
    # Run with optimized uvicorn settings for low latency
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=8000,
        workers=1,
        loop="asyncio",  # Use asyncio instead of uvloop for compatibility
        limit_concurrency=1000,
        timeout_keep_alive=30,
    )
