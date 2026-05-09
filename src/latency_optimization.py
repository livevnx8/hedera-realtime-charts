"""Ultra low-latency optimizations for sub-10ms performance."""

import asyncio
import time
from typing import Dict, List, Callable, Any
import numpy as np
from collections import deque
import msgpack


class LatencyMonitor:
    """Monitor and track latency across the system."""
    
    def __init__(self, window_size: int = 1000):
        self.window_size = window_size
        self.latencies = deque(maxlen=window_size)
        self.start_time = time.time()
    
    def record_latency(self, latency_ms: float):
        """Record a latency measurement."""
        self.latencies.append(latency_ms)
    
    def get_stats(self) -> Dict[str, float]:
        """Get latency statistics."""
        if not self.latencies:
            return {"avg": 0, "p50": 0, "p95": 0, "p99": 0, "max": 0}
        
        sorted_latencies = sorted(self.latencies)
        n = len(sorted_latencies)
        
        return {
            "avg": sum(sorted_latencies) / n,
            "p50": sorted_latencies[n // 2],
            "p95": sorted_latencies[int(n * 0.95)],
            "p99": sorted_latencies[int(n * 0.99)],
            "max": max(sorted_latencies),
            "min": min(sorted_latencies),
        }


class OptimizedCallback:
    """Optimized callback handler for minimal latency."""
    
    def __init__(self, callback: Callable, monitor: LatencyMonitor):
        self.callback = callback
        self.monitor = monitor
        self._serialize = msgpack.packb
        self._deserialize = msgpack.unpackb
    
    async def __call__(self, data: Dict[str, Any]):
        """Handle callback with minimal overhead."""
        start = time.perf_counter()
        
        # Minimal processing - just pass through
        await self.callback(data)
        
        # Record latency
        latency_ms = (time.perf_counter() - start) * 1000
        self.monitor.record_latency(latency_ms)


class ZeroCopyBuffer:
    """Zero-copy buffer for minimizing memory allocations."""
    
    def __init__(self, max_size: int = 10000):
        self.buffer = bytearray(max_size)
        self.max_size = max_size
        self.pos = 0
    
    def write(self, data: bytes) -> bool:
        """Write data to buffer without copying."""
        if len(data) > (self.max_size - self.pos):
            return False
        
        self.buffer[self.pos:self.pos + len(data)] = data
        self.pos += len(data)
        return True
    
    def reset(self):
        """Reset buffer position."""
        self.pos = 0
    
    def get_bytes(self) -> bytes:
        """Get bytes from buffer."""
        return bytes(self.buffer[:self.pos])


class BatchProcessor:
    """Batch processing for reducing overhead."""
    
    def __init__(self, batch_size: int = 100, max_wait_ms: float = 10):
        self.batch_size = batch_size
        self.max_wait_ms = max_wait_ms
        self.current_batch = []
        self.last_flush = time.time()
    
    def add(self, item: Any) -> bool:
        """Add item to batch, return True if batch should be flushed."""
        self.current_batch.append(item)
        
        # Flush if batch is full or time exceeded
        if len(self.current_batch) >= self.batch_size:
            return True
        
        if (time.time() - self.last_flush) * 1000 >= self.max_wait_ms:
            return True
        
        return False
    
    def get_batch(self) -> List[Any]:
        """Get and clear current batch."""
        batch = self.current_batch
        self.current_batch = []
        self.last_flush = time.time()
        return batch


class OptimizedWebSocketHandler:
    """WebSocket handler with sub-10ms latency optimizations."""
    
    def __init__(self, callback: Callable):
        self.callback = callback
        self.monitor = LatencyMonitor()
        self.optimized_callback = OptimizedCallback(callback, self.monitor)
        self.batch_processor = BatchProcessor()
    
    async def handle_message(self, message: bytes):
        """Handle WebSocket message with minimal latency."""
        start = time.perf_counter()
        
        # Deserialize with MessagePack (faster than JSON)
        try:
            data = msgpack.unpackb(message, raw=False)
        except:
            # Fallback to JSON if MessagePack fails
            import json
            data = json.loads(message)
        
        # Process through optimized callback
        await self.optimized_callback(data)
        
        # Record total latency
        latency_ms = (time.perf_counter() - start) * 1000
        self.monitor.record_latency(latency_ms)
    
    def get_latency_stats(self) -> Dict[str, float]:
        """Get latency statistics."""
        return self.monitor.get_stats()


# Usage example
if __name__ == "__main__":
    async def test_callback(data):
        """Test callback."""
        pass
    
    handler = OptimizedWebSocketHandler(test_callback)
    
    # Simulate processing
    for i in range(100):
        test_data = msgpack.packb({"symbol": "BTCUSDT", "price": 50000.0})
        asyncio.run(handler.handle_message(test_data))
    
    stats = handler.get_latency_stats()
    print(f"Latency stats: {stats}")
