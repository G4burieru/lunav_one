"""Site Planner panel: place a Surface Asset and evaluate its sunlight and Earth visibility (docs/UI_OVERHAUL.md,
task B3). Owner: Gabriel."""
import datetime

import streamlit as st

from src import catalog
from src.charts import plot_earth_visibility, plot_sun_elevation
from src.colors import EARTH_RAMP, SUN_RAMP, css_gradient, ramp_hex
from src.conditions import cell_corners
from src.metrics import earth_visible_hours, hours_until_earthset, hours_until_sunset, sunlight_hours
from src.panels import texts
from src.panels.common import (CACHE_START, CUSTOM_SITE, DATE_HELP, MOON_VIEW, data_note, format_countdown,
                               get_neighborhood, icon, load, site_label, time_payload)
from src.sites import LUNAR_SITES

HEIGHTS = {"Rover or lander · 2 m": catalog.ASSET_HEIGHT_M, "Mast · 10 m": 10.0, "Other height": None}
CELL = "planner_cell"  # {"site", "index"}: the Site Neighborhood cell holding the Surface Asset, None at the site
POLAR_LAT = -80.0  # south of this, the Site Planner shows the south polar map


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


def choose_cell(key, index):
    st.session_state[CELL] = {"site": key, "index": index} if index is not None else None


def on_map_cell():
    """Moon View callback: a click on a Site Neighborhood cell moves the Surface Asset there."""
    index = st.session_state[MOON_VIEW].get("cell")
    if index is not None:
        choose_cell(st.session_state.get("planner_site"), int(index))


def neighborhood(key, date, days, mask):
    """The Site Neighborhood, painted on the south polar map (task B6). A click on a cell, or the "best cell" button,
    moves the Surface Asset there. Returns ((lat, lon) of the Surface Asset, the Moon View's neighborhood data)."""
    site = LUNAR_SITES[key]
    st.markdown(f"{icon('neighborhood')} **Site Neighborhood**: click a cell on the map to move the Surface Asset "
                "there.")
    layer = st.radio("Color by", ["Sunlight", "Earth visibility"], horizontal=True, key="planner_layer")
    column, ramp = ("sunlight_pct", SUN_RAMP) if layer == "Sunlight" else ("earth_visible_pct", EARTH_RAMP)
    measure = "sunlight" if layer == "Sunlight" else "Earth visibility"  # mid-sentence
    try:
        points = get_neighborhood(key, str(date), days, mask)
    except Exception as e:
        st.error(f"Could not compute the Site Neighborhood: {e}")
        return (site["lat"], site["lon"]), None
    st.html(f'<div style="display:flex;align-items:center;gap:8px;font-size:0.8rem;opacity:0.8">0%'
            f'<div style="flex:1;height:10px;border-radius:5px;background:{css_gradient(ramp)}"></div>100%</div>')
    best = int(points[column].to_numpy().argmax())
    chosen = st.session_state.get(CELL) or {}
    index = chosen.get("index") if chosen.get("site") == key and (chosen.get("index") or 0) < len(points) else None
    best_point = points.iloc[best]
    use_best, use_site = st.columns(2)
    use_best.button(f"Best cell: {best_point[column]:.0f}%", key="planner_best", on_click=choose_cell,
                    args=(key, best), width="stretch", disabled=index == best)
    use_site.button("Back to the site", key="planner_center", on_click=choose_cell, args=(key, None),
                    width="stretch", disabled=index is None)
    if index is None:
        st.caption(f"Surface Asset at {site_label(key)} itself. Darker cells get less {measure}; the dashed "
                   f"outline marks the best cell, {best_point['east_m']:+.0f} m east and "
                   f"{best_point['north_m']:+.0f} m north.")
        lat, lon = site["lat"], site["lon"]
    else:
        point = points.iloc[index]
        st.caption(f"Surface Asset {point['east_m']:+.0f} m east and {point['north_m']:+.0f} m north of "
                   f"{site_label(key)}: {point[column]:.0f}% {measure} · Lat {point['lat']:.5f}° · "
                   f"Lon {point['lon']:.5f}° E")
        lat, lon = float(point["lat"]), float(point["lon"])
    corners = cell_corners(site, points["east_m"], points["north_m"]).round(6).tolist()
    colors = ramp_hex(points[column] / 100, ramp)
    data = {"site": key, "center": {"lat": site["lat"], "lon": site["lon"]}, "label": measure, "selected": index,
            "best": best, "reach_m": catalog.NEIGHBORHOOD_RADIUS_M + catalog.NEIGHBORHOOD_SPACING_M,
            "cells": [{"corners": c, "value": round(float(v), 1), "color": color}
                      for c, v, color in zip(corners, points[column], colors)]}
    return (lat, lon), data


def results(df, mask, days):
    # shortcut: keeps its own Instant slider until the Moon View time bar (task A3) covers the Planner window.
    times = list(df["time"].dt.to_pydatetime())
    at = st.slider("Instant (UTC)", times[0], times[-1], times[0], datetime.timedelta(hours=1),
                   format="YYYY-MM-DD HH:mm", key="planner_at")
    row = df[df["time"] == at].iloc[0]
    sunset, earthset = hours_until_sunset(df, at), hours_until_earthset(df, at, mask)
    sun_hours, earth_hours = sunlight_hours(df), earth_visible_hours(df, mask)
    cols = [*st.columns(2), *st.columns(2)]
    cols[0].metric(f"{icon('sun')} Time to Sunset", format_countdown(sunset, "Sun down"),
                   f"{row['illumination_fraction']:.0%} of the solar disk visible", delta_color="off",
                   delta_arrow="off", border=True)
    cols[1].metric(f"{icon('earth')} Time to Earthset", format_countdown(earthset, "Not visible"),
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
    """The four steps. Returns what the Moon View should show: the map or the globe for the site, the Surface Asset,
    the Site Neighborhood and the Surface Asset's time bar states."""
    st.markdown(f"### {icon('planner')} Site Planner")
    st.caption("Place a Surface Asset precisely and evaluate its sunlight and Earth visibility.")
    st.markdown("**1 · Where**")
    key, lat, lon = where()
    st.markdown("**2 · Surface Asset**")
    height, mask = surface_asset()
    st.markdown("**3 · When**")
    date, days = when()
    hood = None
    polar = lat <= POLAR_LAT
    if key != CUSTOM_SITE and height == catalog.ASSET_HEIGHT_M and polar:
        (lat, lon), hood = neighborhood(key, date, days, mask)
    elif key != CUSTOM_SITE:
        st.caption(f"The Site Neighborhood is drawn on the south polar map, for sites south of 80°S at "
                   f"{catalog.ASSET_HEIGHT_M:g} m Asset Height, where it is pre-computed.")
    view = {"mode": "planner", "asset": {"lat": lat, "lon": lon}, "neighborhood": hood,
            "view": "map" if polar else "globe", "view_id": f"planner:{key}"}

    st.markdown("**4 · Results**")
    df = load(lat, lon, date, days, height, catalog_site=key != CUSTOM_SITE)
    if df is None:
        return view
    results(df, mask, days)
    return {**view, "time": time_payload({"asset": df}, elevation_mask=mask)}
