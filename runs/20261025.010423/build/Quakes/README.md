# drydock Quakes Uat Case

Drydock uat - Quakes is the get-data-and-report kit. The source is an original brief for a Python command-line tool that downloads the USGS earthquake feed as GeoJSON and writes five CSV reports from a saved file: summary, largest events, events per day, events per region, and events within a haversine distance of a point. The supplied grader, sources/run.sh, runs 26 checks of exit code and output against a frozen real USGS snapshot of the 44 magnitude 5+ events of 2025-01-01 to 2025-01-07 (non-ASCII place names, quoted commas, the Tibet aftershock cluster). The grader never uses the network; fetch is tested against a stub. Run with drydock uat Quakes. Source Repo: none, the brief is original to this kit; data from the USGS FDSN event service.

## Intent

Build a command-line earthquake feed reporter, an executable named `quakes` at the application
root, as described in `sources/INSTRUCTIONS.md`. It downloads a period of the USGS event feed as
GeoJSON and writes five CSV reports from a saved file: summary, largest events, events per day,
events per region, and events within a haversine distance of a point.

Correctness is measured by `sources/run.sh`: 26 checks of exit code and standard output against a
frozen 44-event USGS snapshot. The goal is every check passing.

## What It Does

This foundation stands up the command-line entry point everything else registers into. It delivers the `cli` package, `main(argv=None) -> int`, the in-process `cli_runner` helper, and an executable file named `quakes` at the application root.

`quakes daily [--min-mag <m>] <file>` reads a saved USGS GeoJSON file and reports how many events occurred on each UTC date and the strongest magnitude on that date.

Reports operate on `Event` records, not raw features. Extraction reads only the fields the reports
need and excludes every feature whose magnitude is `null`.

`cli/errors.py` defines `UsageError` (exit 2) and `OperationalError` (exit 1), both subclasses of a common `QuakesError(Exception)` carrying a one-line message. `cli.main` parses arguments, looks up the handler in `cli.COMMANDS`, and runs it.

Every report command starts by reading a saved feed file. `read_feed` returns the raw `features` list
and rejects anything that is not a GeoJSON FeatureCollection as an operational failure (exit 1).

`quakes fetch --start <YYYY-MM-DD> --end <YYYY-MM-DD> [--min-mag <m>] --out <file>` saves a period of the USGS event feed so the report commands can read it.

When the download cannot produce a valid GeoJSON FeatureCollection, `fetch` reports an operational failure and leaves the filesystem exactly as it found it.

`cli/formatting.py` holds the pure formatting functions every report uses.

`--min-mag <m>` applies to every report. `filter_events` is the single shared implementation, so
all reports share one inclusive rule: `mag >= m`.

`quakes near --lat <deg> --lon <deg> --radius <km> [--min-mag <m>] <file>` lists the events whose distance from a point is at most the radius.

`cli.options.parse_args(argv) -> Parsed` turns the argument list into a validated `Parsed` record or raises `cli.errors.UsageError`. `UsageError` is defined in `cli/errors.py` (see `FEATURE-ExitCodes.md`); this story creates the module with both exception classes if it does not exist yet. The dispatcher maps `UsageError` to exit code 2.

`quakes regions [--min-mag <m>] <file>` reports the most active regions in a saved USGS GeoJSON file.

`quakes summary [--min-mag <m>] <file>` reads a saved feed, applies the filter, and writes a
one-row CSV report to standard output.

The Compass requires reading, filtering, computing, and formatting to be separate unit-tested functions, with HTTP stubbed and no network connection in any test. `bin/test.sh` is the single entry point that runs that suite from the application root. It is the command named by the Compass Verification Protocol for every behavioral story.

`quakes top [--min-mag <m>] [--n <count>] <file>` writes the `--n` largest events as CSV.

## Stack

Python

## Setup and Running

**Before first run:**

- Confirm the repository has the expected remote with `git remote -v`; add `origin` if the startup guard requires it.
- Run `git status --short` and commit or intentionally stash local changes before deployment-oriented runs.

**Install dependencies:**

```bash
uv sync
```

## Verification

```bash
bash bin/test.sh
```

## Next Steps

- Complete the first-run checks above.
- Run `bash bin/test.sh` before making release or deployment changes.
