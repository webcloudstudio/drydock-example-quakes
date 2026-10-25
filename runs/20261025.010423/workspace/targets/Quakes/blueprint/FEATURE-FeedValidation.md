# FEATURE: Feed Validation

| Field       | Value |
|-------------|-------|
| Version     | 20261025 V1 |
| Description | Read a saved GeoJSON file and confirm it is a USGS FeatureCollection. |
| Depends On  | ARCHITECTURE.md, FEATURE-ExitCodes.md |
| Provides    | read_feed |
| Consumes    | OperationalError |

## Purpose

Every report command starts by reading a saved feed file. `read_feed` returns the raw `features` list
and rejects anything that is not a GeoJSON FeatureCollection as an operational failure (exit 1).

## Interface

- Module: `cli.feed`. Function: `read_feed(path) -> list`.
- `path` is a `str` or `pathlib.Path`. The file is read as UTF-8 and parsed with `json`.
- Returns the value of the `features` array unchanged (a `list` of feature objects).
- Raises `OperationalError` when:
  - the file cannot be read (missing, directory, permissions, undecodable bytes),
  - the content is not valid JSON,
  - the JSON value is not an object,
  - `"type"` is not the string `FeatureCollection`,
  - `features` is missing or not an array.
- An empty `features` array is valid and returns `[]`.
- The function writes nothing to standard output. The diagnostic line is produced by `main`.

## Programmatic Acceptance

=== AC feed-valid-collection ===
Intent: A FeatureCollection file returns its features list, including an empty one.
Requires: executable=python3; scope=test

import json
import tempfile
from pathlib import Path

from cli.feed import read_feed

with tempfile.TemporaryDirectory() as tmp:
    features = [{"type": "Feature", "id": "a", "properties": {"mag": 5.0}, "geometry": None},
                {"type": "Feature", "id": "b", "properties": {"mag": 6.0}, "geometry": None}]
    full = Path(tmp) / "full.geojson"
    full.write_text(json.dumps({"type": "FeatureCollection", "features": features}), encoding="utf-8")
    assert read_feed(full) == features
    assert read_feed(str(full)) == features

    empty = Path(tmp) / "empty.geojson"
    empty.write_text(json.dumps({"type": "FeatureCollection", "features": []}), encoding="utf-8")
    assert read_feed(empty) == []
=== END AC feed-valid-collection ===

=== AC feed-unreadable-file ===
Intent: A missing file and a directory both raise OperationalError.
Requires: executable=python3; scope=test

import tempfile
from pathlib import Path

from cli.feed import read_feed

with tempfile.TemporaryDirectory() as tmp:
    for target in (Path(tmp) / "no-such-file.geojson", Path(tmp)):
        raised = None
        try:
            read_feed(target)
        except Exception as exc:
            raised = exc
        assert raised is not None
        assert type(raised).__name__ == "OperationalError"
=== END AC feed-unreadable-file ===

=== AC feed-not-json ===
Intent: Content that is not JSON raises OperationalError.
Requires: executable=python3; scope=test

import tempfile
from pathlib import Path

from cli.feed import read_feed

with tempfile.TemporaryDirectory() as tmp:
    garbage = Path(tmp) / "garbage.json"
    garbage.write_text("this is not json\n", encoding="utf-8")
    raised = None
    try:
        read_feed(garbage)
    except Exception as exc:
        raised = exc
    assert raised is not None
    assert type(raised).__name__ == "OperationalError"
=== END AC feed-not-json ===

=== AC feed-wrong-shape ===
Intent: JSON that is not a FeatureCollection object with a features array raises OperationalError.
Requires: executable=python3; scope=test

import json
import tempfile
from pathlib import Path

from cli.feed import read_feed

bad_values = [
    {"type": "Feature", "properties": {}, "geometry": None},
    {"type": "FeatureCollection"},
    {"type": "FeatureCollection", "features": {"a": 1}},
    {"type": "FeatureCollection", "features": None},
    {"features": []},
    [],
    "FeatureCollection",
    None,
]
with tempfile.TemporaryDirectory() as tmp:
    for n, value in enumerate(bad_values):
        path = Path(tmp) / f"bad{n}.json"
        path.write_text(json.dumps(value), encoding="utf-8")
        raised = None
        try:
            read_feed(path)
        except Exception as exc:
            raised = exc
        assert raised is not None, value
        assert type(raised).__name__ == "OperationalError", value
=== END AC feed-wrong-shape ===

## User Acceptance

- None.

## Guardrails

- Application code never reads `sources/run.sh` or the frozen snapshot.
- `read_feed` never writes to standard output; failures surface only through `OperationalError`.
- Standard library only.
