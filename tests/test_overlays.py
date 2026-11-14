import numpy as np

from scripts.render_overlays import EARTH_RAMP, SUN_RAMP, colorize


def test_colorize_follows_the_ramp_and_hides_missing_data():
    fraction = np.ma.masked_array([[0.0, 0.5, 1.0, 0.3]], mask=[[False, False, False, True]])
    for ramp in (SUN_RAMP, EARTH_RAMP):
        rgba = np.asarray(colorize(fraction, ramp).convert("RGBA"))
        assert ["#%02x%02x%02x" % tuple(px[:3]) for px in rgba[0, :3]] == [ramp[0][1], ramp[2][1], ramp[-1][1]]
        assert rgba[0, :, 3].tolist() == [255, 255, 255, 0]
