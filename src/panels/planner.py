"""Site Planner panel: place a Surface Asset and evaluate its sunlight and Earth visibility (docs/UI_OVERHAUL.md,
task B3). Owner: Gabriel."""
import streamlit as st

from src import catalog
from src.charts import plot_earth_visibility, plot_sun_elevation
from src.colors import EARTH_RAMP, SUN_RAMP, css_gradient, ramp_hex
from src.conditions import cell_corners, live_neighborhood_horizons, live_neighborhood_summary
from src.metrics import earth_visible_hours, hours_until_earthset, hours_until_sunset, sunlight_hours
from src.panels import texts
from src.panels.common import (CACHE_START, CUSTOM_SITE, DATE_HELP, MOON_VIEW, SAVED_PREFIX, VIEW_CHOICE, VIEWS,
                               data_note, format_countdown, get_neighborhood, icon, load, planner_time, saved_sites,
                               selected_instant, site_label)
from src.sites import LUNAR_SITES
from src.terrain import SOUTH_POLE_DEM_LIMIT

HEIGHTS = {"Rover or lander · 2 m": catalog.ASSET_HEIGHT_M, "Mast · 10 m": 10.0, "Other height": None}
CELL = "planner_cell"  # {"hood", "index"}: the Site Neighborhood cell holding the Surface Asset, None at the center
HOOD, LIVE_HOOD = "planner_hood", "planner_live_hood"  # the Site Neighborhood shown, and the one asked for live

get_live_horizons = st.cache_data(show_spinner=False, max_entries=8)(live_neighborhood_horizons)  # ~3.6 MB each
get_live_summary = st.cache_data(show_spinner=False, max_entries=32)(live_neighborhood_summary)


def save_custom(lat, lon):
    """Keep the Custom Site on the Moon View under the typed name, and plan it under that name."""
    name = st.session_state.get("planner_name", "").strip()
    key = SAVED_PREFIX + name
    saved_sites()[key] = {"name": name, "lat": lat, "lon": lon}
    st.session_state.update(planner_site=key, planner_name="")


def remove_saved(key):
    """Back to an unnamed Custom Site at the same place."""
    site = saved_sites().pop(key)
    st.session_state.update(planner_site=CUSTOM_SITE, planner_lat=site["lat"], planner_lon=site["lon"])


def where():
    saved = saved_sites()
    key = st.selectbox("Site", [*LUNAR_SITES, *saved, CUSTOM_SITE], format_func=site_label, key="planner_site")
    if key == CUSTOM_SITE:
        col_lat, col_lon = st.columns(2)
        lat = col_lat.number_input("Latitude (°)", -90.0, 90.0, -89.5, 0.01, key="planner_lat")
        lon = col_lon.number_input("East longitude (°)", -180.0, 180.0, 0.0, 0.01, key="planner_lon")
        col_name, col_save = st.columns([3, 2], vertical_alignment="bottom")
        name = col_name.text_input("Name", key="planner_name", max_chars=40,
                                   placeholder="e.g. Ridge east of Shackleton",
                                   help="Keeps this Custom Site on the Moon View until you reload or close the page.")
        taken = {s["name"] for s in saved.values()} | {site_label(k) for k in LUNAR_SITES}
        col_save.button("Keep on the map", key="planner_save", on_click=save_custom, args=(lat, lon),
                        width="stretch", disabled=not name.strip() or name.strip() in taken)
        if name.strip() in taken:
            st.caption("That name is already used.")
    elif key in saved:
        lat, lon = saved[key]["lat"], saved[key]["lon"]
        col_text, col_remove = st.columns([3, 2], vertical_alignment="center")
        col_text.caption(f"Custom Site · Lat {lat:.4f}° · Lon {lon:.4f}° E")
        col_remove.button("Remove from the map", key="planner_remove", on_click=remove_saved, args=(key,),
                          width="stretch")
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


def choose_cell(hood, index):
    st.session_state[CELL] = {"hood": hood, "index": index} if index is not None else None


def ask_live(hood):
    st.session_state[LIVE_HOOD] = hood


def on_map_cell():
    """Moon View callback: a click on a Site Neighborhood cell moves the Surface Asset there."""
    index = st.session_state[MOON_VIEW].get("cell")
    if index is not None:
        choose_cell(st.session_state.get(HOOD), int(index))


def neighborhood_points(key, lat, lon, height, date, days, mask):
    """(id, points) of the Site Neighborhood around (lat, lon): pre-computed for a Catalog Site at 2 m, otherwise
    computed live (about 30 s) once the user asks; points is None until then."""
    if key in LUNAR_SITES and height == catalog.ASSET_HEIGHT_M:
        return key, get_neighborhood(key, str(date), days, mask)
    hood = f"{key}:{lat:.5f},{lon:.5f}:{height:g}"
    if st.session_state.get(LIVE_HOOD) != hood:
        st.button("Paint the Site Neighborhood (computed live, about 30 s)", key="planner_live", on_click=ask_live,
                  args=(hood,), width="stretch")
        return hood, None
    with st.spinner("Computing the Site Neighborhood live, about 30 s..."):
        return hood, get_live_summary(lat, lon, get_live_horizons(lat, lon, height), str(date), days, mask)


