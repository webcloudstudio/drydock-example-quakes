# FEATURE: Regions

| Field       | Value |
|-------------|-------|
| Version     | 20261025 V1 |
| Description | The `regions` report: event count and maximum magnitude per region derived from the place text. |
| Depends On  | FEATURE-MagFilter.md, FEATURE-Formatting.md, FEATURE-Options.md, FEATURE-ExitCodes.md |
| Provides    | quakes regions |
| Consumes    | read_feed, extract_events, filter_events, write_csv, format_mag, parse_args |

## Purpose

`quakes regions [--min-mag <m>] <file>` reports the most active regions in a saved USGS GeoJSON file.

## Trigger

Command line: `./quakes regions [--min-mag <m>] <file>`. Only `--min-mag` is accepted.

## Sequence

1. `read_feed`, `extract_events`, and `filter_events` produce the kept events.
2. `region_of(place)` is a pure function: the text after the last `", "` (comma, space) in `place`; the whole `place` when it has none; `"Unknown"` when `place` is `None`.
3. `compute_regions(events)` counts events and tracks the maximum magnitude per region.
4. Rows are ordered by events descending, then region ascending by byte value (plain code point order, so uppercase sorts before lowercase).
5. `write_csv` writes the complete report.

## Output

Header: `region,events,max_mag`. One row per region; `max_mag` has one decimal. With no events, the output is only the header, exit 0. A region containing a comma cannot occur (the last `", "` is split on), but quoting is always delegated to the `csv` module. Non-ASCII region names are written as UTF-8.

## Reads

The saved GeoJSON file named on the command line.

## Writes

Standard output only.

## Programmatic Acceptance

=== AC regions-extract-and-order ===
Intent: Region is the text after the last comma-space, counts and maxima are per region, ordered by events descending then region by byte value.
Suite: scoped
Requires: executable=python3; scope=test

import csv
import io
import json
import os
import tempfile

from cli.testing import cli_runner

# (region, mag) pairs supplied as input; the place text is built from the region.
pairs = [
    ("Zed", 5.0), ("Zed", 5.6),
    ("alpha", 5.1),
    ("Beta", 5.2), ("Beta", 5.0),
    ("Gamma", 5.3), ("Gamma", 5.9), ("Gamma", 5.1),
    ("Delta", 5.4),
]
features = []
for i, (region, mag) in enumerate(pairs):
    features.append({
        "type": "Feature",
        "properties": {"mag": mag, "place": "12 km N of Town " + str(i) + ", " + region,
                       "time": 1735706358208 + i, "tsunami": 0},
        "geometry": {"type": "Point", "coordinates": [1.0, 2.0, 3.0]},
        "id": "e" + str(i),
    })
doc = {"type": "FeatureCollection", "features": features}
expected = {}
for region, mag in pairs:
    entry = expected.setdefault(region, [0, mag])
    entry[0] += 1
    entry[1] = max(entry[1], mag)
order = sorted(expected, key=lambda r: (-expected[r][0], r))
with tempfile.TemporaryDirectory() as tmp:
    path = os.path.join(tmp, "q.geojson")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(doc, fh)
    code, out, err = cli_runner("regions", path)
print(out)
print(err)
assert code == 0
rows = list(csv.reader(io.StringIO(out)))
assert rows[0] == ["region", "events", "max_mag"]
assert [r[0] for r in rows[1:]] == order
for r in rows[1:]:
    assert int(r[1]) == expected[r[0]][0]
    assert float(r[2]) == expected[r[0]][1]
=== END AC regions-extract-and-order ===

=== AC regions-place-rules ===
Intent: A place with several commas splits on the last comma-space, a place without one is its own region, and a null place is Unknown.
Suite: scoped
Requires: executable=python3; scope=test

import csv
import io
import json
import os
import tempfile

from cli.testing import cli_runner

last_part = "Country"
multi_place = "Near Town, Province, " + last_part
plain_place = "Mid-Atlantic Ridge"
comma_no_space = "A,B"
places = [multi_place, plain_place, comma_no_space, None]
features = []
for i, place in enumerate(places):
    features.append({
        "type": "Feature",
        "properties": {"mag": 5.0, "place": place, "time": 1735706358208 + i, "tsunami": 0},
        "geometry": {"type": "Point", "coordinates": [1.0, 2.0, 3.0]},
        "id": "e" + str(i),
    })
doc = {"type": "FeatureCollection", "features": features}
with tempfile.TemporaryDirectory() as tmp:
    path = os.path.join(tmp, "q.geojson")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(doc, fh)
    code, out, err = cli_runner("regions", path)
print(out)
assert code == 0
rows = list(csv.reader(io.StringIO(out)))
names = {r[0] for r in rows[1:]}
assert names == {last_part, plain_place, comma_no_space, "Unknown"}
=== END AC regions-place-rules ===

=== AC regions-min-mag-and-empty ===
Intent: --min-mag restricts the regions counted, null magnitudes are excluded, and an empty result is only the header with exit 0.
Suite: scoped
Requires: executable=python3; scope=test

import csv
import io
import json
import os
import tempfile

from cli.testing import cli_runner

threshold = 5.4
pairs = [("Aland", 5.0), ("Aland", 5.4), ("Bland", 6.0), ("Cland", None), ("Dland", 5.3)]
features = []
for i, (region, mag) in enumerate(pairs):
    features.append({
        "type": "Feature",
        "properties": {"mag": mag, "place": "5 km S of T, " + region, "time": 1735706358208 + i, "tsunami": 0},
        "geometry": {"type": "Point", "coordinates": [1.0, 2.0, 3.0]},
        "id": "e" + str(i),
    })
doc = {"type": "FeatureCollection", "features": features}
kept = [(r, m) for r, m in pairs if m is not None and m >= threshold]
with tempfile.TemporaryDirectory() as tmp:
    path = os.path.join(tmp, "q.geojson")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(doc, fh)
    code, out, err = cli_runner("regions", "--min-mag", str(threshold), path)
    code_none, out_none, err_none = cli_runner("regions", "--min-mag", "9", path)
print(out)
assert code == 0 and code_none == 0
rows = list(csv.reader(io.StringIO(out)))
assert {r[0] for r in rows[1:]} == {r for r, _ in kept}
assert sum(int(r[1]) for r in rows[1:]) == len(kept)
assert list(csv.reader(io.StringIO(out_none))) == [["region", "events", "max_mag"]]
=== END AC regions-min-mag-and-empty ===

=== AC regions-failure-contract ===
Intent: A file that is not a FeatureCollection exits 1 and an unlisted option exits 2, each with empty standard output.
Suite: scoped
Requires: executable=python3; scope=test

import os
import tempfile

from cli.testing import cli_runner

with tempfile.TemporaryDirectory() as tmp:
    bad = os.path.join(tmp, "bad.json")
    with open(bad, "w", encoding="utf-8") as fh:
        fh.write("this is not json")
    code, out, err = cli_runner("regions", bad)
    assert code == 1
    assert out == ""
    code2, out2, err2 = cli_runner("regions", "--lat", "1", bad)
    assert code2 == 2
    assert out2 == ""
=== END AC regions-failure-contract ===

## User Acceptance

- None.

## Guardrails

- Region splitting uses the last `", "` only; `","` without a following space does not split.
- Ties in event count are broken by region name in byte order, not locale or case-insensitive order.
- No region row is hardcoded; all values come from the file read.
