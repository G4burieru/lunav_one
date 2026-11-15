"""What there is to see and read at each Catalog Site, for the Site Card's Overview tab. Owner: Gabriel.

Every image comes from the NASA Image and Video Library (images.nasa.gov), with its credit in the caption and a link
to its page there. Images of uncertain origin or with reuse limits (LROC featured images, Wikimedia Commons copies,
the Apollo 15 "Malapert" photo, the Faustini and Diviner images) are left out.
A place is (title, text, [(image URL, caption with credit, source page)]).
"""
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
