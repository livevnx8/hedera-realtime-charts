"""
Example: GPU-accelerated data processing.

This example demonstrates the performance benefits of using GPU acceleration
for data processing tasks like price aggregation and volatility calculation.
"""

from gpu_acceleration import GPUAccelerator
import numpy as np
import time


def main():
    """Run the GPU acceleration example."""
    gpu = GPUAccelerator()
    
    print("=== GPU Acceleration Example ===\n")
    
    if gpu.cuda_available:
        print("✅ CUDA is available - using GPU acceleration")
    else:
        print("❌ CUDA not available - falling back to CPU")
    
    # Generate test data (1000 price points)
    prices = [50000.0 + np.random.randn() * 100 for _ in range(1000)]
    
    print(f"\nProcessing {len(prices)} price points\n")
    
    # Test price aggregation
    print("--- Price Aggregation (window=100) ---")
    start = time.perf_counter()
    aggregated = gpu.aggregate_prices(prices, window_size=100)
    agg_time = (time.perf_counter() - start) * 1000
    print(f"Aggregated price: ${aggregated:.2f}")
    print(f"Time: {agg_time:.4f}ms\n")
    
    # Test volatility calculation
    print("--- Volatility Calculation (window=100) ---")
    start = time.perf_counter()
    volatility = gpu.calculate_volatility(prices, window_size=100)
    vol_time = (time.perf_counter() - start) * 1000
    print(f"Volatility: ${volatility:.2f}")
    print(f"Time: {vol_time:.4f}ms\n")
    
    # Test batch normalization
    print("--- Batch Normalization (100 samples, 50 features each) ---")
    batch_data = [[np.random.randn() for _ in range(50)] for _ in range(100)]
    
    start = time.perf_counter()
    normalized = gpu.batch_normalize(batch_data)
    norm_time = (time.perf_counter() - start) * 1000
    print(f"Normalized {len(batch_data)} samples with {len(batch_data[0])} features")
    print(f"Time: {norm_time:.4f}ms")
    print(f"Sample normalized data: {normalized[0][:3]}...\n")
    
    print("=== Performance Summary ===")
    print(f"Aggregation: {agg_time:.4f}ms")
    print(f"Volatility: {vol_time:.4f}ms")
    print(f"Batch normalization: {norm_time:.4f}ms")


if __name__ == "__main__":
    main()
