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


GAPS = pd.DataFrame({
    "time": pd.date_range("2027-01-01", periods=8, freq="h"),
    "sun_elevation": [0.0] * 8,  # ignored: the illumination_fraction column wins
    "illumination_fraction": [1.0, 0.0, 0.0, 0.0, 0.5, 0.0, 0.0, 1.0],
    "earth_elevation": [1.0, -1.0, 1.0, -1.0, -1.0, 1.0, 1.0, 1.0],
    "earth_horizon": [0.0] * 8,
})


def test_longest_night_and_earth_absence_are_the_longest_runs():
    from src.metrics import longest_earth_absence, longest_night
    assert longest_night(GAPS) == 3.0  # a partly lit hour (0.5) ends the night
    assert longest_earth_absence(GAPS) == 2.0
    assert longest_earth_absence(GAPS, elevation_mask=1.5) == 8.0  # Earth never clears the mask
    assert longest_night(GAPS.assign(illumination_fraction=1.0)) == 0.0


def test_site_summary_is_the_site_card_grid():
    from src.metrics import site_summary
    assert site_summary(GAPS) == pytest.approx({"sunlight_pct": 100 * 2.5 / 8, "earth_visible_pct": 100 * 5 / 8,
                                                "longest_night_h": 3.0, "longest_earth_absence_h": 2.0})


def test_hourly_states_round_trip():
    from src.metrics import hourly_states
    states = hourly_states(GAPS)
    assert states.dtype == "uint8" and len(states) == len(GAPS)
    assert (states & 0x7F).tolist() == [100, 0, 0, 0, 50, 0, 0, 100]
    assert (states >> 7).astype(bool).tolist() == (GAPS["earth_elevation"] > 0).tolist()
