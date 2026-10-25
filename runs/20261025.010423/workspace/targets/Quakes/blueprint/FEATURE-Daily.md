# FEATURE: Daily

| Field       | Value |
|-------------|-------|
| Version     | 20261025 V1 |
| Description | The `daily` report: event count and maximum magnitude per UTC date, followed by a TOTAL row. |
| Depends On  | FEATURE-MagFilter.md, FEATURE-Formatting.md, FEATURE-Options.md, FEATURE-ExitCodes.md |
| Provides    | quakes daily |
| Consumes    | read_feed, extract_events, filter_events, write_csv, format_time, format_mag, parse_args |

## Purpose

`quakes daily [--min-mag <m>] <file>` reads a saved USGS GeoJSON file and reports how many events occurred on each UTC date and the strongest magnitude on that date.

## Trigger

Command line: `./quakes daily [--min-mag <m>] <file>`. The command accepts only `--min-mag`; any other option is a usage error handled by `parse_args`.

## Sequence

1. `read_feed(file)` validates and returns the features (`OperationalError`, exit 1, on failure).
2. `extract_events` drops null-magnitude features.
3. `filter_events(events, min_mag)` applies `--min-mag`.
4. `compute_daily(events)` groups events by date, where date is the first 10 characters of `format_time(event.time)`.
5. Rows are ordered by date ascending (byte order), followed by one `TOTAL` row.
6. `write_csv` writes the whole report to standard output in one step, after it is fully computed.

`compute_daily(events)` is a pure function returning `(rows, total_row)` with no I/O; formatting is performed by the `format_daily` step that uses `format_mag` and `write_csv`.

## Output

Header: `date,events,max_mag`.

- One row per date that has at least one event, ascending.
- `events` is the integer count; `max_mag` is the maximum magnitude with one decimal.
- Final row: `TOTAL,<events>,<max_mag>` where both values are over all kept events.
- With no events the output is the header followed by `TOTAL,0,` (empty max).
- Exit code 0, including the empty case.

## Reads

The saved GeoJSON file named on the command line. No other input.

## Writes

Standard output only. Nothing is written to any file.

## Programmatic Acceptance

=== AC daily-groups-by-utc-date ===
Intent: Events are grouped per UTC date with counts and maximum magnitude, ascending, followed by a TOTAL row.
Suite: scoped
Requires: executable=python3; scope=test

import csv
import io
import json
import os
import tempfile
from datetime import datetime, timezone

from cli.testing import cli_runner


def ms(day, hour, minute=0, second=0, milli=0):
    moment = datetime(2025, 1, day, hour, minute, second, tzinfo=timezone.utc)
    return int(moment.timestamp()) * 1000 + milli


def feat(i, mag, t):
    return {
        "type": "Feature",
        "properties": {"mag": mag, "place": "10 km N of Town, Land", "time": t, "tsunami": 0},
        "geometry": {"type": "Point", "coordinates": [10.0, 20.0, 5.0]},
        "id": "e" + str(i),
    }


