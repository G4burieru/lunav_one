// Moon View entry point (docs/adr/0003-one-screen-moon-view.md). src/moon_view/__init__.py joins the view files
// before this one into a single module. Streamlit calls the default export again on every rerun with new data, on
// the same element, so the view is created once and then only updated.
export default function (component) {
  const { data, parentElement, setTriggerValue } = component;
  const root = parentElement.querySelector(".moon-view");
  root.style.setProperty("--view-height", data.height);
  const state = root.__lunav || (root.__lunav = { root });
  state.setTriggerValue = setTriggerValue;
  state.data = data;  // the views read the latest data from here, including in their event handlers
  globeView.load().then(() => {
    if (!state.globe) globeView.create(state);
    globeView.update(state, data);
  }).catch(() => {
    root.querySelector(".status").textContent = "Could not load globe.gl from the CDN.";
  });
  return () => {
    state.observer?.disconnect();
    if (state.onFullscreenChange) document.removeEventListener("fullscreenchange", state.onFullscreenChange);
    state.globe?._destructor?.();
    delete root.__lunav;
  };
}
