# Demonstration script — approximately three minutes

Draft for the current devel_renata build. Narration is about 331 words; rehearse
at 125–140 words per minute, allowing pauses for screen transitions. Bracketed
production notes are not spoken. Do not read numerical results before checking
them in the actual run. Recheck this script when the interface changes.

## Preparation

- Run `python -m streamlit run app.py` with network access for Horizons.
- Select `Shackleton Crater (Rim)`; its display name in the map is Shackleton Rim S1.
- Choose a date and a short analysis window, then let the request finish before recording.
- Export the map in advance: `python -m src.site_map --site 'Connecting Ridge C1' --output /tmp/lunar_demo.html`.
- Keep the exported file open in the browser as a fallback. If Horizons fails,
  show the offline map and explain that live charts are unavailable. Do not
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

[If Horizons succeeded, show the app controls, Sun curve and Earth curve.]

“In the current application we can select a Catalog Site, choose a date and
analysis window, or enter a Custom Site. JPL Horizons supplies Sun and Earth
positions. These curves show elevation relative to the Ideal Horizon at zero
degrees. They help us ask how the geometry changes over time. The current cards
use that same simplified threshold: they are not electrical power calculations
or confirmation of a working radio link.”

[Fallback narration, replacing this segment if live data is unavailable:
“The map works independently of Horizons. Live ephemeris charts need a successful
network request and are unavailable in this recording. We are showing the
catalog and its assumptions, without substituting simulated mission results.”]

## 1:40–2:20 — What remains in development

[Show README's implementation-status table, not an invented UI screen.]

“Our science modules already contain Terrain Horizon and Illumination Fraction
calculations. Illumination Fraction describes how much of the solar disk clears
the terrain; it does not measure generated electricity. These functions are not
yet connected to the interface. The team still needs to validate the Catalog
Sites against its elevation model, reconcile coordinate frames and prepare
pre-computed data. Side-by-side comparisons are also still in development.”

## 2:20–3:00 — Purpose and next steps

[Return to the map and its legend.]

“Explorer is our planned learning mode; Site Planner is our planned mode for
placing and evaluating a Surface Asset. Neither is a separate finished mode
today. Our immediate contribution is a transparent catalog and an accessible
way to discuss geometry, terrain and uncertainty. We want students and future
users to understand why a promising position needs further investigation.
Lunav One supports that discussion; a complete landing assessment must also
consider slopes, obstacles, vehicle requirements and operational constraints.”

## Evidence and publication notes

Scientific background: [NASA south-pole environment](https://www.nasa.gov/reference/moonbase-environment/).
Coordinate study: [Gläser et al. (2017), Table 2](https://ntrs.nasa.gov/api/citations/20170007365/downloads/20170007365.pdf).
Ephemeris method: [JPL Horizons manual](https://ssd.jpl.nasa.gov/horizons/manual.html).
Implementation evidence: `app.py`, `src/sites.py`, `src/site_map.py`,
`src/terrain.py` and `src/metrics.py`; no live scientific validation is implied.
Add the verified application/video URLs to the submission after recording.
