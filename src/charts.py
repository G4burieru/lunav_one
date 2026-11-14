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

