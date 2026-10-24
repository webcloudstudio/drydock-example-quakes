# ARCHITECTURE: Quakes

| Field       | Value |
|-------------|-------|
| Version     | 20261024 V1 |
| Description | Module layout, boundaries and technical decisions for the `quakes` earthquake feed reporter command-line tool. |
| Depends On  | None |
| Provides    | quakes executable, cli.main, cli.testing.cli_runner, cli.errors.UsageError, cli.errors.OperationalFailure |
| Consumes    | None |

## Purpose

`quakes` is a Python 3.11+ standard-library command-line tool. `quakes fetch` saves a period of the
USGS FDSN event feed as a GeoJSON file. Five report commands (`summary`, `top`, `daily`, `regions`,
`near`) read a saved file and write a CSV report to standard output. Every report value is computed
from the file being read; nothing is embedded.

## Technology Stack

Derived from `TECHNOLOGY_STACK.md`, which remains the decision of record.

| Technology | Where it applies |
|---|---|
| Python 3.11+ (standard library only) | All application code: `cli/` package and the `quakes` executable. |
| CLI (`cli.md`) | The `quakes` entry point and the `cli` package with `main(argv) -> int`. |
| pytest | The project test suite under `tests/`, run through `bin/test.sh`. |
| USGS GeoJSON | Input format for every report; fetched with `urllib.request`. |
| POSIX sh | `bin/test.sh` and the supplied grader `sources/run.sh`. |

## Module Layout

All application code lives in the `cli` package at the application root.

| Module | Responsibility | Built by story |
|---|---|---|
| `quakes` (root, executable) | `#!` Python launcher that calls `cli.main` and exits with its return value | foundation |
| `cli/__init__.py` | `main(argv) -> int`: help check, parse, dispatch, exit-code mapping, writing stdout | foundation, then feature stories |
| `cli/testing.py` | `cli_runner(*args) -> (exit_code, stdout, stderr)` | foundation |
| `cli/errors.py` | `UsageError` and `OperationalFailure`, both `Exception` subclasses | foundation |
| `cli/options.py` | `COMMANDS`, `Invocation`, `parse_args(argv)` | feature-cli-dispatch |
| `cli/commands.py` | `HANDLERS` registry and `dispatch(invocation) -> str` | feature-cli-dispatch |
| `cli/help.py` | `wants_help(argv)`, `help_text(command)` | feature-help |
| `cli/reader.py` | `Event`, `read_events(path)` | feature-feed-reader |
| `cli/normalise.py` | `format_time`, `region_of`, number formatting helpers | feature-event-normalise |
| `cli/filtering.py` | `filter_min_mag(events, m)` | feature-min-mag |
| `cli/reports.py` and per-report modules | One compute function and one format function per report | report stories |
| `cli/fetch.py` | `http_get(url)` and the fetch handler | feature-fetch |

Reading the file, filtering, computing each report, and formatting are separate functions, each
unit-tested on its own.

## Control Flow

`main(argv)` runs, in order:

1. Reconfigure standard output to UTF-8 with `\n` newlines when the stream supports it.
2. If `cli.help.wants_help(argv)`, write the help text to standard output and return `0`.
3. `invocation = parse_args(argv)`, then `text = commands.dispatch(invocation)`.
4. Write `text` to standard output once, only after the handler has returned, and return `0`.
5. `UsageError` returns `2` and `OperationalFailure` returns `1`. Each writes exactly one diagnostic
   line to standard error and nothing to standard output.

A handler is a function `handler(invocation) -> str` returning the complete standard-output text. A
handler never writes to standard output itself. This is what guarantees that a failing command
writes nothing to standard output.

## Boundaries and Ownership

| Boundary | Owning module | Notes |
|---|---|---|
| Local file reads | `cli/reader.py` | The only module that opens a feed file for reading. |
| Network | `cli/fetch.py` `http_get` | The only module that opens a connection; tests replace `http_get`. |
| Standard output | `cli/__init__.py` `main` | Handlers return text. |
| Standard error | `cli/__init__.py` `main` | Diagnostics only; never compared. |
| Persistence, configuration, external stores | None | The product has no database or configuration. |

## Technical Decisions

- Exit codes: `0` success (including a report with no matching events), `1` operational failure,
  `2` usage error.
- Magnitudes are held as `decimal.Decimal` built from `str(value)` so that half-up rounding is exact.
- CSV is written with Python's `csv` module, `lineterminator="\n"`, and encoded as UTF-8.
- Application code never reads `sources/run.sh` or the snapshot and never embeds a report row,
  count, or distance.

## Programmatic Acceptance

=== AC foundation-imports ===
Intent: The cli package publishes main, the testing runner, and the two error types.
Requires: executable=python3; scope=test

import os
import sys

sys.path.insert(0, os.getcwd())

import cli
from cli import main
from cli.errors import OperationalFailure, UsageError
from cli.testing import cli_runner

assert callable(main)
assert callable(cli_runner)
assert issubclass(UsageError, Exception)
assert issubclass(OperationalFailure, Exception)
assert UsageError is not OperationalFailure
assert sys.version_info >= (3, 11)
=== END AC foundation-imports ===

=== AC foundation-runner-contract ===
Intent: cli_runner returns an integer exit code with text standard output and standard error without spawning a process.
Requires: executable=python3; scope=test

import os
import sys

sys.path.insert(0, os.getcwd())

from cli.testing import cli_runner

code, out, err = cli_runner()
print(code, repr(out), repr(err))
assert isinstance(code, int)
assert isinstance(out, str)
assert isinstance(err, str)
=== END AC foundation-runner-contract ===

=== AC foundation-executable ===
Intent: The quakes file at the application root is executable and exits with the same code as cli.main.
Requires: executable=python3; scope=test

import os
import subprocess
import sys

sys.path.insert(0, os.getcwd())

from cli.testing import cli_runner

assert os.path.isfile("quakes")
assert os.access("quakes", os.X_OK)
with open("quakes", "rb") as handle:
    first_two = handle.read(2)
assert first_two == b"#!"

inproc_code, _, _ = cli_runner()
result = subprocess.run([sys.executable, "quakes"], capture_output=True, text=True)
print(result.stdout)
print(result.stderr, file=sys.stderr)
assert result.returncode == inproc_code
=== END AC foundation-executable ===

=== AC foundation-pytest-fixture ===
Intent: The root conftest exposes the cli_runner fixture and the project declares its dependency manifest.
Requires: executable=python3; scope=test

import os
import sys

sys.path.insert(0, os.getcwd())

import conftest

assert hasattr(conftest, "cli_runner")
assert os.path.isfile("pyproject.toml")
assert os.path.isdir("cli")
=== END AC foundation-pytest-fixture ===

## User Acceptance

- None.

## Guardrails

- Do not modify, rewrite, regenerate, or substitute any file under `sources/`.
- Application code never reads `sources/run.sh` or the snapshot and never hardcodes a report row, a count, or a distance.
- Standard library only; Python 3.11 or newer.
- Diagnostics go to standard error and are never compared.
- No test opens a network connection.
