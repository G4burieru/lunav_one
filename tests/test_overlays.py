import json
from pathlib import Path

import numpy as np
from PIL import Image

from scripts.render_overlays import EARTH_RAMP, EXTENTS, MAPS, NO_DATA, OUT, SUN_RAMP, colorize


def test_colorize_follows_the_ramp_and_hides_missing_data():
    fraction = np.ma.masked_array([[0.0, 0.5, 1.0, 0.3]], mask=[[False, False, False, True]])
    for ramp in (SUN_RAMP, EARTH_RAMP):
        rgba = np.asarray(colorize(fraction, ramp).convert("RGBA"))
        assert ["#%02x%02x%02x" % tuple(px[:3]) for px in rgba[0, :3]] == [ramp[0][1], ramp[2][1], ramp[-1][1]]
        assert rgba[0, :, 3].tolist() == [255, 255, 255, 0]


def test_the_polar_map_places_every_layer_disc_at_its_bounds():
    js = (Path(__file__).resolve().parent.parent / "src" / "moon_view" / "polar_map.js").read_text(encoding="utf-8")
    for name in MAPS:
        for extent in EXTENTS:
            meta = json.loads((OUT / f"{name}_{extent}.json").read_text(encoding="utf-8"))
            west, south, east, north = meta["bounds_m"]
            assert (west, south, north) == (-east, -east, east)  # a square centered on the pole
            assert f'["{extent}", {east:.0f}]' in js
            image = Image.open(OUT / f"{name}_{extent}.png")
            width, height = image.size
            # A disc: data at the center, transparent in the corners, beyond the extent's latitude.
            assert image.getpixel((width // 2, height // 2)) != NO_DATA
            assert image.getpixel((0, 0)) == image.getpixel((width - 1, height - 1)) == NO_DATA
