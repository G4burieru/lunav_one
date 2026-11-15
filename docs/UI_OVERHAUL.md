# UI Overhaul Plan

Replace the two-page interface with one Google Earth-style screen that is easy to read for the public and still
precise for mission planners. Terms follow [`GLOSSARY.md`](../GLOSSARY.md); the architecture is recorded in
[ADR 0003](adr/0003-one-screen-moon-view.md).

**Deadline:** everything the demo needs is on `main` by **Sunday 16:00 (UTC−3)**, when Renata records the video.
**Feature cut: Sunday 12:00.** Work not merged by then is dropped; 12:00–16:00 is for fixes only.

## Status

- **Done: T0a, T0b, A1, A2, A3 and A4.** The app is one screen with the rail and the panels, and the globe lives in
  `src/moon_view/`. `tests/test_app.py` opens every panel. The `.js` and `.css` files are read on every run, so
  pressing R in the app shows edits without a restart. Adding a file to `_JS_FILES` needs a restart.
- **A2 result:** the south polar map is `src/moon_view/polar_map.js`. It replaces the Plotly south pole map, which
  is gone from `app.py` and `src/charts.py`. Notes for A3 and A5–A8:
  - Every Moon Trek south polar layer uses one tile grid. The projection is
    `+proj=stere +lat_0=-90 +lon_0=0 +k=1 +R=1737400`. Tiles are 256 px with the origin at (−1,095,930 m,
    1,095,930 m), and level 0 is 8,561.95 m per pixel.
  - Photos stacks the WAC mosaic to 60°S (levels 0–4) under the NAC mosaic to 85.5°S (0–11). Relief stacks the LOLA
    color shaded relief to 55°S (0–4), to 75°S (0–6) and to 87.5°S (0–9). The Earth visibility tiles for A8 use the
    same grid, with levels 0–6.
  - The globe/map switch is a button at the top right of the view, before Photos and Relief (the same two base
    layers on both views): it names the other view and switches in JavaScript alone, because the view keeps its
    own choice until `view_id` changes. Choosing a site still switches to the view that shows it: polar sites
    (south of 80°S) open the map and the others open the globe (`view_request` in `app.py`).
  - A click on a marker, or Enter or Space on a focused marker, sends `site`. The map centers the selected site in
    the area to the right of the panel. It centers again when the panel changes width, unless the user has moved
    the map.
- **A4 result:** the globe stops turning for good at the first drag or zoom on it, or at the first click or key
  press anywhere on the page. Key presses count too, so keyboard users can stop the motion. With reduced motion it
  never turns.
- **A3 result:** the time bar is `src/moon_view/time_bar.js`.
  - `app.py` passes `catalog_time()` with the last instant in the Explorer. A panel that returns its own `time`
    replaces it: the Site Planner does, and so does a Custom Site's Site Card, which adds the Custom Site's states
    under `"custom"`.
  - The bar sends `instant` when it is released, when playback pauses, and when a typed date is entered. It reaches
    `st.session_state["moon_view"]` only because `app.py` registers `on_instant`: components v2 keep only the state
    keys that have a callback.
  - Playback speed is chosen with buttons: 1 h/s, 6 h/s (the default), 1 day/s and 3 days/s. The choice is kept
    across reruns and windows. The instant can also be typed in UTC (`YYYY-MM-DD HH:00`, then Enter); an
    unreadable date is outlined in red and put back on Escape or when the field is left.
  - Markers are the same SVG on the globe, where they are HTML elements, and on the map. Catalog Sites are circles,
    and the panels name their coordinate kind. With time data, a badge beside each marker shows the bar's hour: a
    Sun that fills from the bottom with the Illumination Fraction, and an Earth that is blue while in view and gray,
    crossed out, below the horizon. The selected site or the Custom Site has an orange ring and its name. A click
    on a marker never reaches the Moon below it, so it does not open the "Analyze this point?" balloon.
  - In the Site Planner, the Surface Asset (a cross in a circle) carries the `asset` states and is the only marker
    highlighted. The map frames the Site Neighborhood when there is one, and otherwise centers on the Surface Asset.
  - The map's zoom buttons and both scale bars (the map's and the globe's) move up above the time bar when the bar
    would cover them. This happens beside the wide panel on screens under about 1800 px (`liftMapControls` in
    `view.js`).
  - The Explorer's `time` is 183 KB on every rerun. The view decodes it only when it changes, and no lag was
    visible locally.
  - **For B3 (done):** the bar now spans the Site Planner window, so the Planner's own Instant slider can go. Read
    the bar's instant with `selected_instant()`.
