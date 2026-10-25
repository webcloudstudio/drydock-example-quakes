"""Feed-validation story: read_feed returns the features of a FeatureCollection or raises OperationalError."""

import json

import pytest

from cli.errors import OperationalError
from cli.feed import read_feed


def _write(tmp_path, name, text):
    path = tmp_path / name
    path.write_text(text, encoding="utf-8")
    return path


def _feature(ident):
    return {"type": "Feature", "id": ident, "properties": {"mag": 5.0}, "geometry": None}


# ── Declared acceptance assertions ──────────────────────────────────────────────────────


def test_feed_valid_collection(tmp_path):
    features = [_feature("a"), _feature("b")]
    full = _write(tmp_path, "full.geojson", json.dumps({"type": "FeatureCollection", "features": features}))
    assert read_feed(full) == features
    assert read_feed(str(full)) == features

    empty = _write(tmp_path, "empty.geojson", json.dumps({"type": "FeatureCollection", "features": []}))
    assert read_feed(empty) == []


def test_feed_unreadable_file(tmp_path):
    for target in (tmp_path / "no-such-file.geojson", tmp_path):
        with pytest.raises(OperationalError):
            read_feed(target)


def test_feed_not_json(tmp_path):
    garbage = _write(tmp_path, "garbage.json", "this is not json\n")
    with pytest.raises(OperationalError):
        read_feed(garbage)


@pytest.mark.parametrize(
    "value",
    [
        {"type": "Feature", "properties": {}, "geometry": None},
        {"type": "FeatureCollection"},
        {"type": "FeatureCollection", "features": {"a": 1}},
        {"type": "FeatureCollection", "features": None},
        {"features": []},
        [],
        "FeatureCollection",
        None,
    ],
)
def test_feed_wrong_shape(tmp_path, value):
    path = _write(tmp_path, "bad.json", json.dumps(value))
    with pytest.raises(OperationalError):
        read_feed(path)


# ── Finer coverage: each failure branch and the returned value ──────────────────────────


def test_read_feed_returns_features_in_feed_order_unchanged(tmp_path):
    features = [_feature("z"), _feature("a"), {"type": "Feature", "id": "m", "extra": [1, 2]}]
    path = _write(tmp_path, "order.geojson", json.dumps({"type": "FeatureCollection", "features": features}))
    assert read_feed(path) == features


def test_read_feed_ignores_other_top_level_members(tmp_path):
    document = {"type": "FeatureCollection", "metadata": {"count": 1}, "features": [_feature("a")]}
    assert read_feed(_write(tmp_path, "meta.geojson", json.dumps(document))) == [_feature("a")]


def test_read_feed_rejects_a_file_that_is_not_utf8(tmp_path):
    path = tmp_path / "latin.geojson"
    path.write_bytes(b'{"type": "FeatureCollection", "features": [], "place": "\xff"}')
    with pytest.raises(OperationalError):
        read_feed(path)


def test_read_feed_rejects_an_empty_file(tmp_path):
    with pytest.raises(OperationalError):
        read_feed(_write(tmp_path, "empty.geojson", ""))


def test_read_feed_rejects_a_json_array_at_the_top_level(tmp_path):
    with pytest.raises(OperationalError):
        read_feed(_write(tmp_path, "array.json", "[1, 2, 3]"))


def test_read_feed_accepts_a_path_string_and_a_path_object(tmp_path):
    path = _write(tmp_path, "ok.geojson", json.dumps({"type": "FeatureCollection", "features": []}))
    assert read_feed(path) == read_feed(str(path)) == []


def test_read_feed_writes_nothing_to_standard_output(tmp_path, capsys):
    with pytest.raises(OperationalError):
        read_feed(_write(tmp_path, "garbage.json", "nope"))
    assert capsys.readouterr().out == ""

