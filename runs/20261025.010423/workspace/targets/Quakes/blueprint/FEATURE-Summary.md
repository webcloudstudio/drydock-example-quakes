# FEATURE: Summary Report

| Field       | Value |
|-------------|-------|
| Version     | 20261025 V1 |
| Description | The summary command reports event count, time span, magnitude range, mean, and tsunami count. |
| Depends On  | FEATURE-MagFilter.md, FEATURE-Formatting.md, FEATURE-Options.md, FEATURE-ExitCodes.md |
| Provides    | quakes summary |
| Consumes    | read_feed, extract_events, filter_events, write_csv, parse_args |

## Purpose

`quakes summary [--min-mag <m>] <file>` reads a saved feed, applies the filter, and writes a
one-row CSV report to standard output.

## Behavior

- Header: `events,first,last,min_mag,max_mag,mean_mag,tsunami`.
- One data row computed over the filtered events:
  - `events`: the count.
  - `first` / `last`: the earliest and latest event times, formatted `YYYY-MM-DDTHH:MM:SSZ`.
  - `min_mag` / `max_mag`: one decimal place.
  - `mean_mag`: arithmetic mean, two decimals, rounded half up.
  - `tsunami`: the number of events whose `tsunami` equals `1`.
- With no events the row is `0,,,,,,0`.
- Only `--min-mag` is accepted; any other option is a usage error (exit 2).
- Success, including the empty report, exits `0`. An unreadable or invalid file exits `1` with
  nothing on standard output.

## Programmatic Acceptance

=== AC summary-values ===
Intent: The summary row carries count, time span, magnitude range, mean and tsunami count computed from the file.
Requires: executable=python3; scope=test

import csv
import datetime
import io
import json
import tempfile
from pathlib import Path

from cli.testing import cli_runner

BASE = 1735689600000


def feature(ident, mag, k, tsunami):
    return {"type": "Feature", "id": ident,
            "properties": {"mag": mag, "place": "10 km N of Town, Land",
                           "time": BASE + k * 3600000, "tsunami": tsunami},
            "geometry": {"type": "Point", "coordinates": [10.0, 20.0, 12.0]}}


specs = [("a", 5.0, 5, 0), ("b", 6.5, 1, 1), ("c", 5.5, 9, 1), ("d", 5.0, 3, 0)]
features = [feature(*s) for s in specs]
with tempfile.TemporaryDirectory() as tmp:
    path = Path(tmp) / "feed.geojson"
    path.write_text(json.dumps({"type": "FeatureCollection", "features": features}), encoding="utf-8")
    code, out, err = cli_runner("summary", str(path))
print(out, err)
assert code == 0
rows = list(csv.reader(io.StringIO(out)))
assert len(rows) == 2
header, row = rows
assert header == ["events", "first", "last", "min_mag", "max_mag", "mean_mag", "tsunami"]
mags = [s[1] for s in specs]
times = [BASE + s[2] * 3600000 for s in specs]
record = dict(zip(header, row))
assert int(record["events"]) == len(specs)


def epoch(text):
    return int(datetime.datetime.fromisoformat(text).timestamp() * 1000)


assert record["first"].endswith("Z") and record["last"].endswith("Z")
assert epoch(record["first"]) == min(times)
assert epoch(record["last"]) == max(times)
assert float(record["min_mag"]) == min(mags)
assert float(record["max_mag"]) == max(mags)
assert abs(float(record["mean_mag"]) - sum(mags) / len(mags)) <= 0.005
assert int(record["tsunami"]) == sum(s[3] for s in specs)
=== END AC summary-values ===

=== AC summary-mean-half-up ===
Intent: A mean falling exactly on a half cent is rounded up, not to even.
Requires: executable=python3; scope=test

import csv
import io
import json
import tempfile
from pathlib import Path

from cli.testing import cli_runner

mags = [5.0] * 7 + [6.0]
features = [{"type": "Feature", "id": f"e{i}",
             "properties": {"mag": m, "place": "P", "time": 1735689600000 + i * 1000, "tsunami": 0},
             "geometry": {"type": "Point", "coordinates": [0.0, 0.0, 1.0]}} for i, m in enumerate(mags)]
with tempfile.TemporaryDirectory() as tmp:
    path = Path(tmp) / "feed.geojson"
    path.write_text(json.dumps({"type": "FeatureCollection", "features": features}), encoding="utf-8")
    code, out, err = cli_runner("summary", str(path))
