"""Streamlit user interface. Owner: Igor.

Two modes (see GLOSSARY.md): Explorer, to learn about the Moon and compare Catalog Sites, and Site Planner,
to evaluate one point (catalog or custom) with an Asset Height and an Elevation Mask.
"""
import datetime

import pandas as pd
import streamlit as st

from src import catalog
from src.charts import plot_earth_visibility, plot_sun_elevation
from src.conditions import get_conditions
from src.metrics import earth_visible_hours, hours_until_earthset, hours_until_sunset, sunlight_hours
from src.site_map import plot_south_pole_map
from src.sites import LUNAR_SITES

st.set_page_config(page_title="Lunar Landing Site Navigator", page_icon="🌕", layout="wide")
st.title("🌕 Lunar Landing Site Navigator")
st.caption("Solar power and direct-to-Earth communication for lunar south pole landings | NASA Space Apps 2026")

get_data = st.cache_data(show_spinner=False)(get_conditions)
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


def load(lat, lon, date, days, asset_height=catalog.ASSET_HEIGHT_M):
    """Conditions DataFrame, or None (with an error shown) so the rest of the page keeps working."""
    live = "" if is_cached(date, days) else " Live computation can take up to ~30 s."
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


def site_details(site):
    st.markdown(f"**{site.get('name', '')}** · {KIND_LABELS.get(site.get('coordinate_kind'), 'Unspecified')}")
    st.caption(f"Lat {site['lat']}° · Lon {site['lon']}° E")
    st.write(site["description"])
    if "coordinate_meaning" in site:
        st.caption(f"Coordinate meaning: {site['coordinate_meaning']}")
    with st.expander("Scientific and exploration context", expanded=True):
        if "scientific_context" in site:
            st.markdown(f"**Science.** {site['scientific_context']}")
        if "exploration_context" in site:
            st.markdown(f"**Exploration.** {site['exploration_context']}")
        if "topographic_validation" in site:
            st.markdown(f"**Validation.** {site['topographic_validation']}")
        sources = [f"[Coordinate source]({site['coordinate_source']})" if "coordinate_source" in site else None,
                   site.get("source_location"),
                   f"[Exploration source]({site['exploration_source']})" if "exploration_source" in site else None]
        st.caption(" · ".join(s for s in sources if s))


def site_analysis(key, df, mask=0.0):
    """Timeline slider, countdown cards at the selected instant, and elevation charts."""
    times = list(df["time"].dt.to_pydatetime())
    at = st.slider("Instant (UTC)", times[0], times[-1], times[0], datetime.timedelta(hours=1),
                   format="YYYY-MM-DD HH:mm", key=f"{key}_at")
    row = df[df["time"] == at].iloc[0]
    earth_margin = row["earth_elevation"] - row.get("earth_horizon", 0.0) - mask
    window_hours = len(df)  # 1-hour time step
    sun_hours, earth_hours = sunlight_hours(df), earth_visible_hours(df, mask)

    cols = st.columns(4)
    cols[0].metric("Time to Sunset", format_countdown(hours_until_sunset(df, at), "🌑 Sun set"),
                   f"{row.get('illumination_fraction', float(row['sun_elevation'] > 0)):.0%} of solar disk visible",
                   delta_color="off")
    cols[1].metric("Time to Earthset", format_countdown(hours_until_earthset(df, at, mask), "🚫 Earth not visible"),
                   f"Earth {earth_margin:+.2f}° vs horizon" + (" + mask" if mask else ""), delta_color="off")
    cols[2].metric("Sunlight in window", f"{sun_hours:.0f} h", f"{sun_hours / window_hours:.0%} of the window",
                   delta_color="off")
    cols[3].metric("Earth visibility in window", f"{earth_hours:.0f} h",
                   f"{earth_hours / window_hours:.0%} of the window", delta_color="off")

    data_note(df)
    col_a, col_b = st.columns(2)
    col_a.plotly_chart(plot_sun_elevation(df, at), width="stretch", key=f"{key}_sun")
    col_b.plotly_chart(plot_earth_visibility(df, at, mask), width="stretch", key=f"{key}_earth")


