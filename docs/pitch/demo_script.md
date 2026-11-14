# Three-minute demo — Moon View interface

D2 draft for the current branch, not every feature in UI_OVERHAUL.md. Rehearse the
spoken paragraphs at about 130 words per minute, allowing time for transitions.
Bracketed instructions and the checklist are not narration. Use the deployed
[application](https://lunavone.streamlit.app/) only after checking its build
against the branch used for this script.

## Prepare before recording

- Start `python -m streamlit run app.py` and open the Catalog panel. Let globe
  libraries, NASA textures and cached Catalog Site summaries load.
- Confirm Globe / South pole map switches, Photos / Relief layers and site selection
  in the browser. Python smoke tests do not test browser tile loading or interaction.
- Rehearse Connecting Ridge C1, then Plan here. Keep 2 m Asset Height, 0° Elevation
  Mask, 2027-01-01 and 14 Earth days; avoid a slow live-height change during narration.
- Prepare the offline alternative: `python -m src.site_map --site 'Connecting Ridge C1'`.
  Open `lunar_south_pole.html` in a browser. It embeds Plotly and needs no Horizons,
  tiles or CDN after export. It cannot demonstrate real imagery or the full interface.

## 0:00–0:20 — Why this matters

[Show the globe with the Catalog panel open; drag gently to show the 3D view.]

“Near the lunar south pole, the Sun stays low and nearby terrain can hide both
sunlight and Earth. A regional name alone does not tell us what a surface asset
will see. Lunav One makes those differences easier to explore, while keeping the
scientific assumptions visible.”

## 0:20–0:50 — From globe to real polar imagery

[Search for Connecting Ridge C1 and select it. The polar site opens the map.
Briefly switch Photos / Relief, then return to Photos.]

“This Moon View combines a three-dimensional globe with a south polar map using
real NASA imagery. Photos show LROC mosaics; Relief shows LOLA shaded terrain.
Selecting Connecting Ridge C1 takes us to its surroundings. These images provide
geographic context: they are not a live view of today's shadows or proof of a
safe landing.”

## 0:50–1:35 — Read a Site Card

[Point to type, coordinate context, four metrics and rank. Open Sun & Earth,
then briefly Seasons. Do not operate a nonexistent play/time bar.]

“The Site Card distinguishes a specific study point from a regional center or a
historical landing. Its sources explain the coordinates. Sunlight averages the
visible fraction of the solar disk over 2027 and 2028 at two metres above ground.
It does not measure electricity. Earth Visibility is a geometric Earth view,
not a guaranteed radio link. Longest Night and Longest Earth Absence describe
the longest modeled gaps within that window. They do not calculate battery
endurance. Charts show the Terrain Horizon, and Seasons summarizes monthly
changes. The rank compares this metric among our catalog entries, not landing
safety.”

## 1:35–2:15 — Plan a scenario

[Click Plan here. Show Where, Surface Asset, When and Results. Use the current
Planner's Instant slider. In the polar map, choose Sunlight or Earth visibility,
click a neighborhood cell and point out the updated Surface Asset/results. The
current metric's best cell has a dashed outline; the selected cell has a solid
outline. Use Back to the site to return to the catalog position.]

“Plan here opens four steps: choose a position, set the Surface Asset, choose
when to analyze, and inspect the results. Asset Height can change what clears
the terrain. Elevation Mask requires extra clearance for Earth's center. We
keep two metres to use the prepared neighborhood, choose a time window and
inspect the countdowns. They describe Sunset and Earthset from the selected
instant. Selecting a neighborhood cell directly on the polar map moves our
Surface Asset and updates its analysis.”

## 2:15–3:00 — Science, boundaries and purpose

[Return to the Catalog or About panel; end on the Moon View.]

“NASA provides the ephemerides, elevation models and imagery; our project
calculates the terrain horizons and summary metrics. Our four illumination-study
points are within one point two percentage points of published means. That is
a consistency check, not independent validation: both use LOLA data and different
time periods. Terrain resolution, hourly sampling and operational constraints
still matter. We do not certify safe landings, electrical power or communications.
Our contribution is an accessible way to inspect locations, understand what the
numbers mean and ask better questions before a complete mission assessment.”

## Offline replacement if external services fail

Show the already exported Plotly map and say: “This is our schematic offline
fallback. It preserves documented locations and coordinate meaning without
requiring remote services. Real imagery and the interactive Moon View are
unavailable in this recording.” If cached panels still work, show those separately.
Do not imply the offline HTML includes the NASA imagery, charts or live calculations.

## Final pass after the team's last merge

- Confirm the hosted build and exact control names; rehearse in the recording browser.
- A6/B6 neighborhood cells are implemented on the polar map for Catalog Sites
  at or south of 80°S, at 2 m height. Rehearse cell selection, both color metrics,
  Best cell and Back to the site in the recording browser. Best means highest
  value for the selected metric and window, not safest landing point.
- A3 time-bar playback, animated marker states, A7 in-view navigation and A8/B7
  additional layer controls still need a new code/browser check. They are not
  demonstrated as implemented in this script.
- Currently the Site Card falls back to the first 2027 instant without a time-bar
  event; the Planner has its own Instant slider. Update this narration if that changes.
- Check legends actually consuming SUN_LAYER / EARTH_LAYER before showing them;
  text constants alone do not add a working Layers panel.
- If using the optional Malapert example, select (-1600 m east, +100 m north) directly on
  the polar map's Site Neighborhood cells. The separate 2027–2028 check gives 100% of hourly Earth-view
  samples there; the screen's selected window is a different summary. Do not call
  it a summit, permanent visibility or a validated communications link.
- Coordinate a final copy pass with the panel owners: some chart/result sentences
  are still hardcoded outside texts.py, including “the Sun shines X% of the time”.
  Narrate that number as mean Illumination Fraction, not binary sunlight duration.
  Countdown tooltips are not centralized yet; About explains their interpretation.
- Record the final duration and publish the video URL only after reviewing the take.

Scientific references and reproducible comparisons remain in
[illumination_comparison.md](illumination_comparison.md). See also the
[mission explainer](mission_explainer.md), [NASA south-pole background](https://www.nasa.gov/reference/moonbase-environment/)
and [JPL Horizons manual](https://ssd.jpl.nasa.gov/horizons/manual.html).
