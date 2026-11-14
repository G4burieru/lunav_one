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
select a date and analysis duration, and request hourly Sun/Earth elevations from
NASA JPL Horizons. Plotly charts show those elevations relative to 0°. A
schematic south-pole map distinguishes study points and regional centers and
can be exported as a self-contained HTML file without querying Horizons.

Eight Catalog Sites retain coordinate provenance and validation status. Four
priority points come from Gläser et al.'s illumination study at a 2 m Asset
Height. Their published results are context, not computed outputs or a safety
ranking from our tool. The coordinates await checks against the project DEM.

Separate science modules implement Terrain Horizon calculations, Illumination
Fraction and terrain-aware countdowns with an Ideal Horizon fallback. These calculations are covered
by automated tests but are not yet integrated into the main interface's charts
and indicators. Synthetic tests check computational behavior; they do not
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

Planned Explorer and Site Planner modes will organize learning and Surface Asset
analysis. Pre-computed catalog data and an automatic regeneration workflow are
now present. Next steps include DEM/frame validation, investigation of the
Shackleton S2 discrepancy, terrain-aware chart integration and scenario comparisons. These are
planned capabilities, not completed features.

The current prototype does not certify landing safety, locate ice deposits,
calculate electrical power or validate radio links. It does not identify an
optimal landing location. Historical Artemis III region references do not imply
selection for any current mission.

## Preliminary numerical comparison

[Comparison with published results](illumination_comparison.md) checks mean
Illumination Fraction for four study points using committed 2027–2028 data.
C1 and Shackleton S1 are close to the literature values; S2 differs substantially.
This supports further investigation, not a completed independent validation.
The literature and prototype share LOLA-derived terrain and use different DEM
resolutions and time windows. Do not omit S2 when presenting the comparison.

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
