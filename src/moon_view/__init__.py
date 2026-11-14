"""Moon View: the Moon that fills the page behind the panels (docs/adr/0003-one-screen-moon-view.md). Owner: Igor.

One Streamlit custom component (components v2) written in JavaScript, one file per part, joined in `_JS_FILES`
order into a single module. The data going in and the events coming out are listed in docs/UI_OVERHAUL.md. Read an
event in its callback from st.session_state[key], e.g. st.session_state[key]["site"] for a clicked Catalog Site.
"""
from pathlib import Path

import streamlit as st

_DIR = Path(__file__).parent
_JS_FILES = ("globe.js", "view.js")  # view.js last: it holds the module's default export
_HTML = """
<div class="moon-view">
  <div class="globe"></div>
  <div class="overlay hint">Drag to rotate · scroll to zoom · click a site to explore it</div>
  <div class="overlay layers"></div>
  <div class="overlay info"><div class="info-name"></div><div class="info-text"></div></div>
  <div class="overlay status"></div>
  <div class="overlay credit">Imagery: LRO WAC · Elevation: LOLA · NASA Moon Trek</div>
</div>
"""


def _read(name):
    return (_DIR / name).read_text(encoding="utf-8")


def moon_view(sites, selected=None, *, key, on_site=None, on_point=None, on_cell=None, on_instant=None,
              height="100vh", mode="explorer", view="globe", view_id="", custom=None, asset=None, time=None,
              overlays=(), neighborhood=None):
    """Mount the Moon View over `sites` (a LUNAR_SITES-like dict), highlighting the `selected` key.

    `height` is any CSS length. The arguments after it follow the data contract in docs/UI_OVERHAUL.md; the globe
    ignores them until the polar map, the time bar and the overlays use them.
    """
    # Registered on every run, so edits to the .js and .css files show up on the next rerun without a restart.
    component = st.components.v2.component(
        "lunav_moon_view", html=_HTML, css=_read("view.css"), js="\n".join(_read(f) for f in _JS_FILES))
    data = {
        "sites": [{"key": k, "name": s.get("name", k), "lat": s["lat"], "lon": s["lon"],
                   "kind": s.get("coordinate_kind"), "description": s.get("description", "")}
                  for k, s in sites.items()],
        "selected": selected, "height": height, "mode": mode, "view": view, "view_id": view_id, "custom": custom,
        "asset": asset, "time": time, "overlays": list(overlays), "neighborhood": neighborhood,
    }
    return component(key=key, data=data, on_site_change=on_site, on_point_change=on_point, on_cell_change=on_cell,
                     on_instant_change=on_instant)
