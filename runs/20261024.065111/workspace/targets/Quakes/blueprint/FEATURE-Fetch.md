# FEATURE: Fetch

| Field       | Value |
|-------------|-------|
| Version     | 20261024 V1 |
| Description | Downloads a validated USGS earthquake feed and saves it unchanged. |
| Depends On  |  |
| Provides    | quakes fetch |
| Consumes    |  |

## Purpose

Fetch earthquake events from the USGS FDSN event service for a requested date range and save the response as GeoJSON.

## Workflow

1. Accept `--start`, `--end`, optional `--min-mag`, and required `--out`.
2. Request `https://earthquake.usgs.gov/fdsnws/event/1/query` with `format=geojson`, the supplied start and end dates, `minmagnitude` (default `2.5`), and `orderby=time-asc`.
3. Require HTTP status 200 and a JSON GeoJSON `FeatureCollection` object with a `features` array.
4. Write the successful response body unchanged to the output file.
5. Write the fetched feature count to standard output.

The request uses the standard library `urllib.request`. The HTTP call is kept replaceable so tests can stub it without network access.

## CLI Contract

`quakes fetch --start <YYYY-MM-DD> --end <YYYY-MM-DD> [--min-mag <m>] --out <file>`

The magnitude is a decimal matching `-?[0-9]+(\.[0-9]+)?`. Invalid arguments use exit code 2. Network errors, non-200 HTTP status, and invalid response bodies use exit code 1, write no output file, and produce one diagnostic line on standard error. Success exits 0 and writes `fetched,<count>` as CSV to standard output.

## Programmatic Acceptance

=== AC fetch-success ===
Intent: A stubbed HTTP response is saved byte for byte and reports its feature count.

import json
from pathlib import Path
from cli.testing import cli_runner
import quakes

payload = b'{"type":"FeatureCollection","features":[{"id":"event-1"}]}'
expected = json.loads(payload)["features"]
output = Path("fetch-output.geojson")
quakes.urlopen = lambda request: type("Response", (), {
    "__enter__": lambda self: self,
    "__exit__": lambda self, *args: None,
    "status": lambda self: 200,
    "read": lambda self: payload,
})()
code, stdout, stderr = cli_runner(
    "fetch", "--start", "2025-01-01", "--end", "2025-01-02", "--out", str(output)
)
assert code == 0
assert output.read_bytes() == payload
assert len(expected) == 1

=== END AC fetch-success ===

=== AC fetch-failure ===
Intent: A failed HTTP request does not create its output file.

from pathlib import Path
from cli.testing import cli_runner
import quakes

output = Path("fetch-failure.geojson")
quakes.urlopen = lambda request: (_ for _ in ()).throw(OSError())
code, stdout, stderr = cli_runner(
    "fetch", "--start", "2025-01-01", "--end", "2025-01-02", "--out", str(output)
)
assert code == 1
assert not output.exists()

=== END AC fetch-failure ===

## User Acceptance

- None.

## Guardrails

- Never modify or read `sources/run.sh` from application code.
- Never embed report rows, counts, or distances; derive values from the fetched response.
- Tests stub HTTP and do not use the network.
