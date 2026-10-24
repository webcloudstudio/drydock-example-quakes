# FEATURE: Feed Reader

| Field       | Value |
|-------------|-------|
| Version     | 20261024 V1 |
| Description | Read a saved USGS GeoJSON FeatureCollection file into a list of events. |
| Depends On  | ARCHITECTURE.md |
| Provides    | read_events(path), cli.reader.Event |
| Consumes    | cli.errors.OperationalFailure |

## Purpose

`read_events` is the only function that reads a feed file. It turns the file into events, ignores
every field it does not need, and excludes events with no magnitude. Normalisation (time, region),
filtering and formatting are other functions.

## Interface

`cli.reader.Event` is a frozen dataclass:

| Field | Type | Source |
|---|---|---|
| `id` | `str` | feature `id` |
| `mag` | `decimal.Decimal` | `Decimal(str(properties.mag))` |
| `place` | `str \| None` | `properties.place`, unchanged (`None` stays `None`) |
| `time_ms` | `int` | `properties.time`, milliseconds since the Unix epoch |
| `tsunami` | `int` | `properties.tsunami` (`1` or `0`) |
| `lon` | `float` | `geometry.coordinates[0]` |
| `lat` | `float` | `geometry.coordinates[1]` |
| `depth_km` | `float` | `geometry.coordinates[2]` |

`cli.reader.read_events(path: str | os.PathLike) -> list[Event]` returns events in file order.

## Rules

1. The file is read as UTF-8. A file that cannot be read, is not valid UTF-8, or is not JSON raises
   `cli.errors.OperationalFailure`.
2. The top level must be an object with `"type": "FeatureCollection"` and a `features` array;
   otherwise `OperationalFailure`.
3. Every other field of a feature is ignored.
4. A feature whose `properties.mag` is `null` is excluded.
5. A feature that lacks a field the reader needs (other than a null `mag`, and a null `place` which is
   kept as `None`) raises `OperationalFailure` rather than being skipped (decision Q-004).
6. An empty `features` array yields an empty list.

## Programmatic Acceptance

=== AC reader-fields ===
Intent: read_events returns one Event per feature with the mapped fields, in file order, excluding null-magnitude features.
Requires: executable=python3; scope=test

import json
import os
import sys
import tempfile
from decimal import Decimal

sys.path.insert(0, os.getcwd())

from cli.reader import Event, read_events

def feature(fid, mag, place, ms, tsunami, lon, lat, depth):
    return {
        "type": "Feature",
        "properties": {"mag": mag, "place": place, "time": ms, "tsunami": tsunami,
                       "updated": 1, "status": "reviewed", "sig": 400},
        "geometry": {"type": "Point", "coordinates": [lon, lat, depth]},
        "id": fid,
    }

features = [
    feature("ev-a", 5.1, "12 km N of Alpha, Beta", 1735706358208, 0, 169.3819, -20.9273, 22),
    feature("ev-null", None, "ignored", 1735706358209, 0, 1.0, 2.0, 3),
    feature("ev-b", 7, None, 1736211916734, 1, 87.3781, 28.6036, 10.5),
]
doc = {"type": "FeatureCollection", "metadata": {"count": 3}, "features": features}
with tempfile.TemporaryDirectory() as tmp:
    path = os.path.join(tmp, "feed.geojson")
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(doc, handle)
    events = read_events(path)

expected = [f for f in features if f["properties"]["mag"] is not None]
assert len(events) == len(expected)
for event, src in zip(events, expected):
    assert isinstance(event, Event)
    props = src["properties"]
    lon, lat, depth = src["geometry"]["coordinates"]
    assert event.id == src["id"]
    assert event.mag == Decimal(str(props["mag"]))
    assert event.place == props["place"]
    assert event.time_ms == props["time"]
    assert event.tsunami == props["tsunami"]
    assert event.lon == lon
    assert event.lat == lat
    assert event.depth_km == depth
=== END AC reader-fields ===

=== AC reader-empty-collection ===
Intent: A FeatureCollection with an empty features array yields no events.
Requires: executable=python3; scope=test

import json
import os
import sys
import tempfile

sys.path.insert(0, os.getcwd())

from cli.reader import read_events

