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
