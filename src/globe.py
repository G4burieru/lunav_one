"""Interactive 3D Moon globe: globe.gl (Three.js / WebGL) as a Streamlit custom component. Owner: Igor.

The browser builds the textures itself from NASA Moon Trek WMTS tiles (served with CORS `*`), so nothing heavy goes
through Python and the tiles stay in the browser cache across reruns. Clicking a Catalog Site sends its key back
to Python as the `clicked` trigger. The globe is created once per page; later reruns only update the sites, the
selection and the camera.
"""
import json
from html import escape

import streamlit as st

GLOBE_GL_URL = "https://cdn.jsdelivr.net/npm/globe.gl@2.46.2/dist/globe.gl.min.js"
TREK_TILE_URL = "https://trek.nasa.gov/tiles/Moon/EQ/{layer}/1.0.0/default/default028mm/{level}/{row}/{col}.{ext}"
# Equirectangular Moon Trek layers: (layer, tile extension, highest level to load; level n = 2^(n+1) x 2^n tiles).
MOON_LAYERS = {
    "Imagery": ("LRO_WAC_Mosaic_Global_303ppd_v02", "jpg", 3),  # LROC WAC global mosaic, 4096 x 2048 px
    "Elevation": ("LRO_LOLA_ClrShade_Global_128ppd_v04", "png", 3),  # LOLA color shaded relief
}
BUMP_LAYER = ("LRO_LOLA_DEM_Global_128ppd_v04", "png", 2)  # LOLA elevation (grayscale) for bump shading
SELECTED_COLOR, SITE_COLOR = "#e66b27", "#4ba3d3"

_HTML = """
<div class="lunav-globe">
  <div class="globe"></div>
  <div class="overlay top">
    <div class="title">Lunar Landing Site Navigator</div>
    <div class="hint">Drag to rotate · scroll to zoom · click a site to explore it</div>
  </div>
  <div class="overlay layers"></div>
  <div class="overlay info"><div class="info-name"></div><div class="info-text"></div></div>
  <div class="overlay status"></div>
  <div class="overlay credit">Imagery: LRO WAC · Elevation: LOLA · NASA Moon Trek</div>
</div>
"""

_CSS = """
.lunav-globe { position: relative; width: 100%; height: var(--globe-height, 600px); min-height: 420px;
  background: #000005; border-radius: 0.5rem; overflow: hidden; font-family: sans-serif; color: #e8e8e8; }
.globe { position: absolute; inset: 0; }
.overlay { position: absolute; pointer-events: none; text-shadow: 0 1px 3px #000; }
.top { top: 14px; left: 18px; }
.title { font-size: 1.35rem; font-weight: 600; letter-spacing: 0.02em; }
.hint { font-size: 0.85rem; opacity: 0.75; margin-top: 2px; }
.layers { top: 14px; right: 14px; pointer-events: auto; display: flex; gap: 4px; }
.layers button { background: rgba(20, 22, 30, 0.75); color: #e8e8e8; border: 1px solid rgba(255,255,255,0.25);
  border-radius: 999px; padding: 4px 12px; font-size: 0.8rem; cursor: pointer; }
.layers button.active { background: #e66b27; border-color: #e66b27; color: #fff; }
.layers button.fullscreen { margin-left: 8px; }
.status { bottom: 14px; left: 18px; font-size: 0.8rem; opacity: 0.8; }
.credit { bottom: 14px; right: 18px; font-size: 0.7rem; opacity: 0.6; }
/* Page background mode: no frame; the app's panel covers the top-left, so the hint moves to the bottom center. */
.lunav-globe.page { border-radius: 0; min-height: 0; }
.lunav-globe.page .title { display: none; }
.lunav-globe.page .top { top: auto; bottom: 14px; left: 50%; transform: translateX(-50%); text-align: center; }
/* Full screen: the globe covers the monitor; the catalog panel is hidden, so show the selected site here. */
.lunav-globe:fullscreen { height: 100vh; border-radius: 0; }
.info { display: none; bottom: 40px; left: 18px; max-width: min(460px, 60%); background: rgba(10, 12, 18, 0.72);
  border: 1px solid rgba(255,255,255,0.15); border-radius: 0.5rem; padding: 10px 14px; text-shadow: none; }
.lunav-globe:fullscreen .info.has-site { display: block; }
.info-name { font-weight: 600; font-size: 1.05rem; }
.info-text { font-size: 0.85rem; opacity: 0.85; margin-top: 4px; line-height: 1.35; }
"""

