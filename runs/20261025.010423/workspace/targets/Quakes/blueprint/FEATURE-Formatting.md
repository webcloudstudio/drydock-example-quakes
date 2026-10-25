# FEATURE: Formatting

| Field       | Value |
|-------------|-------|
| Version     | 20261025 V1 |
| Description | Formats UTC times, magnitudes, depths, distances, and CSV output for every report. |
| Depends On  | ARCHITECTURE.md |
| Provides    | format_time, format_mag, format_mean, format_decimal, write_csv |

## Purpose

`cli/formatting.py` holds the pure formatting functions every report uses.

## Interface

- `format_time(ms: int | float) -> str` — epoch milliseconds to UTC `YYYY-MM-DDTHH:MM:SSZ`, truncated (floored) to whole seconds. The date is the first 10 characters.
- `format_mag(x) -> str` — one decimal place (`5.0`, `7.1`).
- `format_mean(x) -> str` — two decimal places, rounded half up.
- `format_decimal(x) -> str` — one decimal place, rounded half up (used for `depth_km` and `distance_km`).
- `render_csv(rows) -> str` — rows (lists of strings) rendered with Python's `csv` module, `lineterminator="\n"`, so a field containing a comma is quoted.
- `write_csv(rows, stream=None)` — writes `render_csv(rows)` to `stream`; when `stream` is `None` it writes UTF-8 to standard output (the underlying binary buffer when present, otherwise `sys.stdout.write`).

Rounding uses `decimal.Decimal(repr(x))` quantized with `ROUND_HALF_UP` (decision Q-002); built-in `round()` is not used. Output is UTF-8 and non-ASCII place names are written unescaped.

## Programmatic Acceptance

=== AC fmt-time ===
Intent: format_time yields a UTC timestamp truncated to whole seconds whose first 10 characters are the date.

from datetime import datetime, timezone

from cli.formatting import format_time

seconds = 1735706358
ms = seconds * 1000 + 999
text = format_time(ms)
parsed = datetime.strptime(text, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
assert int(parsed.timestamp()) == seconds
assert len(text) == 20
assert text[:10] == parsed.strftime("%Y-%m-%d")
assert format_time(seconds * 1000) == text
=== END AC fmt-time ===

=== AC fmt-magnitude ===
Intent: Magnitudes are written with exactly one decimal place.

from cli.formatting import format_mag

assert format_mag(5) == "5.0"
assert format_mag(7.1) == "7.1"
assert format_mag(5.0) == "5.0"
=== END AC fmt-magnitude ===

=== AC fmt-mean-half-up ===
Intent: mean_mag has two decimals and rounds exact halves up.

from cli.formatting import format_mean

assert format_mean(5.3) == "5.30"
assert format_mean(5.125) == "5.13"
assert format_mean(5.135) == "5.14"
assert format_mean(5) == "5.00"
=== END AC fmt-mean-half-up ===

=== AC fmt-decimal-half-up ===
Intent: depth and distance have one decimal and round exact halves up.

from cli.formatting import format_decimal

assert format_decimal(0.25) == "0.3"
assert format_decimal(10) == "10.0"
assert format_decimal(216.25) == "216.3"
assert format_decimal(46) == "46.0"
=== END AC fmt-decimal-half-up ===

=== AC fmt-csv-roundtrip ===
Intent: render_csv round-trips fields containing commas and non-ASCII characters through the csv parser with \n line endings.

import csv
import io

from cli.formatting import render_csv

place = "\u0100wash, Ethiopia"
rows = [["time", "place"], ["2025-01-01T00:00:00Z", place], ["a", "plain"]]
text = render_csv(rows)
parsed = list(csv.reader(io.StringIO(text, newline="")))
assert parsed == rows
assert text.count("\n") == len(rows)
assert text.endswith("\n")
=== END AC fmt-csv-roundtrip ===

=== AC fmt-write-csv ===
Intent: write_csv writes the rendered CSV to the given stream and to standard output by default.

import contextlib
import io

from cli.formatting import render_csv, write_csv

rows = [["h1", "h2"], ["x", "y, z"]]
stream = io.StringIO()
write_csv(rows, stream)
assert stream.getvalue() == render_csv(rows)

captured = io.StringIO()
with contextlib.redirect_stdout(captured):
    write_csv(rows)
assert captured.getvalue() == render_csv(rows)
=== END AC fmt-write-csv ===

## User Acceptance

- None.

## Guardrails

- CSV is always produced with Python's `csv` module, never by string concatenation.
- Rounding never uses built-in `round()`.
