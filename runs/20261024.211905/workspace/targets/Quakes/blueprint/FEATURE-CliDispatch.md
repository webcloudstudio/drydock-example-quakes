# FEATURE: Cli Dispatch

| Field       | Value |
|-------------|-------|
| Version     | 20261024 V1 |
| Description | Parse the command and its options in any order with the file last, and dispatch to the registered command handler. |
| Depends On  | ARCHITECTURE.md |
| Provides    | quakes <command> dispatch, cli.options.parse_args, cli.options.COMMANDS, cli.options.Invocation, cli.commands.HANDLERS, cli.commands.dispatch |
| Consumes    | cli.main, cli.errors.UsageError, cli.errors.OperationalFailure |

## Purpose

`quakes <command> [options] [<file>]`. The command comes first, options follow in any order, and
the file is last. Any malformed command line is a usage error. This feature parses and validates the
shape of the command line and routes a parsed invocation to a handler; reports, validation of `near`
ranges, and exit-code mapping belong to other features.

## Trigger

Every invocation of `quakes`.

## Interface

- `cli.options.COMMANDS`: tuple `("fetch", "summary", "top", "daily", "regions", "near")`.
- `cli.options.Invocation`: frozen dataclass with `command: str`, `options: dict[str, str]`, and
  `file: str | None`. `options` is keyed by the option name without its leading `--` (`min-mag`,
  `n`, `lat`, `lon`, `radius`, `start`, `end`, `out`) and holds the value text exactly as given.
  An option that was not given is absent from the dict; the owning command applies defaults
  (`n` = 10, fetch `min-mag` = 2.5).
- `cli.options.parse_args(argv: list[str]) -> Invocation`, raising `cli.errors.UsageError`.
- `cli.commands.HANDLERS`: plain `dict[str, Callable[[Invocation], str]]`; each handler returns the
  complete standard-output text.
- `cli.commands.dispatch(invocation) -> str`: calls `HANDLERS[invocation.command]`; when no handler is
  registered it raises `cli.errors.OperationalFailure`.

## Rules

1. `argv[0]` is the command; an unknown command or an empty `argv` is a usage error.
2. The token after an option name is always that option's value, even when it begins with `-`
   (so `--lat -5.25` is valid). A missing value is a usage error.
3. Options accepted per command:

   | Command | Options | Positional file |
   |---|---|---|
   | `fetch` | `--start`, `--end`, `--out` (all required), `--min-mag` | none (an extra positional is a usage error) |
   | `summary`, `daily`, `regions` | `--min-mag` | exactly one, last |
   | `top` | `--min-mag`, `--n` | exactly one, last |
   | `near` | `--lat`, `--lon`, `--radius`, `--min-mag` | exactly one, last |

4. Any other option, or an option the command does not list, is a usage error.
5. An option given more than once is a usage error.
6. `--min-mag`, `--lat`, `--lon` and `--radius` values must match `-?[0-9]+(\.[0-9]+)?`. `--n` must be
   a positive integer (`0`, negatives, decimals and text are usage errors). `--start` and `--end`
   must have the shape `YYYY-MM-DD`.
7. A report command with no file, or with more than one file, is a usage error.
8. For `near`, the presence of `--lat`, `--lon`, `--radius` and the range checks belong to
   FEATURE-NearValidation.md; the parser only accepts them.

## Programmatic Acceptance

=== AC dispatch-option-order ===
Intent: Options may appear in any order and parse to the same invocation with the file last.
Requires: executable=python3; scope=test

import os
import sys

sys.path.insert(0, os.getcwd())

from cli.options import parse_args

path = os.path.join("somewhere", "feed.geojson")
mag = "5.5"
count = "3"
first = parse_args(["top", "--min-mag", mag, "--n", count, path])
second = parse_args(["top", "--n", count, "--min-mag", mag, path])
assert first.command == "top"
assert first.options == second.options
assert first.options["min-mag"] == mag
assert first.options["n"] == count
assert first.file == path
assert second.file == path
=== END AC dispatch-option-order ===

=== AC dispatch-negative-values ===
Intent: A value beginning with a minus sign is read as the option's value, not as an option.
Requires: executable=python3; scope=test

import os
import sys

sys.path.insert(0, os.getcwd())

from cli.options import parse_args