print(out, err)
assert code == 0
header, row = list(csv.reader(io.StringIO(out)))
mean_text = dict(zip(header, row))["mean_mag"]
# 41.0 / 8 is exactly 5.125, so half-up yields 5.13 (banker's rounding would give 5.12).
assert mean_text == "5.13"
=== END AC summary-mean-half-up ===

=== AC summary-min-mag-filter ===
Intent: --min-mag restricts the summary to events at or above the threshold.
Requires: executable=python3; scope=test

import csv
import io
import json
import tempfile
from pathlib import Path

from cli.testing import cli_runner

mags = [5.0, 5.4, 5.5, 6.0, 7.1]
features = [{"type": "Feature", "id": f"e{i}",
             "properties": {"mag": m, "place": "P", "time": 1735689600000 + i * 1000, "tsunami": 0},
             "geometry": {"type": "Point", "coordinates": [0.0, 0.0, 1.0]}} for i, m in enumerate(mags)]
threshold = 5.5
with tempfile.TemporaryDirectory() as tmp:
    path = Path(tmp) / "feed.geojson"
    path.write_text(json.dumps({"type": "FeatureCollection", "features": features}), encoding="utf-8")
    code, out, err = cli_runner("summary", "--min-mag", str(threshold), str(path))
print(out, err)
assert code == 0
header, row = list(csv.reader(io.StringIO(out)))
record = dict(zip(header, row))
kept = [m for m in mags if m >= threshold]
assert int(record["events"]) == len(kept)
assert float(record["min_mag"]) == min(kept)
assert float(record["max_mag"]) == max(kept)
=== END AC summary-min-mag-filter ===

=== AC summary-null-mag-excluded ===
Intent: Features with a null magnitude are not counted.
Requires: executable=python3; scope=test

import csv
import io
import json
import tempfile
from pathlib import Path

from cli.testing import cli_runner

mags = [5.0, None, 6.0, None]
features = [{"type": "Feature", "id": f"e{i}",
             "properties": {"mag": m, "place": "P", "time": 1735689600000 + i * 1000, "tsunami": 0},
             "geometry": {"type": "Point", "coordinates": [0.0, 0.0, 1.0]}} for i, m in enumerate(mags)]
with tempfile.TemporaryDirectory() as tmp:
    path = Path(tmp) / "feed.geojson"
    path.write_text(json.dumps({"type": "FeatureCollection", "features": features}), encoding="utf-8")
    code, out, err = cli_runner("summary", str(path))
print(out, err)
assert code == 0
header, row = list(csv.reader(io.StringIO(out)))
assert int(dict(zip(header, row))["events"]) == len([m for m in mags if m is not None])
=== END AC summary-null-mag-excluded ===

=== AC summary-empty ===
Intent: When nothing matches, the report is a single row with a zero count and empty fields.
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
    code, out, err = cli_runner("summary", "--min-mag", "9", str(path))
print(out, err)
assert code == 0
rows = list(csv.reader(io.StringIO(out)))
assert len(rows) == 2
assert rows[1] == ["0", "", "", "", "", "", "0"]
=== END AC summary-empty ===

=== AC summary-failure-codes ===
Intent: An invalid file exits 1, an unlisted option or missing file exits 2, and stdout stays empty in both.
Requires: executable=python3; scope=test

import tempfile
from pathlib import Path

from cli.testing import cli_runner

with tempfile.TemporaryDirectory() as tmp:
    garbage = Path(tmp) / "garbage.json"
    garbage.write_text("this is not json\n", encoding="utf-8")
    missing = Path(tmp) / "no-such-file.geojson"

    code, out, err = cli_runner("summary", str(garbage))
    assert code == 1 and out == ""
    code, out, err = cli_runner("summary", str(missing))
    assert code == 1 and out == ""
    code, out, err = cli_runner("summary", "--n", "3", str(garbage))
    assert code == 2 and out == ""
    code, out, err = cli_runner("summary")
    assert code == 2 and out == ""
    code, out, err = cli_runner("summary", "--min-mag", "big", str(garbage))
    assert code == 2 and out == ""
=== END AC summary-failure-codes ===

## User Acceptance

- None.

## Guardrails

- No report row, count, or value is hardcoded; all values are computed from the file read.
- Application code never reads `sources/run.sh` or the frozen snapshot.
- Output is built completely before being written, so a failing command leaves standard output empty.
