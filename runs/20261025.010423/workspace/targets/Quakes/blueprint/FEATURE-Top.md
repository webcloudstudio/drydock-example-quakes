# FEATURE: Top Report

| Field       | Value |
|-------------|-------|
| Version     | 20261025 V1 |
| Description | The top command lists the largest events by magnitude. |
| Depends On  | FEATURE-MagFilter.md, FEATURE-Formatting.md, FEATURE-Options.md, FEATURE-ExitCodes.md |
| Provides    | quakes top |
| Consumes    | read_feed, extract_events, filter_events, write_csv, parse_args |

## Purpose

`quakes top [--min-mag <m>] [--n <count>] <file>` writes the `--n` largest events as CSV.

## Behavior

- Header: `time,mag,depth_km,place,id`.
- Events are filtered by `--min-mag` first, then sorted by magnitude descending, then time ascending
  (ties beyond that keep feed order), then the first `--n` are written.
- `--n` is a positive integer and defaults to `10`. `--n 0` or a non-integer is a usage error (exit 2).
- `time` is `YYYY-MM-DDTHH:MM:SSZ`; `mag` and `depth_km` have one decimal place.
- A place containing a comma is quoted by the `csv` module.
- Only `--min-mag` and `--n` are accepted. No matching events yields the header alone with exit `0`.

## Programmatic Acceptance

=== AC top-order-and-default-n ===
Intent: Rows are sorted by magnitude descending then time ascending, and the default count is ten.
Requires: executable=python3; scope=test

import csv
import datetime
import io
import json
import tempfile
from pathlib import Path

from cli.testing import cli_runner

BASE = 1735689600000
# (id, mag, minutes offset); two pairs tie on magnitude with different times.
specs = [("a", 5.0, 50), ("b", 6.0, 40), ("c", 6.0, 10), ("d", 5.5, 30), ("e", 5.1, 20),
         ("f", 7.0, 60), ("g", 5.2, 70), ("h", 5.3, 80), ("i", 5.4, 90), ("j", 5.6, 15),
         ("k", 5.7, 25), ("l", 5.8, 35)]
features = [{"type": "Feature", "id": s[0],
             "properties": {"mag": s[1], "place": "P", "time": BASE + s[2] * 60000, "tsunami": 0},
             "geometry": {"type": "Point", "coordinates": [0.0, 0.0, 12.0]}} for s in specs]
with tempfile.TemporaryDirectory() as tmp:
    path = Path(tmp) / "feed.geojson"
    path.write_text(json.dumps({"type": "FeatureCollection", "features": features}), encoding="utf-8")
    code, out, err = cli_runner("top", str(path))
print(out, err)
assert code == 0
rows = list(csv.reader(io.StringIO(out)))
header, body = rows[0], rows[1:]
assert header == ["time", "mag", "depth_km", "place", "id"]
ranked = sorted(specs, key=lambda s: (-s[1], s[2]))
default_n = 10
assert len(specs) > default_n
assert [r[4] for r in body] == [s[0] for s in ranked[:default_n]]
first = dict(zip(header, body[0]))
assert float(first["mag"]) == ranked[0][1]
assert float(first["depth_km"]) == 12.0
parsed = datetime.datetime.fromisoformat(first["time"])
assert int(parsed.timestamp() * 1000) == BASE + ranked[0][2] * 60000
=== END AC top-order-and-default-n ===

=== AC top-n-option ===
Intent: --n limits the number of rows written.
Requires: executable=python3; scope=test

import csv
import io
import json
import tempfile
from pathlib import Path

from cli.testing import cli_runner

specs = [("a", 5.0), ("b", 6.0), ("c", 7.1), ("d", 5.5), ("e", 6.2)]
features = [{"type": "Feature", "id": s[0],
             "properties": {"mag": s[1], "place": "P", "time": 1735689600000 + i * 1000, "tsunami": 0},
             "geometry": {"type": "Point", "coordinates": [0.0, 0.0, 5.0]}} for i, s in enumerate(specs)]
count = 3
with tempfile.TemporaryDirectory() as tmp:
    path = Path(tmp) / "feed.geojson"
    path.write_text(json.dumps({"type": "FeatureCollection", "features": features}), encoding="utf-8")
    code, out, err = cli_runner("top", "--n", str(count), str(path))
print(out, err)
assert code == 0
body = list(csv.reader(io.StringIO(out)))[1:]
assert [r[4] for r in body] == [s[0] for s in sorted(specs, key=lambda s: -s[1])[:count]]
=== END AC top-n-option ===