def catalog_comparison(date, days):
    rows = []
    for key, site in LUNAR_SITES.items():
        try:
            df = get_data(site["lat"], site["lon"], str(date), days, catalog.ASSET_HEIGHT_M)
        except Exception:
            continue
        rows.append({
            "Site": site_label(key),
            "Type": KIND_LABELS.get(site.get("coordinate_kind"), "Unspecified"),
            "Sunlight (%)": 100 * sunlight_hours(df) / len(df),
            # Without terrain columns, sunlight_hours falls back to the ideal horizon: shows what relief changes.
            "Sunlight, ideal horizon (%)":
                100 * sunlight_hours(df.drop(columns=["sun_horizon", "illumination_fraction"])) / len(df),
            "Earth visibility (%)": 100 * earth_visible_hours(df) / len(df),
            "First Sunset in": format_countdown(hours_until_sunset(df, df["time"].iloc[0]), "Set at start"),
        })
    return pd.DataFrame(rows)


tab_explorer, tab_planner = st.tabs(["🔭 Explorer", "📍 Site Planner"])

with tab_explorer:
    col_map, col_info = st.columns([3, 2])
    with col_info:
        key = st.selectbox("Catalog Site", list(LUNAR_SITES), format_func=site_label, key="explorer_site")
        site = LUNAR_SITES[key]
        site_details(site)
    # The map needs no external data, so it renders even if Horizons is down.
    col_map.plotly_chart(plot_south_pole_map(key), width="stretch")

    st.subheader("☀️ Sunlight and 📡 Earth visibility")
    date, days = window_inputs("explorer")
    df = load(site["lat"], site["lon"], date, days)
    if df is not None:
        site_analysis("explorer", df)

    st.subheader("⚖️ Compare Catalog Sites")
    st.caption(f"Same window ({date}, {days} days) at {catalog.ASSET_HEIGHT_M:g} m Asset Height, with terrain. "
               "Pick a 28-day window to see a full lunar day, where terrain matters most.")
    if is_cached(date, days):
        st.dataframe(
            catalog_comparison(date, days), hide_index=True, width="stretch",
            column_config={
                "Sunlight (%)": st.column_config.ProgressColumn(min_value=0, max_value=100, format="%.0f%%"),
                "Earth visibility (%)": st.column_config.ProgressColumn(min_value=0, max_value=100, format="%.0f%%"),            },
        )
    else:
        st.info(f"The comparison uses pre-computed data only. Pick a window between {CACHE_START} and {CACHE_END}.")

with tab_planner:
    col_site, col_asset = st.columns(2)
    with col_site:
        key = st.selectbox("Site", [*LUNAR_SITES, CUSTOM_SITE], format_func=site_label, key="planner_site")
        if key == CUSTOM_SITE:
            lat = st.number_input("Latitude (°)", -90.0, 90.0, -89.5, 0.01, key="planner_lat")
            lon = st.number_input("East longitude (°)", -180.0, 180.0, 0.0, 0.01, key="planner_lon")
        else:
            lat, lon = LUNAR_SITES[key]["lat"], LUNAR_SITES[key]["lon"]
            st.caption(f"Lat {lat}° · Lon {lon}° E")
    with col_asset:
        height = st.number_input(
            "Asset Height (m)", 0.5, 100.0, catalog.ASSET_HEIGHT_M, 0.5, key="planner_height",
            help=f"Height of the panel or antenna above the ground. Only {catalog.ASSET_HEIGHT_M:g} m is "
                 "pre-computed; other heights compute the terrain horizon live.")
        mask = st.number_input("Elevation Mask (°)", 0.0, 20.0, 0.0, 0.5, key="planner_mask",
                               help="Minimum angle Earth must clear above the terrain horizon to count as visible.")
    date, days = window_inputs("planner")
    df = load(lat, lon, date, days, height)
    if df is not None:
        site_analysis("planner", df, mask)
