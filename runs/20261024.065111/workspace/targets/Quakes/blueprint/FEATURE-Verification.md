# FEATURE: Verification

| Field       | Value |
|-------------|-------|
| Version     | 20261024 V1 |
| Description | Provides the offline pytest suite and final conformance verification workflow. |
| Depends On  | FEATURE-Fetch.md, FEATURE-Summary.md, FEATURE-Top.md, FEATURE-Daily.md, FEATURE-Regions.md, FEATURE-Near.md |
| Provides    | bin/test.sh, pytest suite, final conformance verification |
| Consumes    | quakes fetch, quakes summary, quakes top, quakes daily, quakes regions, quakes near |

## Purpose

The project provides a POSIX-compatible `bin/test.sh` that runs the project's pytest suite from the application root and exits zero only when every test passes. The suite covers each report command, behavior-changing options, region and distance rules, fetch through a stubbed HTTP response, and exit codes. Tests use files written by the tests and never open a network connection.

After all command capabilities are implemented, run the supplied grader from the application root as the final conformance check.

## Programmatic Acceptance

=== AC verification-test-suite ===
Intent: The project test launcher succeeds after running the automated tests.

import subprocess

result = subprocess.run(
    ["sh", "bin/test.sh"],
    capture_output=True,
    text=True,
)
print(result.stdout)
print(result.stderr)
assert result.returncode == 0
=== END AC verification-test-suite ===

=== AC verification-full-conformance ===
Intent: The complete supplied grader passes against the finished command set.
Suite: full

import subprocess

result = subprocess.run(
    ["sh", "sources/run.sh"],
    capture_output=True,
    text=True,
)
print(result.stdout)
print(result.stderr)
assert result.returncode == 0
=== END AC verification-full-conformance ===

## User Acceptance

- None.

## Guardrails

- Keep `sources/run.sh` and the frozen GeoJSON snapshot unchanged.
- Tests must stub the HTTP call for fetch and must not use the network.
- Run the supplied grader only as the full terminal conformance check after all implementation stories are complete.
