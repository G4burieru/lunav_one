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
