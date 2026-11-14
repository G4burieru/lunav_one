"""Terrain horizon from LOLA DEMs, streamed from NASA servers (see docs/adr/0002). Owner: Gabriel.

A Terrain Horizon is the elevation angle of the skyline in each azimuth (0° = north, clockwise), as seen by a
Surface Asset `asset_height` metres above the ground.
"""
import time

import numpy as np
import rasterio
import rasterio.errors
from rasterio.crs import CRS
from rasterio.warp import transform as warp_transform
from rasterio.windows import Window, from_bounds

MOON_RADIUS_M = 1737400.0
SUN_RADIUS_DEG = 0.2665  # apparent solar disk radius from the Moon
AZIMUTHS = np.arange(360.0)
SOUTH_POLE_80M = "/vsicurl/https://pgda.gsfc.nasa.gov/data/LOLA_20mpp/LDEM_80S_80MPP_ADJ.TIF"
GLOBAL_118M = "/vsicurl/https://planetarymaps.usgs.gov/mosaic/Lunar_LRO_LOLA_Global_LDEM_118m_Mar2014.tif"
SOUTH_POLE_DEM_LIMIT = -80.0  # SOUTH_POLE_80M covers 80°S to the pole
MOON_GEOGRAPHIC = CRS.from_proj4(f"+proj=longlat +R={MOON_RADIUS_M} +no_defs")
GDAL_ENV = {
    "GDAL_DISABLE_READDIR_ON_OPEN": "EMPTY_DIR",
    "CPL_VSIL_CURL_ALLOWED_EXTENSIONS": ".TIF,.tif",
    "GDAL_HTTP_VERSION": "1.1",  # PGDA returns empty tile reads over HTTP/2
    "GDAL_HTTP_MAX_RETRY": "3",
    "GDAL_HTTP_RETRY_DELAY": "2",
}


def elevation_angle(distance, target_height, observer_height):
    """Elevation angle (deg) of a point `distance` m away along the surface, on a sphere, seen from the observer."""
    phi = distance / MOON_RADIUS_M
    up = (MOON_RADIUS_M + target_height) * np.cos(phi) - (MOON_RADIUS_M + observer_height)
    along = (MOON_RADIUS_M + target_height) * np.sin(phi)
    return np.degrees(np.arctan2(up, along))


def horizon_profile(dem, dem_transform, x0, y0, north, east, asset_height=2.0, max_distance=150_000.0,
                    azimuths=AZIMUTHS):
    """Terrain horizon (deg) per azimuth from a DEM array of heights relative to the reference sphere.

    `north` and `east` are the map displacements of one surface metre north and east at (x0, y0) (see local_axes).
    Directions that leave the DEM use the terrain seen so far.
    shortcut: the map scale is taken at the site; in the global (cylindrical) DEM it drifts over 150 km at high
    latitudes. Fine below ~60° and inside the south pole DEM.
    """
    inverse = ~dem_transform
    step = abs(dem_transform.a) / max(np.linalg.norm(north), np.linalg.norm(east))  # about one pixel per sample
    distances = np.arange(step, max_distance, step)

    col0, row0 = inverse * (x0, y0)
    ground = dem[int(row0), int(col0)]

    az = np.radians(np.asarray(azimuths))[:, None]
    dx = np.sin(az) * east[0] + np.cos(az) * north[0]
    dy = np.sin(az) * east[1] + np.cos(az) * north[1]
    cols, rows = inverse * (x0 + dx * distances, y0 + dy * distances)
    cols, rows = np.floor(cols).astype(int), np.floor(rows).astype(int)
    inside = (rows >= 0) & (rows < dem.shape[0]) & (cols >= 0) & (cols < dem.shape[1])

    heights = np.full(cols.shape, np.nan)
    heights[inside] = dem[rows[inside], cols[inside]]
    angles = elevation_angle(distances, heights, ground + asset_height)
    return np.nanmax(angles, axis=1)


def local_axes(crs, lat, lon):
    """Map position of a lunar lat/lon, and the map displacements of one surface metre north and east."""
    lat = max(min(lat, 89.9999), -89.9999)  # north/east are undefined exactly at a pole
    step_m = 100.0
    dlat = np.degrees(step_m / MOON_RADIUS_M)
    dlon = dlat / np.cos(np.radians(lat))
    xs, ys = warp_transform(MOON_GEOGRAPHIC, crs, [lon, lon, lon + dlon], [lat, lat + dlat, lat])
    origin = np.array([xs[0], ys[0]])
    north = (np.array([xs[1], ys[1]]) - origin) / step_m
    east = (np.array([xs[2], ys[2]]) - origin) / step_m
    return origin, north, east


def dem_for(lat):
    """DEM URL and description used for a latitude."""
    if lat <= SOUTH_POLE_DEM_LIMIT:
        return SOUTH_POLE_80M, "LOLA 80 m south pole DEM"
    return GLOBAL_118M, "LOLA 118 m global DEM"


