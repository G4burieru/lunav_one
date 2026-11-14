import numpy as np
import pytest

from src import catalog
from src.conditions import get_conditions, offset_from
from src.sites import LUNAR_SITES
from src.terrain import MOON_RADIUS_M


def test_offset_from_site_points_north():
    site = {"lat": -85.0, "lon": 10.0}
    east, north = offset_from(site, -85.0 + np.degrees(1000 / MOON_RADIUS_M), 10.0)
    assert east == pytest.approx(0.0, abs=1.0)
    assert north == pytest.approx(1000.0, rel=1e-3)


def _precomputed_site():
    for name, site in LUNAR_SITES.items():
        data = catalog.load_site(name, site)
        if data is not None and data[1] is not None:
            return name, site
    pytest.skip("no pre-computed catalog data for the current coordinates; run python -m scripts.precompute")


def test_catalog_site_uses_precomputed_data_offline():
    name, site = _precomputed_site()
    df = get_conditions(site["lat"], site["lon"], "2027-03-01", 7)
    assert df.attrs["source"] == "pre-computed" and df.attrs["site"] == name
    assert len(df) == 7 * 24
    assert {"sun_horizon", "earth_horizon", "illumination_fraction"} <= set(df.columns)
    assert df["illumination_fraction"].between(0, 1).all()
