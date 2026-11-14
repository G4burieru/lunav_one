"""User-facing explanatory text for the panels. Owner: Renata.

First versions, to be rewritten in task D1 of docs/UI_OVERHAUL.md. Use the terms in GLOSSARY.md.
"""

INTRO = ("Near the lunar south pole the Sun stays close to the horizon, so nearby terrain decides when a place gets "
         "sunlight and a view of Earth. Pick a site to see how often it has both.")

SUNLIGHT_HELP = ("Share of the time the Sun shines on a panel 2 m above the ground in 2027–2028, counting a partly "
                 "hidden Sun in proportion. The best ridges near the pole get about 80–90%; the lunar equator, 50%.")
EARTH_HELP = ("Share of the hours in 2027–2028 when Earth's center is above the terrain, so an antenna could point "
              "straight at it. Near-side equatorial sites see Earth all the time; polar sites about half the time.")
LONGEST_NIGHT_HELP = ("Longest stretch in 2027–2028 with the Sun completely hidden: how long batteries would have to "
                      "last. Nights at the lunar equator last about 15 days.")
LONGEST_EARTH_ABSENCE_HELP = ("Longest stretch in 2027–2028 without Earth in view: how long direct-to-Earth "
                              "communication would be impossible.")
ASSET_HEIGHT_HELP = ("Height of the solar panel or antenna above the ground. 2 m is pre-computed and instant; other "
                     "heights compute the terrain horizon live, in about 30 s.")
ELEVATION_MASK_HELP = ("Minimum angle Earth's center must clear above the terrain horizon to count as visible, for "
                       "example to keep an antenna's beam clear of the ground.")
SUN_LAYER = ("Average sunlight at ground level over 18.6 years (NASA PGDA). Site figures are 2 m above the ground "
             "and differ: at Connecting Ridge C1 this map gives 44% and the Site Card 88%.")
EARTH_LAYER = ("Share of the time any part of Earth is above the terrain, at ground level over 18.6 years (NASA PGDA). "
               "It matches our Site Card values within 1 to 5 points.")
CUSTOM_SITE = "A location you picked. Its conditions are computed live from NASA JPL Horizons and LOLA terrain."
NO_TERRAIN = "No terrain data here (outside 80°S): these figures use the ideal horizon of a smooth Moon."

ABOUT = """
Lunar Landing Site Navigator shows how much sunlight (for power) and Earth visibility (for direct-to-Earth
communication) a Surface Asset would have near the lunar south pole, and when.

- **Sunlight** is the share of the Sun's disk above the terrain horizon, averaged over time.
- **Earth visibility** counts the hours when Earth's center is above the terrain horizon.
- Catalog Sites are pre-computed hourly for 2027–2028 at 2 m above the ground. Other points, heights and dates
  are computed live.

**Data.** Sun and Earth positions from NASA JPL Horizons; terrain from NASA LOLA elevation models (NASA Goddard
PGDA); imagery from NASA Moon Trek.

**Limits.** These are modeled conditions, not measured power or verified radio links. No site here is a certified
landing site.
"""