- **A1 result:** Leaflet and Proj4Leaflet work inside the component's shadow DOM, so `isolate_styles` stays on. The
  Moon Trek NAC tiles line up with the sites (Shackleton Rim S1 sits on the crater rim), and clicks on a site or on
  the map reach Python. Notes for A2:
  - Add `user-select: none` to the map; otherwise a drag selects the text of the zoom buttons.
  - A fast drag flings the map through Leaflet's inertia.
  - Trigger events last one run, so read them in their callbacks, as `on_view_site` in `app.py` does.
- **Done: C1, C2, C3, B1, B2, B4, and the search half of B5.** The catalog has the search (names and coordinates)
  and the sorted compact cards; the Site Card has the grid, the rank sentence, the selected-instant line and the
  three tabs, for Catalog Sites and Custom Sites. The comparison table is gone; the Plotly south pole map stays until
  A2 replaces it.
- **Done: B3.** The Site Planner has the four steps and the Asset Height presets. A panel's `render()` can return
  keyword arguments for `moon_view`, so `app.py` now fills the view after the panel. The Site Planner returns
  `mode="planner"`, the Surface Asset position as `asset`, and its window's states as `time`. Its results follow
  the Moon View time bar's instant (`selected_instant`), as the Site Card does; the panel's own Instant slider is
  gone.
