"""Moon View: the Moon that fills the page behind the panels (docs/adr/0003-one-screen-moon-view.md). Owner: Igor.

One Streamlit custom component (components v2) written in JavaScript, one file per part, joined in `_JS_FILES`
order into a single module. The data going in and the events coming out are listed in docs/UI_OVERHAUL.md. Read an
event in its callback from st.session_state[key], e.g. st.session_state[key]["site"] for a clicked Catalog Site.
"""
from pathlib import Path

import streamlit as st

_DIR = Path(__file__).parent
_JS_FILES = ("globe.js", "polar_map.js", "time_bar.js", "view.js")  # view.js last: helpers and the default export
# Overlays marked data-for show only with that view. Leaflet's stylesheet is linked here, inside the component's
# shadow root, where the polar map lives; keep its version in step with polar_map.js.
_HTML = """
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/leaflet@1.9.4/dist/leaflet.css">
<div class="moon-view" data-view="globe">
  <div class="globe"></div>
  <div class="polar-map"></div>
  <div class="overlay hint" data-for="globe">Drag to rotate · scroll to zoom · click a site to explore it</div>
  <div class="overlay hint" data-for="map">Drag to pan · scroll to zoom · click a site to explore it</div>
  <div class="overlay layers"><span class="choices" data-for="globe"></span><span class="choices" data-for="map"></span>
  </div>
  <div class="overlay info"><div class="info-name"></div><div class="info-text"></div></div>
  <div class="overlay time-bar" hidden>
    <button class="play" type="button" aria-label="Play"></button>
    <input class="time-slider" type="range" min="0" max="0" step="1" value="0" aria-label="Instant (UTC)">
    <output class="time-label"></output>
    <div class="time-readout"></div>
  </div>
  <div class="overlay status" data-for="globe"></div>
  <div class="overlay status" data-for="map"></div>
  <div class="overlay credit" data-for="globe">Imagery: LRO WAC · Elevation: LOLA · NASA Moon Trek</div>
  <div class="overlay credit" data-for="map">Photos: LROC NAC and WAC · Relief: LOLA · NASA Moon Trek</div>
</div>
"""


def _read(name):
    return (_DIR / name).read_text(encoding="utf-8")


def moon_view(sites, selected=None, *, key, on_site=None, on_point=None, on_cell=None, on_instant=None,
              height="100vh", mode="explorer", view="globe", view_id="", custom=None, asset=None, time=None,
              overlays=(), neighborhood=None):
    """Mount the Moon View over `sites` (a LUNAR_SITES-like dict), highlighting the `selected` key.

    `height` is any CSS length. The arguments after it follow the data contract in docs/UI_OVERHAUL.md: `view`
    ("globe" or "map") is applied only when `view_id` changes; `time` feeds the time bar, whose `instant` reaches
    Python only if `on_instant` is given; `mode` and `asset` draw the Site Planner's Surface Asset. `custom`,
    `overlays` and `neighborhood` wait for their tasks.
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
