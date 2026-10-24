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

Report the number of events and maximum magnitude for each UTC date in the input file.

Fetch earthquake events from the USGS FDSN event service for a requested date range and save the response as GeoJSON.

The `near` command lists events within a radius of a latitude and longitude. It reads a saved GeoJSON FeatureCollection and writes a CSV report to standard output.

Report counts and maximum magnitudes grouped by the source-defined region of each event.

Summarize the events in a saved GeoJSON file, optionally filtering by minimum magnitude.

List up to the requested number of largest events, optionally filtered by minimum magnitude.

The project provides a POSIX-compatible `bin/test.sh` that runs the project's pytest suite from the application root and exits zero only when every test passes. The suite covers each report command, behavior-changing options, region and distance rules, fetch through a stubbed HTTP response, and exit codes. Tests use files written by the tests and never open a network connection.

After all command capabilities are implemented, run the supplied grader from the application root as the final conformance check.

## Stack

Python

## Verification

```bash
bash bin/test.sh
```

## Next Steps

- Complete the first-run checks above.
- Run `bash bin/test.sh` before making release or deployment changes.
