# COMPASS: Quakes

## Compass

Build a command-line earthquake feed reporter, an executable named `quakes` at the application
root, as described in `sources/INSTRUCTIONS.md`. It downloads a period of the USGS event feed as
GeoJSON and writes five CSV reports from a saved file: summary, largest events, events per day,
events per region, and events within a haversine distance of a point.

Correctness is measured by `sources/run.sh`: 26 checks of exit code and standard output against a
frozen 44-event USGS snapshot. The goal is every check passing.

## Constraints

- Implement in Python 3.11 or newer with the standard library only.
- Provide an executable named `quakes` at the application root, invoked as `./quakes <command>`.
- Reading the file, filtering, computing each report, and formatting are separate, unit-tested
  functions.
- Tests stub the HTTP call; no test opens a network connection.
- Diagnostics go to standard error and are never compared.

## Guardrails

- Do not modify, rewrite, regenerate, or substitute any file under `sources/`.
- Do not read `sources/run.sh` or the snapshot from application code, and do not hardcode a
  report row, a count, or a distance. Every value comes from the file being read.

## Verification Protocol

| Story kind | Command | Asserts |
|---|---|---|
| Every behavioral story | `sh bin/test.sh` | exit `0` |
| Terminal story (once, last) | `sh sources/run.sh` | exit `0` |
