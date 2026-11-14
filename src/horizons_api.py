"""Sun and Earth ephemerides from JPL Horizons. Owner: Gabriel.

Contract used by app.py and charts.py; coordinate any change with the team:
    get_ephemerides_data(lat, lon, start_date, days) -> DataFrame with columns
        time            datetime (UTC), 1-hour step
        sun_elevation   degrees above the horizon
        earth_elevation degrees above the horizon

shortcut: elevation is relative to the ideal ellipsoid horizon, without terrain. At the pole the Sun
stays ~1.5° above it, so terrain decides real visibility. Next step: terrain horizon from the LOLA DEM.
"""
import pandas as pd
import requests

API_URL = "https://ssd.jpl.nasa.gov/api/horizons.api"
SUN, EARTH = 10, 399


def parse_elevation(text):
    if "$$SOE" not in text:
        raise ValueError(f"Unexpected JPL Horizons response:\n{text[:500]}")
    block = text.split("$$SOE")[1].split("$$EOE")[0]
    rows = [line.split(",") for line in block.strip().splitlines()]
    return pd.DataFrame({
        "time": pd.to_datetime([r[0].strip() for r in rows], format="%Y-%b-%d %H:%M"),
        "elevation": [float(r[4]) for r in rows],
    })


def _fetch_elevation(body, lat, lon, start, stop):
    params = {
        "format": "text",
        "COMMAND": f"'{body}'",
        "EPHEM_TYPE": "'OBSERVER'",
        "CENTER": "'coord@301'",  # observer on the lunar surface
        "COORD_TYPE": "'GEODETIC'",
        "SITE_COORD": f"'{lon},{lat},0'",
        "START_TIME": f"'{start}'",
        "STOP_TIME": f"'{stop}'",
        "STEP_SIZE": "'1h'",
        "QUANTITIES": "'4'",  # azimuth and elevation
        "CSV_FORMAT": "'YES'",
    }
    response = requests.get(API_URL, params=params, timeout=30)
    response.raise_for_status()
    return parse_elevation(response.text)


def get_ephemerides_data(lat, lon, start_date, days):
    start = pd.Timestamp(start_date)
    stop = start + pd.Timedelta(days=days)
    sun = _fetch_elevation(SUN, lat, lon, start.date(), stop.date())
    earth = _fetch_elevation(EARTH, lat, lon, start.date(), stop.date())
    return pd.DataFrame({
        "time": sun["time"],
        "sun_elevation": sun["elevation"],
        "earth_elevation": earth["elevation"],
    })
