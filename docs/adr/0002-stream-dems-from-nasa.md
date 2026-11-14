# Stream DEMs from NASA servers; use the global DEM only offline

Terrain is read with HTTP range requests straight from NASA and USGS servers instead of bundling or rehosting DEM
files. This avoids paying for storage and always uses the latest published data. The south pole LOLA DEMs from PGDA
(80 m and 20 m, 80°S to the pole) are cloud-optimized GeoTIFFs in 512×512 tiles, so reading a site's surroundings is
cheap. The global LOLA DEM (118 m, 8.5 GB) is stored in full-width strips, so a single 150 km horizon needs about
470 MB of reads. It is therefore used only by the pre-computation for catalog sites; custom sites outside 80°S fall
back to the ideal horizon with a visible warning.

## Consequences

- The app depends on `rasterio` and on network access to the DEM servers for anything not pre-computed.
- If a server changes its URLs or file layout, live terrain stops working until the URLs are updated.
