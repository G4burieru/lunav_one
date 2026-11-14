"""Landing site map. Owner: Renata."""
import plotly.graph_objects as go


def plot_south_pole_map(sites, lat, lon):
    """Polar map of the south pole (radius = angular distance from the pole). Shows only latitudes below -80°."""
    polar = {name: s for name, s in sites.items() if s["lat"] <= -80}
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=[90 + s["lat"] for s in polar.values()],
        theta=[s["lon"] for s in polar.values()],
        mode="markers+text", text=list(polar), textposition="top center", name="Candidate sites",
    ))
    fig.add_trace(go.Scatterpolar(
        r=[90 + lat], theta=[lon], mode="markers", name="Selected site",
        marker=dict(size=14, symbol="x", color="red"),
    ))
    fig.update_layout(polar=dict(radialaxis=dict(range=[0, 10], title="degrees from pole")))
    return fig
