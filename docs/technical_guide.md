# Technical guide

This guide documents the completed hackathon prototype. See the [README](../README.md)
for the project overview, results, official demo and license. Earlier plans in
TEAM_PLAN and UI_OVERHAUL are historical records.

## Reading the Moon View

The Globe | South pole switch is separate from the Photos/Relief base-layer selector.
Globe zoom buttons and scroll change the viewpoint. **3D relief ×5** displaces the
surface using the LOLA elevation image with illustrative vertical exaggeration;
it does not change the Terrain Horizon computations, coordinates or Asset Height.
The control becomes available after the elevation image loads. Photos/Relief
and the 3D relief toggle are different controls.

The globe starts spinning unless reduced motion is requested. A globe press,
drag, wheel interaction or site selection stops it. **Rotate** starts it again,
zooming out to the whole Moon when needed while preserving the chosen tilt;
pressing Rotate again stops it. Adjacent relief/base-layer/zoom buttons do not
by themselves stop rotation. Reduced-motion users do not get the automatic
opening spin; they can explicitly choose Rotate.

Catalog Sites are circles. An unnamed Custom Site is a ticked ring; a named one
is a violet diamond retained in the session. A Surface Asset is a cross in a circle.
The Sun badge fills from the bottom with the visible solar-disk fraction. Earth
is blue when its center clears the Terrain Horizon plus Elevation Mask, otherwise
gray and crossed out. These states describe geometry, not power or radio performance.

The UTC time bar accepts dragging, typed dates and Play/Pause at 1 h/s, 6 h/s,
1 day/s or 3 days/s. Markers update as time moves; slider release, pause or
committed date entry updates the panels. The Site Card summary remains the
2027–2028 average at 2 m, while its selected-instant line and charts follow time.
The Planner uses its chosen Analysis Window. Within covered dates, Catalog Site
badges retain the 2 m reference height and use the Planner's Elevation Mask;
the asset uses its chosen height. Outside coverage only the computed asset's
states are supplied. Missing or incompatible data do not produce a badge.

On the polar map, green dashed rings mark prepared neighborhoods and cyan
marks the 80°S terrain boundary. They are data-coverage boundaries, not site
markers, safety areas or guarantees of instant service for every height/date.

## Site Planner and Site Neighborhood

Where, Surface Asset, When and Results let users choose location, Asset Height,
Elevation Mask and dates. Pre-computed neighborhoods have 100 m spacing within
2 km at 2 m height. At or south of 80°S, Custom Sites and other heights can request
live neighborhoods explicitly through Paint the Site Neighborhood. Clicking a
cell moves the asset. Best cell picks the maximum for the selected metric when
values differ by at least 0.5 percentage points; otherwise No better cell is
shown. This is not a landing recommendation. A dashed outline marks the best
cell, a solid one the selected cell; Back to the site restores the center.
Neighborhoods are not offered north of 80°S.

Saved Custom Site names are checked at save time for empty or duplicate values.
Failed saved-location Explorer calculations are not retried on every interaction
in the same session. Live calculations depend on external services and can fail.

## Project Structure

```text
lunav_one/
├── app.py                       # Shell: rail, panel routing and Moon View
├── LICENSE                      # Apache-2.0 for original code/documentation
├── NOTICE                       # Collective project attribution
├── THIRD_PARTY_NOTICES.md        # External resources retain their own terms
├── requirements.txt
├── pytest.ini
├── GLOSSARY.md                  # Shared terminology
├── .streamlit/
│   └── config.toml              # Interface theme
├── .github/workflows/
│   ├── precompute.yml           # Regenerate data and open a review PR
│   └── tests.yml                # Run tests on pull requests and main
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
│   │   ├── places.py           # Site descriptions and external image references
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
│   └── compare_pgda.py          # Numerical PGDA consistency check
├── media/
│   └── lunavone.mp4             # Local copy of the official demo
├── static/
│   └── icons/                  # SVG interface icons
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
│   ├── test_catalog_time.py     # Catalog/Planner states and JavaScript badges
│   └── test_panels.py           # Search, formatting and state contracts
└── docs/
    ├── technical_guide.md       # Controls, coordinates, data pipeline and offline map
    ├── final_release_review.md  # Final documentation/license checks
    ├── TEAM_PLAN.md             # Ownership and workflow
    ├── UI_OVERHAUL.md           # Interface plan and integration tasks
    ├── agents/                 # Repository instructions
    ├── adr/                    # Data architecture decisions
    └── pitch/
        ├── mission_explainer.md
        ├── submission_draft.md
        ├── demo_30s.md          # Official short submission demo
        ├── illumination_comparison.md
        ├── final_science_review.md # Historical scientific and image-source review
        └── catalog_expansion_review.md # 17-site provenance and temporal integration
```

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
[-180, 180]. The catalog has 17 Catalog Sites for Explorer context and
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
| Peak Near Shackleton | -88.811 | 123.6901 | NASA Table A2-2 region center, R07 / Site07 |
| Connecting Ridge Extension | -89.0324 | -101.999 | NASA Table A2-2 region center, SL3 |
| de Gerlache Rim 1 | -88.6834 | -67.9321 | NASA Table A2-2 region center, R11 / Site11 |
| de Gerlache Rim 2 | -88.23 | -64.6284 | NASA Table A2-2 region center, SL2 |
| de Gerlache-Kocher Massif | -85.8296 | -116.322 | NASA Table A2-2 region center, R42 / Site42 |
| Leibnitz Beta Plateau (historical region) | -85.4266 | 31.74276 | NASA Table A2-2 historical region center, R20 / Site20 |
| Nobile Rim 1 | -85.4381 | 37.36667 | NASA Table A2-2 region center, R06 / Site06 |
| Nobile Rim 2 | -83.954 | 58.82206 | NASA Table A2-2 region center, DM2 |
| Amundsen Rim | -84.2287 | 69.44396 | NASA Table A2-2 region center, DM1 |
| Apollo 11 (Tranquility Base) | 0.67416 | 23.47314 | Historical lunar module location |

