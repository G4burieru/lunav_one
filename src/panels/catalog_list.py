"""Catalog panel: search and the Catalog Sites to choose from (docs/UI_OVERHAUL.md, task B1). Owner: Gabriel."""
import streamlit as st

from src.panels import texts
from src.panels.common import (KIND_LABELS, catalog_summaries, format_duration, header, parse_coordinates,
                               select_custom, select_site, site_label)
from src.sites import LUNAR_SITES

SEARCH, SEARCH_ERROR = "search", "search_error"
SORTS = {"Sunlight": ("sunlight_pct", False), "Earth visibility": ("earth_visible_pct", False),
         "Longest night": ("longest_night_h", True), "Name": (None, True)}  # column, ascending


def on_search():
    value = st.session_state[SEARCH]
    st.session_state[SEARCH] = None
    if value in LUNAR_SITES:
        select_site(value)
    elif (point := parse_coordinates(value)) is not None:
        select_custom(*point)
    elif value:
        st.session_state[SEARCH_ERROR] = value


def render():
    header()
    st.selectbox("Search", list(LUNAR_SITES), index=None, format_func=site_label, accept_new_options=True,
                 placeholder="Search a site, or type coordinates: -89.44, -137.17", key=SEARCH,
                 on_change=on_search, label_visibility="collapsed")
    if error := st.session_state.pop(SEARCH_ERROR, None):
        st.error(f"“{error}” is neither a Catalog Site nor a latitude, longitude pair such as -89.44, -137.17.")
    st.caption(texts.INTRO)

    sort = st.segmented_control("Sort by", list(SORTS), default="Sunlight", key="catalog_sort") or "Sunlight"
    column, ascending = SORTS[sort]
    summaries = catalog_summaries()
    keys = sorted(LUNAR_SITES, key=site_label) if column is None else \
        summaries.sort_values(column, ascending=ascending).index
    for key in keys:
        site, summary = LUNAR_SITES[key], summaries.loc[key]
        with st.container(border=True):
            st.markdown(f"**{site_label(key)}**  \n{KIND_LABELS.get(site.get('coordinate_kind'), 'Unspecified')}")
            stats = f"☀️ Sunlight {summary['sunlight_pct']:.0f}% · 🌍 Earth visible {summary['earth_visible_pct']:.0f}%"
            if sort == "Longest night":
                stats += f" · 🌑 Longest night {format_duration(summary['longest_night_h'])}"
            st.caption(stats)
            st.button("Explore", key=f"explorer_pick_{key}", on_click=select_site, args=(key,), width="stretch")
