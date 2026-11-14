"""Site Planner panel: one point, an Asset Height and an Elevation Mask (docs/UI_OVERHAUL.md, task B3).
Owner: Gabriel."""
import streamlit as st

from src import catalog
from src.charts import plot_neighborhood
from src.panels.common import (CUSTOM_SITE, get_neighborhood, load, site_analysis, site_label,
                               window_inputs)
from src.sites import LUNAR_SITES


def render():
    st.caption("🌕 **Lunar Landing Site Navigator** · Site Planner: place a surface asset precisely and evaluate its "
               "sunlight and Earth visibility")
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
    if key != CUSTOM_SITE and height == catalog.ASSET_HEIGHT_M:
        st.subheader("🧭 Site Neighborhood")
        layer = st.radio("Color by", ["Sunlight", "Earth visibility"], horizontal=True, key="planner_layer")
        column = "sunlight_pct" if layer == "Sunlight" else "earth_visible_pct"
        try:
            points = get_neighborhood(key, str(date), days, mask)
        except Exception as e:
            st.error(f"Could not compute the Site Neighborhood: {e}")
            points = None
        if points is not None:
            event = st.plotly_chart(plot_neighborhood(points, column, layer), width="stretch", on_select="rerun",
                                    selection_mode="points", key=f"planner_neighborhood_{key}")
            picked = event.selection.points
            match = points[(points["east_m"] == picked[0]["x"]) & (points["north_m"] == picked[0]["y"])] \
                if picked else points.iloc[0:0]
            if not match.empty:
                point = match.iloc[0]
                lat, lon = float(point["lat"]), float(point["lon"])
                st.caption(f"Analyzing the selected point: {point['east_m']:+.0f} m east, {point['north_m']:+.0f} m "
                           f"north of {site_label(key)} · Lat {lat:.5f}° · Lon {lon:.5f}° E")
            else:
                st.caption(f"Click a cell (or the ★ best point) to analyze that exact point. "
                           f"Showing {site_label(key)} at (0, 0).")
    elif key != CUSTOM_SITE:
        st.caption(f"The Site Neighborhood map is pre-computed for {catalog.ASSET_HEIGHT_M:g} m Asset Height only.")
    df = load(lat, lon, date, days, height, catalog_site=key != CUSTOM_SITE)
    if df is not None:
        site_analysis("planner", df, mask, compact=True)
