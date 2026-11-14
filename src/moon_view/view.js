// Moon View entry point (docs/adr/0003-one-screen-moon-view.md). src/moon_view/__init__.py joins the view files
// before this one into a single module. Streamlit calls the default export again on every rerun with new data, on
// the same element, so each view is created the first time it is shown and then only updated.
//
// A view is an object with load(), exists(state), create(state), update(state, data, active), paint(state),
// layout(state) and destroy(state). The declarations below are shared by the other files (they are hoisted).
const VIEWS = { globe: globeView, map: polarMap };

// Site markers, the same in both views. The shape shows the coordinate kind, as in src/site_map.py: ◆ studied
// point, ● region center, ■ historical landing, ▲ approximate reference; a Custom Site is a ring with ticks and the
// Site Planner's Surface Asset a cross in a circle. With time data, the fill rises with the Illumination Fraction at
// the time bar's hour, and the dot at the top right is filled while Earth is visible and hollow while it is not:
// shape as well as color.
const SHAPES = {
  studied_point: '<path d="M12 1.5 22.5 12 12 22.5 1.5 12Z"/>',
  region_center: '<circle cx="12" cy="12" r="9.5"/>',
  actual_landing: '<path d="M3 3H21V21H3Z"/>',
  approximate_reference: '<path d="M12 2 22.5 21H1.5Z"/>',
  custom: '<circle cx="12" cy="12" r="6"/><path class="cross" d="M12 1v5M12 18v5M1 12h5M18 12h5"/>',
  asset: '<circle cx="12" cy="12" r="9.5"/><path class="cross" d="M12 4v16M4 12h16"/>',
};
const KINDS = { studied_point: "studied point", region_center: "region center", actual_landing: "historical landing",
                approximate_reference: "approximate reference", custom: "Custom Site", asset: "Surface Asset" };

function markerHtml(kind) {
  const shape = SHAPES[kind] || SHAPES.region_center;
  return `<svg class="shape" viewBox="0 0 24 24" aria-hidden="true">${shape}</svg>`
    + `<svg class="lit" viewBox="0 0 24 24" aria-hidden="true">${shape}</svg><span class="earth"></span>`;
}

// Show `s` ({sun, earth} from timeBar.stateOf, or null without time data) on a marker element.
function paintMarker(el, s) {
  if (!el) return;
  el.classList.toggle("timed", !!s);
  if (!s) return;
  el.querySelector(".lit").style.clipPath = `inset(${100 - s.sun}% 0 0 0)`;
  el.classList.toggle("earth-up", s.earth);
}

function paintViews(state) {
  Object.values(VIEWS).forEach(view => view.exists(state) && view.paint(state));
}

function escapeHtml(text) {
  return String(text).replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;",
    "'": "&#39;" })[c]);
}

// Loads a script once per page; the promise lives on window, so it survives the component being remounted.
function loadScript(url) {
  const scripts = window.__lunavScripts || (window.__lunavScripts = {});
  if (!scripts[url]) {
    scripts[url] = new Promise((resolve, reject) => {
      const script = document.createElement("script");
      script.src = url;
      script.onload = resolve;
      script.onerror = () => { delete scripts[url]; script.remove(); reject(new Error(url)); };
      document.head.appendChild(script);
    });
  }
  return scripts[url];
}

function setStatus(state, view, text) {
  state.root.querySelector(`.status[data-for="${view}"]`).textContent = text;
}

// The right edge of the app's floating panel (st.container(key="panel") in app.py), in px from the view's left
// edge: the views keep what they show to the right of it. 0 in full screen and on phones, where the panel stacks
// under the view instead of floating over it.
function panelRight(root) {
  const panel = document.querySelector(".st-key-panel");
  if (root.getRootNode().fullscreenElement === root || !panel || getComputedStyle(panel).position !== "fixed") return 0;
  return Math.max(0, panel.getBoundingClientRect().right - root.getBoundingClientRect().left);
}

function layoutViews(state) {
  state.root.style.setProperty("--panel-right", `${panelRight(state.root)}px`);
  Object.values(VIEWS).forEach(view => view.exists(state) && view.layout(state));
}

