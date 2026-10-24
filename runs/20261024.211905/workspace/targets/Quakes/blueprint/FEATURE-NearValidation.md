# FEATURE: Near Validation

| Field       | Value |
|-------------|-------|
| Version     | 20261024 V1 |
| Description | The near command rejects out-of-range or missing coordinates and radius as usage errors. |
| Depends On  | FEATURE-Near.md |
| Provides    | near option validation |
| Consumes    | quakes near |

## Purpose

Guarantee that `quakes near` only runs with a valid point and radius, and otherwise fails as a usage
error before reading the file.

## Rules

- `--lat` must be within -90 to 90 inclusive.
- `--lon` must be within -180 to 180 inclusive.
- `--radius` must be greater than zero.
- All three of `--lat`, `--lon` and `--radius` are required.
- Any violation exits 2, writes nothing to standard output, and writes one diagnostic line to
  standard error.
- The boundary values -90, 90, -180 and 180 are valid.

## Reads

The command line only.

## Writes

Nothing on standard output on failure; one line on standard error.

## Programmatic Acceptance

=== AC near-validation-rejects ===
Intent: Out-of-range or missing near options exit 2 with empty standard output and one diagnostic line.

import json
import os
import tempfile
from cli.testing import cli_runner

with tempfile.TemporaryDirectory() as tmp:
    path = os.path.join(tmp, "q.geojson")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump({"type": "FeatureCollection", "features": []}, fh)
    cases = [
        ["--lat", "95", "--lon", "0", "--radius", "10"],
        ["--lat", "-90.5", "--lon", "0", "--radius", "10"],
        ["--lat", "0", "--lon", "180.5", "--radius", "10"],
        ["--lat", "0", "--lon", "-181", "--radius", "10"],
        ["--lat", "0", "--lon", "0", "--radius", "0"],
        ["--lat", "0", "--lon", "0", "--radius", "-5"],
        ["--lon", "0", "--radius", "10"],
        ["--lat", "0", "--radius", "10"],
        ["--lat", "0", "--lon", "0"],
        [],
    ]
    for opts in cases:
        code, out, err = cli_runner("near", *opts, path)
        print(opts, code, repr(err))
        assert code == 2
        assert out == ""
        assert len(err.strip().splitlines()) == 1
=== END AC near-validation-rejects ===

=== AC near-validation-accepts-boundaries ===
Intent: The inclusive boundary values for latitude and longitude and a small positive radius are accepted.

import csv
import io
import json
import os
import tempfile
from cli.testing import cli_runner

with tempfile.TemporaryDirectory() as tmp:
    path = os.path.join(tmp, "q.geojson")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump({"type": "FeatureCollection", "features": []}, fh)
    cases = [
        ["--lat", "90", "--lon", "180", "--radius", "10"],
        ["--lat", "-90", "--lon", "-180", "--radius", "0.5"],
    ]
    for opts in cases:
        code, out, err = cli_runner("near", *opts, path)
        print(opts, code, out)
        assert code == 0
        rows = list(csv.reader(io.StringIO(out)))
        assert len(rows) == 1
=== END AC near-validation-accepts-boundaries ===

=== AC near-validation-precedes-file-read ===
Intent: A usage error is reported as exit 2 even when the file does not exist.

import os
import tempfile
from cli.testing import cli_runner

with tempfile.TemporaryDirectory() as tmp:
    missing = os.path.join(tmp, "absent.geojson")
    code, out, err = cli_runner("near", "--lat", "95", "--lon", "0", "--radius", "10", missing)
    assert code == 2
    assert out == ""
=== END AC near-validation-precedes-file-read ===

## User Acceptance

- None.

## Guardrails

- Validation failures never write to standard output.
- Messages are diagnostics only and are never part of the contract.
