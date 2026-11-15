"""What there is to see and read at each Catalog Site, for the Site Card's Overview tab. Owner: Gabriel.

Every image comes from the NASA Image and Video Library (images.nasa.gov), with its credit in the caption and a link
to its page there. Images of uncertain origin or with reuse limits (LROC featured images, Wikimedia Commons copies,
the Apollo 15 "Malapert" photo, the Faustini and Diviner images) are left out.
A place is (title, text, [(image URL, caption with credit, source page)]).
"""
from src.sites import ARTEMIS_2022_SOURCE, ARTEMIS_2024_SOURCE, POLAR_SOURCE

_ASSETS, _DETAILS = "https://images-assets.nasa.gov/image/", "https://images.nasa.gov/details/"


def _nasa(nasa_id, size, caption):
    return f"{_ASSETS}{nasa_id}/{nasa_id}~{size}.jpg", caption, _DETAILS + nasa_id


_LRO_MOSAIC = _nasa("PIA13523", "medium",
                    "The south polar region in a mosaic from LRO's Wide Angle Camera, polar stereographic, with the "
                    "pole at the center. NASA/GSFC/Arizona State University")
_CLEMENTINE_MOSAIC = _nasa("PIA00001", "medium",
                           "The south polar region in a mosaic of about 1,500 Clementine images (1994), with the "
                           "pole at the center. NASA/JPL/USGS")
_SHACKLETON = (
    "Shackleton crater",
    "A crater about 21 km wide with the lunar south pole on its rim. Parts of its interior remain in permanent "
    "shadow. A 2012 analysis of laser reflectance from NASA's Lunar Reconnaissance Orbiter (LRO) was consistent with "
    "up to about 22% ice in a very thin surface layer, but this indirect interpretation does not establish an "
    "accessible ice deposit. Selected rim points receive sunlight for much of the studied period.",
    [_LRO_MOSAIC, _CLEMENTINE_MOSAIC],
)
_CONNECTING_RIDGE = (
    "Connecting Ridge",
    "The ridge that links the rims of Shackleton and de Gerlache craters. Standing above the ground around it, it "
    "catches sunlight that lower terrain misses: selected elevated points on it have high modeled illumination over "
    "the periods studied, though none is permanently sunlit.",
    [_LRO_MOSAIC],
)

PLACES = {
    "Shackleton Crater (Rim)": _SHACKLETON,
    "Shackleton Rim S2": _SHACKLETON,
    "Connecting Ridge C1": _CONNECTING_RIDGE,
    "Connecting Ridge C2": _CONNECTING_RIDGE,
    "Malapert Massif (Summit)": (
        "Malapert Massif",
        "A mountain massif whose slopes rise several kilometres above the plains around it, on the side of the "
        "south polar region that faces Earth: seen from Earth, it sits at the edge of the Moon's disk. This Catalog "
        "Site marks a regional study center, not a verified summit.",
        [_nasa("PIA12953", "small",
               "Near the summit, seen by LRO with the Sun low: patterns thought to form as loose soil slowly creeps "
               "downhill. NASA/GSFC/Arizona State University")],
    ),
    "Faustini Crater (Rim)": (
        "Faustini crater",
        "A crater about 40 km wide, parts of whose interior are permanently shadowed: cold traps where water ice may "
        "be preserved, which does not establish ice at this Catalog Site. Faustini Rim A is a stretch of its rim.",
        [_CLEMENTINE_MOSAIC],
    ),
    "Haworth": (
        "Haworth crater",
        "A crater about 51 km wide (LRO-based measurement) near the south pole, parts of whose interior are "
        "permanently shadowed: cold traps where water ice may be preserved, which does not establish ice at this "
        "Catalog Site.",
        [_CLEMENTINE_MOSAIC],
    ),
    "Apollo 11 (Tranquility Base)": (
        "What is there",
        "The Lunar Module Eagle landed here on 20 July 1969. Its descent stage, the lower half that served as the "
        "launch pad for the return to orbit, is still on the surface.",
        [_nasa("as11-40-5927", "medium",
               "Buzz Aldrin beside Eagle, photographed by Neil Armstrong (AS11-40-5927). NASA"),
         _nasa("PIA12909", "orig", "The landing site seen from orbit by NASA's Lunar Reconnaissance Orbiter in 2009. "
               "NASA/GSFC/Arizona State University")],
    ),
}


