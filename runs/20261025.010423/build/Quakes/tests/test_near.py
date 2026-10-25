"""Near-report story: events within a haversine great-circle distance of a point, nearest first."""

import csv
import io
import json
import math
import os

import pytest

from cli import reports
from cli.feed import Event

HEADER = ["distance_km", "time", "mag", "place", "id"]


def _hav(lat1, lon1, lat2, lon2):
    """Independent haversine on a 6371.0 km sphere, written separately from the product code."""
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = p2 - p1
    dlam = math.radians(lon2 - lon1)
    h = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlam / 2) ** 2
    return 2 * 6371.0 * math.asin(math.sqrt(h))


def _feature(ident, mag, time_ms, lon, lat, place="P"):
    return {
        "type": "Feature",
        "properties": {"mag": mag, "place": place, "time": time_ms, "tsunami": 0},
        "geometry": {"type": "Point", "coordinates": [lon, lat, 10.0]},
        "id": ident,
    }


def _rows(out):
    return list(csv.reader(io.StringIO(out)))


def _event(ident, lat, lon, time_ms=1736200000000, mag=5.0):
    return Event(id=ident, mag=mag, place="P", time_ms=time_ms, tsunami=0, lon=lon, lat=lat, depth_km=1.0)


# ── Declared acceptance assertions ──────────────────────────────────────────────────────


def test_near_haversine_distance_and_radius(write_feed, cli_runner):
    origin = (27.72, 85.32)
    points = [
        ("far", 35.68, 139.69),
        ("mid", 28.60, 87.37),
        ("near1", 28.80, 87.13),
        ("near2", 28.50, 87.35),
    ]
    features = [_feature(name, 5.0 + i / 10, 1736200000000 + i * 1000, lon, lat, place="Place " + name)
                for i, (name, lat, lon) in enumerate(points)]
    dist = {name: _hav(origin[0], origin[1], lat, lon) for name, lat, lon in points}
    radius = round(sorted(dist.values())[2] + 1.0, 1)
    inside = sorted([n for n in dist if dist[n] <= radius], key=lambda n: dist[n])
    assert 0 < len(inside) < len(points)
    code, out, _ = cli_runner(
        "near", "--lat", str(origin[0]), "--lon", str(origin[1]), "--radius", str(radius), write_feed(features)
    )
    assert code == 0
    rows = _rows(out)
    assert rows[0] == HEADER
    assert [r[4] for r in rows[1:]] == inside
    for r in rows[1:]:
        assert abs(float(r[0]) - dist[r[4]]) <= 0.051


def test_near_ordering_ties_and_quoting(write_feed, cli_runner):
    place = "10 km N of Somewhere, Country"
    times = [1736200003000, 1736200001000, 1736200002000]
    features = [_feature("t" + str(i), 5.0, t, 10.0, 10.0, place=place) for i, t in enumerate(times)]
    expected_ids = ["t" + str(i) for i in sorted(range(len(times)), key=lambda i: times[i])]
    code, out, _ = cli_runner("near", "--lat", "10", "--lon", "10.5", "--radius", "500", write_feed(features))
    assert code == 0
    rows = _rows(out)
    assert [r[4] for r in rows[1:]] == expected_ids
    assert all(r[3] == place for r in rows[1:])


def test_near_min_mag_null_mag_and_empty(write_feed, cli_runner):
    threshold = 5.3
    mags = [5.0, 5.3, 6.0, None]
    features = [_feature("m" + str(i), m, 1736200000000 + i, 20.0, 20.0, place="P" + str(i))
                for i, m in enumerate(mags)]
    path = write_feed(features)
    kept = ["m" + str(i) for i, m in enumerate(mags) if m is not None and m >= threshold]
    code, out, _ = cli_runner("near", "--lat", "20", "--lon", "20", "--radius", "50", "--min-mag", str(threshold), path)
    code_e, out_e, _ = cli_runner("near", "--lat", "0", "--lon", "0", "--radius", "100", path)
    assert code == 0 and code_e == 0
    rows = _rows(out)
    assert sorted(r[4] for r in rows[1:]) == sorted(kept)
    assert _rows(out_e) == [HEADER]


def test_near_usage_errors(write_feed, cli_runner):
    path = write_feed([])
    cases = [
        ("near", "--lat", "10", "--lon", "10", path),
        ("near", "--lat", "10", "--radius", "5", path),
        ("near", "--lon", "10", "--radius", "5", path),
        ("near", "--lat", "95", "--lon", "0", "--radius", "10", path),
        ("near", "--lat", "0", "--lon", "181", "--radius", "10", path),
        ("near", "--lat", "0", "--lon", "0", "--radius", "0", path),
        ("near", "--lat", "x", "--lon", "0", "--radius", "5", path),
        ("near", "--lat", "0", "--lon", "0", "--radius", "5", "--n", "2", path),
    ]
    for args in cases:
        code, out, _ = cli_runner(*args)
        assert code == 2, args
        assert out == "", args


def test_near_unreadable_file(tmp_path, cli_runner):
    missing = os.path.join(tmp_path, "absent.geojson")
    code, out, _ = cli_runner("near", "--lat", "1", "--lon", "1", "--radius", "5", missing)
    assert code == 1
    assert out == ""


# ── Finer coverage ──────────────────────────────────────────────────────────────────────


def test_haversine_one_degree_of_equator_longitude():
    # One degree of longitude on the equator is 2 * pi * 6371 / 360 kilometres.
    expected = 2 * math.pi * 6371.0 / 360
    assert reports.haversine_km(0.0, 0.0, 0.0, 1.0) == pytest.approx(expected, rel=1e-12)


def test_haversine_zero_for_same_point():
    assert reports.haversine_km(27.72, 85.32, 27.72, 85.32) == 0.0


def test_haversine_antipodal_points_do_not_raise():
    # Antipodal points give h == 1, so asin's argument sits at its limit and must not raise.
    assert reports.haversine_km(0.0, 0.0, 0.0, 180.0) == pytest.approx(math.pi * 6371.0)


def test_near_radius_boundary_is_inclusive(write_feed, cli_runner):
    distance = reports.haversine_km(0.0, 0.0, 0.0, 1.0)
    features = [_feature("edge", 5.0, 1736200000000, 1.0, 0.0)]
    code, out, _ = cli_runner("near", "--lat", "0", "--lon", "0", "--radius", repr(distance), write_feed(features))
    assert code == 0
    assert [r[4] for r in _rows(out)[1:]] == ["edge"]


def test_near_compute_orders_by_distance_then_time():
    events = [_event("far", 0.0, 2.0), _event("late", 0.0, 1.0, time_ms=2000), _event("early", 0.0, 1.0, time_ms=1000)]
    rows = reports.compute_near(events, 0.0, 0.0, 500.0)
    assert [r[4] for r in rows[1:]] == ["early", "late", "far"]


def test_near_null_place_is_empty_field():
    event = Event(id="z", mag=5.0, place=None, time_ms=1736200000000, tsunami=0, lon=0.0, lat=0.0, depth_km=1.0)
    rows = reports.compute_near([event], 0.0, 0.0, 1.0)
    assert rows[1][3] == ""
