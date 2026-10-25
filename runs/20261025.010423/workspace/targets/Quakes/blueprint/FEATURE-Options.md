# FEATURE: Options

| Field       | Value |
|-------------|-------|
| Version     | 20261025 V1 |
| Description | Parses and validates the command, its options, and the file argument, raising a usage error for any malformed invocation. |
| Depends On  | FEATURE-CliFoundation.md |
| Provides    | parse_args |

## Purpose

`cli.options.parse_args(argv) -> Parsed` turns the argument list into a validated `Parsed` record or raises `cli.errors.UsageError`. `UsageError` is defined in `cli/errors.py` (see `FEATURE-ExitCodes.md`); this story creates the module with both exception classes if it does not exist yet. The dispatcher maps `UsageError` to exit code 2.

## Grammar

```text
quakes fetch --start <YYYY-MM-DD> --end <YYYY-MM-DD> [--min-mag <m>] --out <file>
quakes summary [--min-mag <m>] <file>
quakes top [--min-mag <m>] [--n <count>] <file>
quakes daily [--min-mag <m>] <file>
quakes regions [--min-mag <m>] <file>
quakes near --lat <deg> --lon <deg> --radius <km> [--min-mag <m>] <file>
```

- The command is the first argument. Options follow in any order; the file (for report commands) is last.
- Each command accepts only its listed options; any other option is a `UsageError`.
- `<m>`, `<deg>`, `<km>` match `-?[0-9]+(\.[0-9]+)?` and a value may begin with `-`. Anything else is malformed.
- `<count>` is a positive integer (digits only, greater than zero), default `10`.
- `--lat` is within -90 to 90, `--lon` within -180 to 180, `--radius` greater than zero. `near` requires all three.
- `fetch` requires `--start`, `--end`, `--out`; dates match `YYYY-MM-DD`. `fetch` takes no positional file. `--min-mag` defaults to `2.5` for `fetch`; for report commands it is `None` when omitted.
- A missing command, unknown command, missing option value, missing file, extra positional argument, or repeated option is a `UsageError` (decision Q-001).
- `parse_args` does not touch the file system.

## Programmatic Acceptance

=== AC options-valid-summary ===
Intent: A valid summary invocation parses into the expected command, filter, and file.

from cli.options import parse_args

path = "quakes-file.geojson"
parsed = parse_args(["summary", "--min-mag", "5.5", path])
assert parsed.command == "summary"
assert parsed.min_mag == 5.5
assert parsed.file == path
=== END AC options-valid-summary ===

=== AC options-defaults ===
Intent: top defaults n to 10, reports default min_mag to None, and fetch defaults min_mag to 2.5.

from cli.options import parse_args

path = "quakes-file.geojson"
top = parse_args(["top", path])
assert top.n == 10
assert top.min_mag is None
fetch = parse_args(["fetch", "--start", "2025-01-01", "--end", "2025-01-08", "--out", path])
assert fetch.min_mag == 2.5
=== END AC options-defaults ===

=== AC options-any-order ===
Intent: Options may appear in any order and produce the same parsed values.

from cli.options import parse_args

path = "quakes-file.geojson"
a = parse_args(["top", "--n", "3", "--min-mag", "5.1", path])
b = parse_args(["top", "--min-mag", "5.1", "--n", "3", path])
assert a.n == b.n == 3
assert a.min_mag == b.min_mag == 5.1
assert a.file == b.file == path
=== END AC options-any-order ===

=== AC options-near-valid ===
Intent: near parses its three required options, accepting the range boundaries and negative decimals.

from cli.options import parse_args

path = "quakes-file.geojson"
parsed = parse_args(["near", "--lat", "90", "--lon", "-180", "--radius", "0.5", path])
assert parsed.lat == 90.0
assert parsed.lon == -180.0
assert parsed.radius == 0.5
negative = parse_args(["summary", "--min-mag", "-1", path])
assert negative.min_mag == -1.0
=== END AC options-near-valid ===

=== AC options-fetch-valid ===
Intent: fetch parses start, end, out, and an explicit min-mag.

from cli.options import parse_args

start, end, out = "2025-01-01", "2025-01-08", "feed.geojson"
parsed = parse_args(["fetch", "--start", start, "--end", end, "--min-mag", "5", "--out", out])
assert parsed.command == "fetch"
assert parsed.start == start
assert parsed.end == end
assert parsed.out == out
assert parsed.min_mag == 5.0
=== END AC options-fetch-valid ===

=== AC options-usage-errors ===
Intent: Every malformed invocation raises UsageError.

from cli.errors import UsageError
from cli.options import parse_args

f = "quakes-file.geojson"
bad = [
    [],
    ["frobnicate", f],
    ["near", "--lat", "27.72", "--lon", "85.32", f],
    ["near", "--lat", "95", "--lon", "0", "--radius", "10", f],
    ["near", "--lat", "0", "--lon", "181", "--radius", "10", f],
    ["near", "--lat", "0", "--lon", "0", "--radius", "0", f],
    ["top", "--n", "0", f],
    ["top", "--n", "2.5", f],
    ["summary", "--min-mag", "big", f],
    ["summary", "--min-mag", "5.", f],
    ["summary", "--min-mag", ".5", f],
    ["summary", "--n", "3", f],
    ["summary"],
    ["summary", f, f],
    ["summary", "--min-mag", f],
    ["summary", "--min-mag", "5", "--min-mag", "6", f],
    ["fetch", "--start", "2025-01-01", "--end", "2025-01-08"],
    ["fetch", "--start", "2025-01-01", "--out", f],
    ["fetch", "--start", "2025-01-01", "--end", "2025-01-08", "--out", f, f],
    ["fetch", "--start", "yesterday", "--end", "2025-01-08", "--out", f],
]
for argv in bad:
    try:
        parse_args(list(argv))
    except UsageError:
        continue
    raise AssertionError(f"no UsageError for {argv}")
=== END AC options-usage-errors ===

=== AC options-exit-two ===
Intent: Through the executable entry point, an unknown command and a missing command both exit 2.

from cli.testing import cli_runner

code_unknown, out_unknown, _ = cli_runner("frobnicate", "quakes-file.geojson")
code_none, out_none, _ = cli_runner()
assert code_unknown == 2
assert code_none == 2
assert out_unknown == ""
assert out_none == ""
=== END AC options-exit-two ===

## User Acceptance

- None.

## Guardrails

- Usage errors never print to standard output; the parser raises `UsageError` rather than using argparse's default error behavior.
- An option the command does not list is always a usage error.
