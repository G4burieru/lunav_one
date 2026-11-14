"""About panel (docs/UI_OVERHAUL.md, task B4). Owner: Gabriel."""
import streamlit as st

from src.panels import texts


def render():
    st.markdown("### About")
    st.markdown(texts.ABOUT)
