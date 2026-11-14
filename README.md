# Lunav One: Lunar Landing Site Navigator

Lunav (Lunar Navigation) develops data-driven solutions to identify safe and optimal landing sites on the Moon.
Using open NASA datasets, our team bridges space science and technology to guide the future of lunar exploration.

This repository is our submission to the
[2026 NASA Space Apps Challenge: Lunar Landing Site Navigator](https://www.spaceappschallenge.org/2026/challenges/lunar-landing-site-navigator/).
It is an interactive web application that lets mission planners, educators, and the public compare lunar landing
sites and dates by visualizing the position of the Sun (power generation) and Earth (direct-to-Earth communication)
relative to the local horizon.

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
pytest
```

## Project Structure

```
app.py                  Streamlit user interface
src/horizons_api.py     Sun and Earth ephemerides from JPL Horizons
src/metrics.py          Operational metrics (time to sunset / Earthset)
src/charts.py           Plotly charts
src/site_map.py         Landing site map
src/sites.py            Curated landing site catalog
data/                   Pre-computed ephemeris cache
tests/                  Automated tests
docs/TEAM_PLAN.md       Task assignments, file ownership, and Git workflow
```

## Data Sources

- [JPL Horizons System](https://ssd.jpl.nasa.gov/horizons/): Sun and Earth positions from any point on the lunar surface.
- [LROC QuickMap](https://quickmap.lroc.asu.edu/) and [Moon Trek](https://trek.nasa.gov/moon/): lunar imagery and topography (LOLA).
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

Open the resulting HTML file in a browser. Plotly is embedded, so no network connection
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
[-180, 180]. Polar coordinates come from the **NASA Lunar Surface Data Book,
ACD-50044 Rev A (2023), Table A2-2, printed pages 57–58**:

| Region | Latitude | East longitude | Source ID |
|---|---:|---:|---|
| Shackleton Rim | -89.7668 | -171.87 | R04 / Site04 |
| Malapert Massif | -85.9948 | -0.23578 | R23 / Site23 |
| Faustini Rim A | -87.8897 | 90.0 | LM7 |
| Haworth | -86.7639 | -22.777 | Haworth |

These are representative DEM polygon centers, not certified safe landing points,
crater centers or guaranteed summits. Existing catalog keys are retained for app
compatibility; `name` gives the source region name. Each entry includes its source,
source location, scientific context and exploration context.

- [NASA coordinate table](https://ntrs.nasa.gov/api/citations/20230007818/downloads/ACD-50044%20Lunar%20Surface%20Data%20Book%20Rev%20A.pdf).
- [GSFC LOLA region products](https://pgda.gsfc.nasa.gov/products/78): MOON_ME / DE421 frame.
- [NASA Apollo coordinates](https://nssdc.gsfc.nasa.gov/planetary/lunar/lunar_sites.html): Apollo 11 lunar module reference location.
- [NASA 2022 candidate-region announcement](https://www.nasa.gov/centers-and-facilities/marshall/the-marshall-star-361/): historical Artemis context, not a statement of current mission selection.

## Current limitations

The main app already requests Horizons elevations and plots Sun/Earth curves.
Terrain horizons, ephemeris disk cache, countdown metrics and site comparison are
not implemented yet. Visibility relative to a geometric horizon does not account
for LOLA terrain, power availability or communication link performance. No frame
transformation or observer height from a terrain model is applied by the catalog
or map; the science module must reconcile its ephemeris frame with MOON_ME before
precision analysis. This is an educational prototype, not a mission safety tool.

Application and demonstration-video links: pending publication.
