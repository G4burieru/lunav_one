"""Operational metrics from a conditions DataFrame (see src/conditions.py). Owner: Gabriel.

app.py depends on these signatures; coordinate any change with the team. Without `sun_horizon` /
`earth_horizon` columns the ideal 0° horizon is used.
"""
import numpy as np
import pandas as pd

from src.terrain import SUN_RADIUS_DEG, illumination_fraction


def _horizon(df, body):
    return df[f"{body}_horizon"] if f"{body}_horizon" in df else 0.0


def _illumination(df):
    if "illumination_fraction" in df:
        return df["illumination_fraction"]
    return illumination_fraction(df["sun_elevation"], 0.0)


def _earth_visible(df, elevation_mask):
    return df["earth_elevation"] - _horizon(df, "earth") > elevation_mask


def _hours_until_negative(df, margin, at):
    """Hours from `at` until `margin` drops to <= 0 (0.0 if already there, None if not within the data)."""
    at = pd.Timestamp(at)
    future = df["time"] >= at
    if not future.any():
        return None
    times = df["time"][future]
    margin = np.asarray(margin)[future.to_numpy()]
    if margin[0] <= 0:
        return 0.0
    below = np.flatnonzero(margin <= 0)
    if below.size == 0:
        return None
    i = below[0]
    t0, t1 = times.iloc[i - 1], times.iloc[i]
    crossing = t0 + (t1 - t0) * (margin[i - 1] / (margin[i - 1] - margin[i]))  # linear interpolation
    return (crossing - at) / pd.Timedelta(hours=1)


def _step_hours(df):
    return df["time"].diff().median() / pd.Timedelta(hours=1)


def hours_until_sunset(df, at):
    """Hours from `at` until Sunset (the whole solar disk below the horizon), or None if it does not set.

    Returns 0.0 if the Sun is already set at `at`.
    """
    return _hours_until_negative(df, df["sun_elevation"] + SUN_RADIUS_DEG - _horizon(df, "sun"), at)


def hours_until_earthset(df, at, elevation_mask=0.0):
    """Hours from `at` until Earthset (Earth's center below the horizon plus the Elevation Mask), or None.

    Returns 0.0 if Earth is already not visible at `at`.
    """
    return _hours_until_negative(df, df["earth_elevation"] - _horizon(df, "earth") - elevation_mask, at)


def sunlight_hours(df):
    """Equivalent full-Sun hours in the DataFrame: the Illumination Fraction summed over time."""
    return float(np.sum(_illumination(df)) * _step_hours(df))


def earth_visible_hours(df, elevation_mask=0.0):
    """Hours with Earth Visibility in the DataFrame."""
    return float(_earth_visible(df, elevation_mask).sum() * _step_hours(df))


def _longest_run_hours(df, flags):
    """Duration of the longest run of consecutive True samples, in hours."""
    flags = np.asarray(flags, dtype=bool)
    if not flags.any():
        return 0.0
    edges = np.flatnonzero(np.diff(np.concatenate(([0], flags.astype(np.int8), [0]))))  # run starts and ends
    return float((edges[1::2] - edges[::2]).max() * _step_hours(df))


def longest_night(df):
    """Longest Night: the longest continuous period, in hours, with the Illumination Fraction at 0."""
    return _longest_run_hours(df, _illumination(df) <= 0)


def longest_earth_absence(df, elevation_mask=0.0):
    """Longest Earth Absence: the longest continuous period, in hours, without Earth Visibility."""
    return _longest_run_hours(df, ~_earth_visible(df, elevation_mask))


def site_summary(df, elevation_mask=0.0):
    """The Site Card grid over the whole DataFrame: `sunlight_pct` (mean Illumination Fraction, %),
    `earth_visible_pct` (% of hours with Earth Visibility), `longest_night_h` and `longest_earth_absence_h`."""
    return {
        "sunlight_pct": float(_illumination(df).mean() * 100),
        "earth_visible_pct": float(_earth_visible(df, elevation_mask).mean() * 100),
        "longest_night_h": longest_night(df),
        "longest_earth_absence_h": longest_earth_absence(df, elevation_mask),
    }


def hourly_states(df, elevation_mask=0.0):
    """One byte per sample for the Moon View time bar: bits 0-6 hold the Illumination Fraction in percent
    (0-100), bit 7 is set when Earth is visible. Returns a uint8 NumPy array."""
    sun = np.rint(np.clip(np.asarray(_illumination(df), dtype=float), 0, 1) * 100).astype(np.uint8)
    return sun | (np.asarray(_earth_visible(df, elevation_mask), dtype=np.uint8) << 7)


def monthly_summary(df, elevation_mask=0.0):
    """Sunlight and Earth Visibility per calendar month, to show seasonal change.

    Returns a DataFrame indexed by month start with `sunlight_pct` (mean Illumination Fraction, %),
    `earth_visible_pct` (% of hours with Earth Visibility) and `hours` (samples in the month, so partial months
    at the window edges can be flagged).
    """
    month = df["time"].dt.to_period("M").dt.to_timestamp()
    grouped = pd.DataFrame({"sunlight": _illumination(df), "earth": _earth_visible(df, elevation_mask),
                            "month": month}).groupby("month")
    return pd.DataFrame({
        "sunlight_pct": grouped["sunlight"].mean() * 100,
        "earth_visible_pct": grouped["earth"].mean() * 100,
        "hours": grouped.size() * _step_hours(df),
    })
