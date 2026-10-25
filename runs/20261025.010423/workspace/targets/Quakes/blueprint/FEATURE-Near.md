# FEATURE: Near

| Field       | Value |
|-------------|-------|
| Version     | 20261025 V1 |
| Description | The `near` report: events within a haversine great-circle distance of a point, nearest first. |
| Depends On  | FEATURE-MagFilter.md, FEATURE-Formatting.md, FEATURE-Options.md, FEATURE-ExitCodes.md |
| Provides    | quakes near, haversine_km |
| Consumes    | read_feed, extract_events, filter_events, write_csv, format_time, format_mag, format_decimal, parse_args |

## Purpose

`quakes near --lat <deg> --lon <deg> --radius <km> [--min-mag <m>] <file>` lists the events whose distance from a point is at most the radius.

## Trigger

Command line. `--lat`, `--lon`, and `--radius` are all required. `parse_args` enforces `--lat` in -90..90, `--lon` in -180..180, and `--radius` greater than zero; any violation or omission is a usage error (exit 2).

## Sequence

1. `read_feed`, `extract_events`, and `filter_events` produce the kept events.
2. `haversine_km(lat1, lon1, lat2, lon2)` is a pure function on a sphere of radius 6371.0 km, with angles in radians:
   `h = sin^2((lat2 - lat1) / 2) + cos(lat1) * cos(lat2) * sin^2((lon2 - lon1) / 2)` and `d = 2 * 6371.0 * asin(sqrt(h))`. Event coordinates are `[longitude, latitude, depth_km]`.
3. `compute_near(events, lat, lon, radius)` keeps events whose unrounded distance is `<= radius` and orders them by unrounded distance ascending, then by event time ascending.
4. `write_csv` writes the report, with `distance_km` rounded half up to one decimal.

## Output

Header: `distance_km,time,mag,place,id`. One row per matching event: distance with one decimal, UTC time, magnitude with one decimal, place, id. An event at exactly the radius is included. No matches yields only the header with exit 0. Places containing commas are quoted by the `csv` module; non-ASCII places are UTF-8.

## Reads

The saved GeoJSON file named on the command line.

## Writes

Standard output only.

## Programmatic Acceptance

=== AC near-haversine-distance-and-radius ===
Intent: Reported distances match an independent haversine on a 6371.0 km sphere, and only events within the radius are listed, nearest first.
Suite: scoped
Requires: executable=python3; scope=test

import csv
import io
import json
import math
import os
import tempfile

from cli.testing import cli_runner


def hav(lat1, lon1, lat2, lon2):
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = p2 - p1
    dlam = math.radians(lon2 - lon1)
    h = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlam / 2) ** 2
    return 2 * 6371.0 * math.asin(math.sqrt(h))


origin = (27.72, 85.32)
points = [
    ("far", 35.68, 139.69),
    ("mid", 28.60, 87.37),
    ("near1", 28.80, 87.13),
    ("near2", 28.50, 87.35),
]
features = []
for i, (name, lat, lon) in enumerate(points):
    features.append({
        "type": "Feature",
        "properties": {"mag": 5.0 + i / 10, "place": "Place " + name, "time": 1736200000000 + i * 1000, "tsunami": 0},
        "geometry": {"type": "Point", "coordinates": [lon, lat, 10.0]},
        "id": name,
    })
doc = {"type": "FeatureCollection", "features": features}
dist = {name: hav(origin[0], origin[1], lat, lon) for name, lat, lon in points}
radius = round(sorted(dist.values())[2] + 1.0, 1)
inside = sorted([n for n in dist if dist[n] <= radius], key=lambda n: dist[n])
assert 0 < len(inside) < len(points)
with tempfile.TemporaryDirectory() as tmp:
    path = os.path.join(tmp, "q.geojson")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(doc, fh)
    code, out, err = cli_runner(
        "near", "--lat", str(origin[0]), "--lon", str(origin[1]), "--radius", str(radius), path
    )
print(out)
print(err)
assert code == 0
rows = list(csv.reader(io.StringIO(out)))
assert rows[0] == ["distance_km", "time", "mag", "place", "id"]
assert [r[4] for r in rows[1:]] == inside
for r in rows[1:]:
    assert abs(float(r[0]) - dist[r[4]]) <= 0.051
=== END AC near-haversine-distance-and-radius ===

