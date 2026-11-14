import numpy as np

from scripts.render_sun_overlay import RAMP, colorize


def test_colorize_follows_the_ramp_and_hides_missing_data():
    fraction = np.ma.masked_array([[0.0, 0.5, 1.0, 0.3]], mask=[[False, False, False, True]])
    rgba = np.asarray(colorize(fraction).convert("RGBA"))
    assert ["#%02x%02x%02x" % tuple(px[:3]) for px in rgba[0, :3]] == [RAMP[0][1], RAMP[2][1], RAMP[-1][1]]
    assert rgba[0, :, 3].tolist() == [255, 255, 255, 0]
