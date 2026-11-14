"""Public-facing panel copy. Owner: Renata (UI_OVERHAUL.md, Lane D1).

Keep constant names stable: panels import them directly. Catalog help describes
2027–2028 at 2 m Asset Height; About also explains the Site Planner's chosen window.
Layer descriptions are ready for integration, not evidence of a working Layers panel.
"""

INTRO = (
    "Near the lunar south pole, low-angle sunlight and uneven terrain change when the Sun and Earth are in view. "
    "Choose a Catalog Site to explore its modeled conditions and the meaning of its coordinates."
)

SUNLIGHT_HELP = (
    "Average Illumination Fraction over 2027–2028 at 2 m Asset Height: how much of the Sun's disk clears the "
    "Terrain Horizon, counting partial views proportionally. 50% means half the full-disk exposure over the "
    "window, not necessarily sunlight for half its hours. It is not generated electrical power."
)
EARTH_HELP = (
    "Percentage of hourly samples in 2027–2028 with Earth's center above the Terrain Horizon at 2 m Asset Height "
    "and a 0° Elevation Mask. This measures geometric Earth Visibility, not a working radio link."
)
LONGEST_NIGHT_HELP = (
    "Longest run of hourly samples in 2027–2028 with the entire Sun below the Terrain Horizon. "
    "It helps describe a no-sunlight interval; battery endurance and survival are not calculated. "
    "A run reaching the window boundary may continue beyond it."
)
LONGEST_EARTH_ABSENCE_HELP = (
    "Longest run of hourly samples in 2027–2028 when Earth's center does not clear the Terrain Horizon. "
    "It describes loss of the modeled direct Earth view, not loss of every possible relay connection. "
    "A run reaching the window boundary may continue beyond it."
)
ASSET_HEIGHT_HELP = (
    "Height of a Surface Asset's panel or antenna above local ground. A higher position can change the "
    "Terrain Horizon. The rover/lander preset is 2 m and uses pre-computed data where covered; the 10 m mast "
    "and other heights may require slower live calculations. These presets do not model a vehicle's performance."
)
ELEVATION_MASK_HELP = (
    "Extra clearance angle required above the Terrain Horizon for Earth's center to count as visible. "
    "0° uses the horizon alone; a larger mask can reduce Earth Visibility. This is a geometric margin, "
    "not an antenna or radio-link calculation."
)
SUN_LAYER = (
    "NASA PGDA Sun visibility: percentage of hourly samples with any part of the Sun visible at ground level, "
    "averaged over 18.6 years. Darker amber means less visibility. Site Card Sunlight instead averages the "
    "visible fraction of the solar disk at 2 m over 2027–2028. Height, period, resolution and metric differ; "
    "the layer and Site Card values are not interchangeable."
)
EARTH_LAYER = (
    "NASA PGDA Earth visibility: percentage of hourly samples with any part of Earth's disk visible at ground "
    "level, averaged over 18.6 years. Site Cards use Earth's center at 2 m over 2027–2028. These different "
    "definitions can give different percentages; neither measures radio-link availability."
)
CUSTOM_SITE = (
    "A location you selected, without a Catalog Site's source context. Conditions are calculated from JPL "
    "Horizons and LOLA terrain where supported; some cases use pre-computed neighborhoods. Selecting a "
    "point does not establish that it is a summit, a rim or a safe landing location."
)
NO_TERRAIN = (
    "Terrain is unavailable for this calculation outside the south-pole coverage. Results use the Ideal "
    "Horizon of a smooth Moon, so local ridges and crater walls are not included."
)

ABOUT = """
Lunav One helps you explore sunlight and Earth Visibility near the lunar south pole.
**Explorer** opens documented Catalog Sites; **Site Planner** evaluates a Surface Asset
at a chosen location, height and Analysis Window. This is an educational prototype.

**Read the Site Card.** Its averages and longest intervals cover **2027–2028 at 2 m
Asset Height**. Rankings compare only the eight Catalog Sites and the selected metric;
they do not rank landing safety. The selected-instant line and 28-day Sun & Earth charts
describe a shorter interval; the Seasons chart groups results by month.

- **Sunlight** is the mean **Illumination Fraction**: the portion of the Sun's disk above
  the **Terrain Horizon**, averaged over time. Partial views count proportionally. It
  is neither electrical energy nor simply the percentage of hours with any sunlight.
- **Earth Visibility** counts hourly samples when Earth's center clears the Terrain
  Horizon. Site Cards use a 0° **Elevation Mask**; Site Planner lets you require more
  clearance. A visible Earth does not guarantee an antenna connection or a working link.
- **Longest Night** is the longest modeled interval with the Sun fully hidden.
  **Longest Earth Absence** is the longest interval without the required Earth view.
  These describe conditions within the analyzed window, not battery autonomy or
  guaranteed outage durations beyond that window. Relay paths are not modeled.
- **Countdowns** run from the selected instant to **Sunset** (the solar disk becomes
  fully hidden) or **Earthset** (the required Earth view ends). No set found in the
  window does not mean permanent visibility. Hourly sampling and interpolation limit
  the timing precision.
- **Asset Height** is height above local ground, not elevation above the Moon's
  reference sphere. The 2 m preset supports pre-computed neighborhoods; 10 m and other
  heights can need live terrain calculations. **Elevation Mask** adds angular clearance
  for Earth's center; it does not evaluate antenna performance.

**NASA inputs and project calculations.** JPL Horizons provides Sun/Earth ephemerides;
LOLA elevation models distributed by NASA Goddard PGDA provide terrain. Lunav One
calculates Terrain Horizons, Illumination Fractions, durations and rankings from those
inputs. The Moon View displays LROC photographs and LOLA shaded relief through NASA
Moon Trek. Imagery is visual context, not an instantaneous shadow or safety measurement.
NASA's long-term, ground-level visibility layers use different definitions and periods
from the Site Card; their values must not be read as the same calculation.

**Coverage and limits.** Covered Catalog Site scenarios use pre-computed hourly data;
other supported cases compute live and can take longer or fail if services are unavailable.
Pre-computed Site Neighborhoods use 100 m spacing within 2 km at 2 m height, with nearby
positions snapped to a supported point. An Ideal Horizon fallback is identified where
terrain is unavailable. Literature comparisons are consistency checks, not independent
validation: source data are shared and analysis periods differ. We do not certify landing
safety, permanent illumination, usable power, thermal survival or operational communications.

**Sources and credits.**
[JPL Horizons](https://ssd.jpl.nasa.gov/horizons/manual.html) ·
[NASA PGDA / LOLA](https://pgda.gsfc.nasa.gov/products/69) ·
[Moon Trek](https://trek.nasa.gov/moon/) ·
[LROC](https://lroc.im-ldi.com/) ·
[Gläser et al. (2017)](https://ntrs.nasa.gov/citations/20170007365).
Coordinate references are recorded in each Catalog Site's scientific context.
Lunav One's team: Gabriel (science), Igor (interface), Renata (sites, text and presentation).
"""
