# Quakes

A Drydock UAT kit that builds a Python earthquake feed reporter: fetch data, then process it. The
brief is original to this kit. Complexity: 2 of 5, about 5 to 6 stories.

| Path | Role |
|---|---|
| `sources/INSTRUCTIONS.md` | The specification imported into the Target. |
| `sources/quakes_2025-01-01_07.geojson` | Frozen USGS snapshot: 44 events, M5.0+, 2025-01-01 to 2025-01-07 UTC, one feature per line. |
| `bin/run.sh` | The grader. Staged into the build as `sources/run.sh`; `acceptance.full` runs it. |
| `tools/` | `trim_quakes.py` (froze the snapshot from the live feed) and `quakes.py` (the reference that produced the answers). Not imported. |
| `inputs/` | Frozen `SEA_TRIALS.md`, `TECHNOLOGY_STACK.md`, `COMPASS.md`, `METADATA.md`. |

## Grading

`bin/run.sh [APP]` runs `APP/quakes` (default: the current directory) and makes 26 checks of exit
code and standard output. It never runs `fetch` and uses no network.

| Group | Checks |
|---|---|
| A | `summary`, `top`, `daily`, `regions` over the snapshot |
| B | `--n` and `--min-mag` |
| C | `near`: Kathmandu (the Tibet aftershock cluster), Tokyo, Addis Ababa with a magnitude filter, and an empty result |
| D | a filter that matches nothing |
| E | missing file, non-JSON file, a Feature instead of a FeatureCollection |
| U | usage errors |

## Data traps

Real data, not synthetic: places with non-ASCII characters (`Āwash`, `‘Ohonua`), places with
commas that must be quoted, regions that are whole place strings (`Balleny Islands region`),
lowercase regions that sort last by byte value, and magnitudes stored as `5` that print as `5.0`.
No mean, depth, or distance in the exam lands on a rounding tie.

The snapshot was taken from the live feed on 2026-10-22. USGS revises events, so a fresh `fetch`
of the same window can differ; the grader reads only the frozen file.
