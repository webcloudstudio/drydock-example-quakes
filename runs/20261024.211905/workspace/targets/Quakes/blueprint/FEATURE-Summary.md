# FEATURE: Summary

| Field       | Value |
|-------------|-------|
| Version     | 20261024 V1 |
| Description | The summary report: event count, time span, magnitude range, mean and tsunami count. |
| Depends On  | FEATURE-MinMagFilter.md, FEATURE-ExitCodes.md |
| Provides    | quakes summary |
| Consumes    | filter_min_mag(events, m), format_time |

## Purpose

`quakes summary [--min-mag <m>] <file>` writes the header `events,first,last,min_mag,max_mag,mean_mag,tsunami`
and one row. `first` and `last` are the earliest and latest event times, `min_mag` and `max_mag` have
one decimal, `mean_mag` has two decimals rounded half up, and `tsunami` counts events whose `tsunami`
equals `1`. With no events the row is `0,,,,,,0`. Output is written with the `csv` module and `\n`
line endings; the report is computed fully before anything is written.

## Programmatic Acceptance

=== AC summary-values ===
Intent: The summary row carries the count, earliest and latest time, magnitude range, half-up mean and tsunami count computed from the file.

import csv
import io
import json
import os
import tempfile
from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_UP

from cli.testing import cli_runner


