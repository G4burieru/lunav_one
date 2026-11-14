"""Operational metrics computed from the horizons_api.py DataFrame contract. Owner: Gabriel.

app.py depends on these signatures; coordinate any change with the team.
"""


def hours_until_sunset(df, at):
    """Hours from instant `at` until sun_elevation drops to <= 0, or None if it does not set within the window."""
    raise NotImplementedError


def hours_until_earthset(df, at):
    """Hours from instant `at` until earth_elevation drops to <= 0, or None if it does not set within the window."""
    raise NotImplementedError
