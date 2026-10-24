# FEATURE: Daily

| Field       | Value |
|-------------|-------|
| Version     | 20261024 V1 |
| Description | Groups saved earthquake events by UTC date and reports daily totals. |
| Depends On  |  |
| Provides    | quakes daily |
| Consumes    |  |

## Purpose

Report the number of events and maximum magnitude for each UTC date in the input file.

## Workflow

1. Read events, exclude null magnitudes, and apply the optional minimum magnitude.
2. Group matching events by the first ten characters of their UTC timestamp.
3. Sort dates ascending and compute each date's count and maximum magnitude.
4. Emit a final `TOTAL` row with overall event count and maximum magnitude.

Maximum magnitudes use one decimal place. With no matching events, the total maximum magnitude is empty.

## CLI Contract

`quakes daily [--min-mag <m>] <file>`

Success exits 0; operational file or FeatureCollection errors exit 1; usage errors exit 2. Failures write no standard output and one diagnostic line to standard error.

## Programmatic Acceptance

=== AC daily-empty ===
Intent: An empty event file produces a successful daily report with an empty total maximum.

import json
import tempfile
from pathlib import Path
from cli.testing import cli_runner

with tempfile.TemporaryDirectory() as directory:
    source = Path(directory) / "empty.json"
    source.write_text(json.dumps({"type": "FeatureCollection", "features": []}))
    code, stdout, stderr = cli_runner("daily", str(source))
    assert code == 0

=== END AC daily-empty ===

=== AC daily-filter ===
Intent: The minimum magnitude option is accepted and the report succeeds.

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
    code, stdout, stderr = cli_runner("daily", "--min-mag", "6", str(source))
    assert code == 0

=== END AC daily-filter ===

## User Acceptance

- None.

## Guardrails

- Use UTC dates and ascending date order.
- Include the total row, including when no events match.
- Compute all values from the supplied file.
