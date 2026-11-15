"""Layers panel: NASA visibility maps over the south polar map (docs/UI_OVERHAUL.md, task B7). Owner: Gabriel."""
import streamlit as st

from src.colors import EARTH_RAMP, SUN_RAMP, css_gradient
from src.panels import texts
from src.panels.common import OVERLAYS, VIEW_CHOICE, VIEWS

# name: (label, ramp, explanation). The images are static/overlays/<name>_<extent>.png (scripts/render_overlays.py).
LAYERS = {"sun": ("Sunlight", SUN_RAMP, texts.SUN_LAYER), "earth": ("Earth visibility", EARTH_RAMP, texts.EARTH_LAYER)}


def toggle(name):
    """Show or hide a layer. The layers cover the south polar map, so showing one switches the view to it."""
    shown = set(st.session_state.get(OVERLAYS, ())) ^ {name}
    st.session_state[OVERLAYS] = sorted(shown)
    if name in shown:
        st.session_state[VIEW_CHOICE] = VIEWS[1]


def render():
    st.markdown("### Layers")
    st.caption("NASA Goddard maps over the south polar map, from 65°S to the pole, sharpest near the pole. NASA "
               "publishes them only for the polar regions. They stay on while you use the other panels.")
    shown = st.session_state.get(OVERLAYS, ())
    for name, (label, ramp, text) in LAYERS.items():
        with st.container(border=True):
            # No icon in the label: a switch is named after its label, icon markdown included.
            st.toggle(label, value=name in shown, key=f"layer_{name}", on_change=toggle, args=(name,))
            st.html(f'<div style="display:flex;align-items:center;gap:8px;font-size:0.8rem;opacity:0.8">0%'
                    f'<div style="flex:1;height:10px;border-radius:5px;background:{css_gradient(ramp)}"></div>'
                    "100%</div>")
            st.caption(text)
