# Hybrid pre-computed and live data

Catalog sites are pre-computed (2027–2028 hourly Sun/Earth ephemerides, terrain horizons, and a 2 km Site
Neighborhood at 100 m spacing for a 2 m asset height) and committed to git as compressed files, about 30 MB.
Everything else (other dates, custom sites, other asset heights) is computed live from JPL Horizons and the DEMs.
This keeps the demo instant and independent of the network for the cases judges will see, while still supporting any
date or coordinate. A GitHub Action regenerates the data when `src/sites.py` changes and monthly, and opens a pull
request because `main` is protected.

## Considered Options

- **Live only:** simplest, but every interaction waits on Horizons and the DEM servers.
- **Pre-computed only:** fastest, but limits users to catalog sites and a fixed date range.
- **Git LFS or GitHub release for the data:** adds steps for the team and for Streamlit Cloud deployment. Revisit if
  the data grows well beyond 30 MB.
