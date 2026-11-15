"""About panel (docs/UI_OVERHAUL.md, task B4). Owner: Gabriel."""
import streamlit as st

from src.panels import texts


def render():
    """The intro, then each section of texts.ABOUT_SECTIONS in a closed expander, so the panel reads as a list of
    topics instead of one long text."""
    st.markdown("### About")
    st.markdown(texts.ABOUT_INTRO)
    for title, text in texts.ABOUT_SECTIONS.items():
        with st.expander(title):
            st.markdown(text)
