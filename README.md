# Lunav One: Lunar Landing Site Navigator

Lunav One is a Python educational prototype for exploring sunlight and Earth
visibility at lunar locations and dates, with a focus on the south pole. It
supports investigation of selected environmental factors; it does not identify
safe or optimal landing sites or certify mission operations.

The project is being developed for the
[2026 NASA Space Apps Challenge: Lunar Landing Site Navigator](https://www.spaceappschallenge.org/2026/challenges/lunar-landing-site-navigator/).
The current interface combines a documented catalog, a schematic polar map and
terrain-aware Sun/Earth charts in Explorer and Site Planner, plus a Catalog Site
comparison for windows covered by pre-computed data.

## Implementation status

| Capability | State in this branch |
|---|---|
| Catalog Site or Custom Site, date and duration selection | Available in Streamlit |
| Sun/Earth elevation curves | Available with Terrain Horizon through get_conditions; pre-computed or live |
| Schematic polar map and independent HTML export | Available without Horizons |
| Terrain Horizon and Illumination Fraction | Integrated into charts and indicators; Ideal Horizon fallback is identified |
| Countdown metrics | Time to Sunset and Earthset shown at a selected instant |
| Pre-computed catalog data | Eight sites, 2027–2028 hourly ephemerides and Terrain Horizons at 2 m Asset Height; available through get_conditions |
| Streamlit request cache | Caches get_conditions results |
| Explorer and Site Planner modes | Available; Site Planner accepts Asset Height and Elevation Mask |
| Catalog Site comparison | Available for pre-computed date windows at 2 m Asset Height |
| Monthly and Site Neighborhood summaries | Science functions available; not yet displayed in app.py |
| Full scientific validation | Pending |
| Automatic data regeneration | Workflow opens a data PR after relevant changes on main; requires review and merge |

The glossary defines **Catalog Site** as a curated site with pre-computed data.
The eight entries now have pre-computed data. Numerical comparison with the
literature is documented below; complete topographic and scientific validation
is still pending. Automated tests check software
behavior, including synthetic terrain cases, rather than scientific validation
of the real Catalog Sites. See [GLOSSARY.md](GLOSSARY.md) and [design decisions](docs/adr/).

## Getting Started

Requirements: Python 3.11+.

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
source .venv/bin/activate       # macOS / Linux
pip install -r requirements.txt
streamlit run app.py
```

Run the tests:

```bash
python -m pytest -q
```

## Project Structure

```text
app.py                       Streamlit interface
src/horizons_api.py          Live Sun/Earth azimuth and elevation
src/terrain.py               LOLA DEM access, Terrain Horizon, Illumination Fraction
src/metrics.py               Terrain-aware countdowns, durations and monthly summary
src/conditions.py            Conditions entry point and Site Neighborhood summary
src/catalog.py               Pre-computed data loader
src/charts.py                Ephemeris charts
src/site_map.py              Schematic polar map and offline HTML export
src/sites.py                 Sourced coordinate catalog
data/                        Pre-computed ephemerides and terrain horizons for catalog sites
data/catalog/                Eight sites and coordinate manifest, 2027–2028
scripts/precompute.py        Generates data/catalog/ (Gabriel)
.github/workflows/precompute.yml  Regenerates data and opens a review PR (Gabriel)
tests/test_horizons_api.py    Ephemeris parsing tests
tests/test_terrain.py         Synthetic terrain and illumination tests
tests/test_metrics.py         Terrain-aware countdown and duration tests
tests/test_catalog.py         Pre-computed data loading tests
tests/test_conditions.py      Conditions entry-point tests
tests/test_sites.py           Coordinate provenance and compatibility tests
tests/test_site_map.py        Map integration and offline export tests
docs/pitch/                  Science explainer, submission draft and demo script
docs/adr/                    Data design decisions
docs/TEAM_PLAN.md            Ownership and workflow
GLOSSARY.md                  Shared project terminology
```

## Data Sources

- [JPL Horizons System](https://ssd.jpl.nasa.gov/horizons/): Observer ephemerides for specified lunar coordinates.
- [LOLA terrain products](https://pgda.gsfc.nasa.gov/products/78): elevation data for terrain calculations.
- [LROC QuickMap](https://quickmap.lroc.asu.edu/) and [Moon Trek](https://trek.nasa.gov/moon/): cartographic references; imagery is not embedded in the prototype map.
- [Canadian Space Agency: Moon Exploration](https://www.asc-csa.gc.ca/eng/astronomy/moon-exploration/).

## Team

| Member | Role |
|---|---|
| Gabriel | Data & Science |
| Igor | Interface & Deployment |
| Renata | Sites, Context & Pitch |

See [docs/TEAM_PLAN.md](docs/TEAM_PLAN.md) for details.

## Standalone south-pole map (offline)

The catalog and map run independently of Streamlit, Horizons and the other science modules:

```bash
.venv/bin/python -m src.site_map --site 'Haworth' --output /tmp/lunar_south_pole.html
```

Open the resulting HTML file in a browser. Use `--output` to choose an accessible folder if needed. Plotly is embedded, so no network connection
is needed to view it. Hover over markers for names, coordinates and descriptions.

```python
from src.site_map import plot_south_pole_map

fig = plot_south_pole_map(selected_site='Haworth')
# In Streamlit: st.plotly_chart(fig, width='stretch')
```

The existing `plot_south_pole_map(LUNAR_SITES, lat, lon)` call remains supported.
The map shows 90–80° S using a schematic polar equidistant representation:
`r = 90 + latitude`, longitude 0° at the top, east clockwise. It has no imagery
or terrain layer. Sites outside this cap (including Apollo 11) are not plotted;
selecting one displays an explanation.

## Catalog provenance and conventions

Coordinates use degrees, north-positive latitude and east-positive longitude in
[-180, 180]. The initial set has eight Catalog Sites for Explorer context and
Site Planner analysis. Four specific study points are prioritized;
no pre-computation is performed by the catalog module itself.

| Catalog display name | Latitude | East longitude | Coordinate meaning |
|---|---:|---:|---|
| Shackleton Rim S1 | -89.6866 | -162.81 | Gläser et al. Table 2, Shackleton first row |
| Connecting Ridge C1 | -89.4398 | -137.17 | Gläser et al. Table 2, C1 |
| Connecting Ridge C2 | -89.3130 | -114.02 | Gläser et al. Table 2, C2 |
| Shackleton Rim S2 | -89.7815 | -155.30 | Gläser et al. Table 2, Shackleton second row |
| Malapert Massif | -85.9948 | -0.23578 | NASA Table A2-2 region center, R23 / Site23 |
| Faustini Rim A | -87.8897 | 90.0 | NASA Table A2-2 region center, LM7 |
| Haworth | -86.7639 | -22.777 | NASA Table A2-2 region center, Haworth |
| Apollo 11 (Tranquility Base) | 0.67416 | 23.47314 | Historical lunar module location |

[Gläser et al. (2017), Table 2, PDF page 12](https://ntrs.nasa.gov/api/citations/20170007365/downloads/20170007365.pdf)
studied the four priority points at a 2 m Asset Height for 2017–2037. Their source
longitudes (222.83, 245.98, 197.19, 204.70 degrees east) were converted by subtracting
360. S1/S2 are local catalog labels for the two Shackleton rows, not the cluster
identifiers in the article's Table 3. These are not certified landing points and
no permanent illumination is claimed. Reconciliation of the source coordinate
frame and topographic validation against the project's LOLA DEM remain pending.

Existing dictionary keys are retained for compatibility. **The key
`Shackleton Crater (Rim)` now uses S1 instead of the previous Site04 region center
(-89.7668, -171.87).** The current manifest matches S1. The loader rejects
pre-computed entries whose manifest coordinates differ from the catalog.
The legacy key `Malapert Massif (Summit)` remains a region center, not a verified
summit. Regional centers are from NASA's Lunar Surface Data Book ACD-50044 Rev A
(2023), Table A2-2, printed pages 57–58. Each entry records its source, coordinate
meaning and validation status. The map uses diamonds for study points, circles
for regional centers, and squares for actual landing locations within its extent. A symbol key explains these types;
hover information groups coordinates, context, provenance and validation status.

Peak Near Shackleton, Nobile Rim 1, IM-1 Odysseus and IM-2 Athena are deferred to
limit automatic pre-computation costs; no approximate Malapert summit is included.
Historical Artemis III candidate-region associations are separate from
[NASA's 2026 architecture](https://www.nasa.gov/news-release/nasa-adds-mission-to-artemis-lunar-program-updates-architecture/):
Artemis III is an Earth-orbit demonstration planned for 2027, while Artemis IV
targets the first Artemis crewed lunar landing in 2028. No current landing-region
selection is implied by this catalog.

- [NASA coordinate table](https://ntrs.nasa.gov/api/citations/20230007818/downloads/ACD-50044%20Lunar%20Surface%20Data%20Book%20Rev%20A.pdf).
- [GSFC LOLA region products](https://pgda.gsfc.nasa.gov/products/78): MOON_ME / DE421 frame.
- [NASA Apollo coordinates](https://nssdc.gsfc.nasa.gov/planetary/lunar/lunar_sites.html): Apollo 11 lunar module reference location.
- [NASA 2022 candidate-region announcement](https://www.nasa.gov/centers-and-facilities/marshall/the-marshall-star-361/): historical Artemis context, not a statement of current mission selection.

## Pre-computed data workflow

`app.py` uses `src/conditions.py:get_conditions` for both Explorer and Site
Planner. The conditions entry point uses committed
catalog data for covered dates and locations at the supported Asset Height,
and falls back to live calculation where supported. Custom locations outside the
south-pole DEM use the Ideal Horizon when no catalog neighborhood is available.

Changes to coordinates should be grouped into one PR. After relevant source
changes reach `main`, `.github/workflows/precompute.yml` regenerates data and
opens or updates **Regenerate pre-computed catalog data**. That data PR needs
review and merge. A monthly schedule and manual trigger are also configured.
There is no need to run pre-computation for documentation-only changes.

[Preliminary literature comparison](docs/pitch/illumination_comparison.md) records
four study points. With the combined 20 m/80 m terrain, all four mean
illumination estimates differ from the paper by less than two percentage points. This is a
consistency check, not a claim of independent mission validation.

## Scientific explanation and presentation drafts

- [Mission explainer](docs/pitch/mission_explainer.md): accessible scientific background.
- [Submission draft](docs/pitch/submission_draft.md): current work, intended impact and pending details.
- [Three-minute demo script](docs/pitch/demo_script.md): demonstrated features versus planned work.

## Current limitations

The interface now uses Terrain Horizon, Illumination Fraction and terrain-aware
countdowns through `get_conditions`. “Sunlight in window” means equivalent
full-Sun hours (the integral of Illumination Fraction), not hours with any part
of the Sun visible and not generated electrical energy. Earth Visibility is a
geometric criterion; it does not establish a working radio link.

Polar terrain calculations combine 20 m LOLA data within 10 km with 80 m data
farther away. Apollo 11 uses the pre-computed global DEM. Pre-computed Site
Neighborhoods sample a 2 km radius at 100 m spacing and 2 m Asset Height;
nearby coordinates use the nearest supported point. Other heights and dates can
require live requests. Custom Sites outside the south-pole DEM use the Ideal
Horizon if no pre-computed neighborhood is available, with a warning.

Monthly and Site Neighborhood summaries exist as science functions but are not
yet exposed by the current interface. No complete reference-frame, uncertainty,
vehicle-safety or operational assessment has been performed. The literature
comparison is a consistency check using related LOLA-derived inputs, not an
independent validation. This is an educational prototype, not a mission safety
tool. The schematic map itself does not calculate terrain or illumination.

Application and demonstration-video links: pending publication.
