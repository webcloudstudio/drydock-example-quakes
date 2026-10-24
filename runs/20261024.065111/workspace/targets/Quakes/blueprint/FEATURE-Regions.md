# FEATURE: Regions

| Field       | Value |
|-------------|-------|
| Version     | 20261024 V1 |
| Description | Groups saved earthquake events by region and reports event counts. |
| Depends On  |  |
| Provides    | quakes regions |
| Consumes    |  |

## Purpose

Report counts and maximum magnitudes grouped by the source-defined region of each event.

## Region Rule

The region is the text after the last comma and space in `place`, or the whole place when no such delimiter occurs. A null place is `Unknown`, which is also its region.

## Workflow

1. Read and normalize events, exclude null magnitudes, and apply `--min-mag`.
2. Group by region, count events, and compute each group's maximum magnitude.
3. Sort groups by event count descending, then region ascending.
4. Write CSV with one row per region.

Maximum magnitudes use one decimal place.

## CLI Contract

`quakes regions [--min-mag <m>] <file>`

Success exits 0; operational file or FeatureCollection errors exit 1; usage errors exit 2. Failures write no standard output and one diagnostic line to standard error.

## Programmatic Acceptance

=== AC regions-command ===
Intent: The regions command succeeds for a FeatureCollection with an event.

import json
import tempfile
from pathlib import Path
from cli.testing import cli_runner

event = {"type": "Feature", "id": "input-id", "properties": {
    "mag": 5.5, "place": "Input Place, Region", "time": 1735689600000, "tsunami": 0
}, "geometry": {"type": "Point", "coordinates": [0, 0, 1]}}
with tempfile.TemporaryDirectory() as directory:
    source = Path(directory) / "events.json"
    source.write_text(json.dumps({"type": "FeatureCollection", "features": [event]}))
    code, stdout, stderr = cli_runner("regions", str(source))
    assert code == 0

=== END AC regions-command ===

=== AC regions-filter ===
Intent: The minimum magnitude option is accepted and returns success.

import json
import tempfile
from pathlib import Path
from cli.testing import cli_runner

event = {"type": "Feature", "id": "input-id", "properties": {
    "mag": 5.5, "place": "Input Place, Region", "time": 1735689600000, "tsunami": 0
}, "geometry": {"type": "Point", "coordinates": [0, 0, 1]}}
with tempfile.TemporaryDirectory() as directory:
    source = Path(directory) / "events.json"
    source.write_text(json.dumps({"type": "FeatureCollection", "features": [event]}))
    code, stdout, stderr = cli_runner("regions", "--min-mag", "6", str(source))
    assert code == 0

=== END AC regions-filter ===

## User Acceptance

- None.

## Guardrails

- Apply the same magnitude filter used by all reports.
- Region extraction follows the exact delimiter rule.
- Derive all rows and counts from the input file.
