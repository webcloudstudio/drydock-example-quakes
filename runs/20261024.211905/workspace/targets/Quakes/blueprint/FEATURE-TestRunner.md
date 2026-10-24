# FEATURE: Test Runner

| Field       | Value |
|-------------|-------|
| Version     | 20261024 V1 |
| Description | Provide a POSIX-compatible bin/test.sh that runs the project's pytest suite from the application root. |
| Depends On  | ARCHITECTURE.md |
| Provides    | bin/test.sh |
| Consumes    | cli.testing.cli_runner |

## Purpose

The application ships its own pytest suite, and `bin/test.sh` is the single entry point that runs it. The script is POSIX `sh`, changes to the application root regardless of the caller's working directory, activates the `.venv` launcher, runs `pytest -q`, and exits zero only when every test passes. Unit tests for each pure function (read, filter, compute, format) live under `tests/`.

## Interface

- `sh bin/test.sh` — no arguments. Exit status is the pytest exit status.
- Standard output and standard error carry pytest's own output; neither is compared.

## Behavior

1. Resolve the application root from the script's own location, not the caller's working directory.
2. Use the `.venv` environment created by `uv venv` when present.
3. Run `pytest -q` and propagate its exit status unchanged.

## Programmatic Acceptance

=== AC testrunner-syntax ===
Intent: bin/test.sh exists and is syntactically valid POSIX sh.
Requires: executable=sh; scope=test

import subprocess
from pathlib import Path

script = Path("bin") / "test.sh"
assert script.is_file()
result = subprocess.run(["sh", "-n", str(script)], capture_output=True, text=True)
print(result.stdout)
print(result.stderr)
assert result.returncode == 0
=== END AC testrunner-syntax ===

=== AC testrunner-suite-exists ===
Intent: The project's own pytest suite exists under tests/ with at least one test module.

from pathlib import Path

modules = sorted(Path("tests").glob("test_*.py"))
print([m.name for m in modules])
assert len(modules) >= 1
=== END AC testrunner-suite-exists ===

=== AC testrunner-runs-green ===
Intent: Running bin/test.sh from a different working directory exits zero when the suite passes.
Requires: executable=sh; scope=test

import os
import subprocess
import sys
import tempfile
from pathlib import Path

script = (Path("bin") / "test.sh").resolve()
with tempfile.TemporaryDirectory() as elsewhere:
    result = subprocess.run(
        ["sh", str(script)], capture_output=True, text=True, cwd=elsewhere,
        env={**os.environ, "QUAKES_TEST_RUNNER_NESTED": "1"},
    )
print(result.stdout)
print(result.stderr, file=sys.stderr)
assert result.returncode == 0
=== END AC testrunner-runs-green ===

## User Acceptance

- None.

## Guardrails

- `bin/test.sh` must be POSIX `sh`; it must not require bash features.
- Tests must not open a network connection.
- `bin/test.sh` must not modify anything under `sources/`.
