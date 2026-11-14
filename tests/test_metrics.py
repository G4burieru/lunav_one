import pandas as pd
import pytest

from src.metrics import hours_until_earthset, hours_until_sunset

DF = pd.DataFrame({
    "time": pd.date_range("2026-12-01", periods=5, freq="h"),
    "sun_elevation": [2.0, 1.0, -1.0, -2.0, 1.0],
    "earth_elevation": [1.0, 2.0, 3.0, 4.0, 5.0],
})


def test_sunset_interpolates_horizon_crossing():
    # Elevation goes from +1° at 01:00 to -1° at 02:00, so it crosses 0° at 01:30.
    assert hours_until_sunset(DF, "2026-12-01 00:00") == pytest.approx(1.5)


def test_already_below_horizon_returns_zero():
    assert hours_until_sunset(DF, "2026-12-01 03:00") == 0.0


def test_no_set_within_window_returns_none():
    assert hours_until_earthset(DF, "2026-12-01 00:00") is None


def test_instant_outside_window_returns_none():
    assert hours_until_sunset(DF, "2026-12-02 00:00") is None
