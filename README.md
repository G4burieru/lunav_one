# Lunav One: Lunar Landing Site Navigator

Lunav One is a Python educational prototype for exploring sunlight and Earth
visibility at lunar locations and dates, with a focus on the south pole. It
supports investigation of selected environmental factors; it does not identify
safe or optimal landing sites or certify mission operations.

The project is being developed for the
[2026 NASA Space Apps Challenge: Lunar Landing Site Navigator](https://www.spaceappschallenge.org/2026/challenges/lunar-landing-site-navigator/).
The current application uses one screen: a full-page **Moon View** behind a rail
and floating panels. Explorer combines a searchable catalog and Site Cards;
Site Planner evaluates a Surface Asset through four steps. The former comparison
table is replaced by sortable catalog cards and metric-specific ranks.

## Implementation status

| Capability | Current branch |
|---|---|
| Moon View | Interactive 3D globe and south polar map with real NASA imagery |
| Base layers | Globe imagery/elevation; polar Photos (LROC NAC/WAC) and Relief (LOLA) |
| Explorer catalog | Name/coordinate search, type labels, sorting and compact cards |
| Site Card | 2027–2028 averages, Longest Night, Longest Earth Absence, metric ranks, source context |
| Site Card tabs | Overview, Sun & Earth (28-day charts), Seasons (monthly summaries) |
| Site Planner | Where, Surface Asset, When, Results; Asset Height, Elevation Mask and countdowns |
| Site Neighborhood | Polar-map cells: pre-computed for Catalog Sites at 2 m; computed on demand for Custom Sites and other heights at or south of 80°S |
| Custom Site | Coordinate search or confirmed point selection on globe/map; live calculation where needed |
| Offline alternative | src/site_map.py exports a schematic Plotly map, separate from the Moon View |
| Data pipeline | Eight sites pre-computed hourly for 2027–2028 at 2 m, automatic regeneration workflow |
| Moon View time bar | Hourly UTC slider, Play/Pause and dynamic Sun/Earth marker states |
| Site Card synchronization | Updates selected-instant information and charts when the slider is released or playback paused |
| Globe rotation | Starts automatically unless reduced motion is requested; stops at the first interaction |
| Additional layers | Layers Panel is not implemented in this checkout |
| Full scientific/operational validation | Not completed |

The Explorer's Site Card summary always covers 2027–2028 at 2 m. Moving or playing
the Moon View time bar changes the marker states immediately. Releasing the slider
or pausing sends the UTC instant to the Site Card's selected-instant line and
28-day charts; it does not change the two-year averages or ranks. If no instant
has been sent, the first sample is used. In Site Planner the Moon View time bar
covers its Analysis Window; the results panel still has its own Instant slider.
That panel's countdowns are not yet driven by the Moon View bar.

Marker **shape** identifies the coordinate type: diamond for a studied point,
circle for a regional center, square for a historical landing, and triangle for
an approximate reference. Custom Sites use a ticked ring; a Surface Asset uses
a cross in a circle. With time data, **fill level** represents the visible solar
disk fraction, while the **small upper-right dot** is filled for Earth Visibility
and hollow when Earth does not meet the visibility criterion. These are modeled
states, not power generation or communications status. The globe's initial
rotation stops at the first interaction and is disabled for reduced-motion users.

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
lunav_one/
├── app.py                       # Shell: rail, panel routing and Moon View
├── requirements.txt
├── pytest.ini
├── GLOSSARY.md                  # Shared terminology
├── .streamlit/
│   └── config.toml              # Interface theme
├── .github/workflows/
│   └── precompute.yml           # Regenerate data and open a review PR
├── src/
│   ├── sites.py                 # Sourced Catalog Sites
│   ├── site_map.py              # Schematic polar map and offline HTML export
│   ├── moon_view/               # Streamlit browser component
│   │   ├── __init__.py          # Component contract and asset loading
│   │   ├── globe.js             # 3D Moon, NASA textures and markers
│   │   ├── polar_map.js         # Leaflet + Moon Trek south polar tiles
│   │   ├── time_bar.js          # UTC slider, playback and hourly marker states
│   │   ├── view.js              # Shared view state and events
│   │   └── view.css
│   ├── panels/                 # Floating panels
│   │   ├── catalog_list.py     # Search and sorted catalog cards
│   │   ├── site_card.py        # Metrics, context and chart tabs
│   │   ├── planner.py          # Four-step Site Planner
│   │   ├── about.py
│   │   ├── common.py           # Shared helpers and cached data
│   │   └── texts.py            # Scientific explanatory copy
│   ├── charts.py                # Conditions and monthly charts
│   ├── colors.py                # Shared Sunlight / Earth Visibility color ramps
│   ├── horizons_api.py          # JPL observer ephemerides
│   ├── terrain.py               # LOLA access and Terrain Horizon
│   ├── conditions.py            # Conditions and Site Neighborhood summaries
│   ├── metrics.py               # Countdowns, durations and monthly summary
│   └── catalog.py               # Pre-computed data loader
├── scripts/
│   ├── precompute.py            # Generates data/catalog/
│   ├── compare_pgda.py          # Numerical PGDA consistency check
│   └── render_overlays.py       # Prepares the NASA-derived Layers images
├── static/
│   ├── icons/                  # SVG interface icons
│   └── overlays/               # Prepared Sun and Earth visibility images and metadata
├── data/
│   └── catalog/                 # Pre-computed ephemerides and terrain horizons
│       ├── manifest.json        # Coordinates, date coverage and terrain source
│       ├── *_ephemerides.csv.gz # Hourly ephemerides, 2027–2028
│       └── *_terrain.npz        # Site Neighborhood horizons at 2 m Asset Height
├── tests/
│   ├── test_sites.py
│   ├── test_site_map.py
│   ├── test_horizons_api.py
│   ├── test_terrain.py
│   ├── test_conditions.py
│   ├── test_metrics.py
│   ├── test_catalog.py
│   ├── test_app.py              # Panel smoke tests
│   ├── test_panels.py           # Search, formatting and state contracts
│   └── test_overlays.py
└── docs/
    ├── TEAM_PLAN.md             # Ownership and workflow
    ├── UI_OVERHAUL.md           # Interface plan and integration tasks
    ├── agents/                 # Repository instructions
    ├── adr/                    # Data architecture decisions
    └── pitch/
        ├── mission_explainer.md
        ├── submission_draft.md
        ├── demo_script.md
        └── illumination_comparison.md
```

## Data Sources

- [JPL Horizons System](https://ssd.jpl.nasa.gov/horizons/): Observer ephemerides for specified lunar coordinates.
- [LOLA terrain products](https://pgda.gsfc.nasa.gov/products/78): elevation data for terrain calculations.
- [LROC QuickMap](https://quickmap.lroc.asu.edu/) and [Moon Trek](https://trek.nasa.gov/moon/): the Moon View uses NASA imagery tiles and LOLA shaded relief; QuickMap is a reference, and the standalone Plotly map remains schematic.
- [Canadian Space Agency: Moon Exploration](https://www.asc-csa.gc.ca/eng/astronomy/moon-exploration/).

## Team

| Member | Role |
|---|---|
| Gabriel | Data & Science |
| Igor | Interface & Deployment |
| Renata | Sites, Context & Pitch |

See [docs/TEAM_PLAN.md](docs/TEAM_PLAN.md) for details.

## Standalone south-pole map (offline)

This schematic alternative runs independently of Streamlit, Horizons and the
Moon View's remote imagery/CDN services:

```bash
.venv/bin/python -m src.site_map --site 'Haworth'
```

Open the resulting HTML file in a browser. Use `--output` to choose an accessible folder if needed. Plotly is embedded, so no network connection
is needed to view it. By default, `lunar_south_pole.html` is written to the current
folder and is ignored by Git. Hover over markers for names, coordinates and descriptions.

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
no permanent illumination is claimed. The studied points, PGDA DEMs and Horizons
lunar orientation use the DE421 mean-Earth (MOON_ME) frame on a 1737.4 km sphere.
Frame compatibility is confirmed; complete topographic validation remains pending.
See the [frame evidence and Earth Visibility comparison](docs/pitch/illumination_comparison.md).

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
illumination estimates differ from the paper by less than 1.2 percentage points. Earth
visibility at all seven polar Catalog Sites is compared with NASA's PGDA average Earth
visibility map: six are within 1.3 percentage points and all within 4.6
(`python -m scripts.compare_pgda`). These are consistency checks, not a claim of
independent mission validation.

## Scientific explanation and presentation drafts

- [Mission explainer](docs/pitch/mission_explainer.md): accessible scientific background.
- [Submission draft](docs/pitch/submission_draft.md): current work, intended impact and pending details.
- [Three-minute demo script](docs/pitch/demo_script.md): demonstrated features versus planned work.

## External services and integration status

The Moon View uses browser libraries from a CDN and remote NASA Moon Trek tiles.
A tile or CDN failure can prevent the globe/map from displaying even when cached
science panels work. The standalone Plotly export is the recording fallback;
it is not a local copy of the real imagery or the full application.

`docs/UI_OVERHAUL.md` is a plan as well as a status record. The current rail opens
Catalog, Plan and About. The Site Planner already draws selectable Site
Neighborhood cells on the polar map. UTC time-bar playback and dynamic marker
states are implemented. The Layers Panel, full in-view navigation and additional
NASA Sunlight/Earth visibility layer controls still require integration or
verification; they are not implied by the existing base-layer switches. Prepared data, helper functions and legend
text do not by themselves make these controls available. No side-by-side comparison
table is present in the current interface; the catalog is sortable by metric.

## Current limitations

The interface now uses Terrain Horizon, Illumination Fraction and terrain-aware
countdowns through `get_conditions`. “Sunlight in window” means equivalent
full-Sun hours (the integral of Illumination Fraction), not hours with any part
of the Sun visible and not generated electrical energy. Earth Visibility is a
geometric criterion; it does not establish a working radio link.

Polar terrain calculations combine 20 m LOLA data within 10 km, 80 m data
from 10–50 km, and a 320 m overview from 50–150 km. The DEM read-window
correction in PR #12 and regenerated data are included. Apollo 11 uses the pre-computed global DEM. Pre-computed Site
Neighborhoods sample a 2 km radius at 100 m spacing and 2 m Asset Height;
nearby coordinates use the nearest supported point. Other heights and dates can
require live requests. Custom Sites outside the south-pole DEM use the Ideal
Horizon if no pre-computed neighborhood is available, with a warning.

Monthly charts are in Site Card → Seasons. For a polar Catalog Site at 2 m,
Site Planner uses the pre-computed neighborhood. For a Custom Site or other Asset
Height at or south of 80°S, Paint the Site Neighborhood explicitly starts a live
calculation; it may take longer or fail if external services are unavailable.
The neighborhood is centered on the chosen point, with 100 m spacing over a 2 km
radius. Colors summarize Sunlight or Earth Visibility over the Analysis Window;
the Elevation Mask affects Earth Visibility. Clicking a cell moves the
Surface Asset and updates its results. Best cell selects the highest value for
the current metric when cell values differ by at least 0.5 percentage points;
otherwise No better cell is shown. Ties use the first maximum. This is not an
overall landing recommendation. A dashed outline marks the best cell when one
is identified, and a solid outline marks the selected one. Back to the site
restores the neighborhood center. No neighborhood is offered north of 80°S.
The former Plotly neighborhood chart has been removed; src/site_map.py remains
the separate schematic Plotly export for offline use. Reference-frame compatibility has been checked; a complete
uncertainty, vehicle-safety or operational assessment has not been performed. The literature
comparison is a consistency check using related LOLA-derived inputs, not an
independent validation. This is an educational prototype, not a mission safety
tool. The schematic map itself does not calculate terrain or illumination.

Application: [Lunav One](https://lunavone.streamlit.app/).

Demonstration video: pending publication.
