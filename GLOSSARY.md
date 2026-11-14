# Lunar Landing Site Navigator

Evaluates candidate lunar landing sites and dates by how much sunlight (power) and Earth visibility
(direct-to-Earth communication) a surface asset would have.

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
A curated, named landing site whose terrain horizon and ephemerides are pre-computed.
_Avoid_: Preset, predefined location

**Custom Site**:
A latitude/longitude entered by the user that is not in the catalog.
_Avoid_: Manual coordinates, user location

**Site Neighborhood**:
The area around a catalog site whose terrain horizons are pre-computed for the Site Planner.
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

**Elevation Mask**:
The minimum angle Earth's center must clear above the terrain horizon to count as visible; 0° by default.
_Avoid_: Margin, cutoff angle

**Earth Visibility**:
Whether Earth's center is above the terrain horizon by at least the elevation mask.
_Avoid_: Line of sight, comms window (for a single instant)

**Earthset**:
The instant Earth visibility ends.
_Avoid_: Loss of signal
