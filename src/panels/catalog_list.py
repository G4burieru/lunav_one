"""Catalog panel: the Catalog Sites to choose from (docs/UI_OVERHAUL.md, task B1). Owner: Gabriel."""
import streamlit as st

from src.panels import texts
from src.panels.common import KIND_LABELS, header, select_site, site_label
from src.sites import LUNAR_SITES


def render():
    header()
    st.caption(texts.INTRO)
    st.caption("Click a site on the globe or the map, or pick one below.")
    for key, site in LUNAR_SITES.items():
        with st.container(border=True):
            st.markdown(f"**{site_label(key)}**  \n{KIND_LABELS.get(site.get('coordinate_kind'), 'Unspecified')}"
                        f" · {site['lat']:.2f}°, {site['lon']:.2f}° E")
            st.caption(site["description"])
            st.button("Explore", key=f"explorer_pick_{key}", on_click=select_site, args=(key,), width="stretch")
