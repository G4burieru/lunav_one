"""3D Moon globe rendered with globe.gl (Three.js / WebGL) inside st.iframe. Owner: Igor.

The GPU maps the full-resolution texture onto the sphere, which keeps the imagery sharp. Textures are embedded
as data URIs, which avoids cross-origin restrictions on WebGL textures. Clicks stay inside the globe (an
embedded page cannot send values back to Streamlit); the site is still chosen with the app's selector.
"""
import base64
import io
import json
from concurrent.futures import ThreadPoolExecutor
from html import escape

import numpy as np
import requests
from PIL import Image

GLOBE_GL_URL = "https://cdn.jsdelivr.net/npm/globe.gl@2.46.2/dist/globe.gl.min.js"
SELECTED_COLOR, SITE_COLOR = "#e66b27", "#4ba3d3"
BUMP_SCALE = 6  # strength of the LOLA bump map shading

# Textures are streamed like the DEMs (docs/adr/0002) instead of being committed. All sources are
# equirectangular: longitude -180..180 left to right, latitude +90..-90 top to bottom.
# Surface color: NASA Moon Trek WMTS mosaics (https://trek.nasa.gov/moon/).
TREK_TILE_URL = "https://trek.nasa.gov/tiles/Moon/EQ/{layer}/1.0.0/default/default028mm/{level}/{row}/{col}.{ext}"
MOON_LAYERS = {
    "Imagery": ("LRO_WAC_Mosaic_Global_303ppd_v02", "jpg"),  # LROC WAC global mosaic
    "Elevation": ("LRO_LOLA_ClrShade_Global_128ppd_v04", "png"),  # LOLA color shaded relief
}
TREK_LEVEL, TREK_TILE_PX = 3, 256  # level 3 = 16 x 8 tiles = 4096 x 2048 px, ~0.09° per pixel
# Bump map shading: LOLA 8-bit elevation from the NASA SVS CGI Moon Kit (https://svs.gsfc.nasa.gov/4720).
LOLA_ELEVATION_URL = "https://svs.gsfc.nasa.gov/vis/a000000/a004700/a004720/ldem_3_8bit.jpg"


def _get_image(url):
    response = requests.get(url, timeout=20)
    response.raise_for_status()
    return Image.open(io.BytesIO(response.content))


def load_moon_layer(name, level=TREK_LEVEL):
    """Moon Trek mosaic for a MOON_LAYERS entry as an RGB uint8 array (256·2^level x 512·2^level x 3).

    Level 2 is 2048 x 1024 px (32 tiles), level 3 is 4096 x 2048 px (128 tiles). Raises on failure.
    """
    layer, ext = MOON_LAYERS[name]
    cols, rows = 2 ** (level + 1), 2 ** level
    keys = [(r, c) for r in range(rows) for c in range(cols)]
    urls = [TREK_TILE_URL.format(layer=layer, level=level, row=r, col=c, ext=ext) for r, c in keys]
    with ThreadPoolExecutor(8) as pool:
        tiles = list(pool.map(_get_image, urls))
    mosaic = Image.new("RGB", (cols * TREK_TILE_PX, rows * TREK_TILE_PX))
    for (r, c), tile in zip(keys, tiles):
        mosaic.paste(tile.convert("RGB"), (c * TREK_TILE_PX, r * TREK_TILE_PX))
    return np.asarray(mosaic)


def load_moon_elevation():
    """LOLA elevation as floats in 0..1 (512 x 1024). Raises on failure."""
    return np.asarray(_get_image(LOLA_ELEVATION_URL).convert("L"), dtype=float) / 255.0

_TEMPLATE = """<!doctype html>
<html><head><meta charset="utf-8">
<style>
  html, body { margin: 0; background: #000; overflow: hidden; }
  #globe { width: 100%; height: __HEIGHT__px; }
  #msg { color: #bbb; font: 14px sans-serif; padding: 1em; }
</style>
<script src="__GLOBE_GL_URL__"></script>
</head><body><div id="globe"></div>
<script>
const points = __POINTS__, view = __VIEW__, texture = __TEXTURE__, bump = __BUMP__;
const el = document.getElementById("globe");
if (typeof Globe === "undefined") {
  el.innerHTML = '<div id="msg">Could not load globe.gl from the CDN.</div>';
} else {
  const globe = new Globe(el)
    .width(el.clientWidth).height(__HEIGHT__)
    .backgroundColor("#000005")
    .showAtmosphere(false)
    .globeImageUrl(texture)
    .bumpImageUrl(bump)
    .pointsData(points).pointLat("lat").pointLng("lng")
    .pointColor(p => p.selected ? "__SELECTED__" : "__SITE__")
    .pointAltitude(p => p.selected ? 0.02 : 0.008)
    .pointRadius(p => p.selected ? 0.5 : 0.3)
    .pointLabel("label")
    .labelsData(points.filter(p => p.selected)).labelLat("lat").labelLng("lng").labelText("name")
    .labelSize(1.1).labelDotRadius(0.35).labelColor(() => "#ffffff").labelResolution(2)
    .labelLabel("label");
  globe.globeMaterial().bumpScale = __BUMP_SCALE__;
  globe.pointOfView(view, 0);
  window.addEventListener("resize", () => globe.width(el.clientWidth));
}
</script></body></html>
"""


def image_data_uri(array, quality=85):
    """JPEG data URI for an image array: uint8 RGB/gray, or floats in 0..1."""
    array = np.asarray(array)
    if array.dtype != np.uint8:
        array = (np.clip(array, 0, 1) * 255).astype(np.uint8)
    buffer = io.BytesIO()
    Image.fromarray(array).save(buffer, "JPEG", quality=quality)
    return "data:image/jpeg;base64," + base64.b64encode(buffer.getvalue()).decode()


def _js(value):
    return json.dumps(value).replace("</", "<\\/")  # never close the <script> tag from data


def globe_html(sites, selected_key, texture_uri, bump_uri=None, height=600):
    """HTML page with a rotatable globe; the camera faces the selected site. URIs may be None (plain gray)."""
    points = []
    for key, site in sites.items():
        name = site.get("name", key)
        points.append({
            "lat": site["lat"], "lng": site["lon"], "name": name, "selected": key == selected_key,
            "label": f"<b>{escape(name)}</b><br>{site['lat']:.4f}°, {site['lon']:.4f}° E",
        })
    site = sites[selected_key]
    polar = site["lat"] < -75
    # Polar sites: look from just off the pole (OrbitControls misbehaves exactly at it), closer in.
    view = {"lat": max(site["lat"], -85.0), "lng": site["lon"], "altitude": 0.9 if polar else 1.6}
    replacements = {
        "__GLOBE_GL_URL__": GLOBE_GL_URL, "__HEIGHT__": str(height), "__POINTS__": _js(points),
        "__VIEW__": _js(view), "__TEXTURE__": _js(texture_uri), "__BUMP__": _js(bump_uri),
        "__SELECTED__": SELECTED_COLOR, "__SITE__": SITE_COLOR, "__BUMP_SCALE__": str(BUMP_SCALE),
    }
    html = _TEMPLATE
    for placeholder, value in replacements.items():
        html = html.replace(placeholder, value)
    return html
