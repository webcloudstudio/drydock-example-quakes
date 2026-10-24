# FEATURE: Top

| Field       | Value |
|-------------|-------|
| Version     | 20261024 V1 |
| Description | Lists the largest earthquake events from a saved GeoJSON FeatureCollection. |
| Depends On  |  |
| Provides    | quakes top |
| Consumes    |  |

## Purpose

List up to the requested number of largest events, optionally filtered by minimum magnitude.

## Workflow

1. Read and normalize the events from the input FeatureCollection.
2. Exclude null magnitudes and apply `--min-mag`.
3. Sort by magnitude descending, then event time ascending.
4. Keep the first `--n` events (default 10) and write the defined CSV header and rows.

Magnitude and depth are formatted to one decimal place, with depth rounded half up.

## CLI Contract

`quakes top [--min-mag <m>] [--n <count>] <file>`

`<count>` is a positive integer. Success exits 0; unreadable or invalid input exits 1; malformed or unsupported arguments exit 2. Failures write no standard output and one diagnostic line to standard error.

## Programmatic Acceptance

=== AC top-options ===
Intent: The top command accepts its count option and succeeds on a supplied event file.

import json
import tempfile
from pathlib import Path
from cli.testing import cli_runner

event = {"type": "Feature", "id": "input-id", "properties": {
    "mag": 5.5, "place": "Input Place", "time": 1735689600000, "tsunami": 0
}, "geometry": {"type": "Point", "coordinates": [0, 0, 1]}}
with tempfile.TemporaryDirectory() as directory:
    source = Path(directory) / "events.json"
    source.write_text(json.dumps({"type": "FeatureCollection", "features": [event]}))
    code, stdout, stderr = cli_runner("top", "--n", "1", str(source))
    assert code == 0

=== END AC top-options ===

=== AC top-invalid-count ===
Intent: A nonpositive count returns the usage exit code.

import json
import tempfile
from pathlib import Path
from cli.testing import cli_runner

event = {"type": "Feature", "id": "input-id", "properties": {
    "mag": 5.5, "place": "Input Place", "time": 1735689600000, "tsunami": 0
}, "geometry": {"type": "Point", "coordinates": [0, 0, 1]}}
with tempfile.TemporaryDirectory() as directory:
    source = Path(directory) / "events.json"
    source.write_text(json.dumps({"type": "FeatureCollection", "features": [event]}))
    code, stdout, stderr = cli_runner("top", "--n", "0", str(source))
    assert code == 2
    assert stdout == ""

=== END AC top-invalid-count ===

## User Acceptance

- None.

## Guardrails

- Ordering is magnitude descending and then time ascending.
- The count must be positive.
- Event values come from the file; do not hardcode report output.
