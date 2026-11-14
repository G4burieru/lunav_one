"""Site Planner panel: place a Surface Asset and evaluate its sunlight and Earth visibility (docs/UI_OVERHAUL.md,
task B3). Owner: Gabriel."""
import datetime

import streamlit as st

from src import catalog
from src.charts import plot_earth_visibility, plot_neighborhood, plot_sun_elevation
from src.metrics import earth_visible_hours, hours_until_earthset, hours_until_sunset, sunlight_hours
from src.panels import texts
from src.panels.common import (CACHE_START, CUSTOM_SITE, DATE_HELP, data_note, format_countdown, get_neighborhood,
                               load, site_label, time_payload)
from src.sites import LUNAR_SITES

HEIGHTS = {"Rover or lander · 2 m": catalog.ASSET_HEIGHT_M, "Mast · 10 m": 10.0, "Other height": None}


def where():
    key = st.selectbox("Site", [*LUNAR_SITES, CUSTOM_SITE], format_func=site_label, key="planner_site")
    if key == CUSTOM_SITE:
        col_lat, col_lon = st.columns(2)
        lat = col_lat.number_input("Latitude (°)", -90.0, 90.0, -89.5, 0.01, key="planner_lat")
        lon = col_lon.number_input("East longitude (°)", -180.0, 180.0, 0.0, 0.01, key="planner_lon")
    else:
        lat, lon = LUNAR_SITES[key]["lat"], LUNAR_SITES[key]["lon"]
        st.caption(f"Lat {lat}° · Lon {lon}° E")
    return key, lat, lon


def surface_asset():
    preset = st.segmented_control("Asset Height", list(HEIGHTS), default=next(iter(HEIGHTS)), key="planner_preset",
                                  help=texts.ASSET_HEIGHT_HELP) or next(iter(HEIGHTS))
    height = HEIGHTS[preset]
    if height is None:
        height = st.number_input("Asset Height (m)", 0.5, 100.0, catalog.ASSET_HEIGHT_M, 0.5, key="planner_height")
    mask = st.number_input("Elevation Mask (°)", 0.0, 20.0, 0.0, 0.5, key="planner_mask",
                           help=texts.ELEVATION_MASK_HELP)
    return height, mask


def when():
    col_date, col_days = st.columns(2)
    date = col_date.date_input("Start date (UTC)", CACHE_START, key="planner_date", help=DATE_HELP)
    days = col_days.slider("Duration (Earth days)", 3, 28, 14, key="planner_days")
    return date, days


def neighborhood(key, date, days, mask):
    """The Site Neighborhood heatmap (moves onto the map in task B6). Returns the clicked cell's (lat, lon)."""
    st.markdown("**🧭 Site Neighborhood**: click a cell to move the Surface Asset there.")
    layer = st.radio("Color by", ["Sunlight", "Earth visibility"], horizontal=True, key="planner_layer")
    column = "sunlight_pct" if layer == "Sunlight" else "earth_visible_pct"
    try:
        points = get_neighborhood(key, str(date), days, mask)
    except Exception as e:
        st.error(f"Could not compute the Site Neighborhood: {e}")
        return None
    event = st.plotly_chart(plot_neighborhood(points, column, layer), width="stretch", on_select="rerun",
                            selection_mode="points", key=f"planner_neighborhood_{key}")
    picked = event.selection.points
    match = points[(points["east_m"] == picked[0]["x"]) & (points["north_m"] == picked[0]["y"])] \
        if picked else points.iloc[0:0]
    if match.empty:
        st.caption(f"Showing {site_label(key)} itself, at (0, 0). The ★ marks the best cell.")
        return None
    point = match.iloc[0]
    st.caption(f"Surface Asset {point['east_m']:+.0f} m east and {point['north_m']:+.0f} m north of "
               f"{site_label(key)} · Lat {point['lat']:.5f}° · Lon {point['lon']:.5f}° E")
    return float(point["lat"]), float(point["lon"])


def results(df, mask, days):
    # shortcut: keeps its own Instant slider until the Moon View time bar (task A3) covers the Planner window.
    times = list(df["time"].dt.to_pydatetime())
    at = st.slider("Instant (UTC)", times[0], times[-1], times[0], datetime.timedelta(hours=1),
                   format="YYYY-MM-DD HH:mm", key="planner_at")
    row = df[df["time"] == at].iloc[0]
    sunset, earthset = hours_until_sunset(df, at), hours_until_earthset(df, at, mask)
    sun_hours, earth_hours = sunlight_hours(df), earth_visible_hours(df, mask)
    cols = [*st.columns(2), *st.columns(2)]
    cols[0].metric("Time to Sunset", format_countdown(sunset, "🌑 Sun set"),
                   f"{row['illumination_fraction']:.0%} of the solar disk visible", delta_color="off",
                   delta_arrow="off", border=True)
    cols[1].metric("Time to Earthset", format_countdown(earthset, "🚫 Not visible"),
                   f"Earth {row['earth_elevation'] - row['earth_horizon'] - mask:+.2f}° vs horizon"
                   + (" + mask" if mask else ""), delta_color="off", delta_arrow="off", border=True)
    cols[2].metric("Sunlight", f"{100 * sun_hours / len(df):.0f}%", f"{sun_hours:.0f} h of full Sun",
                   delta_color="off", delta_arrow="off", border=True)
    cols[3].metric("Earth visible", f"{100 * earth_hours / len(df):.0f}%", f"{earth_hours:.0f} h",
                   delta_color="off", delta_arrow="off", border=True)

    sun = ("the Sun is down" if sunset == 0 else "the Sun stays up to the end of the window" if sunset is None
           else f"the Sun sets in {format_countdown(sunset, '')}")
    earth = ("Earth is out of view" if earthset == 0 else "Earth stays in view to the end of the window"
             if earthset is None else f"Earth sets in {format_countdown(earthset, '')}")
    st.markdown(f"From the selected instant, {sun} and {earth}. Over the {days} days, the Sun shines "
                f"{100 * sun_hours / len(df):.0f}% of the time and Earth is in view "
                f"{100 * earth_hours / len(df):.0f}% of the time.")
    data_note(df)
    st.plotly_chart(plot_sun_elevation(df, at), width="stretch", key="planner_sun")
    st.plotly_chart(plot_earth_visibility(df, at, mask), width="stretch", key="planner_earth")


def render():
    """The four steps. Returns what the Moon View should show: the Surface Asset and its time bar states."""
    st.markdown("### 📍 Site Planner")
    st.caption("Place a Surface Asset precisely and evaluate its sunlight and Earth visibility.")
    st.markdown("**1 · Where**")
    key, lat, lon = where()
    st.markdown("**2 · Surface Asset**")
    height, mask = surface_asset()
    st.markdown("**3 · When**")
    date, days = when()
    if key != CUSTOM_SITE and height == catalog.ASSET_HEIGHT_M:
        lat, lon = neighborhood(key, date, days, mask) or (lat, lon)
    elif key != CUSTOM_SITE:
        st.caption(f"The Site Neighborhood is pre-computed for {catalog.ASSET_HEIGHT_M:g} m Asset Height only.")

    st.markdown("**4 · Results**")
    df = load(lat, lon, date, days, height, catalog_site=key != CUSTOM_SITE)
    if df is None:
        return None
    results(df, mask, days)
    return {"mode": "planner", "asset": {"lat": lat, "lon": lon},
            "time": time_payload({"asset": df}, elevation_mask=mask)}
