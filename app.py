"""Streamlit user interface: one Google Earth-style screen (docs/UI_OVERHAUL.md). Owner: Igor.

The Moon View (src/moon_view) fills the page with the 3D globe or the south polar map. A rail of icons on the left
opens one floating panel at a time (src/panels): the catalog, a Site Card, the Site Planner or About. Explorer and
Site Planner are the two modes in GLOSSARY.md.
"""
import sys
from pathlib import Path

import streamlit as st


@st.cache_resource
def _imported_src():
    """Process-wide record of the src code that the imported src modules come from."""
    return {}


# Streamlit drops changed modules only for the browser sessions that saw the change, and Streamlit Cloud updates the
# code in place without restarting Python. A new session could then run this app.py with old src modules: the
# ImportError after PR #24. So whenever a src/*.py file changed since the src modules were imported, drop them all;
# the imports below then load the current code.
_stamp = max(path.stat().st_mtime for path in (Path(__file__).parent / "src").rglob("*.py"))
if _imported_src().get("stamp") != _stamp:
    for name in [name for name in sys.modules if name == "src" or name.startswith("src.")]:
        del sys.modules[name]
    _imported_src()["stamp"] = _stamp

from src.moon_view import moon_view  # noqa: E402 (imports after the check above)
from src.panels import about, catalog_list, layers, planner, site_card  # noqa: E402
from src.panels.common import (  # noqa: E402
    CUSTOM, MOON_VIEW, OVERLAYS, PANEL, PANEL_OPEN, SELECTED, VIEW_CHOICE, VIEWS, catalog_time, open_panel,
    rail_active, select_custom, select_site)
from src.sites import LUNAR_SITES  # noqa: E402

st.set_page_config(page_title="Lunar Landing Site Navigator", page_icon="static/icons/favicon.svg", layout="wide")

PANELS = {"catalog": catalog_list.render, "site": site_card.render, "planner": planner.render,
          "layers": layers.render, "about": about.render}
RAIL = [("catalog", "Catalog", ":material/public:"), ("planner", "Plan", ":material/edit_location_alt:"),
        ("layers", "Layers", ":material/layers:"), ("about", "About", ":material/info:")]
RAIL_WIDTH = "76px"
PANEL_LEFT = f"calc({RAIL_WIDTH} + 38px)"  # 14 px margins around the rail, 10 px gap
PANEL_WIDTH = {"catalog": "380px", "layers": "380px", "about": "380px", "site": "min(46vw, 760px)",
               "planner": "min(46vw, 760px)"}
POLAR_LAT = -80.0  # choosing a site south of this opens the south polar map; other sites open the globe

# The view is pinned behind everything and the rail and the panel float over it. The rest of the page ignores the
# pointer so drags and clicks reach the view. `st-key-<key>` classes come from st.container(key=).
CSS = f"""<style>
  /* Streamlit's header stays only for its "Running..." indicator, the one sign that a click is being processed.
     Its toolbar spans the top right and sits above the view, so it must let clicks through too: otherwise it takes
     them from the view's layer and full screen buttons there. */
  [data-testid="stHeader"], [data-testid="stToolbar"] {{ background: transparent; pointer-events: none; }}
  [data-testid="stToolbarActions"], [data-testid="stAppDeployButton"], [data-testid="stMainMenu"] {{ display: none; }}
  [data-testid="stStatusWidget"] {{ position: fixed; top: 14px; left: 50%; transform: translateX(-50%); z-index: 3;
    pointer-events: auto; padding: 2px 12px; border-radius: 999px; background: rgba(14, 17, 23, 0.9);
    border: 1px solid rgba(255, 255, 255, 0.12); }}
  [data-testid="stApp"], [data-testid="stMain"], [data-testid="stMainBlockContainer"] {{ background: #000005; }}
  [data-testid="stMainBlockContainer"] {{ pointer-events: none; }}
  .st-key-view {{ position: fixed; inset: 0; z-index: 0; width: auto !important; pointer-events: auto; }}
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


def on_view_site():
    clicked = st.session_state[MOON_VIEW].get("site")
    if clicked in LUNAR_SITES:
        select_site(clicked)


def on_view_point():
    point = st.session_state[MOON_VIEW].get("point")  # sent after the user confirms "Analyze this point?"
    if point:
        select_custom(point["lat"], point["lon"])


def on_view_instant():
    """Registering a callback is what keeps the time bar's "instant" in st.session_state[MOON_VIEW]; the panels
    read it while they render (selected_instant in src/panels/common.py)."""


def explorer_time():
    """The Explorer's time bar: every Catalog Site over 2027–2028, from the instant the bar last sent."""
    try:
        return dict(catalog_time(), instant=(st.session_state.get(MOON_VIEW) or {}).get("instant"))
    except Exception:  # pre-computed data missing: the view opens without a time bar
        return None


