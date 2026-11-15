# Final science and image review — through PR #37

Historical review against main `03c026f`. The science-copy corrections and image
replacements were subsequently integrated in PR #39; the old image inventory
below records the reviewed version, not the current NASA-Library-only collection.
For the 17-site catalog and current additions, see the
[catalog expansion review](catalog_expansion_review.md).

The original review and proposed handoff to Gabriel follows;
`src/panels/places.py` has not been changed. No new Catalog Sites or numerical
results are introduced. Metadata checks are distinguished from visual verification.

## Scientific findings and proposed corrections

| Item | Finding | Suggested change for Gabriel |
|---|---|---|
| Shackleton dimensions and pole | About 20 km is appropriate (roughly 21 km in the LOLA study); the pole lies on its rim. | Retain approximate diameter and rim wording. |
| Shackleton 22% ice | The 2012 result interprets near-infrared LOLA laser reflectance. It is consistent with up to about 22% surface ice in a very thin surface layer, not a measured bulk ice inventory. Brightness can also reflect regolith properties; brighter walls were attributed to exposed material. | Describe a possible interpretation, its method and shallow sampling; do not imply a confirmed resource. |
| Connecting Ridge | LROC identifies a ridge between Shackleton and de Gerlache. Favorable illumination is supported for specific elevated points, not every position on the ridge. | Retain geography; say studied points have high modeled illumination over specified periods, without permanent sunlight. |
| Malapert coordinates | The catalog explicitly uses NASA's regional center. The Overview description does not make this distinction explicit. | Add: “This Catalog Site marks a regional study center, not a verified summit.” |
| Apollo 15 Malapert identification | AS15-96-13090 exists, but the Flight Journal describes a south-pole-directed view including Vallis Schrödinger, Jenner and Lyot; it does not substantiate the precise Malapert identification or pole position in the caption. A filename is insufficient evidence. | Withhold that specific identification pending a registered/annotated original. Prefer the separately identified LROC near-summit image for recording. This review has not proved Malapert absent from the frame. |
| Faustini diameter | Approximately 40 km is reasonable; USGS lists 42.48 km. | Retain approximation. |
| Haworth diameter | Approximately 50 km agrees with the LRO-based 51.42 km entry and the scientific study's 51.4 km. The USGS page also retains an older 35 km control-network entry. | Retain approximation; cite the LRO-based measurement rather than mixing control networks. |
| Shadowed floors | Published maps and research establish permanently shadowed regions in these craters. They do not justify treating every part of each floor or the entire crater as permanently dark. | Replace “its floor never sees the Sun” with “parts of its interior are permanently shadowed.” Water ice may be preserved in sufficiently cold traps; this does not establish ice at the catalog coordinate. |
| Malapert regolith patterns | LROC describes downslope creep as an interpretation of the patterns, not a demonstrated mechanism at every feature. | Use “patterns thought to result from slow downslope movement of regolith.” |

