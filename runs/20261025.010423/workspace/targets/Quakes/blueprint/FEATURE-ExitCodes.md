# FEATURE: Exit Codes

| Field       | Value |
|-------------|-------|
| Version     | 20261025 V1 |
| Description | Maps usage and operational failures to exit codes 2 and 1 with empty standard output and one standard-error line. |
| Depends On  | FEATURE-Options.md |
| Provides    | UsageError, OperationalError, exit code mapping |

## Purpose

`cli/errors.py` defines `UsageError` (exit 2) and `OperationalError` (exit 1), both subclasses of a common `QuakesError(Exception)` carrying a one-line message. `cli.main` parses arguments, looks up the handler in `cli.COMMANDS`, and runs it.

## Behavior

- Success, including a report with no matching events, returns `0` after writing the handler's returned text to standard output.
- `UsageError` returns `2`; `OperationalError` returns `1`.
- On either failure `main` writes nothing to standard output and exactly one diagnostic line (ending in a single newline, no embedded newline) to standard error.
- Handlers return their complete output text and write nothing themselves, so a failure leaves standard output empty.
- An unexpected exception is not mapped; only the two named errors are.

## Programmatic Acceptance

=== AC exit-usage-code ===
Intent: A usage error returns exit code 2 with empty stdout and a single stderr line.

from cli.testing import cli_runner

code, out, err = cli_runner("frobnicate", "quakes-file.geojson")
assert code == 2
assert out == ""
assert len(err.splitlines()) == 1
=== END AC exit-usage-code ===

=== AC exit-operational-code ===
Intent: An OperationalError raised by a handler returns exit code 1 with empty stdout and a single stderr line.

import cli
from cli.errors import OperationalError
from cli.testing import cli_runner

def failing(parsed):
    raise OperationalError("cannot read the file")

original = cli.COMMANDS.get("summary")
cli.COMMANDS["summary"] = failing
try:
    code, out, err = cli_runner("summary", "quakes-file.geojson")
finally:
    if original is None:
        del cli.COMMANDS["summary"]
    else:
        cli.COMMANDS["summary"] = original
assert code == 1
assert out == ""
assert len(err.splitlines()) == 1
=== END AC exit-operational-code ===

=== AC exit-success-code ===
Intent: A handler that returns text yields exit 0 and that exact text on stdout, and an empty result is still success.

import cli
from cli.testing import cli_runner

text = "header\nrow\n"
original = cli.COMMANDS.get("daily")
cli.COMMANDS["daily"] = lambda parsed: text
try:
    code, out, err = cli_runner("daily", "quakes-file.geojson")
    cli.COMMANDS["daily"] = lambda parsed: ""
    empty_code, empty_out, _ = cli_runner("daily", "quakes-file.geojson")
finally:
    if original is None:
        del cli.COMMANDS["daily"]
    else:
        cli.COMMANDS["daily"] = original
assert code == 0
assert out == text
assert empty_code == 0
assert empty_out == ""
=== END AC exit-success-code ===

=== AC exit-error-classes ===
Intent: UsageError and OperationalError are distinct exception classes.

from cli.errors import OperationalError, UsageError

assert issubclass(UsageError, Exception)
assert issubclass(OperationalError, Exception)
assert not issubclass(UsageError, OperationalError)
assert not issubclass(OperationalError, UsageError)
=== END AC exit-error-classes ===

=== AC exit-launcher-status ===
Intent: The quakes executable surfaces exit 2 for a usage error with empty stdout.

import subprocess
import sys

result = subprocess.run(["./quakes", "frobnicate", "quakes-file.geojson"], capture_output=True, text=True)
print(result.stdout)
print(result.stderr, file=sys.stderr)
assert result.returncode == 2
assert result.stdout == ""
=== END AC exit-launcher-status ===

## User Acceptance

- None.

## Guardrails

- A failing command never writes to standard output.
- Standard error carries exactly one diagnostic line on failure; its wording is not part of the contract.
