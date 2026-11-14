"""Streamlit user interface. Owner: Igor.

Two modes (see GLOSSARY.md), as pages in the top navigation bar: Explorer, to learn about the Moon and compare
Catalog Sites, and Site Planner, to evaluate one point (catalog or custom) with an Asset Height and an Elevation Mask.

The Explorer works like Google Earth: the 3D Moon (or the south pole relief map) fills the page behind a floating
panel on the left. The panel lists the catalog; choosing a site on the globe, the map or the list turns it into the
site's card, with its catalog information and data cards.
"""
import datetime

import pandas as pd
import streamlit as st

from src import catalog
from src.charts import (load_south_pole_relief, plot_earth_visibility, plot_monthly, plot_neighborhood,
                        plot_south_pole_relief_map, plot_sun_elevation)
from src.conditions import get_conditions, neighborhood_summary
from src.globe import moon_globe
from src.metrics import earth_visible_hours, hours_until_earthset, hours_until_sunset, monthly_summary, sunlight_hours
from src.sites import LUNAR_SITES

st.set_page_config(page_title="Lunar Landing Site Navigator", page_icon="🌕", layout="wide")

get_data = st.cache_data(show_spinner=False)(get_conditions)
get_neighborhood = st.cache_data(show_spinner=False)(neighborhood_summary)


@st.cache_data(show_spinner="Loading the LOLA south pole relief from NASA...")
def south_pole_relief():
    return load_south_pole_relief()


CUSTOM_SITE = "Custom Site"
SITE_STATE = "explorer_site"  # selected Catalog Site key, shared by the globe, the map and the catalog panel
NAV_HEIGHT = "3.75rem"  # Streamlit's top navigation bar
# Explorer panel widths: browsing the catalog, and with a site's data cards. src/globe.py mirrors them to keep the
# selected site centered in the uncovered part of the globe.
PANEL_NARROW, PANEL_WIDE = "380px", "min(46vw, 760px)"
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

# Explorer layout. The view (globe or map) is pinned behind everything; the panel floats over it. The rest of the
# page ignores the pointer so drags and clicks reach the globe. `st-key-<key>` classes come from st.container(key=).
EXPLORER_CSS = f"""<style>
  [data-testid="stApp"], [data-testid="stMain"], [data-testid="stMainBlockContainer"] {{ background: #000005; }}
  [data-testid="stMainBlockContainer"] {{ pointer-events: none; }}
  .st-key-explorer_view {{ position: fixed; top: {NAV_HEIGHT}; left: 0; right: 0; bottom: 0; z-index: 0;
    width: auto !important; pointer-events: auto; }}  /* Streamlit sets width: 100%, which would ignore right */
  .st-key-explorer_view [data-testid="stPlotlyChart"] {{ height: calc(100vh - {NAV_HEIGHT}); }}
  [class*="st-key-explorer_panel"] {{ position: fixed; top: calc({NAV_HEIGHT} + 14px); left: 14px; bottom: 14px;
    width: {PANEL_NARROW}; z-index: 2; pointer-events: auto; overflow-y: auto; padding: 16px 18px;
    background: rgba(14, 17, 23, 0.9); backdrop-filter: blur(10px); border: 1px solid rgba(255, 255, 255, 0.12);
    border-radius: 14px; box-shadow: 0 8px 30px rgba(0, 0, 0, 0.45); }}
  .st-key-explorer_panel_wide {{ width: {PANEL_WIDE}; }}
  @media (max-width: 760px) {{  /* phones: stack the panel under a shorter view instead of floating it */
    .st-key-explorer_view {{ position: relative; top: 0; left: 0 !important; height: 60vh; }}
    [class*="st-key-explorer_panel"] {{ position: relative; top: 0; left: 0; width: auto !important;
      max-height: none; }}
  }}
</style>"""


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


def site_details(site):
    st.markdown(f"**{site.get('name', '')}** · {KIND_LABELS.get(site.get('coordinate_kind'), 'Unspecified')}")
    st.caption(f"Lat {site['lat']}° · Lon {site['lon']}° E")
    st.write(site["description"])
    if "coordinate_meaning" in site:
        st.caption(f"Coordinate meaning: {site['coordinate_meaning']}")
    with st.expander("Scientific and exploration context"):
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


