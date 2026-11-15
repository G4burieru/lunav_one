"""Helpers shared by the floating panels (docs/UI_OVERHAUL.md). Owner: Gabriel."""
import base64
import datetime
import re

import pandas as pd
import streamlit as st

from src import catalog
from src.conditions import get_conditions, neighborhood_summary
from src.metrics import hourly_states, site_summary
from src.sites import LUNAR_SITES

get_data = st.cache_data(show_spinner=False)(get_conditions)
get_neighborhood = st.cache_data(show_spinner=False)(neighborhood_summary)

# Session state: the open panel, the selected Catalog Site key, and the Custom Site ({"lat", "lon"}) if any.
PANEL, SELECTED, CUSTOM = "panel", "selected", "custom"
PANEL_OPEN = "panel_open"  # False while the panel is hidden (a second click on its rail icon)
MOON_VIEW = "moon_view"  # the Moon View's key in app.py; its "instant" comes from the time bar
VIEW_CHOICE, VIEWS = "view_choice", ("Globe", "South pole map")
VIEW_ICONS = {"Globe": "moon", "South pole map": "pole-map"}
CUSTOM_SITE = "Custom Site"
KIND_LABELS = {
    "studied_point": "◆ Studied point",
    "region_center": "● Region center",
    "actual_landing": "■ Historical landing",
    "approximate_reference": "▲ Approximate reference",
}
CACHE_START = datetime.date.fromisoformat(catalog.START)
CACHE_END = datetime.date.fromisoformat(catalog.END)  # exclusive
EXPLORER_DAYS = (CACHE_END - CACHE_START).days  # the Explorer's Analysis Window: all of 2027–2028
DATE_HELP = (f"Catalog Sites are pre-computed from {CACHE_START} to {CACHE_END - datetime.timedelta(days=1)} "
             "and load instantly. Other dates and Custom Sites query JPL Horizons and the LOLA DEM live.")
_COORDINATES = re.compile(r"^\s*(-?\d+(?:\.\d+)?)\s*°?\s*[,;\s]\s*(-?\d+(?:\.\d+)?)\s*°?\s*(?:E)?\s*$", re.IGNORECASE)


def icon(name):
    """Markdown for an SVG icon in static/icons/ (served with server.enableStaticServing), shown at text height.
    Empty alt text: the icons are decorative, the words next to them carry the meaning."""
    return f"![](app/static/icons/{name}.svg)"


def rail_active(name):
    """Whether rail icon `name` stands for the current panel (the catalog icon also stands for a Site Card)."""
    panel = st.session_state.get(PANEL, "catalog")
    return name == panel or (name, panel) == ("catalog", "site")


def open_panel(name):
    """Rail callback. A click on the current panel's icon hides the panel and the next click shows it again, so the
    whole Moon can be seen. Opening the catalog clears the selection; the Site Planner starts at the selected site."""
    if rail_active(name):
        st.session_state[PANEL_OPEN] = not st.session_state.get(PANEL_OPEN, True)
        return
    st.session_state[PANEL], st.session_state[PANEL_OPEN] = name, True
    if name == "catalog":
        st.session_state[SELECTED] = st.session_state[CUSTOM] = None
    elif name == "planner" and st.session_state.get(SELECTED):
        st.session_state["planner_site"] = st.session_state[SELECTED]
    elif name == "planner" and st.session_state.get(CUSTOM):
        custom = st.session_state[CUSTOM]
        st.session_state.update(planner_site=CUSTOM_SITE, planner_lat=custom["lat"], planner_lon=custom["lon"])


def select_site(key):
    """Every way of choosing a Catalog Site (globe, map, catalog list) calls this before the script reruns."""
    st.session_state[SELECTED], st.session_state[CUSTOM] = key, None
    st.session_state[PANEL], st.session_state[PANEL_OPEN] = ("site" if key else "catalog"), True


def select_custom(lat, lon):
    """Open the Site Card of a Custom Site (from the search, or a confirmed click on the Moon View)."""
    st.session_state[SELECTED], st.session_state[CUSTOM] = None, {"lat": lat, "lon": lon}
    st.session_state[PANEL], st.session_state[PANEL_OPEN] = "site", True


def parse_coordinates(text):
    """(lat, lon) from text such as "-89.44, -137.17" or "-89.44° 222.83° E", or None. Longitudes above 180°
    are east-positive from 0 to 360 and are wrapped to [-180, 180]."""
    match = _COORDINATES.match(text or "")
    if not match:
        return None
    lat, lon = float(match[1]), float(match[2])
    if not (-90 <= lat <= 90 and -180 <= lon <= 360):
        return None
    return lat, lon - 360 if lon > 180 else lon


