"""Smoke test: the app and every panel render without exceptions, using pre-computed catalog data only."""
from streamlit.testing.v1 import AppTest


def test_every_panel_renders():
    at = AppTest.from_file("../app.py", default_timeout=120).run()
    assert not at.exception
    at.button(key="explorer_pick_Connecting Ridge C1").click().run()  # catalog list -> Site Card
    assert not at.exception
    assert at.session_state["panel"] == "site"
    for panel in ("planner", "about", "catalog"):
        at.button(key=f"rail_{panel}").click().run()
        assert not at.exception, panel
        assert at.session_state["panel"] == panel