_JS = """
const GLOBE_GL_URL = __GLOBE_GL_URL__;
const TILE_URL = __TILE_URL__;

function loadGlobeGl() {
  if (window.Globe) return Promise.resolve();
  if (!window.__lunavGlobeGl) {
    window.__lunavGlobeGl = new Promise((resolve, reject) => {
      const script = document.createElement("script");
      script.src = GLOBE_GL_URL;
      script.onload = resolve;
      script.onerror = () => { window.__lunavGlobeGl = null; reject(new Error("globe.gl")); };
      document.head.appendChild(script);
    });
  }
  return window.__lunavGlobeGl;
}

// One equirectangular texture per (layer, level), assembled from Moon Trek tiles on a canvas and kept for the
// lifetime of the page. Tiles that fail stay black; the promise rejects only if every tile failed.
const mosaics = window.__lunavMosaics || (window.__lunavMosaics = {});
function mosaic(layer, ext, level) {
  const id = `${layer}/${level}`;
  if (!mosaics[id]) {
    mosaics[id] = new Promise((resolve, reject) => {
      const cols = 2 ** (level + 1), rows = 2 ** level, px = 256;
      const canvas = document.createElement("canvas");
      canvas.width = cols * px; canvas.height = rows * px;
      const ctx = canvas.getContext("2d");
      let pending = cols * rows, failed = 0;
      const done = () => {
        if (--pending > 0) return;
        if (failed === cols * rows) { delete mosaics[id]; reject(new Error("tiles")); }
        else resolve(canvas.toDataURL("image/jpeg", 0.92));
      };
      for (let row = 0; row < rows; row++) for (let col = 0; col < cols; col++) {
        const img = new Image();
        img.crossOrigin = "anonymous";
        img.onload = () => { ctx.drawImage(img, col * px, row * px); done(); };
        img.onerror = () => { failed++; done(); };
        img.src = TILE_URL.replace("{layer}", layer).replace("{level}", level)
          .replace("{row}", row).replace("{col}", col).replace("{ext}", ext);
      }
    });
  }
  return mosaics[id];
}

function setLayer(state, name) {
  state.layer = name;
  state.root.querySelectorAll(".layers button").forEach(b => b.classList.toggle("active", b.dataset.layer === name));
  const [layer, ext, maxLevel] = state.data.layers[name];
  const status = state.root.querySelector(".status");
  status.textContent = "Loading NASA Moon Trek imagery…";
  // Show a quick low-resolution texture first, then the full one.
  const levels = [...new Set([Math.min(2, maxLevel), maxLevel])];
  let shown = -1;
  levels.forEach(level => mosaic(layer, ext, level).then(url => {
    if (state.layer !== name || level < shown) return;
    shown = level;
    state.globe.globeImageUrl(url);
    if (level === maxLevel) status.textContent = "";
  }).catch(() => {
    if (state.layer === name) status.textContent = "Could not load NASA Moon Trek imagery.";
  }));
}

// In page mode the app's panel covers the left of the globe, so shift the projection center to the middle of the
// uncovered area. Panel widths mirror EXPLORER_CSS in app.py (380 px, or min(46vw, 760 px) with a site selected,
// plus a 14 px margin); phones stack the panel instead, so no shift there.
function applyViewOffset(state) {
  const el = state.root.querySelector(".globe"), w = el.clientWidth, h = el.clientHeight, data = state.data;
  let panel = 0;
  if (data.page && window.innerWidth > 760) {
    panel = (data.selected ? Math.min(window.innerWidth * 0.46, 760) : 380) + 14;
  }
  const camera = state.globe.camera();
  if (panel && w && h) camera.setViewOffset(w, h, -panel / 2, 0, w, h);
  else camera.clearViewOffset();
  camera.updateProjectionMatrix();
}

function update(state, data) {
  state.data = data;
  const globe = state.globe;
  applyViewOffset(state);
  globe.pointsData(data.points).labelsData(data.points.filter(p => p.selected));
  globe.controls().autoRotate = !data.selected;
  if (state.viewId !== data.view_id) {
    state.viewId = data.view_id;
    globe.pointOfView(data.view, state.created ? 1500 : 0);
  }
  const info = state.root.querySelector(".info");
  info.classList.toggle("has-site", !!data.info);
  info.querySelector(".info-name").textContent = data.info ? data.info.name : "";
  info.querySelector(".info-text").textContent = data.info ? data.info.text : "";
  state.created = true;
}

function addFullscreenButton(state) {
  // The component lives in a shadow root, so ask the root node (not document) which element is full screen.
  const root = state.root, isFullscreen = () => root.getRootNode().fullscreenElement === root;
  const button = document.createElement("button");
  button.className = "fullscreen";
  const label = () => { button.textContent = isFullscreen() ? "✕ Exit full screen" : "⛶ Full screen"; };
  button.onclick = () => (isFullscreen() ? document.exitFullscreen() : root.requestFullscreen()).catch(() => {});
  state.onFullscreenChange = label;
  document.addEventListener("fullscreenchange", label);
  label();
  root.querySelector(".layers").appendChild(button);
}

function create(state, data) {
  const root = state.root, el = root.querySelector(".globe");
  const globe = new Globe(el, { rendererConfig: { antialias: true, alpha: false } })
    .backgroundColor("#000005")
    .showAtmosphere(false)
    .pointLat("lat").pointLng("lng")
    .pointColor(p => p.selected ? data.colors.selected : data.colors.site)
    .pointAltitude(p => p.selected ? 0.025 : 0.01)
    .pointRadius(p => p.selected ? 0.55 : 0.35)
    .pointLabel("label")
    .onPointClick(p => state.setTriggerValue("clicked", p.key))
    .labelLat("lat").labelLng("lng").labelText("name")
    .labelSize(1.1).labelDotRadius(0.35).labelColor(() => "#ffffff").labelResolution(2)
    .labelLabel("label")
    .onLabelClick(l => state.setTriggerValue("clicked", l.key));
  globe.controls().autoRotateSpeed = 0.35;
  state.globe = globe;

  const [bumpLayer, bumpExt, bumpLevel] = data.bump;
  mosaic(bumpLayer, bumpExt, bumpLevel).then(url => {
    globe.bumpImageUrl(url);
    globe.globeMaterial().bumpScale = 6;
  }).catch(() => {});

  const buttons = root.querySelector(".layers");
  Object.keys(data.layers).forEach(name => {
    const b = document.createElement("button");
    b.textContent = name; b.dataset.layer = name;
    b.onclick = () => setLayer(state, name);
    buttons.appendChild(b);
  });
  setLayer(state, Object.keys(data.layers)[0]);
  if (root.requestFullscreen) addFullscreenButton(state);

  const resize = () => { globe.width(el.clientWidth).height(el.clientHeight); applyViewOffset(state); };
  state.observer = new ResizeObserver(resize);
  state.observer.observe(el);
  resize();
}

export default function (component) {
  const { data, parentElement, setTriggerValue } = component;
  const root = parentElement.querySelector(".lunav-globe");
  root.style.setProperty("--globe-height", data.height);
  root.classList.toggle("page", !!data.page);
  // Streamlit calls this again on every rerun with new data, on the same element: keep one globe.
  const state = root.__lunav || (root.__lunav = { root });
  state.setTriggerValue = setTriggerValue;
  state.data = data;  // create() and setLayer() read it before update() runs
  loadGlobeGl().then(() => {
    if (!state.globe) create(state, data);
    update(state, data);
  }).catch(() => {
    root.querySelector(".status").textContent = "Could not load globe.gl from the CDN.";
  });
  return () => {
    state.observer?.disconnect();
    if (state.onFullscreenChange) document.removeEventListener("fullscreenchange", state.onFullscreenChange);
    state.globe?._destructor?.();
    delete root.__lunav;
  };
}
"""

