import base64

import numpy as np
import pandas as pd
import pytest

from src.metrics import hourly_states
from src.panels.common import format_duration, ordinal, parse_coordinates, time_payload


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
