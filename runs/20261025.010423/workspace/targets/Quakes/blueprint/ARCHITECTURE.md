# ARCHITECTURE: Quakes

| Field       | Value |
|-------------|-------|
| Version     | 20261025 V1 |
| Description | Module layout, boundaries, and technical decisions for the standard-library-only `quakes` command-line earthquake reporter. |
| Depends On  | None |
| Provides    | project tree, pytest runner |

## Purpose

`quakes` is a single-process Python 3.11+ command-line tool at the application root. `fetch` downloads a USGS FDSN GeoJSON feed to a file. Five report commands (`summary`, `top`, `daily`, `regions`, `near`) read a saved file, filter it, compute rows, and print CSV to standard output.

## Technology Stack

Derived from `TECHNOLOGY_STACK.md`; that file is the decision of record.

| Technology | Where it applies |
|---|---|
| Python 3.11+ (standard library only) | All application code. `urllib.request` for HTTP, `json`, `csv`, `decimal`, `datetime`, `math`, `re`. |
| CLI | The `quakes` executable and the `cli` package. |
| pytest | Test runner behind `bin/test.sh`; the only development dependency. |
| USGS GeoJSON | Input format. |
| POSIX sh | `bin/test.sh`. |

## Project Layout

| Path | Role |
|---|---|
| `quakes` | Executable launcher at the application root; calls `cli.main` and exits with its return value. |
| `pyproject.toml`, `uv.lock` | Dependency manifest and lockfile. Runtime dependencies: none. |
| `.venv` | Environment created by `uv venv`. |
| `conftest.py` | Exposes the `cli_runner` pytest fixture from `cli.testing`. |
| `cli/__init__.py` | `main(argv=None) -> int`, the command registry `COMMANDS`, exit-code mapping. |
| `cli/errors.py` | `UsageError` (exit 2) and `OperationalError` (exit 1). |
| `cli/options.py` | `parse_args(argv) -> Parsed`. |
| `cli/formatting.py` | `format_time`, `format_mag`, `format_mean`, `format_decimal`, `render_csv`, `write_csv`. |
| `cli/feed.py` | `read_feed(path)`, `extract_events(features)`, `Event`, `filter_events(events, min_mag)`. |
| `cli/reports.py` | One pure function per report, plus `haversine_km`. |
| `cli/fetch.py` | `build_url`, `http_get`, the fetch command. |
| `cli/testing.py` | `cli_runner(*args) -> (exit_code, stdout, stderr)`. |
| `tests/` | Application pytest suite. |
| `bin/test.sh` | POSIX sh wrapper that runs the pytest suite. |
| `sources/` | Read-only scoring assets; never modified and never read by application code. |

## Boundaries and Interfaces

Reading the file, filtering, computing each report, and formatting are separate functions:

1. `read_feed(path) -> list[dict]` validates and returns raw features.
2. `extract_events(features) -> list[Event]` normalizes and drops null-magnitude events.
3. `filter_events(events, min_mag) -> list[Event]` applies `--min-mag`.
4. A report function maps events (and its options) to a list of rows, each row a list of already-formatted strings.
5. `write_csv(rows, stream=None)` writes rows with the `csv` module.

`Parsed` (returned by `parse_args`) is a dataclass with fields `command: str`, `min_mag: float | None`, `n: int`, `lat: float | None`, `lon: float | None`, `radius: float | None`, `start: str | None`, `end: str | None`, `out: str | None`, `file: str | None`. `n` defaults to `10`. `min_mag` is `None` for report commands when omitted and `2.5` for `fetch` when omitted.

Command handlers are registered in `cli.COMMANDS: dict[str, Callable[[Parsed], str]]`. A handler returns the complete standard-output text for the command. `main` writes that text to standard output only after the handler returns, so a failing command leaves standard output empty.

## Exit Codes and Channels

| Code | Cause |
|---|---|
| 0 | Success, including a report with no matching events. |
| 1 | `OperationalError`: unreadable file, not a FeatureCollection, fetch network/HTTP/body failure. |
| 2 | `UsageError`: any malformed invocation. |

A failing command writes nothing to standard output and exactly one diagnostic line to standard error. Standard error is never compared by the grader.

## Technical Decisions

- Half-up rounding uses `decimal.Decimal(repr(x))` quantized with `ROUND_HALF_UP`; built-in `round()` is not used.
- Text ordering is by byte value (plain Python string comparison on code points, with UTF-8 output).
- Tests stub `cli.fetch.http_get`; no test opens a network connection.
- No report row, count, or distance is hardcoded; every value comes from the file read.

## Module Ownership

No persistent store, configuration file, or external service other than the USGS HTTP endpoint exists. File I/O is owned by `cli.feed` (reading) and `cli.fetch` (writing the fetched file). HTTP is owned by `cli.fetch.http_get`. No `DATABASE.md` applies.

## Programmatic Acceptance

=== AC arch-project-files ===
Intent: The project root carries a dependency manifest, lockfile, tests directory, and a conftest exposing the cli_runner fixture.
Suite: scoped

from pathlib import Path

assert Path("pyproject.toml").is_file()
assert Path("uv.lock").is_file()
assert Path("tests").is_dir()
conftest = Path("conftest.py")
assert conftest.is_file()
assert "cli_runner" in conftest.read_text(encoding="utf-8")
=== END AC arch-project-files ===

=== AC arch-stdlib-only ===
Intent: The project declares no runtime dependencies and requires Python 3.11 or newer.

import sys
import tomllib
from pathlib import Path

data = tomllib.loads(Path("pyproject.toml").read_text(encoding="utf-8"))
project = data["project"]
assert project.get("dependencies", []) == []
assert sys.version_info >= (3, 11)
=== END AC arch-stdlib-only ===

=== AC arch-pytest-available ===
Intent: The pytest runner is importable in the project environment.

import importlib.util

assert importlib.util.find_spec("pytest") is not None
=== END AC arch-pytest-available ===

## User Acceptance

- None.

## Guardrails

- Do not modify, rewrite, regenerate, or substitute any file under `sources/`.
- Do not read `sources/run.sh` or the snapshot from application code, and do not hardcode a report row, a count, or a distance.
- Standard library only at runtime; no third-party runtime dependency.
- Tests never open a network connection.
