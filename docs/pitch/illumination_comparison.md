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
source data. Horizon construction, reference-frame realization and the remaining
differences still warrant scientific review. No permanent illumination, landing
safety, measured energy yield or radio-link performance is established.

Suggested pitch wording: “With finer local terrain, our four mean illumination
estimates are within 1.2 percentage points of published values. This supports
consistency with the literature, rather than independent validation, because the
periods differ and both calculations use LOLA-derived terrain.”

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
alignment and remaining differences. Do not change coordinates to force agreement.
