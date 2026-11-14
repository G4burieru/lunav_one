# Why exploring the lunar south pole is difficult

Audience: educators, the public and the project team. This explanation describes
scientific principles, not a validation of the project's Catalog Sites.

## A low Sun makes the terrain matter

Near the lunar poles, sunlight arrives at a shallow angle. A ridge can intercept
that light and cast a long shadow across a nearby depression. A position that
looks promising on a regional map can therefore experience very different
lighting from another position a short distance away. Polar exploration requires
attention to both location and time. [NASA's south-pole environment overview](https://www.nasa.gov/reference/moonbase-environment/)
explains the relationship between terrain, lighting and surface operations.

Imagine a solar panel beside a wall: seeing the Sun above a smooth horizon does
not mean the panel can see past the wall. On the Moon, crater walls and ridges
play that role. **Terrain Horizon** is the elevation angle of that surrounding
terrain in each direction, including lunar curvature. **Ideal Horizon** is the
0° reference used when topography is ignored.

## Light is a fraction, not just a switch

**Illumination Fraction** describes how much of the Sun's disk is above the
Terrain Horizon: 0 means none and 1 means the whole disk. It is not an electrical
power estimate. Panel orientation, temperature, equipment efficiency, storage
and other engineering constraints also affect usable energy.

Asset Height matters: a panel two metres above ground can see past an obstruction
that blocks one at ground level. Gläser et al. studied illumination at both
heights; their Table 2 supplies our four priority points. Its simulations cover
2017–2037. Those published conditions are not new results produced by our app,
and they do not establish permanent illumination or certify a landing area.
See [Gläser et al. (2017), Table 2, PDF page 12](https://ntrs.nasa.gov/api/citations/20170007365/downloads/20170007365.pdf).

## Darkness can be scientifically valuable and operationally difficult

Some polar depressions remain in permanent shadow. Cold environments can retain
volatiles, including water ice, making them important exploration targets. The
presence, concentration and accessibility of resources must still be established
at a specific location; shadow alone is not an ice measurement. The
[Canadian Space Agency's explanation of lunar volatiles and rover challenges](https://www.asc-csa.gc.ca/eng/astronomy/moon-exploration/viper-rover-mapping-water-ice-on-moon.asp)
also describes the extreme lighting contrasts and temperature challenges facing
surface systems. We cite that background, not a mission schedule or a partnership.

## Seeing Earth is only one part of communicating

For this project, **Earth Visibility** means Earth's center clears the Terrain
Horizon by the chosen Elevation Mask. This geometric test is useful, but a working
radio link also needs compatible equipment, antenna pointing, adequate signal
strength and an available receiving system. An elevation curve alone cannot
prove communication performance. Likewise, **Sunset** in the glossary occurs
when Illumination Fraction reaches zero; the current countdown functions instead
use a simplified crossing of the Ideal Horizon.

## What Lunav One can explain today

A **Catalog Site** has a documented identity and coordinate meaning. Some entries
are specific illumination-study points, others are regional centers, and Apollo
11 is a historical landing location. A region center must not be presented as a
verified summit. All project-specific topographic checks remain pending.

The prototype displays a schematic polar map and live Sun/Earth elevation curves
from [JPL Horizons](https://ssd.jpl.nasa.gov/horizons/manual.html). Separate science
functions calculate Terrain Horizon and Illumination Fraction using terrain
arrays; the interface does not yet apply them to its displayed curves.
[LOLA products](https://pgda.gsfc.nasa.gov/products/78) provide topographic context,
while [LROC QuickMap](https://quickmap.lroc.im-ldi.com/) is a cartographic reference,
not an image layer currently embedded in our map.

**Explorer** is the planned mode for learning about Catalog Sites and their
context. **Site Planner** is the planned mode for evaluating a precisely placed
Surface Asset. Neither is a separate working mode in this version. Pre-computed
Terrain Horizons and ephemerides are also pending for this branch's catalog.

Illumination and Earth Visibility are two factors in exploration planning. A
complete landing assessment must also address slopes, obstacles, terrain
uncertainty and vehicle constraints. Lunav One currently supports education and
exploration of these questions; it does not identify safe or optimal landings.