path = os.path.join("somewhere", "feed.geojson")
lat = "-5.25"
lon = "-170"
radius = "100"
inv = parse_args(["near", "--lat", lat, "--lon", lon, "--radius", radius, path])
assert inv.command == "near"
assert inv.options["lat"] == lat
assert inv.options["lon"] == lon
assert inv.options["radius"] == radius
assert inv.file == path
=== END AC dispatch-negative-values ===

=== AC dispatch-every-command-parses ===
Intent: Each report command parses with a file, and fetch parses with its required options and no file.
Requires: executable=python3; scope=test

import os
import sys

sys.path.insert(0, os.getcwd())

from cli.options import COMMANDS, parse_args

path = os.path.join("somewhere", "feed.geojson")
start = "2025-01-01"
end = "2025-01-08"
out = os.path.join("somewhere", "out.geojson")
for command in ("summary", "daily", "regions", "top"):
    assert command in COMMANDS
    inv = parse_args([command, path])
    assert inv.command == command
    assert inv.file == path
assert "near" in COMMANDS
assert "fetch" in COMMANDS
fetch = parse_args(["fetch", "--end", end, "--start", start, "--out", out, "--min-mag", "4.5"])
assert fetch.command == "fetch"
assert fetch.file is None
assert fetch.options["start"] == start
assert fetch.options["end"] == end
assert fetch.options["out"] == out
assert fetch.options["min-mag"] == "4.5"
assert len(COMMANDS) == 6
=== END AC dispatch-every-command-parses ===

=== AC dispatch-usage-errors ===
Intent: Every malformed command line raises UsageError.
Requires: executable=python3; scope=test

import os
import sys

sys.path.insert(0, os.getcwd())

from cli.errors import UsageError
from cli.options import parse_args

path = os.path.join("somewhere", "feed.geojson")
start = "2025-01-01"
end = "2025-01-08"
out = os.path.join("somewhere", "out.geojson")
bad = [
    [],
    ["frobnicate", path],
    ["summary"],
    ["summary", path, path],
    ["summary", "--n", "3", path],
    ["summary", "--bogus", "1", path],
    ["summary", "--min-mag", "big", path],
    ["summary", "--min-mag", ".5", path],
    ["summary", "--min-mag"],
    ["summary", "--min-mag", "5", "--min-mag", "6", path],
    ["top", "--n", "0", path],
    ["top", "--n", "-1", path],
    ["top", "--n", "2.5", path],
    ["top", "--n", "many", path],
    ["daily", "--lat", "1", path],
    ["fetch", "--start", start, "--end", end],
    ["fetch", "--start", start, "--out", out],
    ["fetch", "--end", end, "--out", out],
    ["fetch", "--start", start, "--end", end, "--out", out, path],
    ["fetch", "--start", "yesterday", "--end", end, "--out", out],
]
accepted = []
for argv in bad:
    try:
        parse_args(list(argv))
    except UsageError:
        continue
    accepted.append(argv)
print(f"{len(bad) - len(accepted)} rejected, {len(accepted)} accepted")
assert accepted == []
=== END AC dispatch-usage-errors ===

=== AC dispatch-routes-to-handler ===
Intent: dispatch calls the registered handler with the invocation and returns its text unchanged.
Requires: executable=python3; scope=test

import os
import sys

sys.path.insert(0, os.getcwd())

from cli import commands
from cli.options import parse_args

path = os.path.join("somewhere", "feed.geojson")
text = "col_a,col_b\nvalue,1\n"
seen = []

def fake(invocation):
    seen.append(invocation)
    return text

commands.HANDLERS["summary"] = fake
inv = parse_args(["summary", path])
assert commands.dispatch(inv) == text
assert len(seen) == 1
assert seen[0] is inv
=== END AC dispatch-routes-to-handler ===

=== AC dispatch-missing-handler ===
Intent: Dispatching a command with no registered handler raises OperationalFailure.
Requires: executable=python3; scope=test

import os
import sys

sys.path.insert(0, os.getcwd())

from cli import commands
from cli.errors import OperationalFailure
from cli.options import parse_args

path = os.path.join("somewhere", "feed.geojson")
commands.HANDLERS.pop("daily", None)
inv = parse_args(["daily", path])
try:
    commands.dispatch(inv)
except OperationalFailure:
    pass
else:
    raise AssertionError("dispatch of an unregistered command did not raise")
=== END AC dispatch-missing-handler ===

## User Acceptance

- None.

## Guardrails

- An option the command does not list is a usage error, never ignored.
- The parser never opens the file; reading it belongs to the feed reader.
- Handlers return text; only `main` writes to standard output.
