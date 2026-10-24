# FEATURE: Help

| Field       | Value |
|-------------|-------|
| Version     | 20261024 V1 |
| Description | Provide help text for the program and for each command, shown by `--help`. |
| Depends On  | ARCHITECTURE.md, FEATURE-CliDispatch.md |
| Provides    | --help for quakes and each command, cli.help.wants_help, cli.help.help_text |
| Consumes    | quakes <command> dispatch, cli.options.COMMANDS |

## Purpose

Every command has help text so a user can discover its options. Help is requested output, not a
failure: it is written to standard output and exits `0` (decision Q-001).

## Interface

- `cli.help.help_text(command: str | None) -> str`: program-level help when `command` is `None`
  (listing every command), otherwise that command's synopsis and options. Each command's text is
  distinct.
- `cli.help.wants_help(argv: list[str]) -> bool`: `True` when `argv[0]` is `--help`, or when
  `argv[0]` is a known command and `--help` appears later in `argv`; otherwise `False`.

## Rules

1. `quakes --help` writes the program help and exits `0`.
2. `quakes <command> --help` for each of `fetch`, `summary`, `top`, `daily`, `regions`, `near` writes
   that command's help and exits `0`.
3. Help is written before any file is read or any other validation is attempted.
4. `quakes frobnicate --help` is not help: the unknown command is a usage error (exit `2`).
5. `main` checks `wants_help` first, as step 2 of the control flow in ARCHITECTURE.md.

## Programmatic Acceptance

=== AC help-program ===
Intent: quakes --help prints program help to standard output and exits 0.
Requires: executable=python3; scope=test

import os
import sys

sys.path.insert(0, os.getcwd())

from cli.help import help_text
from cli.testing import cli_runner

code, out, err = cli_runner("--help")
print(code, repr(err))
assert code == 0
assert out.strip() != ""
assert out == help_text(None)
=== END AC help-program ===

=== AC help-every-command ===
Intent: Every command has its own non-empty help text shown by --help with exit 0.
Requires: executable=python3; scope=test

import os
import sys

sys.path.insert(0, os.getcwd())

from cli.help import help_text
from cli.options import COMMANDS
from cli.testing import cli_runner

texts = {}
for command in COMMANDS:
    code, out, err = cli_runner(command, "--help")
    print(command, code, repr(err))
    assert code == 0
    assert out.strip() != ""
    assert out == help_text(command)
    texts[command] = out
assert len(set(texts.values())) == len(COMMANDS)
assert help_text(None) not in texts.values()
=== END AC help-every-command ===

=== AC help-wants-help ===
Intent: wants_help recognises --help for the program and for known commands only.
Requires: executable=python3; scope=test

import os
import sys

sys.path.insert(0, os.getcwd())

from cli.help import wants_help
from cli.options import COMMANDS

path = os.path.join("somewhere", "feed.geojson")
assert wants_help(["--help"]) is True
for command in COMMANDS:
    assert wants_help([command, "--help"]) is True
    assert wants_help([command, "--min-mag", "5", "--help"]) is True
assert wants_help(["summary", path]) is False
assert wants_help([]) is False
=== END AC help-wants-help ===

=== AC help-unknown-command ===
Intent: An unknown command with --help is a usage error, not help.
Requires: executable=python3; scope=test

import os
import sys

sys.path.insert(0, os.getcwd())

from cli.testing import cli_runner

code, out, err = cli_runner("frobnicate", "--help")
assert code == 2
assert out == ""
=== END AC help-unknown-command ===

## User Acceptance

- Commander reads the help text for each command and finds the options listed in the instructions understandable.

## Guardrails

- Help never reads a file or touches the network.
- `--help` is the only otherwise unlisted option that is accepted.
