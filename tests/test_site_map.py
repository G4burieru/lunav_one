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
    assert len(named.data[0].r) == 4
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
    assert "Study regions" in html
    assert '<script src=' not in html
