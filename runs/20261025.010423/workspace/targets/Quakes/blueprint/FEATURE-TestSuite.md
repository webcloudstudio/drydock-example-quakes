# FEATURE: Test Suite

| Field       | Value |
|-------------|-------|
| Version     | 20261025 V1 |
| Description | Provide a POSIX bin/test.sh that runs the application's pytest suite and exits zero only when every test passes. |
| Depends On  | ARCHITECTURE.md, FEATURE-CliFoundation.md |
| Provides    | bin/test.sh |
| Consumes    | cli.testing.cli_runner |

## Purpose

The Compass requires reading, filtering, computing, and formatting to be separate unit-tested functions, with HTTP stubbed and no network connection in any test. `bin/test.sh` is the single entry point that runs that suite from the application root. It is the command named by the Compass Verification Protocol for every behavioral story.

## Behavior

- `bin/test.sh` is a POSIX `sh` script (`#!/bin/sh`), with no bashisms.
- It resolves the application root from its own location (the parent of `bin/`) and changes to it, so it works from any current directory.
- When `.venv/bin/activate` exists under the application root it is sourced; otherwise the ambient interpreter is used.
- It runs `pytest -q` over the whole suite, unfiltered: no `-k`, no marker selection, no path restriction.
- It exits with pytest's own exit status: zero only when every test passes, nonzero otherwise.
- It writes nothing of its own to standard output beyond what pytest prints.

## Suite Requirements

The tests the build agent writes beside the code must:

- Cover each report (`summary`, `top`, `daily`, `regions`, `near`), each option, the region rule, the haversine distance rule, and each exit code, using files the tests write themselves.
- Exercise `fetch` through a stubbed `http_get`; no test opens a network connection.
- Never read `sources/run.sh` or the snapshot from tests or application code.

## Programmatic Acceptance

=== AC testsuite-script-exists ===
Intent: bin/test.sh exists at the application root and declares a POSIX sh interpreter.
Requires: executable=sh; scope=test

from pathlib import Path

script = Path("bin/test.sh")
assert script.is_file()
first_line = script.read_text(encoding="utf-8").splitlines()[0]
print(first_line)
assert first_line.startswith("#!")
assert first_line.rstrip().endswith("sh")
assert "bash" not in first_line
=== END AC testsuite-script-exists ===

=== AC testsuite-runs-green ===
Intent: Running bin/test.sh over the built application's own pytest suite exits zero.
Requires: executable=sh; scope=test
Requires: python-package=pytest; scope=test

import subprocess

result = subprocess.run(["sh", "bin/test.sh"], capture_output=True, text=True)
print(result.stdout)
print(result.stderr)
assert result.returncode == 0
=== END AC testsuite-runs-green ===

=== AC testsuite-runs-from-other-directory ===
Intent: bin/test.sh resolves the application root itself, so an outside working directory gives the same exit status.
Requires: executable=sh; scope=test
Requires: python-package=pytest; scope=test

import os
import subprocess
import tempfile

script = os.path.abspath("bin/test.sh")
with tempfile.TemporaryDirectory() as elsewhere:
    result = subprocess.run(["sh", script], capture_output=True, text=True, cwd=elsewhere)
print(result.stdout)
print(result.stderr)
assert result.returncode == 0
=== END AC testsuite-runs-from-other-directory ===

=== AC testsuite-propagates-failure ===
Intent: bin/test.sh exits nonzero when a test in its application root fails.
Requires: executable=sh; scope=test
Requires: python-package=pytest; scope=test

import os
import shutil
import subprocess
import sys
import tempfile

script_source = os.path.abspath("bin/test.sh")
with tempfile.TemporaryDirectory() as root:
    os.makedirs(os.path.join(root, "bin"))
    os.makedirs(os.path.join(root, "tests"))
    shutil.copy(script_source, os.path.join(root, "bin", "test.sh"))
    with open(os.path.join(root, "tests", "test_always_fails.py"), "w", encoding="utf-8") as handle:
        handle.write("def test_always_fails():\n    assert False\n")
    env = {**os.environ, "PATH": os.path.dirname(sys.executable) + os.pathsep + os.environ.get("PATH", "")}
    result = subprocess.run(
        ["sh", os.path.join(root, "bin", "test.sh")],
        capture_output=True, text=True, env=env, cwd=root,
    )
print(result.stdout)
print(result.stderr)
assert result.returncode != 0
=== END AC testsuite-propagates-failure ===

=== AC testsuite-passes-when-tests-pass ===
Intent: bin/test.sh exits zero for an application root whose only test passes.
Requires: executable=sh; scope=test
Requires: python-package=pytest; scope=test

import os
import shutil
import subprocess
import sys
import tempfile

script_source = os.path.abspath("bin/test.sh")
with tempfile.TemporaryDirectory() as root:
    os.makedirs(os.path.join(root, "bin"))
    os.makedirs(os.path.join(root, "tests"))
    shutil.copy(script_source, os.path.join(root, "bin", "test.sh"))
    with open(os.path.join(root, "tests", "test_always_passes.py"), "w", encoding="utf-8") as handle:
        handle.write("def test_always_passes():\n    assert True\n")
    env = {**os.environ, "PATH": os.path.dirname(sys.executable) + os.pathsep + os.environ.get("PATH", "")}
    result = subprocess.run(
        ["sh", os.path.join(root, "bin", "test.sh")],
        capture_output=True, text=True, env=env, cwd=root,
    )
print(result.stdout)
print(result.stderr)
assert result.returncode == 0
=== END AC testsuite-passes-when-tests-pass ===

## User Acceptance

- None.

## Guardrails

- `bin/test.sh` runs the full suite unfiltered; it never skips, deselects, or reinterprets tests.
- No test opens a network connection; `fetch` is tested only through a stubbed HTTP call.
- No test or application code reads `sources/run.sh` or the snapshot.
- Nothing under `sources/` is modified.