doc = {"type": "FeatureCollection", "features": []}
with tempfile.TemporaryDirectory() as tmp:
    path = os.path.join(tmp, "empty.geojson")
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(doc, handle)
    assert read_events(path) == []
=== END AC reader-empty-collection ===

=== AC reader-only-null-mag ===
Intent: A collection whose only feature has a null magnitude yields no events.
Requires: executable=python3; scope=test

import json
import os
import sys
import tempfile

sys.path.insert(0, os.getcwd())

from cli.reader import read_events

feature = {
    "type": "Feature",
    "properties": {"mag": None, "place": "somewhere", "time": 1000, "tsunami": 0},
    "geometry": {"type": "Point", "coordinates": [1.0, 2.0, 3.0]},
    "id": "only-null",
}
doc = {"type": "FeatureCollection", "features": [feature]}
with tempfile.TemporaryDirectory() as tmp:
    path = os.path.join(tmp, "null.geojson")
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(doc, handle)
    assert read_events(path) == []
=== END AC reader-only-null-mag ===

=== AC reader-operational-failures ===
Intent: Unreadable, non-JSON, non-UTF-8, non-FeatureCollection, and malformed-feature files raise OperationalFailure.
Requires: executable=python3; scope=test

import json
import os
import sys
import tempfile

sys.path.insert(0, os.getcwd())

from cli.errors import OperationalFailure
from cli.reader import read_events

good_feature = {
    "type": "Feature",
    "properties": {"mag": 5.0, "place": "p", "time": 1000, "tsunami": 0},
    "geometry": {"type": "Point", "coordinates": [1.0, 2.0, 3.0]},
    "id": "ok",
}
no_geometry = {
    "type": "Feature",
    "properties": {"mag": 5.0, "place": "p", "time": 1000, "tsunami": 0},
    "id": "broken",
}
payloads = {
    "not-json": b"this is not json\n",
    "not-utf8": b"\xff\xfe\xfa\xfb",
    "single-feature": json.dumps({"type": "Feature", "properties": {}, "geometry": None}).encode("utf-8"),
    "no-features": json.dumps({"type": "FeatureCollection"}).encode("utf-8"),
    "features-not-list": json.dumps({"type": "FeatureCollection", "features": {}}).encode("utf-8"),
    "json-list": json.dumps([good_feature]).encode("utf-8"),
    "missing-geometry": json.dumps({"type": "FeatureCollection", "features": [good_feature, no_geometry]}).encode("utf-8"),
}
survivors = []
with tempfile.TemporaryDirectory() as tmp:
    for name, payload in payloads.items():
        path = os.path.join(tmp, name + ".json")
        with open(path, "wb") as handle:
            handle.write(payload)
        try:
            read_events(path)
        except OperationalFailure:
            continue
        survivors.append(name)
    try:
        read_events(os.path.join(tmp, "no-such-file.geojson"))
    except OperationalFailure:
        pass
    else:
        survivors.append("no-such-file")
print(survivors)
assert survivors == []
=== END AC reader-operational-failures ===

=== AC reader-utf8-place ===
Intent: Non-ASCII place text is read as UTF-8 and returned unchanged.
Encoding: utf-8
Requires: executable=python3; scope=test

import json
import os
import sys
import tempfile

sys.path.insert(0, os.getcwd())

from cli.reader import read_events

place = "13 km NW of \u0100wash, Ethiopia"
feature = {
    "type": "Feature",
    "properties": {"mag": 5, "place": place, "time": 1735718987701, "tsunami": 0},
    "geometry": {"type": "Point", "coordinates": [40.0976, 9.0855, 10]},
    "id": "utf8-event",
}
doc = {"type": "FeatureCollection", "features": [feature]}
with tempfile.TemporaryDirectory() as tmp:
    path = os.path.join(tmp, "utf8.geojson")
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(doc, handle, ensure_ascii=False)
    events = read_events(path)
assert len(events) == 1
assert events[0].place == place
=== END AC reader-utf8-place ===

## User Acceptance

- None.

## Guardrails

- The reader never reads `sources/run.sh` or the snapshot and embeds no event data.
- Every field other than `id`, `mag`, `place`, `time`, `tsunami` and `geometry.coordinates` is ignored.
- A failure to read the file never produces partial events.
