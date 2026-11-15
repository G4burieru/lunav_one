# Third-party sources, credits and licenses

Lunav One's [Apache-2.0 license](LICENSE) applies to the team's original code and
documentation. It does not relicense NASA or other third-party imagery, source
data, map services, publications or software. The collective project attribution
is in [NOTICE](NOTICE). This source inventory is not a replacement for upstream
license texts, copyright notices or product-specific conditions.

## NASA data, map services and images

| Resource | Role and credit | Original source / terms |
|---|---|---|
| JPL Horizons | Sun/Earth observer ephemerides; NASA/JPL Solar System Dynamics | [Horizons documentation](https://ssd.jpl.nasa.gov/horizons/manual.html) |
| LOLA elevation products | Terrain data distributed by NASA Goddard PGDA; acknowledge the LOLA team and product provenance | [PGDA terrain products](https://pgda.gsfc.nasa.gov/products/78), [polar visibility products and references](https://pgda.gsfc.nasa.gov/products/69) |
| NASA Moon Trek | Remote LROC imagery and LOLA shaded-relief/elevation tiles; NASA/JPL-Caltech and each layer's source team | [Moon Trek](https://trek.nasa.gov/moon/), [JPL image-use policy](https://www.jpl.nasa.gov/jpl-image-use-policy/) |
| LROC products | Credit NASA/GSFC/Arizona State University as specified by the product | [LROC terms and citation policy](https://lroc.im-ldi.com/about/terms) |
| NASA Image and Video Library | Overview imagery; source identifiers and credits listed below | [NASA media guidelines](https://www.nasa.gov/nasa-brand-center/images-and-media/) |

NASA media guidance generally permits educational and informational use while
requiring proper treatment of third-party rights, trademarks and identifiable
people. NASA/JPL/ASU attribution does not by itself establish that every asset is
public domain. LROC distinguishes public-domain PDS products from copyrighted
website/featured imagery, for which educational reuse with credit is permitted.
Check the particular product's conditions before reuse, especially outside the
educational context. Neither the project license nor a source credit implies
NASA or partner endorsement.

### Current Site Card imagery

The image URLs are remote references in `src/panels/places.py`; image files are
not copied into this source repository. Several Site Cards share regional mosaics,
explicitly identified as geographic context rather than exact-coordinate images.

| Library identifier | Subject | Credit retained in the application |
|---|---|---|
| [PIA13523](https://images.nasa.gov/details/PIA13523) | LROC Wide Angle Camera south polar mosaic | NASA/GSFC/Arizona State University |
| [PIA00001](https://images.nasa.gov/details/PIA00001) | Clementine south polar mosaic | NASA/JPL/USGS |
| [PIA12953](https://images.nasa.gov/details/PIA12953) | LROC view near Malapert's summit, not the catalog center | NASA/GSFC/Arizona State University |
| [as11-40-5927](https://images.nasa.gov/details/as11-40-5927) | Aldrin beside Eagle, photographed by Armstrong | NASA |
| [PIA12909](https://images.nasa.gov/details/PIA12909) | LROC image of Apollo 11 surface hardware and tracks | NASA/GSFC/Arizona State University |

The [catalog review](docs/pitch/catalog_expansion_review.md) records image identity
and geographic-context checks. The older [science review](docs/pitch/final_science_review.md)
is historical and includes images subsequently removed from the application.

### Scientific references and generated catalog files

Regional coordinates are attributed to the [NASA Lunar Surface Data Book](https://ntrs.nasa.gov/api/citations/20230007818/downloads/ACD-50044%20Lunar%20Surface%20Data%20Book%20Rev%20A.pdf).
Study points and published solar values are attributed to
[Gläser et al. (2017)](https://ntrs.nasa.gov/citations/20170007365).
Citing a publication does not relicense the publication, its figures or its data.

`data/catalog/` contains project-generated ephemerides files and Terrain Horizon
products derived from Horizons and LOLA inputs, with provenance in `manifest.json`.
Those outputs do not give the team ownership of the underlying source datasets.
Retain the source acknowledgments when sharing them. Source papers, imagery and
maps remain governed by their own terms even when used alongside original project
calculations. The [consistency comparison](docs/pitch/illumination_comparison.md)
records method and source distinctions.

## External software

Python dependencies are installed separately, and browser libraries are loaded
from jsDelivr. They retain their original licenses. The following inventory covers
the directly used software and the globe's rendering library; installed wheels
and CDN bundles can include additional dependencies and their own notices.
The license file shipped with the actual version takes precedence over this
summary and links to upstream development branches.

| Component | Upstream license | Authoritative license reference |
|---|---|---|
| Streamlit | Apache-2.0 | [LICENSE](https://raw.githubusercontent.com/streamlit/streamlit/develop/LICENSE) |
| Plotly.py / embedded Plotly.js | MIT | [Plotly.py license](https://raw.githubusercontent.com/plotly/plotly.py/master/LICENSE.txt), [Plotly.js license](https://raw.githubusercontent.com/plotly/plotly.js/master/LICENSE) |
| Pandas | BSD-3-Clause | [LICENSE](https://raw.githubusercontent.com/pandas-dev/pandas/main/LICENSE) |
| NumPy | BSD-3-Clause | [LICENSE](https://raw.githubusercontent.com/numpy/numpy/main/LICENSE.txt) |
| Requests | Apache-2.0 | [LICENSE](https://raw.githubusercontent.com/psf/requests/main/LICENSE) |
| Rasterio | BSD-3-Clause | [LICENSE](https://raw.githubusercontent.com/rasterio/rasterio/main/LICENSE.txt) |
| globe.gl | MIT | [LICENSE](https://raw.githubusercontent.com/vasturiano/globe.gl/master/LICENSE) |
| Three.js | MIT | [LICENSE](https://raw.githubusercontent.com/mrdoob/three.js/dev/LICENSE) |
| Leaflet | BSD-2-Clause | [LICENSE](https://raw.githubusercontent.com/Leaflet/Leaflet/main/LICENSE) |
| Proj4js | MIT | [LICENSE](https://raw.githubusercontent.com/proj4js/proj4js/master/LICENSE.md) |
| Proj4Leaflet | BSD-2-Clause | [LICENSE](https://raw.githubusercontent.com/kartena/Proj4Leaflet/master/LICENSE) |
| Pytest (tests only) | MIT | [LICENSE](https://raw.githubusercontent.com/pytest-dev/pytest/main/LICENSE) |

This repository does not vendor those libraries' implementation sources. If
redistributing installed environments, bundled assets or the generated offline
HTML, retain the relevant upstream license/copyright notices and any bundled
NOTICE files. In particular, preserve the Plotly.js notices included by its
HTML exporter and the licenses of Rasterio's native dependencies. No blanket
Apache-2.0 grant is made for third-party libraries or their transitive components.