def _regional_overview(title, geography, in_2024=False, naming_source=None):
    """Regional context, not an exact-coordinate photograph or a landing assessment."""
    history = ("This region was included in NASA's historical 2022 Artemis III candidate list. "
               "The Catalog Site is the Data Book's representative region center, not a verified "
               "summit or landing point. ")
    sources = f"[NASA 2022]({ARTEMIS_2022_SOURCE}) · [Coordinate table]({POLAR_SOURCE})"
    if in_2024:
        history += "The associated region also appears in NASA's revised 2024 list. "
        sources += f" · [NASA 2024]({ARTEMIS_2024_SOURCE})"
    if naming_source:
        sources += f" · [Name and geographic context]({naming_source})"
    image = _nasa("PIA13523", "medium",
                  "Regional context: LROC Wide Angle Camera mosaic of the lunar south polar region, "
                  "not a close-up or marker of this Catalog Site's exact coordinates. "
                  "NASA/GSFC/Arizona State University")
    return title, geography + " " + history + "Sources: " + sources, [image]


PLACES.update({
    "Peak Near Shackleton": _regional_overview(
        "Peak Near Shackleton",
        "A high-terrain study region near Shackleton crater. Its name describes the surrounding "
        "terrain; the catalog coordinate is not a surveyed peak. Local ridges can change the Terrain Horizon.",
    ),
    "Connecting Ridge Extension": _regional_overview(
        "Connecting Ridge Extension",
        "A study region extending the Connecting Ridge area near the lunar south pole. It is distinct "
        "from the Connecting Ridge regional center and from the specific Gläser C1/C2 study points.",
    ),
    "de Gerlache Rim 1": _regional_overview(
        "de Gerlache Rim 1",
        "One of two named study regions around de Gerlache crater's rim. Elevated terrain and nearby "
        "crater walls make sunlight and Earth Visibility dependent on the precise position and time.",
    ),
    "de Gerlache Rim 2": _regional_overview(
        "de Gerlache Rim 2",
        "A second study region associated with de Gerlache crater's rim, separate from Rim 1. "
        "A regional rim name does not establish that every point lies on the crest.",
        in_2024=True,
    ),
    "de Gerlache-Kocher Massif": _regional_overview(
        "de Gerlache-Kocher Massif",
        "A south polar massif study region associated with de Gerlache and Kocher craters. Its raised "
        "terrain is useful context for exploring how topography changes the visible Sun and Earth.",
    ),
    "Leibnitz Beta Plateau": _regional_overview(
        "Mons Mouton — historical Leibnitz Beta Plateau region",
        "Leibnitz Beta was an informal name for the mountain now officially named Mons Mouton, "
        "near Nobile crater. The catalog keeps its historical identifier and center. NASA's 2024 "
        "list distinguishes Mons Mouton and Mons Mouton Plateau; this older coordinate does not "
        "define either revised region's boundaries.",
        in_2024=True, naming_source="https://svs.gsfc.nasa.gov/5074/",
    ),
    "Nobile Rim 1": _regional_overview(
        "Nobile Rim 1",
        "A study region associated with Nobile crater's rim in the south polar highlands. "
        "Nearby slopes and crater walls affect the Terrain Horizon; the regional name alone "
        "does not determine illumination at a particular point.",
        in_2024=True,
    ),
    "Nobile Rim 2": _regional_overview(
        "Nobile Rim 2",
        "A separate Nobile rim study region, with a different representative center from Rim 1. "
        "Comparisons should use each location's modeled conditions rather than assuming equal "
        "sunlight or Earth Visibility across the rim.",
        in_2024=True,
    ),
    "Amundsen Rim": _regional_overview(
        "Amundsen Rim",
        "A study region associated with Amundsen crater's rim near the south pole. "
        "The catalog center describes a region of interest, not the crater center or a "
        "topographically verified crest.",
    ),
})
