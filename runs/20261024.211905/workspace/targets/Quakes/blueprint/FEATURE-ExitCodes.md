# FEATURE: Exit Codes

| Field       | Value |
|-------------|-------|
| Version     | 20261024 V1 |
| Description | Map outcomes to exit codes 0, 1 and 2 and guarantee empty standard output with one standard-error line on failure. |
| Depends On  | ARCHITECTURE.md, FEATURE-CliDispatch.md |
| Provides    | exit code contract |
| Consumes    | quakes <command> dispatch, cli.errors.UsageError, cli.errors.OperationalFailure, cli.commands.dispatch |

## Purpose

`cli.main` turns the result of parsing and dispatching into a process exit code and guarantees that a
failing command writes nothing to standard output.

## Rules

| Code | Meaning |
|---|---|
| `0` | Success, including a report with no matching events. The handler text is written to standard output exactly once. |
| `1` | Operational failure (`OperationalFailure`): file unreadable or not a FeatureCollection; fetch network or HTTP failure. |
| `2` | Usage error (`UsageError`): any malformed command line. |

- `main` writes the handler's text to standard output only after the handler returned, so a failing
  command has written nothing to standard output.
- A failure writes exactly one diagnostic line to standard error (the exception message on a single
  line, no traceback). Standard error is never compared.
- `main` configures standard output as UTF-8 with `\n` newlines when the stream supports
  `reconfigure`, and writes the text without adding or altering line endings.

## Programmatic Acceptance

=== AC exit-success-writes-text ===
Intent: A handler that returns text yields exit 0 and exactly that text on standard output.
Requires: executable=python3; scope=test

import os
import sys

sys.path.insert(0, os.getcwd())

from cli import commands
from cli.testing import cli_runner

path = os.path.join("somewhere", "feed.geojson")
text = "col_a,col_b\nvalue,1\n"
commands.HANDLERS["summary"] = lambda invocation: text
code, out, err = cli_runner("summary", path)
print(code, repr(out), repr(err))
assert code == 0
assert out == text
=== END AC exit-success-writes-text ===

=== AC exit-empty-result-is-success ===
Intent: A handler that returns no text still exits 0 with empty standard output.
Requires: executable=python3; scope=test

import os
import sys

sys.path.insert(0, os.getcwd())

from cli import commands
from cli.testing import cli_runner

path = os.path.join("somewhere", "feed.geojson")
commands.HANDLERS["daily"] = lambda invocation: ""
code, out, err = cli_runner("daily", path)
assert code == 0
assert out == ""
=== END AC exit-empty-result-is-success ===

=== AC exit-operational-failure ===
Intent: An OperationalFailure from a handler gives exit 1, empty standard output and a diagnostic on standard error.
Requires: executable=python3; scope=test

import os
import sys

sys.path.insert(0, os.getcwd())

from cli import commands
from cli.errors import OperationalFailure
from cli.testing import cli_runner

path = os.path.join("somewhere", "feed.geojson")

def failing(invocation):
    raise OperationalFailure("cannot read the feed")

commands.HANDLERS["regions"] = failing
code, out, err = cli_runner("regions", path)
print(code, repr(out), repr(err))
assert code == 1
assert out == ""
assert err.strip() != ""
assert len(err.strip().splitlines()) == 1
=== END AC exit-operational-failure ===

=== AC exit-usage-error-from-handler ===
Intent: A UsageError raised by a handler gives exit 2 and empty standard output.
Requires: executable=python3; scope=test

import os
import sys

sys.path.insert(0, os.getcwd())

from cli import commands
from cli.errors import UsageError
from cli.testing import cli_runner

path = os.path.join("somewhere", "feed.geojson")

def rejecting(invocation):
    raise UsageError("bad value")

commands.HANDLERS["top"] = rejecting
code, out, err = cli_runner("top", path)
assert code == 2
assert out == ""
assert len(err.strip().splitlines()) == 1
=== END AC exit-usage-error-from-handler ===

=== AC exit-parse-usage-errors ===
Intent: Malformed command lines exit 2 with empty standard output and one diagnostic line.
Requires: executable=python3; scope=test

import os
import sys

sys.path.insert(0, os.getcwd())

from cli.testing import cli_runner

path = os.path.join("somewhere", "feed.geojson")
cases = [
    [],
    ["frobnicate", path],
    ["summary"],
    ["summary", "--n", "3", path],
    ["summary", "--min-mag", "big", path],
    ["top", "--n", "0", path],
]
bad = []
for argv in cases:
    code, out, err = cli_runner(*argv)
    if code != 2 or out != "" or len(err.strip().splitlines()) != 1:
        bad.append((argv, code, out, err))
print(bad)
assert bad == []
=== END AC exit-parse-usage-errors ===

## User Acceptance

- None.

## Guardrails

- A failing command never writes to standard output.
- Standard error carries one diagnostic line and no traceback; it is never compared.
- Exit code `0` is used for success including a report with no matching events.
