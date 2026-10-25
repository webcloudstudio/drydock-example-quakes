"""Event-extraction story: features become Event records; null-magnitude features are dropped."""

import dataclasses

import pytest

from cli.errors import OperationalError
from cli.feed import Event, extract_events


def _feature(ident, mag, place="P", time=1735706358000, tsunami=0):
    return {
        "type": "Feature",
        "id": ident,
        "properties": {"mag": mag, "place": place, "time": time, "tsunami": tsunami},
        "geometry": {"type": "Point", "coordinates": [1.0, 2.0, 3.0]},
    }


# ── Declared acceptance assertions ──────────────────────────────────────────────────────


def test_extract_fields():
    feature = {
        "type": "Feature",
        "id": "ev1",
        "properties": {"mag": 5.4, "place": "10 km N of Town, Land", "time": 1735706358208,
                       "tsunami": 1, "ignored": {"deep": [1, 2, 3]}},
        "geometry": {"type": "Point", "coordinates": [169.5, -20.25, 22]},
    }
    events = extract_events([feature])
    assert len(events) == 1
    event = events[0]
    assert event.id == feature["id"]
    assert event.mag == feature["properties"]["mag"]
    assert event.place == feature["properties"]["place"]
    assert event.time_ms == feature["properties"]["time"]
    assert event.tsunami == feature["properties"]["tsunami"]
    lon, lat, depth = feature["geometry"]["coordinates"]
    assert event.lon == lon
    assert event.lat == lat
    assert event.depth_km == depth


def test_extract_null_mag_excluded():
    features = [_feature("a", 5.0), _feature("b", None), _feature("c", 0), _feature("d", 6.1), _feature("e", None)]
    events = extract_events(features)
    kept_ids = [f["id"] for f in features if f["properties"]["mag"] is not None]
    assert [e.id for e in events] == kept_ids
    assert len(events) == len(kept_ids)


def test_extract_null_place_and_empty():
    assert extract_events([]) == []
    events = extract_events([_feature("np", 5.1, place=None)])
    assert len(events) == 1
    assert events[0].place is None


# ── Finer coverage: absent optional fields, field selection, and malformed input ────────


def test_missing_tsunami_is_read_as_zero():
    feature = _feature("x", 5.0)
    del feature["properties"]["tsunami"]
    assert extract_events([feature])[0].tsunami == 0


def test_null_tsunami_is_read_as_zero():
    assert extract_events([_feature("x", 5.0, tsunami=None)])[0].tsunami == 0


def test_magnitude_zero_is_kept():
    events = extract_events([_feature("zero", 0)])
    assert [e.id for e in events] == ["zero"]
    assert events[0].mag == 0.0


def test_depth_is_the_third_coordinate_and_extra_coordinates_are_ignored():
    feature = _feature("d", 5.0)
    feature["geometry"]["coordinates"] = [10.5, -7.25, 33.0, 999.0]
    event = extract_events([feature])[0]
    assert (event.lon, event.lat, event.depth_km) == (10.5, -7.25, 33.0)


def test_event_fields_are_typed_as_declared():
    event = extract_events([_feature("t", 5, tsunami=1, time=1735706358000)])[0]
    assert isinstance(event.mag, float)
    assert isinstance(event.time_ms, int)
    assert isinstance(event.tsunami, int)
    assert isinstance(event.lon, float)
    assert isinstance(event.depth_km, float)


def test_event_is_immutable():
    event = extract_events([_feature("i", 5.0)])[0]
    assert isinstance(event, Event)
    with pytest.raises(dataclasses.FrozenInstanceError):
        event.mag = 9.0


def test_feed_order_is_preserved_for_many_features():
    features = [_feature(f"e{i}", 5.0 + i / 10) for i in range(25)]
    assert [e.id for e in extract_events(features)] == [f"e{i}" for i in range(25)]


def test_all_null_magnitudes_yield_no_events():
    assert extract_events([_feature("a", None), _feature("b", None)]) == []


def test_extraction_does_not_mutate_the_features():
    features = [_feature("m", 5.0)]
    snapshot = [dict(f, properties=dict(f["properties"])) for f in features]
    extract_events(features)
    assert features == snapshot


@pytest.mark.parametrize(
    "broken",
    [
        "not-a-feature",
        {"type": "Feature", "id": "x"},
        {"type": "Feature", "id": "x", "properties": {"mag": 5.0, "time": 1}, "geometry": None},
        {"type": "Feature", "properties": {"mag": 5.0, "time": 1}, "geometry": {"coordinates": [1, 2, 3]}},
        {"type": "Feature", "id": "x", "properties": {"mag": 5.0, "time": None},
         "geometry": {"coordinates": [1, 2, 3]}},
        {"type": "Feature", "id": "x", "properties": {"mag": 5.0, "time": 1},
         "geometry": {"coordinates": [1, 2]}},
    ],
)
def test_malformed_feature_is_an_operational_failure(broken):
    with pytest.raises(OperationalError):
        extract_events([broken])
