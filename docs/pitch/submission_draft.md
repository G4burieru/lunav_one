# Lunav One — submission draft

Working draft for NASA Space Apps Challenge 2026, Lunar Landing Site Navigator.
Review against the submission form and the build actually demonstrated before
publishing. No deployment, award, external validation or partnership is claimed.

## Project summary

Lunav One is a Python prototype for exploring how location and time affect
sunlight and Earth visibility near the lunar south pole. It brings documented
coordinates, a schematic polar map and live ephemeris charts into one interface.
Its purpose is to make scientific assumptions and limitations understandable to
students, educators and people interested in lunar exploration.

## The problem

Low-angle sunlight and rugged terrain complicate polar operations. A location
with the Sun above an Ideal Horizon may still be shaded by nearby terrain.
Positions described as a crater rim or mountain region can represent broad study
areas rather than precise points. Users need to know what coordinates mean and
which environmental effects a visualization includes. [NASA's environment overview](https://www.nasa.gov/reference/moonbase-environment/)
provides the scientific background for this problem.

## Our solution and current implementation

The Streamlit interface lets users choose a Catalog Site or enter coordinates,
select a date and analysis duration, and view hourly Sun/Earth conditions. NASA JPL Horizons supplies ephemerides;
Plotly charts compare elevations against the Terrain Horizon. Covered Catalog
Site scenarios use pre-computed data; other supported cases are calculated live. A
schematic south-pole map distinguishes study points and regional centers and
can be exported as a self-contained HTML file without querying Horizons.

Eight Catalog Sites retain coordinate provenance and validation status. Four
priority points come from Gläser et al.'s illumination study at a 2 m Asset
Height. Their published results are context, not computed outputs or a safety
ranking from our tool. Project terrain has been calculated at these coordinates; the literature
comparison is preliminary and does not complete topographic validation.

The interface integrates Terrain Horizon, Illumination Fraction and terrain-aware
countdowns, with an identified Ideal Horizon fallback where terrain is unavailable.
The polar terrain model uses 20 m sampling within 10 km, 80 m from 10–50 km,
and a 320 m overview from 50–150 km, with the corrected DEM read window.
These calculations are covered by automated tests. Synthetic tests check computational behavior; they do not
constitute validation of real Catalog Site terrain.

## Technologies and source use

- Python, Streamlit and Plotly provide the interface and visualizations.
- Pandas and Requests support time-series handling and live Horizons queries.
- NumPy and Rasterio support terrain computations and DEM reading.
- Pytest checks parsing, catalog coordinates, map compatibility and science functions.
- [JPL Horizons](https://ssd.jpl.nasa.gov/horizons/manual.html) supplies ephemerides.
- [NASA's Lunar Surface Data Book, Table A2-2](https://ntrs.nasa.gov/api/citations/20230007818/downloads/ACD-50044%20Lunar%20Surface%20Data%20Book%20Rev%20A.pdf)
  supplies regional centers; [Gläser et al. (2017), Table 2](https://ntrs.nasa.gov/api/citations/20170007365/downloads/20170007365.pdf)
  supplies the specific priority study points.
- [NASA GSFC LOLA products](https://pgda.gsfc.nasa.gov/products/78) support terrain work.
  [LROC QuickMap](https://quickmap.lroc.im-ldi.com/) and
  [Moon Trek](https://trek.nasa.gov/moon/) are cartographic references, not embedded imagery.
- [CSA's lunar exploration background](https://www.asc-csa.gc.ca/eng/astronomy/moon-exploration/)
  provides educational context; CSA is not a project partner.

## Intended impact and next steps

Our intended impact is educational: help users distinguish a coordinate from a
validated landing point, solar geometry from usable power, and Earth Visibility
from a working communications link. This benefit has not yet been measured in
user studies or operational use.

Explorer now provides Catalog Site context, time-series analysis and a comparison
table for covered dates. Site Planner accepts Custom Sites, Asset Height and
Elevation Mask. Pre-computed data and automatic regeneration are present.
Monthly summaries and a selectable Site Neighborhood heatmap are available in
the interface. Lunar reference-frame compatibility has been checked against
Horizons and LOLA documentation and response headers. Complete scientific,
uncertainty and operational review remains required.

The current prototype does not certify landing safety, locate ice deposits,
calculate electrical power or validate radio links. It does not identify an
optimal landing location. Historical Artemis III region references do not imply
selection for any current mission.

## Preliminary numerical comparison

[Comparison with published results](illumination_comparison.md) checks mean
Illumination Fraction for four study points using committed 2027–2028 data.
With finer local terrain, all four average illumination values differ from the
paper by less than 1.2 percentage points. S2 improved from a -12.33 to a -1.11
percentage-point difference, consistent with terrain resolution contributing to
the earlier discrepancy. This is a consistency check, not independent validation:
the time windows differ and both calculations use LOLA-derived terrain. The
project combines 20 m, 80 m and 320 m terrain at different distances rather than exactly
reproducing the study's 20 m method.

## Earth Visibility evidence

The documented Malapert regional center gives 48.90% Earth Visibility. A modeled
cell 1600 m west and 100 m north gives 100% of hourly samples in 2027–2028 at
2 m Asset Height and 0° Elevation Mask. It is an example of terrain sensitivity,
not a confirmed summit or a guarantee of a working communications link.

Earth visibility is checked numerically against NASA Goddard's PGDA average
Earth visibility map (Mazarico et al., 2011), the reference product named in
NASA's Lunar Surface Data Book. Using the map's definition (any part of Earth's
disk), six of seven catalog points are within 1.3 percentage points of the map,
and C1 and S2 within 4.6, always slightly higher as expected for a 2 m observer
versus the map's surface level. The
[comparison document](illumination_comparison.md) gives the table, the remaining
differences and the reproduction command. Both the exact offset and the analysis
window must accompany the Malapert percentage.

## Publication details to complete

- Application URL: pending deployment and verification.
- Demonstration video URL: pending recording.
- Repository: https://github.com/G4burieru/lunav_one
- Team: Gabriel (science), Igor (interface), Renata (sites, context and pitch).
- Recheck the current build, source credits and submission length before upload.

Challenge reference supplied by the team:
https://www.spaceappschallenge.org/2026/challenges/lunar-landing-site-navigator/
The challenge page could not be retrieved during this documentation review;
wording and submission requirements still need confirmation on the official form.
