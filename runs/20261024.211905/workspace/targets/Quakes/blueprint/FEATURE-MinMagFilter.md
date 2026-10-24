# FEATURE: Min Magnitude Filter

| Field       | Value |
|-------------|-------|
| Version     | 20261024 V1 |
| Description | Keep only events with magnitude at least the --min-mag value, for every report. |
| Depends On  | FEATURE-EventNormalise.md, FEATURE-CliDispatch.md |
| Provides    | filter_min_mag(events, m), --min-mag option |
| Consumes    | read_events(path) |

## Purpose

`filter_min_mag(events, m)` is a pure function over the event list the reader returns. It keeps
events with `mag >= m`, preserving order. It sits in the common pipeline (read, filter, compute,
format) shared by every report command, so `--min-mag` means the same thing in all of them. When
`--min-mag` is absent no filtering beyond the reader's null-magnitude exclusion happens. A
`--min-mag` value that does not match `-?[0-9]+(\.[0-9]+)?` is a usage error (exit 2).

## Programmatic Acceptance

=== AC minmag-keeps-at-least ===
Intent: filter_min_mag keeps events whose magnitude is greater than or equal to the threshold, boundary included.

import importlib
import json
import os
import pkgutil
import tempfile
from pathlib import Path

import cli


def find(name):
    mods = [cli]
    for info in pkgutil.walk_packages(cli.__path__, "cli."):
        try:
            mods.append(importlib.import_module(info.name))
        except Exception:
            pass
    for mod in mods:
        if hasattr(mod, name):
            return getattr(mod, name)
    raise AssertionError("no function named " + name + " under the cli package")


read_events = find("read_events")
filter_min_mag = find("filter_min_mag")

mags = [4.9, 5.0, 5.5, 6.1, 5.0]
feats = [
    {"type": "Feature",
     "properties": {"mag": m, "place": "P" + str(i), "time": 1735700000000 + i * 1000, "tsunami": 0},
     "geometry": {"type": "Point", "coordinates": [0.0, 0.0, 10]},
     "id": "ev" + str(i)}
    for i, m in enumerate(mags)
]
with tempfile.TemporaryDirectory() as d:
    path = Path(d) / "q.geojson"
    path.write_text(json.dumps({"type": "FeatureCollection", "features": feats}), encoding="utf-8")
    events = read_events(path)
    assert len(events) == len(mags)
    for threshold in (5.0, 5.5, 6.1):
        kept = filter_min_mag(events, threshold)
        assert len(kept) == sum(1 for m in mags if m >= threshold), threshold
=== END AC minmag-keeps-at-least ===

=== AC minmag-extremes ===
Intent: A threshold below every event keeps all of them and one above every event keeps none.

import importlib
import json
import pkgutil
import tempfile
from pathlib import Path

import cli


def find(name):
    mods = [cli]
    for info in pkgutil.walk_packages(cli.__path__, "cli."):
        try:
            mods.append(importlib.import_module(info.name))
        except Exception:
            pass
    for mod in mods:
        if hasattr(mod, name):
            return getattr(mod, name)
    raise AssertionError("no function named " + name + " under the cli package")


read_events = find("read_events")
filter_min_mag = find("filter_min_mag")

mags = [5.0, 5.3, 7.1]
feats = [
    {"type": "Feature",
     "properties": {"mag": m, "place": "P" + str(i), "time": 1735700000000 + i * 1000, "tsunami": 0},
     "geometry": {"type": "Point", "coordinates": [0.0, 0.0, 10]},
     "id": "ev" + str(i)}
    for i, m in enumerate(mags)
]
with tempfile.TemporaryDirectory() as d:
    path = Path(d) / "q.geojson"
    path.write_text(json.dumps({"type": "FeatureCollection", "features": feats}), encoding="utf-8")
    events = read_events(path)
    assert len(filter_min_mag(events, 0.0)) == len(mags)
    assert len(filter_min_mag(events, 9.0)) == 0
    assert len(filter_min_mag(events, -1.0)) == len(mags)
=== END AC minmag-extremes ===

=== AC minmag-does-not-mutate ===
Intent: filter_min_mag returns a new selection and leaves the input event list unchanged.

import importlib
import json
import pkgutil
import tempfile
from pathlib import Path

import cli


def find(name):
    mods = [cli]
    for info in pkgutil.walk_packages(cli.__path__, "cli."):
        try:
            mods.append(importlib.import_module(info.name))
        except Exception:
            pass
    for mod in mods:
        if hasattr(mod, name):
            return getattr(mod, name)
    raise AssertionError("no function named " + name + " under the cli package")


read_events = find("read_events")
filter_min_mag = find("filter_min_mag")

mags = [5.0, 6.0, 5.5]
feats = [
    {"type": "Feature",
     "properties": {"mag": m, "place": "P" + str(i), "time": 1735700000000 + i * 1000, "tsunami": 0},
     "geometry": {"type": "Point", "coordinates": [0.0, 0.0, 10]},
     "id": "ev" + str(i)}
    for i, m in enumerate(mags)
]
with tempfile.TemporaryDirectory() as d:
    path = Path(d) / "q.geojson"
    path.write_text(json.dumps({"type": "FeatureCollection", "features": feats}), encoding="utf-8")
    events = read_events(path)
    before = len(events)
    kept = filter_min_mag(events, 5.5)
    assert len(events) == before
    assert len(kept) == sum(1 for m in mags if m >= 5.5)
=== END AC minmag-does-not-mutate ===

=== AC minmag-malformed-value-usage-error ===
Intent: A --min-mag value that is not a decimal is a usage error with exit 2 and nothing on standard output.

import json
import os
import tempfile

from cli.testing import cli_runner

with tempfile.TemporaryDirectory() as d:
    path = os.path.join(d, "q.geojson")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump({"type": "FeatureCollection", "features": []}, fh)
    for bad in ("big", "5.", ".5", "1e3"):
        code, out, err = cli_runner("summary", "--min-mag", bad, path)
        assert code == 2, bad
        assert out == "", bad
=== END AC minmag-malformed-value-usage-error ===

## User Acceptance

- None.

## Guardrails

- `--min-mag` applies to every report, never to a subset of them.
- The comparison is `mag >= m`; an event equal to the threshold is kept.
- No default threshold is applied when the option is absent.
