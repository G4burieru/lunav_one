"""Streamlit user interface: one Google Earth-style screen (docs/UI_OVERHAUL.md). Owner: Igor.

The Moon View (src/moon_view), or the south pole relief map, fills the page. A rail of icons on the left opens one
floating panel at a time (src/panels): the catalog, a Site Card, the Site Planner or About. Explorer and Site
Planner are the two modes in GLOSSARY.md.
"""
import streamlit as st

from src.charts import load_south_pole_relief, plot_south_pole_relief_map
from src.moon_view import moon_view
from src.panels import about, catalog_list, planner, site_card
from src.panels.common import CUSTOM, PANEL, SELECTED, VIEW_CHOICE, VIEWS, open_panel, select_site
from src.sites import LUNAR_SITES

st.set_page_config(page_title="Lunar Landing Site Navigator", page_icon="static/icons/favicon.svg", layout="wide")

PANELS = {"catalog": catalog_list.render, "site": site_card.render, "planner": planner.render, "about": about.render}
RAIL = [("catalog", "Catalog", ":material/public:"), ("planner", "Plan", ":material/edit_location_alt:"),
        ("about", "About", ":material/info:")]
RAIL_WIDTH = "76px"
PANEL_LEFT = f"calc({RAIL_WIDTH} + 38px)"  # 14 px margins around the rail, 10 px gap
PANEL_WIDTH = {"catalog": "380px", "about": "380px", "site": "min(46vw, 760px)", "planner": "min(46vw, 760px)"}

# The view is pinned behind everything and the rail and the panel float over it. The rest of the page ignores the
# pointer so drags and clicks reach the view. `st-key-<key>` classes come from st.container(key=).
CSS = f"""<style>
  [data-testid="stHeader"] {{ display: none; }}
  [data-testid="stApp"], [data-testid="stMain"], [data-testid="stMainBlockContainer"] {{ background: #000005; }}
  [data-testid="stMainBlockContainer"] {{ pointer-events: none; }}
  .st-key-view {{ position: fixed; inset: 0; z-index: 0; width: auto !important; pointer-events: auto; }}
  .st-key-view [data-testid="stPlotlyChart"] {{ height: 100vh; }}
  .st-key-rail, .st-key-panel {{ position: fixed; top: 14px; z-index: 2; pointer-events: auto;
    background: rgba(14, 17, 23, 0.9); backdrop-filter: blur(10px); border: 1px solid rgba(255, 255, 255, 0.12);
    border-radius: 14px; box-shadow: 0 8px 30px rgba(0, 0, 0, 0.45); }}
  .st-key-rail {{ left: 14px; width: {RAIL_WIDTH}; padding: 8px 6px; }}
  .st-key-rail button {{ padding: 8px 2px; min-height: 0; }}
  .st-key-rail button > div, .st-key-rail button > div > span {{ flex-direction: column; gap: 2px; }}
  .st-key-rail button p {{ font-size: 0.72rem; }}
  .st-key-panel {{ left: {PANEL_LEFT}; bottom: 14px; overflow-y: auto; padding: 16px 18px; }}
  img[src*="static/icons/"] {{ height: 1.15em; width: auto; vertical-align: -0.2em; }}  /* icons at text size */
  @media (max-width: 760px) {{  /* phones: stack the rail, a shorter view and the panel instead of floating them */
    .st-key-rail, .st-key-view, .st-key-panel {{ position: relative; inset: auto; width: auto !important; }}
    .st-key-view {{ height: 60vh; overflow: hidden; }}
  }}
</style>"""


@st.cache_data(show_spinner="Loading the LOLA south pole relief from NASA...")
def south_pole_relief():
    return load_south_pole_relief()


def on_view_site():
    clicked = st.session_state["moon_view"].get("site")
    if clicked in LUNAR_SITES:
        select_site(clicked)


def on_map_select(map_key):
    points = st.session_state[map_key]["selection"]["points"]
    if points:
        picked = points[0].get("customdata")
        picked = picked[0] if isinstance(picked, list) else picked
        if picked in LUNAR_SITES:
            select_site(picked)


selected = st.session_state.get(SELECTED)
panel = st.session_state.get(PANEL, "catalog")
if panel == "site" and selected not in LUNAR_SITES and not st.session_state.get(CUSTOM):
    panel = "catalog"
st.html(CSS + f"<style>.st-key-panel {{ width: {PANEL_WIDTH[panel]}; }}</style>")

with st.container(key="rail"):
    for name, label, icon in RAIL:
        active = name == panel or (name, panel) == ("catalog", "site")
        st.button(label, icon=icon, key=f"rail_{name}", on_click=open_panel, args=(name,),
                  type="primary" if active else "secondary", width="stretch")

view = st.container(key="view")  # filled after the panel, whose render() can return what the view shows
with st.container(key="panel"):
    view_data = PANELS[panel]() or {}

with view:  # neither view needs Horizons, so it opens even if Horizons is down
    if (st.session_state.get(VIEW_CHOICE) or VIEWS[0]) == VIEWS[0]:
        moon_view(LUNAR_SITES, selected, key="moon_view", on_site=on_view_site, **view_data)
    else:
        # Unlike the globe, the flat map is not a background: start it at the panel's right edge.
        st.html(f"<style>.st-key-view {{ left: calc({PANEL_LEFT} + {PANEL_WIDTH[panel]} + 14px); }}</style>")
        try:
            relief = south_pole_relief()
        except Exception:
            relief = None
            st.caption("Could not load the LOLA relief from NASA PGDA; showing the sites only.")
        map_key = f"map_{selected}"  # a new widget per selection, so a stale selection never sticks
        st.plotly_chart(plot_south_pole_relief_map(LUNAR_SITES, selected, relief, height=None), width="stretch",
                        height="stretch", on_select=lambda: on_map_select(map_key), selection_mode="points",
                        key=map_key, config={"scrollZoom": True})
