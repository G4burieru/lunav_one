// Moon View entry point (docs/adr/0003-one-screen-moon-view.md). src/moon_view/__init__.py joins the view files
// before this one into a single module. Streamlit calls the default export again on every rerun with new data, on
// the same element, so each view is created the first time it is shown and then only updated.
//
// A view is an object with load(), exists(state), create(state), update(state, data, active), paint(state),
// layout(state) and destroy(state). The declarations below are shared by the other files (they are hoisted).
const VIEWS = { globe: globeView, map: polarMap };

// Site markers, the same in both views. Every Catalog Site is a circle, whatever its coordinate kind (the panels name
// the kind); a Custom Site is a ring with ticks, a Custom Site named in the Site Planner (data.saved) a violet diamond,
// and the Site Planner's Surface Asset a cross in a circle. With time
// data, a badge beside the marker shows the time bar's hour: a Sun that fills from the bottom with the Illumination
// Fraction, like a sunrise, and an Earth that is blue while in view and gray, crossed out, while below the horizon:
// shape as well as color.
const SHAPES = {
  site: '<circle cx="12" cy="12" r="9.5"/>',
  custom: '<circle cx="12" cy="12" r="6"/><path class="cross" d="M12 1v5M12 18v5M1 12h5M18 12h5"/>',
  asset: '<circle cx="12" cy="12" r="9.5"/><path class="cross" d="M12 4v16M4 12h16"/>',
  saved: '<path d="M12 1.5 22.5 12 12 22.5 1.5 12Z"/>',
};
const KINDS = { studied_point: "studied point", region_center: "region center", actual_landing: "historical landing",
                approximate_reference: "approximate reference", custom: "Custom Site", asset: "Surface Asset",
                saved: "your Custom Site" };

const SUN = '<circle cx="12" cy="12" r="5"/><path d="M12 1.5v3M12 19.5v3M1.5 12h3M19.5 12h3M4.6 4.6l2.1 2.1'
  + 'M17.3 17.3l2.1 2.1M4.6 19.4l2.1-2.1M17.3 6.7l2.1-2.1"/>';
const EARTH = '<circle cx="12" cy="12" r="8.5"/><path class="grid" d="M3.5 12h17M12 3.5c-3.2 3-3.2 14 0 17'
  + 'M12 3.5c3.2 3 3.2 14 0 17"/><path class="slash" d="M4 20 20 4"/>';
const svg = (cls, body) => `<svg class="${cls}" viewBox="0 0 24 24" aria-hidden="true">${body}</svg>`;

function markerHtml(kind) {
  return svg(`shape ${kind === "saved" ? "saved" : ""}`, SHAPES[kind] || SHAPES.site)
    + `<span class="conditions"><span class="sun">${svg("sun-off", SUN)}${svg("sun-on", SUN)}</span>`
    + `${svg("earth", EARTH)}</span>`;
}

// Show `s` ({sun, earth} from timeBar.stateOf, or null without time data) on a marker element.
function paintMarker(el, s) {
  if (!el) return;
  el.classList.toggle("timed", !!s);
  if (!s) return;
  el.querySelector(".sun-on").style.clipPath = `inset(${100 - s.sun}% 0 0 0)`;
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
  liftMapControls(state);
  Object.values(VIEWS).forEach(view => view.exists(state) && view.layout(state));
}

// The polar map's zoom buttons and scale bar, and the globe's scale bar, stand in a column at the bottom right,
// CONTROLS_PX wide with a scale bar at its widest. When the bottom stack (status, hints and time bar) reaches under
// that column, as it does beside the wide panel on screens under about 1800 px, they move up above the stack
// (--controls-lift in view.css).
const CONTROLS_PX = 190;
function liftMapControls(state) {
  const root = state.root, box = root.getBoundingClientRect();
  const stack = root.querySelector(".bottom").getBoundingClientRect();
  const lift = stack.right > box.right - CONTROLS_PX ? Math.ceil(box.bottom - stack.top) + 8 : 0;
  root.style.setProperty("--controls-lift", `${lift}px`);
}

