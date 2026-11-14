"""Plotly charts built from the src/conditions.py DataFrame contract. Owner: Igor."""
import plotly.graph_objects as go

SUN_COLOR, EARTH_COLOR, TERRAIN_COLOR = "orange", "royalblue", "gray"


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