# Read in bands of full window width: PGDA intermittently returns empty tiles on large reads (so read small and
# retry), and the global DEM is stored in full-width rows (so column chunks would re-download the same rows).
CHUNK_ROWS = 512


def _read_chunk(src, window, attempts=4):
    for attempt in range(attempts):
        try:
            return src.read(1, window=window, masked=True).astype(float)
        except rasterio.errors.RasterioIOError:
            if attempt == attempts - 1:
                raise
            time.sleep(2 * (attempt + 1))


def _read_around(url, lat, lon, radius):
    """DEM heights (m, relative to the reference sphere) within `radius` surface metres of a site; NaN outside.

    shortcut: windows are not wrapped across the ±180° meridian of the global DEM; add it if a catalog site needs it.
    """
    with rasterio.Env(**GDAL_ENV), rasterio.open(url) as src:
        (x0, y0), north, east = local_axes(src.crs, lat, lon)
        rx = radius * max(abs(north[0]), abs(east[0]))
        ry = radius * max(abs(north[1]), abs(east[1]))
        window = from_bounds(x0 - rx, y0 - ry, x0 + rx, y0 + ry, src.transform).round_offsets().round_lengths()
        r0, c0, h, w = int(window.row_off), int(window.col_off), int(window.height), int(window.width)
        c_start, c_stop = max(c0, 0), min(c0 + w, src.width)
        dem = np.full((h, w), np.nan)
        for r in range(max(r0, 0), min(r0 + h, src.height), CHUNK_ROWS):
            rows = min(CHUNK_ROWS, r0 + h - r, src.height - r)
            band = _read_chunk(src, Window(c_start, r, c_stop - c_start, rows))
            dem[r - r0:r - r0 + rows, c_start - c0:c_stop - c0] = band.filled(np.nan) * src.scales[0] + src.offsets[0]
        return dem, src.window_transform(window), (x0, y0), north, east


def site_horizon(lat, lon, asset_height=2.0, max_distance=150_000.0):
    """Terrain horizon (deg, per 1° azimuth) at a lunar site, reading only the needed part of the DEM."""
    dem, dem_transform, (x0, y0), north, east = _read_around(dem_for(lat)[0], lat, lon, max_distance)
    return horizon_profile(dem, dem_transform, x0, y0, north, east, asset_height, max_distance)


def neighborhood_horizons(lat, lon, east_offsets, north_offsets, asset_height=2.0, max_distance=150_000.0):
    """Terrain horizons (N x 360, deg) at points offset (east, north) metres from a site.

    Azimuths stay in the site's frame (the site's north), so they match the site's ephemerides; near the pole the
    local north of a point 2 km away can differ by ~10°.
    """
    reach = max_distance + np.hypot(east_offsets, north_offsets).max()
    dem, dem_transform, (x0, y0), north, east = _read_around(dem_for(lat)[0], lat, lon, reach)
    return np.array([
        horizon_profile(dem, dem_transform, x0 + e * east[0] + n * north[0], y0 + e * east[1] + n * north[1],
                        north, east, asset_height, max_distance)
        for e, n in zip(east_offsets, north_offsets)
    ])


def apply_terrain(ephemerides, horizon, east_m=0.0, north_m=0.0):
    """Copy of an ephemerides DataFrame seen from a point offset from where it was computed, with the terrain
    horizon in the direction of each body and the Illumination Fraction."""
    out = ephemerides.copy()
    for body in ("sun", "earth"):
        azimuth = out[f"{body}_azimuth"]
        out[f"{body}_elevation"] = elevation_at_offset(out[f"{body}_elevation"], azimuth, east_m, north_m)
        out[f"{body}_horizon"] = horizon_at(horizon, azimuth)
    out["illumination_fraction"] = illumination_fraction(out["sun_elevation"], out["sun_horizon"])
    return out


def elevation_at_offset(elevation, azimuth, east_m, north_m):
    """Elevation (deg) of a distant body seen from a point offset (east_m, north_m) from where it was computed.

    Moving over the curved surface tilts the local vertical by distance / radius toward the direction of travel.
    """
    az = np.radians(azimuth)
    return elevation + np.degrees((east_m * np.sin(az) + north_m * np.cos(az)) / MOON_RADIUS_M)


def horizon_at(horizon, azimuth):
    """Terrain horizon elevation at arbitrary azimuths (deg), interpolating the 1° profile."""
    return np.interp(np.mod(azimuth, 360.0), np.append(AZIMUTHS, 360.0), np.append(horizon, horizon[0]))


def illumination_fraction(sun_elevation, horizon_elevation):
    """Fraction (0–1) of the solar disk above the terrain horizon."""
    h = np.clip((np.asarray(sun_elevation) - np.asarray(horizon_elevation)) / SUN_RADIUS_DEG, -1.0, 1.0)
    hidden = (np.arccos(h) - h * np.sqrt(1 - h**2)) / np.pi  # circular segment below the horizon line
    return 1.0 - hidden
