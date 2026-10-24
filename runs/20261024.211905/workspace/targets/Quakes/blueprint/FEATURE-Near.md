# FEATURE: Near

| Field       | Value |
|-------------|-------|
| Version     | 20261024 V1 |
| Description | The near report lists events within a haversine distance of a point, nearest first. |
| Depends On  | FEATURE-MinMagFilter.md, FEATURE-ExitCodes.md |
| Provides    | quakes near, haversine_km |
| Consumes    | filter_min_mag(events, m), format_time |

## Purpose

`quakes near --lat <deg> --lon <deg> --radius <km> [--min-mag <m>] <file>` lists the events whose
great-circle distance from the given point is at most the radius.

## Trigger

The command line `quakes near ...` with all of `--lat`, `--lon` and `--radius`.

## Sequence

1. Read the file and drop events with a null magnitude.
2. Apply `--min-mag` when given.
3. Compute each event's haversine distance from (`--lat`, `--lon`) with `haversine_km`.
4. Keep events whose unrounded distance is `<= --radius` (decision Q-003).
5. Order by unrounded distance ascending, then time ascending.
6. Write CSV; distance is rounded half up to one decimal place.

## Distance

Haversine on a sphere of radius 6371.0 km, angles in radians:

```text
h = sin^2((lat2 - lat1) / 2) + cos(lat1) * cos(lat2) * sin^2((lon2 - lon1) / 2)
d = 2 * 6371.0 * asin(sqrt(h))
```

`haversine_km(lat1, lon1, lat2, lon2) -> float` is a pure function in the compute module.

## Output

Header `distance_km,time,mag,place,id`. Time is UTC `YYYY-MM-DDTHH:MM:SSZ`; magnitude has one decimal
place. Places containing commas are quoted by the `csv` module. With no matching events only the
header is written and the exit status is 0.

## Reads

The saved GeoJSON file named on the command line.

## Writes

CSV on standard output only.

## Programmatic Acceptance

=== AC near-order-and-distance ===
Intent: Events within the radius are listed nearest first with ties broken by time and one-decimal distances.

import csv
import datetime
import io
import json
import math
import os
import re
import tempfile
from cli.testing import cli_runner

BASE = 1735689600000

def hav(lat1, lon1, lat2, lon2):
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = p2 - p1
    dl = math.radians(lon2 - lon1)
    h = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * 6371.0 * math.asin(math.sqrt(h))

def feat(i, mag, place, t, lon, lat):
    return {"type": "Feature",
            "properties": {"mag": mag, "place": place, "time": t, "tsunami": 0},
            "geometry": {"type": "Point", "coordinates": [lon, lat, 10]},
            "id": "ev%d" % i}

# (id suffix, mag, place, time, lon, lat); center is (0, 0)
events = [
    (0, 5.5, "far, Faraway", BASE + 1000, 3.0, 0.0),
    (1, 5.1, "late one, Nearby", BASE + 9000, 1.0, 0.0),
    (2, 5.2, "mid, Midway", BASE + 5000, 2.0, 0.0),
    (3, 5.3, "early one, Nearby", BASE + 2000, 1.0, 0.0),
]
features = [feat(i, m, p, t, lo, la) for (i, m, p, t, lo, la) in events]
radius = 250.0
lat0, lon0 = 0.0, 0.0

inside = [e for e in events if hav(lat0, lon0, e[5], e[4]) <= radius]
inside.sort(key=lambda e: (hav(lat0, lon0, e[5], e[4]), e[3]))
assert 0 < len(inside) < len(events)

with tempfile.TemporaryDirectory() as tmp:
    path = os.path.join(tmp, "q.geojson")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump({"type": "FeatureCollection", "features": features}, fh)
    code, out, err = cli_runner("near", "--lat", str(lat0), "--lon", str(lon0),
                                "--radius", str(radius), path)
print(out)
print(err)
assert code == 0
rows = list(csv.reader(io.StringIO(out)))
assert rows[0] == ["distance_km", "time", "mag", "place", "id"]
body = rows[1:]
assert [r[4] for r in body] == ["ev%d" % e[0] for e in inside]
for r, e in zip(body, inside):
    d = hav(lat0, lon0, e[5], e[4])
    assert re.fullmatch(r"\d+\.\d", r[0])
    assert abs(float(r[0]) - d) <= 0.0501
    stamp = datetime.datetime.fromtimestamp(e[3] / 1000, datetime.timezone.utc)
    assert r[1] == stamp.strftime("%Y-%m-%dT%H:%M:%SZ")
    assert float(r[2]) == e[1]
    assert r[3] == e[2]
