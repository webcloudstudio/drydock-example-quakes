# FEATURE: Top

| Field       | Value |
|-------------|-------|
| Version     | 20261024 V1 |
| Description | The top report: the largest events by magnitude, limited by --n. |
| Depends On  | FEATURE-MinMagFilter.md, FEATURE-ExitCodes.md |
| Provides    | quakes top |
| Consumes    | filter_min_mag(events, m), format_time |

## Purpose

`quakes top [--min-mag <m>] [--n <count>] <file>` writes the header `time,mag,depth_km,place,id` and the
`--n` largest events ordered by `mag` descending, then time ascending. `--n` is a positive integer
defaulting to `10`; `0`, a negative number or a non-integer is a usage error (exit 2). Magnitude and
depth have one decimal (depth rounded half up). Rows are written with the `csv` module, so a place
containing a comma is quoted, and as UTF-8.

## Programmatic Acceptance

=== AC top-ordering ===
Intent: Events are ordered by magnitude descending and then by time ascending.

import csv
import io
import json
import os
import tempfile

from cli.testing import cli_runner

mags = [5.5, 6.1, 5.5, 6.1, 5.0]
times = [1735700300000, 1735700200000, 1735700100000, 1735700000000, 1735700400000]
feats = [
    {"type": "Feature",
     "properties": {"mag": mags[i], "place": "Place " + str(i), "time": times[i], "tsunami": 0},
     "geometry": {"type": "Point", "coordinates": [0.0, 0.0, 10]},
     "id": "ev" + str(i)}
    for i in range(len(mags))
]
with tempfile.TemporaryDirectory() as d:
    path = os.path.join(d, "q.geojson")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump({"type": "FeatureCollection", "features": feats}, fh)
    code, out, err = cli_runner("top", path)

print(out)
print(err)
assert code == 0
rows = list(csv.reader(io.StringIO(out)))
assert rows[0] == ["time", "mag", "depth_km", "place", "id"]
order = sorted(range(len(mags)), key=lambda i: (-mags[i], times[i]))
assert [r[4] for r in rows[1:]] == ["ev" + str(i) for i in order]
assert "\r" not in out
=== END AC top-ordering ===

=== AC top-n-limits-rows ===
Intent: --n limits the number of rows and the default limit is ten.

import csv
import io
import json
import os
import tempfile

from cli.testing import cli_runner

count = 12
feats = [
    {"type": "Feature",
     "properties": {"mag": 5.0 + i / 10, "place": "Place " + str(i), "time": 1735700000000 + i * 1000, "tsunami": 0},
     "geometry": {"type": "Point", "coordinates": [0.0, 0.0, 10]},
     "id": "ev" + str(i)}
    for i in range(count)
]
with tempfile.TemporaryDirectory() as d:
    path = os.path.join(d, "q.geojson")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump({"type": "FeatureCollection", "features": feats}, fh)
    default_code, default_out, _ = cli_runner("top", path)
    n = 3
    limited_code, limited_out, _ = cli_runner("top", "--n", str(n), path)
    big_code, big_out, _ = cli_runner("top", "--n", "100", path)

assert default_code == 0 and limited_code == 0 and big_code == 0
default_rows = list(csv.reader(io.StringIO(default_out)))
limited_rows = list(csv.reader(io.StringIO(limited_out)))
big_rows = list(csv.reader(io.StringIO(big_out)))
assert len(default_rows) - 1 == min(10, count)
assert len(limited_rows) - 1 == n
assert len(big_rows) - 1 == count
assert limited_rows[1:] == default_rows[1:1 + n]
=== END AC top-n-limits-rows ===

=== AC top-n-usage-errors ===
Intent: A zero, negative or non-integer --n is a usage error with exit 2 and nothing on standard output.

import json
import os
import tempfile

from cli.testing import cli_runner

with tempfile.TemporaryDirectory() as d:
    path = os.path.join(d, "q.geojson")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump({"type": "FeatureCollection", "features": []}, fh)
    for bad in ("0", "-1", "abc", "2.5"):
        code, out, err = cli_runner("top", "--n", bad, path)
        assert code == 2, bad
        assert out == "", bad
=== END AC top-n-usage-errors ===

