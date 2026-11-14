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

Calculated locally from the committed catalog data introduced by main through
fb8d2d4, using `get_conditions` at each site's exact coordinates, Asset Height
2 m, and the half-open interval [2027-01-01, 2029-01-01). All eight calls returned
`source = pre-computed`. Each returned 17,544 hourly samples (731 days, including
leap year 2028). No live network or DEM regeneration was required.

| Point | Project average (%) | Difference from paper (percentage points) | Project any-Sun visibility (%) |
|---|---:|---:|---:|
| Connecting Ridge C1 | 89.94 | +1.94 | 93.61 |
| Connecting Ridge C2 | 75.43 | -2.67 | 80.65 |
| Shackleton Rim S1 | 85.64 | +0.14 | 89.60 |
| Shackleton Rim S2 | 69.77 | -12.33 | 76.05 |

These are combined two-year averages, not claims about each year individually.
Malapert regional center (21.56%), Faustini Rim A regional center (26.43%) and
Haworth regional center (15.76%) also reproduce the approximate project values
Gabriel reported. They do not have matching points in Table 2 and must not be
presented as validated by that table.

## Interpretation for the pitch

C1 and S1 show close numerical agreement; C2 differs by a few percentage points.
S2 has a substantial discrepancy that must remain visible in any summary.
There is no defined scientific acceptance tolerance for this comparison.

The study uses 20 m terrain sampling; the polar project data uses an 80 m DEM.
The time windows also differ. Both use LOLA-derived terrain, so agreement is not
independent of the underlying source data. Differences in horizon construction,
coordinate-frame realization and local terrain sampling require investigation;
we have not established which explains the S2 result. Do not attribute that
result to a specific cause or accept it solely on an order-of-magnitude basis.

Suggested pitch wording: “We compared four modeled illumination estimates with
published values. Several are close, while one discrepancy remains under
investigation. This is a preliminary consistency check, not full validation.”

## Reproduction without remote requests

Run from the repository root with the virtual environment active. This reads the
existing data files and does not modify the science modules or catalog:

```python
from unittest.mock import patch
from src.conditions import get_conditions
from src.sites import LUNAR_SITES

names = ["Connecting Ridge C1", "Connecting Ridge C2",
         "Shackleton Crater (Rim)", "Shackleton Rim S2"]
with patch("requests.sessions.Session.request", side_effect=RuntimeError("Network disabled")):
    for name in names:
        site = LUNAR_SITES[name]
        df = get_conditions(site["lat"], site["lon"], "2027-01-01", 731, asset_height=2.0)
        assert df.attrs["source"] == "pre-computed"
        assert len(df) == 17544
        f = df["illumination_fraction"]
        print(name, 100 * f.mean(), 100 * (f > 0).mean())
```

Before publication, ask Gabriel to review the comparison method, source-frame
alignment and S2 discrepancy. Do not change coordinates to force agreement.
