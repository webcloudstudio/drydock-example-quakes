# Evidence: Block 1 · Foundational (block-1)

- block type: block
- date: 2026-10-24
- resulting state: closed/verified
- story points (combined assembled cost): 7386
- execution id: 20261025.011423.936Z-50b38c55

## Stories built
- Stand up the Python project tree, environment, dependency manifest, and pytest runner. (architecture) [story]

## Reusable compacts
- ARCHITECTURE_compact.md

## Stacked context
- implements: python.md (SP 1166)
- compass: COMPASS.md (SP 986)
- implements: ARCHITECTURE.md (SP 2331)
- stack: common.md (SP 2776)

## Build directory changes
- .gitignore
- bin/test.sh
- conftest.py
- pyproject.toml
- tests/test_foundation.py
- uv.lock

## Pre-build acceptance observation
- RED: arch-project-files (ARCHITECTURE.md)
  intent: The project root carries a dependency manifest, lockfile, tests directory, and a conftest exposing the cli_runner fixture.
  return code: 1
  stderr:
    Traceback (most recent call last):
      File "arch-project-files.py", line 4, in <module>
        assert Path("uv.lock").is_file()
               ^^^^^^^^^^^^^^^^^^^^^^^^^
    AssertionError
- GREEN (prepassed): arch-stdlib-only (ARCHITECTURE.md)
  intent: The project declares no runtime dependencies and requires Python 3.11 or newer.
  return code: 0
- GREEN (prepassed): arch-pytest-available (ARCHITECTURE.md)
  intent: The pytest runner is importable in the project environment.
  return code: 0

## Post-build programmatic acceptance
- PASS: arch-project-files (ARCHITECTURE.md)
  intent: The project root carries a dependency manifest, lockfile, tests directory, and a conftest exposing the cli_runner fixture.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/Quakes/runs/20261025.010423/build/Quakes/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: arch-stdlib-only (ARCHITECTURE.md)
  intent: The project declares no runtime dependencies and requires Python 3.11 or newer.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/Quakes/runs/20261025.010423/build/Quakes/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: arch-pytest-available (ARCHITECTURE.md)
  intent: The pytest runner is importable in the project environment.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/Quakes/runs/20261025.010423/build/Quakes/.venv/bin/python
  provisioning: not required
  return code: 0

## Build summary
There's already a `pyproject.toml` in the build directory. I'll read it before touching anything.The existing `pyproject.toml` is a minimal stub with no dev dependency or pytest config. I'll extend it rather than replace it. Next I'll create the environment with `uv`.The environment is up. Now I'll add pytest as the only dev dependency through `uv`, which also writes `uv.lock`.pytest 9.1.1 is locked. Before writing the foundation tests, I'll check how pytest 9 marks fixtures so the test can read the fixture registration back rather than grep source text.pytest 9 has no public check for fixture registration, so the test will use the `_fixture_function_marker` attribute. I'll note that in the summary. Now I'll write the config, conftest, launcher, ignore file, and tests.The suite passes, but `set -u` makes `activate` print an `OSTYPE` warning. I'll drop `-u` around the activate call and remove a redundant assertion and the unneeded cache option.The suite is green and the git status shows only the expected files, with `.venv/` ignored. Last, I'll confirm the declared `test_command` and the lockfile are consistent.Foundation is in place and verified. Here is the consumer-facing summary of the architecture spec.

<reusable-compact filename="ARCHITECTURE.md">
Project: quakes (Python >=3.11, stdlib only at runtime; pytest dev-only). Executable `quakes` at root -> `cli.main(argv=None)->int`.
Modules: cli/__init__.py (main, COMMANDS: dict[str, Callable[[Parsed], str]], exit mapping); cli/errors.py (UsageError exit 2, OperationalError exit 1); cli/options.py (parse_args(argv)->Parsed); cli/formatting.py (format_time, format_mag, format_mean, format_decimal, render_csv, write_csv); cli/feed.py (read_feed(path)->list[dict], extract_events(features)->list[Event], Event, filter_events(events,min_mag)); cli/reports.py (one pure fn per report, haversine_km); cli/fetch.py (build_url, http_get, fetch command); cli/testing.py (cli_runner(*args)->(exit_code, stdout, stderr)).
Parsed dataclass: command:str, min_mag:float|None, n:int (default 10), lat, lon, radius:float|None, start, end, out, file:str|None. min_mag default None for reports, 2.5 for fetch.
Commands: fetch, summary, top, daily, regions, near.
Exit codes: 0 success (incl. empty report); 1 OperationalError (unreadable file, not FeatureCollection, fetch network/HTTP/body failure); 2 UsageError. Failing command: empty stdout, one stderr line.
Pipeline: read_feed -> extract_events (drops null magnitude) -> filter_events -> report fn returns rows of preformatted strings -> write_csv. Handlers return full stdout text; main writes only after success.
Technical: half-up rounding via Decimal(repr(x)) ROUND_HALF_UP; string ordering by code point; UTF-8 output. Tests stub cli.fetch.http_get; no network in tests. No hardcoded rows/counts/distances.
Guardrails: never modify/read sources/ from app code. Tests never open network.
Project layout: pyproject.toml + uv.lock, .venv (uv venv), conftest.py (cli_runner fixture from cli.testing), tests/, bin/test.sh (runs pytest -q).
</reusable-compact>

RESULT: SUCCESS

FILES CHANGED:
- pyproject.toml
- uv.lock
- .gitignore
- conftest.py
- bin/test.sh
- tests/test_foundation.py

SUMMARY:
Stood up the Python project foundation in the build directory.
- `pyproject.toml`: kept the existing `quakes` project block (Python >=3.11, `dependencies = []`), added `[dependency-groups] dev = ["pytest>=9.1.1"]` and `[tool.pytest.ini_options] testpaths = ["tests"]`. The pytest name was added through `uv add --dev pytest`, which resolved it from the registry (pytest 9.1.1).
- `uv.lock`: generated by uv; `uv lock --check` passes.
- `.venv/`: created by `uv venv` (CPython 3.12.13). It is gitignored and not committed.
- `.gitignore`: ignores `.venv/`, caches, and build output.
- `conftest.py`: exposes the `cli_runner` fixture. It imports `cli.testing` lazily inside the fixture, because that module belongs to a later block and the fixture is not used yet.
- `bin/test.sh`: POSIX sh launcher that activates `.venv` and runs `pytest -q`.
- `tests/test_foundation.py`: 8 tests covering the three declared architecture criteria (manifest, lockfile, tests dir, conftest fixture, empty runtime deps, Python 3.11+, pytest importable) and the launcher's executable bit.

Checks run:
- `sh bin/test.sh` → 8 passed, exit 0.
- `.venv/bin/pytest -q` (the declared `test_command`) → 8 passed.
- `uv lock --check` → consistent.
- Declared acceptance criteria `arch-project-files`, `arch-stdlib-only`, and `arch-pytest-available` are satisfied by the same checks in `tests/test_foundation.py`. I did not run the criterion scripts through the Drydock runner.
- Did not run `sh sources/run.sh`; this is not a terminal story and no `quakes` executable exists yet.

Nothing was committed or staged, and `sources/` was not touched.

<blueprint-decisions>
[{"spec":"ARCHITECTURE.md","severity":"Low","subject":"cli_runner fixture import timing","decision":"conftest.py defines the cli_runner fixture but imports cli.testing lazily inside the fixture body, because cli/ is built in a later block and an eager import would break collection of the foundation tests. Is that acceptable, or should cli/testing.py be created in this block?"}]
</blueprint-decisions>

FAILURE_SUMMARY: none
FAILURE_DETAIL: not applicable
