"""Helpers shared by the floating panels (docs/UI_OVERHAUL.md). Owner: Gabriel."""
import datetime

import streamlit as st

from src import catalog
from src.charts import plot_earth_visibility, plot_sun_elevation
from src.conditions import get_conditions, neighborhood_summary
from src.metrics import earth_visible_hours, hours_until_earthset, hours_until_sunset, sunlight_hours
from src.sites import LUNAR_SITES

get_data = st.cache_data(show_spinner=False)(get_conditions)
get_neighborhood = st.cache_data(show_spinner=False)(neighborhood_summary)

PANEL, SELECTED = "panel", "selected"  # session state: the open panel, and the selected Catalog Site key
VIEW_CHOICE, VIEWS = "view_choice", ("🌕 Globe", "🗺️ South pole map")
CUSTOM_SITE = "Custom Site"
KIND_LABELS = {
    "studied_point": "◆ Studied point",
    "region_center": "● Region center",
    "actual_landing": "■ Historical landing",
    "approximate_reference": "▲ Approximate reference",
}
CACHE_START = datetime.date.fromisoformat(catalog.START)
CACHE_END = datetime.date.fromisoformat(catalog.END)  # exclusive
DATE_HELP = (f"Catalog Sites are pre-computed from {CACHE_START} to {CACHE_END - datetime.timedelta(days=1)} "
             "and load instantly. Other dates and Custom Sites query JPL Horizons and the LOLA DEM live.")


def open_panel(name):
    """Rail callback. The catalog clears the selection; the Site Planner starts at the selected site."""
    st.session_state[PANEL] = name
    if name == "catalog":
        st.session_state[SELECTED] = None
    elif name == "planner" and st.session_state.get(SELECTED):
        st.session_state["planner_site"] = st.session_state[SELECTED]


def select_site(key):
    """Every way of choosing a Catalog Site (globe, map, catalog list) calls this before the script reruns."""
    st.session_state[SELECTED] = key
    st.session_state[PANEL] = "site" if key else "catalog"


def header():
    """App title and the globe/map switch, at the top of the Explorer panels."""
    st.markdown("### 🌕 Lunar Landing Site Navigator")
    st.caption("Solar power and direct-to-Earth communication for lunar south pole landings · NASA Space Apps 2026")
    st.segmented_control("View", VIEWS, default=VIEWS[0], key=VIEW_CHOICE, label_visibility="collapsed")


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


def window_inputs(key):
    col_date, col_days = st.columns(2)
    date = col_date.date_input("Start date (UTC)", CACHE_START, key=f"{key}_date", help=DATE_HELP)
    days = col_days.slider("Analysis window (Earth days)", 3, 28, 14, key=f"{key}_days")
    return date, days


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


def site_analysis(key, df, mask=0.0, compact=False):
    """Timeline slider, countdown cards at the selected instant, and elevation charts.

    `compact` lays the cards out 2 x 2 and stacks the charts, for the narrow floating panel.
    """
    times = list(df["time"].dt.to_pydatetime())
    at = st.slider("Instant (UTC)", times[0], times[-1], times[0], datetime.timedelta(hours=1),
                   format="YYYY-MM-DD HH:mm", key=f"{key}_at")
    row = df[df["time"] == at].iloc[0]
    earth_margin = row["earth_elevation"] - row.get("earth_horizon", 0.0) - mask
    window_hours = len(df)  # 1-hour time step
    sun_hours, earth_hours = sunlight_hours(df), earth_visible_hours(df, mask)

    cols = [*st.columns(2), *st.columns(2)] if compact else st.columns(4)
    cols[0].metric("Time to Sunset", format_countdown(hours_until_sunset(df, at), "🌑 Sun set"),
                   f"{row.get('illumination_fraction', float(row['sun_elevation'] > 0)):.0%} of solar disk visible",
                   delta_color="off", delta_arrow="off", border=True)
    cols[1].metric("Time to Earthset", format_countdown(hours_until_earthset(df, at, mask), "🚫 Not visible"),
                   f"Earth {earth_margin:+.2f}° vs horizon" + (" + mask" if mask else ""), delta_color="off",
                   delta_arrow="off", border=True)
    cols[2].metric("Sunlight in window", f"{sun_hours:.0f} h", f"{sun_hours / window_hours:.0%} of the window",
                   delta_color="off", delta_arrow="off", border=True)
    cols[3].metric("Earth visibility in window", f"{earth_hours:.0f} h",
                   f"{earth_hours / window_hours:.0%} of the window", delta_color="off", delta_arrow="off",
                   border=True)

    data_note(df)
    chart_cols = [st.container(), st.container()] if compact else st.columns(2)
    chart_cols[0].plotly_chart(plot_sun_elevation(df, at), width="stretch", key=f"{key}_sun")
    chart_cols[1].plotly_chart(plot_earth_visibility(df, at, mask), width="stretch", key=f"{key}_earth")
