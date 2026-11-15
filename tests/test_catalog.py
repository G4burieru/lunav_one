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
    entry = {"lat": -89.0, "lon": 0.0, "start": catalog.START, "end": catalog.END}
    (tmp_path / "manifest.json").write_text(json.dumps({"Site A": entry}))
    pd.DataFrame({"time": ["2027-01-01"], "sun_elevation": [1.0]}).to_csv(tmp_path / "site-a_ephemerides.csv.gz")
    assert catalog.load_site("Site A", {"lat": -89.0, "lon": 0.0}, tmp_path) is not None
    assert catalog.load_site("Site A", {"lat": -88.0, "lon": 0.0}, tmp_path) is None
    assert catalog.load_site("Site B", {"lat": -89.0, "lon": 0.0}, tmp_path) is None


def test_load_site_ignores_data_for_another_window(tmp_path):
    """After START or END changes, data from the old window must not be cut into the new one."""
    entry = {"lat": -89.0, "lon": 0.0, "start": "2026-01-01", "end": catalog.END}
    (tmp_path / "manifest.json").write_text(json.dumps({"Site A": entry}))
    pd.DataFrame({"time": ["2027-01-01"], "sun_elevation": [1.0]}).to_csv(tmp_path / "site-a_ephemerides.csv.gz")
    assert catalog.load_site("Site A", {"lat": -89.0, "lon": 0.0}, tmp_path) is None


def test_precompute_script_imports():
    import scripts.precompute  # noqa: F401  (guards against syntax errors in the CLI script)


def test_unchanged_data_is_not_rewritten(tmp_path):
    from scripts.precompute import save_ephemerides, save_terrain
    eph = pd.DataFrame({"time": pd.to_datetime(["2027-01-01 00:00"]), "sun_elevation": [1.23456]})
    csv, npz = tmp_path / "a_ephemerides.csv.gz", tmp_path / "a_terrain.npz"
    save_ephemerides(csv, eph)
    save_terrain(npz, horizons=np.array([1, 2], dtype=np.int16))
    before = csv.read_bytes(), npz.stat().st_mtime_ns
    save_ephemerides(csv, eph)
    save_terrain(npz, horizons=np.array([1, 2], dtype=np.int16))
    assert (csv.read_bytes(), npz.stat().st_mtime_ns) == before
    save_terrain(npz, horizons=np.array([1, 3], dtype=np.int16))
    assert np.load(npz)["horizons"].tolist() == [1, 3]
