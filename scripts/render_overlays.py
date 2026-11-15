"""Render the NASA PGDA average Sun and Earth visibility maps as the images of the Moon View's Layers.

Usage: python -m scripts.render_overlays [sun] [earth]   (both by default)

The maps (https://pgda.gsfc.nasa.gov/products/69, Mazarico et al. 2011) give the share of hourly timesteps over
18.6 years with any part of the Sun, or of Earth, above the terrain, at ground level. PGDA publishes each one three
times: to 65°S at 240 m per pixel, to 75°S at 120 m and to 85°S at 60 m. For each map and extent this writes
static/overlays/<name>_<extent>.png (coarser: 1920, 960 and 240 m per pixel, colored with the ramps of src/colors.py)
and a .json with its polar stereographic bounds, source and ramp. Each map is a square around the pole; the image
keeps the disc inside it, which ends at the extent's latitude, and is transparent elsewhere. The polar map stacks
the three discs, finest on top (docs/UI_OVERHAUL.md, task A8), so the layer reaches 65°S and is sharpest near the
pole, where the Catalog Sites are. A layer weighs about 2 MB.
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
MAPS = {"sun": ("", SUN_RAMP), "earth": ("_EARTH", EARTH_RAMP)}  # name: (file suffix, ramp)
OUT = Path(__file__).resolve().parent.parent / "static" / "overlays"
# extent: (PGDA file part, decimation), coarse to fine as the polar map stacks them
EXTENTS = {"65s": ("65S_240M", 8), "75s": ("75S_120M", 8), "85s": ("85S_060M", 4)}
NO_DATA = 255  # palette index left transparent; indices 0-254 run along the ramp


def colorize(fraction, ramp):
    """Paletted image of a masked array of fractions (0-1), transparent where masked. Building the palette from the
    ramp keeps every step; generic quantizers collapse a single hue to a few colors."""
    level = np.rint(np.clip(np.ma.filled(fraction, 0.0), 0, 1) * (NO_DATA - 1))
    image = Image.fromarray(np.where(np.ma.getmaskarray(fraction), NO_DATA, level).astype(np.uint8), "P")
    image.putpalette([*ramp_rgb(np.linspace(0, 1, NO_DATA), ramp).ravel().tolist(), 0, 0, 0])
    image.info["transparency"] = NO_DATA
    return image


def render(name, extent):
    (suffix, ramp), (part, decimation) = MAPS[name], EXTENTS[extent]
    with rasterio.Env(**GDAL_ENV), rasterio.open(f"{BASE_URL}AVGVISIB_{part}_201608{suffix}.TIF") as src:
        shape = (src.height // decimation, src.width // decimation)
        fraction = _read_chunk(src, Window(0, 0, src.width, src.height), shape,
                               resampling=Resampling.average) * src.scales[0]
        bounds, crs = src.bounds, src.crs.to_proj4()
    rows, cols = np.indices(fraction.shape) + 0.5  # pixel centers
    fraction[np.hypot(rows - shape[0] / 2, cols - shape[1] / 2) > min(shape) / 2] = np.ma.masked
    OUT.mkdir(parents=True, exist_ok=True)
    image = OUT / f"{name}_{extent}.png"
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
        for extent in EXTENTS:
            render(name, extent)
