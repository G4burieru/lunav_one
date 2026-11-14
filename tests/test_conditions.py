import numpy as np
import pytest

from src import catalog
from src.conditions import cell_corners, get_conditions, offset_from
from src.sites import LUNAR_SITES
from src.terrain import MOON_RADIUS_M


def test_offset_from_site_points_north():
    site = {"lat": -85.0, "lon": 10.0}
    east, north = offset_from(site, -85.0 + np.degrees(1000 / MOON_RADIUS_M), 10.0)
    assert east == pytest.approx(0.0, abs=1.0)
    assert north == pytest.approx(1000.0, rel=1e-3)


def _precomputed_site():
    for name, site in LUNAR_SITES.items():
        data = catalog.load_site(name, site)
        if data is not None and data[1] is not None:
            return name, site
    pytest.skip("no pre-computed catalog data for the current coordinates; run python -m scripts.precompute")


def test_catalog_site_uses_precomputed_data_offline():
    name, site = _precomputed_site()
    df = get_conditions(site["lat"], site["lon"], "2027-03-01", 7)
    assert df.attrs["source"] == "pre-computed" and df.attrs["site"] == name
    assert len(df) == 7 * 24
    assert {"sun_horizon", "earth_horizon", "illumination_fraction"} <= set(df.columns)
    assert df["illumination_fraction"].between(0, 1).all()


def test_neighborhood_summary_matches_get_conditions_at_the_site():
    from src.conditions import neighborhood_summary
    from src.metrics import earth_visible_hours, sunlight_hours
    name, site = _precomputed_site()
    summary = neighborhood_summary(name, "2027-03-01", 14)
    assert len(summary) == len(catalog.neighborhood_offsets()[0])
    centre = summary[(summary["east_m"] == 0) & (summary["north_m"] == 0)].iloc[0]
    assert centre["lat"] == pytest.approx(site["lat"], abs=1e-6)
    df = get_conditions(site["lat"], site["lon"], "2027-03-01", 14)
    assert centre["sunlight_pct"] == pytest.approx(100 * sunlight_hours(df) / len(df), abs=1e-6)
    assert centre["earth_visible_pct"] == pytest.approx(100 * earth_visible_hours(df) / len(df), abs=1e-6)


def test_neighborhood_points_round_trip_through_get_conditions():
    from src.conditions import neighborhood_summary
    name, _ = _precomputed_site()
    summary = neighborhood_summary(name, "2027-03-01", 7)
    best = summary.loc[summary["sunlight_pct"].idxmax()]
    df = get_conditions(best["lat"], best["lon"], "2027-03-01", 7)
    assert df.attrs["source"] == "pre-computed"
    assert 100 * df["illumination_fraction"].mean() == pytest.approx(best["sunlight_pct"], abs=1e-6)


def test_catalog_site_outside_the_pole_keeps_terrain_at_other_heights():
    for name, site in LUNAR_SITES.items():
        data = catalog.load_site(name, site)
        if site["lat"] > -80 and data is not None and data[1] is not None:
            break
    else:
        pytest.skip("no pre-computed catalog site outside 80°S")
    df = get_conditions(site["lat"], site["lon"], "2027-03-01", 7, asset_height=5.0)
    assert df.attrs["source"] == "pre-computed"
    assert "pre-computed for 2 m Asset Height" in df.attrs["terrain"]


def test_cell_corners_surround_each_neighborhood_point():
    site = LUNAR_SITES["Connecting Ridge C1"]
    corners = cell_corners(site, [0.0, 300.0], [0.0, -200.0])
    assert corners.shape == (2, 4, 2)
    offsets = np.array([offset_from(site, lat, lon) for lat, lon in corners[1]])
    np.testing.assert_allclose(offsets, [[250, -250], [350, -250], [350, -150], [250, -150]], atol=0.01)


def test_live_neighborhood_summary_matches_the_precomputed_one(monkeypatch):
    """With the pre-computed horizons and ephemerides, the live path gives the pre-computed Site Neighborhood."""
    from src import conditions
    key = "Connecting Ridge C1"
    site = LUNAR_SITES[key]
    ephemerides, neighborhood = catalog.load_site(key, site)
    monkeypatch.setattr(conditions, "get_ephemerides_data", lambda lat, lon, start, days: ephemerides)
    live = conditions.live_neighborhood_summary(site["lat"], site["lon"], neighborhood["horizons"], "2027-03-01", 14)
    precomputed = conditions.neighborhood_summary(key, "2027-03-01", 14)
    assert len(live) == len(precomputed)
    np.testing.assert_allclose(live[["east_m", "north_m", "sunlight_pct", "earth_visible_pct"]],
                               precomputed[["east_m", "north_m", "sunlight_pct", "earth_visible_pct"]])