=== END AC near-order-and-distance ===

=== AC near-radius-uses-unrounded-distance ===
Intent: The radius comparison uses the unrounded distance, so a radius just below it excludes the event and one just above includes it.

import csv
import io
import json
import math
import os
import tempfile
from cli.testing import cli_runner

BASE = 1735689600000

def hav(lat1, lon1, lat2, lon2):
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dl = math.radians(lon2 - lon1)
    h = math.sin((p2 - p1) / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * 6371.0 * math.asin(math.sqrt(h))

event = {"type": "Feature",
         "properties": {"mag": 5.0, "place": "x, Region", "time": BASE, "tsunami": 0},
         "geometry": {"type": "Point", "coordinates": [1.0, 0.0, 10]},
         "id": "only"}
d = hav(0.0, 0.0, 0.0, 1.0)
below = math.floor(d * 10) / 10
above = math.ceil(d * 10) / 10
assert below < d < above

with tempfile.TemporaryDirectory() as tmp:
    path = os.path.join(tmp, "q.geojson")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump({"type": "FeatureCollection", "features": [event]}, fh)
    code, out, err = cli_runner("near", "--lat", "0", "--lon", "0", "--radius", "%.1f" % below, path)
    assert code == 0
    assert len(list(csv.reader(io.StringIO(out)))) == 1
    code, out, err = cli_runner("near", "--lat", "0", "--lon", "0", "--radius", "%.1f" % above, path)
    print(out)
    assert code == 0
    rows = list(csv.reader(io.StringIO(out)))
    assert len(rows) == 2
    assert rows[1][4] == "only"
=== END AC near-radius-uses-unrounded-distance ===

=== AC near-min-mag-and-empty ===
Intent: --min-mag applies to near and a search with no matches writes only the header with exit 0.

import csv
import io
import json
import os
import tempfile
from cli.testing import cli_runner

BASE = 1735689600000

def feat(i, mag, lon):
    return {"type": "Feature",
            "properties": {"mag": mag, "place": "p%d, Region" % i, "time": BASE + i, "tsunami": 0},
            "geometry": {"type": "Point", "coordinates": [lon, 0.0, 10]},
            "id": "ev%d" % i}

specs = [(0, 5.0, 0.5), (1, 6.5, 0.6), (2, 5.5, 0.7)]
threshold = 5.5
with tempfile.TemporaryDirectory() as tmp:
    path = os.path.join(tmp, "q.geojson")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump({"type": "FeatureCollection", "features": [feat(*s) for s in specs]}, fh)
    code, out, err = cli_runner("near", "--lat", "0", "--lon", "0", "--radius", "500",
                                "--min-mag", str(threshold), path)
    print(out)
    assert code == 0
    rows = list(csv.reader(io.StringIO(out)))
    kept = sorted("ev%d" % i for i, m, lo in specs if m >= threshold)
    assert sorted(r[4] for r in rows[1:]) == kept

    code, out, err = cli_runner("near", "--lat", "60", "--lon", "100", "--radius", "10", path)
    assert code == 0
    assert list(csv.reader(io.StringIO(out))) == [["distance_km", "time", "mag", "place", "id"]]
=== END AC near-min-mag-and-empty ===

=== AC near-haversine-function ===
Intent: haversine_km is a pure function that returns zero for identical points and a symmetric positive distance otherwise.

import importlib
import pkgutil
import cli

found = None
for mod in pkgutil.walk_packages(cli.__path__, "cli."):
    if mod.name.endswith(".testing"):
        continue
    m = importlib.import_module(mod.name)
    if hasattr(m, "haversine_km"):
        found = m.haversine_km
        break
assert found is not None
assert found(10.0, 20.0, 10.0, 20.0) == 0
a = found(0.0, 0.0, 0.0, 90.0)
b = found(0.0, 90.0, 0.0, 0.0)
assert a > 0
assert abs(a - b) < 1e-9
=== END AC near-haversine-function ===

## User Acceptance

- None.

## Guardrails

- Distance uses a sphere of radius 6371.0 km; no other earth model.
- The radius comparison uses the unrounded distance; rounding is for display only.
- No distance is embedded in code; every value is computed from the file being read.
- A failing command writes nothing to standard output.
