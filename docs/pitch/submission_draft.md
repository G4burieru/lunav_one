# Lunav One — submission draft

D3 working draft for NASA Space Apps Challenge 2026, Lunar Landing Site Navigator.
Check the final submission form and the deployed build before publishing. The
application is hosted at [lunavone.streamlit.app](https://lunavone.streamlit.app/);
no award, agency endorsement or operational validation is claimed.

## Project summary

Lunav One is a Python educational prototype for exploring how location, terrain
and time affect sunlight and Earth Visibility near the lunar south pole. A
full-page Moon View combines a three-dimensional Moon and a polar map using real
NASA imagery. A searchable catalog, scientific Site Cards and a four-step Site
Planner help people connect geographic context with transparent model results.

## The problem

Low-angle sunlight and cratered terrain make polar conditions strongly dependent
on position. Seeing the Sun above an Ideal Horizon does not mean it clears a
nearby ridge. A region center is not necessarily a summit or a landing point.
Users need both a readable view of the terrain and a clear explanation of the
numbers, their sources and their limitations. See [NASA's south-pole background](https://www.nasa.gov/reference/moonbase-environment/).

## Current implementation

One screen holds the Moon View, an icon rail and one floating panel. Explorer
starts with name/coordinate search and compact Catalog Site cards, sortable by
Sunlight, Earth Visibility, Longest Night or name. Selecting a polar site opens
the south polar map, while nonpolar locations use the globe. The view streams
LROC imagery and LOLA shaded relief through NASA Moon Trek, with Photos and
Relief base layers on both the globe and the map. The Globe | South pole switch changes views. These images provide context, not live shadows.

A Site Card shows coordinate type, source context and 2027–2028 conditions at
2 m Asset Height: mean Illumination Fraction, Earth Visibility, Longest Night
and Longest Earth Absence. Its rank compares one metric among Catalog Sites,
not safety or mission suitability. An integrated UTC time bar supports dragging,
typed dates and Play/Pause at several speeds. Every Catalog Site marker is a
circle; a badge beside it shows a Sun that fills with the Illumination Fraction
and an Earth that is blue during Earth Visibility. Markers update during playback. Releasing the slider or pausing
synchronizes the Site Card's instant, countdown line and charts; its two-year
summary and ranks remain unchanged. The initial globe rotation stops at the
first interaction and respects reduced-motion preferences.

Overview, Sun & Earth and Seasons tabs show
source details, external site images and descriptions, 28-day elevation charts
and monthly summaries. Photographs, composites and measurement-derived maps are
credited to their providers, not presented as original project results. The old comparison
table has been replaced by the sorted catalog cards and ranks.

Green dashed rings mark prepared neighborhoods; a cyan ring marks the 80°S
terrain boundary. Covered scenarios reuse prepared data; other supported polar
cases compute live. Outside terrain coverage, the Ideal Horizon applies when
no prepared neighborhood is available. Other heights or dates can require live
work within a green ring. These boundaries are separate from site markers.
The Layers panel and NASA visibility overlays were removed.

Plan here opens Where, Surface Asset, When and Results. Users choose a Catalog
Site or Custom Site, Asset Height, Elevation Mask and Analysis Window. Results
include Sunset/Earthset countdowns, equivalent full-Sun hours and Earth-view
percentages. The Moon View time bar follows the Analysis Window and synchronizes
results on slider release, pause or a committed typed date; there is no separate
selected-instant slider in Site Planner. Within pre-computed date coverage,
Catalog Site badges follow that same window at 2 m with the chosen Elevation
Mask; the asset follows its chosen height. Outside coverage, only asset states
are sent and catalog badges are omitted. For Catalog Sites at or south of 80°S and at 2 m Asset Height,
Site Neighborhood cells are drawn directly on the polar map, colored by Sunlight
or Earth Visibility for the chosen window and mask. Clicking a cell moves the
Surface Asset and updates its analysis. Best cell selects the highest modeled
value for the chosen metric; Back to the site restores the catalog position.
Neither selects a certified landing location. For Custom Sites and other heights
at or south of 80°S, Paint the Site Neighborhood starts a live calculation on
demand; external-service availability and waiting time still apply. Custom Sites can also be created from
coordinate search or an analyzed click on the globe/map.

Seventeen Catalog Sites have source references and coordinate meanings, including all 13
historical Artemis III candidate regions NASA named in 2022: Connecting Ridge is
represented by C1/C2, not its regional center. The Leibnitz Beta identifier is
retained as a historical reference associated with the mountain Mons Mouton;
this does not establish retention or polygon equivalence with either 2024 region.
Haworth's 2022/2024 associations are documented. All 17 have
Overviews; the nine new entries use an explicitly labeled regional LROC mosaic.
Four
specific study points come from Gläser et al. (2017); other entries are regional
centers or a historical landing. Pre-computed data covers 2027–2028. Supported
cases outside that coverage use live calculations; an identified Ideal Horizon
fallback applies where terrain is unavailable. The schematic Plotly export in
`src/site_map.py` remains an offline alternative, not the primary visualization.

## NASA inputs and our calculations

JPL Horizons supplies ephemerides. LOLA models supply elevation. Our Python
science modules calculate Terrain Horizons, Illumination Fractions, durations,
Earth Visibility and catalog rankings. NASA imagery is distinct from those
project calculations. NASA's long-term surface-level visibility layers also
have different periods and definitions from our 2 m Site Card figures.

The polar calculation uses 20 m terrain within 10 km, 80 m from 10–50 km and a
320 m overview from 50–150 km. Site Neighborhoods sample a 2 km radius at 100 m
spacing. Lunar mean-Earth frame compatibility has been checked; this does not
constitute a complete terrain, uncertainty or landing-safety assessment.

## Technologies and scientific references

- Python, Streamlit, Plotly, Pandas, Requests, NumPy and Rasterio form the Python
  application and calculation stack; Pytest checks software behavior.
- The Moon View uses JavaScript/WebGL with globe.gl, Leaflet and projection
  libraries loaded from a CDN. Running the application requires no Node.js build.
- [JPL Horizons](https://ssd.jpl.nasa.gov/horizons/manual.html): ephemerides and frame definitions.
- [NASA PGDA / LOLA](https://pgda.gsfc.nasa.gov/products/78): elevation models;
  [polar visibility products](https://pgda.gsfc.nasa.gov/products/69): reference maps.
- [NASA Lunar Surface Data Book, Table A2-2](https://ntrs.nasa.gov/api/citations/20230007818/downloads/ACD-50044%20Lunar%20Surface%20Data%20Book%20Rev%20A.pdf)
  and [Gläser et al. (2017), Table 2](https://ntrs.nasa.gov/api/citations/20170007365/downloads/20170007365.pdf): coordinate provenance.
- [Moon Trek](https://trek.nasa.gov/moon/) and [LROC](https://lroc.im-ldi.com/):
  imagery; [QuickMap](https://quickmap.lroc.im-ldi.com/): cartographic reference.
- [NASA 2022 regional list](https://www.nasa.gov/news-release/nasa-identifies-candidate-regions-for-landing-next-americans-on-moon/),
  [2024 revision](https://www.nasa.gov/news-release/nasa-provides-update-on-artemis-iii-moon-landing-regions/)
  and [Mons Mouton naming](https://svs.gsfc.nasa.gov/5074/): historical regional context.
- [CSA lunar exploration resources](https://www.asc-csa.gc.ca/eng/astronomy/moon-exploration/):
  educational context, not a project partnership.

## Scientific checks and limitations

The [reproducible comparison](illumination_comparison.md) records four solar
study-point means within 1.2 percentage points of Gläser et al.'s Table 2. The
periods differ and both use LOLA-derived terrain, so this is a consistency check,
not independent validation. The document also separates the project's Earth-center
visibility criterion from NASA PGDA's any-part-of-Earth reference-map criterion.
Shared inputs, model assumptions and resolution differences remain relevant.

The Malapert neighborhood example gives 100% of hourly Earth-view samples in
2027–2028 at 1600 m west and 100 m north, 2 m Asset Height and 0° Elevation Mask.
This is a modeled cell, not a verified summit, permanent view or working radio link.

Sunlight is mean visible solar-disk fraction, not electrical power. Longest Night
is not calculated battery autonomy, and Earth Visibility is not operational
communications availability. No safe or optimal landing, ice deposit, energy
yield or thermal survival is certified. Automated tests verify software behavior;
they do not establish scientific accuracy for every real location.

## Intended impact and integration work

The intended benefit is educational: let people inspect terrain, compare clearly
defined environmental metrics and understand uncertainty. User-study or
operational impact has not been measured.

The Site Neighborhood is integrated into the polar map, including explicitly
requested live neighborhoods for Custom Sites and other heights in the supported
polar region. The separate schematic Plotly map remains an offline export.
The Moon View has a working UTC slider, playback and dynamic marker states.

Before recording, consult the [17-site review](catalog_expansion_review.md) and
verify the hosted build, browser/CDN/imagery loading, marker changes and Site Card
synchronization after slider release or pause. Live neighborhood computation
should not be required by the main recording path.

## Publication details

The team will use only the short video as its official demonstration. No slide
presentation is planned; the extended video is complementary GitHub material.

- Application: https://lunavone.streamlit.app/
- Official Demo: at most 30 seconds, pending recording; [script](demo_30s.md).
- Extended Demo: approximately three minutes of complementary material, pending
  recording; [script](demo_script.md). This does not replace the official demo.
- Repository: https://github.com/G4burieru/lunav_one
- Team: Lunav One — João Gabriel Santos (science), Igor Wanderley (interface),
  Renata Andrade (sites, texts and presentation).
- Challenge reference: https://www.spaceappschallenge.org/2026/challenges/lunar-landing-site-navigator/

Confirm the official form's limits and the final deployed feature set before submission.
