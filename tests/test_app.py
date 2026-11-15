"""Smoke test: the app and every panel render without exceptions, using pre-computed catalog data only."""
from streamlit.testing.v1 import AppTest

from src.panels.common import VIEW_CHOICE, VIEWS


def test_every_panel_renders():
    at = AppTest.from_file("../app.py", default_timeout=120).run()
    assert not at.exception
    at.button(key="explorer_pick_Connecting Ridge C1").click().run()  # catalog list -> Site Card
    assert not at.exception
    assert at.session_state["panel"] == "site"
    at.button(key="card_back").click().run()
    at.selectbox(key="search").set_value("Haworth").run()  # search -> Site Card
    assert not at.exception
    assert at.session_state["selected"] == "Haworth"
    at.button(key="card_back").click().run()
    at.button(key="explorer_pick_Apollo 11 (Tranquility Base)").click().run()  # a Site Card with photos
    assert not at.exception
    for panel in ("planner", "about", "catalog"):
        at.button(key=f"rail_{panel}").click().run()
        assert not at.exception, panel
        assert at.session_state["panel"] == panel


def test_choosing_a_site_switches_the_view():
    """Polar sites open on the south polar map and other sites on the globe; other panels keep the view."""
    at = AppTest.from_file("../app.py", default_timeout=120).run()
    assert (at.session_state[VIEW_CHOICE], at.session_state["view_id"]) == (VIEWS[0], 1)
    at.button(key="explorer_pick_Connecting Ridge C1").click().run()
    assert (at.session_state[VIEW_CHOICE], at.session_state["view_id"]) == (VIEWS[1], 2)
    at.button(key="rail_about").click().run()
    at.button(key="rail_catalog").click().run()
    assert (at.session_state[VIEW_CHOICE], at.session_state["view_id"]) == (VIEWS[1], 2)
    at.button(key="explorer_pick_Apollo 11 (Tranquility Base)").click().run()
    assert (at.session_state[VIEW_CHOICE], at.session_state["view_id"]) == (VIEWS[0], 3)
    assert not at.exception


def test_a_second_click_on_the_rail_icon_hides_the_panel():
    at = AppTest.from_file("../app.py", default_timeout=120).run()
    at.button(key="rail_catalog").click().run()
    assert at.session_state["panel_open"] is False  # the catalog, open by default, is now hidden
    at.button(key="rail_catalog").click().run()
    assert at.session_state["panel_open"] is True
    at.button(key="rail_catalog").click().run()
    at.button(key="explorer_pick_Haworth").click().run()  # a hidden panel is still rendered; choosing a site shows it
    assert (at.session_state["panel"], at.session_state["panel_open"]) == ("site", True)
    assert not at.exception

