"""Plotly charts built from the horizons_api.py DataFrame contract. Owner: Igor."""
import plotly.express as px


def _elevation_chart(df, column, title, color):
    fig = px.line(df, x="time", y=column, title=title, color_discrete_sequence=[color])
    fig.add_hline(y=0, line_dash="dash", annotation_text="Horizon (0°)")
    fig.update_layout(xaxis_title="Time (UTC)", yaxis_title="Elevation (°)")
    return fig


def plot_sun_elevation(df):
    return _elevation_chart(df, "sun_elevation", "Sun Elevation", "orange")


def plot_earth_visibility(df):
    return _elevation_chart(df, "earth_elevation", "Earth Elevation", "royalblue")

