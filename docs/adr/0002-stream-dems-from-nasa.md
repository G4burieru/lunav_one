# Stream DEMs from NASA servers; use the global DEM only offline

Terrain is read with HTTP range requests straight from NASA and USGS servers instead of bundling or rehosting DEM
files. This avoids paying for storage and always uses the latest published data. The south pole LOLA DEMs from PGDA
(80 m and 20 m, 80°S to the pole) are cloud-optimized GeoTIFFs in 512×512 tiles, so reading a site's surroundings is
cheap. The global LOLA DEM (118 m, 8.5 GB) is stored in full-width strips, so a single 150 km horizon needs about
470 MB of reads. It is therefore used only by the pre-computation for catalog sites; custom sites outside 80°S fall
back to the ideal horizon with a visible warning.

Inside 80°S the horizon is built from distance rings: the 20 m DEM up to 10 km (and for the ground height under
the Surface Asset), the 80 m DEM from 10 to 50 km, and the 80 m DEM's built-in 320 m overview from 50 to 150 km.
Near terrain decides most shadows and needs fine resolution (80 m alone left a −12 point gap at Shackleton Rim S2
against Gläser et al. 2017), while far terrain subtends small angles: the 320 m ring changes horizons by at most
0.06° and makes live horizons 2–3× faster. The global DEM has no overviews, so it is read at full resolution.

## Consequences

- The app depends on `rasterio` and on network access to the DEM servers for anything not pre-computed.
- If a server changes its URLs or file layout, live terrain stops working until the URLs are updated.
- PGDA intermittently returns empty tiles; reads are done in small bands with retries that back off for about
  2.5 minutes before failing.