// Lay the views out again whenever the view or the panel changes size. Streamlit renders the panel after the view,
// so it may not exist yet on the first run.
function watchLayout(state) {
  state.observer = new ResizeObserver(() => layoutViews(state));
  state.observer.observe(state.root);
  state.findPanel = (tries = 25) => {
    const panel = document.querySelector(".st-key-panel");
    if (panel && panel !== state.panel) { state.panel = panel; state.observer.observe(panel); }
    else if (!panel && tries > 0) setTimeout(() => state.findPanel(tries - 1), 200);
  };
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

// The site the views focus on: the Custom Site (key "custom") if there is one, else the selected Catalog Site.
function focusSite(data) {
  if (data.custom) {
    return { key: "custom", name: "Custom Site", kind: "custom", lat: data.custom.lat, lon: data.custom.lon,
             description: "A location you picked." };
  }
  return data.sites.find(s => s.key === data.selected) || null;
}

// Full screen hides the app's panel, so the view shows the selected site itself.
function updateInfo(state, data) {
  const selected = focusSite(data), info = state.root.querySelector(".info");
  info.classList.toggle("has-site", !!selected);
  info.querySelector(".info-name").textContent = selected ? selected.name : "";
  info.querySelector(".info-text").textContent = selected
    ? `${selected.lat.toFixed(4)}°, ${selected.lon.toFixed(4)}° E · ${selected.description}` : "";
}

// Asks before analyzing a clicked point as a Custom Site (task A5): the live computation takes about 30 s, so a stray
// click must not start one. Analyze sends the "point" event; `close` removes the balloon and the provisional marker.
function analyzeBalloon(state, lat, lon, close) {
  lon = ((lon + 540) % 360) - 180;
  const el = document.createElement("div");
  el.className = "analyze";
  el.innerHTML = `<b>Analyze this point?</b><div>${lat.toFixed(2)}°, ${lon.toFixed(2)}° E · `
    + `${lat <= -80 ? "computed live, about 30 s" : "no terrain data here (outside 80°S), so a smooth horizon is used"}`
    + '</div><div class="analyze-buttons"><button class="primary">Analyze</button><button>Cancel</button></div>';
  const [analyze, cancel] = el.querySelectorAll("button");
  analyze.onclick = () => { close(); state.setTriggerValue("point", { lat, lon }); };
  cancel.onclick = close;
  el.addEventListener("keydown", e => { if (e.key === "Escape") close(); });
  setTimeout(() => analyze.focus({ preventScroll: true }));
  return el;
}

// Update every view that exists, creating the one shown if needed. The hidden view keeps its data current but
// stops drawing. Only a failed library load shows loadError; errors in the views' own code go to the console.
function render(state) {
  Object.entries(VIEWS).forEach(([name, view]) => {
    if (state.view !== name && !view.exists(state)) return;
    view.load().then(() => {
      if (!view.exists(state)) {
        view.create(state);
        layoutViews(state);
      }
      view.update(state, state.data, state.view === name);
    }, () => setStatus(state, name, view.loadError));
  });
}

export default function (component) {
  const { data, parentElement, setTriggerValue, setStateValue } = component;
  const root = parentElement.querySelector(".moon-view");
  root.style.setProperty("--view-height", data.height);
  const state = root.__lunav || (root.__lunav = { root });
  state.setTriggerValue = setTriggerValue;
  state.setStateValue = setStateValue;
  state.data = data;  // the views read the latest data from here, including in their event handlers
  if (!state.observer) {
    watchLayout(state);
    if (root.requestFullscreen) addFullscreenButton(state);
  }
  state.findPanel();
  // Python asks for a view ("globe" or "map"), applied only when view_id changes, so that a view the user picked
  // in the view itself survives the reruns in between.
  if (state.viewId !== data.view_id) {
    state.viewId = data.view_id;
    state.view = data.view === "map" ? "map" : "globe";
    root.dataset.view = state.view;
  }
  updateInfo(state, data);
  timeBar.update(state, data.time);
  render(state);
  return () => {
    state.observer.disconnect();
    if (state.onFullscreenChange) document.removeEventListener("fullscreenchange", state.onFullscreenChange);
    Object.values(VIEWS).forEach(view => view.exists(state) && view.destroy(state));
    delete root.__lunav;
  };
}
