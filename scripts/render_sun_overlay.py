"""Render the NASA PGDA average Sun visibility map as the image of the Moon View's Sunlight overlay.

Usage: python -m scripts.render_sun_overlay

The map (https://pgda.gsfc.nasa.gov/products/69, Mazarico et al. 2011) gives, per 60 m pixel from 85°S to the
pole, the share of hourly timesteps over 18.6 years with any part of the Sun above the terrain, at ground level.
Writes static/overlays/sun_85s.png (240 m pixels, transparent where the map has no data) and sun_85s.json (polar
stereographic bounds, source and color ramp) for the polar map (docs/UI_OVERHAUL.md, task A8) and the legend (B7).
"""
import json
from pathlib import Path

import numpy as np
import rasterio
from PIL import Image
from rasterio.enums import Resampling
from rasterio.windows import Window

from src.terrain import GDAL_ENV, _read_chunk

URL = "https://pgda.gsfc.nasa.gov/data/MoonIllumination/AVGVISIB_85S_060M_201608.TIF"
OUT = Path(__file__).resolve().parent.parent / "static" / "overlays"
DECIMATION = 4  # 60 m pixels -> 240 m
# Sequential: one amber hue, lightness rising with sunlight. Passes the dataviz ordinal checks on the app's dark
# surface (#0e1117): monotone lightness, visible steps, 0% end at 2.2:1 contrast.
RAMP = [(0.0, "#6b4400"), (0.25, "#8f5c00"), (0.5, "#c27c00"), (0.75, "#f5a623"), (1.0, "#ffd98a")]


NO_DATA = 255  # palette index left transparent; indices 0-254 run along the ramp


def ramp(values):
    """RGB (0-255) along RAMP for an array of fractions 0-1."""
    stops = [stop for stop, _ in RAMP]
    colors = np.array([[int(hex_[i:i + 2], 16) for i in (1, 3, 5)] for _, hex_ in RAMP], dtype=float)
    return np.stack([np.interp(values, stops, colors[:, c]) for c in range(3)], axis=-1).round().astype(np.uint8)


def colorize(fraction):
    """Paletted image of a masked array of sunlight fractions (0-1), transparent where masked. Building the
    palette from the ramp keeps every step; generic quantizers collapse a single hue to a few colors."""
    level = np.rint(np.clip(np.ma.filled(fraction, 0.0), 0, 1) * (NO_DATA - 1))
    image = Image.fromarray(np.where(np.ma.getmaskarray(fraction), NO_DATA, level).astype(np.uint8), "P")
    image.putpalette([*ramp(np.linspace(0, 1, NO_DATA)).ravel().tolist(), 0, 0, 0])
    image.info["transparency"] = NO_DATA
    return image


def main():
    with rasterio.Env(**GDAL_ENV), rasterio.open(URL) as src:
        shape = (src.height // DECIMATION, src.width // DECIMATION)
        fraction = _read_chunk(src, Window(0, 0, src.width, src.height), shape,
                               resampling=Resampling.average) * src.scales[0]
        bounds, crs = src.bounds, src.crs.to_proj4()
    OUT.mkdir(parents=True, exist_ok=True)
    colorize(fraction).save(OUT / "sun_85s.png", optimize=True, transparency=NO_DATA)
    meta = {
        "image": "app/static/overlays/sun_85s.png",
        "crs": crs,
        "bounds_m": [bounds.left, bounds.bottom, bounds.right, bounds.top],  # west, south, east, north
        "pixel_m": round((bounds.right - bounds.left) / shape[1], 1),
        "source": "https://pgda.gsfc.nasa.gov/products/69",
        "ramp": RAMP,
    }
    (OUT / "sun_85s.json").write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {OUT / 'sun_85s.png'} ({shape[1]} x {shape[0]} px, "
          f"{(OUT / 'sun_85s.png').stat().st_size / 1e3:.0f} kB); data covers {100 * fraction.count() / fraction.size:.0f}%")


if __name__ == "__main__":
    main()
