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


def test_all_catalog_files_match_registered_coordinates_and_coverage():
    from src.sites import LUNAR_SITES
    manifest = catalog.read_manifest()
    assert len(LUNAR_SITES) == 17 and set(manifest) == set(LUNAR_SITES)
    for key, site in LUNAR_SITES.items():
        entry = manifest[key]
        assert (entry['lat'], entry['lon']) == (site['lat'], site['lon'])
        assert (entry['start'], entry['end']) == (catalog.START, catalog.END)
        ephemerides, hood = catalog.load_site(key, site)
        expected = pd.Series(pd.date_range(catalog.START, catalog.END, freq='h', inclusive='left'), name='time')
        # Horizons exports may retain the stop instant; conditions use the half-open window.
        covered = ephemerides.loc[ephemerides['time'] < pd.Timestamp(catalog.END), 'time'].reset_index(drop=True)
        pd.testing.assert_series_equal(covered, expected)
        assert ephemerides['time'].is_monotonic_increasing and ephemerides['time'].is_unique
        assert hood is not None
        assert hood['horizons'].shape == (len(hood['east']), 360)
        assert np.isfinite(hood['horizons']).all()
