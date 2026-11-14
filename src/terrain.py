"""Terrain horizon from LOLA DEMs, streamed from NASA servers (see docs/adr/0002). Owner: Gabriel.

A Terrain Horizon is the elevation angle of the skyline in each azimuth (0° = north, clockwise), as seen by a
Surface Asset `asset_height` metres above the ground.
"""
import math
import time
import warnings

import numpy as np
import rasterio
import rasterio.errors
from affine import Affine
from rasterio.crs import CRS
from rasterio.enums import Resampling
from rasterio.warp import transform as warp_transform
from rasterio.windows import Window, from_bounds

MOON_RADIUS_M = 1737400.0
SUN_RADIUS_DEG = 0.2665  # apparent solar disk radius from the Moon
AZIMUTHS = np.arange(360.0)
MAX_DISTANCE_M = 150_000.0
SOUTH_POLE_80M = "/vsicurl/https://pgda.gsfc.nasa.gov/data/LOLA_20mpp/LDEM_80S_80MPP_ADJ.TIF"
SOUTH_POLE_20M = "/vsicurl/https://pgda.gsfc.nasa.gov/data/LOLA_20mpp/LDEM_80S_20MPP_ADJ.TIF"
GLOBAL_118M = "/vsicurl/https://planetarymaps.usgs.gov/mosaic/Lunar_LRO_LOLA_Global_LDEM_118m_Mar2014.tif"
SOUTH_POLE_DEM_LIMIT = -80.0  # the south pole DEMs cover 80°S to the pole
MOON_GEOGRAPHIC = CRS.from_proj4(f"+proj=longlat +R={MOON_RADIUS_M} +no_defs")
GDAL_ENV = {
    "GDAL_DISABLE_READDIR_ON_OPEN": "EMPTY_DIR",
    "CPL_VSIL_CURL_ALLOWED_EXTENSIONS": ".TIF,.tif",
    "GDAL_HTTP_VERSION": "1.1",  # PGDA returns empty tile reads over HTTP/2
    "GDAL_HTTP_MAX_RETRY": "3",
    "GDAL_HTTP_RETRY_DELAY": "2",
}

# Distance rings (DEM, decimation, from m, to m): fine terrain close to the point, coarser far away where a pixel
# subtends a smaller angle. Decimation 4 reads the 80 m DEM's built-in 320 m overview.
SOUTH_POLE_RINGS = [
    (SOUTH_POLE_20M, 1, 0.0, 10_000.0),
    (SOUTH_POLE_80M, 1, 10_000.0, 50_000.0),
    (SOUTH_POLE_80M, 4, 50_000.0, MAX_DISTANCE_M),
]
# The global DEM has no overviews and is stored in full-width rows, so decimating it saves no download.
GLOBAL_RINGS = [(GLOBAL_118M, 1, 0.0, MAX_DISTANCE_M)]


def elevation_angle(distance, target_height, observer_height):
    """Elevation angle (deg) of a point `distance` m away along the surface, on a sphere, seen from the observer."""
    phi = distance / MOON_RADIUS_M
    up = (MOON_RADIUS_M + target_height) * np.cos(phi) - (MOON_RADIUS_M + observer_height)
    along = (MOON_RADIUS_M + target_height) * np.sin(phi)
    return np.degrees(np.arctan2(up, along))


def ground_height(dem, dem_transform, x, y):
    """DEM height at a map point, or NaN outside the array or where the DEM has no data."""
    col, row = ~dem_transform @ (x, y)
    row, col = math.floor(row), math.floor(col)
    inside = 0 <= row < dem.shape[0] and 0 <= col < dem.shape[1]
    return float(dem[row, col]) if inside else math.nan


def horizon_profile(dem, dem_transform, x0, y0, north, east, asset_height=2.0, max_distance=MAX_DISTANCE_M,
                    azimuths=AZIMUTHS, min_distance=0.0, ground=None):
    """Terrain horizon (deg) per azimuth from a DEM array of heights relative to the reference sphere.

    `north` and `east` are the map displacements of one surface metre north and east at (x0, y0) (see local_axes).
    Only terrain between `min_distance` and `max_distance` is considered; `ground` overrides the observer's ground
    height (used when a finer DEM knows it better). Directions with no terrain in range are NaN.
    shortcut: the map scale is taken at the site; in the global (cylindrical) DEM it drifts over 150 km at high
    latitudes. Fine below ~60° and inside the south pole DEM.
    """
    inverse = ~dem_transform
    step = abs(dem_transform.a) / max(np.linalg.norm(north), np.linalg.norm(east))  # about one pixel per sample
    distances = np.arange(max(step, min_distance), max_distance, step)
    if ground is None:
        ground = ground_height(dem, dem_transform, x0, y0)

    az = np.radians(np.asarray(azimuths))[:, None]
    dx = np.sin(az) * east[0] + np.cos(az) * north[0]
    dy = np.sin(az) * east[1] + np.cos(az) * north[1]
    cols, rows = inverse @ (x0 + dx * distances, y0 + dy * distances)
    cols, rows = np.floor(cols).astype(int), np.floor(rows).astype(int)
    inside = (rows >= 0) & (rows < dem.shape[0]) & (cols >= 0) & (cols < dem.shape[1])

    heights = np.full(cols.shape, np.nan)
    heights[inside] = dem[rows[inside], cols[inside]]
    angles = elevation_angle(distances, heights, ground + asset_height)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)  # all-NaN directions (outside the DEM) are expected
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
        return SOUTH_POLE_80M, "LOLA 20 m (within 10 km) and 80 m south pole DEMs"
    return GLOBAL_118M, "LOLA 118 m global DEM"


