# Lunav One — Lunar Landing Site Navigator

**Explore how lunar terrain and time shape sunlight and Earth visibility.**

Lunav One is a completed educational and exploratory prototype built for the
[2026 NASA Space Apps Challenge](https://www.spaceappschallenge.org/2026/challenges/lunar-landing-site-navigator/).
It brings NASA data into an interactive Moon View, a documented catalog of
17 lunar locations and a Site Planner. It helps people investigate environmental
conditions without presenting them as certified landing or mission decisions.

[**Open Lunav One**](https://lunavone.streamlit.app/) ·
[User and technical guide](docs/technical_guide.md) ·
[Scientific background](docs/pitch/mission_explainer.md)

## Why the lunar south pole?

The Sun stays low near the poles. Small changes in position, terrain and height
can change when sunlight or Earth clears a ridge. A named region is not a precise
summit or landing point. Lunav One connects geographic context with modeled
conditions so that these differences and their assumptions are visible.

## Explore the application

| Feature | What it provides |
|---|---|
| **Moon View** | Interactive 3D globe and south polar map, with Photos (LROC) and Relief (LOLA) base layers from NASA Moon Trek |
| **Illustrative 3D terrain** | Optional **3D relief ×5** on the globe; vertical relief is exaggerated five times for visibility, not displayed at its real vertical scale |
| **Globe controls** | Drag, scroll, zoom buttons and **Rotate** to start or stop spinning; a responsive layout also supports phones |
| **Explorer** | Searchable, sortable catalog of 17 Catalog Sites with coordinate meanings, scientific context and sourced Overview imagery |
| **Site Cards** | Sunlight, Earth Visibility, Longest Night, Longest Earth Absence, selected-instant information and Sun & Earth / Seasons charts |
| **Time bar and markers** | Hourly UTC selection, typed dates, playback speeds and dynamic Sun/Earth badges |
| **Site Planner** | Location, Asset Height, Elevation Mask and Analysis Window, with terrain-aware results and countdowns |
| **Site Neighborhood** | Selectable polar-map cells colored by the chosen metric; prepared data or an explicitly requested live calculation where supported |
| **Custom Sites and About** | Coordinate/map selection, session-saved named locations and expandable explanations of the model and sources |
| **Data access** | Pre-computed 2027–2028 scenarios at 2 m for all 17 sites, plus supported live calculations and an identified Ideal Horizon fallback |

The globe initially rotates unless reduced motion is requested. Interacting with
the globe or selecting a site stops it; **Rotate** can restart it, and a second
click stops it again. The adjacent relief, base-layer and zoom buttons do not
by themselves end the spin. **3D relief ×5 is a visual aid**: it does not change
coordinates, Asset Height or the scientific calculations. The Photos/Relief
base-layer selector and the 3D relief toggle are separate controls.

## Official Demo — 30 seconds

[**Watch the official demo — MP4, approximately 28 seconds**](media/lunavone.mp4)

This is the project's main public demonstration and the video prepared for the
official Space Apps submission. The recording is **27.925 seconds** long.
The [English script](docs/pitch/demo_30s.md) covers the team, problem, working
application, NASA inputs and educational impact.

## Technologies

Python and Streamlit run the app; Pandas, NumPy, Rasterio and Requests support
the data pipeline. Plotly renders scientific charts and the standalone offline
map. JavaScript/WebGL uses globe.gl / Three.js, Leaflet, Proj4js and Proj4Leaflet.
Browser libraries load from a CDN; no Node.js build is needed to run the app.
Pytest and Streamlit AppTest verify software behavior.

## NASA data and scientific sources

| Source | Use in Lunav One |
|---|---|
| [JPL Horizons](https://ssd.jpl.nasa.gov/horizons/manual.html) | Sun/Earth observer ephemerides |
| [NASA Goddard PGDA / LOLA](https://pgda.gsfc.nasa.gov/products/78) | Elevation models for Terrain Horizons |
| [NASA PGDA polar visibility products](https://pgda.gsfc.nasa.gov/products/69) | Reference-map consistency comparison |
| [NASA Moon Trek](https://trek.nasa.gov/moon/) and [LROC](https://lroc.im-ldi.com/) | Geographic imagery and shaded-relief context |
| [NASA Lunar Surface Data Book, Table A2-2](https://ntrs.nasa.gov/api/citations/20230007818/downloads/ACD-50044%20Lunar%20Surface%20Data%20Book%20Rev%20A.pdf) | Regional-center coordinates and identifiers |
| [Gläser et al. (2017), Table 2](https://ntrs.nasa.gov/api/citations/20170007365/downloads/20170007365.pdf) | Four specific illumination-study points and published reference values |

NASA supplies source data and imagery. **Lunav One calculates** Terrain Horizons,
Illumination Fractions, Earth Visibility, durations and ranks from those inputs.
Imagery is geographic context, not a current shadow measurement or project output.
[LROC QuickMap](https://quickmap.lroc.im-ldi.com/) and
[CSA lunar exploration resources](https://www.asc-csa.gc.ca/eng/astronomy/moon-exploration/)
provide additional context. See [third-party notices](THIRD_PARTY_NOTICES.md)
for credits and applicable terms; no agency partnership or endorsement is implied.

## Results and scientific checks

**Consistency-checked against published studies; independent validation not performed.**

- **Solar illumination:** means for four studied points differ by less than
  **1.2 percentage points** from Gläser et al. (2017).
- **Earth Visibility:** seven polar locations were compared with NASA PGDA's
  reference map. Six differ by at most **1.3 percentage points**; all seven
  differ by at most **4.6 percentage points**.

These are documented consistency checks, not independent validation: the project
and references share LOLA-derived terrain, and their periods, heights, resolutions
and metric definitions differ. See the [values, methods and reproduction commands](docs/pitch/illumination_comparison.md).

The hackathon implementation is complete. Automated tests check software behavior,
including synthetic terrain, catalog files, panel flows and temporal markers;
they are distinct from scientific validation. The final documentation review
recorded **134 passing tests**; commands and environment details are in the
[release review](docs/final_release_review.md). No operational certification is claimed.

## Catalog provenance and conventions

The 17 entries comprise four studied points, 12 regional centers and Apollo 11.
Connecting Ridge C1/C2 are specific study points, not the regional center.
Leibnitz Beta's historical association with Mons Mouton does not establish an
identical footprint for either region named in NASA's 2024 list. Historical
Artemis III regional studies are separate from subsequent mission architecture.

The [technical guide](docs/technical_guide.md#catalog-provenance-and-conventions)
retains the complete coordinate table, original references, longitude convention,
reference-frame evidence, legacy identifiers and data-regeneration workflow.
No Catalog Site is a certified landing location.

## Install and run

Use Python **3.11+**; the CI workflow uses Python **3.13**.

```bash
python -m venv .venv
```

Activate the environment using the command for your platform:

```powershell
.venv\Scripts\Activate.ps1
```

```bash
source .venv/bin/activate  # macOS / Linux
```

```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Open the local address printed by Streamlit, usually `http://localhost:8501`.
The Moon View needs remote imagery and browser libraries; live calculations
also need external services. The [schematic offline Plotly map](docs/technical_guide.md#standalone-south-pole-map-offline)
can be exported independently of Horizons and Streamlit.

To run the tests:

```bash
python -m pip install pytest
python -m pytest -q
```

The JavaScript badge regression runs when a Node-compatible runtime is available;
otherwise that test is explicitly skipped. Node is not needed to run the app.
[Project structure and implementation details](docs/technical_guide.md#project-structure)
are maintained separately from this overview.

## Scientific limitations

- **Illumination Fraction** is the visible fraction of the solar disk, not
  generated electricity. Battery autonomy, usable energy and thermal survival
  are not calculated.
- **Earth Visibility** is geometric visibility of Earth's center above the
  Terrain Horizon plus Elevation Mask, not a guaranteed radio link or relay service.
- Hourly sampling, DEM resolution and coordinate meaning limit interpretation.
  A region center is not necessarily a summit or rim crest; imagery and exaggerated
  relief are illustrative rather than a landing-safety measurement.
- Independent image-based shadow checks, a full uncertainty assessment, vehicle
  safety and operational communications analysis are outside the hackathon scope.
  No permanent sunlight, safe landing or operational capability is certified.

## Team

**Lunav One**

| Member | Contribution |
|---|---|
| João Gabriel Santos | Data & Science |
| Igor Wanderley | Interface & Deployment |
| Renata Andrade | Sites, Context & Pitch |

## License

The team's original code and documentation are licensed under the
**Apache License 2.0 — SPDX: Apache-2.0**. See [LICENSE](LICENSE) and [NOTICE](NOTICE).
Copyright 2026 Lunav One contributors.

Apache 2.0 permits use, modification and redistribution under its conditions;
it does not prevent others from using the software. NASA imagery, source data,
external maps and third-party libraries retain their own terms and credits.
They are not relicensed by Lunav One. See [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

[Scientific explainer](docs/pitch/mission_explainer.md) ·
[Submission text](docs/pitch/submission_draft.md) ·
[Official demo script](docs/pitch/demo_30s.md) ·
[Shared vocabulary](GLOSSARY.md) ·
[Architecture decisions](docs/adr/)