def neighborhood(key, lat, lon, height, date, days, mask):
    """The Site Neighborhood around (lat, lon), painted on the south polar map (tasks A6 and B6). A click on a cell,
    or the best cell button, moves the Surface Asset there. Returns ((lat, lon) of the Surface Asset, the Moon View's
    neighborhood data or None)."""
    name = "the Custom Site" if key == CUSTOM_SITE else site_label(key)
    st.markdown(f"{icon('neighborhood')} **Site Neighborhood**: click a cell on the map to move the Surface Asset "
                "there.")
    layer = st.radio("Color by", ["Sunlight", "Earth visibility"], horizontal=True, key="planner_layer")
    column, ramp = ("sunlight_pct", SUN_RAMP) if layer == "Sunlight" else ("earth_visible_pct", EARTH_RAMP)
    measure = "sunlight" if layer == "Sunlight" else "Earth visibility"  # mid-sentence
    try:
        hood, points = neighborhood_points(key, lat, lon, height, date, days, mask)
    except Exception as e:
        st.error(f"Could not compute the Site Neighborhood: {e}")
        return (lat, lon), None
    st.session_state[HOOD] = hood  # for on_map_cell
    if points is None:
        return (lat, lon), None
    st.html(f'<div style="display:flex;align-items:center;gap:8px;font-size:0.8rem;opacity:0.8">0%'
            f'<div style="flex:1;height:10px;border-radius:5px;background:{css_gradient(ramp)}"></div>100%</div>')
    values = points[column].to_numpy()
    best = int(values.argmax()) if values.max() - values.min() >= 0.5 else None  # None: no cell is better
    chosen = st.session_state.get(CELL) or {}
    index = chosen.get("index") if chosen.get("hood") == hood and (chosen.get("index") or 0) < len(points) else None
    use_best, use_center = st.columns(2)
    use_best.button(f"Best cell: {values[best]:.0f}%" if best is not None else "No better cell", key="planner_best",
                    on_click=choose_cell, args=(hood, best), width="stretch", disabled=best is None or index == best)
    use_center.button("Back to the site", key="planner_center", on_click=choose_cell, args=(hood, None),
                      width="stretch", disabled=index is None)
    if best is None:
        st.caption(f"Every cell gets {values.mean():.0f}% {measure} in this window.")
    if index is None:
        st.caption(f"Surface Asset at {name} itself. Darker cells get less {measure}"
                   + ("." if best is None else f"; the dashed outline marks the best cell, "
                      f"{points['east_m'].iloc[best]:+.0f} m east and {points['north_m'].iloc[best]:+.0f} m north."))
        asset = lat, lon
    else:
        point = points.iloc[index]
        st.caption(f"Surface Asset {point['east_m']:+.0f} m east and {point['north_m']:+.0f} m north of {name}: "
                   f"{point[column]:.0f}% {measure} · Lat {point['lat']:.5f}° · Lon {point['lon']:.5f}° E")
        asset = float(point["lat"]), float(point["lon"])
    corners = cell_corners({"lat": lat, "lon": lon}, points["east_m"], points["north_m"]).round(6).tolist()
    colors = ramp_hex(points[column] / 100, ramp)
    data = {"site": hood, "center": {"lat": lat, "lon": lon}, "label": measure, "selected": index, "best": best,
            "reach_m": catalog.NEIGHBORHOOD_RADIUS_M + catalog.NEIGHBORHOOD_SPACING_M,
            "cells": [{"corners": c, "value": round(float(v), 1), "color": color}
                      for c, v, color in zip(corners, points[column], colors)]}
    return asset, data


def results(df, mask, days):
    """The Surface Asset at the Moon View time bar's instant, and over the whole window. Returns the instant."""
    at = selected_instant(df)
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
    st.markdown(f"At **{at:%Y-%m-%d %H:%M} UTC**, {sun} and {earth}. Over the {days} days, the mean Illumination "
                f"Fraction is {100 * sun_hours / len(df):.0f}% ({sun_hours:.0f} h of full Sun) and Earth is in view "
                f"{100 * earth_hours / len(df):.0f}% of the time.")
    st.caption("The countdowns follow the time bar at the bottom of the view: move it, type a date or play it, "
               "then release or pause.")
    data_note(df)
    st.plotly_chart(plot_sun_elevation(df, at), width="stretch", key="planner_sun")
    st.plotly_chart(plot_earth_visibility(df, at, mask), width="stretch", key="planner_earth")
    return at


def render():
    """The four steps. Returns what the Moon View should show: the map or the globe for the site, the Surface Asset,
    the Site Neighborhood and the Surface Asset's time bar states."""
    st.markdown(f"### {icon('planner')} Site Planner")
    st.caption("Place a Surface Asset precisely and evaluate its sunlight and Earth visibility. Right-click the Moon "
               "to leave the Planner and browse again.")
    st.markdown("**1 · Where**")
    key, lat, lon = where()
    st.markdown("**2 · Surface Asset**")
    height, mask = surface_asset()
    st.markdown("**3 · When**")
    date, days = when()
    hood = None
    polar = lat <= SOUTH_POLE_DEM_LIMIT  # the Site Neighborhood needs the south pole DEMs
    st.session_state[VIEW_CHOICE] = VIEWS[1] if polar else VIEWS[0]  # leaving the Planner keeps this view
    if polar:
        (lat, lon), hood = neighborhood(key, lat, lon, height, date, days, mask)
    else:
        st.caption("The Site Neighborhood is drawn on the south polar map, for sites south of 80°S.")
    view = {"mode": "planner", "asset": {"lat": lat, "lon": lon}, "neighborhood": hood,
            "view": "map" if polar else "globe", "view_id": f"planner:{key}"}

    st.markdown("**4 · Results**")
    df = load(lat, lon, date, days, height, catalog_site=key in LUNAR_SITES)
    if df is None:
        return view
    at = results(df, mask, days)  # the time bar starts there when its window changes
    return {**view, "time": planner_time(df, instant=f"{at:%Y-%m-%dT%H:%M:%SZ}", elevation_mask=mask)}