specs = [
    (5.0, ms(3, 1)),
    (6.1, ms(1, 2)),
    (5.4, ms(1, 23, 59, 59, 999)),
    (5.5, ms(3, 12)),
    (5.2, ms(7, 0)),
]
expected = {}
for mag, t in specs:
    label = datetime.fromtimestamp(t // 1000, timezone.utc).strftime("%Y-%m-%d")
    entry = expected.setdefault(label, [0, mag])
    entry[0] += 1
    entry[1] = max(entry[1], mag)

doc = {"type": "FeatureCollection", "features": [feat(i, m, t) for i, (m, t) in enumerate(specs)]}
with tempfile.TemporaryDirectory() as tmp:
    path = os.path.join(tmp, "q.geojson")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(doc, fh)
    code, out, err = cli_runner("daily", path)
print(out)
print(err)
assert code == 0
rows = list(csv.reader(io.StringIO(out)))
assert rows[0] == ["date", "events", "max_mag"]
body = rows[1:-1]
assert [r[0] for r in body] == sorted(expected)
for r in body:
    assert int(r[1]) == expected[r[0]][0]
    assert float(r[2]) == expected[r[0]][1]
total = rows[-1]
assert total[0] == "TOTAL"
assert int(total[1]) == len(specs)
assert float(total[2]) == max(m for m, _ in specs)
=== END AC daily-groups-by-utc-date ===

=== AC daily-empty-report ===
Intent: With no matching events the report is the header and a TOTAL row with zero events and an empty maximum, exit 0.
Suite: scoped
Requires: executable=python3; scope=test

import csv
import io
import json
import os
import tempfile

from cli.testing import cli_runner

feature = {
    "type": "Feature",
    "properties": {"mag": 5.0, "place": "X, Y", "time": 1735706358208, "tsunami": 0},
    "geometry": {"type": "Point", "coordinates": [1.0, 2.0, 3.0]},
    "id": "only",
}
doc = {"type": "FeatureCollection", "features": [feature]}
threshold = 9
with tempfile.TemporaryDirectory() as tmp:
    path = os.path.join(tmp, "q.geojson")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(doc, fh)
    code, out, err = cli_runner("daily", "--min-mag", str(threshold), path)
    empty_doc = {"type": "FeatureCollection", "features": []}
    path2 = os.path.join(tmp, "empty.geojson")
    with open(path2, "w", encoding="utf-8") as fh:
        json.dump(empty_doc, fh)
    code2, out2, err2 = cli_runner("daily", path2)
print(out, out2)
assert code == 0 and code2 == 0
for text in (out, out2):
    rows = list(csv.reader(io.StringIO(text)))
    assert rows == [["date", "events", "max_mag"], ["TOTAL", "0", ""]]
=== END AC daily-empty-report ===

=== AC daily-min-mag-and-null-mag ===
Intent: --min-mag keeps only events with mag at or above it, and null-magnitude events are absent from rows and TOTAL.
Suite: scoped
Requires: executable=python3; scope=test

import csv
import io
import json
import os
import tempfile
from datetime import datetime, timezone

from cli.testing import cli_runner


def ms(day, hour):
    return int(datetime(2025, 1, day, hour, tzinfo=timezone.utc).timestamp()) * 1000


def feat(i, mag, t):
    return {
        "type": "Feature",
        "properties": {"mag": mag, "place": "P", "time": t, "tsunami": 0},
        "geometry": {"type": "Point", "coordinates": [0.0, 0.0, 1.0]},
        "id": "e" + str(i),
    }


threshold = 5.4
specs = [(5.0, ms(1, 1)), (5.4, ms(1, 2)), (6.0, ms(2, 3)), (None, ms(2, 4)), (5.3, ms(4, 5))]
kept = [(m, t) for m, t in specs if m is not None and m >= threshold]
doc = {"type": "FeatureCollection", "features": [feat(i, m, t) for i, (m, t) in enumerate(specs)]}
with tempfile.TemporaryDirectory() as tmp:
    path = os.path.join(tmp, "q.geojson")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(doc, fh)
    code, out, err = cli_runner("daily", "--min-mag", str(threshold), path)
    code_all, out_all, err_all = cli_runner("daily", path)
print(out)
print(out_all)
assert code == 0 and code_all == 0
rows = list(csv.reader(io.StringIO(out)))
assert int(rows[-1][1]) == len(kept)
assert float(rows[-1][2]) == max(m for m, _ in kept)
assert len(rows) - 2 == len({datetime.fromtimestamp(t // 1000, timezone.utc).date() for _, t in kept})
rows_all = list(csv.reader(io.StringIO(out_all)))
assert int(rows_all[-1][1]) == len([1 for m, _ in specs if m is not None])
=== END AC daily-min-mag-and-null-mag ===

=== AC daily-failure-contract ===
Intent: An unreadable file exits 1 and an option daily does not take exits 2, both with empty standard output.
Suite: scoped
Requires: executable=python3; scope=test

import os
import tempfile

from cli.testing import cli_runner

with tempfile.TemporaryDirectory() as tmp:
    missing = os.path.join(tmp, "absent.geojson")
    code, out, err = cli_runner("daily", missing)
    assert code == 1
    assert out == ""
    present = os.path.join(tmp, "x.geojson")
    with open(present, "w", encoding="utf-8") as fh:
        fh.write("{}")
    code2, out2, err2 = cli_runner("daily", "--n", "3", present)
    assert code2 == 2
    assert out2 == ""
=== END AC daily-failure-contract ===

## User Acceptance

- None.

## Guardrails

- The date is the first 10 characters of the formatted UTC time; local time zones are never used.
- No report row, count, or date is hardcoded; every value is computed from the file read.
- Standard output is written only after the report is fully computed, so a failure leaves it empty.
- `daily` accepts no option other than `--min-mag`.
