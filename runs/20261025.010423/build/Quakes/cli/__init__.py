"""Command-line entry point for quakes.

`main` parses the invocation, runs the registered handler, and returns an exit code. It never calls
`sys.exit`; the `quakes` launcher is the only caller that turns the return value into a process exit.
A failing command writes nothing to standard output and exactly one line to standard error.
"""

import sys
from collections.abc import Callable

from cli.errors import QuakesError, UsageError
from cli.fetch import fetch_command
from cli.formatting import write_stdout
from cli.options import Parsed, parse_args
from cli.reports import daily_command, near_command, regions_command, summary_command, top_command

# Command name -> handler. A handler takes the parsed arguments and returns the full standard-output
# text; `main` writes that text only after the handler succeeds.
COMMANDS: dict[str, Callable[[Parsed], str]] = {
    "fetch": fetch_command,
    "summary": summary_command,
    "top": top_command,
    "daily": daily_command,
    "regions": regions_command,
    "near": near_command,
}


def main(argv: list[str] | None = None) -> int:
    """Run one invocation and return its exit code: 0 success, 1 operational failure, 2 usage error."""
    if argv is None:
        argv = sys.argv[1:]
    try:
        parsed = parse_args(argv)
        handler = COMMANDS.get(parsed.command)
        if handler is None:
            raise UsageError(f"command not available: {parsed.command!r}")
        text = handler(parsed)
    except QuakesError as exc:
        message = " ".join(str(exc).split()) or type(exc).__name__
        print(f"error: {message}", file=sys.stderr)
        return exc.exit_code
    write_stdout(text)
    return 0
