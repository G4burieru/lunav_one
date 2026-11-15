"""Curated lunar sites. Owner: Renata.

Degrees: latitude positive north; longitude positive east, in [-180, 180].
Catalog Sites support Explorer context and Site Planner analysis.
No entry certifies landing safety or permanent illumination. Coordinate reference
frames are recorded per source; no frame transformation or DEM validation is done.

Compatibility: legacy dictionary keys are retained. In particular, the key
"Malapert Massif (Summit)" identifies a region center, NOT a summit. The key
"Shackleton Crater (Rim)" now identifies Table 2 point 1 (local label S1),
replacing the old Site04 center (-89.7668, -171.87). Invalidate its cached data.

Twelve regional centers and Connecting Ridge C1/C2 represent the 13 historical
2022 candidate regions. The Shackleton points are additional study locations.
Specific study points do not replace original regional centers. No CLPS sites
are added here.
"""

COORDINATE_CONVENTION = "Lunar coordinates; degrees; north-positive latitude; east-positive longitude [-180, 180]"
POLAR_SOURCE = (
    "https://ntrs.nasa.gov/api/citations/20230007818/downloads/"
    "ACD-50044%20Lunar%20Surface%20Data%20Book%20Rev%20A.pdf"
)

ILLUMINATION_SOURCE = "https://ntrs.nasa.gov/api/citations/20170007365/downloads/20170007365.pdf"
ARTEMIS_SOURCE = "https://www.nasa.gov/news-release/nasa-adds-mission-to-artemis-lunar-program-updates-architecture/"
# NASA's Artemis III candidate landing regions: 13 in August 2022, refined to 9 in October 2024.
ARTEMIS_2022_SOURCE = "https://www.nasa.gov/news-release/nasa-identifies-candidate-regions-for-landing-next-americans-on-moon/"
ARTEMIS_2024_SOURCE = "https://www.nasa.gov/news-release/nasa-provides-update-on-artemis-iii-moon-landing-regions/"
ARTEMIS_2022 = "Included in NASA's 2022 Artemis III candidate-region list. "
ARTEMIS_2024 = "Included in NASA's 2022 list and kept in its refined 2024 list of nine regions. "
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
        "coordinate_reference_frame": "DE421 mean-Earth (MOON_ME); 1737.4 km reference sphere; aligned with Horizons lunar orientation and PGDA LOLA source coordinates",
        "coordinate_frame_sources": [
            "https://ssd.jpl.nasa.gov/horizons/manual.html#lunar-mean-earth-frame-of-de421",
            "https://pgda.gsfc.nasa.gov/products/78",
            "https://pgda.gsfc.nasa.gov/products/69",
        ],
        "coordinate_kind": "studied_point",
        "coordinate_meaning": "Specific point studied for illumination; not a landing certification",
        "source_longitude_east_360": source_lon,
        "study_asset_height_m": 2.0,
        "priority": "high",
        "topographic_validation": "Pending complete topographic validation; DE421 MOON_ME reference-frame compatibility confirmed",
    }


def _region(name, lat, lon, source_id, page, description, science, exploration, exploration_source=ARTEMIS_SOURCE):
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
        "exploration_source": exploration_source,
    }


def _artemis_region(name, lat, lon, source_id, page, description, science, in_2024=False):
    """One of NASA's 2022 Artemis III candidate regions, at its Table A2-2 center."""
    return _region(name, lat, lon, source_id, page, description, science,
                   (ARTEMIS_2024 if in_2024 else ARTEMIS_2022) + ARTEMIS_CONTEXT,
                   ARTEMIS_2024_SOURCE if in_2024 else ARTEMIS_2022_SOURCE)


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
        ARTEMIS_2024 + ARTEMIS_CONTEXT, ARTEMIS_2024_SOURCE,
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
        ARTEMIS_2024 + ARTEMIS_CONTEXT, ARTEMIS_2024_SOURCE,
    ),
    "Peak Near Shackleton": _artemis_region(
        "Peak Near Shackleton", -88.811, 123.6901, "R07 / Site07", 58,
        "Representative center of the Peak Near Shackleton study region.",
        "Elevated polar terrain supports studies of illumination and Earth line of sight.",
    ),
    "Connecting Ridge Extension": _artemis_region(
        "Connecting Ridge Extension", -89.0324, -101.999, "SL3", 58,
        "Representative center of the Connecting Ridge Extension study region.",
        "Elevated polar terrain supports studies of illumination and Earth line of sight.",
    ),
    "de Gerlache Rim 1": _artemis_region(
        "de Gerlache Rim 1", -88.6834, -67.9321, "R11 / Site11", 58,
        "Representative center of the de Gerlache Rim 1 study region.",
        "Polar rim terrain provides context for studies of shadow, cold traps and volatiles.",
    ),
    "de Gerlache Rim 2": _artemis_region(
        "de Gerlache Rim 2", -88.23, -64.6284, "SL2", 58,
        "Representative center of the de Gerlache Rim 2 study region.",
        "Polar rim terrain provides context for studies of shadow, cold traps and volatiles.",
        in_2024=True,
    ),
    "de Gerlache-Kocher Massif": _artemis_region(
        "de Gerlache-Kocher Massif", -85.8296, -116.322, "R42 / Site42", 58,
        "Representative center of the de Gerlache-Kocher Massif study region, not a measured summit.",
        "Elevated polar terrain supports studies of illumination and Earth line of sight.",
    ),
    "Leibnitz Beta Plateau": _region(
        "Leibnitz Beta Plateau", -85.4266, 31.74276, "R20 / Site20", 58,
        "Representative center of the historical 2022 Leibnitz Beta Plateau study region. "
        "Leibnitz Beta was an informal name for the mountain now officially named Mons Mouton; "
        "the regional center is not a verified summit. The legacy name and coordinates are retained.",
        "Elevated polar terrain supports studies of illumination and Earth line of sight. "
        "The mountain-name correspondence does not establish identical regional boundaries. "
        "Naming reference: https://svs.gsfc.nasa.gov/5074/.",
        ARTEMIS_2022 + "NASA revised the regional selection and nomenclature in 2024, listing "
        "Mons Mouton and Mons Mouton Plateau separately. Equivalence of this older polygon "
        "with either revised region is not established here; no automatic retention in the "
        "2024 list is claimed. "
        f"[NASA 2024 regional update]({ARTEMIS_2024_SOURCE}). " + ARTEMIS_CONTEXT,
        ARTEMIS_2022_SOURCE,
    ),
    "Nobile Rim 1": _artemis_region(
        "Nobile Rim 1", -85.4381, 37.36667, "R06 / Site06", 58,
        "Representative center of the Nobile Rim 1 study region.",
        "Polar rim terrain provides context for studies of shadow, cold traps and volatiles.",
        in_2024=True,
    ),
    "Nobile Rim 2": _artemis_region(
        "Nobile Rim 2", -83.954, 58.82206, "DM2", 57,
        "Representative center of the Nobile Rim 2 study region.",
        "Polar rim terrain provides context for studies of shadow, cold traps and volatiles.",
        in_2024=True,
    ),
    "Amundsen Rim": _artemis_region(
        "Amundsen Rim", -84.2287, 69.44396, "DM1", 57,
        "Representative center of the Amundsen Rim study region.",
        "Polar rim terrain provides context for studies of shadow, cold traps and volatiles.",
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
