// Time bar (docs/UI_OVERHAUL.md, task A3): a slider over the window in data.time, play and pause, and the UTC
// instant. Moving it repaints the markers of both views with each hour's state (src/metrics.hourly_states: one
// byte per hour, bits 0-6 the Illumination Fraction in percent, bit 7 Earth Visibility). Releasing the slider, or
// pausing, sends `instant` to Python, where the Site Card follows it.
const timeBar = (() => {
  const HOUR_MS = 3600e3;
  const ICONS = { play: '<path d="M8 5v14l11-7z"/>', pause: '<path d="M7 5h4v14H7zM13 5h4v14h-4z"/>' };
  // Playback speed in hours per second: a lunar day in about ten seconds over the Explorer's two years, and about
  // forty seconds for a whole Site Planner window.
  const speed = hours => Math.min(72, Math.max(6, hours / 40));
  const pad = n => String(n).padStart(2, "0");

  function decode(base64) {
    const text = atob(base64), bytes = new Uint8Array(text.length);
    for (let i = 0; i < text.length; i++) bytes[i] = text.charCodeAt(i);
    return bytes;
  }

  // The state of `key` (a Catalog Site key, or "asset" in the Site Planner) at the bar's hour:
  // {sun: Illumination Fraction in %, earth: Earth visible}, or null when there is no time data for it.
  function stateOf(state, key) {
    const t = state.time, bytes = t && t.states[key];
    if (!bytes) return null;
    const byte = bytes[Math.min(t.index, bytes.length - 1)];
    return { sun: byte & 0x7f, earth: byte >= 0x80 };
  }

  const at = t => new Date(t.start + t.index * HOUR_MS);
  const label = d => `${d.getUTCFullYear()}-${pad(d.getUTCMonth() + 1)}-${pad(d.getUTCDate())} ${pad(d.getUTCHours())}:00 UTC`;
  const bar = state => state.root.querySelector(".time-bar");

  // In words, for the Site Planner's Surface Asset, the Custom Site or the selected site, in the Site Card's terms;
  // without any of them, how to read the markers.
  function readout(state) {
    const data = state.data;
    const key = data.mode === "planner" && data.asset ? "asset" : data.custom ? "custom" : data.selected;
    const s = key ? stateOf(state, key) : null;
    if (!s) return "Markers fill with sunlight · the dot is filled while Earth is in view";
    const name = { asset: "Surface Asset", custom: "Custom Site" }[key]
      || (data.sites.find(site => site.key === key) || {}).name;
    const sun = s.sun >= 100 ? "Sun up" : s.sun > 0 ? `Sun partly hidden (${s.sun}% of the disk)` : "Sun down";
    return `${name}: ${sun} · ${s.earth ? "Earth in view" : "Earth below the horizon"}`;
  }

  function show(state) {
    const t = state.time, el = bar(state);
    el.querySelector(".time-slider").value = t.index;
    el.querySelector(".time-label").textContent = label(at(t));
    el.querySelector(".time-readout").textContent = readout(state);
    paintViews(state);
  }

  function setPlaying(state, playing) {
    const t = state.time, button = bar(state).querySelector(".play");
    t.playing = playing;
    if (!playing) cancelAnimationFrame(t.frame);
    button.innerHTML = `<svg viewBox="0 0 24 24" aria-hidden="true">${playing ? ICONS.pause : ICONS.play}</svg>`;
    button.setAttribute("aria-label", playing ? "Pause" : "Play");
  }

  // Tell Python the bar's instant. Debounced, so that holding an arrow key on the slider reruns the app once.
  function send(state) {
    const t = state.time;
    clearTimeout(t.timer);
    t.timer = setTimeout(() => state.setStateValue("instant", at(t).toISOString().replace(".000Z", "Z")), 250);
  }

  function play(state) {
    const t = state.time;
    if (t.index >= t.hours - 1) t.index = 0;  // at the end: play again from the start
    setPlaying(state, true);
    let clock = performance.now(), hours = 0;
    const step = now => {
      if (!t.playing || state.time !== t) return;
      hours += (now - clock) / 1000 * speed(t.hours);
      clock = now;
      if (hours >= 1) {
        t.index = Math.min(t.hours - 1, t.index + Math.floor(hours));
        hours %= 1;
        show(state);
      }
      if (t.index >= t.hours - 1) pause(state);
      else t.frame = requestAnimationFrame(step);
    };
    t.frame = requestAnimationFrame(step);
  }

  function pause(state) {
    setPlaying(state, false);
    send(state);
  }

  function wire(state) {
    const el = bar(state), slider = el.querySelector(".time-slider");
    el.querySelector(".play").addEventListener("click", () => (state.time.playing ? pause(state) : play(state)));
    slider.addEventListener("input", () => {  // dragging, or arrow keys: follow at once, and stop playback
      if (state.time.playing) setPlaying(state, false);
      state.time.index = +slider.value;
      show(state);
    });
    slider.addEventListener("change", () => send(state));  // released, or a key pressed
  }

  // Called on every rerun. A new window (Explorer and Site Planner differ) starts at Python's instant; the same
  // window keeps the bar where it is, playing or not, so that reruns from the panels do not move it.
  function update(state, time) {
    const el = bar(state);
    if (!state.timeWired) { wire(state); state.timeWired = true; }
    const old = state.time;
    if (!time || !time.hours) {
      if (old) setPlaying(state, false);
      state.time = null;
      el.hidden = true;
      state.root.classList.remove("has-time");
      return;
    }
    const start = Date.parse(time.start);
    if (!old || old.start !== start || old.hours !== time.hours) {
      if (old) setPlaying(state, false);
      const wanted = time.instant ? Math.round((Date.parse(time.instant) - start) / HOUR_MS) : 0;
      state.time = { start, hours: time.hours, index: Math.min(Math.max(wanted, 0), time.hours - 1), raw: {},
                     states: {}, playing: false };
      el.querySelector(".time-slider").max = time.hours - 1;
      setPlaying(state, false);
    }
    const t = state.time, keys = Object.keys(time.states);
    if (keys.length !== Object.keys(t.raw).length || keys.some(key => t.raw[key] !== time.states[key])) {
      t.raw = time.states;  // decoded only when they change: the Explorer sends about 190 KB on every rerun
      t.states = Object.fromEntries(keys.map(key => [key, decode(time.states[key])]));
    }
    el.hidden = false;
    state.root.classList.add("has-time");
    show(state);
  }

  return { update, stateOf };
})();
