# Catalog expansion review — PR #41

> Historical catalog and integration review. The completed product is described
> in the [README](../../README.md) and [technical guide](../technical_guide.md).
> Final documentation and licensing checks are recorded in the
> [release review](../final_release_review.md). The only presentation deliverable
> is the [official short video](demo_30s.md); earlier demo planning is superseded.


Baseline: main `2b55b23`, incorporated into `devel_renata` by fast-forward, without
creating a commit. Validation here means checking published names, regional
coordinates and provenance, not certifying topography or landing suitability.

## Coordinate and identifier checks

The nine additions match NASA's [Lunar Surface Data Book, Revision A, Table A2-2](https://ntrs.nasa.gov/api/citations/20230007818/downloads/ACD-50044%20Lunar%20Surface%20Data%20Book%20Rev%20A.pdf),
printed pages 57–58. All are representative polygon centers, not measured peaks,
rim crests or landing positions. Existing keys and all numerical coordinates
were preserved; longitudes are already east-positive in [-180, 180]. The
[complete coordinate table](../technical_guide.md#catalog-provenance-and-conventions)
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
because metadata and coordinates share that file. The catalog work and scientific
correction were committed in `d77cdc3` and `09cd8a8`; integration status is recorded below.

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
  `docs/pitch/demo_30s.md`, `docs/pitch/mission_explainer.md`,
  `docs/pitch/final_science_review.md` (historical-status notice), and this report.
- Tests: `tests/test_sites.py`, `tests/test_catalog.py`, `tests/test_panels.py`,
  `tests/test_app.py`, `tests/test_catalog_time.py`.


## PR #42 integration check

Main `1e1d7c1` was merged into `devel_renata` based on `09cd8a8`, committed and
pushed as `7373541` — Merge main into devel_renata preserving catalog states and
Custom Site fixes. The only textual conflict was at the end of
`tests/test_app.py`; the Planner-state test and both incoming Custom Site tests
were retained. The Planner's name validation and `planner_time()` coexist.

Igor's saved-location failure tracking, manifest START/END validation and
empty/duplicate-name rejection are preserved. All 17 catalog data sets load for
2027–2028. The 17 Overviews, regional image captions, Leibnitz historical-region
correction were preserved. Presentation planning was subsequently finalized as
one official video of at most 30 seconds, also used in the README.

The integrated suite passed **128 tests, with no failures or skips**, including
the JavaScript badge regression. The Streamlit server started and its health
endpoint returned `ok`; AppTest exercised the main panels and Custom Site flows.
Both working-tree and staged `git diff --check` checks passed. No scientific
calculations, JavaScript or pre-computed files were changed. This integration
is complete and published; it no longer needs a merge commit or push. The final
review below describes subsequent test/documentation corrections, committed and
published as `c8b769f`.


## Final review: CI timeout

[Workflow run 43725870352](https://github.com/G4burieru/lunav_one/actions/runs/43725870352)
checked out main `1e1d7c1`, before Renata's catalog/badge changes were merged. Its
pre-computation step succeeded; the test step reported 112 passes and one timeout
in `test_a_name_typed_just_before_the_click_is_still_checked`. The runner used
Python 3.13.18 and Streamlit 1.67.0.

A guarded reproduction exposed an unintended live calculation. The test saves
Ridge A at Connecting Ridge C1, so the coordinate widgets disappear. Streamlit
cleans up their widget state. Choosing Custom Site again recreates them at the
default (-89.5, 0.0), outside any prepared neighborhood. The reproduction recorded
a Horizons request for that coordinate; if ephemerides succeed, the production
path then calculates a live polar Terrain Horizon via NASA DEMs. The workflow
log does not identify the particular network operation that exceeded its time
budget, so that narrower attribution is not established. It does establish the
120-second AppTest timeout. This is a network-dependent test scenario, not
evidence that `planner_time()` introduced the failure.

The test now seeds the same covered C1 coordinate before recreating the widgets
and checks that those values are retained. Test-only guards fail immediately on
any HTTP request or Rasterio dataset open; rendered science errors are also
rejected. This keeps the real save callback, enabled-button race and checks for
saved-name duplicates, catalog-name duplicates and whitespace-only names. No
production logic or timeout was changed. `with_saved_states()` is not responsible
for this transition: the failure is in Planner results for the newly selected
point. The separate failed-saved-site regression remains in place.

## Team credit provenance

The full names were supplied explicitly by Renata during the project review.
They also match repository commit author records:

- João Gabriel Santos: [commit 2b55b23](https://github.com/G4burieru/lunav_one/commit/2b55b23).
- Igor Wanderley: [commit 1e1d7c1](https://github.com/G4burieru/lunav_one/commit/1e1d7c1).
- Renata Andrade: [commit 7373541](https://github.com/G4burieru/lunav_one/commit/7373541).

These are the approved project credits; commit author records corroborate the
spelling used in the documentation. The short script now states this provenance
explicitly. No surnames were inferred.

## Final review: CI compatibility and validation results

A temporary environment reproduced Python 3.13.18, Streamlit 1.67.0, Pandas
3.1.1, Rasterio 1.5.2 and Pytest 9.2.0 from the failed workflow's logs. No project
dependency, workflow setting or existing virtual environment was changed. The
host operating system and the full pre-computation job were not reproduced;
these checks use the committed catalog data and do not regenerate it.

This exposed a separate branch compatibility issue: Pandas 3 loaded cached
hours as `datetime64[us]` while `date_range` inferred `datetime64[s]`.
`Series.equals()` rejected identical instants because the storage units differed,
so the catalog payload omitted valid states. The first full run in that
environment had 122 passes and six failures, distinct from the original main
workflow's name-test timeout. Both axis checks in `common.py` now compare the
actual ordered timestamps, with the existing length and window checks retained.
No hours, masks, heights, scientific equations or underlying data are changed.
Three regression cases cover seconds, microseconds and nanoseconds.

Final results after both fixes:

| Environment / check | Passed | Failed | Skipped |
|---|---:|---:|---:|
| Existing environment: Python 3.10.12, Streamlit 1.65.0, Pandas 2.3.3, Rasterio 1.4.4 | 131 | 0 | 0 |
| Temporary CI-version environment: Python 3.13.18, Streamlit 1.67.0, Pandas 3.1.1, Rasterio 1.5.2 | 131 | 0 | 0 |
| Previously timing-out test, run alone in the CI-version environment | 1 | 0 | 0 |

Both complete runs included the production JavaScript decoder and marker painters
using an existing Node-compatible runtime. The CI-version Streamlit server also
started successfully and its health endpoint returned `ok`; AppTest rendered
the main panels and exercised saved Custom Sites. `git diff --check` passed.
The 17 catalog/manifest entries and Overviews, source references, imagery,
Leibnitz correction were preserved. The official narration script remains 55 words.
The single official video is now recorded: [lunavone.mp4](../../media/lunavone.mp4),
27.925 seconds, linked from the README.

At that review, remote-reference inspection confirmed main at `1e1d7c1`, fully
included in `devel_renata` at `c8b769f` (zero main commits missing). The branch matches
`origin/devel_renata`. The timeout and Pandas 3 corrections were committed and
published on GitHub in `c8b769f` — fix: keep name validation tests offline and
support Pandas 3 time axes. The results above describe local validation in the
two recorded environments; a passing GitHub Actions result for `c8b769f` has not
been confirmed. Browser rehearsal of the hosted build remains a manual
publication check, not scientific certification; the recorded video's duration
has since been measured at 27.925 seconds.
No other technical blocker was found.
