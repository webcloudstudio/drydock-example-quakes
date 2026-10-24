# FEATURE: Summary

| Field       | Value |
|-------------|-------|
| Version     | 20261024 V1 |
| Description | Produces summary statistics for events in a saved GeoJSON FeatureCollection. |
| Depends On  |  |
| Provides    | quakes summary |
| Consumes    |  |

## Purpose

Summarize the events in a saved GeoJSON file, optionally filtering by minimum magnitude.

## Workflow

1. Read the supplied FeatureCollection and normalize each feature into an event.
2. Exclude events with null magnitude and apply `--min-mag` to all remaining events.
3. Compute count, earliest and latest UTC event times, minimum, maximum and mean magnitudes, and tsunami count.
4. Write the result as CSV with the defined header and one data row.

`properties.time` is milliseconds since the Unix epoch; output times are UTC, truncated to whole seconds. Mean magnitude uses two decimal places rounded half up. An empty result writes `0,,,,,,0` after the header.

## CLI Contract

`quakes summary [--min-mag <m>] <file>`

Magnitude values are decimals matching `-?[0-9]+(\.[0-9]+)?`. Success exits 0, operational file or FeatureCollection errors exit 1, and malformed or unsupported arguments exit 2. A failing command writes no standard output and one diagnostic line to standard error.

## Programmatic Acceptance

=== AC summary-success ===
Intent: The summary command succeeds on a supplied FeatureCollection.
Requires: executable=./quakes; scope=test

import json
import tempfile
from pathlib import Path
from cli.testing import cli_runner

event = {"type": "Feature", "id": "a", "properties": {
    "mag": 5.0, "place": "Test Place", "time": 1735689600000, "tsunami": 1
}, "geometry": {"type": "Point", "coordinates": [0, 0, 1]}}
with tempfile.TemporaryDirectory() as directory:
    source = Path(directory) / "events.json"
    source.write_text(json.dumps({"type": "FeatureCollection", "features": [event]}))
    code, stdout, stderr = cli_runner("summary", str(source))
    assert code == 0

=== END AC summary-success ===

=== AC summary-invalid-file ===
Intent: An unreadable or invalid input file returns the operational exit code.

from cli.testing import cli_runner

code, stdout, stderr = cli_runner("summary", "missing-file.geojson")
assert code == 1

=== END AC summary-invalid-file ===

## User Acceptance

- None.

## Guardrails

- Every summary value must be computed from the input file.
- Apply `--min-mag` consistently and exclude null magnitudes.
- Emit CSV with newline line endings.
