# Three-minute demo — time-aware Moon View

Draft checked against PRs #28 and #29, present in main 3c9e9fd. Rehearse the
spoken paragraphs at about 130 words per minute, allowing screen transitions.
Bracketed directions and checklists are not narration. Confirm that the
[hosted application](https://lunavone.streamlit.app/) has the same build before recording.

## Prepare before recording

- Start `python -m streamlit run app.py` and let NASA imagery and catalog data load.
- Start in Globe; its slow initial rotation stops on the first interaction and
  stays off. Reduced-motion settings may prevent rotation from starting.
- Rehearse Connecting Ridge C1. Find two instants with visibly different Sun/Earth
  marker states. Record the UTC labels for rehearsal; do not invent a transition.
- Test Play, Pause and dragging. Markers update during playback; release the
  slider or pause to update the Site Card. Its 2027–2028 grid stays fixed.
- Use Plan here with a Catalog Site at 2 m Asset Height, 0° Elevation Mask and a
  covered 14-day window, such as 2027-01-01. Keep the map's pre-computed neighborhood
  as the main demonstration; do not request a live neighborhood or change height.
- Export the offline fallback: `python -m src.site_map --site 'Connecting Ridge C1'`.
  Open `lunar_south_pole.html` in advance. It embeds Plotly but contains neither
  NASA imagery nor the Moon View's time controls or analysis panels.

## 0:00–0:20 — The problem

[Show the globe; begin narration before the first interaction.]

“Near the lunar south pole, the Sun stays low and nearby terrain can hide both
sunlight and Earth. A regional name alone cannot tell us what a surface asset
will see. Lunav One connects geographic context with modeled conditions and
explains what those numbers can, and cannot, tell us.”

## 0:20–0:45 — A documented location on real imagery

[Search for Connecting Ridge C1 and select it. The site opens the polar map.
Show Photos briefly, then the Site Card's coordinate context.]

“The Moon View combines a three-dimensional Moon with a polar map using real
NASA imagery. Selecting Connecting Ridge C1 takes us to a documented study
point. A diamond means a studied point, a circle a regional center, and a square
a historical landing. These shapes identify location types, not landing safety.”

## 0:45–1:30 — Move through time

[Drag the UTC slider and release. Press Play briefly, then Pause. Point to
marker fill, its upper-right dot and the Site Card's updated UTC instant.]

“The time bar lets us move through hourly conditions or play and pause them.
Marker fill follows how much of the Sun's disk clears the terrain. The small
dot is filled when Earth's center is visible and hollow when it is not.
Markers change while time moves. When we release or pause, the Site Card's
instant and charts follow. Its two-year averages stay fixed. Sunlight is mean
Illumination Fraction, not generated electricity. Longest Night and Longest Earth
Absence describe gaps within that window, not battery endurance or guaranteed
communication outages.”

## 1:30–2:15 — Inspect the neighborhood

[Click Plan here. Keep the pre-computed 2 m Catalog Site scenario. Show the
four steps and Color by; select a visible neighborhood cell on the polar map.
Point to the moved Surface Asset and results, then Back to the site.]

“Plan here opens four steps: position, Surface Asset, time window and results.
We keep two metres to use the pre-computed neighborhood. Selecting a cell on
the polar map moves our asset and updates its analysis. Sunlight and Earth
Visibility colors summarize the chosen window. Best cell means highest value
for that metric, not safest landing. Custom Sites and other heights can request
live neighborhoods in the supported polar region, but those calculations take
longer. Here we use prepared data to keep exploration responsive.”

## 2:15–3:00 — What the science supports

[Return to the Site Card or About; end on the Moon View.]

“NASA supplies ephemerides, terrain and imagery; our project calculates horizons,
illumination and visibility metrics. Our four illumination-study points are
within one point two percentage points of published means. That is a consistency
check, not independent validation: both use LOLA data and different time periods.
Hourly sampling, terrain resolution and operational constraints still matter.
We do not certify safe landings, usable power or working radio links. Our goal
is to help people inspect locations, understand assumptions and ask better
questions before a complete mission assessment.”

## Offline replacement

If remote imagery or browser libraries fail, show the exported Plotly map and
say: “This is our schematic offline fallback. It preserves documented locations
without remote services. It does not reproduce the NASA imagery, time playback
or the full application.” Cached scientific panels may still be shown separately.
Do not present a fallback as a recording of an unavailable live interaction.

## Final checks before recording

- Rehearse for approximately three minutes in the actual browser and hosted build.
  Check that Pause/slider release updates the Site Card, while the summary stays fixed.
- Explain a Custom Site's ticked ring and a Surface Asset's cross in a circle
  only if they appear. A triangle denotes an approximate reference; no new entry
  of that kind is required for the demonstration.
- The Planner's Moon View time bar covers its Analysis Window, but its results
  panel still has an independent Instant slider. Do not claim its countdowns
  synchronize with the Moon View bar. Use the panel slider if demonstrating them.
- Neighborhoods are offered at or south of 80°S. Catalog Sites at 2 m reuse prepared
  terrain; other cases require Paint the Site Neighborhood. Keep that slower path
  out of the main take. Best cell is disabled as No better cell when differences
  are below the implementation's threshold; choose another covered window if needed.
- Layers Panel and additional NASA visibility-layer controls are still pending;
  existing Photos/Relief switches are base layers, not those controls.
- Some scientific captions remain hardcoded in other owners' panels; narrate
  Sunlight as mean Illumination Fraction rather than binary sunlight duration.
- If using the optional Malapert example, the point is -1600 m east, +100 m north.
  Its separate two-year Earth Visibility result is not the same as a short-window
  percentage and does not establish a summit or permanent communications.
- Publish the video URL after reviewing the final recording.

Sources and reproducible checks: [illumination comparison](illumination_comparison.md),
[mission explainer](mission_explainer.md), [NASA south-pole background](https://www.nasa.gov/reference/moonbase-environment/)
and [Horizons manual](https://ssd.jpl.nasa.gov/horizons/manual.html).
