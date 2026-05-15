"""Unit tests for VNX Chart Server."""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from vnx_chart_server import StateManager


class TestStateManager:
    def test_initial_state(self):
        state = StateManager()
        assert state.active_connections == set()
        assert state.last_prediction_id == 0
        assert state.last_agent_weights == {}

    def test_update_candle_new_minute(self):
        state = StateManager()
        ts = 1_000_000_000_000  # Exact minute
        state.update_candle("HBARUSDT", ts, 0.1650, 1.0)

        candles = state.candle_cache["HBARUSDT"]
        assert len(candles) == 1
        assert candles[0]["open"] == 0.1650
        assert candles[0]["high"] == 0.1650
        assert candles[0]["low"] == 0.1650
        assert candles[0]["close"] == 0.1650
        assert candles[0]["volume"] == 1.0

    def test_update_candle_same_minute(self):
        state = StateManager()
        ts = 1_000_000_000_000
        state.update_candle("HBARUSDT", ts, 0.1650, 1.0)
        state.update_candle("HBARUSDT", ts, 0.1660, 2.0)
        state.update_candle("HBARUSDT", ts, 0.1640, 3.0)

        candles = state.candle_cache["HBARUSDT"]
        assert len(candles) == 1
        assert candles[0]["open"] == 0.1650
        assert candles[0]["high"] == 0.1660
        assert candles[0]["low"] == 0.1640
        assert candles[0]["close"] == 0.1640
        assert candles[0]["volume"] == 6.0

    def test_candle_rollover_limit(self):
        state = StateManager()
        base_ts = 1_000_000_000_000
        for i in range(502):
            state.update_candle("HBARUSDT", base_ts + i * 60000, 0.1650 + i * 0.0001, 1.0)

        assert len(state.candle_cache["HBARUSDT"]) == 500

    def test_price_data_storage(self):
        state = StateManager()
        state.price_data_dict["HBARUSDT"] = {"price": 0.1654, "quantity": 2.5, "time": 12345}

        assert state.price_data_dict["HBARUSDT"]["price"] == 0.1654

    def test_multiple_symbols(self):
        state = StateManager()
        state.update_candle("BTCUSDT", 1_000_000_000_000, 50000.0, 1.0)
        state.update_candle("ETHUSDT", 1_000_000_000_000, 3000.0, 1.0)

        assert len(state.candle_cache["BTCUSDT"]) == 1
        assert len(state.candle_cache["ETHUSDT"]) == 1
        assert state.candle_cache["BTCUSDT"][0]["close"] == 50000.0
        assert state.candle_cache["ETHUSDT"][0]["close"] == 3000.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
