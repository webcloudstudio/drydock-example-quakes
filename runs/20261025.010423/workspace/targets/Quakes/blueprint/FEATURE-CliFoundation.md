# FEATURE: CLI Foundation

| Field       | Value |
|-------------|-------|
| Version     | 20261025 V1 |
| Description | Publishes the cli package, its main entry point, the cli_runner test helper, and the executable quakes launcher. |
| Depends On  | ARCHITECTURE.md |
| Provides    | cli.main, cli.testing.cli_runner, ./quakes |

## Purpose

This foundation stands up the command-line entry point everything else registers into. It delivers the `cli` package, `main(argv=None) -> int`, the in-process `cli_runner` helper, and an executable file named `quakes` at the application root.

## Interface

- `cli.main(argv: list[str] | None = None) -> int` — when `argv` is `None` it uses `sys.argv[1:]`. Returns the process exit code and never raises for `UsageError` or `OperationalError`.
- `cli.COMMANDS` — registry mapping command name to a handler `Callable[[Parsed], str]` returning the full standard-output text.
- `cli.testing.cli_runner(*args) -> tuple[int, str, str]` — runs `main` in-process with redirected stdout and stderr and returns `(exit_code, stdout, stderr)`.
- `conftest.py` exposes `cli_runner` as a pytest fixture.
- `./quakes` — executable file (mode with the execute bit set, `#!/usr/bin/env python3`) that puts its own directory on `sys.path`, calls `cli.main()`, and exits with the returned value.

Dispatch is a skeleton in this story; later stories register commands and argument parsing.

## Programmatic Acceptance

=== AC clifound-main-returns-int ===
Intent: main accepts an argv list and returns an integer exit code.

from cli import main

code = main([])
assert isinstance(code, int)
=== END AC clifound-main-returns-int ===

=== AC clifound-runner-shape ===
Intent: cli_runner returns an exit code, stdout text, and stderr text, and agrees with main.

from cli import main
from cli.testing import cli_runner

args = ["no-such-command-xyz"]
code, out, err = cli_runner(*args)
assert isinstance(code, int)
assert isinstance(out, str)
assert isinstance(err, str)
assert code == main(list(args))
=== END AC clifound-runner-shape ===

=== AC clifound-registry ===
Intent: The command registry is a dict that main consults for dispatch.

import cli

assert isinstance(cli.COMMANDS, dict)
=== END AC clifound-registry ===

=== AC clifound-launcher ===
Intent: The quakes launcher at the application root is executable and exits with the same code main returns.

import os
import subprocess
import sys

from cli import main

assert os.path.isfile("quakes")
assert os.access("quakes", os.X_OK)
argv = []
result = subprocess.run(["./quakes", *argv], capture_output=True, text=True)
print(result.stdout)
print(result.stderr, file=sys.stderr)
assert result.returncode == main(list(argv))
=== END AC clifound-launcher ===

## User Acceptance

- None.

## Guardrails

- The launcher contains no report logic; it only delegates to `cli.main`.
- Diagnostics go to standard error only.
