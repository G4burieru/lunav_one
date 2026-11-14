// 3D Moon: globe.gl (Three.js / WebGL). The browser builds the textures itself from NASA Moon Trek WMTS tiles
// (served with CORS *), so nothing heavy goes through Python and the tiles stay in the browser cache across reruns.
const globeView = (() => {
  const GLOBE_GL_URL = "https://cdn.jsdelivr.net/npm/globe.gl@2.46.2/dist/globe.gl.min.js";
  const TILE_URL = "https://trek.nasa.gov/tiles/Moon/EQ/{layer}/1.0.0/default/default028mm/{level}/{row}/{col}.{ext}";
  // Equirectangular Moon Trek layers: [layer, tile extension, highest level to load]; level n = 2^(n+1) x 2^n tiles.
  const LAYERS = {
    Imagery: ["LRO_WAC_Mosaic_Global_303ppd_v02", "jpg", 3],  // LROC WAC global mosaic, 4096 x 2048 px
    Elevation: ["LRO_LOLA_ClrShade_Global_128ppd_v04", "png", 3],  // LOLA color shaded relief
  };
  const BUMP = ["LRO_LOLA_DEM_Global_128ppd_v04", "png", 2];  // LOLA elevation (grayscale) for bump shading
  const SELECTED_COLOR = "#e66b27", SITE_COLOR = "#4ba3d3";

  const tooltip = s => `<b>${escapeHtml(s.name)}</b><br>${s.lat.toFixed(4)}°, ${s.lon.toFixed(4)}° E`;

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
  }

  // Camera for a site; polar sites are seen from just off the pole (OrbitControls misbehaves exactly at it).
  function cameraFor(site) {
    if (!site) return { lat: -55, lng: 0, altitude: 1.8 };  // whole Moon, tilted toward the south pole
    return { lat: Math.max(site.lat, -85), lng: site.lon, altitude: site.lat < -75 ? 0.9 : 1.6 };
  }

  function update(state, data, active) {
    const globe = state.globe, selected = data.sites.find(s => s.key === data.selected);
    globe.pointsData(data.sites).labelsData(selected ? [selected] : []);
    if (!active) {  // hidden behind the polar map: stop drawing until shown again
      if (!state.globePaused) { state.globePaused = true; globe.pauseAnimation(); }
      return;
    }
    if (state.globePaused) { state.globePaused = false; globe.resumeAnimation(); }
    globe.controls().autoRotate = !selected;
    if (state.cameraKey !== (data.selected || "")) {
      state.cameraKey = data.selected || "";
      globe.pointOfView(cameraFor(selected), state.globeShown ? 1500 : 0);
    }
    state.globeShown = true;
  }

  function create(state) {
    const root = state.root, el = root.querySelector(".globe");
    const isSelected = s => s.key === state.data.selected;
    const globe = new Globe(el, { rendererConfig: { antialias: true, alpha: false } })
      .backgroundColor("#000005")
      .showAtmosphere(false)
      .pointLat("lat").pointLng("lon")
      .pointColor(s => isSelected(s) ? SELECTED_COLOR : SITE_COLOR)
      .pointAltitude(s => isSelected(s) ? 0.025 : 0.01)
      .pointRadius(s => isSelected(s) ? 0.55 : 0.35)
      .pointLabel(tooltip)
      .onPointClick(s => state.setTriggerValue("site", s.key))
      .labelLat("lat").labelLng("lon").labelText("name")
      .labelSize(1.1).labelDotRadius(0.35).labelColor(() => "#ffffff").labelResolution(2)
      .labelLabel(tooltip)
      .onLabelClick(s => state.setTriggerValue("site", s.key));
    globe.controls().autoRotateSpeed = 0.35;
    state.globe = globe;

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

  const destroy = state => state.globe._destructor?.();

  return { load, loadError: "Could not load globe.gl from the CDN.", exists: state => !!state.globe, create, update,
           layout, destroy };
})();
