"""Plotly charts built from the src/conditions.py DataFrame contract, and the south pole relief map. Owner: Igor."""
import base64
import io
import time
from html import escape
from textwrap import wrap

import numpy as np
import plotly.graph_objects as go
import rasterio
import rasterio.errors
from PIL import Image
from rasterio.crs import CRS
from rasterio.warp import transform as warp_transform

from src.site_map import SITE_TYPES
from src.terrain import GDAL_ENV, MOON_GEOGRAPHIC, MOON_RADIUS_M, SOUTH_POLE_80M

SUN_COLOR, EARTH_COLOR, TERRAIN_COLOR = "orange", "royalblue", "gray"
SELECTED_COLOR, SITE_COLOR = "#e66b27", "#4ba3d3"


def _elevation_chart(df, body, title, color, at=None, mask=0.0):
    """Body elevation against the terrain horizon in the body's direction (both relative to the ideal horizon)."""
    fig = go.Figure(go.Scatter(x=df["time"], y=df[f"{body}_elevation"], name=title, line_color=color))
    horizon = df.get(f"{body}_horizon")
    if horizon is not None:
        fig.add_trace(go.Scatter(x=df["time"], y=horizon + mask, name="Terrain horizon" + (" + mask" if mask else ""),
                                 line=dict(color=TERRAIN_COLOR, dash="dot"), fill="tozeroy"))
    fig.add_hline(y=0, line_dash="dash", line_width=1, annotation_text="Ideal horizon (0°)")
    if at is not None:
        fig.add_vline(x=at, line_color="gray")  # no annotation: Plotly fails to place it on datetime axes
    fig.update_layout(title=title, xaxis_title="Time (UTC)", yaxis_title="Elevation (°)",
                      legend=dict(orientation="h", y=-0.25), hovermode="x unified")
    return fig


def plot_sun_elevation(df, at=None):
    return _elevation_chart(df, "sun", "Sun Elevation", SUN_COLOR, at)


def plot_earth_visibility(df, at=None, mask=0.0):
    return _elevation_chart(df, "earth", "Earth Elevation", EARTH_COLOR, at, mask)


def plot_monthly(monthly, full_month_hours):
    """Grouped bars per month (src/metrics.monthly_summary); partial months at the edges are faded."""
    opacity = [1.0 if full else 0.4 for full in monthly["hours"] >= full_month_hours]
    fig = go.Figure([
        go.Bar(x=monthly.index, y=monthly["sunlight_pct"], name="Sunlight", marker=dict(color=SUN_COLOR,
               opacity=opacity), hovertemplate="%{x|%b %Y}: %{y:.0f}% sunlight<extra></extra>"),
        go.Bar(x=monthly.index, y=monthly["earth_visible_pct"], name="Earth visibility", marker=dict(
               color=EARTH_COLOR, opacity=opacity), hovertemplate="%{x|%b %Y}: %{y:.0f}% Earth visible<extra></extra>"),
    ])
    fig.update_layout(title="Seasons: monthly Sunlight and Earth Visibility", barmode="group",
                      yaxis=dict(title="% of the month", range=[0, 100]), xaxis=dict(dtick="M1", tickformat="%b\n%Y"),
                      legend=dict(orientation="h", y=-0.25))
    return fig


def plot_neighborhood(points, column, label):
    """Site Neighborhood map (src/conditions.neighborhood_summary): 100 m cells colored by `column`.

    The catalog site is at (0, 0); the best cell is starred. Each marker carries its row index as customdata.
    """
    best = points[column].idxmax()
    fig = go.Figure(go.Scatter(
        x=points["east_m"], y=points["north_m"], mode="markers", customdata=points.index, name=label,
        marker=dict(symbol="square", size=10, color=points[column], colorscale="Cividis", cmin=0, cmax=100,
                    colorbar=dict(title=f"{label} (%)")),
        text=[f"{v:.0f}%" for v in points[column]],
        hovertemplate="East %{x:.0f} m · North %{y:.0f} m<br>" + label + ": %{text}<extra></extra>",
    ))
    fig.add_trace(go.Scatter(x=[0], y=[0], mode="markers", name="Catalog Site", hoverinfo="skip",
                             marker=dict(symbol="x", size=14, color="#e66b27", line=dict(width=1, color="white"))))
    fig.add_trace(go.Scatter(x=[points.at[best, "east_m"]], y=[points.at[best, "north_m"]], mode="markers",
                             name=f"Best point ({points.at[best, column]:.0f}%)", customdata=[best],
                             marker=dict(symbol="star", size=18, color="white", line=dict(width=1, color="black"))))
    fig.update_layout(title=f"Site Neighborhood: {label}", height=560, xaxis_title="East (m)",
                      yaxis=dict(title="North (m)", scaleanchor="x"), legend=dict(orientation="h", y=-0.15),
                      clickmode="event+select")
    return fig


