#!/usr/bin/env python3
"""
VNX Unified Chart Server — Real-time price + prediction streaming.

Merges:
  - Binance WebSocket price ticks (~100ms)
  - VNX SQLite prediction DB (5-min swarm predictions)
  - Agent vote tracking

Broadcasts a unified WebSocket stream for the React dashboard.

Usage:
    uvicorn src.vnx_chart_server:app --host 0.0.0.0 --port 8010
"""

import asyncio
import json
import sqlite3
import sys
import time
from collections import defaultdict
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Dict, List, Optional, Set

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse

sys.path.insert(0, str(Path(__file__).parent))

from binance_websocket import BinanceWebSocket

# ── Configuration ───────────────────────────────────────────
VNX_DB_PATH = Path("/home/vera-live-0-1/hedera-llm-api/data/fast_predictions.db")
SYMBOLS = ["HBARUSDT"]  # Focus on HBAR for VNX
PORT = 8010

# ── State ───────────────────────────────────────────────────
active_connections: Set[WebSocket] = set()
price_data_dict: Dict[str, Dict] = defaultdict(dict)
candle_cache: Dict[str, List[Dict]] = defaultdict(list)  # OHLCV per symbol
last_prediction_id = 0
last_agent_weights: Dict[str, Dict] = {}


class ConnectionManager:
    async def connect(self, ws: WebSocket):
        await ws.accept()
        active_connections.add(ws)

    def disconnect(self, ws: WebSocket):
        active_connections.discard(ws)

    async def broadcast(self, message: dict):
        dead = set()
        for ws in active_connections:
            try:
                await ws.send_json(message)
            except Exception:
                dead.add(ws)
        for ws in dead:
            active_connections.discard(ws)


manager = ConnectionManager()


# ── Price Ingestion ─────────────────────────────────────────
async def price_callback(price_data: dict):
    """Handle incoming price ticks from Binance."""
    symbol = price_data["symbol"]
    ts = price_data.get("time", int(time.time() * 1000))

    price_data_dict[symbol] = {
        "price": price_data["price"],
        "quantity": price_data.get("quantity", 0),
        "time": ts,
    }

    # Build 1-minute candles
    _update_candle(symbol, ts, price_data["price"], price_data.get("quantity", 0))

    # Broadcast price tick
    await manager.broadcast({
        "type": "price_tick",
        "symbol": symbol,
        "price": price_data["price"],
        "timestamp": ts,
        "latency_ms": price_data.get("latency", 0),
    })


