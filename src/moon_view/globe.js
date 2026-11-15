// 3D Moon: globe.gl (Three.js / WebGL). The browser builds the textures itself from NASA Moon Trek WMTS tiles
// (served with CORS *), so nothing heavy goes through Python and the tiles stay in the browser cache across reruns.
const globeView = (() => {
  const GLOBE_GL_URL = "https://cdn.jsdelivr.net/npm/globe.gl@2.46.2/dist/globe.gl.min.js";
  const TILE_URL = "https://trek.nasa.gov/tiles/Moon/EQ/{layer}/1.0.0/default/default028mm/{level}/{row}/{col}.{ext}";
  // Equirectangular Moon Trek layers: [layer, tile extension, highest level to load]; level n = 2^(n+1) x 2^n tiles.
  const LAYERS = {
    Photos: ["LRO_WAC_Mosaic_Global_303ppd_v02", "jpg", 3],  // LROC WAC global mosaic, 4096 x 2048 px
    Relief: ["LRO_LOLA_ClrShade_Global_128ppd_v04", "png", 3],  // LOLA color shaded relief, as on the polar map
  };
  const BUMP = ["LRO_LOLA_DEM_Global_128ppd_v04", "png", 2];  // LOLA elevation (grayscale) for bump shading
  const REDUCED_MOTION = window.matchMedia("(prefers-reduced-motion: reduce)");
  const MOON_RADIUS_M = 1737400, SCALE_MAX_PX = 160;  // the scale bar's widest, as on the polar map
  // Past this, near the south pole, the globe's texture (about 2.7 km per pixel) is coarser than the screen: the
  // polar map shows it far better.
  const POLE_LAT = -70, POLE_ALTITUDE = 0.5;

  const load = () => (window.Globe ? Promise.resolve() : loadScript(GLOBE_GL_URL));

  // One equirectangular texture per (layer, level), assembled from Moon Trek tiles on a canvas and kept for the
  // lifetime of the page. Tiles that fail stay black; the promise rejects only if every tile failed.
  const mosaics = window.__lunavMosaics || (window.__lunavMosaics = {});
  function mosaic(layer, ext, level) {
    const id = `${layer}/${level}`;
    if (!mosaics[id]) {
      mosaics[id] = new Promise((resolve, reject) => {
        const cols = 2 ** (level + 1), rows = 2 ** level, px = 256;
        const canvas = document.createElement("canvas");
        canvas.width = cols * px; canvas.height = rows * px;
        const ctx = canvas.getContext("2d");
        let pending = cols * rows, failed = 0;
        const done = () => {
          if (--pending > 0) return;
          if (failed === cols * rows) { delete mosaics[id]; reject(new Error("tiles")); }
          else resolve(canvas.toDataURL("image/jpeg", 0.92));
        };
        for (let row = 0; row < rows; row++) for (let col = 0; col < cols; col++) {
          const img = new Image();
          img.crossOrigin = "anonymous";
          img.onload = () => { ctx.drawImage(img, col * px, row * px); done(); };
          img.onerror = () => { failed++; done(); };
          img.src = TILE_URL.replace("{layer}", layer).replace("{level}", level)
            .replace("{row}", row).replace("{col}", col).replace("{ext}", ext);
        }
      });
    }
    return mosaics[id];
  }

  function setLayer(state, name) {
    state.layer = name;
    state.root.querySelectorAll('.choices[data-for="globe"] button')
      .forEach(b => b.classList.toggle("active", b.dataset.layer === name));
    const [layer, ext, maxLevel] = LAYERS[name];
    setStatus(state, "globe", "Loading NASA Moon Trek imagery…");
    // Show a quick low-resolution texture first, then the full one.
    const levels = [...new Set([Math.min(2, maxLevel), maxLevel])];
    let shown = -1;
    levels.forEach(level => mosaic(layer, ext, level).then(url => {
      if (state.layer !== name || level < shown) return;
      shown = level;
      state.globe.globeImageUrl(url);
      if (level === maxLevel) setStatus(state, "globe", "");
    }).catch(() => {
      if (state.layer === name) setStatus(state, "globe", "Could not load NASA Moon Trek imagery.");
    }));
  }

  // Fit the globe to the view and shift the projection center to the middle of the area the panel leaves uncovered.
  function layout(state) {
    const el = state.root.querySelector(".globe"), w = el.clientWidth, h = el.clientHeight;
    if (!w || !h) return;
    state.globe.width(w).height(h);
    const right = panelRight(state.root), camera = state.globe.camera();
    if (right) camera.setViewOffset(w, h, -right / 2, 0, w, h);
    else camera.clearViewOffset();
    camera.updateProjectionMatrix();
    drawScale(state);
  }

  // The globe turns slowly when the app opens and stops for good at the first interaction: dragging or zooming
  // it, or any click or key press on the page (the panels too). It never turns when the system asks for reduced
  // motion. Clicks inside the view reach `document` too: pointer and key events cross the shadow root.
  function spinUntilFirstInteraction(state) {
    state.spinning = !REDUCED_MOTION.matches;
    if (!state.spinning) return;
    const controls = state.globe.controls(), events = ["pointerdown", "keydown"];
    const stop = () => {
      state.spinning = controls.autoRotate = false;
      state.stopWatching();
    };
    state.stopWatching = () => {
      events.forEach(type => document.removeEventListener(type, stop, true));
      controls.removeEventListener("start", stop);  // OrbitControls: a drag or wheel zoom begins
      REDUCED_MOTION.removeEventListener("change", stop);
    };
    events.forEach(type => document.addEventListener(type, stop, true));
    controls.addEventListener("start", stop);
    REDUCED_MOTION.addEventListener("change", stop);
  }

  // Scale bar for the surface at the middle of the view, rounded like Leaflet's (1, 2, 3 or 5 times a power of 10).
  function drawScale(state) {
    const globe = state.globe, camera = globe.camera(), h = state.root.querySelector(".globe").clientHeight;
    if (!h) return;
    const r = globe.getGlobeRadius();
    const metersPerPx = (camera.position.length() - r) * 2 * Math.tan(camera.fov * Math.PI / 360) / h
      * MOON_RADIUS_M / r;
    const max = SCALE_MAX_PX * metersPerPx, p = 10 ** Math.floor(Math.log10(max)), d = max / p;
    const meters = p * (d >= 5 ? 5 : d >= 3 ? 3 : d >= 2 ? 2 : 1);
    const el = state.root.querySelector(".globe-scale");
    el.style.width = `${Math.round(meters / metersPerPx)}px`;
    el.textContent = meters >= 1000 ? `${meters / 1000} km` : `${meters} m`;
  }

  // The + and − buttons step the camera's distance like the mouse wheel, within OrbitControls' limits, keeping the
  // point the camera looks at.
  const ZOOM_STEP = 1.6;
  function altitudeLimits(state) {
    const r = state.globe.getGlobeRadius(), c = state.globe.controls();
    return [c.minDistance / r - 1, Math.min(c.maxDistance, 1e6 * r) / r - 1];
  }
  function zoom(state, factor) {
    const [min, max] = altitudeLimits(state), { altitude } = state.globe.pointOfView();
    state.closeBalloon?.();
    state.globe.pointOfView({ altitude: Math.min(max, Math.max(min, altitude * factor)) }, 300);
  }
  function markZoomLimits(state) {
    const [min, max] = altitudeLimits(state), { altitude } = state.globe.pointOfView();
    state.root.querySelector('[data-zoom="in"]').disabled = altitude <= min * 1.01;
    state.root.querySelector('[data-zoom="out"]').disabled = altitude >= max * 0.99;
  }

  // Zooming in close to the south pole points at the polar map, once each time the camera comes that close.
  function watchPole(state) {
    const { lat, altitude } = state.globe.pointOfView(), near = lat < POLE_LAT && altitude < POLE_ALTITUDE;
    if (near && !state.nearPole && state.view === "globe") {
      nudgeView(state, "map", "Close to the south pole: switch to the South pole map for sharper terrain");
    }
    state.nearPole = near;
  }

  // Camera for a site; polar sites are seen from just off the pole (OrbitControls misbehaves exactly at it).
  function cameraFor(site) {
    if (!site) return { lat: -55, lng: 0, altitude: 1.8 };  // whole Moon, tilted toward the south pole
    return { lat: Math.max(site.lat, -85), lng: site.lon, altitude: site.lat < -75 ? 0.9 : 1.6 };
  }

  // A click on the Moon (not on a site) offers to analyze that point, with a pulsing ring as provisional marker. The
  // balloon floats at the click, so it closes when the globe is turned.
  function askToAnalyze(state, lat, lng, event) {
    state.closeBalloon?.();
    const globe = state.globe, box = state.root.getBoundingClientRect();
    globe.controls().autoRotate = false;
    globe.ringsData([{ lat, lng }]);
    const el = analyzeBalloon(state, lat, lng, () => {
      globe.ringsData([]); el.remove(); state.closeBalloon = null;
    });
    el.classList.add("floating");
    el.style.left = `${event.clientX - box.left}px`;
    el.style.top = `${event.clientY - box.top}px`;
    state.root.appendChild(el);
    state.closeBalloon = () => el.querySelector("button:last-child").click();
  }

  // The markers are HTML elements (markerHtml in view.js) that globe.gl places over the canvas and hides behind the
  // Moon: the Catalog Sites, the Custom Site and, in the Site Planner, the Surface Asset. globe.gl builds one element
  // per data object, so the objects are kept across reruns and only updated.
  function markerItems(state, data) {
    const kept = state.globeMarkers || {}, next = {}, custom = data.custom;
    const items = data.sites.map(s => ({ key: s.key, name: s.name, kind: s.kind, lat: s.lat, lon: s.lon }));
    data.saved.forEach(s => items.push({ key: s.key, name: s.name, kind: "saved", lat: s.lat, lon: s.lon }));
    if (custom) items.push({ key: "custom", name: "Custom Site", kind: "custom", lat: custom.lat, lon: custom.lon });
    if (data.mode === "planner" && data.asset) {
      items.push({ key: "asset", name: "Surface Asset", kind: "asset", lat: data.asset.lat, lon: data.asset.lon });
    }
    state.globeMarkers = next;  // an item that leaves (Custom Site, Surface Asset) comes back as a new object
    return items.map(item => (next[item.key] = Object.assign(kept[item.key] || {}, item)));
  }

  // The selected site or the Custom Site is highlighted; in the Site Planner only the Surface Asset, which starts on
  // the site.
  const highlighted = (state, item) => (state.data.mode === "planner" ? item.key === "asset"
    : item.key === "custom" || item.key === state.data.selected);
  const clickable = item => !isPicked(item);

  function markerElement(state, item) {
    const el = document.createElement("div");
    el.className = `site-marker globe-marker${item.kind === "saved" ? " saved" : ""}`;
    el.innerHTML = `${markerHtml(item.kind)}<span class="marker-name">${escapeHtml(item.name)}</span>`;
    // Keep marker clicks away from the globe, which would offer to analyze the point under them.
    ["pointerdown", "pointerup", "click"].forEach(type => el.addEventListener(type, e => e.stopPropagation()));
    if (clickable(item)) {  // a focusable button: click, Enter or Space chooses the site
      const choose = () => state.setTriggerValue("site", item.key);
      el.tabIndex = 0;
      el.setAttribute("role", "button");
      el.addEventListener("click", choose);
      el.addEventListener("keydown", e => {
        if (e.key === "Enter" || e.key === " ") { e.preventDefault(); choose(); }
      });
    }
    item.el = el;
    mark(state, item);
    return el;
  }

  // Selection and the time bar's state, on one marker; elements appear a moment after htmlElementsData().
  function mark(state, item) {
    if (!item.el) return;
    const on = highlighted(state, item);
    item.el.classList.toggle("selected", on);
    if (clickable(item)) {
      item.el.setAttribute("aria-label", `${item.name}, ${KINDS[item.kind] || "site"}${on ? ", selected" : ""}`);
    }
    paintMarker(item.el, timeBar.stateOf(state, item.key));
  }

  function paint(state) {
    (state.globeItems || []).forEach(item => mark(state, item));
  }

  function update(state, data, active) {
    const globe = state.globe, focus = focusSite(data);
    state.globeItems = markerItems(state, data);
    globe.htmlElementsData(state.globeItems);
    paint(state);
    if (!active) {  // hidden behind the polar map: stop drawing until shown again
      state.closeBalloon?.();
      if (!state.globePaused) { state.globePaused = true; globe.pauseAnimation(); }
      return;
    }
    if (state.globePaused) { state.globePaused = false; globe.resumeAnimation(); }
    globe.controls().autoRotate = state.spinning && !focus && !state.closeBalloon;
    const key = focus ? `${focus.key}:${focus.lat},${focus.lon}` : "";
    if (state.cameraKey !== key) {
      // A site to show moves the camera, and so does the first view; deselecting keeps it where it is.
      if (focus || state.cameraKey === undefined) globe.pointOfView(cameraFor(focus), state.globeShown ? 1500 : 0);
      state.cameraKey = key;
    }
    state.globeShown = true;
  }

  function create(state) {
    const root = state.root, el = root.querySelector(".globe");
    const globe = new Globe(el, { rendererConfig: { antialias: true, alpha: false } })
      .backgroundColor("#000005")
      .showAtmosphere(false)
      .htmlLat("lat").htmlLng("lon").htmlAltitude(0.005).htmlTransitionDuration(0)
      .htmlElement(item => markerElement(state, item))
      .htmlElementVisibilityModifier((marker, visible) => marker.classList.toggle("behind", !visible))
      .ringLat("lat").ringLng("lng").ringColor(() => t => `rgba(230, 107, 39, ${1 - t})`)
      .ringMaxRadius(2.5).ringPropagationSpeed(2).ringRepeatPeriod(900)
      .onGlobeClick(({ lat, lng }, event) => deselect(state) || askToAnalyze(state, lat, lng, event));
    globe.controls().autoRotateSpeed = 0.35;
    globe.controls().addEventListener("start", () => state.closeBalloon?.());
    // OrbitControls' "change" fires whenever the camera moves: user, damping and pointOfView flights alike.
    globe.controls().addEventListener("change", () => {
      drawScale(state); watchPole(state); markZoomLimits(state);
    });
    root.querySelector('[data-zoom="in"]').onclick = () => zoom(state, 1 / ZOOM_STEP);
    root.querySelector('[data-zoom="out"]').onclick = () => zoom(state, ZOOM_STEP);
    state.globe = globe;
    spinUntilFirstInteraction(state);

    const [bumpLayer, bumpExt, bumpLevel] = BUMP;
    mosaic(bumpLayer, bumpExt, bumpLevel).then(url => {
      globe.bumpImageUrl(url);
      globe.globeMaterial().bumpScale = 6;
    }).catch(() => {});

    const buttons = root.querySelector('.choices[data-for="globe"]');
    Object.keys(LAYERS).forEach(name => {
      const b = document.createElement("button");
      b.textContent = name; b.dataset.layer = name;
      b.onclick = () => setLayer(state, name);
      buttons.appendChild(b);
    });
    setLayer(state, Object.keys(LAYERS)[0]);
  }

  function destroy(state) {
    state.stopWatching?.();
    state.globe._destructor?.();
  }

  return { load, loadError: "Could not load globe.gl from the CDN.", exists: state => !!state.globe, create, update,
           paint, layout, destroy };
})();