# Read in bands of full window width: PGDA intermittently returns empty tiles on large reads (so read small and
# retry), and the global DEM is stored in full-width rows (so column chunks would re-download the same rows).
CHUNK_ROWS = 512


def _read_chunk(src, window, out_shape, attempts=6, resampling=Resampling.nearest):
    for attempt in range(attempts):
        try:
            return src.read(1, window=window, out_shape=out_shape, masked=True,
                            resampling=resampling).astype(np.float32)
        except rasterio.errors.RasterioIOError:
            if attempt == attempts - 1:
                raise
            time.sleep(5 * 2 ** attempt)  # 5, 10, 20, 40, 80 s: PGDA outages can last over a minute


def _read_around(url, lat, lon, radius, decimation=1):
    """DEM heights (m, relative to the reference sphere) within `radius` surface metres of a site; NaN outside.

    `decimation` > 1 reads a coarser version (one value per `decimation` pixels), served from the file's overviews.
    shortcut: windows are not wrapped across the ±180° meridian of the global DEM; add it if a catalog site needs it.
    """
    f = decimation
    with rasterio.Env(**GDAL_ENV), rasterio.open(url) as src:
        (x0, y0), north, east = local_axes(src.crs, lat, lon)
        # Largest map extent of `radius` surface metres in any direction (north/east can point diagonally on the map).
        rx = radius * np.hypot(north[0], east[0])
        ry = radius * np.hypot(north[1], east[1])
        window = from_bounds(x0 - rx, y0 - ry, x0 + rx, y0 + ry, src.transform)
        # Align the window to multiples of the decimation so coarse pixels line up with the overview grid.
        r0, c0 = math.floor(window.row_off / f) * f, math.floor(window.col_off / f) * f
        h = math.ceil((window.row_off + window.height - r0) / f) * f
        w = math.ceil((window.col_off + window.width - c0) / f) * f
        c_start, c_stop = max(c0, 0), min(c0 + w, src.width)
        dem = np.full((h // f, w // f), np.nan, dtype=np.float32)
        for r in range(max(r0, 0), min(r0 + h, src.height), CHUNK_ROWS * f):
            rows = min(CHUNK_ROWS * f, r0 + h - r, src.height - r)
            out_shape = (math.ceil(rows / f), math.ceil((c_stop - c_start) / f))
            band = _read_chunk(src, Window(c_start, r, c_stop - c_start, rows), out_shape)
            top, left = (r - r0) // f, (c_start - c0) // f
            dem[top:top + out_shape[0], left:left + out_shape[1]] = (
                band.filled(np.nan) * src.scales[0] + src.offsets[0])
        dem_transform = src.window_transform(Window(c0, r0, w, h)) @ Affine.scale(f)
        return dem, dem_transform, (x0, y0), north, east


def site_horizon(lat, lon, asset_height=2.0, max_distance=MAX_DISTANCE_M):
    """Terrain horizon (deg, per 1° azimuth) at a lunar site, reading only the needed part of the DEM."""
    return _horizons(lat, lon, np.zeros(1), np.zeros(1), asset_height, max_distance)[0]


def neighborhood_horizons(lat, lon, east_offsets, north_offsets, asset_height=2.0, max_distance=MAX_DISTANCE_M):
    """Terrain horizons (N x 360, deg) at points offset (east, north) metres from a site.

    Azimuths stay in the site's frame (the site's north), so they match the site's ephemerides; near the pole the
    local north of a point 2 km away can differ by ~10°.
    """
    return _horizons(lat, lon, np.asarray(east_offsets), np.asarray(north_offsets), asset_height, max_distance)


def _horizons(lat, lon, east_offsets, north_offsets, asset_height, max_distance, rings=None):
    """Horizons at points offset from a site, combining the distance rings for the latitude.

    The observer's ground height comes from the finest ring with data there. Raises ValueError for a point with no
    terrain data, rather than returning a horizon full of NaN.
    """
    if rings is None:
        rings = SOUTH_POLE_RINGS if lat <= SOUTH_POLE_DEM_LIMIT else GLOBAL_RINGS
    rings = [(url, f, near, min(far, max_distance)) for url, f, near, far in rings if near < max_distance]
    reach = np.hypot(east_offsets, north_offsets).max()
    grids = [_read_around(url, lat, lon, far + reach, f) for url, f, _, far in rings]
    (x0, y0), north, east = grids[0][2:]

    horizons = []
    for e, n in zip(east_offsets, north_offsets):
        x, y = x0 + e * east[0] + n * north[0], y0 + e * east[1] + n * north[1]
        grounds = (ground_height(dem, dem_transform, x, y) for dem, dem_transform, *_ in grids)
        ground = next((g for g in grounds if math.isfinite(g)), math.nan)
        if not math.isfinite(ground):
            raise ValueError(f"No terrain data at lat {lat}, lon {lon}, offset ({e:.0f} m E, {n:.0f} m N)")
        profiles = [horizon_profile(dem, dem_transform, x, y, north, east, asset_height, far, min_distance=near,
                                    ground=ground)
                    for (dem, dem_transform, *_), (_, _, near, far) in zip(grids, rings)]
        horizons.append(np.fmax.reduce(profiles))
    return np.array(horizons)


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