=== AC top-columns-formatted ===
Intent: Each row carries the UTC time, one-decimal magnitude, half-up one-decimal depth, place and id.

import csv
import io
import json
import os
import tempfile
from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_UP

from cli.testing import cli_runner

ms = 1736211916734
mag = 7
depth = 10.25
place = "Plain place"
feats = [
    {"type": "Feature",
     "properties": {"mag": mag, "place": place, "time": ms, "tsunami": 0},
     "geometry": {"type": "Point", "coordinates": [87.0, 28.0, depth]},
     "id": "us-test-1"}
]
with tempfile.TemporaryDirectory() as d:
    path = os.path.join(d, "q.geojson")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump({"type": "FeatureCollection", "features": feats}, fh)
    code, out, err = cli_runner("top", path)

assert code == 0
rows = list(csv.reader(io.StringIO(out)))
expected_time = datetime.fromtimestamp(ms // 1000, timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
expected_depth = str(Decimal(str(depth)).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP))
assert rows[1] == [expected_time, f"{float(mag):.1f}", expected_depth, place, "us-test-1"]
=== END AC top-columns-formatted ===

=== AC top-place-with-comma-roundtrips ===
Intent: A place containing a comma is quoted so the CSV parses back to the original place, including non-ASCII text written as UTF-8.
Encoding: utf-8

import csv
import io
import json
import os
import tempfile

from cli.testing import cli_runner

place = "13 km NW of \u0100wash, Ethiopia"
feats = [
    {"type": "Feature",
     "properties": {"mag": 5.0, "place": place, "time": 1735718987701, "tsunami": 0},
     "geometry": {"type": "Point", "coordinates": [40.0, 9.0, 10]},
     "id": "ev-comma"}
]
with tempfile.TemporaryDirectory() as d:
    path = os.path.join(d, "q.geojson")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump({"type": "FeatureCollection", "features": feats}, fh, ensure_ascii=False)
    code, out, err = cli_runner("top", path)

assert code == 0
rows = list(csv.reader(io.StringIO(out)))
assert len(rows) == 2
assert len(rows[1]) == 5
assert rows[1][3] == place
=== END AC top-place-with-comma-roundtrips ===

=== AC top-min-mag-option ===
Intent: top honours --min-mag and --n together, listing the largest events at or above the threshold.

import csv
import io
import json
import os
import tempfile

from cli.testing import cli_runner

mags = [5.0, 5.2, 5.4, 5.6, 5.8, 6.0]
threshold = 5.2
n = 2
feats = [
    {"type": "Feature",
     "properties": {"mag": mags[i], "place": "Place " + str(i), "time": 1735700000000 + i * 1000, "tsunami": 0},
     "geometry": {"type": "Point", "coordinates": [0.0, 0.0, 10]},
     "id": "ev" + str(i)}
    for i in range(len(mags))
]
with tempfile.TemporaryDirectory() as d:
    path = os.path.join(d, "q.geojson")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump({"type": "FeatureCollection", "features": feats}, fh)
    code, out, err = cli_runner("top", "--min-mag", str(threshold), "--n", str(n), path)

assert code == 0
rows = list(csv.reader(io.StringIO(out)))
kept = [i for i in range(len(mags)) if mags[i] >= threshold]
order = sorted(kept, key=lambda i: (-mags[i], i))[:n]
assert [r[4] for r in rows[1:]] == ["ev" + str(i) for i in order]
=== END AC top-min-mag-option ===

=== AC top-no-events ===
Intent: When no event matches, top exits 0 and writes only the header.

import csv
import io
import json
import os
import tempfile

from cli.testing import cli_runner

with tempfile.TemporaryDirectory() as d:
    path = os.path.join(d, "q.geojson")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump({"type": "FeatureCollection", "features": []}, fh)
    code, out, err = cli_runner("top", path)

assert code == 0
rows = list(csv.reader(io.StringIO(out)))
assert len(rows) == 1
assert rows[0] == ["time", "mag", "depth_km", "place", "id"]
=== END AC top-no-events ===

## User Acceptance

- None.

## Guardrails

- No row, count or place is hardcoded; every value comes from the file read.
- Output is written with the `csv` module and `\n` line endings.
- A failing command writes nothing to standard output.
