# Preliminary illumination comparison

This is a consistency check against literature, not a landing-safety assessment
or completed independent validation. Do not describe it as a measured power yield.

## Published values

Source: [Gläser et al. (2017), Table 2, PDF page 12](https://ntrs.nasa.gov/api/citations/20170007365/downloads/20170007365.pdf).
The study uses a 2 m Asset Height and the 2017–2037 interval. S1/S2 below are our
local labels for the two Shackleton rows, not the Table 3 cluster identifiers.

| Catalog name | Latitude | East longitude | Paper average illumination (%) | Paper solar visibility (%) |
|---|---:|---:|---:|---:|
| Connecting Ridge C1 | -89.4398 | -137.17 | 88.0 | 92.1 |
| Connecting Ridge C2 | -89.3130 | -114.02 | 78.1 | 82.0 |
| Shackleton Rim S1 | -89.6866 | -162.81 | 85.5 | 89.4 |
| Shackleton Rim S2 | -89.7815 | -155.30 | 82.1 | 89.8 |

Average illumination is the mean visible solar-disk fraction, not the fraction
of samples with any sunlight. Solar visibility is the latter measure. Compare
like quantities: `100 * mean(illumination_fraction)` for average illumination,
and `100 * mean(illumination_fraction > 0)` for any-Sun visibility.

## Reproduced project values

Calculated locally from the regenerated catalog data in PR #12 (main merge
889cd7e, including the corrected DEM read window), using `get_conditions` at each site's exact coordinates, Asset Height
2 m, and the half-open interval [2027-01-01, 2029-01-01). All eight calls returned
`source = pre-computed`. Each returned 17,544 hourly samples (731 days, including
leap year 2028). No live network or DEM regeneration was required.

| Point | Project average (%) | Difference from paper (percentage points) | Project any-Sun visibility (%) | Earth Visibility (%) |
|---|---:|---:|---:|---:|
| Connecting Ridge C1 | 88.35 | +0.35 | 92.37 | 54.30 |
| Connecting Ridge C2 | 79.01 | +0.91 | 82.79 | 55.22 |
| Shackleton Rim S1 | 85.90 | +0.40 | 89.71 | 49.97 |
| Shackleton Rim S2 | 80.99 | -1.11 | 87.57 | 52.88 |

Earth Visibility uses Earth's center above the Terrain Horizon and an Elevation
Mask of 0°. It is not a radio-link availability calculation and is not a metric
validated against Table 2. Values are rounded only for presentation.

These are combined two-year averages, not claims about each year individually.
The recalculated means for the other polar sites are Malapert regional center
15.41%, Faustini Rim A regional center 26.32%, and Haworth regional center 12.64%.
Apollo 11 remains 49.74% (global 118 m DEM). They do not have matching points in Table 2 and must not be
presented as validated by that table.

## Interpretation for the pitch

All four mean Illumination Fraction estimates differ from the published values
by less than 1.2 percentage points. This is a descriptive result, not a predefined
scientific acceptance tolerance or proof of full model accuracy.

The corrected DEM read window in PR #12 includes terrain that could previously
be omitted between roughly 7 and 10 km in some directions. After regeneration,
C1 changed from 89.72% (+1.72 percentage points) to 88.35% (+0.35). These final
values supersede the earlier PR #9 figures.

The previous 80 m-only result for Shackleton S2 was 69.77%, a difference of
-12.33 percentage points. With 20 m terrain within the first 10 km, combined
with 80 m terrain from 10–50 km and a 320 m overview from 50–150 km, it is 80.99%, a difference of -1.11 percentage
points. The coordinates, 2 m Asset Height and comparison interval are unchanged.
This improvement is consistent with near-field terrain resolution contributing
to the earlier discrepancy. It does not establish resolution as the sole cause
or certify the modeled point. The paper uses a 20 m DTM; our combined-resolution
calculation is not an exact reproduction of that method.

The time windows differ (2017–2037 versus 2027–2028), and both calculations use
LOLA-derived terrain. Agreement is therefore not independent of the underlying
source data. Reference-frame compatibility is confirmed as described below. Horizon
construction, terrain uncertainty and remaining differences still warrant review. No permanent illumination, landing
safety, measured energy yield or radio-link performance is established.

Suggested pitch wording: “With finer local terrain, our four mean illumination
estimates are within 1.2 percentage points of published values. This supports
consistency with the literature, rather than independent validation, because the
periods differ and both calculations use LOLA-derived terrain.”

## Coordinate-frame compatibility

