"""Advanced technical indicators for crypto charting."""

import numpy as np
from typing import List, Dict, Tuple
from dataclasses import dataclass


@dataclass
class IndicatorResult:
    """Result of technical indicator calculation."""
    name: str
    values: List[float]
    signals: List[str]  # 'buy', 'sell', 'neutral'
    parameters: Dict


class TechnicalIndicators:
    """Advanced technical indicators for cryptocurrency analysis."""
    
    @staticmethod
    def calculate_rsi(prices: List[float], period: int = 14) -> IndicatorResult:
        """
        Calculate Relative Strength Index (RSI).
        
        RSI measures the magnitude of recent price changes to evaluate overbought or oversold conditions.
        - RSI > 70: Overbought (potential sell signal)
        - RSI < 30: Oversold (potential buy signal)
        """
        if len(prices) < period:
            return IndicatorResult(
                name="RSI",
                values=[50.0] * len(prices),
                signals=["neutral"] * len(prices),
                parameters={"period": period}
            )
        
        prices = np.array(prices)
        deltas = np.diff(prices)
        
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        
        avg_gain = np.convolve(gains, np.ones(period)/period, mode='valid')
        avg_loss = np.convolve(losses, np.ones(period)/period, mode='valid')
        
        rs = np.where(avg_loss == 0, 100, avg_gain / avg_loss)
        rsi = 100 - (100 / (1 + rs))
        
        # Pad with neutral values for initial period
        rsi_padded = np.concatenate([[50.0] * (period - 1), rsi])
        
        # Generate signals
        signals = []
        for val in rsi_padded:
            if val > 70:
                signals.append("sell")
            elif val < 30:
                signals.append("buy")
            else:
                signals.append("neutral")
        
        return IndicatorResult(
            name="RSI",
            values=rsi_padded.tolist(),
            signals=signals,
            parameters={"period": period}
        )
    
    @staticmethod
    def calculate_macd(prices: List[float], fast_period: int = 12, 
                      slow_period: int = 26, signal_period: int = 9) -> IndicatorResult:
        """
        Calculate Moving Average Convergence Divergence (MACD).
        
        MACD is a trend-following momentum indicator.
        - MACD line > Signal line: Bullish (potential buy)
        - MACD line < Signal line: Bearish (potential sell)
        """
        if len(prices) < slow_period:
            return IndicatorResult(
                name="MACD",
                values=[0.0] * len(prices),
                signals=["neutral"] * len(prices),
                parameters={"fast": fast_period, "slow": slow_period, "signal": signal_period}
            )
        
        prices = np.array(prices)
        
        # Calculate EMAs
        def ema(data, period):
            return np.convolve(data, np.exp(np.linspace(-1, 0, period)), mode='valid') / np.sum(np.exp(np.linspace(-1, 0, period)))
        
        ema_fast = ema(prices, fast_period)
        ema_slow = ema(prices, slow_period)
        
        # Align arrays
        min_len = min(len(ema_fast), len(ema_slow))
        ema_fast = ema_fast[-min_len:]
        ema_slow = ema_slow[-min_len:]
        
        macd_line = ema_fast - ema_slow
        signal_line = ema(macd_line, signal_period)
        
        # Align signal line
        signal_line = signal_line[-len(macd_line):]
        
        # Histogram
        histogram = macd_line - signal_line
        
        # Pad with zeros
        padding = len(prices) - len(histogram)
        histogram_padded = np.concatenate([[0.0] * padding, histogram])
        
        # Generate signals
        signals = []
        for i, hist in enumerate(histogram_padded):
            if i > 0:
                if histogram_padded[i-1] < 0 and hist > 0:
                    signals.append("buy")
                elif histogram_padded[i-1] > 0 and hist < 0:
                    signals.append("sell")
                else:
                    signals.append("neutral")
            else:
                signals.append("neutral")
        
        return IndicatorResult(
            name="MACD",
            values=histogram_padded.tolist(),
            signals=signals,
            parameters={"fast": fast_period, "slow": slow_period, "signal": signal_period}
        )
    
    @staticmethod
    def calculate_stochastic(prices: List[float], highs: List[float], lows: List[float], 
                           k_period: int = 14, d_period: int = 3) -> IndicatorResult:
        """
        Calculate Stochastic Oscillator.
        
        Stochastic oscillator compares a particular closing price of a security to a range of its prices over a certain period of time.
        - %K > 80: Overbought (potential sell)
        - %K < 20: Oversold (potential buy)
        """
        if len(prices) < k_period:
            return IndicatorResult(
                name="Stochastic",
                values=[50.0] * len(prices),
                signals=["neutral"] * len(prices),
                parameters={"k_period": k_period, "d_period": d_period}
            )
        
        prices = np.array(prices)
        highs = np.array(highs)
        lows = np.array(lows)
        
        # Calculate %K
        k_values = []
        for i in range(k_period - 1, len(prices)):
            high_window = highs[i - k_period + 1:i + 1]
            low_window = lows[i - k_period + 1:i + 1]
            current_close = prices[i]
            
            if high_window.max() == low_window.min():
                k = 50.0
            else:
                k = ((current_close - low_window.min()) / (high_window.max() - low_window.min())) * 100
            
            k_values.append(k)
        
        # Calculate %D (SMA of %K)
        d_values = []
        for i in range(d_period - 1, len(k_values)):
            d_values.append(np.mean(k_values[i - d_period + 1:i + 1]))
        
        # Pad with neutral values
        padding = len(prices) - len(k_values)
        k_padded = np.concatenate([[50.0] * padding, k_values])
        d_padded = np.concatenate([[50.0] * (padding + d_period - 1), d_values])
        
        # Use %K for signals
        signals = []
        for val in k_padded:
            if val > 80:
                signals.append("sell")
            elif val < 20:
                signals.append("buy")
            else:
                signals.append("neutral")
        
        return IndicatorResult(
            name="Stochastic",
            values=k_padded.tolist(),
            signals=signals,
            parameters={"k_period": k_period, "d_period": d_period}
        )
    
    @staticmethod
    def calculate_ema(prices: List[float], period: int = 20) -> IndicatorResult:
        """Calculate Exponential Moving Average (EMA)."""
        if len(prices) < period:
            return IndicatorResult(
                name="EMA",
                values=prices,
                signals=["neutral"] * len(prices),
                parameters={"period": period}
            )
        
        prices = np.array(prices)
        multiplier = 2 / (period + 1)
        ema = []
        
        # Start with SMA
        sma = np.mean(prices[:period])
        ema.append(sma)
        
        # Calculate EMA
        for price in prices[period:]:
            ema.append((price - ema[-1]) * multiplier + ema[-1])
        
        # Pad with initial prices
        ema_padded = np.concatenate([prices[:period - 1], ema])
        
        return IndicatorResult(
            name="EMA",
            values=ema_padded.tolist(),
            signals=["neutral"] * len(prices),
            parameters={"period": period}
        )
    
    @staticmethod
    def calculate_atr(highs: List[float], lows: List[float], closes: List[float], 
                     period: int = 14) -> IndicatorResult:
        """
        Calculate Average True Range (ATR).
        
        ATR measures market volatility.
        - Higher ATR: Higher volatility
        - Lower ATR: Lower volatility
        """
        if len(closes) < period:
            return IndicatorResult(
                name="ATR",
                values=[0.0] * len(closes),
                signals=["neutral"] * len(closes),
                parameters={"period": period}
            )
        
        highs = np.array(highs)
        lows = np.array(lows)
        closes = np.array(closes)
        
        # Calculate True Range
        tr = []
        for i in range(1, len(closes)):
            high_low = highs[i] - lows[i]
            high_close = abs(highs[i] - closes[i - 1])
            low_close = abs(lows[i] - closes[i - 1])
            tr.append(max(high_low, high_close, low_close))
        
        # Calculate ATR (EMA of TR)
        atr = []
        atr.append(np.mean(tr[:period]))
        
        for val in tr[period:]:
            atr.append((val - atr[-1]) / period + atr[-1])
        
        # Pad with zeros
        atr_padded = np.concatenate([[0.0] * (period), atr])
        
        return IndicatorResult(
            name="ATR",
            values=atr_padded.tolist(),
            signals=["neutral"] * len(closes),
            parameters={"period": period}
        )
    
    @staticmethod
    def calculate_all_indicators(prices: List[float], highs: List[float] = None, 
                                 lows: List[float] = None) -> Dict[str, IndicatorResult]:
        """
        Calculate all technical indicators.
        
        Args:
            prices: List of closing prices
            highs: List of high prices (optional, defaults to prices)
            lows: List of low prices (optional, defaults to prices)
        
        Returns:
            Dictionary of indicator results
        """
        if highs is None:
            highs = prices
        if lows is None:
            lows = prices
        
        return {
            "RSI": TechnicalIndicators.calculate_rsi(prices),
            "MACD": TechnicalIndicators.calculate_macd(prices),
            "Stochastic": TechnicalIndicators.calculate_stochastic(prices, highs, lows),
            "EMA20": TechnicalIndicators.calculate_ema(prices, 20),
            "EMA50": TechnicalIndicators.calculate_ema(prices, 50),
            "ATR": TechnicalIndicators.calculate_atr(highs, lows, prices),
        }
