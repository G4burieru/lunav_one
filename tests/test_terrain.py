import numpy as np
import pytest
from rasterio.transform import from_origin

from src.terrain import (SUN_RADIUS_DEG, elevation_angle, horizon_at, horizon_profile, illumination_fraction)

NORTH, EAST = np.array([0.0, 1.0]), np.array([1.0, 0.0])
TRANSFORM = from_origin(-50_000, 50_000, 100, 100)  # 1000x1000 px grid of 100 m centred on (0, 0)


def test_flat_sphere_horizon_dips_below_zero():
    dem = np.zeros((1000, 1000))
    horizon = horizon_profile(dem, TRANSFORM, 0, 0, NORTH, EAST, asset_height=2.0, max_distance=40_000)
    # Ideal horizon dip for a 2 m observer on a 1737.4 km sphere is sqrt(2h/R) rad, about -0.087°.
    assert horizon == pytest.approx(np.full(360, -np.degrees(np.sqrt(2 * 2.0 / 1737400))), abs=0.002)


def test_wall_to_the_east_raises_only_eastern_horizon():
    dem = np.zeros((1000, 1000))
    dem[:, 600:] = 1000.0  # 1 km high wall starting 10 km east of the site
    horizon = horizon_profile(dem, TRANSFORM, 0, 0, NORTH, EAST, asset_height=0.0, max_distance=40_000)
    expected = elevation_angle(10_000, 1000.0, 0.0)
    assert horizon[90] == pytest.approx(expected, abs=0.05)
    assert horizon[270] < 0.01


def test_horizon_at_interpolates_and_wraps():
    profile = np.zeros(360)
    profile[359] = 2.0
    assert horizon_at(profile, 359.5) == pytest.approx(1.0)


@pytest.mark.parametrize("offset, expected", [
    (SUN_RADIUS_DEG, 1.0), (0.0, 0.5), (-SUN_RADIUS_DEG, 0.0), (5.0, 1.0), (-5.0, 0.0),
])
def test_illumination_fraction(offset, expected):
    assert illumination_fraction(10.0 + offset, 10.0) == pytest.approx(expected)


def test_moving_toward_the_sun_raises_it():
    from src.terrain import MOON_RADIUS_M, elevation_at_offset
    one_km_in_degrees = np.degrees(1000 / MOON_RADIUS_M)
    assert elevation_at_offset(5.0, 90.0, 1000.0, 0.0) == pytest.approx(5.0 + one_km_in_degrees)
    assert elevation_at_offset(5.0, 90.0, 0.0, 1000.0) == pytest.approx(5.0)


def test_local_axes_scale_east_by_latitude_in_cylindrical_maps():
    from rasterio.crs import CRS
    from src.terrain import local_axes
    cylindrical = CRS.from_proj4("+proj=eqc +R=1737400 +units=m +no_defs")
    _, north, east = local_axes(cylindrical, 60.0, 10.0)
    assert np.linalg.norm(north) == pytest.approx(1.0, rel=1e-6)
    assert np.linalg.norm(east) == pytest.approx(2.0, rel=1e-4)  # 1 / cos(60°)


def _synthetic_dem(memfile, lat, lon, height_at):
    """Write a 60 x 60 km south polar stereographic DEM around (lat, lon) into `memfile`; return its path."""
    from rasterio.crs import CRS
    from src.terrain import local_axes
    crs = CRS.from_proj4("+proj=stere +lat_0=-90 +lat_ts=-90 +lon_0=0 +R=1737400 +units=m +no_defs")
    (x0, y0), _, _ = local_axes(crs, lat, lon)
    size, res = 600, 100.0
    transform = from_origin(x0 - size * res / 2, y0 + size * res / 2, res, res)
    cols, rows = np.meshgrid(np.arange(size) + 0.5, np.arange(size) + 0.5)
    xs, ys = transform @ (cols, rows)
    dem = height_at(np.hypot(xs - x0, ys - y0)).astype(np.float32)
    with memfile.open(driver="GTiff", width=size, height=size, count=1, dtype="float32", crs=crs,
                      transform=transform, nodata=np.nan) as dst:
        dst.write(dem, 1)
    return memfile.name


# Longitude -135° makes local north point diagonally on the polar map: the case where the read window used to shrink.
DIAGONAL = (-89.4, -135.0)


def test_read_window_reaches_full_radius_when_north_is_diagonal():
    from rasterio.io import MemoryFile
    from src.terrain import _horizons
    ring = lambda d: np.where((d > 8500) & (d < 9500), 500.0, 0.0)
    with MemoryFile() as memfile:
        url = _synthetic_dem(memfile, *DIAGONAL, ring)
        horizon = _horizons(*DIAGONAL, np.zeros(1), np.zeros(1), 2.0, 9_600.0, rings=[(url, 1, 0.0, 9_600.0)])[0]
    expected = elevation_angle(8500, 500.0, 2.0)
    assert horizon == pytest.approx(np.full(360, expected), abs=0.1)  # the ring is seen in every direction


def test_decimated_ring_sees_the_same_terrain():
    from rasterio.io import MemoryFile
    from src.terrain import _horizons
    ring = lambda d: np.where((d > 8000) & (d < 10000), 500.0, 0.0)
    with MemoryFile() as memfile:
        url = _synthetic_dem(memfile, *DIAGONAL, ring)
        rings = [(url, 1, 0.0, 5_000.0), (url, 2, 5_000.0, 12_000.0)]
        horizon = _horizons(*DIAGONAL, np.zeros(1), np.zeros(1), 2.0, 12_000.0, rings=rings)[0]
    assert horizon == pytest.approx(np.full(360, elevation_angle(8000, 500.0, 2.0)), abs=0.3)


def test_point_without_terrain_data_raises():
    from rasterio.io import MemoryFile
    from src.terrain import _horizons
    with MemoryFile() as memfile:
        url = _synthetic_dem(memfile, *DIAGONAL, lambda d: np.full(d.shape, np.nan))
        with pytest.raises(ValueError, match="No terrain data"):
            _horizons(*DIAGONAL, np.zeros(1), np.zeros(1), 2.0, 5_000.0, rings=[(url, 1, 0.0, 5_000.0)])
