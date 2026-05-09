"""GPU acceleration for data processing using CUDA."""

import numpy as np
from typing import Optional, List, Dict


class GPUAccelerator:
    """GPU-accelerated data processing for low-latency operations."""

    def __init__(self):
        """Initialize GPU accelerator."""
        self.cuda_available = self._check_cuda()
        if self.cuda_available:
            try:
                import cupy as cp
                self.cp = cp
                print("CUDA initialized successfully")
            except ImportError:
                print("CuPy not installed, falling back to NumPy")
                self.cuda_available = False
                self.cp = None

    def _check_cuda(self) -> bool:
        """Check if CUDA is available."""
        try:
            import cupy as cp
            cp.cuda.Device(0).compute_capability
            return True
        except:
            return False

    def aggregate_prices(self, prices: List[float], window_size: int = 10) -> float:
        """
        Aggregate prices using GPU for faster computation.

        Args:
            prices: List of price values
            window_size: Window size for aggregation

        Returns:
            Aggregated price
        """
        if self.cuda_available and len(prices) >= window_size:
            # Use GPU for computation
            prices_array = self.cp.array(prices[-window_size:])
            result = float(self.cp.mean(prices_array))
        else:
            # Fallback to CPU
            prices_array = np.array(prices[-window_size:])
            result = float(np.mean(prices_array))
        
        return result

    def calculate_volatility(self, prices: List[float], window_size: int = 20) -> float:
        """
        Calculate price volatility using GPU.

        Args:
            prices: List of price values
            window_size: Window size for calculation

        Returns:
            Volatility (standard deviation)
        """
        if self.cuda_available and len(prices) >= window_size:
            prices_array = self.cp.array(prices[-window_size:])
            result = float(self.cp.std(prices_array))
        else:
            prices_array = np.array(prices[-window_size:])
            result = float(np.std(prices_array))
        
        return result

    def batch_normalize(self, data: List[List[float]]) -> List[List[float]]:
        """
        Normalize a batch of data using GPU.

        Args:
            data: List of data arrays

        Returns:
            Normalized data
        """
        if self.cuda_available:
            data_array = self.cp.array(data)
            mean = self.cp.mean(data_array, axis=1, keepdims=True)
            std = self.cp.std(data_array, axis=1, keepdims=True)
            normalized = (data_array - mean) / (std + 1e-8)
            return normalized.tolist()
        else:
            data_array = np.array(data)
            mean = np.mean(data_array, axis=1, keepdims=True)
            std = np.std(data_array, axis=1, keepdims=True)
            normalized = (data_array - mean) / (std + 1e-8)
            return normalized.tolist()


# Example usage
if __name__ == "__main__":
    accelerator = GPUAccelerator()
    
    # Test data
    prices = [50000.0, 50100.0, 50200.0, 50300.0, 50400.0]
    
    # Aggregate prices
    aggregated = accelerator.aggregate_prices(prices)
    print(f"Aggregated price: {aggregated}")
    
    # Calculate volatility
    volatility = accelerator.calculate_volatility(prices)
    print(f"Volatility: {volatility}")
