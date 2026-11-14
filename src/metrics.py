"""Operational metrics from a conditions DataFrame (see src/conditions.py). Owner: Gabriel.

app.py depends on these signatures; coordinate any change with the team. Without `sun_horizon` /
`earth_horizon` columns the ideal 0° horizon is used.
"""
import numpy as np
import pandas as pd

from src.terrain import SUN_RADIUS_DEG, illumination_fraction


def _horizon(df, body):
    return df[f"{body}_horizon"] if f"{body}_horizon" in df else 0.0


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
    fraction = df["illumination_fraction"] if "illumination_fraction" in df else \
        illumination_fraction(df["sun_elevation"], 0.0)
    return float(np.sum(fraction) * _step_hours(df))


def earth_visible_hours(df, elevation_mask=0.0):
    """Hours with Earth Visibility in the DataFrame."""
    visible = df["earth_elevation"] - _horizon(df, "earth") > elevation_mask
    return float(visible.sum() * _step_hours(df))


def monthly_summary(df, elevation_mask=0.0):
    """Sunlight and Earth Visibility per calendar month, to show seasonal change.

    Returns a DataFrame indexed by month start with `sunlight_pct` (mean Illumination Fraction, %),
    `earth_visible_pct` (% of hours with Earth Visibility) and `hours` (samples in the month, so partial months
    at the window edges can be flagged).
    """
    fraction = df["illumination_fraction"] if "illumination_fraction" in df else \
        illumination_fraction(df["sun_elevation"], 0.0)
    visible = df["earth_elevation"] - _horizon(df, "earth") > elevation_mask
    month = df["time"].dt.to_period("M").dt.to_timestamp()
    grouped = pd.DataFrame({"sunlight": fraction, "earth": visible, "month": month}).groupby("month")
    return pd.DataFrame({
        "sunlight_pct": grouped["sunlight"].mean() * 100,
        "earth_visible_pct": grouped["earth"].mean() * 100,
        "hours": grouped.size() * _step_hours(df),
    })
