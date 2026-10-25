# FEATURE: Verification

| Field       | Value |
|-------------|-------|
| Version     | 20261025 V1 |
| Description | Terminal release gate that runs the supplied grader and the application's own test suite against the finished application. |
| Depends On  | FEATURE-Summary.md, FEATURE-Top.md, FEATURE-Daily.md, FEATURE-Regions.md, FEATURE-Near.md, FEATURE-FetchFailure.md, FEATURE-TestSuite.md |
| Provides    | release verification |
| Consumes    | quakes summary, quakes top, quakes daily, quakes regions, quakes near, quakes fetch, bin/test.sh |

## Purpose

This is the assembly story. Every behavior is built by its member stories; this story proves the seams between them by running the supplied grader `sources/run.sh` (26 checks of exit code and standard output against the frozen 44-event snapshot) and the application's own pytest suite through `bin/test.sh`.

## Behavior

- `sh sources/run.sh` run from the application root exits zero, meaning every one of its checks passes.
- `sh bin/test.sh` run from the application root exits zero.
- Nothing under `sources/` is modified, rewritten, regenerated, or substituted.
- This story adds no application behavior; a failure here is repaired in the member story that owns the behavior.

## Programmatic Acceptance

=== AC verification-grader ===
Intent: The supplied grader sources/run.sh exits zero against the finished application.
Suite: full
Requires: executable=sh; scope=test

import subprocess

result = subprocess.run(["sh", "sources/run.sh"], capture_output=True, text=True)
print(result.stdout)
print(result.stderr)
assert result.returncode == 0
=== END AC verification-grader ===

=== AC verification-test-suite ===
Intent: The application's own pytest suite, run through bin/test.sh, exits zero.
Requires: executable=sh; scope=test
Requires: python-package=pytest; scope=test

import subprocess

result = subprocess.run(["sh", "bin/test.sh"], capture_output=True, text=True)
print(result.stdout)
print(result.stderr)
assert result.returncode == 0
=== END AC verification-test-suite ===

=== AC verification-quakes-executable ===
Intent: The quakes executable exists at the application root and is executable, as the grader requires.

import os

assert os.path.isfile("quakes")
assert os.access("quakes", os.X_OK)
=== END AC verification-quakes-executable ===

## User Acceptance

- None.

## Guardrails

- Do not modify, rewrite, regenerate, or substitute any file under `sources/`.
- Application code never reads `sources/run.sh` or the snapshot and never embeds a report row, count, or distance.
- Only this terminal story runs the full grader; no other story runs it unscoped.
