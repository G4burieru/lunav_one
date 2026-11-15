# Catalog expansion review — PR #41

Baseline: main `2b55b23`, incorporated into `devel_renata` by fast-forward, without
creating a commit. Validation here means checking published names, regional
coordinates and provenance, not certifying topography or landing suitability.

## Coordinate and identifier checks

The nine additions match NASA's [Lunar Surface Data Book, Revision A, Table A2-2](https://ntrs.nasa.gov/api/citations/20230007818/downloads/ACD-50044%20Lunar%20Surface%20Data%20Book%20Rev%20A.pdf),
printed pages 57–58. All are representative polygon centers, not measured peaks,
rim crests or landing positions. Existing keys and all numerical coordinates
were preserved; longitudes are already east-positive in [-180, 180]. The
[README coordinate table](../../README.md#catalog-provenance-and-conventions)
records the nine coordinates and source identifiers.

| Addition | Table identifier | Printed page | Historical context |
|---|---|---:|---|
| Peak Near Shackleton | R07 / Site07 | 58 | 2022 list |
| Connecting Ridge Extension | SL3 | 58 | 2022 list |
| de Gerlache Rim 1 | R11 / Site11 | 58 | 2022 list |
| de Gerlache Rim 2 | SL2 | 58 | 2022 and 2024 lists |
| de Gerlache-Kocher Massif | R42 / Site42 | 58 | 2022 list |
| Leibnitz Beta Plateau | R20 / Site20 | 58 | 2022 region; no equivalent 2024 polygon established |
| Nobile Rim 1 | R06 / Site06 | 58 | 2022 and 2024 lists |
| Nobile Rim 2 | DM2 | 57 | 2022 and 2024 lists |
| Amundsen Rim | DM1 | 57 | 2022 list |

Historical region lists: [NASA, 19 August 2022](https://www.nasa.gov/news-release/nasa-identifies-candidate-regions-for-landing-next-americans-on-moon/)
and [NASA, 28 October 2024](https://www.nasa.gov/news-release/nasa-provides-update-on-artemis-iii-moon-landing-regions/).
Haworth belongs to **both** lists; its record now documents this rather than only
its DEM origin. The catalog has 12 regional centers, four studied points and
Apollo 11. It represents the 13 historical 2022 regions through those 12 centers
and Connecting Ridge C1/C2; Shackleton S1/S2 are additional study points.

[NASA's naming reference](https://svs.gsfc.nasa.gov/5074/) establishes the informal
Leibnitz Beta / official Mons Mouton correspondence. The old key is retained for
pre-computed file compatibility. NASA lists **Mons Mouton** and **Mons Mouton
Plateau** separately in 2024; an earlier polygon center is not a new boundary
measurement or proof of an identical regional footprint. Its record therefore
uses the 2022 association and links the 2024 revision as context, without the
automatic claim that it was retained. The Overview follows the same distinction.
This update adds no
missing 2024 regions and claims no current mission selection.

Connecting Ridge C1/C2 remain the specific Gläser illumination-study points.
The Data Book's R01/Site01 center is (-89.4632, -137.49); it is not substituted
for either studied point and is not added as an eighteenth entry. Connecting
Ridge Extension (SL3) is a separate region. Full DEM assessment remains pending.

## Nine new Overviews and image verification

All nine additions now have distinct short descriptions, historical context,
coordinate-source links and an image. They reuse **PIA13523** as an explicitly
labeled **regional context mosaic**, not a close-up, exact-coordinate image,
instantaneous shadow map or output of Lunav One.

The [NASA Image and Video Library record](https://images.nasa.gov/details/PIA13523),
its [metadata](https://images-assets.nasa.gov/image/PIA13523/metadata.json) and the
[NASA Photojournal original](https://science.nasa.gov/photojournal/the-lunar-south-pole/)
identify a LROC Wide Angle Camera south polar mosaic. The actual medium JPEG was
visually inspected; its projection/region labeling matches the source. Credit:
**NASA/GSFC/Arizona State University**, retained in every new image caption.
There are no new image providers or downloaded repository assets.

PIA00001, already used by existing entries, was also checked against the
[Library metadata](https://images-assets.nasa.gov/image/PIA00001/metadata.json),
[Photojournal original](https://science.nasa.gov/photojournal/south-pole-region-of-the-moon-as-seen-by-clementine/)
and actual JPEG: a Clementine south polar mosaic with NASA/JPL/USGS credit.
The existing caption remains unchanged. These checks identify regional products;
they do not independently geolocate every catalog center in a thumbnail.
[NASA media guidance](https://www.nasa.gov/nasa-brand-center/images-and-media/)
applies, including credit, third-party rights and no implied endorsement.

## Temporal badge fix

The Explorer already supplied all Catalog Site states. The Site Planner sent
only `asset`, so JavaScript correctly had no state to paint on catalog markers.
The fix is confined to Python payload construction in `common.py` and the
Planner's call to that helper; no JavaScript, layout or scientific calculations
were modified.

For a covered Planner window, every available Catalog Site receives states on
the **same hourly axis**, with the Planner's Elevation Mask and the catalog's
2 m reference height. The Surface Asset uses its chosen height. States retain
meanings from `hourly_states`: solar-disk Illumination Fraction and Earth-center
clearance above the Terrain Horizon plus mask. The selected hour continues to
be decoded and painted by the existing time bar and both views.

No 2027–2028 states are reused for another date window. Outside pre-computed
coverage, the asset's computed states are sent alone, avoiding 17 extra live
requests. Unavailable or misaligned catalog data are omitted rather than
invented. Catalog marker presence does not imply state availability.

## Reproduction and handoff

Run `python -m pytest -q`. The new temporal regression executes the real
JavaScript decoder and globe/polar marker painters when a Node-compatible runtime
is available; otherwise that one test is explicitly skipped. `NODE_BINARY` may
point to an existing compatible runtime without adding project dependencies.
Tests also check real catalog/manifest coordinates, hourly coverage, terrain
files, all Overview entries, source links and the Planner payload integration.
After the Leibnitz historical-association correction, the full suite passed
**125 tests**, including the JavaScript regression using
an existing Node-compatible runtime. `git diff --check` also passed.

No identifier, coordinate, pre-computed file or scientific equation was changed.
No manual regeneration is required for coordinate compatibility; changing
`sites.py` on main may still trigger the team's automatic pre-computation workflow
because metadata and coordinates share that file. No commit or push is part of
this update.

There is no required Igor implementation change: the existing marker painters
already support the corrected data contract. Gabriel can review the small
Python integration change and historical metadata. Before recording, rehearse
the deployed build, including time transitions and a covered 2 m neighborhood.
High illumination and Earth Visibility do not certify landing safety, electrical
power, ice resources or a working communication link.

Files changed in this update:

- Catalog and panels: `src/sites.py`, `src/panels/places.py`,
  `src/panels/common.py`, `src/panels/planner.py`, `src/panels/texts.py`.
- Documentation: `README.md`, `docs/pitch/submission_draft.md`,
  `docs/pitch/demo_script.md`, `docs/pitch/mission_explainer.md`,
  `docs/pitch/final_science_review.md` (historical-status notice), and this report.
- Tests: `tests/test_sites.py`, `tests/test_catalog.py`, `tests/test_panels.py`,
  `tests/test_app.py`, `tests/test_catalog_time.py`.