def _update_candle(symbol: str, ts: int, price: float, vol: float):
    """Aggregate ticks into 1-minute OHLCV candles."""
    minute_ts = (ts // 60000) * 60000
    candles = candle_cache[symbol]

    if not candles or candles[-1]["time"] != minute_ts:
        candles.append({
            "time": minute_ts,
            "open": price,
            "high": price,
            "low": price,
            "close": price,
            "volume": vol,
        })
        # Keep last 500 candles (~8 hours)
        if len(candles) > 500:
            candles.pop(0)
    else:
        c = candles[-1]
        c["high"] = max(c["high"], price)
        c["low"] = min(c["low"], price)
        c["close"] = price
        c["volume"] += vol


# ── Prediction Poller ─────────────────────────────────────────
async def watch_predictions():
    """Poll VNX SQLite DB for new predictions and broadcast."""
    global last_prediction_id, last_agent_weights

    while True:
        try:
            if not VNX_DB_PATH.exists():
                await asyncio.sleep(10)
                continue

            conn = sqlite3.connect(str(VNX_DB_PATH))
            conn.row_factory = sqlite3.Row

            # New predictions
            rows = conn.execute(
                "SELECT id, timestamp, iso_time, price_at_predict, direction, "
                "confidence, up_prob, pattern, pattern_confidence "
                "FROM fast_predictions WHERE id > ? ORDER BY id",
                (last_prediction_id,)
            ).fetchall()

            for row in rows:
                last_prediction_id = row["id"]

                # Fetch agent votes for this prediction
                votes = conn.execute(
                    "SELECT agent_name, score, vote_direction, correct "
                    "FROM agent_votes WHERE prediction_id = ?",
                    (row["id"],)
                ).fetchall()

                agent_details = {}
                for v in votes:
                    agent_details[v["agent_name"]] = {
                        "score": round(v["score"], 3),
                        "vote": v["vote_direction"],
                        "correct": v["correct"],
                    }

                await manager.broadcast({
                    "type": "prediction",
                    "symbol": "HBAR",
                    "direction": row["direction"],
                    "confidence": row["confidence"],
                    "up_probability": row["up_prob"],
                    "price_at_predict": row["price_at_predict"],
                    "timestamp": int(row["timestamp"] * 1000),
                    "iso_time": row["iso_time"],
                    "pattern": row["pattern"],
                    "pattern_confidence": row["pattern_confidence"],
                    "agents": agent_details,
                    "prediction_id": row["id"],
                })

            # Agent weights (cache, only broadcast if changed)
            weights = conn.execute(
                "SELECT agent_name, weight, total_votes, correct_votes, accuracy "
                "FROM agent_weights ORDER BY accuracy DESC"
            ).fetchall()

            new_weights = {}
            for w in weights:
                new_weights[w["agent_name"]] = {
                    "weight": round(w["weight"], 3),
                    "total_votes": w["total_votes"],
                    "correct_votes": w["correct_votes"],
                    "accuracy": round(w["accuracy"] or 0, 3),
                }

            if new_weights != last_agent_weights:
                last_agent_weights = new_weights
                await manager.broadcast({
                    "type": "agent_weights",
                    "weights": new_weights,
                })

            conn.close()

        except Exception as e:
            print(f"[watch_predictions] error: {e}")

        await asyncio.sleep(5)


# ── Accuracy Poller ───────────────────────────────────────────
async def watch_accuracy():
    """Broadcast rolling accuracy stats periodically."""
    while True:
        try:
            if not VNX_DB_PATH.exists():
                await asyncio.sleep(30)
                continue

            conn = sqlite3.connect(str(VNX_DB_PATH))
            conn.row_factory = sqlite3.Row

            total = conn.execute(
                "SELECT COUNT(*) FROM fast_predictions WHERE correct IS NOT NULL"
            ).fetchone()[0]
            correct = conn.execute(
                "SELECT COUNT(*) FROM fast_predictions WHERE correct = 1"
            ).fetchone()[0]
            overall = round(correct / total, 4) if total else 0

            r10 = conn.execute(
                "SELECT correct FROM fast_predictions WHERE correct IS NOT NULL "
                "ORDER BY timestamp DESC LIMIT 10"
            ).fetchall()
            l10 = round(sum(r[0] for r in r10) / len(r10), 4) if r10 else 0

            r50 = conn.execute(
                "SELECT correct FROM fast_predictions WHERE correct IS NOT NULL "
                "ORDER BY timestamp DESC LIMIT 50"
            ).fetchall()
            l50 = round(sum(r[0] for r in r50) / len(r50), 4) if r50 else 0

            conn.close()

            await manager.broadcast({
                "type": "accuracy",
                "overall": overall,
                "last_10": l10,
                "last_50": l50,
                "total_scored": total,
                "total_correct": correct,
                "timestamp": int(time.time() * 1000),
            })

        except Exception as e:
            print(f"[watch_accuracy] error: {e}")

        await asyncio.sleep(30)


# ── Binance Client ────────────────────────────────────────────
_binance_client: Optional[BinanceWebSocket] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup / shutdown lifecycle."""
    global _binance_client

    print("[VNX Chart Server] Starting...")

    # Start Binance WS
    try:
        _binance_client = BinanceWebSocket(
            symbols=SYMBOLS,
            callback=price_callback,
        )
        await _binance_client.connect()
        asyncio.create_task(_binance_client.listen())
        print(f"[Binance] Connected: {SYMBOLS}")
    except Exception as e:
        print(f"[Binance] Real connection failed: {e}")
        print("[Binance] Falling back to mock mode...")
        _binance_client = BinanceWebSocket(
            symbols=SYMBOLS,
            callback=price_callback,
            mock_mode=True,
        )
        await _binance_client.connect()
        asyncio.create_task(_binance_client.listen())

    # Start pollers
    asyncio.create_task(watch_predictions())
    asyncio.create_task(watch_accuracy())

    print(f"[VNX Chart Server] Ready on ws://localhost:{PORT}/ws/vnx")
    print(f"[VNX Chart Server] REST API: http://localhost:{PORT}/api/v1/")

    yield

    print("[VNX Chart Server] Shutting down...")
    if _binance_client:
        await _binance_client.close()


# ── FastAPI App ───────────────────────────────────────────────
app = FastAPI(
    title="VNX Chart Server",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/v1/prices")
async def get_prices():
    """Latest prices for all tracked symbols."""
    return dict(price_data_dict)


@app.get("/api/v1/candles/{symbol}")
async def get_candles(symbol: str, limit: int = 100):
    """OHLCV candles for a symbol."""
    return candle_cache.get(symbol.upper(), [])[-limit:]


@app.get("/api/v1/predictions")
async def get_predictions(limit: int = 50):
    """Last N VNX predictions with outcomes."""
    if not VNX_DB_PATH.exists():
        return {"predictions": []}
    conn = sqlite3.connect(str(VNX_DB_PATH))
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        "SELECT id, timestamp, iso_time, price_at_predict, direction, "
        "confidence, up_prob, correct, scored_at, pattern, pattern_confidence "
        "FROM fast_predictions ORDER BY timestamp DESC LIMIT ?",
        (limit,)
    ).fetchall()
    conn.close()
    return {"predictions": [dict(r) for r in rows]}


@app.get("/api/v1/agents")
async def get_agents():
    """Per-agent accuracy and adaptive weights."""
    if not VNX_DB_PATH.exists():
        return {"agents": []}
    conn = sqlite3.connect(str(VNX_DB_PATH))
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        "SELECT agent_name, weight, total_votes, correct_votes, accuracy "
        "FROM agent_weights ORDER BY accuracy DESC"
    ).fetchall()
    conn.close()
    return {"agents": [dict(r) for r in rows]}


@app.get("/api/v1/accuracy")
async def get_accuracy():
    """Rolling accuracy stats."""
    if not VNX_DB_PATH.exists():
        return {"message": "No data"}
    conn = sqlite3.connect(str(VNX_DB_PATH))
    conn.row_factory = sqlite3.Row
    total = conn.execute(
        "SELECT COUNT(*) FROM fast_predictions WHERE correct IS NOT NULL"
    ).fetchone()[0]
    correct = conn.execute(
        "SELECT COUNT(*) FROM fast_predictions WHERE correct = 1"
    ).fetchone()[0]
    r10 = conn.execute(
        "SELECT correct FROM fast_predictions WHERE correct IS NOT NULL "
        "ORDER BY timestamp DESC LIMIT 10"
    ).fetchall()
    l10 = round(sum(r[0] for r in r10) / len(r10), 4) if r10 else 0
    r50 = conn.execute(
        "SELECT correct FROM fast_predictions WHERE correct IS NOT NULL "
        "ORDER BY timestamp DESC LIMIT 50"
    ).fetchall()
    l50 = round(sum(r[0] for r in r50) / len(r50), 4) if r50 else 0
    conn.close()
    return {
        "overall": round(correct / total, 4) if total else 0,
        "last_10": l10,
        "last_50": l50,
        "total_scored": total,
        "total_correct": correct,
    }


@app.websocket("/ws/vnx")
async def websocket_endpoint(websocket: WebSocket):
    """Unified real-time stream: price ticks + predictions + accuracy."""
    await manager.connect(websocket)
    try:
        # Send initial state
        await websocket.send_json({
            "type": "init",
            "prices": dict(price_data_dict),
            "candles": {s: candle_cache[s][-100:] for s in candle_cache},
            "agent_weights": last_agent_weights,
        })

        # Keep alive, handle client pings
        while True:
            msg = await websocket.receive_text()
            if msg == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception:
        manager.disconnect(websocket)


@app.get("/")
async def root():
    return {
        "name": "VNX Chart Server",
        "version": "1.0.0",
        "endpoints": {
            "prices": "/api/v1/prices",
            "candles": "/api/v1/candles/{symbol}",
            "predictions": "/api/v1/predictions",
            "agents": "/api/v1/agents",
            "accuracy": "/api/v1/accuracy",
            "websocket": "/ws/vnx",
        },
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.vnx_chart_server:app",
        host="0.0.0.0",
        port=PORT,
        workers=1,
        loop="asyncio",
    )
