import base64

import numpy as np
import pandas as pd
import pytest

from src.metrics import hourly_states
from src.panels.common import format_countdown, format_duration, ordinal, parse_coordinates, time_payload


@pytest.mark.parametrize("text, expected", [
    ("-89.44, -137.17", (-89.44, -137.17)),
    ("-89.44 -137.17", (-89.44, -137.17)),
    ("-89.44°, 222.83° E", (-89.44, 222.83 - 360)),
    ("0.6742;23.473", (0.6742, 23.473)),
])
def test_parse_coordinates(text, expected):
    assert parse_coordinates(text) == pytest.approx(expected)


@pytest.mark.parametrize("text", ["Shackleton", "-95, 10", "10, 400", "", None])
def test_parse_coordinates_rejects_other_text(text):
    assert parse_coordinates(text) is None


def test_time_payload_carries_the_hourly_states():
    df = pd.DataFrame({"time": pd.date_range("2027-01-01", periods=3, freq="h"), "sun_elevation": [1.0, -1.0, 2.0],
                       "illumination_fraction": [1.0, 0.0, 0.25], "earth_elevation": [1.0, 1.0, -1.0]})
    payload = time_payload({"asset": df}, instant="2027-01-01T01:00:00Z")
    assert payload["start"] == "2027-01-01T00:00:00Z" and payload["hours"] == 3
    states = np.frombuffer(base64.b64decode(payload["states"]["asset"]), dtype=np.uint8)
    assert states.tolist() == hourly_states(df).tolist()


def test_people_friendly_numbers():
    assert [ordinal(n) for n in (1, 2, 3, 4, 11, 12, 13, 21, 22)] == \
        ["1st", "2nd", "3rd", "4th", "11th", "12th", "13th", "21st", "22nd"]
    assert [format_duration(h) for h in (0, 30, 110.4)] == ["None", "30 h", "4.6 days"]
    assert [format_countdown(h, "down") for h in (None, 0, 0.04, 0.995, 5.3, 23.97, 47.5, 95.6)] ==         ["No set in window", "down", "2 min", "1.0 h", "5.3 h", "1 d 0 h", "2 d 0 h", "4 d 0 h"]


def test_every_place_is_a_catalog_site_with_sourced_images():
    from src.panels.places import PLACES
    from src.sites import LUNAR_SITES
    assert len(PLACES) == 17 and set(PLACES) == set(LUNAR_SITES)
    for title, text, photos in PLACES.values():
        assert title and text and photos
        for url, caption, page in photos:
            # Only the NASA Image and Video Library: no images of uncertain origin or with reuse limits
            assert url.startswith("https://images-assets.nasa.gov/") and caption
            assert page.startswith("https://images.nasa.gov/details/")
            assert "(" not in page  # a parenthesis would end the caption's markdown link early


def test_selected_instant_follows_the_bar_inside_the_window_and_restarts_it_outside(monkeypatch):
    import streamlit as st
    from src.panels.common import MOON_VIEW, selected_instant
    df = pd.DataFrame({"time": pd.date_range("2027-01-01", periods=72, freq="h")})
    for instant, expected in [(None, "2027-01-01 00:00"),  # the bar has not sent one yet
                              ("2027-01-02T05:40:00Z", "2027-01-02 05:00"),  # inside: its hour
                              ("2027-06-15T12:00:00Z", "2027-01-01 00:00")]:  # another window's: the start
        monkeypatch.setattr(st, "session_state", {MOON_VIEW: {"instant": instant}})
        assert selected_instant(df) == pd.Timestamp(expected)


def test_new_overviews_distinguish_regional_imagery_and_link_scientific_sources():
    from src.panels.places import PLACES
    from src.sites import ARTEMIS_2022_SOURCE, POLAR_SOURCE, LUNAR_SITES
    for key, site in LUNAR_SITES.items():
        if site['coordinate_kind'] != 'region_center' or key in {'Haworth', 'Malapert Massif (Summit)', 'Faustini Crater (Rim)'}:
            continue
        title, text, images = PLACES[key]
        assert title and POLAR_SOURCE in text and ARTEMIS_2022_SOURCE in text
        assert 'representative region center' in text
        for url, caption, page in images:
            assert 'Regional context' in caption and 'exact coordinates' in caption
            assert 'NASA/GSFC/Arizona State University' in caption
            assert 'PIA13523' in url and page.endswith('PIA13523')
