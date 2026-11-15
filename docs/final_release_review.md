# Final hackathon documentation and license review

## Branch synchronization

The working tree was clean at `d2b1aac`. Remote references showed main at
`2a58ef3` and no branch-only commits: the branch was 17 commits behind main.
`git merge --ff-only origin/main` advanced local `devel_renata` to `2a58ef3`
without conflicts or a new integration commit. PR #43 was already present and
was not reapplied. PRs #44–#50 are included. The documentation and licensing
update was subsequently committed and pushed as `7152685` — docs: finalize
hackathon documentation and add Apache-2.0 licensing.

At this status review, remote-reference inspection confirmed local and remote
`devel_renata` at
`7152685`, one commit ahead of main `2a58ef3` and zero commits behind. Main is
fully incorporated; no additional synchronization or conflict resolution is needed.

## Product and science presentation

The README now presents the completed educational/exploratory prototype, rather
than an implementation backlog. The detailed coordinate table, legacy identifiers,
frame evidence, offline Plotly export and data workflow moved into
[the technical guide](technical_guide.md); scientific references were preserved.

Descriptions were checked against the synchronized code: 17 Catalog Sites and
Overviews, responsive Moon View, Photos/Relief, optional 3D relief ×5, zoom and
Rotate controls, time bar and badges, Site Planner/Neighborhood, Custom Sites,
expandable About topics and pre-computed/live scenarios. Fivefold vertical
exaggeration is explicitly illustrative and does not modify scientific results.
Rotate can restart and stop spinning; the old “off for good after any interaction”
claim is not used as the current product behavior. Earlier planning documents
are labeled historical, without rewriting their original design history.

The README states: **Consistency-checked against published studies; independent
validation not performed.** It retains solar differences below 1.2 percentage
points for four study points and Earth Visibility differences at most 4.6 points
for seven locations (six at most 1.3), with a link to the
[full comparison](pitch/illumination_comparison.md). Shared LOLA inputs, period,
height, pixel-resolution and metric differences remain explicit. Software
completion and tests do not establish independent validation or operational
certification. Safety, electrical generation and guaranteed communication are
outside this educational prototype's claims.

## Single official video

The [30-second script](pitch/demo_30s.md) is the sole video deliverable and the
same video linked from the GitHub README. Its 55-word narration script is unchanged.
Recording instructions mention the optional exaggerated-relief opening without
adding narration or a control tour. The recorded [official video](../media/lunavone.mp4)
is stored in `media/lunavone.mp4`; its measured duration is **27.925 seconds**,
within the 30-second maximum. The original uploaded file was moved unchanged.

The superseded extended-demo script was removed, with all current references
updated. No extended video or slide presentation is planned. Research documents
remain available. The README links to the actual video file; no fictional files,
images or media URLs are used.

## Licensing audit and team agreement

At the start of the original licensing audit, no pre-existing project LICENSE,
COPYING or NOTICE file, incompatible project-level restriction or vendored
third-party implementation source was identified in the tracked repository.
Directly used libraries were checked against their upstream license files: Apache-2.0, MIT, BSD-2-Clause or BSD-3-Clause as recorded in
[THIRD_PARTY_NOTICES.md](../THIRD_PARTY_NOTICES.md). The installed packages and CDN
bundles retain their own licensing and transitive notices; this is not a blanket
license claim for every dependency or future package version.

