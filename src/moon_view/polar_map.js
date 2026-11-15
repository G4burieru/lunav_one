// South polar map: Leaflet with Proj4Leaflet on NASA Moon Trek south polar stereographic tiles (served with CORS *).
// The globe's tiles are too coarse near the pole (docs/adr/0003-one-screen-moon-view.md). All Moon Trek south polar
// layers share one tile grid. Each base layer stacks finer data over coarser data, and Moon Trek tiles are
// transparent where a layer has no data, so the coarser layer shows through there.
const polarMap = (() => {
  const LEAFLET_URL = "https://cdn.jsdelivr.net/npm/leaflet@1.9.4/dist/leaflet.js";  // CSS: _HTML in __init__.py
  const PROJ4_URL = "https://cdn.jsdelivr.net/npm/proj4@2.20.8/dist/proj4.js";
  const PROJ4LEAFLET_URL = "https://cdn.jsdelivr.net/npm/proj4leaflet@1.0.2/src/proj4leaflet.js";
  const TILE_URL = "https://trek.nasa.gov/tiles/Moon/SP/{layer}/1.0.0/default/default028mm/{z}/{y}/{x}.png";
  const MOON_RADIUS_M = 1737400;
  // The tile grid is a square reaching GRID_M meters from the pole on each side (about 55°S). Level 0 is one 256 px
  // tile across it, and each level halves the pixel size: about 4 m at level 11.
  const GRID_M = 1095930, RES0 = 2 * GRID_M / 256, MAX_ZOOM = 13;
  const MAP_M = 931100;  // the map stops where the Photos layer does: 60°S
  // Base layers, coarse to fine: [Moon Trek layer, highest tile level, meters from the pole to the edge of its data].
  const BASES = {
    Photos: [
      ["LRO_WAC_Mosaic_SPole60_100mp", 4, MAP_M],  // LROC WAC mosaic, to 60°S; Moon Trek serves it to level 4 only
      ["LRO_NAC_AvgMosaic_SPole855_1mp", 11, 136526],  // LROC NAC average mosaic, about 4 m per pixel to 85.5°S
    ],
    Relief: [
      ["LRO_LOLA_ClrShade_SPole45_100mp_v04", 4, GRID_M],  // LOLA color shaded relief, about 500 m per pixel
      ["LRO_LOLA_ClrShade_SPole75_30mp_v04", 6, 457440],  // about 130 m per pixel to 75°S
      ["LRO_LOLA_ClrShade_SPole875_5mp_v04", 9, 75840],  // about 17 m per pixel to 87.5°S
    ],
  };
  const MAP_LAT = -60;  // sites farther north are off the map
  const SITE_ZOOM = 8.5;  // about 25 m per pixel: a selected site with the terrain around it
  const OVERVIEW_M = 135000;  // the overview shows this far from the pole: every polar Catalog Site

  function load() {
    if (window.L?.Proj) return Promise.resolve();
    return Promise.all([loadScript(LEAFLET_URL), loadScript(PROJ4_URL)]).then(() => loadScript(PROJ4LEAFLET_URL));
  }

  // Leaflet bounds for the square reaching `reach` meters from the pole. Leaflet projects a bounds' west corners to
  // the top left and its east corners to the bottom right here, so all four corners share one latitude.
  function squareBounds(crs, reach) {
    const corner = crs.unproject(L.point(-reach, reach));
    return L.latLngBounds([corner.lat, corner.lng], [corner.lat, corner.lng + 180]);
  }

  // Center `site`, or the pole for the overview, in the part of the map that the panel leaves uncovered.
  // A site with `reach` (meters) is framed so that far around it fits; other sites use SITE_ZOOM.
  function centerOn(state, site, animate) {
    const m = state.map, map = m.leaflet, size = map.getSize(), right = panelRight(state.root);
    const fit = reach => Math.floor(4 * Math.log2(RES0 * Math.min(size.x - right, size.y) / (2 * reach))) / 4;
    const zoom = !site ? Math.max(map.getMinZoom(), fit(OVERVIEW_M))
      : site.reach ? Math.min(MAX_ZOOM, fit(site.reach)) : SITE_ZOOM;
    const point = map.project(site ? [site.lat, site.lon] : [-90, 0], zoom).subtract([right / 2, 0]);
    const center = map.unproject(point, zoom);
    m.userMoved = false;
    if (animate) map.flyTo(center, zoom, { duration: 1.2 });
    else map.setView(center, zoom, { animate: false });
  }

  function setBase(state, name) {
    const m = state.map;
    Object.entries(m.bases).forEach(([n, group]) => (n === name ? group.addTo(m.leaflet) : group.remove()));
    state.root.querySelectorAll('.choices[data-for="map"] button')
      .forEach(b => b.classList.toggle("active", b.dataset.layer === name));
  }

  // The markers on the map: the Catalog Sites, the Custom Site and, in the Site Planner, the Surface Asset. The
  // selected site or the Custom Site is highlighted; in the Site Planner only the Surface Asset, which starts on the
  // site (two labels would overlap). Only Catalog Sites can be chosen.
  function markerItems(data) {
    const planner = data.mode === "planner", custom = data.custom;
    const picked = custom ? [{ key: "custom", name: "Custom Site", kind: "custom", lat: custom.lat,
                               lon: custom.lon }] : [];
    const items = [...data.sites, ...picked].filter(s => s.lat <= MAP_LAT)
      .map(s => ({ key: s.key, name: s.name, kind: s.kind, lat: s.lat, lon: s.lon,
                   selected: !planner && (s.key === "custom" || s.key === data.selected) }));
    if (planner && data.asset && data.asset.lat <= MAP_LAT) {
      items.push({ key: "asset", name: "Surface Asset", kind: "asset", lat: data.asset.lat, lon: data.asset.lon,
                   selected: true });
    }
    return items;
  }

  // What the map centers on: in the Site Planner its whole Site Neighborhood, which stays put while the Surface Asset
  // moves inside it; otherwise focusSite() in view.js (the Surface Asset, the Custom Site or the selected site).
  // null for the overview.
  function focusOf(data) {
    const hood = data.mode === "planner" ? data.neighborhood : null;
    if (hood) return { key: `hood:${hood.site}`, lat: hood.center.lat, lon: hood.center.lon, reach: hood.reach_m };
    const focus = focusSite(data);
    return focus && focus.lat <= MAP_LAT ? focus : null;
  }

  // Redraw the markers when the sites, the selection, the Custom Site or the Surface Asset change; paint() shows the
  // hour's state.
  function drawSites(state, data) {
    const m = state.map, items = markerItems(data), signature = JSON.stringify(items);
    if (signature === m.signature) return;
    m.signature = signature;
    m.sites.clearLayers();
    m.markers = items.map(item => {
      const size = item.selected ? 30 : 22, choosable = !isPicked(item);
      const marker = L.marker([item.lat, item.lon], {  // interactive, so that a click never reaches the map below
        icon: L.divIcon({ className: `site-marker${item.selected ? " selected" : ""}${choosable ? "" : " static"}`,
                          iconSize: [size, size], html: markerHtml(item.kind) }),
        zIndexOffset: item.selected ? 1000 : 0, riseOnHover: true, keyboard: choosable,
      });
      marker.bindTooltip(escapeHtml(item.name), { direction: "top", offset: [0, -size / 2 - 6],
                                                  permanent: item.selected, className: "site-label" });
      if (choosable) {
        const choose = () => state.setTriggerValue("site", item.key);
        marker.on("click", choose);
        marker.on("add", () => {  // Leaflet makes markers focusable buttons; give them a name and Enter or Space
          const el = marker.getElement();
          el.setAttribute("aria-label", `${item.name}, ${KINDS[item.kind] || "site"}${item.selected ? ", selected" : ""}`);
          el.addEventListener("keydown", e => {
            if (e.key === "Enter" || e.key === " ") { e.preventDefault(); choose(); }
          });
        });
      }
      m.sites.addLayer(marker);
      return { marker, key: item.key };
    });
  }

  // The limits of analysisSource (view.js), dashed: the south pole terrain data's edge, and the pre-computed Site
  // Neighborhood around each Catalog Site. Drawn once, as rings in map meters: Proj4Leaflet measures an L.circle
  // with the Earth's radius.
  function drawZones(state, data) {
    const m = state.map, z = data.zones;
    if (m.zones || !z) return;
    const crs = m.leaflet.options.crs;
    const ring = (lat, lon, radius, color) => {  // dashed, over a dark halo that keeps it visible on bright terrain
      const center = crs.project(L.latLng(lat, lon));
      const points = Array.from({ length: 180 }, (_, i) => crs.unproject(
        center.add([radius * Math.cos(i * Math.PI / 90), radius * Math.sin(i * Math.PI / 90)])));
      const line = { fill: false, interactive: false };
      return L.layerGroup([L.polygon(points, { ...line, color: "#000", weight: 4, opacity: 0.45 }),
                           L.polygon(points, { ...line, color, weight: 2, dashArray: "7 6" })]);
    };
    const edge = crs.project(L.latLng(z.terrain_lat, 0));  // a parallel is a circle around the pole here
    m.zones = L.layerGroup([
      ring(-90, 0, Math.hypot(edge.x, edge.y), "#4fd1e8"),
      ...data.sites.filter(s => z.precomputed.includes(s.key) && s.lat <= MAP_LAT)
        .map(s => ring(s.lat, s.lon, z.precomputed_m, "#7fd18b")),
    ]).addTo(m.leaflet);
  }

  function paint(state) {
    (state.map.markers || []).forEach(({ marker, key }) => paintMarker(marker.getElement(), timeBar.stateOf(state, key)));
  }

  function create(state) {
    const el = state.root.querySelector(".polar-map");
    const crs = new L.Proj.CRS("Moon:SouthPolarStereographic",
      `+proj=stere +lat_0=-90 +lon_0=0 +k=1 +x_0=0 +y_0=0 +R=${MOON_RADIUS_M} +units=m +no_defs`, {
        origin: [-GRID_M, GRID_M],
        resolutions: Array.from({ length: MAX_ZOOM + 1 }, (_, z) => RES0 / 2 ** z),
        bounds: L.bounds([-GRID_M, -GRID_M], [GRID_M, GRID_M]),
      });
    crs.R = MOON_RADIUS_M;  // Proj4Leaflet has no distance(); the scale bar needs one, on the Moon
    crs.distance = L.CRS.Earth.distance;
    const map = L.map(el, {
      crs, center: [-90, 0], zoom: 4, minZoom: 2, maxZoom: MAX_ZOOM, zoomSnap: 0.25, wheelPxPerZoomLevel: 100,
      maxBounds: squareBounds(crs, MAP_M), maxBoundsViscosity: 1, inertiaMaxSpeed: 1500,  // no flinging into space
      zoomControl: false, attributionControl: false,  // credits are in the view's own overlay
    });
    L.control.zoom({ position: "bottomright" }).addTo(map);
    // A flight (centerOn's flyTo) cut short by a drag never fires zoomend, so the vector layers (the dashed rings,
    // the Site Neighborhood) keep the scale of the zoom where it stopped until the next zoom. Redraw them when a move
    // ends at a zoom they were not drawn for.
    let drawnZoom = map.getZoom();
    map.on("zoomend viewreset", () => { drawnZoom = map.getZoom(); });
    map.on("moveend", () => { if (map.getZoom() !== drawnZoom) map.fire("viewreset"); });
    L.control.scale({ position: "bottomright", imperial: false, maxWidth: 160 }).addTo(map);

    // Skip tiles outside a layer's data square, where Moon Trek answers 404.
    const Tiles = L.TileLayer.extend({
      _isValidTile(coords) {
        const size = 256 * RES0 / 2 ** coords.z, reach = this.options.reach;
        const left = -GRID_M + coords.x * size, top = GRID_M - coords.y * size;
        return left < reach && left + size > -reach && top > -reach && top - size < reach
          && L.TileLayer.prototype._isValidTile.call(this, coords);
      },
    });
    const tiles = ([layer, maxNativeZoom, reach]) => new Tiles(TILE_URL.replace("{layer}", layer),
      { maxNativeZoom, maxZoom: MAX_ZOOM, reach })
      .on("loading", () => setStatus(state, "map", ""))
      .on("tileerror", () => setStatus(state, "map", "Some NASA Moon Trek tiles could not be loaded."));
    state.map = {
      leaflet: map, sites: L.layerGroup().addTo(map), hood: L.layerGroup().addTo(map), canvas: L.canvas(),
      bases: Object.fromEntries(Object.entries(BASES).map(([name, layers]) => [name, L.layerGroup(layers.map(tiles))])),
    };

    // Marker clicks do not reach the map. Beyond MAP_LAT is off the map's imagery, so nothing to analyze there.
    map.on("click", e => deselect(state) || e.latlng.lat > MAP_LAT || askToAnalyze(state, e.latlng));
    const buttons = state.root.querySelector('.choices[data-for="map"]');
    Object.keys(BASES).forEach(name => {
      const b = document.createElement("button");
      b.textContent = name; b.dataset.layer = name;
      b.onclick = () => setBase(state, name);
      buttons.appendChild(b);
    });
    setBase(state, Object.keys(BASES)[0]);
    // Once the user moves the map, a change in the panel's width no longer re-centers it.
    el.addEventListener("pointerdown", () => { state.map.userMoved = true; });
    el.addEventListener("wheel", () => { state.map.userMoved = true; }, { passive: true });
  }

  // A click on the map (not on a site) offers to analyze that point, with a dashed ring as provisional marker.
  function askToAnalyze(state, latlng) {
    const map = state.map.leaflet;
    const ring = L.circleMarker(latlng, { radius: 9, color: "#e66b27", weight: 2, dashArray: "4 3", fill: false,
                                          interactive: false }).addTo(map);
    const popup = L.popup({ className: "analyze-popup", closeButton: false, offset: [0, -8] }).setLatLng(latlng);
    popup.setContent(analyzeBalloon(state, latlng.lat, latlng.lng, () => map.closePopup(popup)));
    popup.on("remove", () => ring.remove());
    popup.openOn(map);
  }

  // The Site Planner's Site Neighborhood (task A6): one 100 m square per point, colored by the panel's choice, on a
  // canvas, which keeps some 1,300 cells fast. A click on a cell sends "cell" with its index. The best cell has a
  // dashed outline and the Surface Asset's cell a solid one.
  function drawNeighborhood(state, data) {
    const m = state.map, hood = data.mode === "planner" ? data.neighborhood : null;
    const signature = JSON.stringify(hood);
    if (signature === m.hoodSignature) return;
    m.hoodSignature = signature;
    m.hood.clearLayers();
    if (!hood) return;
    const unit = `% ${hood.label}`;
    hood.cells.forEach((cell, i) => {
      L.polygon(cell.corners, { renderer: m.canvas, stroke: false, fillColor: cell.color, fillOpacity: 0.8,
                                bubblingMouseEvents: false })
        .bindTooltip(`${cell.value.toFixed(0)}${unit}`, { sticky: true, className: "site-label" })
        .on("click", () => state.setTriggerValue("cell", i))
        .addTo(m.hood);
    });
    const outline = (i, dashArray) => L.polygon(hood.cells[i].corners, { renderer: m.canvas, color: "#fff",
      weight: 2, dashArray, fill: false, interactive: false }).addTo(m.hood);
    if (hood.best != null) outline(hood.best, "4 3");
    if (hood.selected != null) outline(hood.selected, null);
  }

  function update(state, data, active) {
    const m = state.map;
    drawSites(state, data);
    drawNeighborhood(state, data);
    drawZones(state, data);
    paint(state);
    if (!active) { m.shown = false; m.leaflet.closePopup(); return; }
    const focus = focusOf(data), key = focus ? `${focus.key}:${focus.lat},${focus.lon}` : "";
    if (!m.shown) {  // just switched to the map: start from the overview the first time, then fly to the focus
      m.shown = true;
      m.leaflet.invalidateSize();
      const first = !m.placed;
      m.placed = true;
      if (first) centerOn(state, null, false);
      m.centeredOn = key;
      if (focus || !first) centerOn(state, focus, true);
    } else if (m.centeredOn !== key) {
      m.centeredOn = key;
      centerOn(state, focus, true);
    }
  }

  // The panel widens when a Site Card opens, so center the focus again unless the user has moved the map since.
  function layout(state) {
    const m = state.map;
    m.leaflet.invalidateSize({ pan: false });
    if (m.shown && !m.userMoved) centerOn(state, focusOf(state.data), true);
  }

  const destroy = state => state.map.leaflet.remove();

  return { load, loadError: "Could not load the map (Leaflet and proj4) from the CDN.", exists: state => !!state.map,
           create, update, paint, layout, destroy };
})();
