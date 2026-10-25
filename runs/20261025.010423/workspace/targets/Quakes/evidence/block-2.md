# Evidence: Block 2 · Foundational (block-2)

- block type: block
- date: 2026-10-24
- resulting state: closed/verified
- story points (combined assembled cost): 6576
- execution id: 20261025.011616.186Z-e5617d6c

## Stories built
- Publish the cli package, main entry point, cli_runner test helper, and the quakes launcher. (cli-foundation) [story]

## Stacked context
- stack: python_compact.md (SP 921)
- compass: COMPASS.md (SP 986)
- implements: FEATURE-CliFoundation.md (SP 1116)
- context: ARCHITECTURE_compact.md (SP 741)
- stack: cli.md (SP 2689)

## Build directory changes
- cli/__init__.py
- cli/errors.py
- cli/testing.py
- quakes
- tests/test_cli_foundation.py

## Pre-build acceptance observation
- RED: clifound-main-returns-int (FEATURE-CliFoundation.md)
  intent: main accepts an argv list and returns an integer exit code.
  error: foundation not built: `cli` is the package the cli foundation (cli.md) builds, and the build directory has no `cli/`. The criterion exercises the built application, so it was not run.
- RED: clifound-runner-shape (FEATURE-CliFoundation.md)
  intent: cli_runner returns an exit code, stdout text, and stderr text, and agrees with main.
  error: foundation not built: `cli` is the package the cli foundation (cli.md) builds, and the build directory has no `cli/`. The criterion exercises the built application, so it was not run.
- RED: clifound-registry (FEATURE-CliFoundation.md)
  intent: The command registry is a dict that main consults for dispatch.
  error: foundation not built: `cli` is the package the cli foundation (cli.md) builds, and the build directory has no `cli/`. The criterion exercises the built application, so it was not run.
- RED: clifound-launcher (FEATURE-CliFoundation.md)
  intent: The quakes launcher at the application root is executable and exits with the same code main returns.
  error: foundation not built: `cli` is the package the cli foundation (cli.md) builds, and the build directory has no `cli/`. The criterion exercises the built application, so it was not run.

## Post-build programmatic acceptance
- PASS: clifound-main-returns-int (FEATURE-CliFoundation.md)
  intent: main accepts an argv list and returns an integer exit code.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/Quakes/runs/20261025.010423/build/Quakes/.venv/bin/python
  provisioning: not required
  return code: 0
  stderr:
    error: missing command
- PASS: clifound-runner-shape (FEATURE-CliFoundation.md)
  intent: cli_runner returns an exit code, stdout text, and stderr text, and agrees with main.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/Quakes/runs/20261025.010423/build/Quakes/.venv/bin/python
  provisioning: not required
  return code: 0
  stderr:
    error: unknown command: 'no-such-command-xyz'
- PASS: clifound-registry (FEATURE-CliFoundation.md)
  intent: The command registry is a dict that main consults for dispatch.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/Quakes/runs/20261025.010423/build/Quakes/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: clifound-launcher (FEATURE-CliFoundation.md)
  intent: The quakes launcher at the application root is executable and exits with the same code main returns.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/Quakes/runs/20261025.010423/build/Quakes/.venv/bin/python
  provisioning: not required
  return code: 0
  stderr:
    error: missing command
    
    error: missing command

## Build summary
The block is the CLI foundation only: the `cli` package, the in-process `cli_runner`, and the `quakes` launcher. The project scaffolding (pyproject, conftest, `bin/test.sh`, `.venv`) already exists, so I'll build on it and leave `sources/` alone.Now the test file. It follows the project's act-then-read-back rule, with one subprocess test for the launcher, as the CLI guidance allows.I left a convoluted fixture test and an unused import in that file. Cleaning them up before running anything.Next I'll make the launcher executable, then run the declared acceptance check (`bin/test.sh`) and the two foundation AC checks.All 23 tests pass. Last, I'll confirm the file changes are limited to the authorized paths and that `sources/` is untouched.RESULT: SUCCESS

FILES CHANGED:
- cli/__init__.py
- cli/errors.py
- cli/testing.py
- quakes
- tests/test_cli_foundation.py

SUMMARY:
- `cli/__init__.py`: `main(argv=None) -> int` returns exit codes and never calls `sys.exit`. With `argv=None` it reads `sys.argv[1:]`. It checks the `COMMANDS` registry: an empty or unknown command prints one line to stderr and returns 2. `COMMANDS` is a `dict`, initially empty.
- `cli/errors.py`: `UsageError` (exit 2) and `OperationalError` (exit 1).
- `cli/testing.py`: `cli_runner(*args) -> (exit_code, stdout, stderr)`, in-process, matching the Foundation Contract. The existing `conftest.py` fixture already imports it.
- `quakes`: executable `#!/usr/bin/env python3` launcher at the root. It puts its own directory on `sys.path`, calls `cli.main()`, and exits with the return value. It contains no report logic.
- `tests/test_cli_foundation.py`: 14 tests covering return types, usage and operational exit codes, registry behaviour, `cli_runner` capture (stdout empty, one stderr line on usage errors), and one subprocess test of the launcher's exit code.

Checks run:
- `sh bin/test.sh`: 23 passed, 0 failed (the 9 pre-existing foundation tests plus the 14 new ones), exit 0.
- `./quakes` with no args exits 2. `./quakes frobnicate` exits 2 with one stderr line.
- `sources/` is unchanged. `git status` shows only the new files above.
- `sources/run.sh` was not run, since it is the terminal story's gate.

Not done: `bin/run.sh` and `bin/run.ps1` from the stack's CLI guidance are not in this block's stories, so I left them out.

BLOCKERS:
- None for this block. Note: `core.fileMode` is `false` in this repo, so git will record `quakes` as 644 unless the executable bit is set in the index another way. The working-tree file is executable (`os.access` passes), which is what the acceptance check tests.

<blueprint-decisions>
[{"spec":"FEATURE-CliFoundation.md","severity":"Low","subject":"Dispatch skeleton behaviour for registered commands","decision":"The spec says main consults COMMANDS for dispatch but defines no parser yet. A registered command name is accepted and main returns 0 without calling its handler, since Parsed does not exist until the options story. COMMANDS is typed Callable[[Any], str] to avoid importing a module that is not built yet. The options story should replace the placeholder with real dispatch. Is that acceptable?"}]
</blueprint-decisions>
