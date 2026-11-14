"""User-facing explanatory text for the panels. Owner: Renata.

First versions, to be rewritten in task D1 of docs/UI_OVERHAUL.md. Use the terms in GLOSSARY.md.
"""

INTRO = ("Near the lunar south pole the Sun stays close to the horizon, so nearby terrain decides when a place gets "
         "sunlight and a view of Earth. Pick a site to see how often it has both.")

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
