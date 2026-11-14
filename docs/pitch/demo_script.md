# Demonstration script — approximately three minutes

Draft for the integrated Explorer / Site Planner build. Rehearse
at 125–140 words per minute, allowing pauses for screen transitions. Bracketed
production notes are not spoken. Do not read numerical results before checking
them in the actual run. Recheck this script when the interface changes.

## Preparation

- Run `python -m streamlit run app.py`. Network access is needed for live cases.
- In Explorer, select Shackleton Rim S1 (internal key `Shackleton Crater (Rim)`).
- Choose 2027-01-01 and a 14-day window at the default 2 m Asset Height, then
  let loading finish before recording. Covered scenarios use committed data.
- Export the map in advance: `python -m src.site_map --site 'Connecting Ridge C1'`.
- Keep the exported file open in the browser as a fallback. If a live case fails,
  return to the covered catalog window or show the offline map. Do not
  substitute invented curves or present the map as an offline ephemeris cache.

## 0:00–0:25 — The question

[Show the app title, or the exported map if the live request is unavailable.]

“Where should a mission explore near the Moon's south pole, and when? The Sun
stays low in the sky, so terrain can block light even when a smooth-horizon
calculation says it is visible. Lunav One helps explain that problem through
documented locations, a lunar map and time-dependent Sun and Earth geometry.”

## 0:25–1:00 — Coordinates with meaning

[Show the standalone map. Hover over Shackleton Rim S1, then Malapert Massif.]

“These diamonds represent specific illumination-study points. Circles represent
regional centers. Our priority Shackleton and Connecting Ridge points come from
a published study at two metres above ground. The hover information explains the
coordinate meaning, source and pending validation. A regional center is not a
verified summit, and none of these markers certifies a safe landing. The map is
schematic: it has no surface imagery or terrain layer.”

## 1:00–1:40 — What works now

[Show Explorer controls, the Sun/Earth curves, countdowns and comparison table.]

“Explorer lets us choose a Catalog Site and time window. The charts now include
the Terrain Horizon, and the cards show countdowns and equivalent full-Sun
hours. These hours sum the Illumination Fraction, rather than counting every
partially illuminated hour as full sunlight. Catalog data covers 2027 and 2028
at two metres. The comparison table uses the same window for all sites. These
are modeled conditions, not measured electricity or verified radio links.”

[If no time-series data can be displayed, replace this segment with:
“The standalone map works without Horizons. We cannot display the selected
conditions in this recording, so we will show the catalog and its assumptions
without substituting invented mission results.”]

## 1:40–2:20 — Site Planner and scientific checks

[Show Site Planner at a Catalog Site, 2 m Asset Height and zero Elevation Mask.
Point out the controls without triggering a slower live request during narration.]

“Site Planner accepts a Custom Site, Asset Height and Elevation Mask. Some changes
require live calculations. Polar terrain now uses twenty-metre data close to
the point. Comparing our four study points with the literature, their average
illumination differs by less than 1.2 percentage points. The earlier Shackleton
S2 discrepancy fell substantially. This is consistent with terrain resolution
mattering, but shared LOLA data and different time periods mean this remains a
consistency check, not independent validation.”

## 2:20–3:00 — Purpose and next steps

[Return to the map and its legend.]

“Explorer supports learning; Site Planner helps investigate a Surface Asset's
modeled environment. Monthly and Site Neighborhood summaries are available in
the science modules, but their visual presentation is still future work. Our
next steps include further scientific review, uncertainty assessment and interface
refinement. We want users to understand why a promising position needs further
investigation. A complete landing assessment must also consider slopes,
obstacles, vehicle requirements and operational constraints. Our catalog and
charts help explain selected environmental factors; they do not certify a safe
or optimal landing.”

## Evidence and publication notes

Scientific background: [NASA south-pole environment](https://www.nasa.gov/reference/moonbase-environment/).
Coordinate study: [Gläser et al. (2017), Table 2](https://ntrs.nasa.gov/api/citations/20170007365/downloads/20170007365.pdf).
Ephemeris method: [JPL Horizons manual](https://ssd.jpl.nasa.gov/horizons/manual.html).
Implementation evidence: `app.py`, `src/sites.py`, `src/site_map.py`,
`src/terrain.py` and `src/metrics.py`; no live scientific validation is implied.
Add the verified application/video URLs to the submission after recording.