- **Done: C4** (removed with B7 in PR #33). `python -m scripts.render_overlays` writes the Sunlight overlay for A8, and since A8 also the Earth one:
  - `static/overlays/sun_85s.png` is 1264 × 1264 px at 240 m per pixel, about 1 MB.
  - `sun_85s.json` holds its bounds, ±151740 m in the same polar stereographic CRS as the Moon Trek tiles.
  - In Leaflet: `L.Proj.imageOverlay("app/static/overlays/sun_85s.png", L.bounds([-151740, -151740], [151740,
    151740]), {opacity: 0.7})`.
  - The color ramp (one amber hue, darker means less Sun) is in the JSON for the B7 legend, and the caveat text is
    `texts.SUN_LAYER`.
- **Done: A5 and B5.** A click on the globe or the map, away from a site, shows the "Analyze this point?" balloon
  with a provisional marker (a pulsing ring on the globe, a dashed ring on the map). Analyze sends `point`, and
  `on_view_point` in `app.py` opens the Custom Site's Site Card. The Custom Site is drawn on both views with the key
  `"custom"` (`focusSite()` in `view.js`), the map centers on it, and `view_request` treats it like a site: polar
  points open the map.
- **Done: the rail hides the panel.** A second click on the open panel's icon hides the panel and the next shows it
  again; choosing a site also shows it. The hidden panel is still rendered (`display: none`), so its inputs keep
  their values and the view keeps using what the panel returns.
- **Done: A6 and B6.** In the Site Planner, for a Catalog Site south of 80°S at 2 m, the south polar map paints
  the Site Neighborhood: 100 m cells colored with the sunlight or Earth visibility ramp of `src/colors.py`, the
  best cell outlined in dashes and the Surface Asset's cell in a solid line. A click on a cell sends `cell`, and
  `planner.on_map_cell` moves the Surface Asset there; the panel has a legend and a "Best cell" button, which
  also works from the keyboard. The map frames the whole Site Neighborhood and stays put while the Surface Asset
  moves. The Plotly heatmap (`plot_neighborhood`) is gone. The Site Planner returns `view` and `view_id`
  (`"planner:<site>"`), so the map opens for polar sites and the globe for the others.
- **Site Neighborhood for any polar point:** for a Custom Site, or an Asset Height other than 2 m, the Site Planner
  offers "Paint the Site Neighborhood (computed live, about 30 s)": `live_neighborhood_horizons()` and
  `live_neighborhood_summary()` in `src/conditions.py` build the same grid live. At Connecting Ridge C1 the live
  horizons match the pre-computed ones within 0.005°. When every cell has the same value, no best cell is marked.
- **Busy indicator:** Streamlit's header is transparent instead of hidden, so its Running and Stop indicator shows at
  the top center while a click is processed; without it a slow click looked ignored.
- **Done: A8 and B7, then removed in PR #33:** the panel was neither intuitive nor informative. The rail had a Layers panel with two switches, Sunlight and Earth visibility, each with its
  legend and Renata's explanation (`texts.SUN_LAYER`, `texts.EARTH_LAYER`). The choice lives in
  `st.session_state["overlays"]`, so layers stay on in the other panels, and showing one switches to the map.
  `drawLayers()` in `polar_map.js` stacks three images per layer, finest on top, in a translucent pane between
  the photos and the Site Neighborhood cells: `static/overlays/<name>_65s.png`, `_75s` and `_85s`, at 1920, 960
  and 240 m per pixel, from PGDA's maps to 65°S, 75°S and 85°S, each cut to the disc that ends at its latitude.
  A layer weighs about 2 MB. NASA publishes these maps only from 65°S, so the map's last 5° to 60°S have no layer.
  The map credits NASA PGDA while a layer is shown. The images come from `python -m scripts.render_overlays`, with
  the ramps of `src/colors.py` (the Earth one replaces NASA's colored tiles, so both layers read the same way).
- **Stale modules after a deploy:** Streamlit drops changed modules only for the browser sessions that saw the
  change, and Streamlit Cloud updates the code without restarting Python, so new sessions could mix a new
  `app.py` with old `src` modules (the ImportError after PR #24). `app.py` now drops every `src` module when a
  `src/*.py` file changed since they were imported.
- **For A7:** while the panel is hidden, the globe/map switch at its top is out of reach, so the in-view switch
  matters.

## Decisions

### Audience and accessibility

- The Explorer speaks to the public: plain language, few numbers, and every number comes with a sentence that says
  whether it is good or bad. The Site Planner speaks to mission planners.
- Accessibility baseline: WCAG AA contrast, everything usable by keyboard, never color alone (add shape or text),
  one sentence summarizing each chart, and no automatic motion when the system asks for reduced motion.
- Desktop first. On phones the panel stacks under the view, as today.

### Screen

- One screen. The Moon View (globe or south polar map) fills the page and one floating panel sits on the left. The
  top navigation bar goes away; Explorer and Site Planner stay as modes, shown as panels instead of pages.
- A rail of icons on the left opens the panels: Catalog, Plan, Layers, About. Search sits at the top of the panel.
  A second click on the open panel's icon hides the panel, leaving the whole Moon in view.
- No welcome pop-up. The first screen shows the search, a two-sentence introduction and the catalog cards.
- No emojis. Icons are SVG files in `static/icons/`, served by Streamlit (`server.enableStaticServing`, which the
  Sunlight overlay also needs) and placed in text with `icon(name)` from `src/panels/common.py`. Buttons keep
  Streamlit's Material Symbols.
- The globe rotates slowly when the app opens and stops for good at the first interaction: dragging or zooming the
  globe, or any click on the page. It never rotates when the system asks for reduced motion.

### Views

- **Globe:** the 3D Moon (globe.gl, as today) for the whole Moon and Apollo 11.
- **South polar map:** Leaflet on NASA Moon Trek south polar stereographic tiles, with two base layers:
  - Photos: LROC NAC average mosaic, about 4 m per pixel up to 85.5°S, over the WAC polar mosaic.
  - Relief: LOLA color shaded relief, about 17 m per pixel up to 87.5°S and coarser beyond.
- Choosing a polar site (catalog, search or globe) switches to the map centered on it.
- The Plotly south pole map leaves the Explorer; `src/site_map.py` stays as the offline export.

### Catalog and Site Card

- Catalog cards show the kind of location (◆ studied point, ● region center, ■ historical landing), the name, and
  the two averages over 2027–2028: sunlight and Earth visibility. The list sorts by sunlight, Earth visibility,
  Longest Night or name, and replaces the comparison table.
- The Site Card shows the kind, name, coordinates and description, then a grid over 2027–2028 at 2 m Asset Height:

  | | On average | Worst case |
  |---|---|---|
  | Sun | % of time (mean illumination fraction) | Longest Night |
  | Earth | % of time visible | Longest Earth Absence |

- Below the grid:
  - one sentence placing the site among the catalog ("2nd most sunlit of 8");
  - a line for the selected instant ("Sun up · Earth below the horizon · sunset in 3 d 4 h");
  - a "Plan here" button.
- Three tabs:
  - Overview: description, plus scientific and exploration context and sources (collapsed).
  - Sun & Earth: the two elevation charts for 28 days around the selected instant, one summary sentence per chart,
    and "Without terrain, sunlight would be X%".
  - Seasons: the monthly chart.

Reference values for checking the metrics and writing texts (2027–2028, 2 m, Earth's center, 0° Elevation Mask):

| Site | Sunlight | Longest Night | Earth visibility | Longest Earth Absence |
|---|---|---|---|---|
| Shackleton Rim S1 | 85.9% | 2.8 d | 50.0% | 14.7 d |
| Connecting Ridge C1 | 88.3% | 4.6 d | 54.3% | 13.3 d |
| Connecting Ridge C2 | 79.0% | 6.8 d | 55.2% | 13.1 d |
| Shackleton Rim S2 | 81.0% | 3.5 d | 52.9% | 13.9 d |
| Malapert Massif (region center) | 15.4% | 146.6 d | 48.9% | 14.8 d |
| Faustini Rim A | 26.3% | 27.7 d | 47.4% | 15.2 d |
| Haworth | 12.6% | 117.1 d | 40.3% | 17.0 d |
| Apollo 11 | 49.7% | 14.8 d | 100% | 0 d |

### Time

- **Explorer:** the time bar spans 2027–2028 (pre-computed, instant) and has play. The Site Card grid always covers
  the full two years and does not move with the bar. The markers, the selected-instant line and the Sun & Earth
  charts follow the bar.
- **Site Planner:** start date and duration, any date (computed live outside 2027–2028). While the Planner is open,
  the time bar spans its Analysis Window. The bar's instant drives the countdowns and the chart marker, replacing
  today's Instant slider.

### Site Planner

The Planner opens from "Plan here" on a Site Card or from an analyzed point. It has four steps:

1. **Where:** the Catalog Site or Custom Site.
2. **Surface Asset:** Asset Height presets and an Elevation Mask with a short explanation.
   - "Rover or lander, 2 m": instant.
   - "Mast, 10 m": computed live, about 30 s.
   - "Other height".
3. **When:** start date and duration.
4. **Results:** countdowns and percentages, each with a sentence, and the two charts.

For a Catalog Site at 2 m, the Site Neighborhood is painted on the polar map: 100 m cells within 2 km, colored by
sunlight or Earth visibility in the Planner's window. Clicking a cell moves the Surface Asset there. The Plotly
heatmap stays until the map overlay works.

### Custom Site

- **Creation:** from the search ("-89.44, -137.17"), or by clicking the globe or the map outside a site. Search needs
  no confirmation.
- **Click confirmation:** a click first shows a provisional marker with a balloon, "Analyze this point? −88.50°,
  60.00° · computed live, about 30 s", or "no terrain data here" outside 80°S, with Analyze and Cancel buttons.
  Nothing runs in Python before Analyze.
- **Site Card:** the same card as a Catalog Site, computed live for 2027–2028, with the rank sentence ("would be 3rd
  most sunlit of 8") and the time bar. Outside 80°S the card says the Ideal Horizon is used.
- **Measured time:** about 25 s at −88.5°, 60° (Horizons 6 s, terrain 16 s). It can reach about 2.5 min when PGDA
  needs retries.

### Layers

- **Overlays on the polar map:**
  - Earth visibility: NASA PGDA, the ready Moon Trek tiles `ClrAVGVISIB_85S_060M_201608_EARTH_SP`, which agree
    with our validation within 1–5 points.
  - Sunlight: the NASA PGDA average Sun visibility map, which we render to an image.
- **Sunlight legend:** "Ground level, 18.6-year average. Site figures are 2 m above ground and differ: at
  Connecting Ridge C1 this map gives 44%, the Site Card 88%."
- **No permanently shadowed regions layer:** the only tiled version is about 1 km per pixel.

### Bars and controls

- Search at the top of the panel and the icon rail on the left.
- Time bar at the bottom: slider, play and pause, and the UTC instant.
- Controls at the bottom right: zoom, South pole, globe or map, full screen.
- Status bar: cursor coordinates and the credits of the visible layers.

### External services

The Moon View loads globe.gl, Leaflet and proj4 from jsDelivr and tiles from Moon Trek, with no vendored copies.
If any of them fail, the view shows a clear message and the panels keep working. Renata's offline map is the video
fallback.

### Out of scope

Shareable links, IAU feature names in search, a guided tour, a permanently shadowed regions layer, and Explorer
dates outside 2027–2028.

## Architecture and contract

```
app.py                   shell: page config, CSS, rail, panel routing, Moon View mount
src/panels/
  common.py              shared helpers (site_label, kind labels, load, format_countdown)
  catalog_list.py        search and catalog cards
  site_card.py           Site Card and its tabs
  planner.py             Site Planner panel
  layers.py              overlay switches and legends
  about.py               About panel
  texts.py               user-facing explanatory text (Renata)
src/moon_view/
  __init__.py            moon_view(): builds the data, registers the component, joins the files below
  view.js                entry point: shared state, events, view switching
  globe.js               3D globe
  polar_map.js           Leaflet south polar map
  time_bar.js            time bar, playback, marker states
  controls.js            zoom, South pole, globe/map, full screen, status bar
  view.css
```

Python to Moon View (`data`):

| Key | Content |
|---|---|
| `mode` | `"explorer"` or `"planner"` |
| `view`, `view_id` | `"globe"` or `"map"`, applied only when `view_id` changes so the user's own switch survives reruns |
| `sites` | `[{key, name, lat, lon, kind, description}]` |
| `selected` | Catalog Site key or `null` |
| `custom`, `asset` | `{lat, lon}` or `null`: the Custom Site, and the Surface Asset position in the Planner |
| `saved` | `[{key, name, lat, lon}]`: Custom Sites named in the Site Planner (keys `saved:<name>`), drawn as violet diamonds with their names; kept in session state until the page is reloaded. A click on one sends its key as `site` and opens the Site Planner on it |
| `time` | `{start, hours, instant, states: {key: base64}}`; one byte per hour: bits 0–6 illumination fraction × 100, bit 7 Earth visible |
| `zones` | `{terrain_lat, precomputed_m, precomputed: [keys]}`: where a clicked point's analysis comes from, drawn as dashed rings on the map |
| `neighborhood` | `null` or `{site, center: {lat, lon}, reach_m, label, selected, best, cells: [{corners: [[lat, lon] × 4], value, color}]}` |

Moon View to Python:

| Event | Kind | Value |
|---|---|---|
| `site` | trigger | key of a clicked site, or `""` for a click beside the sites (clears the selection) or a right-click on the Moon (also leaves the Site Planner for the catalog) |
| `point` | trigger | `{lat, lon}` after Analyze |
| `cell` | trigger | index of a clicked Site Neighborhood cell |
| `instant` | state | ISO time, sent when the bar is released or paused |

The panels share `st.session_state` keys `panel` (`catalog`, `site`, `planner`, `about`), `selected` and
`custom`.

## Tasks

Sizes are rough hours. "Needs" lists what must be merged first; everything else can run in parallel. Suggested
owners follow file ownership; swap freely.

### Step 0: foundation

| ID | Pri | Task | Size | Needs | Suggested |
|---|---|---|---|---|---|
| T0a | P1 | Create `src/moon_view/` with today's globe moved in, no behavior change. Accept the whole `data` contract (ignore keys not used yet). Delete `src/globe.py`. | 1.5 | — | Igor |
| T0b | P1 | Split `app.py` into the shell and `src/panels/`, moving today's content. Remove the top navigation, add the rail (Catalog, Plan, About), create `texts.py` with placeholder text, and update the ownership table in `docs/TEAM_PLAN.md`. | 2 | — | Gabriel |

T0a and T0b run in parallel. They share one import line in `app.py`; merge T0a first.

### Lane A: Moon View (JavaScript)

| ID | Pri | Task | Size | Needs |
|---|---|---|---|---|
| A1 | P1 | Spike: Leaflet and Proj4Leaflet showing the Moon Trek NAC layer inside the component, with a click that returns lat/lon. Decide `isolate_styles` (shadow DOM). | 0.5–1 | T0a |
| A2 | P1 | Polar map: Photos and Relief base layers with an in-view switch; site markers (shape by kind, selected highlighted, name tooltips); the `site` event; switching between globe and map through `view` and `view_id`; a selected polar site centers the map. | 3–4 | A1 |
| A3 | P1 | Time bar: slider, play and pause, UTC label; decode `time.states`; marker states on globe and map (Sun full, partial or dark; Earth visible or hidden; shape as well as color); `instant` on release or pause. | 3 | T0a (fake states until C3) |
| A4 | P1 | Globe auto-rotation: on at start, off for good at the first interaction, never with reduced motion. | 0.5 | T0a |
| A5 | P2 | Click to analyze a point: provisional marker and confirmation balloon on globe and map; `point` event on Analyze. | 1.5 | A2 |
| A6 | P2 | Site Neighborhood overlay: colored 100 m cells with a legend, the `cell` event, selected and best (★) cells marked. | 2 | A2 |
| A7 | P2 | Controls (zoom, South pole, globe or map, full screen) and status bar (cursor lat/lon, credits). | 1.5 | A2 |
| A8 | P3 | Overlays: Earth visibility tiles, and the Sunlight image from C4. | 1 | A2; C4 for Sunlight |

A2, A3 and A4 live in separate files and can run in parallel. A3 draws globe markers first and map markers once A2 is
merged. A1 then A2 is the critical path: start the spike as early as possible.

### Lane B: panels (Streamlit)

| ID | Pri | Task | Size | Needs |
|---|---|---|---|---|
| B1 | P1 | Catalog panel: search (catalog names; coordinates create a Custom Site, via `st.selectbox(accept_new_options=True)`), intro text, compact cards with kind and the two averages, sort control. | 1.5 | T0b; C2 (placeholder numbers until then) |
| B2 | P1 | Site Card: header, grid, rank sentence, selected-instant line, "Plan here", tabs with chart summary sentences. Delete the comparison table (`catalog_comparison`). | 2.5 | T0b, C1, C2 |
| B3 | P1 | Site Planner panel: four steps, Asset Height presets, Elevation Mask, window; time bar on the Planner window with states for the Surface Asset; results with sentences. Keeps the Plotly neighborhood heatmap for now. | 2 | T0b, C3 |
| B4 | P1 | About panel showing `texts.ABOUT`. | 0.5 | T0b |
| B5 | P2 | Custom Site flow from the search and the `point` event: live computation with a progress message and cache; Site Card with "would be Nth of 8" and the terrain warning outside 80°S; its time bar states. | 1.5 | B2; A5 for clicks |
| B6 | P2 | Site Neighborhood through the map: send the cells, handle `cell`, then delete `plot_neighborhood` and the Plotly heatmap. | 1 | A6, B3 |
| B7 | P3 | Layers panel: overlay switches with legends, including the Sunlight caveat from `texts.py`. | 0.5 | A8 |

B1, B3 and B4 can run in parallel after T0b. B2 can start with placeholder numbers before C1 and C2 are merged.

### Lane C: data and metrics (Python)

| ID | Pri | Task | Size | Needs |
|---|---|---|---|---|
| C1 | P1 | In `src/metrics.py`: `longest_night(df)`, `longest_earth_absence(df, elevation_mask=0.0)` (hours) and `site_summary(df, elevation_mask=0.0)` (the four grid values), with tests. Add them to the interface contracts in `docs/TEAM_PLAN.md`. | 1 | — |
| C2 | P1 | Summaries and ranks over 2027–2028 for every Catalog Site, cached in the app. Pre-compute them into `data/catalog/` only if a cold start takes more than about 5 s. | 0.5–1 | C1 |
| C3 | P1 | Encode a conditions DataFrame into time bar states (one byte per hour), with a round-trip test. | 1 | — |
| C4 | P3 | Render the PGDA average Sun visibility map to a transparent color image (about 240 m per pixel) with its polar stereographic bounds, served as a static file (`static/`, `enableStaticServing` in `.streamlit/config.toml`). | 1.5 | — |

C1, C3 and C4 need nothing and can start right away, even before Step 0.

### Lane D: texts and video (Renata)

| ID | Pri | Task | Size | Needs |
|---|---|---|---|---|
| D1 | P1 | `src/panels/texts.py`: the two-sentence intro; About (what the app is, how to read each number, sources and credits, limitations); one sentence per number (sunlight, Earth visibility, Longest Night, Longest Earth Absence, countdowns, Asset Height presets, Elevation Mask); layer legends, including the Sunlight caveat. | 2 | T0b (drafting can start now) |
| D2 | P1 | Rewrite `docs/pitch/demo_script.md` for the new screen. | 1.5 | this plan; final pass after the cut |
| D3 | P1 | Update `README.md` and `docs/pitch/submission_draft.md`: the schematic south pole map and the comparison table are gone, and the new features need describing. | 1 | after the cut |

## Schedule

| When (UTC−3) | Milestone |
|---|---|
| Saturday evening | T0a and T0b merged, A1 spike done, C1 and C3 merged. |
| Saturday night | A2, A4, B1, B2 and C2 merged; Lane D drafting. |
| Sunday 08:00–12:00 | A3, B3 and B4, then P2 and P3 in priority order. |
| Sunday 12:00 | Feature cut. |
| Sunday 12:00–15:00 | Fixes, Streamlit Cloud check, final D2 and D3. |
| Sunday 15:00–16:00 | Rehearse the demo path. |
| Sunday 16:00 | Recording. |

## Every pull request

- `pytest` passes, and `streamlit run app.py` works along the demo path:
  1. Select Connecting Ridge C1.
  2. Play the time bar.
  3. Open the Site Planner at Malapert Massif.
  4. Pick the cell 1600 m west and 100 m north.
- `main` stays demo-ready after every merge. Keep pull requests small and merge often.
- No new Python dependency; `requirements.txt` stays as it is. Browser libraries come from the CDN.
- After the merge, open https://lunavone.streamlit.app/. If it shows an error that `main` does not have locally,
  reboot it: Manage app (lower right) → ⋮ → Reboot app.
- New non-trivial logic (metrics, search parsing, state encoding) gets a test.

## Risks

| Risk | Mitigation |
|---|---|
| Leaflet misbehaves in the component's shadow DOM. | Resolved: A1 showed it works. |
| Time bar states (about 190 KB for all sites) slow every rerun. | Measure after A3; if needed, send them only when they change, or as a static file. |
| PGDA retries make a Custom Site take about 2.5 min. | Progress message; Custom Sites are P2. |
| CDN or Moon Trek outage during the recording. | Error message in the view; Renata's offline map. |
| Two people editing `app.py`. | After T0b it is a thin shell; announce any change to it. |