=== AC top-min-mag-before-cut ===
Intent: --min-mag filters before --n cuts the list.
Requires: executable=python3; scope=test

import csv
import io
import json
import tempfile
from pathlib import Path

from cli.testing import cli_runner

specs = [("a", 5.0), ("b", 5.1), ("c", 5.2), ("d", 6.0), ("e", 7.0)]
features = [{"type": "Feature", "id": s[0],
             "properties": {"mag": s[1], "place": "P", "time": 1735689600000 + i * 1000, "tsunami": 0},
             "geometry": {"type": "Point", "coordinates": [0.0, 0.0, 5.0]}} for i, s in enumerate(specs)]
threshold = 5.1
count = 4
with tempfile.TemporaryDirectory() as tmp:
    path = Path(tmp) / "feed.geojson"
    path.write_text(json.dumps({"type": "FeatureCollection", "features": features}), encoding="utf-8")
    code, out, err = cli_runner("top", "--min-mag", str(threshold), "--n", str(count), str(path))
print(out, err)
assert code == 0
body = list(csv.reader(io.StringIO(out)))[1:]
kept = sorted([s for s in specs if s[1] >= threshold], key=lambda s: -s[1])
assert [r[4] for r in body] == [s[0] for s in kept[:count]]
assert all(float(r[1]) >= threshold for r in body)
=== END AC top-min-mag-before-cut ===

=== AC top-place-with-comma ===
Intent: A place containing a comma round-trips through CSV quoting.
Requires: executable=python3; scope=test

import csv
import io
import json
import tempfile
from pathlib import Path

from cli.testing import cli_runner

place = "56 km SSE of Some Town, Some Country"
features = [{"type": "Feature", "id": "c1",
             "properties": {"mag": 6.2, "place": place, "time": 1735689600000, "tsunami": 0},
             "geometry": {"type": "Point", "coordinates": [0.0, 0.0, 46.0]}}]
with tempfile.TemporaryDirectory() as tmp:
    path = Path(tmp) / "feed.geojson"
    path.write_text(json.dumps({"type": "FeatureCollection", "features": features}), encoding="utf-8")
    code, out, err = cli_runner("top", str(path))
print(out, err)
assert code == 0
body = list(csv.reader(io.StringIO(out)))[1:]
assert len(body) == 1
assert body[0][3] == place
assert body[0][4] == "c1"
=== END AC top-place-with-comma ===

=== AC top-empty-result ===
Intent: When no event matches, only the header is written and the exit status is 0.
Requires: executable=python3; scope=test

import csv
import io
import json
import tempfile
from pathlib import Path

from cli.testing import cli_runner

features = [{"type": "Feature", "id": "e0",
             "properties": {"mag": 5.0, "place": "P", "time": 1735689600000, "tsunami": 0},
             "geometry": {"type": "Point", "coordinates": [0.0, 0.0, 1.0]}}]
with tempfile.TemporaryDirectory() as tmp:
    path = Path(tmp) / "feed.geojson"
    path.write_text(json.dumps({"type": "FeatureCollection", "features": features}), encoding="utf-8")
    code, out, err = cli_runner("top", "--min-mag", "9", str(path))
print(out, err)
assert code == 0
rows = list(csv.reader(io.StringIO(out)))
assert rows == [["time", "mag", "depth_km", "place", "id"]]
=== END AC top-empty-result ===

=== AC top-usage-errors ===
Intent: A non-positive or malformed --n, an unlisted option, and a missing file all exit 2 with empty stdout.
Requires: executable=python3; scope=test

import json
import tempfile
from pathlib import Path

from cli.testing import cli_runner

features = [{"type": "Feature", "id": "e0",
             "properties": {"mag": 5.0, "place": "P", "time": 1735689600000, "tsunami": 0},
             "geometry": {"type": "Point", "coordinates": [0.0, 0.0, 1.0]}}]
with tempfile.TemporaryDirectory() as tmp:
    path = Path(tmp) / "feed.geojson"
    path.write_text(json.dumps({"type": "FeatureCollection", "features": features}), encoding="utf-8")
    for args in (("top", "--n", "0", str(path)),
                 ("top", "--n", "-2", str(path)),
                 ("top", "--n", "many", str(path)),
                 ("top", "--lat", "1", str(path)),
                 ("top",)):
        code, out, err = cli_runner(*args)
        assert code == 2, args
        assert out == "", args
=== END AC top-usage-errors ===

## User Acceptance

- None.

## Guardrails

- No report row is hardcoded; every row is computed from the file read.
- Application code never reads `sources/run.sh` or the frozen snapshot.
- Output is built completely before being written, so a failing command leaves standard output empty.
