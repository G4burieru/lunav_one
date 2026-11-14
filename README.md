# Lunav One: Lunar Landing Site Navigator

Lunav One is a Python educational prototype for exploring sunlight and Earth
visibility at lunar locations and dates, with a focus on the south pole. It
supports investigation of selected environmental factors; it does not identify
safe or optimal landing sites or certify mission operations.

The project is being developed for the
[2026 NASA Space Apps Challenge: Lunar Landing Site Navigator](https://www.spaceappschallenge.org/2026/challenges/lunar-landing-site-navigator/).
The current interface combines a documented catalog, a schematic polar map and
live Sun/Earth elevation charts. Site comparison remains planned.

## Implementation status

| Capability | State in this branch |
|---|---|
| Catalog Site or Custom Site, date and duration selection | Available in Streamlit |
| Sun/Earth elevation curves | Available through live Horizons requests; relative to the Ideal Horizon |
| Schematic polar map and independent HTML export | Available without Horizons |
| Terrain Horizon and Illumination Fraction | Implemented in science functions; not integrated into interface results |
| Countdown metrics | Implemented as Ideal Horizon crossings; not integrated into the interface |
| Streamlit request cache | In-memory cache present; no committed pre-computed catalog data in this checkout |
| Explorer and Site Planner modes | Planned; not separate working interface modes yet |
| Scenario comparison, validated catalog pre-computation | Pending |

The glossary defines **Catalog Site** as a curated site with pre-computed data.
The eight entries are the catalog being prepared for that workflow; their DEM
validation and pre-computed data are pending. Automated tests check software
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
src/metrics.py               Ideal Horizon countdown functions
src/charts.py                Ephemeris charts
src/site_map.py              Schematic polar map and offline HTML export
src/sites.py                 Sourced coordinate catalog
data/                        Reserved for data; only .gitkeep in this checkout
tests/test_horizons_api.py    Ephemeris parsing tests
tests/test_terrain.py         Synthetic terrain and illumination tests
tests/test_metrics.py         Ideal Horizon countdown tests
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
future Site Planner data preparation. Four specific study points are prioritized;
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
(-89.7668, -171.87); invalidate any cached data for this key before pre-computation.**
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

## Scientific explanation and presentation drafts

- [Mission explainer](docs/pitch/mission_explainer.md): accessible scientific background.
- [Submission draft](docs/pitch/submission_draft.md): current work, intended impact and pending details.
- [Three-minute demo script](docs/pitch/demo_script.md): demonstrated features versus planned work.

## Current limitations

The main app requests Horizons elevations and plots Sun/Earth curves. Its
"Solar Power" and "Earth Communication" cards use a 0° threshold. These are
simplified geometric indicators, not power estimates or verified radio links.
The "Sunlight in Window" card counts positive-elevation hourly samples; it is
not a terrain-corrected duration or an energy calculation.
Terrain-horizon calculations and ideal-horizon countdown functions exist in the
science modules, but are not yet integrated into the main interface. Ephemeris
disk cache and site comparison are not implemented in this checkout. Visibility relative to a geometric horizon does not account
for LOLA terrain, power availability or communication link performance. No frame
transformation or observer height from a terrain model is applied by the catalog
or map; the science module must reconcile its ephemeris frame with the source coordinate frames before
precision analysis. This is an educational prototype, not a mission safety tool.

Application and demonstration-video links: pending publication.
