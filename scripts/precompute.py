"""Pre-compute Catalog Site data into data/catalog/ (see docs/adr/0001). Owner: Gabriel.

Usage: python -m scripts.precompute
Recomputes every site in src/sites.py and removes files of sites no longer in the catalog.
"""
import json
import time

import numpy as np
import pandas as pd

from src import catalog
from src.horizons_api import get_ephemerides_data
from src.sites import LUNAR_SITES
from src.terrain import dem_for, neighborhood_horizons


def save_ephemerides(path, ephemerides):
    """Write the CSV only if its content changed (gzip stores a timestamp, so rewrites always look modified)."""
    numeric = {column: 4 for column in ephemerides.columns if column != "time"}
    ephemerides = ephemerides.round(numeric)
    if path.exists() and pd.read_csv(path, parse_dates=["time"]).equals(ephemerides):
        return
    ephemerides.to_csv(path, index=False, compression={"method": "gzip", "mtime": 0})


def save_terrain(path, **arrays):
    """Write the npz only if its arrays changed (zip stores timestamps, so rewrites always look modified)."""
    if path.exists():
        with np.load(path) as old:
            if set(old.files) == set(arrays) and all(np.array_equal(old[k], v) for k, v in arrays.items()):
                return
    np.savez_compressed(path, **arrays)


def precompute_site(name, site, data_dir):
    days = (pd.Timestamp(catalog.END) - pd.Timestamp(catalog.START)).days
    ephemerides = get_ephemerides_data(site["lat"], site["lon"], catalog.START, days)
    save_ephemerides(data_dir / f"{catalog.slug(name)}_ephemerides.csv.gz", ephemerides)

    east, north = catalog.neighborhood_offsets()
    horizons = neighborhood_horizons(site["lat"], site["lon"], east, north, catalog.ASSET_HEIGHT_M)
    save_terrain(data_dir / f"{catalog.slug(name)}_terrain.npz", east=east, north=north,
                 horizons=np.round(horizons * 100).astype(np.int16))
    return {"lat": site["lat"], "lon": site["lon"], "start": catalog.START, "end": catalog.END,
            "terrain": dem_for(site["lat"])[1]}


def main(data_dir=catalog.DATA_DIR):
    data_dir.mkdir(parents=True, exist_ok=True)
    manifest = {}
    for name, site in LUNAR_SITES.items():
        started = time.time()
        manifest[name] = precompute_site(name, site, data_dir)
        print(f"{name}: {time.time() - started:.0f}s, terrain: {manifest[name]['terrain']}")

    current = {catalog.slug(name) for name in LUNAR_SITES}
    for path in data_dir.glob("*_*.*"):
        if path.name.split("_")[0] not in current:
            path.unlink()
    (data_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
                                            encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