The [Space Apps legal terms](https://www.spaceappschallenge.org/legal/) require
original content to be open source under an OSI-compliant license and identify
Apache 2.0 as their default when one is not specified. The official page's
indexed text was consulted; direct retrieval returned an error during this review.
Apache-2.0 is appropriate for the original project code/documentation and this
open-source requirement, provided its contributors authorize that grant.

[LICENSE](../LICENSE) is the complete, unmodified English text downloaded from
[the Apache Software Foundation](https://www.apache.org/licenses/LICENSE-2.0.txt),
verified byte-for-byte against the source. Its appendix remains part of the
standard text. The project's collective attribution is recorded separately in
[NOTICE](../NOTICE): **Copyright 2026 Lunav One contributors**. This avoids changing
the license text or attributing all contributors' rights to one person.

The optional NOTICE records project attribution and the external-material scope.
Creating one is consistent with the [Apache application guidance](https://www.apache.org/foundation/license-faq.html#apply).
No incoming vendored NOTICE obligation was identified; this does not remove the
need to preserve any upstream notices when redistributing installed libraries,
CDN bundles or generated Plotly HTML. The third-party inventory preserves source
and copyright references rather than attempting to relicense them.

NASA/JPL ephemerides, LOLA inputs, Moon Trek maps, LROC/Clementine imagery and
scientific publications are not granted Apache-2.0 rights by the team. Product
credits and [NASA media rules](https://www.nasa.gov/nasa-brand-center/images-and-media/),
[JPL policy](https://www.jpl.nasa.gov/jpl-image-use-policy/) and
[LROC terms](https://lroc.im-ldi.com/about/terms) remain applicable. The original
code and documentation can be reused, modified and redistributed under Apache
conditions; it is not a prohibition on copying the software.

Renata confirmed during this final review that all three contributors — João
Gabriel Santos, Igor Wanderley and Renata Andrade — agreed to Apache-2.0 for
their original project contributions. Collective license agreement is therefore
recorded as confirmed. This does not change the separate terms for third-party
materials.

## Validation and publication status

The synchronized baseline suite passed 134 tests. Final post-edit runs also passed:

| Local environment | Passed | Failed | Skipped |
|---|---:|---:|---:|
| Python 3.10.12 / Pandas 2.3.3 / Streamlit 1.65.0 | 134 | 0 | 0 |
| Python 3.13.18 / Pandas 3.1.1 / Streamlit 1.67.0 | 134 | 0 | 0 |

The same two environments were checked again in this status review: each full
suite passed 134 tests, with zero failures and zero skips. Both runs included the
real JavaScript badge regression through an existing Node-compatible runtime. These are local results, not a claim about a hosted
Actions run or independent science validation. The license matches the Apache
source byte-for-byte. All 191 Markdown links were parsed, with no missing local
file targets or section anchors. Of 78 unique external references, 63 returned
HTTP 200 in the automated check. Other references were not all confirmed by that
client; request failures alone were not treated as proof of broken sources or
image-loading problems. Official JPL policy and Space Apps legal references were
also consulted through browser/search results. No known missing local target or
fictional media URL remains; external publication links should be checked in a
normal browser before submission. No coordinates, IDs,
pre-computed data, tests, scientific equations, Planner logic or JavaScript
implementation are modified by this documentation work. The only Python change
is explanatory copy in `src/panels/texts.py`, with its public names preserved.

The documentation and licensing update is already published in `7152685`, with
team license agreement confirmed above. The remaining public-presentation tasks
include browser review of the hosted build; the official video is now recorded,
organized in `media/` and linked from the README.
Scientific activities outside the declared scope are limitations, not unfinished
hackathon implementation. Test counts in this report are local results; no passing
GitHub Actions status for `7152685` is inferred from them. This status review does
not create a commit, push, Pull Request or deployment. Only this report was
modified in that earlier status review. The subsequent final media update added
the recorded video, its README link and the repository link in About's Sources
and credits. License files, scientific calculations, interface logic, tests and
the narration script remain unchanged.


## Files in the final review

- Modified: `README.md`, `GLOSSARY.md`, `docs/TEAM_PLAN.md`, `docs/UI_OVERHAUL.md`,
  `docs/pitch/catalog_expansion_review.md`, `docs/pitch/demo_30s.md`,
  `docs/pitch/mission_explainer.md`, `docs/pitch/submission_draft.md`,
  `src/panels/texts.py` (copy only).
- Added: `LICENSE`, `NOTICE`, `THIRD_PARTY_NOTICES.md`, `docs/technical_guide.md`,
  `docs/final_release_review.md`.
- Removed: the superseded extended-demo script. Scientific research documents
  remain in place; no test or functional implementation file was removed.
