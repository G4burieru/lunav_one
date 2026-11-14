import pandas as pd
import pytest

from src.metrics import earth_visible_hours, hours_until_earthset, hours_until_sunset, sunlight_hours
from src.terrain import SUN_RADIUS_DEG

DF = pd.DataFrame({
    "time": pd.date_range("2026-12-01", periods=5, freq="h"),
    "sun_elevation": [2.0, 1.0, -1.0, -2.0, 1.0],
    "earth_elevation": [1.0, 2.0, 3.0, 4.0, 5.0],
})


def test_sunset_is_when_the_top_of_the_disk_crosses_the_horizon():
    # The top limb (elevation + disk radius) goes from +1.27° at 01:00 to -0.73° at 02:00.
    margin = 1.0 + SUN_RADIUS_DEG
    expected = 1.0 + margin / (margin - (-1.0 + SUN_RADIUS_DEG))
    assert hours_until_sunset(DF, "2026-12-01 00:00") == pytest.approx(expected)


def test_terrain_horizon_brings_sunset_earlier():
    with_terrain = DF.assign(sun_horizon=1.5)
    assert hours_until_sunset(with_terrain, "2026-12-01 00:00") < hours_until_sunset(DF, "2026-12-01 00:00")


def test_already_set_returns_zero():
    assert hours_until_sunset(DF, "2026-12-01 03:00") == 0.0


def test_no_set_within_window_returns_none():
    assert hours_until_earthset(DF, "2026-12-01 00:00") is None


def test_elevation_mask_brings_earthset_earlier():
    # Earth elevation minus a 1.5° mask goes from -0.5° at 00:00 (already below), so Earthset is now.
    assert hours_until_earthset(DF, "2026-12-01 00:00", elevation_mask=1.5) == 0.0


def test_instant_outside_window_returns_none():
    assert hours_until_sunset(DF, "2026-12-02 00:00") is None


def test_visibility_hours():
    assert earth_visible_hours(DF) == 5.0
    assert earth_visible_hours(DF, elevation_mask=2.5) == 3.0
    assert sunlight_hours(DF.assign(illumination_fraction=[1.0, 0.5, 0.0, 0.0, 1.0])) == 2.5


def test_monthly_summary_groups_by_calendar_month():
    from src.metrics import monthly_summary
    df = pd.DataFrame({
        "time": pd.to_datetime(["2027-01-31 22:00", "2027-01-31 23:00", "2027-02-01 00:00", "2027-02-01 01:00"]),
        "sun_elevation": [1.0, 1.0, -1.0, -1.0],
        "earth_elevation": [1.0, -1.0, 1.0, 1.0],
        "illumination_fraction": [1.0, 0.5, 0.0, 0.0],
    })
    summary = monthly_summary(df)
    assert list(summary.index.month) == [1, 2]
    assert summary["sunlight_pct"].tolist() == [75.0, 0.0]
    assert summary["earth_visible_pct"].tolist() == [50.0, 100.0]
    assert summary["hours"].tolist() == [2.0, 2.0]