Sources: [LOLA study team explanation](https://news.mit.edu/2012/shackletons-crater-0620),
[Shackleton illumination map](https://lroc.im-ldi.com/images/271),
[ridge geomorphology](https://lroc.im-ldi.com/images/1247),
[Gläser et al., Table 2](https://ntrs.nasa.gov/api/citations/20170007365/downloads/20170007365.pdf),
[Apollo 15 Flight Journal](https://apollojournals.org/afj/ap15fj/21b-day10_tei.html),
[USGS Faustini](https://planetarynames.wr.usgs.gov/Feature/1919),
[USGS Haworth](https://planetarynames.wr.usgs.gov/Feature/14502),
[polar crater study](https://agupubs.onlinelibrary.wiley.com/doi/full/10.1029/2011JE003913),
[LROC Malapert close-up](https://lroc.im-ldi.com/images/21).

Suggested Shackleton copy (not applied):

> Shackleton is about 21 km wide, with the lunar south pole on its rim. Parts of
> its interior remain in permanent shadow. A 2012 analysis of LOLA laser
> reflectance was consistent with up to about 22% ice in a very thin surface
> layer, but this indirect interpretation does not establish an accessible ice
> deposit. Selected rim points receive sunlight for much of the studied period.

## Image-by-image audit

Nine unique URLs are reused across eight Site Cards. Renata confirmed that the
image files open normally in her browser. This confirms access, not the scientific
identification of every feature or the completeness of each attribution. Source
and metadata checks below are distinguished from visual verification; this review
does not claim that all images were visually inspected by the reviewer.

| File/product in places.py | Type and identity | Credit, reuse and action |
|---|---|---|
| [Mosaic_shackleton_crater.jpg](https://commons.wikimedia.org/wiki/File:Mosaic_shackleton_crater.jpg) | Composite of LROC sunlit terrain and ShadowCam shadowed interior; [NASA original](https://www.nasa.gov/missions/lro/nasa-moon-camera-mosaic-sheds-light-on-lunar-south-pole/) matches the subject. Not a single exposure or live shadow state. | Preserve LROC/ShadowCam teams and NASA/KARI/ASU credit. Commons labels it public domain; verify joint-source conditions with the original rather than generalizing from NASA ownership. |
| [South Pole Illumination Map (LROC271)](https://commons.wikimedia.org/wiki/File:South_Pole_Illumination_Map_(LROC271).png) | Measurement-derived illumination-frequency map from stacked LROC images, not a photograph. [Original](https://lroc.im-ldi.com/images/271) supports Shackleton and the pole position in this particular map. Its sampling is not the project's 2027–2028 2 m calculation. | NASA/GSFC/ASU. Commons has a NASA public-domain tag, but LROC featured-image terms require the distinction below. |
| [Traversing the Shackleton de Gerlache Ridge map](https://commons.wikimedia.org/wiki/File:Traversing_the_Shackleton_de_Gerlache_Ridge_(LROC1247_-_content_geomap_snippet).png) | Geomorphic interpretation using NAC imagery **and LOLA topography**, confirmed by [original](https://lroc.im-ldi.com/images/1247). | NASA/GSFC/ASU. Add terrain-data provenance to the caption. Commons public-domain tag does not remove the need to check the original's terms. |
| [AS15-96-13090_Malapert_mountain.jpg](https://commons.wikimedia.org/wiki/File:AS15-96-13090_Malapert_mountain.jpg) | Apollo photograph exists; precise terrain identification remains unresolved as explained above. | NASA mission image; exact rendition's attribution/licensing was not independently verified. Do not use the specific Malapert caption before review. |
| [Near the Summit of Malapert Mountain (LROC21)](https://commons.wikimedia.org/wiki/File:Near_the_Summit_of_Malapert_Mountain_(LROC21).png) | Identified LROC close-up, 2.4 km wide, north up; [original](https://lroc.im-ldi.com/images/21) supports these details. Not the catalog center or an image of its exact summit coordinate. | NASA/GSFC/ASU; use qualified language for inferred creep. Check the rendition’s stated license against the original; LROC permits educational reuse of website images with credit. |
| [FaustiniCrater.jpg](https://commons.wikimedia.org/wiki/File:FaustiniCrater.jpg) | Commons associates the crater image with [USGS feature 1919](https://planetarynames.wr.usgs.gov/Feature/1919). The exact original product/frame still needs to be documented; this review does not establish independent geolocation. | Commons lists NASA/public-domain status. Recover the original image product and full instrument credit before treating “LRO” as verified provenance for this rendition. |
| [Lunar_south_pole_summer_annotated.jpg](https://commons.wikimedia.org/wiki/File:Lunar_south_pole_summer_annotated.jpg) | Measurement-derived Diviner surface-temperature map for southern summer noon, not a photograph or ice-detection image. The original Diviner product identifier and credit still need to be documented. [Instrument science](https://www.diviner.ucla.edu/science) supports the measurement type. | Commons lists NASA/public-domain status; retrieve original Diviner credit and color scale. Prefer “colors encode surface temperature” until the actual scale is checked; do not assume darker always means colder. |
| [as11-40-5927](https://images.nasa.gov/details/as11-40-5927) | NASA asset downloaded and visually checked: Aldrin beside Eagle, photographed by Armstrong. [NASA mission context](https://nssdc.gsfc.nasa.gov/planetary/lunar/apollo11.html). | NASA credit; apply NASA media guidance, including identifiable-person and endorsement restrictions. |
| [PIA12909](https://science.nasa.gov/photojournal/apollo-11-second-look/) | NASA asset downloaded and visually checked: annotated LROC view of Apollo 11 hardware/tracks, 2009. | Expand “NASA” to NASA/GSFC/Arizona State University as specified by the original. |

### Reuse correction requiring Gabriel's review

The module's blanket statement that every image is public domain should be
replaced by per-product provenance and reuse information. Current
[LROC terms](https://lroc.im-ldi.com/about/terms) distinguish public-domain PDS
products from copyrighted website/featured images. Educational reuse of the
latter is permitted with NASA/GSFC/Arizona State University attribution;
commercial reuse requires permission. A Commons public-domain tag can conflict
with the source's stated terms and should not be treated as conclusive.
[NASA media guidance](https://www.nasa.gov/nasa-brand-center/images-and-media/)
also excludes third-party rights from any blanket permission. No agency
endorsement should be implied. This review does not certify legal clearance.

Before publication, retain source URLs and exact credit lines, match the
renditions to documented original products, and resolve the Apollo 15, Faustini
provenance and Diviner scale/credit gaps. Do not present the current external-image collection as completely verified.

## Text/code correspondence and recording handoff

Confirmed in current code: Catalog Sites are circles; Custom Sites are ticked
rings; the Surface Asset uses a cross in a circle. The Sun/Earth badge represents
modeled hourly states. The Sun fills from the bottom; Earth is blue when visible
and gray/crossed otherwise. The time bar accepts typed UTC dates, rounds to an
available hour and clamps to its window, with playback speeds from 1 hour/s to
3 days/s. Slider release, pause and committed date entry synchronize Python
panels. The Planner uses that bar for its Analysis Window, not an independent
instant slider.

Green dashed coverage rings mark prepared neighborhoods; cyan marks the 80°S
terrain boundary. They are separate from catalog symbols, the orange provisional
selection ring and neighborhood cell outlines. Availability still depends on
height/date coverage. The Layers panel and NASA visibility overlays were removed;
Photos/Relief remain base layers on both views.

Documentation and About were corrected without editing Gabriel's or Igor's
implementations. Another scientific-copy issue remains in `planner.py`: “the
Sun shines …% of the time” describes a mean Illumination Fraction as a binary
duration. Ask its owner to use “mean Illumination Fraction” or equivalent full-Sun
hours instead. Narration must preserve that distinction meanwhile.

Use Connecting Ridge C1 and a covered 2 m window to avoid live waits. Rehearse
real marker transitions and the same time selection in Planner; check the hosted
build matches this branch. Keep the schematic Plotly export available offline.
Resolve the above caption/credit issues before showing affected Overview images.
At the time of this historical review, the demo was a timed draft. The
[official recording](https://youtu.be/ASh9yAMIm1U) is now available through the README.

Software validation: `python -m pytest -q` — **91 passed**. All ten public text
constant names and their panel imports were preserved; `git diff --check` passed.
These checks do not verify browser rendering, image licensing or scientific accuracy.
