"""Regions-report story: events per region derived from the place text, with the maximum magnitude."""

import csv
import io

import pytest

from cli import reports
from cli.feed import extract_events

HEADER = ["region", "events", "max_mag"]


def _feature(ident, mag, place, time_ms=1735706358208, tsunami=0):
    return {
        "type": "Feature",
        "properties": {"mag": mag, "place": place, "time": time_ms, "tsunami": tsunami},
        "geometry": {"type": "Point", "coordinates": [1.0, 2.0, 3.0]},
        "id": ident,
    }


def _rows(out):
    return list(csv.reader(io.StringIO(out)))


# ── Declared acceptance assertions ──────────────────────────────────────────────────────


def test_regions_extract_and_order(write_feed, cli_runner):
    pairs = [
        ("Zed", 5.0), ("Zed", 5.6),
        ("alpha", 5.1),
        ("Beta", 5.2), ("Beta", 5.0),
        ("Gamma", 5.3), ("Gamma", 5.9), ("Gamma", 5.1),
        ("Delta", 5.4),
    ]
    features = [_feature("e" + str(i), mag, "12 km N of Town " + str(i) + ", " + region, 1735706358208 + i)
                for i, (region, mag) in enumerate(pairs)]
    expected = {}
    for region, mag in pairs:
        entry = expected.setdefault(region, [0, mag])
        entry[0] += 1
        entry[1] = max(entry[1], mag)
    order = sorted(expected, key=lambda r: (-expected[r][0], r))
    code, out, _ = cli_runner("regions", write_feed(features))
    assert code == 0
    rows = _rows(out)
    assert rows[0] == HEADER
    assert [r[0] for r in rows[1:]] == order
    for r in rows[1:]:
        assert int(r[1]) == expected[r[0]][0]
        assert float(r[2]) == expected[r[0]][1]


def test_regions_place_rules(write_feed, cli_runner):
    last_part = "Country"
    multi_place = "Near Town, Province, " + last_part
    plain_place = "Mid-Atlantic Ridge"
    comma_no_space = "A,B"
    places = [multi_place, plain_place, comma_no_space, None]
    features = [_feature("e" + str(i), 5.0, place, 1735706358208 + i) for i, place in enumerate(places)]
    code, out, _ = cli_runner("regions", write_feed(features))
    assert code == 0
    names = {r[0] for r in _rows(out)[1:]}
    assert names == {last_part, plain_place, comma_no_space, "Unknown"}


def test_regions_min_mag_and_empty(write_feed, cli_runner):
    threshold = 5.4
    pairs = [("Aland", 5.0), ("Aland", 5.4), ("Bland", 6.0), ("Cland", None), ("Dland", 5.3)]
    features = [_feature("e" + str(i), mag, "5 km S of T, " + region, 1735706358208 + i)
                for i, (region, mag) in enumerate(pairs)]
    path = write_feed(features)
    kept = [(r, m) for r, m in pairs if m is not None and m >= threshold]
    code, out, _ = cli_runner("regions", "--min-mag", str(threshold), path)
    code_none, out_none, _ = cli_runner("regions", "--min-mag", "9", path)
    assert code == 0 and code_none == 0
    rows = _rows(out)
    assert {r[0] for r in rows[1:]} == {r for r, _ in kept}
    assert sum(int(r[1]) for r in rows[1:]) == len(kept)
    assert _rows(out_none) == [HEADER]


def test_regions_failure_contract(tmp_path, cli_runner):
    bad = tmp_path / "bad.json"
    bad.write_text("this is not json", encoding="utf-8")
    code, out, _ = cli_runner("regions", str(bad))
    assert code == 1
    assert out == ""
    code2, out2, _ = cli_runner("regions", "--lat", "1", str(bad))
    assert code2 == 2
    assert out2 == ""


# ── Finer coverage ──────────────────────────────────────────────────────────────────────


@pytest.mark.parametrize(
    ("place", "region"),
    [
        ("56 km SSE of La Libertad, El Salvador", "El Salvador"),
        ("a, b, c", "c"),
        ("Fiji region", "Fiji region"),
        ("Tonga, ", ""),
        (None, "Unknown"),
    ],
)
def test_region_of(place, region):
    assert reports.region_of(place) == region


def test_regions_same_count_breaks_tie_by_code_point_order():
    features = [_feature("a", 5.0, "x, b"), _feature("b", 5.0, "x, B")]
    # "B" (0x42) sorts before "b" (0x62); both have one event so the order is by name alone.
    rows = reports.compute_regions(extract_events(features))
    assert [r[0] for r in rows[1:]] == ["B", "b"]


def test_regions_empty_input_is_header_only():
    assert reports.compute_regions([]) == [HEADER]
