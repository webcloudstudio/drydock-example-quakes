# FEATURE: Near Earthquake Events

| Field       | Value |
|-------------|-------|
| Version     | 20261024 V1 |
| Description | Finds saved earthquake events within a requested distance of a point. |
| Depends On  | ARCHITECTURE.md |
| Provides    | quakes near |
| Consumes    | saved GeoJSON FeatureCollection |

## Purpose

The `near` command lists events within a radius of a latitude and longitude. It reads a saved GeoJSON FeatureCollection and writes a CSV report to standard output.

## Trigger and inputs

```text
quakes near --lat <deg> --lon <deg> --radius <km> [--min-mag <m>] <file>
```

The file is the final argument. Options may follow the command in any order. `--min-mag` uses the shared report default when omitted. Decimal values match `-?[0-9]+(\.[0-9]+)?`.

## Behavior

- Reject latitude outside −90 to 90, longitude outside −180 to 180, and radius that is not positive as usage errors.
- Require all of `--lat`, `--lon`, and `--radius`; reject missing values, malformed decimals, extra files, and options not listed for this command.
- Apply the magnitude filter before reporting. Events with null magnitude are excluded.
- Compute great-circle distance with the haversine formula on a sphere of radius 6371.0 km. Include events whose distance is at most the requested radius.
- Order matches by distance ascending, then event time ascending.
- Write CSV with the header `distance_km,time,mag,place,id`. Format distance to one decimal place using round half up, magnitude to one decimal place, and event time in UTC as `YYYY-MM-DDTHH:MM:SSZ`, truncated to whole seconds.
- A null place is `Unknown`. Use the standard region and event parsing rules described in `ARCHITECTURE.md`.
- A valid request with no matching events succeeds and emits the header only.
- On usage errors, return exit code 2. On unreadable or invalid GeoJSON input, return exit code 1. On failure, write no standard output and one diagnostic line to standard error.

## Programmatic Acceptance

=== AC near-valid-request ===
Intent: A valid near request is accepted by the CLI.

from cli.testing import cli_runner

code, _, _ = cli_runner(
    "near", "--lat", "0", "--lon", "0", "--radius", "1", "sources/quakes_2025-01-01_07.geojson"
)
assert code == 0
=== END AC near-valid-request ===

=== AC near-required-options ===
Intent: A near request missing a required coordinate is rejected as a usage error.

from cli.testing import cli_runner

code, _, _ = cli_runner(
    "near", "--lat", "0", "--lon", "0", "sources/quakes_2025-01-01_07.geojson"
)
assert code == 2
=== END AC near-required-options ===

=== AC near-coordinate-bounds ===
Intent: A latitude outside the documented range is rejected as a usage error.

from cli.testing import cli_runner

code, _, _ = cli_runner(
    "near", "--lat", "95", "--lon", "0", "--radius", "1", "sources/quakes_2025-01-01_07.geojson"
)
assert code == 2
=== END AC near-coordinate-bounds ===

=== AC near-invalid-file ===
Intent: An invalid GeoJSON file is reported as an operational failure without standard output.

from cli.testing import cli_runner
from pathlib import Path

invalid_file = Path("near-invalid.geojson")
invalid_file.write_text("not json\n")
try:
    code, stdout, _ = cli_runner(
        "near", "--lat", "0", "--lon", "0", "--radius", "1", str(invalid_file)
    )
    assert code == 1
    assert stdout == ""
finally:
    invalid_file.unlink(missing_ok=True)
=== END AC near-invalid-file ===

## User Acceptance

- None.

## Guardrails

- Do not hardcode report rows, counts, or distances; derive every reported value from the input file.
- Do not read or depend on `sources/run.sh` from application code.
