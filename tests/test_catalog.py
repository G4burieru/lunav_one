import json

import numpy as np
import pandas as pd

from src import catalog


def test_neighborhood_is_a_disk_including_the_site():
    east, north = catalog.neighborhood_offsets()
    assert np.all(np.hypot(east, north) <= catalog.NEIGHBORHOOD_RADIUS_M)
    assert np.any((east == 0) & (north == 0))
    assert 1200 < len(east) < 1300  # ~pi * 20^2 points at 100 m spacing


def test_load_site_ignores_data_for_moved_sites(tmp_path):
    (tmp_path / "manifest.json").write_text(json.dumps({"Site A": {"lat": -89.0, "lon": 0.0}}))
    pd.DataFrame({"time": ["2027-01-01"], "sun_elevation": [1.0]}).to_csv(tmp_path / "site-a_ephemerides.csv.gz")
    assert catalog.load_site("Site A", {"lat": -89.0, "lon": 0.0}, tmp_path) is not None
    assert catalog.load_site("Site A", {"lat": -88.0, "lon": 0.0}, tmp_path) is None
    assert catalog.load_site("Site B", {"lat": -89.0, "lon": 0.0}, tmp_path) is None


def test_precompute_script_imports():
    import scripts.precompute  # noqa: F401  (guards against syntax errors in the CLI script)
