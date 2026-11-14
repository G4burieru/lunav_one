"""Curated lunar sites. Owner: Renata.

Degrees: latitude positive north; longitude positive east, in [-180, 180].
Catalog Sites support Explorer context and future Site Planner pre-computation.
No entry certifies landing safety or permanent illumination. Coordinate reference
frames are recorded per source; no frame transformation or DEM validation is done.

Compatibility: legacy dictionary keys are retained. In particular, the key
"Malapert Massif (Summit)" identifies a region center, NOT a summit. The key
"Shackleton Crater (Rim)" now identifies Table 2 point 1 (local label S1),
replacing the old Site04 center (-89.7668, -171.87). Invalidate its cached data.

Keep this initial set small: additional regional centers and CLPS landing
locations are deferred to avoid increasing automatic pre-computation on main.
"""

COORDINATE_CONVENTION = "Lunar coordinates; degrees; north-positive latitude; east-positive longitude [-180, 180]"
POLAR_SOURCE = (
    "https://ntrs.nasa.gov/api/citations/20230007818/downloads/"
    "ACD-50044%20Lunar%20Surface%20Data%20Book%20Rev%20A.pdf"
)

ILLUMINATION_SOURCE = "https://ntrs.nasa.gov/api/citations/20170007365/downloads/20170007365.pdf"
ARTEMIS_SOURCE = "https://www.nasa.gov/news-release/nasa-adds-mission-to-artemis-lunar-program-updates-architecture/"
ARTEMIS_CONTEXT = (
    "Historical lunar exploration context only; no current landing selection implied. "
    "NASA's 2026 architecture assigns Artemis III an Earth-orbit demonstration in 2027 "
    "and targets Artemis IV for the first Artemis crewed lunar landing in 2028."
)


def _studied_point(name, lat, source_lon, source_row):
    """Table 2 point at 2 m Asset Height; S1/S2 are catalog labels, not Table 3 clusters."""
    return {
        "name": name, "lat": lat, "lon": round(source_lon - 360.0, 2),
        "description": (
            f"{name}: specific illumination-study point at 2 m Asset Height. "
            "Project DEM validation pending; not a certified landing point."
        ),
        "scientific_context": (
            "Gläser et al. (2017), Table 2: illumination study at 2 m above ground "
            "over 2017-01-01 to 2037-01-01. No permanent illumination claimed. "
            "Study results are not forecasts computed by this application."
        ),
        "exploration_context": ARTEMIS_CONTEXT,
        "exploration_source": ARTEMIS_SOURCE,
        "coordinate_source": ILLUMINATION_SOURCE,
        "source_location": f"Table 2, PDF page 12, {source_row}",
        "coordinate_convention": COORDINATE_CONVENTION,
        "coordinate_reference_frame": "Source LOLA DTM; exact frame realization requires reconciliation with project DEM",
        "coordinate_kind": "studied_point",
        "coordinate_meaning": "Specific point studied for illumination; not a landing certification",
        "source_longitude_east_360": source_lon,
        "study_asset_height_m": 2.0,
        "priority": "high",
        "topographic_validation": "Pending validation against the project LOLA DEM and its reference frame",
    }


def _region(name, lat, lon, source_id, page, description, science, exploration):
    return {
        "name": name, "lat": lat, "lon": lon, "description": description,
        "scientific_context": science, "exploration_context": exploration,
        "coordinate_source": POLAR_SOURCE,
        "source_location": f"Table A2-2, printed page {page}, {source_id}",
        "coordinate_convention": COORDINATE_CONVENTION,
        "coordinate_kind": "region_center",
        "coordinate_meaning": "Representative region center from DEM polygon; not a measured summit or rim point",
        "coordinate_reference_frame": "Lunar Mean Earth (MOON_ME), PGDA DEM provenance",
        "priority": "context",
        "topographic_validation": "Pending: region center must not be used as a validated summit or landing point",
        "exploration_source": ARTEMIS_SOURCE,
    }


LUNAR_SITES = {
    "Shackleton Crater (Rim)": _studied_point(
        "Shackleton Rim S1", -89.6866, 197.19,
        "Shackleton first row; S1 is a local catalog label, not a Table 3 cluster ID",
    ),
    "Connecting Ridge C1": _studied_point(
        "Connecting Ridge C1", -89.4398, 222.83, "Connecting Ridge C1 row",
    ),
    "Connecting Ridge C2": _studied_point(
        "Connecting Ridge C2", -89.3130, 245.98, "Connecting Ridge C2 row",
    ),
    "Shackleton Rim S2": _studied_point(
        "Shackleton Rim S2", -89.7815, 204.70,
        "Shackleton second row; S2 is a local catalog label, not a Table 3 cluster ID",
    ),
    "Malapert Massif (Summit)": _region(
        "Malapert Massif", -85.9948, -0.23578, "R23 / Site23", 58,
        "Representative Malapert Massif region center, not a measured summit point.",
        "Elevated polar terrain supports studies of illumination and Earth line of sight.",
        "Included in NASA's 2022 Artemis III candidate-region list. " + ARTEMIS_CONTEXT,
    ),
    "Faustini Crater (Rim)": _region(
        "Faustini Rim A", -87.8897, 90.0, "LM7", 57,
        "Representative point in the Faustini Rim A study region.",
        "Polar rim terrain provides context for studies of shadow, cold traps and volatiles.",
        "Included in NASA's 2022 Artemis III candidate-region list. " + ARTEMIS_CONTEXT,
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
        "coordinate_kind": "actual_landing",
        "coordinate_meaning": "Lunar module landing location; historical example, not a safety certification",
        "coordinate_reference_frame": "LROC location reported by NASA NSSDC; no frame transformation applied",
        "priority": "context",
        "topographic_validation": "Historical position sourced; project DEM cross-check pending",
    },
}
