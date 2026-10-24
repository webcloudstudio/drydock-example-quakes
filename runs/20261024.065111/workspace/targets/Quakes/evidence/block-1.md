# Evidence: Block 1 · Service (block-1)

- block type: block
- date: 2026-10-24
- resulting state: closed/verified
- story points (combined assembled cost): 5612
- execution id: 20261024.065434.361Z-75a9a6ae

## Stories built
- Fetch and save a validated USGS GeoJSON feed. (fetch) [story]

## Missing context
- context: INSTRUCTIONS.md

## Stacked context
- stack: python_compact.md (SP 601)
- compass: COMPASS.md (SP 643)
- implements: FEATURE-Fetch.md (SP 737)
- stack: common.md (SP 1812)
- stack: cli.md (SP 1755)

## Build directory changes
- cli/__init__.py
- cli/__main__.py
- cli/parser.py
- cli/testing.py
- quakes
- quakes.py
- tests/__init__.py
- tests/test_fetch.py

## Pre-build acceptance observation
- RED: fetch-success (FEATURE-Fetch.md)
  intent: A stubbed HTTP response is saved byte for byte and reports its feature count.
  error: foundation not built: `cli` is the package the cli foundation (cli.md) builds, and the build directory has no `cli/`. The criterion exercises the built application, so it was not run.
- RED: fetch-failure (FEATURE-Fetch.md)
  intent: A failed HTTP request does not create its output file.
  error: foundation not built: `cli` is the package the cli foundation (cli.md) builds, and the build directory has no `cli/`. The criterion exercises the built application, so it was not run.

## Post-build programmatic acceptance
- PASS: fetch-success (FEATURE-Fetch.md)
  intent: A stubbed HTTP response is saved byte for byte and reports its feature count.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: fetch-failure (FEATURE-Fetch.md)
  intent: A failed HTTP request does not create its output file.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/.venv/bin/python
  provisioning: not required
  return code: 0

## Build summary
RESULT: SUCCESS

FILES CHANGED:
- `quakes.py`
- `quakes`
- `cli/__init__.py`
- `cli/parser.py`
- `cli/testing.py`
- `cli/__main__.py`
- `tests/__init__.py`
- `tests/test_fetch.py`

SUMMARY:
Implemented `quakes fetch` with the specified request parameters, response validation, byte-for-byte saving, feature count output, and failure handling. Added five fetch tests. `python -m unittest discover -v` passed all five; `./quakes fetch --help` also succeeded. `sources/` was left untouched.

BLOCKERS:
- `INSTRUCTIONS.md` was absent from the supplied context and workspace.
