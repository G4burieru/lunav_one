"""Catalog/map integration checks; no scientific service required."""
import pytest

from src.site_map import plot_south_pole_map
from src.sites import LUNAR_SITES


def test_named_selection_and_legacy_app_call_agree():
    site = LUNAR_SITES["Haworth"]
    named = plot_south_pole_map("Haworth")
    legacy = plot_south_pole_map(LUNAR_SITES, site["lat"], site["lon"])
    assert list(named.data[1].r) == list(legacy.data[1].r) == [90 + site["lat"]]
    assert list(named.data[1].theta) == [-22.777]
    assert len(named.data[0].r) == sum(-90 <= site["lat"] <= -80 for site in LUNAR_SITES.values())
    assert "Apollo 11 (Tranquility Base)" not in named.data[0].text


def test_equatorial_selection_is_explained_not_misplaced():
    fig = plot_south_pole_map("Apollo 11 (Tranquility Base)")
    assert len(fig.data) == 1
    assert any("outside" in note.text for note in fig.layout.annotations)


@pytest.mark.parametrize("lat,lon", [(-91, 0), (-85, 181), (float('nan'), 0), (-85, None)])
def test_invalid_manual_coordinates(lat, lon):
    with pytest.raises(ValueError):
        plot_south_pole_map(lat=lat, lon=lon)


def test_map_exports_without_network_assets(tmp_path):
    output = tmp_path / "map.html"
    plot_south_pole_map().write_html(output, include_plotlyjs=True)
    html = output.read_text()
    assert "Catalog Sites" in html
    assert '<script src=' not in html


@pytest.mark.parametrize("key", list(LUNAR_SITES))
def test_each_catalog_site_supports_named_and_existing_app_calls(key):
    site = LUNAR_SITES[key]
    named = plot_south_pole_map(key)
    existing = plot_south_pole_map(LUNAR_SITES, site["lat"], site["lon"])
    assert len(named.data) == len(existing.data)
    if site["lat"] <= -80:
        assert list(named.data[1].r) == list(existing.data[1].r)
        assert list(named.data[1].theta) == [site["lon"]]


def test_hover_and_symbols_distinguish_points_regions_and_landings():
    fig = plot_south_pole_map()
    rows = {text: (row, symbol) for text, row, symbol in zip(
        fig.data[0].text, fig.data[0].customdata, fig.data[0].marker.symbol
    )}
    assert rows["Shackleton Rim S1"][0][3] == "studied_point"
    assert rows["Shackleton Rim S1"][1] == "diamond"
    assert rows["Malapert Massif"][0][3] == "region_center"
    assert rows["Malapert Massif"][1] == "circle"
    assert "Pending" in rows["Malapert Massif"][0][5]