[Gläser et al. (2017), Table 2, PDF page 12](https://ntrs.nasa.gov/api/citations/20170007365/downloads/20170007365.pdf)
studied the four priority points at a 2 m Asset Height for 2017–2037. Their source
longitudes (222.83, 245.98, 197.19, 204.70 degrees east) were converted by subtracting
360. S1/S2 are local catalog labels for the two Shackleton rows, not the cluster
identifiers in the article's Table 3. These are not certified landing points and
no permanent illumination is claimed. The studied points, PGDA DEMs and Horizons
lunar orientation use the DE421 mean-Earth (MOON_ME) frame on a 1737.4 km sphere.
Frame compatibility is confirmed; complete topographic validation remains pending.
See the [frame evidence and Earth Visibility comparison](pitch/illumination_comparison.md).

Existing dictionary keys are retained for compatibility. **The key
`Shackleton Crater (Rim)` now uses S1 instead of the previous Site04 region center
(-89.7668, -171.87).** The current manifest matches S1. The loader rejects
pre-computed entries whose manifest coordinates differ from the catalog or whose
START/END dates differ from the supported 2027–2028 window.
The legacy key `Malapert Massif (Summit)` remains a region center, not a verified
summit. Regional centers are from NASA's Lunar Surface Data Book ACD-50044 Rev A
(2023), Table A2-2, printed pages 57–58. Each entry records its source, coordinate
meaning and validation status. The separate offline Plotly map uses diamonds for study points, circles
for regional centers, and squares for actual landing locations within its extent. A symbol key explains these types;
hover information groups coordinates, context, provenance and validation status.

The 17 entries comprise 12 regional centers, four specific illumination-study
points and Apollo 11. They represent all 13 regions in the historical
[NASA August 2022 list](https://www.nasa.gov/news-release/nasa-identifies-candidate-regions-for-landing-next-americans-on-moon/),
with Connecting Ridge represented by C1/C2 rather than its regional center
(R01/Site01: -89.4632, -137.49). The Shackleton S1/S2 points are additional study
locations, not extra 2022 candidate regions. CLPS landings are not added here.

Haworth was listed in both 2022 and the
[October 2024 revision](https://www.nasa.gov/news-release/nasa-provides-update-on-artemis-iii-moon-landing-regions/).
The mountain informally called Leibnitz Beta is now officially named
[Mons Mouton](https://svs.gsfc.nasa.gov/5074/).
Its legacy catalog key and coordinates remain unchanged. Regional selection and
nomenclature changed in 2024: Mons Mouton and Mons Mouton Plateau are listed
separately. The older polygon is not documented here as equivalent to either
revised region, so no automatic retention in the 2024 list is claimed. This catalog is not a complete set of the
nine revised 2024 regional centers. All 17 Overviews now include sourced context;
the nine new entries explicitly label their shared NASA LROC mosaic as regional
context rather than a photograph of the exact coordinate. See the
[catalog expansion review](pitch/catalog_expansion_review.md).
Historical Artemis III candidate-region associations are separate from
[NASA's 2026 architecture](https://www.nasa.gov/news-release/nasa-adds-mission-to-artemis-lunar-program-updates-architecture/):
Artemis III is an Earth-orbit demonstration planned for 2027, while Artemis IV
targets the first Artemis crewed lunar landing in 2028. No current landing-region
selection is implied by this catalog.

- [NASA coordinate table](https://ntrs.nasa.gov/api/citations/20230007818/downloads/ACD-50044%20Lunar%20Surface%20Data%20Book%20Rev%20A.pdf).
- [GSFC LOLA region products](https://pgda.gsfc.nasa.gov/products/78): MOON_ME / DE421 frame.
- [NASA Apollo coordinates](https://nssdc.gsfc.nasa.gov/planetary/lunar/lunar_sites.html): Apollo 11 lunar module reference location.
- [NASA 2022 candidate-region announcement](https://www.nasa.gov/news-release/nasa-identifies-candidate-regions-for-landing-next-americans-on-moon/): historical Artemis context, not a statement of current mission selection.

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

[Preliminary literature comparison](pitch/illumination_comparison.md) records
four study points. With the combined 20 m/80 m terrain, all four mean
illumination estimates differ from the paper by less than 1.2 percentage points. Earth
visibility at the seven polar Catalog Sites evaluated in the reference study is compared with NASA's PGDA average Earth
visibility map: six are within 1.3 percentage points and all within 4.6
(`python -m scripts.compare_pgda`). These are consistency checks, not a claim of
independent mission validation.

Custom Site names are checked again when saved, rejecting empty or already-used
names. If a saved location fails to compute its Explorer states, that coordinate
remains without a badge for the rest of the session instead of retrying on every
interaction (PR #42).

## Data coverage and external services

Polar Terrain Horizons use 20 m LOLA data within 10 km, 80 m data from 10–50 km
and a 320 m overview from 50–150 km. Apollo 11 has a pre-computed global DEM horizon.
For unsupported live terrain outside the polar coverage, the identified Ideal
Horizon fallback ignores local ridges. Covered nonpolar cases can reuse their
pre-computed neighborhood; other-height fallback details are recorded in the
calculation's terrain provenance. No constant global coverage is implied.

Moon View libraries are loaded from a CDN and imagery from NASA Moon Trek.
Scientific results can use cached data while remote imagery is unavailable.
The schematic Plotly export is an offline location map, not an offline copy of
the full app. See [ADRs](adr/) for data and architecture decisions.