def view_request(selected, custom):
    """The view to show ("globe" or "map") and a view_id that changes whenever the Moon View should switch to it.

    The switch at the top of the Explorer panels picks the view. Choosing a site, or a Custom Site, moves the switch
    to the view that shows it: the south polar map for polar sites, the globe for the others.
    """
    ss = st.session_state
    switch = False
    target = selected or (custom and (custom["lat"], custom["lon"]))
    if ss.get("view_site") != target:
        ss["view_site"] = target
        if target:
            lat = LUNAR_SITES[selected]["lat"] if selected else custom["lat"]
            ss[VIEW_CHOICE] = VIEWS[1] if lat <= POLAR_LAT else VIEWS[0]
            switch = True  # even to the view already chosen: the user may have moved away from the site
    if ss.get(VIEW_CHOICE) is None:  # unselected, or dropped while a panel without the switch was open
        ss[VIEW_CHOICE] = ss.get("view_shown", VIEWS[0])
    if ss.get("view_shown") != ss[VIEW_CHOICE]:
        ss["view_shown"] = ss[VIEW_CHOICE]
        switch = True
    if switch:
        ss["view_id"] = ss.get("view_id", 0) + 1
    return ("map" if ss[VIEW_CHOICE] == VIEWS[1] else "globe"), ss["view_id"]


selected, custom = st.session_state.get(SELECTED), st.session_state.get(CUSTOM)
panel, panel_open = st.session_state.get(PANEL, "catalog"), st.session_state.get(PANEL_OPEN, True)
if panel == "site" and selected not in LUNAR_SITES and not custom:
    panel = "catalog"
# A hidden panel is still rendered, so its widgets keep their values until it is shown again.
st.html(CSS + f"<style>.st-key-panel {{ width: {PANEL_WIDTH[panel]};"
        + ("" if panel_open else " display: none;") + " }</style>")

with st.container(key="rail"):
    for name, label, icon in RAIL:
        st.button(label, icon=icon, key=f"rail_{name}", on_click=open_panel, args=(name,),
                  type="primary" if panel_open and rail_active(name) else "secondary", width="stretch",
                  help=f"Hide the {label} panel" if panel_open and rail_active(name) else None)

view, view_id = view_request(selected, custom)  # before the panel, whose globe/map switch it may move
view_slot = st.container(key="view")  # filled after the panel, whose render() can return what the view shows
with st.container(key="panel"):
    view_data = PANELS[panel]() or {}

with view_slot:  # pre-computed data only, so the view opens even if Horizons is down
    # A panel's render() can override any of these, e.g. the Site Planner's view, Surface Asset and time bar data.
    moon_view(LUNAR_SITES, selected, key=MOON_VIEW, **{"on_site": on_view_site, "on_point": on_view_point,
                                                       "on_cell": planner.on_map_cell, "on_instant": on_view_instant,
                                                       "view": view, "view_id": view_id, "custom": custom,
                                                       "time": explorer_time(),
                                                       "overlays": st.session_state.get(OVERLAYS, ()), **view_data})
