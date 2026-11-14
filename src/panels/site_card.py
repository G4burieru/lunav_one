"""Site Card: one Catalog Site or Custom Site over 2027–2028 (docs/UI_OVERHAUL.md, tasks B2 and B5).
Owner: Gabriel."""
import pandas as pd
import streamlit as st

from src.charts import plot_earth_visibility, plot_monthly, plot_sun_elevation
from src.metrics import (earth_visible_hours, hours_until_earthset, hours_until_sunset, monthly_summary,
                         site_summary, sunlight_hours)
from src.panels import texts
from src.panels.common import (CUSTOM, KIND_LABELS, SELECTED, data_note, format_countdown, format_duration, header,
                               icon, open_panel, ordinal, rank, select_site, selected_instant, two_years)
from src.sites import LUNAR_SITES

CHART_DAYS = 28  # the Sun & Earth tab shows this many days around the selected instant


def grid(summary):
    """Sun and Earth, on average and in the worst case, over the Explorer's Analysis Window."""
    whole = "All of 2027–2028"  # a run as long as the window: never lit, or Earth never in view
    night = whole if summary["sunlight_pct"] == 0 else format_duration(summary["longest_night_h"])
    absence = whole if summary["earth_visible_pct"] == 0 else format_duration(summary["longest_earth_absence_h"])
    average, worst = st.columns(2)
    average.caption("On average")
    worst.caption("Worst case")
    average.metric(f"{icon('sun')} Sunlight", f"{summary['sunlight_pct']:.0f}%", help=texts.SUNLIGHT_HELP,
                   border=True)
    worst.metric(f"{icon('night')} Longest night", night, help=texts.LONGEST_NIGHT_HELP, border=True)
    average.metric(f"{icon('earth')} Earth visible", f"{summary['earth_visible_pct']:.0f}%", help=texts.EARTH_HELP,
                   border=True)
    worst.metric(f"{icon('no-earth')} Longest without Earth", absence, help=texts.LONGEST_EARTH_ABSENCE_HELP,
                 border=True)


def rank_sentence(summary, custom):
    sun, earth = rank("sunlight_pct", summary["sunlight_pct"]), rank("earth_visible_pct", summary["earth_visible_pct"])
    places = f"{ordinal(sun)} for sunlight and {ordinal(earth)} for Earth visibility"
    if custom:
        return f"Next to the {len(LUNAR_SITES)} Catalog Sites it would rank {places}."
    return f"{places[0].upper()}{places[1:]} among the {len(LUNAR_SITES)} Catalog Sites."


def instant_line(df, at):
    """What the Sun and Earth are doing at the time bar's instant."""
    row = df[df["time"] == at].iloc[0]
    fraction = row["illumination_fraction"]
    if fraction == 0:
        sun = "Sun down"
    else:
        sun = "Sun up" if fraction >= 0.995 else f"Sun partly hidden ({fraction:.0%} of the disk)"
        hours = hours_until_sunset(df, at)
        sun += ", no sunset before 2029" if hours is None else f", sunset in {format_countdown(hours, 'now')}"
    if row["earth_elevation"] > row["earth_horizon"]:
        hours = hours_until_earthset(df, at)
        earth = "Earth in view, " + ("no Earthset before 2029" if hours is None
                                     else f"Earthset in {format_countdown(hours, 'now')}")
    else:
        earth = "Earth below the horizon"
    return f"**{at:%Y-%m-%d %H:%M} UTC** · {sun} · {earth}"


def overview(site):
    if "coordinate_source" not in site:
        st.caption("A Custom Site has no catalog context. Use Plan here to try another Asset Height or Elevation "
                   "Mask.")
        return
    if "coordinate_meaning" in site:
        st.caption(f"Coordinate meaning: {site['coordinate_meaning']}")
    with st.expander("Scientific and exploration context"):
        if "scientific_context" in site:
            st.markdown(f"**Science.** {site['scientific_context']}")
        if "exploration_context" in site:
            st.markdown(f"**Exploration.** {site['exploration_context']}")
        if "topographic_validation" in site:
            st.markdown(f"**Validation.** {site['topographic_validation']}")
        sources = [f"[Coordinate source]({site['coordinate_source']})" if "coordinate_source" in site else None,
                   site.get("source_location"),
                   f"[Exploration source]({site['exploration_source']})" if "exploration_source" in site else None]
        st.caption(" · ".join(s for s in sources if s) or "No sources recorded.")


def sun_and_earth(df, at, summary):
    span = pd.Timedelta(days=CHART_DAYS)
    start = min(max(at - span / 2, df["time"].iloc[0]), df["time"].iloc[-1] - span)  # full span near the edges
    window = df[(df["time"] >= start) & (df["time"] < start + span)]
    st.caption(f"The {CHART_DAYS} days around the selected instant: the Sun shines "
               f"{100 * sunlight_hours(window) / len(window):.0f}% of the time and Earth is in view "
               f"{100 * earth_visible_hours(window) / len(window):.0f}% of the time.")
    st.plotly_chart(plot_sun_elevation(window, at), width="stretch", key="card_sun")
    st.plotly_chart(plot_earth_visibility(window, at), width="stretch", key="card_earth")
    # Without the terrain columns, sunlight_hours falls back to the ideal horizon: shows what relief changes.
    ideal = 100 * sunlight_hours(df.drop(columns=["sun_horizon", "illumination_fraction"])) / len(df)
    st.caption(f"Without terrain, sunlight over 2027–2028 would be {ideal:.0f}% instead of "
               f"{summary['sunlight_pct']:.0f}%.")
    if df.attrs.get("terrain"):
        data_note(df)


def seasons(df):
    st.caption("Monthly sunlight and Earth visibility over 2027–2028. The Moon's small axial tilt still shifts "
               "polar sunlight by season.")
    st.plotly_chart(plot_monthly(monthly_summary(df), full_month_hours=28 * 24), width="stretch", key="card_seasons")


def render():
    selected, custom = st.session_state.get(SELECTED), st.session_state.get(CUSTOM)
    site = LUNAR_SITES[selected] if selected else {"name": "Custom Site", "lat": custom["lat"],
                                                    "lon": custom["lon"], "description": texts.CUSTOM_SITE}
    header()
    back, plan = st.columns(2)
    back.button("Catalog", icon=":material/arrow_back:", key="card_back", on_click=select_site, args=(None,),
                width="stretch")
    plan.button("Plan here", icon=":material/edit_location_alt:", key="card_plan", on_click=open_panel,
                args=("planner",), type="primary", width="stretch")
    st.markdown(f"### {site['name']}")
    kind = KIND_LABELS.get(site.get("coordinate_kind"), "Custom Site" if custom else "Unspecified")
    st.caption(f"{kind} · {site['lat']:.4f}°, {site['lon']:.4f}° E")
    st.write(site["description"])

    df = two_years(site["lat"], site["lon"], catalog_site=bool(selected))
    if df is None:
        return
    if not df.attrs.get("terrain"):
        st.warning(texts.NO_TERRAIN)
    summary = site_summary(df)
    grid(summary)
    st.markdown(rank_sentence(summary, custom=not selected))
    at = selected_instant(df)
    st.markdown(instant_line(df, at))

    tab_overview, tab_sun_earth, tab_seasons = st.tabs(["Overview", "Sun & Earth", "Seasons"])
    with tab_overview:
        overview(site)
    with tab_sun_earth:
        sun_and_earth(df, at, summary)
    with tab_seasons:
        seasons(df)
