"""What there is to see and read at each Catalog Site, for the Site Card's Overview tab. Owner: Gabriel.

Every image is public domain: NASA, or NASA/GSFC/Arizona State University for the LRO camera. The browser loads
them from the NASA Image and Video Library or Wikimedia Commons, and each caption links to its source page.
A place is (title, text, [(image URL, caption with credit, source page)]).
"""
_COMMONS = "https://upload.wikimedia.org/wikipedia/commons/"
_FILE = "https://commons.wikimedia.org/wiki/File:"

_ILLUMINATION_MAP = (
    _COMMONS + "thumb/8/8e/South_Pole_Illumination_Map_%28LROC271%29.png/"
    "500px-South_Pole_Illumination_Map_%28LROC271%29.png",
    "How often each spot near the pole is sunlit, from many LRO images: the brighter, the more often. Shackleton "
    "crater is in the center, with the south pole on its rim at 9 o'clock. NASA/GSFC/Arizona State University",
    _FILE + "South_Pole_Illumination_Map_%28LROC271%29.png",
)
_TEMPERATURE_MAP = (
    _COMMONS + "thumb/a/ac/Lunar_south_pole_summer_annotated.jpg/960px-Lunar_south_pole_summer_annotated.jpg",
    "Surface temperature around the south pole at noon in southern summer, measured by LRO's Diviner instrument: "
    "the darker, the colder. The permanently shadowed crater floors stay the coldest. NASA",
    _FILE + "Lunar_south_pole_summer_annotated.jpg",
)
_SHACKLETON = (
    "Shackleton crater",
    "A crater about 20 km wide with the south pole on its rim. Its floor never sees the Sun: laser measurements "
    "from NASA's Lunar Reconnaissance Orbiter (LRO) suggest ice may make up as much as 22% of the surface material "
    "there. Points on its rim, like this one, are sunlit much of the time.",
    [(_COMMONS + "9/96/Mosaic_shackleton_crater.jpg",
      "Shackleton crater in LRO and ShadowCam images. ShadowCam, on Korea's Danuri orbiter, sees into the "
      "permanently shadowed floor. NASA/KARI/Arizona State University",
      _FILE + "Mosaic_shackleton_crater.jpg"),
     _ILLUMINATION_MAP],
)
_CONNECTING_RIDGE = (
    "Connecting Ridge",
    "The ridge that links the rims of Shackleton and de Gerlache craters. Standing above the ground around it, it "
    "catches sunlight that lower terrain misses, and its points are among the most often sunlit on the Moon.",
    [_ILLUMINATION_MAP,
     (_COMMONS + "thumb/0/05/Traversing_the_Shackleton_de_Gerlache_Ridge_%28LROC1247_-_content_geomap_snippet%29"
      ".png/500px-Traversing_the_Shackleton_de_Gerlache_Ridge_%28LROC1247_-_content_geomap_snippet%29.png",
      "Part of a geomorphic map of the Shackleton–de Gerlache ridge made from LRO images: each color is a kind of "
      "terrain. NASA/GSFC/Arizona State University",
      _FILE + "Traversing_the_Shackleton_de_Gerlache_Ridge_%28LROC1247_-_content_geomap_snippet%29.png")],
)

PLACES = {
    "Shackleton Crater (Rim)": _SHACKLETON,
    "Shackleton Rim S2": _SHACKLETON,
    "Connecting Ridge C1": _CONNECTING_RIDGE,
    "Connecting Ridge C2": _CONNECTING_RIDGE,
    "Malapert Massif (Summit)": (
        "Malapert Massif",
        "A mountain massif whose slopes rise several kilometres above the plains around it, on the side of the "
        "south polar region that faces Earth: seen from Earth, it sits at the edge of the Moon's disk.",
        [(_COMMONS + "thumb/3/31/AS15-96-13090_Malapert_mountain.jpg/500px-AS15-96-13090_Malapert_mountain.jpg",
          "Malapert mountain on the horizon (center), photographed from Apollo 15 in 1971; the south pole lies in "
          "the shadow to its left. NASA",
          _FILE + "AS15-96-13090_Malapert_mountain.jpg"),
         (_COMMONS + "thumb/1/1f/Near_the_Summit_of_Malapert_Mountain_%28LROC21%29.png/"
          "500px-Near_the_Summit_of_Malapert_Mountain_%28LROC21%29.png",
          "Near the summit, seen by LRO with the Sun low: ripples from the slow downslope creep of loose soil. The "
          "image is 2.4 km wide. NASA/GSFC/Arizona State University",
          _FILE + "Near_the_Summit_of_Malapert_Mountain_%28LROC21%29.png")],
    ),
    "Faustini Crater (Rim)": (
        "Faustini crater",
        "A crater about 40 km wide whose floor never sees the Sun: one of the cold traps near the south pole where "
        "water ice may survive. Faustini Rim A is a stretch of its rim.",
        [(_COMMONS + "d/d7/FaustiniCrater.jpg", "Faustini crater, imaged by LRO. NASA",
          _FILE + "FaustiniCrater.jpg"),
         _TEMPERATURE_MAP],
    ),
    "Haworth": (
        "Haworth crater",
        "A crater about 50 km wide near the south pole whose floor never sees the Sun: a cold trap where water ice "
        "may survive.",
        [_TEMPERATURE_MAP],
    ),
    "Apollo 11 (Tranquility Base)": (
        "What is there",
        "The Lunar Module Eagle landed here on 20 July 1969. Its descent stage, the lower half that served as the "
        "launch pad for the return to orbit, is still on the surface.",
        [("https://images-assets.nasa.gov/image/as11-40-5927/as11-40-5927~medium.jpg",
          "Buzz Aldrin beside Eagle, photographed by Neil Armstrong (AS11-40-5927). NASA",
          "https://images.nasa.gov/details/as11-40-5927"),
         ("https://images-assets.nasa.gov/image/PIA12909/PIA12909~orig.jpg",
          "The landing site seen from orbit by NASA's Lunar Reconnaissance Orbiter in 2009. NASA",
          "https://images.nasa.gov/details/PIA12909")],
    ),
}
