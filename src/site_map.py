"""Schematic lunar south-pole map and offline preview. Owner: Renata."""
import math
from collections.abc import Mapping

import plotly.graph_objects as go

from src.sites import LUNAR_SITES


def plot_south_pole_map(selected_site=None, lat=None, lon=None):
    """Return a Plotly figure for latitudes -90 through -80 degrees.

    Accept a catalog key (or None). The existing app call (sites, lat, lon)
    remains supported. Radius is angular distance from the pole, not elevation.
    Longitude 0 is at the top; east increases clockwise (south-pole view).
    Coordinates outside the cap are reported and never plotted inside it.
    """
    sites = selected_site if isinstance(selected_site, Mapping) else LUNAR_SITES
    selected_name = "Selected coordinates"
    if not isinstance(selected_site, Mapping) and selected_site is not None:
        site = sites[selected_site]
        lat, lon = site["lat"], site["lon"]
        selected_name = site.get("name", selected_site)
    if (lat is None) != (lon is None):
        raise ValueError("Provide both latitude and longitude.")
    if lat is not None:
        if not (math.isfinite(lat) and -90 <= lat <= 90
                and math.isfinite(lon) and -180 <= lon <= 180):
            raise ValueError("Latitude must be [-90, 90] and longitude [-180, 180].")
    polar = {name: site for name, site in sites.items() if -90 <= site["lat"] <= -80}
    fig = go.Figure(go.Scatterpolar(
        r=[90 + site["lat"] for site in polar.values()],
        theta=[site["lon"] for site in polar.values()],
        text=[site.get("name", name) for name, site in polar.items()],
        customdata=[[
            site["lat"], site["lon"], site["description"],
            site.get("coordinate_kind", "unspecified"),
            site.get("coordinate_meaning", "Coordinate meaning not provided"),
            site.get("topographic_validation", "Validation status not provided"),
        ] for site in polar.values()],
        mode="markers+text", textposition="top center", name="Catalog Sites",
        marker=dict(size=10, color="#4ba3d3", symbol=[
            {"studied_point": "diamond", "region_center": "circle",
             "actual_landing": "square"}.get(site.get("coordinate_kind"), "circle")
            for site in polar.values()
        ]),
        hovertemplate=("<b>%{text}</b><br>Latitude: %{customdata[0]:.5f}°"
                       "<br>Longitude: %{customdata[1]:.5f}° E"
                       "<br>%{customdata[2]}<br>Type: %{customdata[3]}"
                       "<br>%{customdata[4]}<br>%{customdata[5]}<extra></extra>"),
    ))
    if lat is not None and lat <= -80:
        fig.add_trace(go.Scatterpolar(
            r=[90 + lat], theta=[lon], mode="markers", name=selected_name,
            customdata=[[lat, lon]], marker=dict(size=16, symbol="x", color="#e66b27"),
            hovertemplate="Latitude: %{customdata[0]:.5f}°<br>Longitude: %{customdata[1]:.5f}° E<extra>%{fullData.name}</extra>",
        ))
    elif lat is not None:
        fig.add_annotation(text="Selected location is outside the south-pole map (90–80° S).",
                           x=0.5, y=1.1, xref="paper", yref="paper", showarrow=False)
    fig.update_layout(
        title="Lunar south pole · schematic Catalog Site map", height=650,
        margin=dict(t=100, b=80),
        polar=dict(
            radialaxis=dict(range=[0, 10], tickvals=[0, 2, 4, 6, 8, 10],
                            ticktext=["90° S", "88° S", "86° S", "84° S", "82° S", "80° S"]),
            angularaxis=dict(rotation=90, direction="clockwise", tickvals=[0, 90, 180, 270],
                             ticktext=["0°", "90° E", "180°", "90° W"]),
        ),
        annotations=list(fig.layout.annotations) + [dict(
            text="Angular distance from pole · no imagery, relief or visibility calculation",
            x=0.5, y=-0.13, xref="paper", yref="paper", showarrow=False)],
    )
    return fig


if __name__ == "__main__":
    import argparse
    from pathlib import Path

    parser = argparse.ArgumentParser(description="Export an offline interactive lunar map.")
    parser.add_argument("--site", choices=list(LUNAR_SITES), default=None)
    parser.add_argument("--output", default="/tmp/lunar_south_pole.html")
    args = parser.parse_args()
    plot_south_pole_map(args.site).write_html(args.output, include_plotlyjs=True, auto_open=False)
    print(f"Map saved to {Path(args.output).resolve()}")
