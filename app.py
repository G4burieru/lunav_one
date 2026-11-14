"""Streamlit user interface. Owner: Igor."""
import datetime

import streamlit as st

from src.charts import plot_earth_visibility, plot_sun_elevation
from src.horizons_api import get_ephemerides_data
from src.site_map import plot_south_pole_map
from src.sites import LUNAR_SITES

st.set_page_config(page_title="Lunar Landing Site Navigator", page_icon="🌕", layout="wide")
st.title("🌕 Lunar Landing Site Navigator")
st.caption("Solar power and direct-to-Earth communication for lunar south pole landings | NASA Space Apps 2026")

get_data = st.cache_data(show_spinner=False)(get_ephemerides_data)

# Sidebar
st.sidebar.header("⚙️ Mission Settings")
custom = "Custom Coordinates"
selected_site = st.sidebar.selectbox("Candidate Landing Site", [*LUNAR_SITES, custom])

if selected_site == custom:
    lat = st.sidebar.number_input("Lunar Latitude (°)", -90.0, 90.0, -89.9, 0.1)
    lon = st.sidebar.number_input("Lunar Longitude (°)", -180.0, 180.0, 0.0, 0.1)
else:
    site = LUNAR_SITES[selected_site]
    lat, lon = site["lat"], site["lon"]
    st.sidebar.info(f"**Lat:** {lat}° | **Lon:** {lon}°\n\n_{site['description']}_")

landing_date = st.sidebar.date_input("Landing Date", datetime.date(2026, 12, 1))
duration_days = st.sidebar.slider("Analysis Window (Earth days)", 3, 28, 14)

with st.spinner("Computing ephemerides with JPL Horizons..."):
    try:
        df = get_data(lat, lon, str(landing_date), duration_days)
    except Exception as e:
        st.error(f"JPL Horizons request failed: {e}")
        st.stop()

# KPIs
sun_now, earth_now = df["sun_elevation"].iloc[0], df["earth_elevation"].iloc[0]
col1, col2, col3 = st.columns(3)
col1.metric("Solar Power", "☀️ Illuminated" if sun_now > 0 else "🌑 In Shadow", f"{sun_now:.2f}° elevation")
col2.metric("Earth Communication", "📡 Line of Sight" if earth_now > 0 else "🚫 No Line of Sight", f"{earth_now:.2f}° elevation")
col3.metric("Sunlight in Window", f"{(df['sun_elevation'] > 0).sum()} h")  # 1-hour time step

st.divider()

tab_map, tab_energy, tab_comm, tab_compare = st.tabs(
    ["🗺️ Map", "⚡ Power Generation", "📶 Direct-to-Earth Communication", "⚖️ Compare Sites"]
)
with tab_map:
    st.plotly_chart(plot_south_pole_map(LUNAR_SITES, lat, lon), width="stretch")
with tab_energy:
    st.caption("Above 0°, sunlight reaches the solar arrays (terrain not yet considered).")
    st.plotly_chart(plot_sun_elevation(df), width="stretch")
with tab_comm:
    st.caption("Above 0°, Earth is above the horizon and direct transmission is possible (terrain not yet considered).")
    st.plotly_chart(plot_earth_visibility(df), width="stretch")
with tab_compare:
    st.info("Coming soon: sunlight and Earth visibility hours for every site in the catalog.")
