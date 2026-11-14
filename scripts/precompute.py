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
from src.terrain import neighborhood_horizons

SOUTH_POLE_DEM_LIMIT = -80.0  # the 80 m south pole DEM covers 80°S to the pole


def precompute_site(name, site, data_dir):
    days = (pd.Timestamp(catalog.END) - pd.Timestamp(catalog.START)).days
    ephemerides = get_ephemerides_data(site["lat"], site["lon"], catalog.START, days)
    numeric = {column: 4 for column in ephemerides.columns if column != "time"}
    ephemerides.round(numeric).to_csv(data_dir / f"{catalog.slug(name)}_ephemerides.csv.gz", index=False)

    terrain = None
    if site["lat"] <= SOUTH_POLE_DEM_LIMIT:
        east, north = catalog.neighborhood_offsets()
        horizons = neighborhood_horizons(site["lat"], site["lon"], east, north, catalog.ASSET_HEIGHT_M)
        np.savez_compressed(data_dir / f"{catalog.slug(name)}_terrain.npz", east=east, north=north,
                            horizons=np.round(horizons * 100).astype(np.int16))
        terrain = "LOLA 80 m south pole DEM"
    # shortcut: sites outside 80°S have no terrain yet; the global 118 m DEM comes next (docs/adr/0002).
    return {"lat": site["lat"], "lon": site["lon"], "start": catalog.START, "end": catalog.END, "terrain": terrain}


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
