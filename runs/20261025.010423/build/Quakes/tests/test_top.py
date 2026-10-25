"""Top-report story: the largest events by magnitude, time ascending on ties, cut to `--n` after filtering."""

import csv
import datetime
import io

from cli import reports
from cli.feed import Event

HEADER = ["time", "mag", "depth_km", "place", "id"]
BASE = 1735689600000


def _feature(ident, mag, time_ms, *, place="P", depth=0.0):
    return {
        "type": "Feature",
        "id": ident,
        "properties": {"mag": mag, "place": place, "time": time_ms, "tsunami": 0},
        "geometry": {"type": "Point", "coordinates": [0.0, 0.0, depth]},
    }


def _rows(out):
    return list(csv.reader(io.StringIO(out)))


def _event(ident, mag, time_ms):
    return Event(id=ident, mag=mag, place="P", time_ms=time_ms, tsunami=0, lon=0.0, lat=0.0, depth_km=0.0)


# ── Declared acceptance assertions ──────────────────────────────────────────────────────


def test_top_order_and_default_n(write_feed, cli_runner):
    # (id, mag, minutes offset); two pairs tie on magnitude with different times.
    specs = [("a", 5.0, 50), ("b", 6.0, 40), ("c", 6.0, 10), ("d", 5.5, 30), ("e", 5.1, 20),
             ("f", 7.0, 60), ("g", 5.2, 70), ("h", 5.3, 80), ("i", 5.4, 90), ("j", 5.6, 15),
             ("k", 5.7, 25), ("l", 5.8, 35)]
    features = [_feature(s[0], s[1], BASE + s[2] * 60000, depth=12.0) for s in specs]
    code, out, _ = cli_runner("top", write_feed(features))
    assert code == 0
    rows = _rows(out)
    header, body = rows[0], rows[1:]
    assert header == HEADER
    ranked = sorted(specs, key=lambda s: (-s[1], s[2]))
    default_n = 10
    assert len(specs) > default_n
    assert [r[4] for r in body] == [s[0] for s in ranked[:default_n]]
    first = dict(zip(header, body[0]))
    assert float(first["mag"]) == ranked[0][1]
    assert float(first["depth_km"]) == 12.0
    parsed = datetime.datetime.fromisoformat(first["time"])
    assert int(parsed.timestamp() * 1000) == BASE + ranked[0][2] * 60000


def test_top_n_option(write_feed, cli_runner):
    specs = [("a", 5.0), ("b", 6.0), ("c", 7.1), ("d", 5.5), ("e", 6.2)]
    features = [_feature(s[0], s[1], BASE + i * 1000, depth=5.0) for i, s in enumerate(specs)]
    count = 3
    code, out, _ = cli_runner("top", "--n", str(count), write_feed(features))
    assert code == 0
    body = _rows(out)[1:]
    assert [r[4] for r in body] == [s[0] for s in sorted(specs, key=lambda s: -s[1])[:count]]


def test_top_min_mag_before_cut(write_feed, cli_runner):
    specs = [("a", 5.0), ("b", 5.1), ("c", 5.2), ("d", 6.0), ("e", 7.0)]
    features = [_feature(s[0], s[1], BASE + i * 1000, depth=5.0) for i, s in enumerate(specs)]
    threshold = 5.1
    count = 4
    code, out, _ = cli_runner("top", "--min-mag", str(threshold), "--n", str(count), write_feed(features))
    assert code == 0
    body = _rows(out)[1:]
    kept = sorted([s for s in specs if s[1] >= threshold], key=lambda s: -s[1])
    assert [r[4] for r in body] == [s[0] for s in kept[:count]]
    assert all(float(r[1]) >= threshold for r in body)


def test_top_place_with_comma(write_feed, cli_runner):
    place = "56 km SSE of Some Town, Some Country"
    features = [_feature("c1", 6.2, BASE, place=place, depth=46.0)]
    code, out, _ = cli_runner("top", write_feed(features))
    assert code == 0
    body = _rows(out)[1:]
    assert len(body) == 1
    assert body[0][3] == place
    assert body[0][4] == "c1"


def test_top_empty_result(write_feed, cli_runner):
    code, out, _ = cli_runner("top", "--min-mag", "9", write_feed([_feature("e0", 5.0, BASE, depth=1.0)]))
    assert code == 0
    assert _rows(out) == [HEADER]


def test_top_usage_errors(write_feed, cli_runner):
    path = write_feed([_feature("e0", 5.0, BASE, depth=1.0)])
    for args in (("top", "--n", "0", path),
                 ("top", "--n", "-2", path),
                 ("top", "--n", "many", path),
                 ("top", "--lat", "1", path),
                 ("top",)):
        code, out, _ = cli_runner(*args)
        assert code == 2, args
        assert out == "", args


# ── Finer coverage ──────────────────────────────────────────────────────────────────────


def test_top_ties_on_mag_and_time_keep_feed_order():
    events = [_event("first", 6.0, BASE), _event("second", 6.0, BASE)]
    rows = reports.compute_top(events, 2)
    assert [r[4] for r in rows[1:]] == ["first", "second"]


def test_top_n_larger_than_events_returns_all():
    rows = reports.compute_top([_event("a", 5.0, BASE)], 50)
    assert len(rows) == 2


def test_top_null_place_is_empty_field():
    event = Event(id="z", mag=5.0, place=None, time_ms=BASE, tsunami=0, lon=0.0, lat=0.0, depth_km=1.0)
    rows = reports.compute_top([event], 1)
    assert rows[1][3] == ""
