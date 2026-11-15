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
    ("Peak Near Shackleton", -88.811, 123.6901),
    ("Connecting Ridge Extension", -89.0324, -101.999),
    ("de Gerlache Rim 1", -88.6834, -67.9321),
    ("de Gerlache Rim 2", -88.23, -64.6284),
    ("de Gerlache-Kocher Massif", -85.8296, -116.322),
    ("Leibnitz Beta Plateau", -85.4266, 31.74276),
    ("Nobile Rim 1", -85.4381, 37.36667),
    ("Nobile Rim 2", -83.954, 58.82206),
    ("Amundsen Rim", -84.2287, 69.44396),
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


def test_region_identifiers_pages_and_historical_associations():
    from src.sites import ARTEMIS_2024_SOURCE
    expected = {
        "Peak Near Shackleton": (58, "R07 / Site07"),
        "Connecting Ridge Extension": (58, "SL3"),
        "de Gerlache Rim 1": (58, "R11 / Site11"),
        "de Gerlache Rim 2": (58, "SL2"),
        "de Gerlache-Kocher Massif": (58, "R42 / Site42"),
        "Leibnitz Beta Plateau": (58, "R20 / Site20"),
        "Nobile Rim 1": (58, "R06 / Site06"),
        "Nobile Rim 2": (57, "DM2"),
        "Amundsen Rim": (57, "DM1"),
    }
    assert len(LUNAR_SITES) == 17
    for key, (page, identifier) in expected.items():
        assert LUNAR_SITES[key]['source_location'] == f'Table A2-2, printed page {page}, {identifier}'
    for key in ['Haworth', 'Leibnitz Beta Plateau']:
        assert LUNAR_SITES[key]['exploration_source'] == ARTEMIS_2024_SOURCE
        assert '2022' in LUNAR_SITES[key]['exploration_context']
        assert '2024' in LUNAR_SITES[key]['exploration_context']
    assert 'Mons Mouton Plateau' in LUNAR_SITES['Leibnitz Beta Plateau']['scientific_context']
    for key in ['Connecting Ridge C1', 'Connecting Ridge C2']:
        assert LUNAR_SITES[key]['coordinate_kind'] == 'studied_point'
        assert (LUNAR_SITES[key]['lat'], LUNAR_SITES[key]['lon']) != (-89.4632, -137.49)
