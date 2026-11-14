"""Operational metrics computed from the horizons_api.py DataFrame contract. Owner: Gabriel.

app.py depends on these signatures; coordinate any change with the team.
"""
import numpy as np
import pandas as pd


def _hours_until_set(df, column, at):
    at = pd.Timestamp(at)
    future = df[df["time"] >= at]
    if future.empty:
        return None
    elevation = future[column].to_numpy()
    if elevation[0] <= 0:
        return 0.0
    below = np.flatnonzero(elevation <= 0)
    if below.size == 0:
        return None
    i = below[0]
    t0, t1 = future["time"].iloc[i - 1], future["time"].iloc[i]
    e0, e1 = elevation[i - 1], elevation[i]
    crossing = t0 + (t1 - t0) * (e0 / (e0 - e1))  # linear interpolation of the 0° crossing
    return (crossing - at) / pd.Timedelta(hours=1)


def hours_until_sunset(df, at):
    """Hours from instant `at` until sun_elevation drops to <= 0, or None if it does not set within the window.

    Returns 0.0 if the Sun is already below the horizon at `at`.
    """
    return _hours_until_set(df, "sun_elevation", at)


def hours_until_earthset(df, at):
    """Hours from instant `at` until earth_elevation drops to <= 0, or None if it does not set within the window.

    Returns 0.0 if Earth is already below the horizon at `at`.
    """
    return _hours_until_set(df, "earth_elevation", at)