def two_years(lat, lon, catalog_site=True):
    """Conditions over the Explorer's Analysis Window: instant for Catalog Sites, live (about 30 s) otherwise.
    None, with an error shown, if the live computation fails."""
    return load(lat, lon, CACHE_START, EXPLORER_DAYS, catalog_site=catalog_site)


@st.cache_data(show_spinner=False)
def catalog_summaries():
    """The Site Card grid (src.metrics.site_summary) of every Catalog Site over 2027–2028, one row per key."""
    return pd.DataFrame({key: site_summary(get_data(site["lat"], site["lon"], str(CACHE_START), EXPLORER_DAYS))
                         for key, site in LUNAR_SITES.items()}).T


def rank(column, value, lower_is_better=False):
    """Place of `value` among the Catalog Sites' `column` in catalog_summaries(): 1 + the number doing better."""
    values = catalog_summaries()[column]
    return int((values < value).sum() if lower_is_better else (values > value).sum()) + 1


def ordinal(n):
    return f"{n}{'th' if 10 <= n % 100 <= 20 else {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')}"


def format_duration(hours):
    """A Longest Night or Longest Earth Absence for people: hours below two days, days above."""
    if hours == 0:
        return "None"
    return f"{hours:.0f} h" if hours < 48 else f"{hours / 24:.1f} days"


def time_payload(dfs, instant=None, elevation_mask=0.0):
    """The Moon View `time` data (docs/UI_OVERHAUL.md) for DataFrames that share one hourly time axis, keyed by
    site key (or "asset" in the Site Planner)."""
    times = next(iter(dfs.values()))["time"]
    return {"start": times.iloc[0].strftime("%Y-%m-%dT%H:%M:%SZ"), "hours": len(times), "instant": instant,
            "states": {key: base64.b64encode(hourly_states(df, elevation_mask).tobytes()).decode()
                       for key, df in dfs.items()}}


@st.cache_data(show_spinner=False)
def catalog_time():
    """Time bar states of every Catalog Site over 2027–2028, for the Explorer; set "instant" before sending."""
    return time_payload({key: get_data(site["lat"], site["lon"], str(CACHE_START), EXPLORER_DAYS)
                         for key, site in LUNAR_SITES.items()})


def selected_instant(df):
    """The time bar's instant (UTC, naive like df["time"]), or the start of `df` until the time bar sets one."""
    value = (st.session_state.get(MOON_VIEW) or {}).get("instant")
    at = pd.Timestamp(value) if value else df["time"].iloc[0]
    at = at.tz_convert("UTC").tz_localize(None) if at.tzinfo else at
    return min(max(at.floor("h"), df["time"].iloc[0]), df["time"].iloc[-1])


def header():
    """App title and the globe/map switch, at the top of the Explorer panels."""
    st.markdown(f"### {icon('moon')} Lunar Landing Site Navigator")
    st.caption("Solar power and direct-to-Earth communication for lunar south pole landings · NASA Space Apps 2026")
    # No default: view_request() in app.py always sets the value first, and a default too makes Streamlit warn.
    st.segmented_control("View", VIEWS, key=VIEW_CHOICE, label_visibility="collapsed",
                         format_func=lambda view: f"{icon(VIEW_ICONS[view])} {view}")


def site_label(key):
    """Display name; the dictionary key stays the internal identifier (see src/sites.py)."""
    return LUNAR_SITES[key].get("name", key) if key in LUNAR_SITES else key


def is_cached(date, days):
    return CACHE_START <= date and date + datetime.timedelta(days=days) <= CACHE_END


def format_countdown(hours, below_label):
    if hours is None:
        return "No set in window"
    if hours == 0:
        return below_label
    days, rest = divmod(hours, 24)
    return f"{int(days)} d {rest:.0f} h" if days else f"{hours:.1f} h"


def load(lat, lon, date, days, asset_height=catalog.ASSET_HEIGHT_M, catalog_site=True):
    """Conditions DataFrame, or None (with an error shown) so the rest of the page keeps working."""
    instant = catalog_site and is_cached(date, days) and asset_height == catalog.ASSET_HEIGHT_M
    live = "" if instant else " Live computation can take up to ~1 min."
    with st.spinner("Computing Sun and Earth conditions..." + live):
        try:
            return get_data(lat, lon, str(date), days, asset_height)
        except Exception as e:
            st.error(f"Could not load Sun and Earth conditions (JPL Horizons or the DEM server failed): {e}")
            return None


def data_note(df):
    terrain, source, near = df.attrs.get("terrain"), df.attrs.get("source", "live"), df.attrs.get("site")
    if terrain:
        neighborhood = f" · Site Neighborhood of {site_label(near)}" if near else ""
        st.caption(f"Terrain horizon: {terrain} · Data: {source}{neighborhood}")
    else:
        st.warning("No terrain data for this point (outside 80°S): visibility uses the ideal horizon.")
