"""Sun and Earth conditions at any lunar point, including the terrain horizon. Owner: Gabriel.

Contract used by app.py; coordinate any change with the team:
    get_conditions(lat, lon, start_date, days, asset_height=2.0) -> DataFrame with
        time, sun_azimuth, sun_elevation, earth_azimuth, earth_elevation   (see horizons_api.py)
        sun_horizon, earth_horizon   terrain horizon (deg) in the direction of the Sun / Earth
        illumination_fraction        0..1 of the solar disk above the terrain horizon
    and df.attrs:
        "terrain"   DEM description, or None when only the ideal horizon is available
        "source"    "pre-computed", "pre-computed terrain + live ephemerides", or "live"
        "site"      catalog site name whose Site Neighborhood was used, or None

Pre-computed data is used when the point is inside a catalog Site Neighborhood at the default asset height
(snapped to the nearest 100 m grid point) and, for ephemerides, when the period is covered (docs/adr/0001).
Otherwise JPL Horizons and the DEM are read live, which can take a minute or two; cache the result in the app.
"""
import numpy as np
import pandas as pd
from rasterio.crs import CRS
from rasterio.warp import transform as warp_transform

from src import catalog
from src.horizons_api import get_ephemerides_data
from src.sites import LUNAR_SITES
from src.terrain import MOON_GEOGRAPHIC, MOON_RADIUS_M, SOUTH_POLE_DEM_LIMIT, apply_terrain, dem_for, site_horizon


def offset_from(site, lat, lon):
    """East and north offset (m) of a lunar point from a site, in the site's local frame."""
    local = CRS.from_proj4(f"+proj=aeqd +lat_0={site['lat']} +lon_0={site['lon']} +R={MOON_RADIUS_M} +units=m "
                           "+no_defs")
    xs, ys = warp_transform(MOON_GEOGRAPHIC, local, [lon], [lat])
    return xs[0], ys[0]


def _catalog_match(lat, lon):
    reach = catalog.NEIGHBORHOOD_RADIUS_M + catalog.NEIGHBORHOOD_SPACING_M / 2
    for name, site in LUNAR_SITES.items():
        east, north = offset_from(site, lat, lon)
        if np.hypot(east, north) > reach:
            continue
        data = catalog.load_site(name, site)
        if data is not None and data[1] is not None:
            return name, site, data, east, north
    return None


def get_conditions(lat, lon, start_date, days, asset_height=catalog.ASSET_HEIGHT_M):
    start = pd.Timestamp(start_date)
    stop = start + pd.Timedelta(days=days)
    match = _catalog_match(lat, lon) if asset_height == catalog.ASSET_HEIGHT_M else None

    if match:
        name, site, (ephemerides, neighborhood), east, north = match
        i = int(np.argmin(np.hypot(neighborhood["east"] - east, neighborhood["north"] - north)))
        horizon, east, north = neighborhood["horizons"][i], neighborhood["east"][i], neighborhood["north"][i]
        if start >= pd.Timestamp(catalog.START) and stop <= pd.Timestamp(catalog.END):
            ephemerides = ephemerides[ephemerides["time"] >= start]
            source = "pre-computed"
        else:
            # Ephemerides from the site centre keep azimuths in the same frame as the pre-computed horizons.
            ephemerides = get_ephemerides_data(site["lat"], site["lon"], start.date(), days)
            source = "pre-computed terrain + live ephemerides"
        terrain = catalog.read_manifest()[name]["terrain"]
    else:
        name, east, north, source = None, 0.0, 0.0, "live"
        ephemerides = get_ephemerides_data(lat, lon, start.date(), days)
        if lat <= SOUTH_POLE_DEM_LIMIT:
            horizon, terrain = site_horizon(lat, lon, asset_height), dem_for(lat)[1]
        else:
            # docs/adr/0002: the global DEM is too slow to read live, so custom sites outside 80°S use the ideal horizon.
            horizon, terrain = np.zeros(360), None

    # Half-open window [start, stop): `days` days of hourly samples, so hour counts add up to days * 24.
    ephemerides = ephemerides[ephemerides["time"] < stop].reset_index(drop=True)
    conditions = apply_terrain(ephemerides, horizon, east, north)
    conditions.attrs.update(terrain=terrain, source=source, site=name)
    return conditions