def iso(ms):
    return datetime.fromtimestamp(ms // 1000, timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


mags = [5.0, 5.1, 5.1]
times = [1735800000999, 1735700000000, 1735900000500]
tsunamis = [1, 0, 1]
feats = [
    {"type": "Feature",
     "properties": {"mag": mags[i], "place": "Place " + str(i), "time": times[i], "tsunami": tsunamis[i]},
     "geometry": {"type": "Point", "coordinates": [10.0, 20.0, 15]},
     "id": "ev" + str(i)}
    for i in range(len(mags))
]
with tempfile.TemporaryDirectory() as d:
    path = os.path.join(d, "q.geojson")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump({"type": "FeatureCollection", "features": feats}, fh)
    code, out, err = cli_runner("summary", path)

print(out)
print(err)
assert code == 0
rows = list(csv.reader(io.StringIO(out)))
assert len(rows) == 2
assert rows[0] == ["events", "first", "last", "min_mag", "max_mag", "mean_mag", "tsunami"]
mean = (sum(Decimal(str(m)) for m in mags) / len(mags)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
expected = [
    str(len(mags)),
    iso(min(times)),
    iso(max(times)),
    f"{min(mags):.1f}",
    f"{max(mags):.1f}",
    str(mean),
    str(sum(1 for t in tsunamis if t == 1)),
]
assert rows[1] == expected
assert "\r" not in out
=== END AC summary-values ===

=== AC summary-no-events ===
Intent: When no event matches, the summary row is a zero count, empty fields and a zero tsunami count.

import csv
import io
import json
import os
import tempfile

from cli.testing import cli_runner

feats = [
    {"type": "Feature",
     "properties": {"mag": 5.0, "place": "Somewhere", "time": 1735700000000, "tsunami": 1},
     "geometry": {"type": "Point", "coordinates": [0.0, 0.0, 10]},
     "id": "ev0"}
]
with tempfile.TemporaryDirectory() as d:
    path = os.path.join(d, "q.geojson")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump({"type": "FeatureCollection", "features": feats}, fh)
    code, out, err = cli_runner("summary", "--min-mag", "9", path)

print(out)
print(err)
assert code == 0
rows = list(csv.reader(io.StringIO(out)))
assert len(rows) == 2
assert rows[1] == ["0"] + [""] * 5 + ["0"]
=== END AC summary-no-events ===

=== AC summary-empty-collection ===
Intent: A valid FeatureCollection with no features also reports the empty row and exits 0.

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
    code, out, err = cli_runner("summary", path)

assert code == 0
rows = list(csv.reader(io.StringIO(out)))
assert len(rows) == 2
assert rows[1] == ["0"] + [""] * 5 + ["0"]
=== END AC summary-empty-collection ===

=== AC summary-null-mag-excluded ===
Intent: A feature whose magnitude is null is excluded from the summary entirely.

import csv
import io
import json
import os
import tempfile

from cli.testing import cli_runner

mags = [5.2, None, 6.0, None]
feats = [
    {"type": "Feature",
     "properties": {"mag": mags[i], "place": "Place " + str(i), "time": 1735700000000 + i * 60000, "tsunami": 0},
     "geometry": {"type": "Point", "coordinates": [0.0, 0.0, 10]},
     "id": "ev" + str(i)}
    for i in range(len(mags))
]
with tempfile.TemporaryDirectory() as d:
    path = os.path.join(d, "q.geojson")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump({"type": "FeatureCollection", "features": feats}, fh)
    code, out, err = cli_runner("summary", path)

assert code == 0
rows = list(csv.reader(io.StringIO(out)))
real = [m for m in mags if m is not None]
assert rows[1][0] == str(len(real))
assert rows[1][3] == f"{min(real):.1f}"
assert rows[1][4] == f"{max(real):.1f}"
=== END AC summary-null-mag-excluded ===

=== AC summary-tsunami-counts-ones ===
Intent: Only events whose tsunami value equals 1 are counted in the tsunami column.

import csv
import io
import json
import os
import tempfile

from cli.testing import cli_runner

tsunamis = [0, 1, 0, 1, 1, 0]
feats = [
    {"type": "Feature",
     "properties": {"mag": 5.5, "place": "Place " + str(i), "time": 1735700000000 + i * 60000, "tsunami": tsunamis[i]},
     "geometry": {"type": "Point", "coordinates": [0.0, 0.0, 10]},
     "id": "ev" + str(i)}
    for i in range(len(tsunamis))
]
with tempfile.TemporaryDirectory() as d:
    path = os.path.join(d, "q.geojson")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump({"type": "FeatureCollection", "features": feats}, fh)
    code, out, err = cli_runner("summary", path)

assert code == 0
rows = list(csv.reader(io.StringIO(out)))
assert rows[1][6] == str(tsunamis.count(1))
=== END AC summary-tsunami-counts-ones ===

=== AC summary-min-mag-option ===
Intent: summary honours --min-mag by computing every column over only the events at or above the threshold.

import csv
import io
import json
import os
import tempfile

from cli.testing import cli_runner

mags = [5.0, 5.5, 6.0, 5.4]
threshold = 5.5
feats = [
    {"type": "Feature",
     "properties": {"mag": mags[i], "place": "Place " + str(i), "time": 1735700000000 + i * 60000, "tsunami": 0},
     "geometry": {"type": "Point", "coordinates": [0.0, 0.0, 10]},
     "id": "ev" + str(i)}
    for i in range(len(mags))
]
with tempfile.TemporaryDirectory() as d:
    path = os.path.join(d, "q.geojson")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump({"type": "FeatureCollection", "features": feats}, fh)
    code, out, err = cli_runner("summary", "--min-mag", str(threshold), path)

assert code == 0
rows = list(csv.reader(io.StringIO(out)))
kept = [m for m in mags if m >= threshold]
assert rows[1][0] == str(len(kept))
assert rows[1][3] == f"{min(kept):.1f}"
assert rows[1][4] == f"{max(kept):.1f}"
=== END AC summary-min-mag-option ===

=== AC summary-failure-silent-stdout ===
Intent: An unreadable file makes summary exit 1 with nothing on standard output.

import os
import tempfile

from cli.testing import cli_runner

with tempfile.TemporaryDirectory() as d:
    missing = os.path.join(d, "no-such-file.geojson")
    code, out, err = cli_runner("summary", missing)

assert code == 1
assert out == ""
=== END AC summary-failure-silent-stdout ===

## User Acceptance

- None.

## Guardrails

- No count, time or magnitude is hardcoded; every value comes from the file read.
- A failing command writes nothing to standard output.
- Standard error carries diagnostics only.