# South pole relief map ---------------------------------------------------------------------------------------
# The LOLA south pole DEM (80°S to the pole) is a polar stereographic COG with overviews, so the whole cap can be
# read at reduced resolution in a few seconds. Map coordinates are kilometres in the DEM's own projection, so
# sites sit exactly where the relief shows them (0° longitude up, 90° E to the right).
RELIEF_PIXELS = 950  # 1/8 overview of the 80 m DEM: 640 m per pixel
SOUTH_POLE_CRS = CRS.from_proj4(f"+proj=stere +lat_0=-90 +lat_ts=-90 +lon_0=0 +x_0=0 +y_0=0 +R={MOON_RADIUS_M} "
                                "+units=m +no_defs")  # the DEM's projection
SOUTH_POLE_HALF_KM = 304.0  # the DEM covers ±304 km, i.e. 80°S to the pole
ELEVATION_STOPS = [  # (elevation in m, RGB), similar to the LOLA color shaded relief
    (-7000, (68, 36, 120)), (-4000, (49, 92, 168)), (-1500, (54, 151, 160)), (0, (112, 182, 96)),
    (2000, (222, 205, 82)), (4500, (226, 128, 50)), (7000, (190, 60, 45)),
]


def load_south_pole_relief(attempts=4):
    """WebP data URI of the colored, shaded relief over SOUTH_POLE_HALF_KM. Raises on failure.

    Cells outside 80°S are transparent so the map is round. WebP keeps the transparency at a fraction of PNG's size.
    """
    for attempt in range(attempts):  # PGDA intermittently returns empty tile reads (see src/terrain.py)
        try:
            with rasterio.Env(**GDAL_ENV), rasterio.open(SOUTH_POLE_80M) as src:
                dem = src.read(1, out_shape=(RELIEF_PIXELS, RELIEF_PIXELS)).astype(float)
            break
        except rasterio.errors.RasterioIOError:
            if attempt == attempts - 1:
                raise
            time.sleep(2 * (attempt + 1))
    dem = np.nan_to_num(dem, nan=0.0)
    cell = 2000 * SOUTH_POLE_HALF_KM / RELIEF_PIXELS
    dz_dy, dz_dx = np.gradient(dem * 2.0, cell)  # 2x vertical exaggeration so relief reads at this scale
    slope = np.arctan(np.hypot(dz_dx, dz_dy))
    aspect = np.arctan2(-dz_dx, dz_dy)
    sun_az, sun_alt = np.radians(315), np.radians(35)
    shade = np.clip(np.sin(sun_alt) * np.cos(slope) + np.cos(sun_alt) * np.sin(slope) * np.cos(sun_az - aspect), 0, 1)
    heights, colors = zip(*ELEVATION_STOPS)
    rgb = np.stack([np.interp(dem, heights, [c[i] for c in colors]) for i in range(3)], axis=-1)
    rgb *= (0.3 + 0.7 * shade)[..., None]
    y, x = np.mgrid[-1:1:RELIEF_PIXELS * 1j, -1:1:RELIEF_PIXELS * 1j]
    alpha = np.where(np.hypot(x, y) <= 1.0, 255, 0)
    buffer = io.BytesIO()
    Image.fromarray(np.dstack([np.clip(rgb, 0, 255), alpha]).astype(np.uint8)).save(buffer, "WEBP", quality=85)
    return "data:image/webp;base64," + base64.b64encode(buffer.getvalue()).decode()


def _polar_km(lats, lons):
    xs, ys = warp_transform(MOON_GEOGRAPHIC, SOUTH_POLE_CRS, list(lons), list(lats))
    return np.array(xs) / 1000, np.array(ys) / 1000


def _hover(text):
    return "<br>".join(escape(line) for line in wrap(str(text), width=60))


