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

## Earth Visibility: comparison with the NASA PGDA map

For the same 2027–2028 window, 2 m Asset Height and 0° Elevation Mask, the
Malapert regional center has 48.90% Earth Visibility. At the pre-computed point
**1600 m west and 100 m north** of that center, it is 100% of the 17,544 hourly
samples. Its coordinates are approximately latitude -85.99115552°, longitude
-0.99054738°. This point is not a new Catalog Site or a verified summit.
Exactly 1600 m west with no north offset gives 65.93%, so the north offset must
be included when reproducing the example.

### Reference data

NASA Goddard's Planetary Geodesy Data Archive publishes an
[average Earth visibility map](https://pgda.gsfc.nasa.gov/products/69) of the
south pole from LOLA topography (Mazarico et al., 2011; product updated 2016).
Each 60 m pixel from 85°S to the pole holds the percentage of hourly timesteps
over an 18.6-year nutation cycle in which any part of Earth's disk is above the
terrain, at the surface. NASA's
[Lunar Surface Data Book (M2M-30044, March 2025)](https://ntrs.nasa.gov/api/citations/20250002845/downloads/M2M-30044%20Lunar%20Surface%20Data%20Book%20Baseline_Final.pdf),
section 5.1, names this product as the Earth visibility reference for Artemis
surface planning. It uses the same polar stereographic projection and 1737.4 km
sphere as our DEMs, so catalog coordinates map onto it directly.

### Like-for-like result

The map counts any part of Earth's disk; our Earth Visibility uses its center.
For this comparison only, the project value counts any part of the disk
(Earth's center above the Terrain Horizon minus its 0.95° apparent radius). The
3×3 range is the spread of map values within 90 m of the point, which shows how
quickly terrain changes the result.

| Point | Project, any part of disk (%) | PGDA map pixel (%) | Difference (points) | PGDA 3×3 range (%) |
|---|---:|---:|---:|---:|
| Shackleton Rim S1 | 54.47 | 53.75 | +0.72 | 30.94–53.75 |
| Connecting Ridge C1 | 58.48 | 53.91 | +4.57 | 50.28–58.19 |
| Connecting Ridge C2 | 59.46 | 58.65 | +0.81 | 16.90–58.65 |
| Shackleton Rim S2 | 57.23 | 53.44 | +3.79 | 15.68–56.69 |
| Malapert regional center | 53.50 | 52.41 | +1.09 | 48.96–53.15 |
| Faustini Rim A regional center | 51.69 | 50.80 | +0.89 | 36.70–50.81 |
| Haworth regional center | 45.18 | 43.94 | +1.24 | 43.71–44.10 |
| Malapert best neighborhood point | 100.00 | 79.70 | +20.30 | 49.83–100.00 |

Six of the seven catalog points are within 1.3 percentage points of NASA's map;
C1 and S2 are within 4.6 points, and for both an adjacent 60 m pixel reaches our
value. Every difference is positive, which is the expected direction: our
observer is 2 m above the ground and the map is at the surface. The Malapert
best point sits on a slope where the map ranges from 50% to 100% across
neighboring pixels, so its single-pixel value is not a meaningful benchmark;
the map does confirm that 100% Earth visibility occurs within 90 m of it.

Differences that remain: 18.6-year versus two-year averaging, 60 m pixels
versus our 20 m near-field terrain and exact points, and surface versus 2 m
observer height. Both calculations use LOLA-derived terrain, so this checks the
horizon and ephemeris computation rather than the terrain data itself.

The same archive offers an average solar illumination map, but it is not
comparable at these points. With the Sun never more than about 1.6° above the
horizon near the pole, a 2 m height and pixel size change the result strongly:
at C1 the surface map gives 44.31%, while Gläser et al. (2017) report 92.1%
solar visibility at 2 m with a 20 m DTM. Solar values are therefore compared
only against Gläser et al. above.

### Other sources

- [Bryant (2009), JPL IPN Progress Report 42-176](https://ipnpr.jpl.nasa.gov/progress_report/42-176/176C.pdf),
  written for NASA's SCaN lunar architecture study, tabulates Earth visibility at
  2 m for 11 south polar peaks. It used a 2006 Goldstone radar DEM whose
  coordinates do not land on the same peaks in LOLA terrain: at 7 of its 11
  points both our model and the PGDA map give 0%. It is used only for its
  summary that polar peaks see some part of Earth about 60–65% of the time,
  the whole disk about 50%, and the Malapert summit 100%.
- [NASA's Malapert region description](https://science.nasa.gov/image-detail/20100618/)
  describes favorable Earth visibility at the massif; it does not identify our
  catalog center or our selected cell as a summit.
- [Moonbase Mons Malapert, hosted by ILOA](https://iloa.org/media/Moonbase_Mons_Malapert.pdf)
  is a secondary source (Aerospace America, October 2008) describing probable
  continuous Earth views from the summit and roughly half-month views from
  Shackleton's rim.
- [Mazarico et al. (2011)](https://ui.adsabs.harvard.edu/abs/2011Icar..211.1066M)
  is the method paper for the PGDA maps.

To reproduce the table, run `python -m scripts.compare_pgda`. It reads the
pre-computed catalog data and about eighteen 3×3 pixel windows from the PGDA maps.

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
