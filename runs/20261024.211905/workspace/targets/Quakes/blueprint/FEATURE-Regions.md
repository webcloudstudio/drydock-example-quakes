# FEATURE: Regions

| Field       | Value |
|-------------|-------|
| Version     | 20261024 V1 |
| Description | The regions report counts events and the maximum magnitude per region of a saved feed. |
| Depends On  | FEATURE-MinMagFilter.md, FEATURE-ExitCodes.md |
| Provides    | quakes regions |
| Consumes    | filter_min_mag(events, m), region_of |

## Purpose

`quakes regions [--min-mag <m>] <file>` answers which regions are most active. It reads the file,
applies the magnitude filter, groups events by region, and writes one CSV row per region.

## Trigger

The command line `quakes regions [--min-mag <m>] <file>`.

## Sequence

1. Read the file and drop events with a null magnitude (reader).
2. Keep events with `mag >= m` when `--min-mag` is given (filter).
3. Compute one row per region: event count and maximum magnitude (compute).
4. Format and write CSV with the `csv` module, `\n` line endings, UTF-8 (formatter).

## Output

Header `region,events,max_mag`. Rows are ordered by `events` descending, then `region` ascending.
Region text is compared by byte value (its UTF-8 encoding). `max_mag` is written with one decimal
place. The region of an event is the text after the last `, ` in its place, or the whole place when
there is none; a null place is `Unknown`, which is its own region. With no matching events only the
header is written and the exit status is 0.

## Reads

The saved GeoJSON file named on the command line. Nothing else.

## Writes

CSV on standard output only.

## Programmatic Acceptance

=== AC regions-counts-and-order ===
Intent: Regions are grouped, counted and ordered by events descending then region bytes ascending.

import csv
import io
import json
import os
import tempfile
from cli.testing import cli_runner

BASE = 1735689600000

def feat(i, mag, place, t):
    return {"type": "Feature",
            "properties": {"mag": mag, "place": place, "time": t, "tsunami": 0},
            "geometry": {"type": "Point", "coordinates": [10.0, 5.0, 10]},
            "id": "ev%d" % i}

# (place, region, mag)
specs = [
    ("5 km N of Town, Beta", "Beta", 5.0),
    ("6 km N of Town, Beta", "Beta", 6.2),
    ("7 km N of Town, Alpha", "Alpha", 5.5),
    ("8 km N of Town, Alpha", "Alpha", 5.1),
    ("9 km N of Town, Gamma", "Gamma", 7.0),
    ("1 km N of Town, alpha", "alpha", 5.3),
    ("2 km N of Town, alpha", "alpha", 5.4),
    ("3 km N of Town, alpha", "alpha", 5.0),
    ("Plain Region Name", "Plain Region Name", 5.6),
    ("4 km N of Town, Sub, Outer", "Outer", 5.2),
    (None, "Unknown", 5.7),
]
features = [feat(i, m, p, BASE + i * 60000) for i, (p, r, m) in enumerate(specs)]
features.append(feat(99, None, "1 km N of Town, Nullland", BASE))

counts = {}
maxes = {}
for p, r, m in specs:
    counts[r] = counts.get(r, 0) + 1
    maxes[r] = max(maxes.get(r, m), m)
expected = sorted(counts, key=lambda r: (-counts[r], r.encode("utf-8")))

with tempfile.TemporaryDirectory() as tmp:
    path = os.path.join(tmp, "q.geojson")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump({"type": "FeatureCollection", "features": features}, fh)
    code, out, err = cli_runner("regions", path)
print(out)
print(err)
assert code == 0
rows = list(csv.reader(io.StringIO(out)))
assert rows[0] == ["region", "events", "max_mag"]
body = rows[1:]
assert [r[0] for r in body] == expected
for r in body:
    assert int(r[1]) == counts[r[0]]
    assert float(r[2]) == maxes[r[0]]
assert "Nullland" not in [r[0] for r in body]
=== END AC regions-counts-and-order ===

=== AC regions-min-mag-and-empty ===
Intent: --min-mag restricts the regions report and an empty result is only the header with exit 0.

import csv
import io
import json
import os
import tempfile
from cli.testing import cli_runner

BASE = 1735689600000

def feat(i, mag, place):
    return {"type": "Feature",
            "properties": {"mag": mag, "place": place, "time": BASE + i * 1000, "tsunami": 0},
            "geometry": {"type": "Point", "coordinates": [10.0, 5.0, 10]},
            "id": "ev%d" % i}

threshold = 6.0
specs = [("1 km N of T, Low", 5.0), ("2 km N of T, Low", 5.9),
         ("3 km N of T, High", 6.0), ("4 km N of T, High", 6.8)]
features = [feat(i, m, p) for i, (p, m) in enumerate(specs)]

with tempfile.TemporaryDirectory() as tmp:
    path = os.path.join(tmp, "q.geojson")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump({"type": "FeatureCollection", "features": features}, fh)
    code, out, err = cli_runner("regions", "--min-mag", str(threshold), path)
    print(out)
    assert code == 0
    rows = list(csv.reader(io.StringIO(out)))
    kept = [m for p, m in specs if m >= threshold]
    assert len(rows) == 2
    assert rows[1][0] == "High"
    assert int(rows[1][1]) == len(kept)
    assert float(rows[1][2]) == max(kept)

    code, out, err = cli_runner("regions", "--min-mag", "99", path)
    print(out)
    assert code == 0
    rows = list(csv.reader(io.StringIO(out)))
    assert rows == [["region", "events", "max_mag"]]
=== END AC regions-min-mag-and-empty ===

=== AC regions-failure-contract ===
Intent: A missing file exits 1 and an extra file argument exits 2, both with empty standard output.

import os
import tempfile
from cli.testing import cli_runner

with tempfile.TemporaryDirectory() as tmp:
    missing = os.path.join(tmp, "absent.geojson")
    code, out, err = cli_runner("regions", missing)
    assert code == 1
    assert out == ""
    code, out, err = cli_runner("regions", missing, missing)
    assert code == 2
    assert out == ""
=== END AC regions-failure-contract ===

## User Acceptance

- None.

## Guardrails

- Region text is compared by byte value, never by locale collation.
- No report value is embedded in code; every row is computed from the file being read.
- A failing command writes nothing to standard output.
