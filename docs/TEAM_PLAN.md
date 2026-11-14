# Team Plan: Lunar Landing Site Navigator

## Objective

Build a Streamlit web application that lets users compare lunar landing sites and dates, with a focus on the
lunar south pole. For each scenario, the application shows the Sun's position (power generation) and Earth's
position (direct-to-Earth communication) relative to the horizon, together with the time remaining before
sunset and Earthset.

Challenge statement: <https://www.spaceappschallenge.org/2026/challenges/lunar-landing-site-navigator/>

## Responsibilities

### Gabriel: Data & Science (branch `devel_gabriel`)

1. **Terrain-aware horizon from LOLA topography (top priority).** The current horizon is the ideal ellipsoid
   horizon. At the pole the Sun stays roughly 1.5° above it, so the application reports continuous sunlight at
   Shackleton. Local terrain determines actual shadow and line-of-sight conditions.
2. **Operational metrics** in `src/metrics.py`: hours until sunset and hours until Earthset.
3. **Ephemeris cache** in `data/sites_cache.json`, so the demo works even if JPL Horizons is unavailable.

### Igor: Interface & Deployment (branch `devel_igor`)

1. Prominent KPI cards with sunset and Earthset countdowns (using `src/metrics.py`).
2. **Side-by-side comparison** of two or three scenarios (site + date), including "same site, different date".
3. Timeline view: a slider that shows the Sun and Earth positions at a selected instant.
4. Dark theme and **deployment to Streamlit Community Cloud** by Saturday evening.

### Renata: Sites, Context & Pitch (branch `devel_renata`)

1. **Expand `src/sites.py`**: Apollo sites, CLPS targets, Artemis III candidate regions, and landing sites from
   other countries' programs, citing the source of each coordinate.
2. Landing site map in `src/site_map.py` (optional: Moon Trek imagery as a background).
3. A short explainer for educators and the public: why the lunar south pole is so challenging.
4. README data source credits (Horizons, LOLA, QuickMap, Moon Trek, CSA), demo video, and submission text.
   Pitch use case: the Canadian Space Agency's lunar utility rover.

## File Ownership

Each member edits only the files they own. This keeps merges conflict-free.

| Owner | Files |
|---|---|
| Gabriel | `src/horizons_api.py`, `src/metrics.py`, `src/terrain.py`, `src/catalog.py`, `src/conditions.py`, `scripts/`, `data/`, `.github/workflows/precompute.yml`, `tests/test_horizons_api.py`, `tests/test_metrics.py`, `tests/test_terrain.py`, `tests/test_catalog.py`, `tests/test_conditions.py` |
| Igor | `app.py`, `src/charts.py`, `.streamlit/` |
| Renata | `src/sites.py`, `src/site_map.py`, `README.md`, `docs/pitch/` |
| Shared | `requirements.txt`, `docs/TEAM_PLAN.md`, `GLOSSARY.md`, `docs/adr/` |

If you need a change in a file you do not own, ask its owner.

### Interface Contracts

Do not change these without telling the team:

- `get_conditions(lat, lon, start_date, days, asset_height=2.0)` in `src/conditions.py` is the entry point for the
  app. It returns a DataFrame with `time`, `sun_azimuth`, `sun_elevation`, `earth_azimuth`, `earth_elevation`,
  `sun_horizon`, `earth_horizon`, `illumination_fraction`, and `df.attrs` `terrain`, `source`, `site`. Catalog
  sites return instantly; other points are computed live (up to ~2 min), so cache the call in the app.
- `src/metrics.py`: `hours_until_sunset(df, at)`, `hours_until_earthset(df, at, elevation_mask=0.0)`,
  `sunlight_hours(df)`, `earth_visible_hours(df, elevation_mask=0.0)`.
- `LUNAR_SITES[name] = {"lat", "lon", "description"}` in `src/sites.py`.

### Shared Vocabulary and Decisions

- Use the terms defined in [`GLOSSARY.md`](../GLOSSARY.md) in code, UI, and the pitch (e.g. Explorer, Site Planner,
  Surface Asset, Illumination Fraction).
- Key data decisions are recorded in [`docs/adr/`](adr/). Read them before changing how data is fetched or stored.

## Git Workflow

```bash
git checkout devel_<your_name>
git pull origin main              # bring in work that has already been merged
# ... work and commit ...
git push origin devel_<your_name>
```

- Open a pull request from `devel_<your_name>` into `main`. Merge small changes often (morning, afternoon, evening).
- `requirements.txt`: only **append** lines at the end; never reorder existing lines.
- Before opening a pull request, run `streamlit run app.py` and `pytest`.
- Write code, comments, commit messages, and documentation in English.

## Milestones

| When | Goal |
|---|---|
| Saturday morning | Everyone runs `streamlit run app.py`; terrain horizon work starts. |
| Saturday evening | Cache working, countdowns on screen, first deployment live. |
| Sunday morning | Terrain horizon integrated; scenario comparison complete. |
| Sunday afternoon | Code freeze, demo video recorded, project submitted. |
