# One screen: a JavaScript Moon View under Streamlit panels

The interface is a single Google Earth-style screen. The Moon View fills the page. It is one Streamlit custom
component written in JavaScript, holding the 3D globe or the 2D south polar map, the time bar, the map controls and
the status bar. Streamlit panels float over it: search, catalog, Site Card, Site Planner, layers and about.

The time bar lives in JavaScript because playback has to animate the site markers every frame. A Streamlit widget
would rerun the whole script on every step.

The polar map is Leaflet on NASA Moon Trek south polar stereographic tiles. globe.gl's tile engine uses Web
Mercator, which stops short of the pole, and the whole-Moon texture the globe can load is far too coarse there
(about 2.7 km per pixel).

The JavaScript is split into one file per part (globe, polar map, time bar, controls), and Python joins them, so
two people can work on the view at once. The data going in and the events coming out are listed in
[`docs/UI_OVERHAUL.md`](../UI_OVERHAUL.md).

## Considered Options

- **Two pages (Explorer and Site Planner), as before:** less work, but planning happens away from the Moon and the
  time controls are repeated.
- **Everything in Streamlit (sliders, Plotly maps):** no JavaScript to maintain, but no playback, and Plotly cannot
  tile polar imagery.
- **Globe only, with a hand-made polar texture cap:** one view, but it needs a custom three.js mesh and a camera
  that looks straight down at the pole. Too risky for the deadline.

## Consequences

- The view depends on jsDelivr (globe.gl, Leaflet, proj4) and on Moon Trek tiles. If they fail, the view shows a
  message and the panels keep working.
- Every panel interaction still reruns the script and resends the view's data, including about 190 KB of hourly
  states for the Catalog Sites. The component keeps its own state (camera, view, playback) across reruns.