=== AC near-ordering-ties-and-quoting ===
Intent: Events at equal distance are ordered by time ascending, and a place containing a comma round-trips through CSV quoting.
Suite: scoped
Requires: executable=python3; scope=test

import csv
import io
import json
import os
import tempfile

from cli.testing import cli_runner

place = "10 km N of Somewhere, Country"
times = [1736200003000, 1736200001000, 1736200002000]
features = []
for i, t in enumerate(times):
    features.append({
        "type": "Feature",
        "properties": {"mag": 5.0, "place": place, "time": t, "tsunami": 0},
        "geometry": {"type": "Point", "coordinates": [10.0, 10.0, 5.0]},
        "id": "t" + str(i),
    })
doc = {"type": "FeatureCollection", "features": features}
expected_ids = ["t" + str(i) for i in sorted(range(len(times)), key=lambda i: times[i])]
with tempfile.TemporaryDirectory() as tmp:
    path = os.path.join(tmp, "q.geojson")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(doc, fh)
    code, out, err = cli_runner("near", "--lat", "10", "--lon", "10.5", "--radius", "500", path)
print(out)
assert code == 0
rows = list(csv.reader(io.StringIO(out)))
assert [r[4] for r in rows[1:]] == expected_ids
assert all(r[3] == place for r in rows[1:])
=== END AC near-ordering-ties-and-quoting ===

=== AC near-min-mag-null-mag-and-empty ===
Intent: --min-mag filters near results, null magnitudes never appear, and no match yields only the header with exit 0.
Suite: scoped
Requires: executable=python3; scope=test

import csv
import io
import json
import os
import tempfile

from cli.testing import cli_runner

threshold = 5.3
mags = [5.0, 5.3, 6.0, None]
features = []
for i, mag in enumerate(mags):
    features.append({
        "type": "Feature",
        "properties": {"mag": mag, "place": "P" + str(i), "time": 1736200000000 + i, "tsunami": 0},
        "geometry": {"type": "Point", "coordinates": [20.0, 20.0, 5.0]},
        "id": "m" + str(i),
    })
doc = {"type": "FeatureCollection", "features": features}
kept = ["m" + str(i) for i, m in enumerate(mags) if m is not None and m >= threshold]
with tempfile.TemporaryDirectory() as tmp:
    path = os.path.join(tmp, "q.geojson")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(doc, fh)
    code, out, err = cli_runner(
        "near", "--lat", "20", "--lon", "20", "--radius", "50", "--min-mag", str(threshold), path
    )
    code_e, out_e, err_e = cli_runner("near", "--lat", "0", "--lon", "0", "--radius", "100", path)
print(out)
assert code == 0 and code_e == 0
rows = list(csv.reader(io.StringIO(out)))
assert sorted(r[4] for r in rows[1:]) == sorted(kept)
assert list(csv.reader(io.StringIO(out_e))) == [["distance_km", "time", "mag", "place", "id"]]
=== END AC near-min-mag-null-mag-and-empty ===

=== AC near-usage-errors ===
Intent: Missing required options and out-of-range values exit 2 with empty standard output.
Suite: scoped
Requires: executable=python3; scope=test

import json
import os
import tempfile

from cli.testing import cli_runner

doc = {"type": "FeatureCollection", "features": []}
with tempfile.TemporaryDirectory() as tmp:
    path = os.path.join(tmp, "q.geojson")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(doc, fh)
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
        code, out, err = cli_runner(*args)
        assert code == 2, args
        assert out == "", args
=== END AC near-usage-errors ===

=== AC near-unreadable-file ===
Intent: An unreadable file is an operational failure: exit 1 with empty standard output.
Suite: scoped
Requires: executable=python3; scope=test

import os
import tempfile

from cli.testing import cli_runner

with tempfile.TemporaryDirectory() as tmp:
    missing = os.path.join(tmp, "absent.geojson")
    code, out, err = cli_runner("near", "--lat", "1", "--lon", "1", "--radius", "5", missing)
assert code == 1
assert out == ""
=== END AC near-unreadable-file ===

## User Acceptance

- None.

## Guardrails

- The earth radius is exactly 6371.0 km; no other radius or formula is used.
- The radius test compares the unrounded distance; only the printed value is rounded.
- An event at exactly the radius is included (`<=`).
- No distance or row is hardcoded; all values are computed from the file and the arguments.
