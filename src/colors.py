"""Sequential color ramps for sunlight and Earth visibility maps. Owner: Gabriel.

One hue each, lightness rising with the value, so a darker cell always means less. Both pass the dataviz ordinal
checks on the app's dark surface #0e1117: monotone lightness, visible steps, the 0% end above 2:1 contrast.
Used by the Site Neighborhood cells and their legends.
"""
import numpy as np

SUN_RAMP = [(0.0, "#6b4400"), (0.25, "#8f5c00"), (0.5, "#c27c00"), (0.75, "#f5a623"), (1.0, "#ffd98a")]  # amber
EARTH_RAMP = [(0.0, "#184f95"), (0.25, "#256abf"), (0.5, "#3987e5"), (0.75, "#6da7ec"), (1.0, "#b7d3f6")]  # blue


def ramp_rgb(values, ramp):
    """RGB (0-255, uint8) along `ramp` for an array of fractions 0-1; values outside are clipped."""
    stops = [stop for stop, _ in ramp]
    colors = np.array([[int(hex_[i:i + 2], 16) for i in (1, 3, 5)] for _, hex_ in ramp], dtype=float)
    values = np.clip(np.asarray(values, dtype=float), 0, 1)
    return np.stack([np.interp(values, stops, colors[:, c]) for c in range(3)], axis=-1).round().astype(np.uint8)


def ramp_hex(values, ramp):
    """Hex colors along `ramp` for fractions 0-1."""
    return ["#%02x%02x%02x" % tuple(rgb) for rgb in ramp_rgb(values, ramp).reshape(-1, 3)]


def css_gradient(ramp):
    """CSS linear-gradient for a legend bar, from 0% on the left to 100% on the right."""
    return "linear-gradient(to right, " + ", ".join(f"{hex_} {100 * stop:.0f}%" for stop, hex_ in ramp) + ")"
