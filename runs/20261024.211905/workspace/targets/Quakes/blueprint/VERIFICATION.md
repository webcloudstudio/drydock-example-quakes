# FEATURE: Verification

| Field       | Value |
|-------------|-------|
| Version     | 20261024 V1 |
| Description | Terminal gate that runs the project test suite and the supplied grader over the completed application. |
| Depends On  | FEATURE-Summary.md, FEATURE-Top.md, FEATURE-Daily.md, FEATURE-Regions.md, FEATURE-NearValidation.md, FEATURE-Help.md, FEATURE-FetchStubTests.md, FEATURE-TestRunner.md |
| Provides    | None |
| Consumes    | quakes executable |

## Purpose

This is the assembly story. Once every member story has closed, the integrated application must pass its own suite via `sh bin/test.sh` and the supplied grader via `sh sources/run.sh`, both exiting zero. The grader's 26 checks compare exit code and standard output of the report commands against the frozen snapshot. The `sources/` directory is staged read-only and is never modified.

## Programmatic Acceptance

=== AC verification-project-suite ===
Intent: The project's own pytest suite passes through bin/test.sh.
Requires: executable=sh; scope=test

import subprocess
import sys

result = subprocess.run(["sh", "bin/test.sh"], capture_output=True, text=True)
print(result.stdout)
print(result.stderr, file=sys.stderr)
assert result.returncode == 0
=== END AC verification-project-suite ===

=== AC verification-grader ===
Intent: The supplied grader sources/run.sh exits zero against the completed application.
Suite: full
Requires: executable=sh; scope=test

import subprocess
import sys

result = subprocess.run(["sh", "sources/run.sh"], capture_output=True, text=True)
print(result.stdout)
print(result.stderr, file=sys.stderr)
assert result.returncode == 0
=== END AC verification-grader ===

## User Acceptance

- None.

## Guardrails

- Do not modify, rewrite, regenerate, or substitute any file under `sources/`.
- Application code never reads `sources/run.sh` or the snapshot and never embeds a report value.
