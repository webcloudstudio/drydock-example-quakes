# FEATURE: Event Extraction

| Field       | Value |
|-------------|-------|
| Version     | 20261025 V1 |
| Description | Turn GeoJSON features into event records and drop events with a null magnitude. |
| Depends On  | FEATURE-FeedValidation.md |
| Provides    | extract_events, Event |
| Consumes    | read_feed |

## Purpose

Reports operate on `Event` records, not raw features. Extraction reads only the fields the reports
need and excludes every feature whose magnitude is `null`.

## Interface

- Module: `cli.feed`. Function: `extract_events(features) -> list[Event]`, preserving feed order.
- `Event` is an immutable dataclass with fields:
  - `id` (str), `mag` (float), `place` (str or `None`),
  - `time_ms` (int, milliseconds since the Unix epoch), `tsunami` (int),
  - `lon` (float), `lat` (float), `depth_km` (float).
- Source fields: `id`, `properties.mag`, `properties.place`, `properties.time`,
  `properties.tsunami`, and `geometry.coordinates` as `[longitude, latitude, depth_km]`.
  Every other field is ignored.
- A feature whose `properties.mag` is `null` is dropped. A magnitude of `0` is kept.
- A `null` place stays `None`; the regions report maps it to `Unknown`.
- A missing `tsunami` is read as `0`.

## Programmatic Acceptance

=== AC extract-fields ===
Intent: Every needed field is read from the feature into the matching Event attribute.
Requires: executable=python3; scope=test

from cli.feed import extract_events

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
=== END AC extract-fields ===

=== AC extract-null-mag-excluded ===
Intent: Features with a null magnitude are absent from the result and the rest keep feed order.
Requires: executable=python3; scope=test

from cli.feed import extract_events


def feature(ident, mag):
    return {"type": "Feature", "id": ident,
            "properties": {"mag": mag, "place": "P", "time": 1735706358000, "tsunami": 0},
            "geometry": {"type": "Point", "coordinates": [1.0, 2.0, 3.0]}}


features = [feature("a", 5.0), feature("b", None), feature("c", 0), feature("d", 6.1), feature("e", None)]
events = extract_events(features)
kept_ids = [f["id"] for f in features if f["properties"]["mag"] is not None]
assert [e.id for e in events] == kept_ids
assert len(events) == len(kept_ids)
=== END AC extract-null-mag-excluded ===

=== AC extract-null-place-and-empty ===
Intent: A null place is preserved as None and an empty feature list yields no events.
Requires: executable=python3; scope=test

from cli.feed import extract_events

assert extract_events([]) == []

feature = {"type": "Feature", "id": "np",
           "properties": {"mag": 5.1, "place": None, "time": 1735706358000, "tsunami": 0},
           "geometry": {"type": "Point", "coordinates": [1.0, 2.0, 3.0]}}
events = extract_events([feature])
assert len(events) == 1
assert events[0].place is None
=== END AC extract-null-place-and-empty ===

## User Acceptance

- None.

## Guardrails

- Fields other than those listed are never read into an `Event`.
- No event value is hardcoded; every value comes from the feature given.
- Standard library only.
