"""Render the NASA PGDA average Sun and Earth visibility maps as the images of the Moon View's Layers.

Usage: python -m scripts.render_overlays [sun] [earth]   (both by default)

The maps (https://pgda.gsfc.nasa.gov/products/69, Mazarico et al. 2011) give, per 60 m pixel from 85°S to the
pole, the share of hourly timesteps over 18.6 years with any part of the Sun, or of Earth, above the terrain, at
ground level. For each map this writes static/overlays/<name>_85s.png (240 m pixels, colored with the ramps of
src/colors.py, transparent where the map has no data) and <name>_85s.json (polar stereographic bounds, source and
ramp) for the polar map (docs/UI_OVERHAUL.md, task A8) and the Layers panel (B7).
"""
import json
import sys
from pathlib import Path

import numpy as np
import rasterio
from PIL import Image
from rasterio.enums import Resampling
from rasterio.windows import Window

from src.colors import EARTH_RAMP, SUN_RAMP, ramp_rgb
from src.terrain import GDAL_ENV, _read_chunk

BASE_URL = "https://pgda.gsfc.nasa.gov/data/MoonIllumination/"
MAPS = {"sun": ("AVGVISIB_85S_060M_201608.TIF", SUN_RAMP), "earth": ("AVGVISIB_85S_060M_201608_EARTH.TIF", EARTH_RAMP)}
OUT = Path(__file__).resolve().parent.parent / "static" / "overlays"
DECIMATION = 4  # 60 m pixels -> 240 m
NO_DATA = 255  # palette index left transparent; indices 0-254 run along the ramp


def colorize(fraction, ramp):
    """Paletted image of a masked array of fractions (0-1), transparent where masked. Building the palette from the
    ramp keeps every step; generic quantizers collapse a single hue to a few colors."""
    level = np.rint(np.clip(np.ma.filled(fraction, 0.0), 0, 1) * (NO_DATA - 1))
    image = Image.fromarray(np.where(np.ma.getmaskarray(fraction), NO_DATA, level).astype(np.uint8), "P")
    image.putpalette([*ramp_rgb(np.linspace(0, 1, NO_DATA), ramp).ravel().tolist(), 0, 0, 0])
    image.info["transparency"] = NO_DATA
    return image


def render(name):
    file, ramp = MAPS[name]
    with rasterio.Env(**GDAL_ENV), rasterio.open(BASE_URL + file) as src:
        shape = (src.height // DECIMATION, src.width // DECIMATION)
        fraction = _read_chunk(src, Window(0, 0, src.width, src.height), shape,
                               resampling=Resampling.average) * src.scales[0]
        bounds, crs = src.bounds, src.crs.to_proj4()
    OUT.mkdir(parents=True, exist_ok=True)
    image = OUT / f"{name}_85s.png"
    colorize(fraction, ramp).save(image, optimize=True, transparency=NO_DATA)
    meta = {
        "image": f"app/static/overlays/{image.name}",
        "crs": crs,
        "bounds_m": [bounds.left, bounds.bottom, bounds.right, bounds.top],  # west, south, east, north
        "pixel_m": round((bounds.right - bounds.left) / shape[1], 1),
        "source": "https://pgda.gsfc.nasa.gov/products/69",
        "ramp": ramp,
    }
    image.with_suffix(".json").write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {image} ({shape[1]} x {shape[0]} px, {image.stat().st_size / 1e3:.0f} kB); "
          f"data covers {100 * fraction.count() / fraction.size:.0f}%")


if __name__ == "__main__":
    for name in sys.argv[1:] or MAPS:
        render(name)
