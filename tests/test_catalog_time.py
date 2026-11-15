"""Regression coverage for Catalog Site states on the Explorer and Planner time axes."""
import base64
import json
import os
from pathlib import Path
import shutil
import subprocess

import numpy as np
import pandas as pd
import pytest

from src.metrics import hourly_states
from src.panels import common
from src.sites import LUNAR_SITES


def decode(value):
    return np.frombuffer(base64.b64decode(value), dtype=np.uint8)


@pytest.fixture(autouse=True)
def clear_time_cache():
    common._catalog_time.clear()
    yield
    common._catalog_time.clear()


def test_explorer_has_real_states_for_all_seventeen_sites():
    payload = common.catalog_time()
    assert set(payload['states']) == set(LUNAR_SITES)
    assert payload['hours'] == 731 * 24
    assert payload['start'] == '2027-01-01T00:00:00Z'
    for key, site in LUNAR_SITES.items():
        df = common.get_data(site['lat'], site['lon'], '2027-01-01', 731)
        np.testing.assert_array_equal(decode(payload['states'][key]), hourly_states(df))


@pytest.mark.parametrize('mask', [0.0, 3.0])
def test_planner_catalog_and_asset_share_window_mask_and_selected_instant(mask):
    site = LUNAR_SITES['Connecting Ridge C1']
    df = common.get_data(site['lat'], site['lon'], '2028-02-28', 3)
    instant = '2028-02-29T12:00:00Z'
    payload = common.planner_time(df, instant, mask)
    assert payload['start'] == '2028-02-28T00:00:00Z'
    assert payload['hours'] == 72 and payload['instant'] == instant
    assert set(payload['states']) == {*LUNAR_SITES, 'asset'}
    for key, location in LUNAR_SITES.items():
        expected = common.get_data(location['lat'], location['lon'], '2028-02-28', 3)
        np.testing.assert_array_equal(decode(payload['states'][key]), hourly_states(expected, mask))
    np.testing.assert_array_equal(decode(payload['states']['asset']), hourly_states(df, mask))


@pytest.mark.parametrize('start,hours', [('2026-12-31', 48), ('2028-12-31', 48),
                                        ('2027-01-01 01:00', 24), ('2027-01-01', 25)])
def test_planner_does_not_reuse_cached_states_for_another_axis(monkeypatch, start, hours):
    def unexpected(*args):
        pytest.fail('Catalog data must not be requested for an uncovered or unsupported axis')
    monkeypatch.setattr(common, 'catalog_time', unexpected)
    df = pd.DataFrame({'time': pd.date_range(start, periods=hours, freq='h'),
                       'illumination_fraction': 0.25, 'earth_elevation': 1.0})
    payload = common.planner_time(df)
    assert set(payload['states']) == {'asset'}
    assert len(decode(payload['states']['asset'])) == hours


def test_unavailable_or_misaligned_catalog_data_does_not_create_states(monkeypatch):
    bad, shifted = list(LUNAR_SITES)[:2]
    original = common.get_data
    def data(lat, lon, date, days):
        if (lat, lon) == (LUNAR_SITES[bad]['lat'], LUNAR_SITES[bad]['lon']):
            raise OSError('unavailable')
        df = original(lat, lon, date, days)
        if (lat, lon) == (LUNAR_SITES[shifted]['lat'], LUNAR_SITES[shifted]['lon']):
            df = df.copy()
            df['time'] += pd.Timedelta(hours=1)
        return df
    monkeypatch.setattr(common, 'get_data', data)
    payload = common.catalog_time(common.CACHE_START, 1)
    assert set(payload['states']) == set(LUNAR_SITES) - {bad, shifted}


def test_javascript_badges_follow_the_selected_hour_in_both_views(tmp_path):
    """Execute the production decoder and both view painters with lightweight marker elements.

    NODE_BINARY can select an existing Node-compatible runtime; no package install or browser network needed.
    """
    node = os.environ.get('NODE_BINARY') or shutil.which('node')
    if not node:
        pytest.skip('A Node-compatible runtime is needed for the JavaScript badge regression')
    source = Path(__file__).resolve().parents[1] / 'src' / 'moon_view'
    explorer = common.catalog_time(common.CACHE_START, 1)
    site = LUNAR_SITES['Connecting Ridge C1']
    asset = common.get_data(site['lat'], site['lon'], '2027-01-01', 1)
    payloads = {'explorer': explorer, 'planner': common.planner_time(asset)}
    script = 'const assert = require("node:assert/strict");\n'
    script += 'const window = {matchMedia: () => ({matches: false})};\n'
    script += '\n'.join((source / name).read_text(encoding='utf-8') for name in
                        ['globe.js', 'polar_map.js', 'time_bar.js'])
    script += (source / 'view.js').read_text(encoding='utf-8').split('export default')[0]
    script += '\nconst payloads = ' + json.dumps(payloads) + ';\n'
    script += r'''
function element() {
  const classes = new Set(), sun = {style: {}};
  return {classes, sun, classList: {toggle: (name, on) => on ? classes.add(name) : classes.delete(name)},
          querySelector: () => sun, setAttribute: () => {}};
}
for (const [mode, payload] of Object.entries(payloads)) {
  const keys = Object.keys(payload.states);
  const state = {data: {mode}, time: {index: 0, states: Object.fromEntries(
    keys.map(key => [key, Uint8Array.from(Buffer.from(payload.states[key], 'base64'))]))}};
  state.globeItems = keys.map(key => ({key, name: key, kind: 'site', el: element()}));
  state.map = {markers: state.globeItems.map(item => ({key: item.key, marker: {getElement: () => item.el}}))};
  for (const index of [0, 7, 23]) {
    state.time.index = index;
    for (const view of [globeView, polarMap]) {
      view.paint(state);
      for (const item of state.globeItems) {
        const byte = Buffer.from(payload.states[item.key], 'base64')[index];
        assert(item.el.classes.has('timed'));
        assert.equal(item.el.sun.style.clipPath, `inset(${100 - (byte & 127)}% 0 0 0)`);
        assert.equal(item.el.classes.has('earth-up'), byte >= 128);
      }
    }
  }
  delete state.time.states[keys[0]];
  for (const view of [globeView, polarMap]) {
    view.paint(state);
    assert.equal(state.globeItems[0].el.classes.has('timed'), false);
  }
}
'''
    path = tmp_path / 'badges.cjs'
    path.write_text(script, encoding='utf-8')
    subprocess.run([node, str(path)], check=True, capture_output=True, text=True,
                   env={**os.environ, 'ELECTRON_RUN_AS_NODE': '1'}, timeout=20)


@pytest.mark.parametrize('unit', ['s', 'us', 'ns'])
def test_matching_time_axes_do_not_depend_on_datetime_storage_precision(monkeypatch, unit):
    """Pandas 2/3 can represent the same hours with different datetime64 units."""
    df = pd.DataFrame({'time': pd.date_range('2027-01-01', periods=24, freq='h'),
                       'illumination_fraction': 0.25, 'earth_elevation': 1.0})
    df['time'] = df['time'].astype(f'datetime64[{unit}]')
    monkeypatch.setattr(common, 'get_data', lambda *args: df)
    payload = common.planner_time(df, elevation_mask=2.0)
    assert set(payload['states']) == {*LUNAR_SITES, 'asset'}
    assert payload['hours'] == 24
    for states in payload['states'].values():
        # Quarter solar disk visible; Earth's center is below the requested 2 degree mask.
        assert decode(states).tolist() == [25] * 24