// Lay the views out again whenever the view or the panel changes size. Streamlit renders the panel after the view,
// so it may not exist yet on the first run. The bottom stack grows on its own (a status appears, the time bar's
// readout wraps), and then only the map's controls need to move.
function watchLayout(state) {
  state.observer = new ResizeObserver(() => layoutViews(state));
  state.observer.observe(state.root);
  state.stackObserver = new ResizeObserver(() => liftMapControls(state));
  state.stackObserver.observe(state.root.querySelector(".bottom"));
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
  const label = () => {
    button.textContent = isFullscreen() ? "✕ Exit full screen" : "⛶ Full screen";
    button.classList.toggle("active", isFullscreen());
  };
  button.onclick = () => (isFullscreen() ? document.exitFullscreen() : root.requestFullscreen()).catch(() => {});
  state.onFullscreenChange = label;
  document.addEventListener("fullscreenchange", label);
  label();
  root.querySelector(".layers").appendChild(button);
}

// The globe/map switch, first among the buttons at the top right: two segments, the current view highlighted, so it
// shows where the user is as well as where they can go. Python picks the view when a site is chosen (data.view,
// applied when view_id changes); in between, this switch changes it here alone, without a rerun.
const VIEW_LABELS = { globe: ["Globe", "moon"], map: ["South pole", "pole-map"] };

function addViewSwitch(state) {
  const group = document.createElement("span");
  group.className = "view-switch";
  group.setAttribute("role", "group");
  group.setAttribute("aria-label", "View");
  Object.entries(VIEW_LABELS).forEach(([name, [label, icon]]) => {
    const b = document.createElement("button");
    b.type = "button";
    b.dataset.view = name;
    b.innerHTML = `<img src="app/static/icons/${icon}.svg" alt="" aria-hidden="true">${label}`;
    b.onclick = () => { if (state.view !== name) { setView(state, name); render(state); } };
    group.appendChild(b);
  });
  const tip = document.createElement("span");
  tip.className = "view-nudge";
  tip.setAttribute("role", "status");
  group.appendChild(tip);
  state.root.querySelector(".layers").prepend(group);
}

function setView(state, name) {
  state.view = name;
  state.root.dataset.view = name;
  state.root.querySelectorAll(".view-switch button").forEach(b => {
    b.classList.toggle("active", b.dataset.view === name);
    b.setAttribute("aria-pressed", b.dataset.view === name);
  });
  nudgeView(state, null);
}

// Points at view `name`'s segment, with `text` under the switch, when the user pushes past what the current view
// shows well (the views call it at their zoom limits). It fades by itself; null clears it.
function nudgeView(state, name, text = "") {
  clearTimeout(state.nudgeTimer);
  state.root.querySelectorAll(".view-switch button").forEach(b => b.classList.toggle("nudge", b.dataset.view === name));
  const tip = state.root.querySelector(".view-nudge");
  tip.textContent = text;
  tip.classList.toggle("shown", !!name);
  if (name) state.nudgeTimer = setTimeout(() => nudgeView(state, null), 5000);
}

// The site the views focus on: in the Site Planner its Surface Asset (key "asset"); otherwise the Custom Site (key
// "custom") if there is one, else the selected Catalog Site.
function focusSite(data) {
  if (data.mode === "planner" && data.asset) {
    return { key: "asset", name: "Surface Asset", kind: "asset", lat: data.asset.lat, lon: data.asset.lon,
             description: "The Site Planner's Surface Asset." };
  }
  if (data.custom) {
    return { key: "custom", name: "Custom Site", kind: "custom", lat: data.custom.lat, lon: data.custom.lon,
             description: "A location you picked." };
  }
  return data.sites.find(s => s.key === data.selected) || null;
}

// A point the user picked rather than a Catalog Site: it is drawn like a selected site but cannot be chosen.
const isPicked = site => site.key === "custom" || site.key === "asset";

// Full screen hides the app's panel, so the view shows the selected site itself.
function updateInfo(state, data) {
  const selected = focusSite(data), info = state.root.querySelector(".info");
  info.classList.toggle("has-site", !!selected);
  info.querySelector(".info-name").textContent = selected ? selected.name : "";
  info.querySelector(".info-text").textContent = selected
    ? `${selected.lat.toFixed(4)}°, ${selected.lon.toFixed(4)}° E · ${selected.description}` : "";
}