def site_analysis(key, df, mask=0.0, compact=False):
    """Timeline slider, countdown cards at the selected instant, and elevation charts.

    `compact` lays the cards out 2 x 2 and stacks the charts, for the Explorer's side panel.
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


def catalog_comparison(date, days, selected=None):
    rows = []
    for key, site in LUNAR_SITES.items():
        try:
            df = get_data(site["lat"], site["lon"], str(date), days, catalog.ASSET_HEIGHT_M)
        except Exception:
            continue
        rows.append({
            "Site": ("▶ " if key == selected else "") + site_label(key),
            "Type": KIND_LABELS.get(site.get("coordinate_kind"), "Unspecified"),
            "Sunlight (%)": 100 * sunlight_hours(df) / len(df),
            # Without terrain columns, sunlight_hours falls back to the ideal horizon: shows what relief changes.
            "Sunlight, ideal horizon (%)":
                100 * sunlight_hours(df.drop(columns=["sun_horizon", "illumination_fraction"])) / len(df),
            "Earth visibility (%)": 100 * earth_visible_hours(df) / len(df),
            "First Sunset in": format_countdown(hours_until_sunset(df, df["time"].iloc[0]), "Set at start"),
        })
    return pd.DataFrame(rows)


# Explorer selection: every way of choosing a site writes the same session state key before the script reruns.
def select_site(key):
    st.session_state[SITE_STATE] = key


def on_globe_click():
    clicked = st.session_state["explorer_globe"].get("clicked")
    if clicked in LUNAR_SITES:
        select_site(clicked)


def on_map_select(map_key):
    points = st.session_state[map_key]["selection"]["points"]
    if points:
        picked = points[0].get("customdata")
        picked = picked[0] if isinstance(picked, list) else picked
        if picked in LUNAR_SITES:
            select_site(picked)


def catalog_list(selected):
    st.caption("Click a site on the globe or the map, or pick one below.")
    for key, site in LUNAR_SITES.items():
        if key == selected:
            continue
        with st.container(border=True):
            st.markdown(f"**{site_label(key)}**  \n{KIND_LABELS.get(site.get('coordinate_kind'), 'Unspecified')}"
                        f" · {site['lat']:.2f}°, {site['lon']:.2f}° E")
            st.caption(site["description"])
            st.button("Explore", key=f"explorer_pick_{key}", on_click=select_site, args=(key,), width="stretch")


def site_cards(selected):
    """The selected site's catalog card followed by its data cards."""
    site = LUNAR_SITES[selected]
    st.button("← Back to catalog", key="explorer_back", on_click=select_site, args=(None,))
    with st.container(border=True):
        site_details(site)

    st.markdown("#### ☀️ Sunlight and 📡 Earth visibility")
    with st.container(border=True):
        date, days = window_inputs("explorer")
        df = load(site["lat"], site["lon"], date, days)
        if df is not None:
            site_analysis("explorer", df, compact=True)

    st.markdown("#### 🗓️ Seasons")
    with st.container(border=True):
        seasons = load(site["lat"], site["lon"], CACHE_START, (CACHE_END - CACHE_START).days)
        if seasons is not None:
            st.caption(f"{CACHE_START} to {CACHE_END - datetime.timedelta(days=1)}, at {catalog.ASSET_HEIGHT_M:g} m "
                       "Asset Height with terrain. The Moon's small axial tilt still shifts polar sunlight by season.")
            st.plotly_chart(plot_monthly(monthly_summary(seasons), full_month_hours=28 * 24), width="stretch",
                            key="explorer_seasons")

    st.markdown("#### ⚖️ Compare Catalog Sites")
    with st.container(border=True):
        st.caption(f"Same window ({date}, {days} days) at {catalog.ASSET_HEIGHT_M:g} m Asset Height, with terrain. "
                   "Pick a 28-day window to see a full lunar day, where terrain matters most.")
        if is_cached(date, days):
            st.dataframe(
                catalog_comparison(date, days, selected), hide_index=True, width="stretch",
                column_config={
                    "Sunlight (%)": st.column_config.ProgressColumn(min_value=0, max_value=100, format="%.0f%%"),
                    "Sunlight, ideal horizon (%)": st.column_config.NumberColumn(format="%.0f%%"),
                    "Earth visibility (%)": st.column_config.ProgressColumn(min_value=0, max_value=100,
                                                                            format="%.0f%%"),
                },
            )
        else:
            st.info(f"The comparison uses pre-computed data only. Pick a window between {CACHE_START} and "
                    f"{CACHE_END}.")


def explorer_page():
    st.html(EXPLORER_CSS)
    selected = st.session_state.get(SITE_STATE)
    views = ["🌕 Globe", "🗺️ South pole map"]
    view = st.session_state.get("explorer_view_choice") or views[0]

    with st.container(key="explorer_view"):  # neither view needs Horizons, so it opens even if Horizons is down
        if view == views[0]:
            moon_globe(LUNAR_SITES, selected, key="explorer_globe", on_click=on_globe_click,
                       height=f"calc(100vh - {NAV_HEIGHT})", page=True)
        else:
            # Unlike the globe, the flat map is not a background: start it at the panel's right edge.
            st.html(f"<style>.st-key-explorer_view {{ left: calc({PANEL_WIDE if selected else PANEL_NARROW} + 28px); "
                    "}</style>")
            try:
                relief = south_pole_relief()
            except Exception:
                relief = None
                st.caption("Could not load the LOLA relief from NASA PGDA; showing the sites only.")
            map_key = f"explorer_map_{selected}"  # a new widget per selection, so a stale selection never sticks
            st.plotly_chart(plot_south_pole_relief_map(LUNAR_SITES, selected, relief, height=None), width="stretch",
                            height="stretch", on_select=lambda: on_map_select(map_key), selection_mode="points",
                            key=map_key, config={"scrollZoom": True})

    with st.container(key="explorer_panel_wide" if selected else "explorer_panel"):
        st.markdown("### 🌕 Lunar Landing Site Navigator")
        st.caption("Solar power and direct-to-Earth communication for lunar south pole landings · "
                   "NASA Space Apps 2026")
        st.segmented_control("View", views, default=views[0], key="explorer_view_choice",
                             label_visibility="collapsed")
        st.selectbox("Catalog Site", list(LUNAR_SITES), index=None, placeholder="Choose a Catalog Site…",
                     format_func=site_label, key=SITE_STATE)
        if selected:
            site_cards(selected)
        else:
            catalog_list(selected)


def planner_page():
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
        site_analysis("planner", df, mask)


st.navigation([
    st.Page(explorer_page, title="Explorer", icon="🔭", url_path="explorer", default=True),
    st.Page(planner_page, title="Site Planner", icon="📍", url_path="planner"),
], position="top").run()
