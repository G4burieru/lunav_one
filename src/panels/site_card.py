"""Site Card: the selected Catalog Site's information and data (docs/UI_OVERHAUL.md, task B2). Owner: Gabriel."""
import datetime

import pandas as pd
import streamlit as st

from src import catalog
from src.charts import plot_monthly
from src.metrics import earth_visible_hours, hours_until_sunset, monthly_summary, sunlight_hours
from src.panels.common import (CACHE_END, CACHE_START, KIND_LABELS, SELECTED, format_countdown, get_data, header,
                               is_cached, load, select_site, site_analysis, site_label, window_inputs)
from src.sites import LUNAR_SITES


def site_details(site):
    st.markdown(f"**{site.get('name', '')}** · {KIND_LABELS.get(site.get('coordinate_kind'), 'Unspecified')}")
    st.caption(f"Lat {site['lat']}° · Lon {site['lon']}° E")
    st.write(site["description"])
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
        st.caption(" · ".join(s for s in sources if s))


def catalog_comparison(date, days, selected=None):
    rows = []
    for key, site in LUNAR_SITES.items():
        try:
            df = get_data(site["lat"], site["lon"], str(date), days, catalog.ASSET_HEIGHT_M)
        except Exception:
            continue
        rows.append({
            "Site": ("▶ " if key == selected else "") + site_label(key),
            "Type": KIND_LABELS.get(site.get("coordinate_kind"), "Unspecified"),
            "Sunlight (%)": 100 * sunlight_hours(df) / len(df),
            # Without terrain columns, sunlight_hours falls back to the ideal horizon: shows what relief changes.
            "Sunlight, ideal horizon (%)":
                100 * sunlight_hours(df.drop(columns=["sun_horizon", "illumination_fraction"])) / len(df),
            "Earth visibility (%)": 100 * earth_visible_hours(df) / len(df),
            "First Sunset in": format_countdown(hours_until_sunset(df, df["time"].iloc[0]), "Set at start"),
        })
    return pd.DataFrame(rows)


def render():
    """The selected site's catalog card followed by its data cards."""
    selected = st.session_state[SELECTED]
    site = LUNAR_SITES[selected]
    header()
    st.button("← Back to catalog", key="explorer_back", on_click=select_site, args=(None,))
    with st.container(border=True):
        site_details(site)

    st.markdown("#### ☀️ Sunlight and 📡 Earth visibility")
    with st.container(border=True):
        date, days = window_inputs("explorer")
        df = load(site["lat"], site["lon"], date, days)
        if df is not None:
            site_analysis("explorer", df, compact=True)

    st.markdown("#### 🗓️ Seasons")
    with st.container(border=True):
        seasons = load(site["lat"], site["lon"], CACHE_START, (CACHE_END - CACHE_START).days)
        if seasons is not None:
            st.caption(f"{CACHE_START} to {CACHE_END - datetime.timedelta(days=1)}, at {catalog.ASSET_HEIGHT_M:g} m "
                       "Asset Height with terrain. The Moon's small axial tilt still shifts polar sunlight by season.")
            st.plotly_chart(plot_monthly(monthly_summary(seasons), full_month_hours=28 * 24), width="stretch",
                            key="explorer_seasons")

    st.markdown("#### ⚖️ Compare Catalog Sites")
    with st.container(border=True):
        st.caption(f"Same window ({date}, {days} days) at {catalog.ASSET_HEIGHT_M:g} m Asset Height, with terrain. "
                   "Pick a 28-day window to see a full lunar day, where terrain matters most.")
        if is_cached(date, days):
            st.dataframe(
                catalog_comparison(date, days, selected), hide_index=True, width="stretch",
                column_config={
                    "Sunlight (%)": st.column_config.ProgressColumn(min_value=0, max_value=100, format="%.0f%%"),
                    "Sunlight, ideal horizon (%)": st.column_config.NumberColumn(format="%.0f%%"),
                    "Earth visibility (%)": st.column_config.ProgressColumn(min_value=0, max_value=100,
                                                                            format="%.0f%%"),
                },
            )
        else:
            st.info(f"The comparison uses pre-computed data only. Pick a window between {CACHE_START} and "
                    f"{CACHE_END}.")
