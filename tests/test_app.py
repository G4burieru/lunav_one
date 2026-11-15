"""Smoke test: the app and every panel render without exceptions, using pre-computed catalog data only."""
from streamlit.testing.v1 import AppTest

from src.panels import texts
from src.panels.common import VIEW_CHOICE, VIEWS


def test_about_shows_each_section_in_an_expander():
    at = AppTest.from_file("../app.py", default_timeout=120).run()
    at.button(key="rail_about").click().run()
    assert [expander.label for expander in at.expander] == list(texts.ABOUT_SECTIONS)
    assert not at.exception


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


def test_leaving_the_planner_keeps_its_view():
    at = AppTest.from_file("../app.py", default_timeout=120).run()
    at.button(key="rail_planner").click().run()  # opens on a polar Catalog Site, on the south polar map
    at.button(key="rail_catalog").click().run()
    assert at.session_state[VIEW_CHOICE] == VIEWS[1]
    assert not at.exception


def test_custom_site_card_renders_offline():
    """A Custom Site within a Catalog Site's Site Neighborhood uses its pre-computed data, so no network."""
    at = AppTest.from_file("../app.py", default_timeout=120).run()
    at.session_state["custom"] = {"lat": -89.4398, "lon": -137.17}  # as a confirmed click on the Moon View sets it
    at.session_state["panel"] = "site"
    at.run()
    assert not at.exception
    assert any("would rank" in m.value for m in at.markdown)


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



def test_a_named_custom_site_stays_on_the_map_until_removed():
    """Keep on the map names the Planner's Custom Site, lists it in the Planner and sends it to the Moon View."""
    at = AppTest.from_file("../app.py", default_timeout=120).run()
    at.session_state["custom"] = {"lat": -89.4398, "lon": -137.17}  # offline: inside a pre-computed neighborhood
    at.button(key="rail_planner").click().run()
    assert at.selectbox(key="planner_site").value == "Custom Site"
    at.text_input(key="planner_name").input("Ridge A").run()
    at.button(key="planner_save").click().run()
    assert not at.exception
    assert at.session_state["saved_sites"] == {"saved:Ridge A": {"name": "Ridge A", "lat": -89.4398, "lon": -137.17}}
    assert at.selectbox(key="planner_site").value == "saved:Ridge A"
    at.button(key="rail_catalog").click().run()  # still kept outside the Planner, and found by the search
    assert "Ridge A · your Custom Site" in at.selectbox(key="search").options
    at.selectbox(key="search").set_value("saved:Ridge A").run()
    assert (at.session_state["panel"], at.selectbox(key="planner_site").value) == ("planner", "saved:Ridge A")
    at.button(key="planner_remove").click().run()
    assert at.session_state["saved_sites"] == {}
    assert at.selectbox(key="planner_site").value == "Custom Site"
    assert not at.exception


def test_planner_sends_all_catalog_states_alongside_the_asset(monkeypatch):
    from src.panels import planner
    from src.sites import LUNAR_SITES
    received = []
    original = planner.planner_time
    def capture(*args, **kwargs):
        payload = original(*args, **kwargs)
        received.append(payload)
        return payload
    monkeypatch.setattr(planner, 'planner_time', capture)
    at = AppTest.from_file('../app.py', default_timeout=120).run()
    at.button(key='rail_planner').click().run()
    assert not at.exception and received
    payload = received[-1]
    assert set(payload['states']) == {*LUNAR_SITES, 'asset'}
    assert payload['hours'] == 14 * 24


def test_a_name_typed_just_before_the_click_is_still_checked(monkeypatch):
    """The button was enabled for the previous name; a taken or empty name sent with the click saves nothing."""
    import rasterio
    import requests

    network_attempts = []
    def unexpected_network(*args, **kwargs):
        network_attempts.append(args[0] if args else kwargs)
        raise RuntimeError("Name validation must use pre-computed data, without Horizons or remote DEM reads")

    monkeypatch.setattr(requests, "get", unexpected_network)
    monkeypatch.setattr(rasterio, "open", unexpected_network)
    at = AppTest.from_file("../app.py", default_timeout=120).run()
    at.session_state["custom"] = {"lat": -89.4398, "lon": -137.17}
    at.button(key="rail_planner").click().run()
    at.text_input(key="planner_name").input("Ridge A").run()
    at.button(key="planner_save").click().run()
    saved = dict(at.session_state["saved_sites"])
    # The coordinate widgets disappear while a saved site is selected, so Streamlit cleans their keys.
    # Seed the covered point again before recreating them; their defaults (-89.5, 0) need live science.
    at.session_state["planner_lat"], at.session_state["planner_lon"] = -89.4398, -137.17
    at.selectbox(key="planner_site").set_value("Custom Site").run()
    assert at.number_input(key="planner_lat").value == -89.4398
    assert at.number_input(key="planner_lon").value == -137.17
    assert not at.error
    for name in ("Ridge A", "Haworth", "  "):
        at.text_input(key="planner_name").input("Ridge B").run()  # enables the button
        at.text_input(key="planner_name").input(name)
        at.button(key="planner_save").click().run()
        assert at.session_state["saved_sites"] == saved, name
        assert not at.error
    assert not at.exception
    assert not network_attempts


def test_a_failing_saved_site_is_not_retried_on_every_rerun(monkeypatch):
    """A saved Custom Site whose live computation fails stays without a badge instead of blocking every rerun."""
    import requests
    calls = []

    def offline(*args, **kwargs):
        calls.append(1)
        raise requests.ConnectionError("offline")

    monkeypatch.setattr(requests, "get", offline)
    at = AppTest.from_file("../app.py", default_timeout=120)
    at.session_state["saved_sites"] = {"saved:Equator": {"name": "Equator", "lat": 10.123, "lon": 10.456}}
    at.run()
    assert calls  # tried once: a live point, JPL Horizons is unreachable
    tried = len(calls)
    at.button(key="rail_about").click().run()
    at.button(key="rail_catalog").click().run()
    assert len(calls) == tried
    assert not at.exception