def plot_south_pole_relief_map(sites, selected_key, relief_uri, height=760):
    """Clickable south pole map over the LOLA relief (a plain disk if `relief_uri` is None).

    Each Catalog Site marker carries its catalog key as customdata, for st.plotly_chart selections.
    """
    half_km = SOUTH_POLE_HALF_KM
    fig = go.Figure()
    if relief_uri is not None:
        fig.add_layout_image(source=relief_uri, xref="x", yref="y", x=-half_km, y=half_km,
                             sizex=2 * half_km, sizey=2 * half_km, sizing="stretch", layer="below")
    else:
        fig.add_shape(type="circle", x0=-half_km, y0=-half_km, x1=half_km, y1=half_km,
                      fillcolor="#1d2330", line_width=0, layer="below")

    # Graticule: latitude circles every 2°, meridians every 30°.
    for lat in (-82, -84, -86, -88):
        r = _polar_km([lat], [90])[0][0]
        fig.add_shape(type="circle", x0=-r, y0=-r, x1=r, y1=r,
                      line=dict(color="rgba(255,255,255,0.35)", width=1, dash="dot"))
        fig.add_annotation(x=r * 0.707, y=-r * 0.707, text=f"{-lat}° S", showarrow=False,
                           font=dict(size=10, color="rgba(255,255,255,0.75)"))
    for lon in range(0, 360, 30):
        x, y = _polar_km([-80], [lon])
        fig.add_shape(type="line", x0=0, y0=0, x1=x[0], y1=y[0], line=dict(color="rgba(255,255,255,0.2)", width=1))
    for lon, label, xanchor, yanchor in ((0, "0°", "center", "bottom"), (90, "90° E", "left", "middle"),
                                         (180, "180°", "center", "top"), (270, "90° W", "right", "middle")):
        x, y = _polar_km([-80], [lon])
        fig.add_annotation(x=x[0], y=y[0], text=label, showarrow=False, font=dict(size=11),
                           xanchor=xanchor, yanchor=yanchor)

    # Catalog Sites, one trace per coordinate kind so the legend doubles as the symbol key.
    polar = {k: s for k, s in sites.items() if s["lat"] <= -80}
    kinds = {}
    for k, s in polar.items():
        kinds.setdefault(s.get("coordinate_kind"), []).append(k)
    for kind, keys in kinds.items():
        label, symbol = SITE_TYPES.get(kind, ("Unspecified", "circle"))
        x, y = _polar_km([polar[k]["lat"] for k in keys], [polar[k]["lon"] for k in keys])
        fig.add_trace(go.Scatter(
            x=x, y=y, mode="markers", name=label, customdata=keys,
            marker=dict(symbol=symbol, size=11, color=SITE_COLOR, line=dict(width=1.5, color="white")),
            text=[f"<b>{escape(polar[k].get('name', k))}</b><br>{label} · {polar[k]['lat']:.4f}°, "
                  f"{polar[k]['lon']:.4f}° E<br>{_hover(polar[k]['description'])}" for k in keys],
            hovertemplate="%{text}<extra></extra>", unselected=dict(marker=dict(opacity=1)),
        ))
    if selected_key in polar:
        site = polar[selected_key]
        x, y = _polar_km([site["lat"]], [site["lon"]])
        symbol = SITE_TYPES.get(site.get("coordinate_kind"), ("Unspecified", "circle"))[1]
        fig.add_trace(go.Scatter(  # highlight on top, kept out of the legend so the symbol key stays neutral
            x=x, y=y, mode="markers", showlegend=False, hoverinfo="skip", customdata=[selected_key],
            marker=dict(symbol=symbol, size=17, color=SELECTED_COLOR, line=dict(width=2, color="white")),
            unselected=dict(marker=dict(opacity=1)),
        ))
        fig.add_annotation(x=x[0], y=y[0], text=f"<b>{escape(site.get('name', selected_key))}</b>", yshift=16,
                           showarrow=False, font=dict(color="white", size=13), bgcolor="rgba(0,0,0,0.55)")
    elif selected_key in sites:
        fig.add_annotation(x=0.5, y=1.0, xref="paper", yref="paper", showarrow=False,
                           text=f"{escape(sites[selected_key].get('name', selected_key))} is outside this map "
                                "(80°S to the pole).")

    # 100 km scale bar and credit.
    x0, y0 = -50, -half_km * 0.9  # inside the disk, centered at the bottom
    fig.add_shape(type="line", x0=x0, y0=y0, x1=x0 + 100, y1=y0, line=dict(color="white", width=3))
    fig.add_annotation(x=x0 + 50, y=y0, yshift=10, text="100 km", showarrow=False,
                       font=dict(size=11, color="white"))
    fig.add_annotation(x=1, y=0, xref="paper", yref="paper", xanchor="right", yanchor="bottom", showarrow=False,
                       text="Relief: LOLA 80 m south pole DEM (NASA PGDA) · click a site to explore it",
                       font=dict(size=10, color="rgba(255,255,255,0.6)"))

    pad = half_km * 1.15  # room for the meridian labels outside the disk
    fig.update_layout(
        height=height, margin=dict(l=0, r=0, t=10, b=0), dragmode="pan", clickmode="event+select",
        # constrain="domain" keeps the 1:1 aspect by shrinking the plot area, not by widening the ranges (which
        # Plotly would otherwise compound on every resize, shrinking the map).
        xaxis=dict(visible=False, range=[-pad, pad], constrain="domain"),
        yaxis=dict(visible=False, range=[-pad, pad], scaleanchor="x", constrain="domain"),
        legend=dict(orientation="h", y=0.02, x=0.01, bgcolor="rgba(0,0,0,0.45)"),
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
    )
    return fig