Horizons lunar orientation, the PGDA DEMs and the LOLA-derived study coordinates
use the DE421 mean-Earth frame (MOON_ME) with a 1737.4 km reference sphere.
The [Horizons manual, Lunar Mean-Earth Frame of DE421](https://ssd.jpl.nasa.gov/horizons/manual.html#lunar-mean-earth-frame-of-de421)
specifies this orientation for 1550–2650, covering our analysis. A fresh observer
request at S1 for 2027-01-01 to 2027-01-02 returned these header fields:

```text
Center pole/equ : MEAN_ME (high precision)
Center radii    : 1737.4, 1737.4, 1737.4 km
```

The header's body-ephemeris source is DE441; that is distinct from the DE421
mean-Earth cartographic frame and does not imply a frame mismatch.
[PGDA region metadata](https://pgda.gsfc.nasa.gov/products/78) identifies
MOON_ME/DE421; [LOLA product documentation](https://pgda.gsfc.nasa.gov/products/69)
identifies the same reference radius. The study coordinates retain their
LOLA-derived provenance. No coordinate transformation or change to catalog
positions is needed for this compatibility check. This resolves the earlier
frame-reconciliation item, not complete terrain or landing-safety validation.

## Earth Visibility: qualitative comparison

For the same 2027–2028 window, 2 m Asset Height and 0° Elevation Mask, the
Malapert regional center has 48.90% Earth Visibility. At the pre-computed point
**1600 m west and 100 m north** of that center, it is 100% of the 17,544 hourly
samples. Its coordinates are approximately latitude -85.99115552°, longitude
-0.99054738°. This point is not a new Catalog Site or a verified summit.
Exactly 1600 m west with no north offset gives 65.93%, so the north offset must
be included when reproducing the example.

The four Shackleton / Connecting Ridge study points have 49.97–55.22% Earth
Visibility. These results are **consistent with published descriptions**, not
numerically validated by a matching external site-by-site percentage table:

- [NASA's Malapert region description](https://science.nasa.gov/image-detail/20100618/)
  describes favorable Earth visibility at the massif; it does not identify our
  catalog center or our selected cell as a summit.
- [Moonbase Mons Malapert, hosted by ILOA](https://iloa.org/media/Moonbase_Mons_Malapert.pdf)
  is a secondary source (Aerospace America, October 2008). It describes probable
  continuous Earth views from the summit and roughly half-month views from
  Shackleton's rim. Those descriptions are qualitative, not measurements at our
  model coordinates, and do not guarantee a radio link.
- [Mazarico et al. (2011), PGDA products](https://pgda.gsfc.nasa.gov/products/69)
  provides Earth-visibility maps, not a numerical benchmark here. Those maps
  count any exposed part of Earth's disk; our Earth Visibility criterion uses
  its center, so the definitions differ. The [paper record](https://ui.adsabs.harvard.edu/abs/2011Icar..211.1066M)
  is retained as a bibliographic reference.

“100%” here means all modeled hourly samples in the stated two-year window,
not guaranteed uninterrupted visibility at finer time scales or for all time.
Libration changes Earth's apparent elevation near the pole; terrain makes the
result strongly position-dependent. No antenna, receiving station, link budget,
or operational communications availability is evaluated.

To reproduce the Malapert example without network calls, select the exact row
from `neighborhood_summary("Malapert Massif (Summit)", "2027-01-01", 731)` where
`east_m == -1600` and `north_m == 100`, then pass its `lat`/`lon` to
`get_conditions` at the default 2 m height. Keep `elevation_mask=0.0`.

## Reproduction without remote requests

Run from the repository root with the virtual environment active. This reads the
existing data files and does not modify the science modules or catalog:

```python
from unittest.mock import patch
from src.conditions import get_conditions
from src.metrics import earth_visible_hours
from src.sites import LUNAR_SITES

names = list(LUNAR_SITES)  # Include the regional centers before quoting their values.
with patch("requests.sessions.Session.request", side_effect=RuntimeError("Network disabled")):
    for name in names:
        site = LUNAR_SITES[name]
        df = get_conditions(site["lat"], site["lon"], "2027-01-01", 731, asset_height=2.0)
        assert df.attrs["source"] == "pre-computed"
        assert len(df) == 17544
        f = df["illumination_fraction"]
        earth_pct = 100 * earth_visible_hours(df, elevation_mask=0.0) / len(df)
        print(name, 100 * f.mean(), 100 * (f > 0).mean(), earth_pct)
```

Before publication, ask Gabriel to review the comparison method, source-frame
evidence and remaining differences. Do not change coordinates to force agreement.
