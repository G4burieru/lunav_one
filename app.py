"""Streamlit user interface: one Google Earth-style screen (docs/UI_OVERHAUL.md). Owner: Igor.

The Moon View (src/moon_view) fills the page with the 3D globe or the south polar map. A rail of icons on the left
opens one floating panel at a time (src/panels): the catalog, a Site Card, the Site Planner or About. Explorer and
Site Planner are the two modes in GLOSSARY.md.
"""
import streamlit as st

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
POLAR_LAT = -80.0  # choosing a site south of this opens the south polar map; other sites open the globe

# The view is pinned behind everything and the rail and the panel float over it. The rest of the page ignores the
# pointer so drags and clicks reach the view. `st-key-<key>` classes come from st.container(key=).
CSS = f"""<style>
  [data-testid="stHeader"] {{ display: none; }}
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
    clicked = st.session_state["moon_view"].get("site")
    if clicked in LUNAR_SITES:
        select_site(clicked)


def view_request(selected):
    """The view to show ("globe" or "map") and a view_id that changes whenever the Moon View should switch to it.

    The switch at the top of the Explorer panels picks the view. Choosing a site moves the switch to the view that
    shows it: the south polar map for polar sites, the globe for the others.
    """
    ss = st.session_state
    switch = False
    if ss.get("view_site") != selected:
        ss["view_site"] = selected
        if selected:
            ss[VIEW_CHOICE] = VIEWS[1] if LUNAR_SITES[selected]["lat"] <= POLAR_LAT else VIEWS[0]
            switch = True  # even to the view already chosen: the user may have moved away from the site
    if ss.get(VIEW_CHOICE) is None:  # unselected, or dropped while a panel without the switch was open
        ss[VIEW_CHOICE] = ss.get("view_shown", VIEWS[0])
    if ss.get("view_shown") != ss[VIEW_CHOICE]:
        ss["view_shown"] = ss[VIEW_CHOICE]
        switch = True
    if switch:
        ss["view_id"] = ss.get("view_id", 0) + 1
    return ("map" if ss[VIEW_CHOICE] == VIEWS[1] else "globe"), ss["view_id"]


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

view, view_id = view_request(selected)  # before the panel, whose globe/map switch it may move
view_slot = st.container(key="view")  # filled after the panel, whose render() can return what the view shows
with st.container(key="panel"):
    view_data = PANELS[panel]() or {}

with view_slot:  # the view needs no Horizons data, so it opens even if Horizons is down
    moon_view(LUNAR_SITES, selected, key="moon_view", on_site=on_view_site, view=view, view_id=view_id, **view_data)