// A click beside the sites first clears the selection (outside the Site Planner); "" is the "site" event for none.
function deselect(state) {
  const data = state.data;
  if (data.mode === "planner" || (!data.selected && !data.custom)) return false;
  state.setTriggerValue("site", "");
  return true;
}

// A right-click on the Moon clears everything: it closes an "Analyze this point?" balloon, and leaves the Site Planner
// for browsing (the "site" event with "", which opens the catalog) or clears the selection in the Explorer. A
// right-drag is not a click: the globe pans with it.
function addRightClick(state) {
  let down = null;
  state.root.addEventListener("pointerdown", e => { if (e.button === 2) down = [e.clientX, e.clientY]; }, true);
  state.root.addEventListener("contextmenu", e => {
    if (e.target.closest(".layers, .time-bar")) return;  // the controls keep the browser's menu
    e.preventDefault();
    const moved = down && Math.hypot(e.clientX - down[0], e.clientY - down[1]) > 5;
    down = null;
    if (moved) return;
    state.closeBalloon?.();  // the globe's balloon
    state.map?.leaflet.closePopup();  // the polar map's
    if (state.data.mode === "planner") state.setTriggerValue("site", "");
    else deselect(state);
  });
}

// Great-circle distance (m) on the Moon from a site to a point.
function surfaceDistance(site, lat, lon) {
  const rad = Math.PI / 180, dLat = (lat - site.lat) * rad, dLon = (lon - site.lon) * rad;
  const h = Math.sin(dLat / 2) ** 2 + Math.cos(site.lat * rad) * Math.cos(lat * rad) * Math.sin(dLon / 2) ** 2;
  return 2 * 1737400 * Math.asin(Math.sqrt(Math.min(1, h)));
}

// Where a clicked point's analysis comes from, as get_conditions (src/conditions.py) decides it: a Catalog Site's
// pre-computed Site Neighborhood, else the south pole terrain data (data.zones from src/panels/common.py).
function analysisSource(data, lat, lon) {
  const z = data.zones || { terrain_lat: -80, precomputed_m: 0, precomputed: [] };
  const near = data.sites.find(s => z.precomputed.includes(s.key) && surfaceDistance(s, lat, lon) <= z.precomputed_m);
  if (near) return `pre-computed near ${escapeHtml(near.name)}, opens at once`;
  return lat <= z.terrain_lat ? "computed live, about 30 s"
    : `no terrain data here (outside ${-z.terrain_lat}°S), so the Ideal Horizon is used`;
}

// Asks before analyzing a clicked point as a Custom Site (task A5): the live computation takes about 30 s, so a stray
// click must not start one. Analyze sends the "point" event; `close` removes the balloon and the provisional marker.
function analyzeBalloon(state, lat, lon, close) {
  lon = ((lon + 540) % 360) - 180;
  const el = document.createElement("div");
  el.className = "analyze";
  el.innerHTML = `<b>Analyze this point?</b><div>${lat.toFixed(2)}°, ${lon.toFixed(2)}° E · `
    + `${analysisSource(state.data, lat, lon)}`
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
    addViewSwitch(state);
    addRightClick(state);
    if (root.requestFullscreen) addFullscreenButton(state);
  }
  state.findPanel();
  // Python asks for a view ("globe" or "map"), applied only when view_id changes, so that a view the user picked
  // in the view itself survives the reruns in between.
  if (state.viewId !== data.view_id) {
    state.viewId = data.view_id;
    setView(state, data.view === "map" ? "map" : "globe");
  }
  updateInfo(state, data);
  root.classList.toggle("has-zones", !!data.zones);
  timeBar.update(state, data.time);
  render(state);
  return () => {
    state.observer.disconnect();
    state.stackObserver.disconnect();
    clearTimeout(state.nudgeTimer);
    if (state.onFullscreenChange) document.removeEventListener("fullscreenchange", state.onFullscreenChange);
    Object.values(VIEWS).forEach(view => view.exists(state) && view.destroy(state));
    delete root.__lunav;
  };
}
