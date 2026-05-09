"""Benchmarking for ultra low-latency crypto charting infrastructure."""

import time
import asyncio
import statistics
from typing import List, Dict
import json
from collections import defaultdict

from binance_websocket import BinanceWebSocket
from serialization import MessagePackSerializer
from socket_optimization import OptimizedSocket
from gpu_acceleration import GPUAccelerator


class Benchmark:
    """Benchmark various components of the infrastructure."""

    def __init__(self):
        self.results: Dict[str, List[float]] = defaultdict(list)
        self.serializer = MessagePackSerializer()
        self.gpu = GPUAccelerator()

    async def benchmark_websocket_latency(self, iterations: int = 100):
        """Benchmark WebSocket connection latency."""
        print("Benchmarking WebSocket latency...")
        
        latencies = []
        
        async def callback(price_data: Dict):
            latencies.append(price_data["latency"])
            if len(latencies) >= iterations:
                return True
            return False
        
        client = BinanceWebSocket(["BTCUSDT"], callback)
        
        try:
            await client.connect()
            await client.listen()
        except:
            pass
        finally:
            await client.close()
        
        if latencies:
            self.results["websocket_latency"] = latencies
            print(f"WebSocket latency: {statistics.mean(latencies):.2f}ms (avg), {statistics.stdev(latencies):.2f}ms (std)")

    def benchmark_serialization(self, iterations: int = 1000):
        """Benchmark MessagePack serialization vs JSON."""
        print("Benchmarking serialization...")
        
        test_data = {
            "symbol": "BTCUSDT",
            "price": 50000.0,
            "quantity": 0.5,
            "time": 1234567890,
            "latency": 10.5,
        }
        
        # Benchmark MessagePack
        msgpack_times = []
        for _ in range(iterations):
            start = time.perf_counter()
            serialized = self.serializer.serialize(test_data)
            deserialized = self.serializer.deserialize(serialized)
            end = time.perf_counter()
            msgpack_times.append((end - start) * 1000)
        
        # Benchmark JSON
        json_times = []
        for _ in range(iterations):
            start = time.perf_counter()
            serialized = json.dumps(test_data)
            deserialized = json.loads(serialized)
            end = time.perf_counter()
            json_times.append((end - start) * 1000)
        
        self.results["msgpack_serialization"] = msgpack_times
        self.results["json_serialization"] = json_times
        
        print(f"MessagePack: {statistics.mean(msgpack_times):.4f}ms (avg)")
        print(f"JSON: {statistics.mean(json_times):.4f}ms (avg)")
        print(f"Speedup: {statistics.mean(json_times) / statistics.mean(msgpack_times):.2f}x")

    def benchmark_gpu_vs_cpu(self, iterations: int = 100):
        """Benchmark GPU acceleration vs CPU."""
        print("Benchmarking GPU vs CPU...")
        
        # Generate test data
        prices = [50000.0 + i * 100 for i in range(100)]
        
        # CPU aggregation
        cpu_times = []
        for _ in range(iterations):
            start = time.perf_counter()
            result = self.gpu.aggregate_prices(prices)
            end = time.perf_counter()
            cpu_times.append((end - start) * 1000)
        
        # GPU aggregation (if available)
        if self.gpu.cuda_available:
            gpu_times = []
            for _ in range(iterations):
                start = time.perf_counter()
                result = self.gpu.aggregate_prices(prices)
                end = time.perf_counter()
                gpu_times.append((end - start) * 1000)
            
            self.results["gpu_aggregation"] = gpu_times
            print(f"GPU aggregation: {statistics.mean(gpu_times):.4f}ms (avg)")
            print(f"CPU aggregation: {statistics.mean(cpu_times):.4f}ms (avg)")
            print(f"Speedup: {statistics.mean(cpu_times) / statistics.mean(gpu_times):.2f}x")
        else:
            print("GPU not available, CPU only")
            self.results["cpu_aggregation"] = cpu_times

    def save_results(self, filename: str = "benchmark_results.json"):
        """Save benchmark results to file."""
        results = {
            "websocket_latency": {
                "avg_ms": statistics.mean(self.results.get("websocket_latency", [0])),
                "std_ms": statistics.stdev(self.results.get("websocket_latency", [0])),
                "min_ms": min(self.results.get("websocket_latency", [0])),
                "max_ms": max(self.results.get("websocket_latency", [0])),
            },
            "msgpack_serialization": {
                "avg_ms": statistics.mean(self.results.get("msgpack_serialization", [0])),
                "std_ms": statistics.stdev(self.results.get("msgpack_serialization", [0])),
            },
            "json_serialization": {
                "avg_ms": statistics.mean(self.results.get("json_serialization", [0])),
                "std_ms": statistics.stdev(self.results.get("json_serialization", [0])),
            },
        }
        
        if "gpu_aggregation" in self.results:
            results["gpu_aggregation"] = {
                "avg_ms": statistics.mean(self.results["gpu_aggregation"]),
                "std_ms": statistics.stdev(self.results["gpu_aggregation"]),
            }
        
        if "cpu_aggregation" in self.results:
            results["cpu_aggregation"] = {
                "avg_ms": statistics.mean(self.results["cpu_aggregation"]),
                "std_ms": statistics.stdev(self.results["cpu_aggregation"]),
            }
        
        with open(filename, "w") as f:
            json.dump(results, f, indent=2)
        
        print(f"Results saved to {filename}")

    def print_summary(self):
        """Print benchmark summary."""
        print("\n=== Benchmark Summary ===")
        
        if "websocket_latency" in self.results:
            latencies = self.results["websocket_latency"]
            print(f"WebSocket Latency: {statistics.mean(latencies):.2f}ms avg, {statistics.p50(latencies):.2f}ms p50, {statistics.p95(latencies):.2f}ms p95")
        
        if "msgpack_serialization" in self.results and "json_serialization" in self.results:
            msgpack = self.results["msgpack_serialization"]
            json_data = self.results["json_serialization"]
            print(f"MessagePack: {statistics.mean(msgpack):.4f}ms avg")
            print(f"JSON: {statistics.mean(json_data):.4f}ms avg")
            print(f"MessagePack is {statistics.mean(json_data) / statistics.mean(msgpack):.2f}x faster")


async def main():
    """Run all benchmarks."""
    benchmark = Benchmark()
    
    # Run benchmarks
    benchmark.benchmark_serialization(iterations=1000)
    benchmark.benchmark_gpu_vs_cpu(iterations=100)
    await benchmark.benchmark_websocket_latency(iterations=50)
    
    # Save and print results
    benchmark.save_results()
    benchmark.print_summary()


if __name__ == "__main__":
    asyncio.run(main())
