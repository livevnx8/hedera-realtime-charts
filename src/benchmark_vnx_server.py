#!/usr/bin/env python3
"""
Benchmark VNX Chart Server end-to-end latency.

Measures:
  1. Tick receipt → candle update latency
  2. Candle update → WebSocket broadcast latency
  3. SQLite query time for predictions
  4. Full round-trip: mock tick → client receive

Usage:
    python src/benchmark_vnx_server.py
"""

import asyncio
import json
import statistics
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from vnx_chart_server import StateManager, VNX_DB_PATH, price_callback, watch_predictions


class LatencyBenchmark:
    def __init__(self, iterations: int = 100):
        self.iterations = iterations
        self.tick_to_candle_ms: list[float] = []
        self.broadcast_ms: list[float] = []
        self.sqlite_query_ms: list[float] = []
        self.round_trip_ms: list[float] = []
        self.state = StateManager()

    async def benchmark_tick_to_candle(self):
        """Measure time from price tick to candle update."""
        print("\n[1/4] Benchmarking tick → candle aggregation...")
        for _ in range(self.iterations):
            ts = int(time.time() * 1000)
            price = 0.1650 + (_ % 10) * 0.0001

            t0 = time.perf_counter()
            self.state.update_candle("HBARUSDT", ts, price, 1.0)
            t1 = time.perf_counter()

            self.tick_to_candle_ms.append((t1 - t0) * 1000)

        avg = statistics.mean(self.tick_to_candle_ms)
        p95 = self._percentile(self.tick_to_candle_ms, 95)
        print(f"  Average: {avg:.4f}ms | P95: {p95:.4f}ms")

    async def benchmark_broadcast(self):
        """Measure WebSocket broadcast time (no real clients)."""
        print("\n[2/4] Benchmarking broadcast latency...")
        for _ in range(self.iterations):
            msg = {
                "type": "price_tick",
                "symbol": "HBARUSDT",
                "price": 0.1654,
                "timestamp": int(time.time() * 1000),
                "latency_ms": 12.0,
            }

            t0 = time.perf_counter()
            await self.state.broadcast(msg)
            t1 = time.perf_counter()

            self.broadcast_ms.append((t1 - t0) * 1000)

        avg = statistics.mean(self.broadcast_ms)
        p95 = self._percentile(self.broadcast_ms, 95)
        print(f"  Average: {avg:.4f}ms | P95: {p95:.4f}ms")

    async def benchmark_sqlite_query(self):
        """Measure SQLite query time for predictions + agent weights."""
        print("\n[3/4] Benchmarking SQLite query latency...")
        if not VNX_DB_PATH.exists():
            print(f"  SKIP: DB not found at {VNX_DB_PATH}")
            return

        import sqlite3

        for _ in range(min(self.iterations, 20)):  # Don't hammer DB too hard
            conn = sqlite3.connect(str(VNX_DB_PATH))
            conn.row_factory = sqlite3.Row

            t0 = time.perf_counter()
            conn.execute(
                "SELECT id, timestamp, direction, confidence FROM fast_predictions "
                "ORDER BY timestamp DESC LIMIT 50"
            ).fetchall()
            conn.execute(
                "SELECT agent_name, weight, accuracy FROM agent_weights ORDER BY accuracy DESC"
            ).fetchall()
            t1 = time.perf_counter()

            self.sqlite_query_ms.append((t1 - t0) * 1000)
            conn.close()

        avg = statistics.mean(self.sqlite_query_ms)
        p95 = self._percentile(self.sqlite_query_ms, 95)
        print(f"  Average: {avg:.4f}ms | P95: {p95:.4f}ms")

    async def benchmark_round_trip(self):
        """Simulate full round-trip through price_callback."""
        print("\n[4/4] Benchmarking full round-trip (tick → candle → broadcast)...")
        for _ in range(self.iterations):
            price_data = {
                "symbol": "HBARUSDT",
                "price": 0.1654 + (_ % 5) * 0.0001,
                "quantity": 1.5,
                "time": int(time.time() * 1000),
                "latency": 15.0,
            }

            t0 = time.perf_counter()
            await price_callback(price_data)
            t1 = time.perf_counter()

            self.round_trip_ms.append((t1 - t0) * 1000)

        avg = statistics.mean(self.round_trip_ms)
        p95 = self._percentile(self.round_trip_ms, 95)
        print(f"  Average: {avg:.4f}ms | P95: {p95:.4f}ms")

    @staticmethod
    def _percentile(data: list[float], p: float) -> float:
        if not data:
            return 0.0
        sorted_data = sorted(data)
        idx = int((p / 100) * (len(sorted_data) - 1))
        return sorted_data[idx]

    def print_summary(self):
        print("\n" + "=" * 50)
        print("VNX Chart Server Latency Benchmark")
        print("=" * 50)

        if self.tick_to_candle_ms:
            print(f"\n  Tick → Candle:     {statistics.mean(self.tick_to_candle_ms):.4f}ms avg")
        if self.broadcast_ms:
            print(f"  Broadcast (empty):   {statistics.mean(self.broadcast_ms):.4f}ms avg")
        if self.sqlite_query_ms:
            print(f"  SQLite Query:        {statistics.mean(self.sqlite_query_ms):.4f}ms avg")
        if self.round_trip_ms:
            print(f"  Full Round-Trip:     {statistics.mean(self.round_trip_ms):.4f}ms avg")

        total = 0
        counts = 0
        for arr in [self.tick_to_candle_ms, self.broadcast_ms, self.round_trip_ms]:
            if arr:
                total += statistics.mean(arr)
                counts += 1

        if counts > 0:
            print(f"\n  Combined Core Latency: {total:.4f}ms")
            status = "✅ Sub-50ms" if total < 50 else ("⚠️ Sub-100ms" if total < 100 else "❌ >100ms")
            print(f"  Status: {status}")

        print("=" * 50)


async def main():
    bench = LatencyBenchmark(iterations=200)
    await bench.benchmark_tick_to_candle()
    await bench.benchmark_broadcast()
    await bench.benchmark_sqlite_query()
    await bench.benchmark_round_trip()
    bench.print_summary()


if __name__ == "__main__":
    asyncio.run(main())