_component = st.components.v2.component(
    "lunav_moon_globe",
    html=_HTML,
    css=_CSS,
    js=_JS.replace("__GLOBE_GL_URL__", json.dumps(GLOBE_GL_URL)).replace("__TILE_URL__", json.dumps(TREK_TILE_URL)),
)


def _view(site):
    """Camera for a site; polar sites are seen from just off the pole (OrbitControls misbehaves exactly at it)."""
    if site is None:
        return {"lat": -55.0, "lng": 0.0, "altitude": 1.8}  # whole Moon, tilted toward the south pole
    polar = site["lat"] < -75
    return {"lat": max(site["lat"], -85.0), "lng": site["lon"], "altitude": 0.9 if polar else 1.6}


def moon_globe(sites, selected_key, *, key, on_click, height="600px", page=False):
    """Mount the globe. `on_click` runs when a site is clicked; read the key from st.session_state[key]["clicked"].

    `height` is any CSS length, such as "calc(100vh - 60px)". `page=True` styles it as a frameless page background
    (no rounded corners or title; the hint moves to the bottom center).
    """
    points = []
    for site_key, site in sites.items():
        name = site.get("name", site_key)
        points.append({
            "key": site_key, "lat": site["lat"], "lng": site["lon"], "name": name,
            "selected": site_key == selected_key,
            "label": f"<b>{escape(name)}</b><br>{site['lat']:.4f}°, {site['lon']:.4f}° E",  # tooltips render HTML
        })
    selected = sites.get(selected_key) if selected_key else None
    data = {
        "points": points, "selected": selected_key, "view": _view(selected), "view_id": selected_key or "",
        "layers": MOON_LAYERS, "bump": BUMP_LAYER, "height": height, "page": page,
        "colors": {"selected": SELECTED_COLOR, "site": SITE_COLOR},
        # Shown over the globe in full screen, where the catalog panel is hidden (rendered as plain text).
        "info": {"name": selected.get("name", selected_key),
                 "text": f"{selected['lat']:.4f}°, {selected['lon']:.4f}° E · {selected['description']}"}
        if selected else None,
    }
    return _component(key=key, data=data, on_clicked_change=on_click)
