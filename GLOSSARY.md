# Lunar Landing Site Navigator

Describes sunlight and geometric Earth Visibility at lunar locations and dates for a Surface Asset.
The completed educational prototype does not calculate electrical power or certify landing safety
or operational communications.

## Language

### Application modes

**Explorer**:
The mode for learning about the Moon: browsing catalog sites, their context, and how they compare.
_Avoid_: Observation tab, overview

**Site Planner**:
The mode for placing a surface asset precisely and evaluating its sunlight and Earth visibility.
_Avoid_: Positioning tab, equipment tab

**Surface Asset**:
Any equipment placed on the lunar surface whose sunlight and Earth visibility we evaluate, such as a lander,
solar array, or antenna.
_Avoid_: Equipment, payload, observer

**Asset Height**:
The height of the surface asset's sensor or panel above the local ground; 2 m by default.
_Avoid_: Observer height, camera height

### Sites

**Catalog Site**:
A curated, named location, such as a studied point, a region center or a historical landing, whose terrain horizon
and ephemerides are pre-computed. None is a certified landing site.
_Avoid_: Landing site, preset, predefined location

**Custom Site**:
A location the user picks, by coordinates or on the map, that is not in the catalog.
_Avoid_: Manual coordinates, user location, pin

**Site Card**:
The panel that presents one selected site: what kind of location it is, where it is, and how much sunlight and
Earth visibility it gets.
_Avoid_: Landing site card, info box, popup

**Site Neighborhood**:
A sampled area around a location used by the Site Planner. Catalog neighborhoods have pre-computed
Terrain Horizons at 2 m Asset Height; supported Custom Sites and other heights can request live
polar calculations.
_Avoid_: Grid, surroundings

### Horizon and visibility

**Terrain Horizon**:
The elevation angle of the skyline seen from a site in each azimuth direction, formed by local topography
and lunar curvature.
_Avoid_: Local horizon, skyline profile

**Ideal Horizon**:
The 0° horizon of a smooth lunar sphere, ignoring topography.
_Avoid_: Flat horizon, geometric horizon

**Illumination Fraction**:
The fraction (0 to 1) of the solar disk that is above the terrain horizon at a given instant.
_Avoid_: Sunlit (as a yes/no), light percentage

**Sunset**:
The instant the illumination fraction reaches 0.
_Avoid_: Shadow onset

**Longest Night**:
The longest continuous period within the analysis window in which the illumination fraction is 0.
_Avoid_: Eclipse, darkness period, shadow duration

**Elevation Mask**:
The minimum angle Earth's center must clear above the terrain horizon to count as visible; 0° by default.
_Avoid_: Margin, cutoff angle

**Earth Visibility**:
Whether Earth's center is above the terrain horizon by at least the elevation mask.
_Avoid_: Line of sight, comms window (for a single instant)

**Earthset**:
The instant Earth visibility ends.
_Avoid_: Loss of signal

**Longest Earth Absence**:
The longest continuous period within the analysis window without Earth visibility.
_Avoid_: Blackout, comms outage, loss of signal

### Time

**Analysis Window**:
The period over which a site's sunlight and Earth visibility figures are computed: all of 2027–2028 in the
Explorer, and a start date and duration chosen by the user in the Site Planner.
_Avoid_: Date range, time range
