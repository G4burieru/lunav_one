# Three-minute demo — time-aware Moon View

Draft checked against main through PR #37 (03c026f). Rehearse the
spoken paragraphs at about 130 words per minute, allowing screen transitions.
Bracketed directions and checklists are not narration. Confirm that the
[hosted application](https://lunavone.streamlit.app/) has the same build before recording.

## Prepare before recording

- Start `python -m streamlit run app.py` and let NASA imagery and catalog data load.
- Start in Globe; its slow initial rotation stops on the first interaction and
  stays off. Reduced-motion settings may prevent rotation from starting.
- Rehearse Connecting Ridge C1. Find two instants with visibly different Sun/Earth
  marker states. Record the UTC labels for rehearsal; do not invent a transition.
- Test typed UTC dates, playback speeds, Play, Pause and dragging. Markers update during playback; release the
  slider or pause to update the Site Card. Its 2027–2028 summary stays fixed.
- Use Plan here with a Catalog Site at 2 m Asset Height, 0° Elevation Mask and a
  covered 14-day window, such as 2027-01-01. Keep the map's pre-computed neighborhood
  as the main demonstration; do not request a live neighborhood or change height.
- Export the offline fallback: `python -m src.site_map --site 'Connecting Ridge C1'`.
  Open `lunar_south_pole.html` in advance. It embeds Plotly but contains neither
  NASA imagery nor the Moon View's time controls or analysis panels.

## 0:00–0:20 — The problem

[Show the globe; begin narration before the first interaction.]

“Near the lunar south pole, the Sun stays low and nearby terrain can hide both
sunlight and Earth. Lunav One connects geographic context with modeled conditions and their limits.”

## 0:20–0:45 — A documented location on real imagery

[Search for Connecting Ridge C1 and select it. The site opens the polar map.
Indicate the Globe | South pole switch and Photos/Relief. Briefly show the
Overview context and the LRO south pole mosaic (NASA Image Library).
The Apollo 15 Malapert photo is no longer in the app.]

“The Moon View combines a three-dimensional Moon with a polar map using real
NASA imagery. We can switch views here. Connecting Ridge C1 is a documented
study point; Overview supplies sourced images and context. Every Catalog Site is a circle; the card distinguishes studied points, regional
centers and historical landings, not landing safety.”

## 0:45–1:30 — Move through time

[Drag the UTC slider and release. Choose a playback speed, press Play briefly, then Pause. Point to
the Sun and Earth badge beside the markers and the Site Card's updated UTC instant.]

“Type a UTC date, move the hourly slider or choose a playback speed.
Beside each marker, the Sun fills as more of its disk clears the terrain, and
the Earth is blue when visible, gray and crossed out otherwise.
Markers change while time moves. When we release or pause, the Site Card's
instant and charts follow. Its two-year averages stay fixed. Sunlight is mean
Illumination Fraction, not generated electricity. Longest Night and Longest Earth Absence describe gaps, not battery endurance
or guaranteed communication outages.”

## 1:30–2:15 — Inspect the neighborhood

[Click Plan here. Keep the pre-computed 2 m Catalog Site scenario. Show the
four steps and the Color by control; keep the polar map visible.
Indicate the green coverage ring. Release the time bar to show Planner following
it. Select a cell, show the moved asset and results, then Back to the site.]

“Plan here opens four steps: position, Surface Asset, time window and results.
Green dashed rings mark prepared neighborhoods; cyan marks polar terrain coverage.
Outside coverage without prepared data, the model uses an Ideal Horizon.
We keep two metres and prepared data; the same time bar drives Planner results. Selecting a cell on
the polar map moves our asset and updates its analysis. Sunlight and Earth
Visibility colors summarize the chosen window. Best cell means highest value
for that metric, not safest landing. Custom Sites and other heights can request slower live neighborhoods in the
supported polar region.”

## 2:15–3:00 — What the science supports

[Return to the Site Card or About; end on the Moon View.]

“NASA supplies ephemerides, terrain and imagery; our project calculates horizons,
illumination and visibility metrics. Our four illumination-study points are
within one point two percentage points of published means. That is a consistency
check, not independent validation: both use LOLA data and different time periods.
Hourly sampling and terrain resolution still matter. We do not certify safe
landings, usable power or working radio links. Our goal is to help people inspect
locations and understand assumptions before a complete mission assessment.”

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
  only if they appear.
- The Planner's Moon View time bar covers its Analysis Window and drives its
  countdowns like the Site Card's: release the slider or pause before pointing to them.
- Neighborhoods are offered at or south of 80°S. Catalog Sites at 2 m reuse prepared
  terrain; other cases require Paint the Site Neighborhood. Keep that slower path
  out of the main take. Best cell is disabled as No better cell when differences
  are below the implementation's threshold; choose another covered window if needed.
- Some scientific captions remain hardcoded in other owners' panels; narrate
  Sunlight as mean Illumination Fraction rather than binary sunlight duration.
- If using the optional Malapert example, the point is -1600 m east, +100 m north.
  Its separate two-year Earth Visibility result is not the same as a short-window
  percentage and does not establish a summit or permanent communications.
- Resolve the [image/caption findings](final_science_review.md) with Gabriel.
- Publish the video URL after reviewing the final recording.

Sources and reproducible checks: [illumination comparison](illumination_comparison.md),
[mission explainer](mission_explainer.md), [NASA south-pole background](https://www.nasa.gov/reference/moonbase-environment/)
and [Horizons manual](https://ssd.jpl.nasa.gov/horizons/manual.html).
