from src.horizons_api import parse_elevation

# Excerpt of a real JPL Horizons response (Sun as seen from lat -89.9, lon 0).
SAMPLE = """header
$$SOE
 2026-Dec-01 00:00,*, , 280.061257,     1.487607,
 2026-Dec-01 06:00,*, , 277.021323,    -1.480977,
$$EOE
footer"""


def test_parse_elevation():
    df = parse_elevation(SAMPLE)
    assert list(df["elevation"]) == [1.487607, -1.480977]
    assert list(df["azimuth"]) == [280.061257, 277.021323]
    assert str(df["time"].iloc[1]) == "2026-12-01 06:00:00"
