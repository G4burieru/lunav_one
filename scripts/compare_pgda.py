"""Compare catalog results with the NASA PGDA average Sun and Earth visibility maps (Mazarico et al. 2011).

Usage: python -m scripts.compare_pgda

The maps (https://pgda.gsfc.nasa.gov/products/69) give, per 60 m pixel from 85°S to the pole, the percentage of
hourly timesteps over 18.6 years in which any part of the solar or Earth disk is above the terrain, at the surface.
For like-for-like numbers, project values here use the same "any part of the disk" definition at the 2 m Asset
Height over 2027-2028. Reads pre-computed catalog data and a 3x3 pixel window per point from each map.
"""
import rasterio
from rasterio.warp import transform
from rasterio.windows import Window

from src.conditions import get_conditions
from src.sites import LUNAR_SITES
from src.terrain import GDAL_ENV, _read_chunk

MAPS = {
    "sun": "https://pgda.gsfc.nasa.gov/data/MoonIllumination/AVGVISIB_85S_060M_201608.TIF",
    "earth": "https://pgda.gsfc.nasa.gov/data/MoonIllumination/AVGVISIB_85S_060M_201608_EARTH.TIF",
}
EARTH_RADIUS_DEG = 0.95  # apparent angular radius of Earth from the Moon (6371 km at ~384,400 km)
# Best Site Neighborhood point for Earth Visibility (1600 m west, 100 m north of the Malapert center).
EXTRA = {"Malapert best neighborhood point": (-85.99115552, -0.99054738)}


def sample(url, points):
    """Map value (%) at each (lat, lon), plus the min and max of the 3x3 pixels (180 m) around it."""
    with rasterio.Env(**GDAL_ENV), rasterio.open(url) as src:
        xs, ys = transform("+proj=longlat +R=1737400 +no_defs", src.crs, [p[1] for p in points], [p[0] for p in points])
        out = []
        for x, y in zip(xs, ys):
            row, col = src.index(x, y)
            window = _read_chunk(src, Window(col - 1, row - 1, 3, 3), (3, 3)) * src.scales[0] * 100
            out.append((window[1, 1], window.min(), window.max()))
        return out


def main():
    points = {name: (s["lat"], s["lon"]) for name, s in LUNAR_SITES.items() if s["lat"] <= -85} | EXTRA
    maps = {body: sample(url, list(points.values())) for body, url in MAPS.items()}
    print(f"{'Point':34} {'Sun ours':>8} {'PGDA':>6} {'3x3 range':>13}   {'Earth ours':>10} {'PGDA':>6} {'3x3 range':>13}")
    for i, (name, (lat, lon)) in enumerate(points.items()):
        df = get_conditions(lat, lon, "2027-01-01", 731)
        sun = 100 * (df["illumination_fraction"] > 0).mean()
        earth = 100 * (df["earth_elevation"] - df["earth_horizon"] > -EARTH_RADIUS_DEG).mean()
        (s, s_lo, s_hi), (e, e_lo, e_hi) = maps["sun"][i], maps["earth"][i]
        print(f"{name:34} {sun:8.2f} {s:6.2f} {s_lo:6.2f}-{s_hi:6.2f}   {earth:10.2f} {e:6.2f} {e_lo:6.2f}-{e_hi:6.2f}"
              f"   [{df.attrs['source']}]")


if __name__ == "__main__":
    main()
