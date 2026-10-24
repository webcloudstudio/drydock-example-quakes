# FEATURE: Daily

| Field       | Value |
|-------------|-------|
| Version     | 20261024 V1 |
| Description | The per-day report: events and maximum magnitude per UTC date, with a TOTAL row. |
| Depends On  | FEATURE-MinMagFilter.md, FEATURE-ExitCodes.md |
| Provides    | quakes daily |
| Consumes    | filter_min_mag(events, m), format_time |

## Purpose

`quakes daily [--min-mag <m>] <file>` writes the header `date,events,max_mag`, one row per UTC date
that has events in ascending order, then `TOTAL,<events>,<max_mag>` covering all events. The date is
the first 10 characters of the event time. Magnitudes have one decimal. With no events the only row
after the header is `TOTAL,0,` with an empty maximum.

## Programmatic Acceptance

=== AC daily-per-date-rows ===
Intent: One row per UTC date with the event count and maximum magnitude, in ascending date order, followed by the TOTAL row.

import csv
import io
import json
import os
import tempfile
from datetime import datetime, timezone

from cli.testing import cli_runner


def day(ms):
    return datetime.fromtimestamp(ms // 1000, timezone.utc).date().isoformat()


mags = [5.1, 6.0, 5.4, 5.0, 5.9, 5.2, 5.6]
times = [
    1735862400000,
    1735689600000,
    1735775999999,
    1735776000000,
    1735689600001,
    1735948800000,
    1735862399999,
]
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
    code, out, err = cli_runner("daily", path)

print(out)
print(err)
assert code == 0
rows = list(csv.reader(io.StringIO(out)))
assert rows[0] == ["date", "events", "max_mag"]
by_day = {}
for m, t in zip(mags, times):
    by_day.setdefault(day(t), []).append(m)
expected = [[k, str(len(v)), f"{max(v):.1f}"] for k, v in sorted(by_day.items())]
expected.append(["TOTAL", str(len(mags)), f"{max(mags):.1f}"])
assert rows[1:] == expected
assert "\r" not in out
=== END AC daily-per-date-rows ===

=== AC daily-total-row-sums ===
Intent: The TOTAL row's event count equals the sum of the per-date counts and its maximum equals the largest per-date maximum.

import csv
import io
import json
import os
import tempfile

from cli.testing import cli_runner

mags = [5.0, 5.3, 6.2, 5.5, 5.1, 5.9]
base = 1735689600000
times = [base + i * 40000000 for i in range(len(mags))]
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
    code, out, err = cli_runner("daily", path)

assert code == 0
rows = list(csv.reader(io.StringIO(out)))
body, total = rows[1:-1], rows[-1]
assert total[0] == "TOTAL"
assert int(total[1]) == sum(int(r[1]) for r in body) == len(mags)
assert float(total[2]) == max(float(r[2]) for r in body)
assert [r[0] for r in body] == sorted(r[0] for r in body)
=== END AC daily-total-row-sums ===

=== AC daily-no-events ===
Intent: When no event matches, daily writes the header and a TOTAL row with zero events and an empty maximum.

import csv
import io
import json
import os
import tempfile

from cli.testing import cli_runner

feats = [
    {"type": "Feature",
     "properties": {"mag": 5.0, "place": "Somewhere", "time": 1735700000000, "tsunami": 0},
     "geometry": {"type": "Point", "coordinates": [0.0, 0.0, 10]},
     "id": "ev0"}
]
with tempfile.TemporaryDirectory() as d:
    path = os.path.join(d, "q.geojson")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump({"type": "FeatureCollection", "features": feats}, fh)
    code, out, err = cli_runner("daily", "--min-mag", "9", path)

print(out)
print(err)
assert code == 0
rows = list(csv.reader(io.StringIO(out)))
assert rows == [["date", "events", "max_mag"], ["TOTAL", "0", ""]]
=== END AC daily-no-events ===

=== AC daily-null-mag-excluded ===
Intent: Features with a null magnitude do not count toward any date or the total.

import csv
import io
import json
import os
import tempfile

from cli.testing import cli_runner

mags = [5.2, None, 6.0, None, 5.4]
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
    code, out, err = cli_runner("daily", path)

assert code == 0
rows = list(csv.reader(io.StringIO(out)))
real = [m for m in mags if m is not None]
assert rows[-1] == ["TOTAL", str(len(real)), f"{max(real):.1f}"]
=== END AC daily-null-mag-excluded ===

=== AC daily-min-mag-option ===
Intent: daily honours --min-mag, dropping dates whose events are all below the threshold.

import csv
import io
import json
import os
import tempfile
from datetime import datetime, timezone

from cli.testing import cli_runner


def day(ms):
    return datetime.fromtimestamp(ms // 1000, timezone.utc).date().isoformat()


threshold = 5.5
mags = [5.0, 5.6, 5.2, 6.0]
times = [1735689600000, 1735776000000, 1735862400000, 1735948800000]
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
    code, out, err = cli_runner("daily", "--min-mag", str(threshold), path)

assert code == 0
rows = list(csv.reader(io.StringIO(out)))
kept = [(m, t) for m, t in zip(mags, times) if m >= threshold]
assert [r[0] for r in rows[1:-1]] == [day(t) for m, t in kept]
assert rows[-1] == ["TOTAL", str(len(kept)), f"{max(m for m, t in kept):.1f}"]
=== END AC daily-min-mag-option ===

=== AC daily-failure-silent-stdout ===
Intent: A file that is not a FeatureCollection makes daily exit 1 with nothing on standard output.

import os
import tempfile

from cli.testing import cli_runner

with tempfile.TemporaryDirectory() as d:
    path = os.path.join(d, "garbage.json")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("this is not json\n")
    code, out, err = cli_runner("daily", path)

assert code == 1
assert out == ""
=== END AC daily-failure-silent-stdout ===

## User Acceptance

- None.

## Guardrails

- No date, count or magnitude is hardcoded; every value comes from the file read.
- Dates follow the UTC day, never the local time zone.
- A failing command writes nothing to standard output.
