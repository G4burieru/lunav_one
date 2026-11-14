"""Source-coordinate regressions and the Catalog Site integration contract."""
import math

import pytest

from src.sites import ILLUMINATION_SOURCE, LUNAR_SITES, POLAR_SOURCE


@pytest.mark.parametrize("key,lat,source_lon", [
    ("Connecting Ridge C1", -89.4398, 222.83),
    ("Connecting Ridge C2", -89.3130, 245.98),
    ("Shackleton Crater (Rim)", -89.6866, 197.19),
    ("Shackleton Rim S2", -89.7815, 204.70),
])
def test_table_2_points_and_east_longitude_conversion(key, lat, source_lon):
    site = LUNAR_SITES[key]
    assert site["lat"] == lat
    assert site["lon"] == pytest.approx(source_lon - 360)
    assert site["source_longitude_east_360"] == source_lon
    assert site["coordinate_source"] == ILLUMINATION_SOURCE
    assert site["coordinate_kind"] == "studied_point"
    assert site["study_asset_height_m"] == 2.0
    assert site["priority"] == "high"
    assert "Pending" in site["topographic_validation"]


@pytest.mark.parametrize("key,lat,lon", [
    ("Malapert Massif (Summit)", -85.9948, -0.23578),
    ("Faustini Crater (Rim)", -87.8897, 90.0),
    ("Haworth", -86.7639, -22.777),
])
def test_regional_coordinates_are_preserved_without_summit_claims(key, lat, lon):
    site = LUNAR_SITES[key]
    assert (site["lat"], site["lon"]) == (lat, lon)
    assert site["coordinate_kind"] == "region_center"
    assert site["coordinate_source"] == POLAR_SOURCE
    assert "not a measured summit" in site["coordinate_meaning"]


def test_legacy_identifiers_and_minimum_app_fields_remain_available():
    assert {"Shackleton Crater (Rim)", "Malapert Massif (Summit)",
            "Faustini Crater (Rim)", "Haworth", "Apollo 11 (Tranquility Base)"} <= LUNAR_SITES.keys()
    for site in LUNAR_SITES.values():
        assert math.isfinite(site["lat"]) and -90 <= site["lat"] <= 90
        assert math.isfinite(site["lon"]) and -180 <= site["lon"] <= 180
        for field in ("description", "name", "coordinate_source", "source_location",
                      "coordinate_kind", "coordinate_meaning", "coordinate_reference_frame",
                      "topographic_validation", "scientific_context", "exploration_context"):
            assert site[field]


def test_shackleton_replacement_is_distinct_from_old_region_center():
    site = LUNAR_SITES["Shackleton Crater (Rim)"]
    assert site["name"] == "Shackleton Rim S1"
    assert (site["lat"], site["lon"]) != (-89.7668, -171.87)
    assert "local catalog label" in site["source_location"]
    assert LUNAR_SITES["Apollo 11 (Tranquility Base)"]["coordinate_kind"] == "actual_landing"
