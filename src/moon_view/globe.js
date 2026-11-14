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

  const escapeHtml = text => text.replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;",
    "'": "&#39;" })[c]);
  const tooltip = s => `<b>${escapeHtml(s.name)}</b><br>${s.lat.toFixed(4)}°, ${s.lon.toFixed(4)}° E`;

  function load() {
    if (window.Globe) return Promise.resolve();
    if (!window.__lunavGlobeGl) {
      window.__lunavGlobeGl = new Promise((resolve, reject) => {
        const script = document.createElement("script");
        script.src = GLOBE_GL_URL;
        script.onload = resolve;
        script.onerror = () => { window.__lunavGlobeGl = null; reject(new Error("globe.gl")); };
        document.head.appendChild(script);
      });
    }
    return window.__lunavGlobeGl;
  }

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
    state.root.querySelectorAll(".layers button").forEach(b => b.classList.toggle("active", b.dataset.layer === name));
    const [layer, ext, maxLevel] = LAYERS[name];
    const status = state.root.querySelector(".status");
    status.textContent = "Loading NASA Moon Trek imagery…";
    // Show a quick low-resolution texture first, then the full one.
    const levels = [...new Set([Math.min(2, maxLevel), maxLevel])];
    let shown = -1;
    levels.forEach(level => mosaic(layer, ext, level).then(url => {
      if (state.layer !== name || level < shown) return;
      shown = level;
      state.globe.globeImageUrl(url);
      if (level === maxLevel) status.textContent = "";
    }).catch(() => {
      if (state.layer === name) status.textContent = "Could not load NASA Moon Trek imagery.";
    }));
  }

  // The app's floating panel covers the left of the globe, so shift the projection center to the middle of the
  // uncovered area. The panel is measured on the page (st.container(key="panel") in app.py); phones stack it under
  // the view instead, and then it is not fixed, so no shift.
  function applyViewOffset(state) {
    const el = state.root.querySelector(".globe"), w = el.clientWidth, h = el.clientHeight;
    const panel = document.querySelector(".st-key-panel");
    const right = panel && getComputedStyle(panel).position === "fixed" ? panel.getBoundingClientRect().right : 0;
    const camera = state.globe.camera();
    if (right && w && h) camera.setViewOffset(w, h, -right / 2, 0, w, h);
    else camera.clearViewOffset();
    camera.updateProjectionMatrix();
  }

  // Camera for a site; polar sites are seen from just off the pole (OrbitControls misbehaves exactly at it).
  function cameraFor(site) {
    if (!site) return { lat: -55, lng: 0, altitude: 1.8 };  // whole Moon, tilted toward the south pole
    return { lat: Math.max(site.lat, -85), lng: site.lon, altitude: site.lat < -75 ? 0.9 : 1.6 };
  }

  // Re-center whenever the panel changes size. Streamlit renders the panel after the view, so it may not exist yet.
  function watchPanel(state, tries = 25) {
    const panel = document.querySelector(".st-key-panel");
    if (panel && panel !== state.panel) { state.panel = panel; state.observer.observe(panel); }
    else if (!panel && tries > 0) setTimeout(() => watchPanel(state, tries - 1), 200);
  }

  function update(state, data) {
    const globe = state.globe, selected = data.sites.find(s => s.key === data.selected);
    watchPanel(state);
    applyViewOffset(state);
    globe.pointsData(data.sites).labelsData(selected ? [selected] : []);
    globe.controls().autoRotate = !selected;
    if (state.cameraKey !== (data.selected || "")) {
      state.cameraKey = data.selected || "";
      globe.pointOfView(cameraFor(selected), state.created ? 1500 : 0);
    }
    const info = state.root.querySelector(".info");
    info.classList.toggle("has-site", !!selected);
    info.querySelector(".info-name").textContent = selected ? selected.name : "";
    info.querySelector(".info-text").textContent = selected
      ? `${selected.lat.toFixed(4)}°, ${selected.lon.toFixed(4)}° E · ${selected.description}` : "";
    state.created = true;
  }

  function addFullscreenButton(state) {
    // The component lives in a shadow root, so ask the root node (not document) which element is full screen.
    const root = state.root, isFullscreen = () => root.getRootNode().fullscreenElement === root;
    const button = document.createElement("button");
    button.className = "fullscreen";
    const label = () => { button.textContent = isFullscreen() ? "✕ Exit full screen" : "⛶ Full screen"; };
    button.onclick = () => (isFullscreen() ? document.exitFullscreen() : root.requestFullscreen()).catch(() => {});
    state.onFullscreenChange = label;
    document.addEventListener("fullscreenchange", label);
    label();
    root.querySelector(".layers").appendChild(button);
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

    const buttons = root.querySelector(".layers");
    Object.keys(LAYERS).forEach(name => {
      const b = document.createElement("button");
      b.textContent = name; b.dataset.layer = name;
      b.onclick = () => setLayer(state, name);
      buttons.appendChild(b);
    });
    setLayer(state, Object.keys(LAYERS)[0]);
    if (root.requestFullscreen) addFullscreenButton(state);

    const resize = () => { globe.width(el.clientWidth).height(el.clientHeight); applyViewOffset(state); };
    state.observer = new ResizeObserver(resize);
    state.observer.observe(el);
    resize();
  }

  return { load, create, update };
})();
