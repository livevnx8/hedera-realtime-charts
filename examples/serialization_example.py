"""
Example: Binary serialization using MessagePack.

This example demonstrates the performance benefits of using MessagePack
over JSON for data serialization in low-latency applications.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from serialization import MessagePackSerializer
import json
import time


def main():
    """Run the serialization example."""
    serializer = MessagePackSerializer()
    
    # Example price data
    price_data = {
        "symbol": "BTCUSDT",
        "price": 50000.0,
        "quantity": 0.5,
        "time": 1234567890,
        "latency": 10.5,
    }
    
    print("=== Serialization Example ===\n")
    print(f"Original data: {price_data}\n")
    
    # MessagePack serialization
    start = time.perf_counter()
    msgpack_serialized = serializer.serialize(price_data)
    msgpack_time = (time.perf_counter() - start) * 1000
    
    start = time.perf_counter()
    msgpack_deserialized = serializer.deserialize(msgpack_serialized)
    msgpack_deserialize_time = (time.perf_counter() - start) * 1000
    
    print(f"MessagePack:")
    print(f"  Serialized size: {len(msgpack_serialized)} bytes")
    print(f"  Serialize time: {msgpack_time:.4f}ms")
    print(f"  Deserialize time: {msgpack_deserialize_time:.4f}ms")
    print(f"  Total time: {msgpack_time + msgpack_deserialize_time:.4f}ms")
    print(f"  Deserialized data: {msgpack_deserialized}\n")
    
    # JSON serialization
    start = time.perf_counter()
    json_serialized = json.dumps(price_data)
    json_time = (time.perf_counter() - start) * 1000
    
    start = time.perf_counter()
    json_deserialized = json.loads(json_serialized)
    json_deserialize_time = (time.perf_counter() - start) * 1000
    
    print(f"JSON:")
    print(f"  Serialized size: {len(json_serialized)} bytes")
    print(f"  Serialize time: {json_time:.4f}ms")
    print(f"  Deserialize time: {json_deserialize_time:.4f}ms")
    print(f"  Total time: {json_time + json_deserialize_time:.4f}ms")
    print(f"  Deserialized data: {json_deserialized}\n")
    
    # Comparison
    size_reduction = (1 - len(msgpack_serialized) / len(json_serialized)) * 100
    speedup = (json_time + json_deserialize_time) / (msgpack_time + msgpack_deserialize_time)
    
    print(f"=== Comparison ===")
    print(f"Size reduction: {size_reduction:.1f}%")
    print(f"Speedup: {speedup:.2f}x")


if __name__ == "__main__":
    main()
