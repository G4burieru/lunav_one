"""Curated lunar sites. Owner: Renata.

Degrees: latitude positive north; longitude positive east, in [-180, 180].
Polar entries are representative region centers, not approved landing points.
Source frame: lunar Mean Earth (MOON_ME); no frame transformation is applied.
"""

COORDINATE_CONVENTION = "Lunar Mean Earth; degrees; north-positive latitude; east-positive longitude [-180, 180]"
POLAR_SOURCE = (
    "https://ntrs.nasa.gov/api/citations/20230007818/downloads/"
    "ACD-50044%20Lunar%20Surface%20Data%20Book%20Rev%20A.pdf"
)


def _region(name, lat, lon, source_id, page, description, science, exploration):
    return {
        "name": name, "lat": lat, "lon": lon, "description": description,
        "scientific_context": science, "exploration_context": exploration,
        "coordinate_source": POLAR_SOURCE,
        "source_location": f"Table A2-2, printed page {page}, {source_id}",
        "coordinate_convention": COORDINATE_CONVENTION,
        "coordinate_kind": "Representative region center from DEM polygon",
    }


LUNAR_SITES = {
    "Shackleton Crater (Rim)": _region(
        "Shackleton Rim", -89.7668, -171.87, "R04 / Site04", 58,
        "Representative region on Shackleton's rim near the south pole.",
        "Terrain-dependent illumination near polar cold traps motivates topographic studies.",
        "LOLA south-pole exploration study region Site04; not a confirmed landing point.",
    ),
    "Malapert Massif (Summit)": _region(
        "Malapert Massif", -85.9948, -0.23578, "R23 / Site23", 58,
        "Representative Malapert Massif region center, not a measured summit point.",
        "Elevated polar terrain supports studies of illumination and Earth line of sight.",
        "Included in NASA's 2022 Artemis III candidate-region list; historical context only.",
    ),
    "Faustini Crater (Rim)": _region(
        "Faustini Rim A", -87.8897, 90.0, "LM7", 57,
        "Representative point in the Faustini Rim A study region.",
        "Polar rim terrain provides context for studies of shadow, cold traps and volatiles.",
        "Included in NASA's 2022 Artemis III candidate-region list; historical context only.",
    ),
    "Haworth": _region(
        "Haworth", -86.7639, -22.777, "Haworth", 57,
        "Haworth DEM study-region center; not the crater center or floor.",
        "LOLA topography supports investigation of polar terrain and horizon obstruction.",
        "NASA GSFC south-pole DEM study region; no mission landing designation implied.",
    ),
    "Apollo 11 (Tranquility Base)": {
        "name": "Apollo 11 (Tranquility Base)", "lat": 0.67416, "lon": 23.47314,
        "description": "Historic equatorial landing site, outside the south-pole map.",
        "scientific_context": "Historical comparison baseline; not a calibration of this tool.",
        "exploration_context": "Apollo 11 crewed landing in 1969.",
        "coordinate_source": "https://nssdc.gsfc.nasa.gov/planetary/lunar/lunar_sites.html",
        "source_location": "Apollo 11 Lunar Module row (Wagner et al., 2017)",
        "coordinate_convention": COORDINATE_CONVENTION,
        "coordinate_kind": "Lunar module landing location",
    },
}
