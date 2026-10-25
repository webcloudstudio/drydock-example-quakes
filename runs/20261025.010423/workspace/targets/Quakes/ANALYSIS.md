# Blueprint Analysis: drydock Quakes Uat Case

## Commander Expectations

- assert the product downloads the USGS earthquake feed as GeoJSON and saves it unchanged to a file
- assert the product reports on a saved earthquake file through five report commands: summary, top, daily, regions, and near
- assert every report honors the `--min-mag` filter
- assert the product runs as a standard-library-only Python 3.11+ command-line tool named `quakes`
- assert the supplied grader `sources/run.sh` passes against the completed application

## Crew

| Crew | Charge |
|---|---|
| Commander | Defines intent and decides what done means. |
| Team Lead | Confirms epic completeness and stakeholder expectations. |
| Planning Crew | Authors atomic specifications and the ordered Manifest. |
| Shipyard Crew | Builds the tickets without synchronous Commander access. |

## Story List

### Feature: Feed Fetch

| ID | Story | High-level AC |
|---|---|---|
| FETCH-001 | Fetch a USGS date range to a GeoJSON file | Request the USGS FDSN query in GeoJSON with the given dates and `--min-mag` (default 2.5, ordered by time ascending); write the response body unchanged to `--out`; print `fetched,<count>` |
| FETCH-002 | Fail fetch without writing on network, HTTP, or non-FeatureCollection failure | On a network error, a non-200 status, or a body that is not a GeoJSON FeatureCollection, exit 1 and write no file |

### Feature: Feed Reading and Validation

| ID | Story | High-level AC |
|---|---|---|
| READ-001 | Read and validate a saved GeoJSON feed file | Accept a FeatureCollection with a `features` array; exit 1 when the file is unreadable, not JSON, or not an object with `"type": "FeatureCollection"` and `features` |
| READ-002 | Read event fields and exclude null-magnitude events | Read `id`, `properties.mag`, `properties.place`, `properties.time`, `properties.tsunami`, and `geometry.coordinates`; exclude features whose `mag` is null from every report |
| READ-003 | Apply the `--min-mag` filter across all reports | Keep only events with `mag >= m` in every report command |

### Feature: Summary Report

| ID | Story | High-level AC |
|---|---|---|
| SUM-001 | Summarize events with count, time span, magnitude range, mean, and tsunami count | Output header `events,first,last,min_mag,max_mag,mean_mag,tsunami`; mean rounded half-up to two decimals; with no events output `0,,,,,,0` |

### Feature: Top Events Report

| ID | Story | High-level AC |
|---|---|---|
| TOP-001 | List the largest events with `--n` count | Output `time,mag,depth_km,place,id` sorted by magnitude descending then time ascending; `--n` defaults to 10 and must be a positive integer |

### Feature: Daily Report

| ID | Story | High-level AC |
|---|---|---|
| DAY-001 | Report event count and maximum magnitude per UTC date | Output `date,events,max_mag` per date with events, ascending, followed by `TOTAL,<events>,<max_mag>`; with no events output `TOTAL,0,` |

### Feature: Regions Report

| ID | Story | High-level AC |
|---|---|---|
| REG-001 | Report event count and maximum magnitude per region | Region is the text after the last `, ` in `place` (or whole place; null place is `Unknown`); output `region,events,max_mag` ordered by events descending then region ascending |

### Feature: Distance Search

| ID | Story | High-level AC |
|---|---|---|
| NEAR-001 | List events within a haversine radius of a point | Validate `--lat`, `--lon`, `--radius` (all required); compute haversine distance on a 6371.0 km sphere; output `distance_km,time,mag,place,id` for events at most `--radius` km, distance ascending then time ascending |

### Feature: Command Interface and Exit Codes

| ID | Story | High-level AC |
|---|---|---|
| CLI-001 | Dispatch commands and validate options | Command first, options in any order, file last; unknown commands or options, malformed values, and missing or extra file exit 2 |
| CLI-002 | Map failures to documented exit codes and silent stdout | Exit 0 on success including empty reports; exit 1 for operational failures; exit 2 for usage errors; a failing command writes nothing to stdout and one diagnostic line to stderr |

### Feature: Output Formatting

| ID | Story | High-level AC |
|---|---|---|
| FMT-001 | Format CSV output with UTC times, decimal precision, and UTF-8 | Times as `YYYY-MM-DDTHH:MM:SSZ` truncated to seconds; magnitudes one decimal; `mean_mag` two decimals; distances one decimal; CSV via Python `csv` module with `\n` line endings and UTF-8 |

### Feature: Test Suite

| ID | Story | High-level AC |
|---|---|---|
| TEST-001 | Provide a POSIX bin/test.sh running the pytest suite | `bin/test.sh` runs the application's pytest suite from the application root and exits zero only when every test passes |

## Story Guidance

Named stories planning must produce. Authoritative record: `STORY_GUIDANCE.json`.

None.

## Surfaced Acceptance Criteria

| ID | Story ID | Criterion |
|---|---|---|
| AC-001 | FETCH-001 | `fetch` writes the response body byte-for-byte to `--out` and prints exactly `fetched,<count>` where count is the number of features |
| AC-002 | FETCH-001 | `--min-mag` defaults to `2.5` when omitted from `fetch` |
| AC-003 | FETCH-002 | `fetch` on failure leaves any pre-existing output file path untouched by writing no file |
| AC-004 | READ-002 | A feature with `mag` null is absent from every report, including counts |
| AC-005 | SUM-001 | `summary` `first` and `last` are the earliest and latest event times in the filtered set |
| AC-006 | SUM-001 | `summary` `tsunami` counts events whose `tsunami` value equals `1` |
| AC-007 | TOP-001 | `top` `--n` default is 10 when omitted |
| AC-008 | DAY-001 | `daily` date is the first 10 characters of the UTC time string |
| AC-009 | REG-001 | A `null` place is reported under region `Unknown` |
| AC-010 | NEAR-001 | `near` rows whose distance is exactly `--radius` are included |
| AC-011 | CLI-001 | An option the command does not list is a usage error (exit 2) |
| AC-012 | CLI-002 | Standard error is never compared by the grader; the diagnostic line is written only on failure |
| AC-013 | FMT-001 | Place names containing commas are quoted by the `csv` module; non-ASCII place names are written as UTF-8 |

## Source Inventory

| Path | Content kind | Disposition | Reason |
|---|---|---|---|
| `sources/INSTRUCTIONS.md` | markdown | analyzed | readable UTF-8 |
| `sources/quakes_2025-01-01_07.geojson` | text | analyzed | readable UTF-8 |
| `sources/run.sh` | code | analyzed | readable UTF-8 |

## Relationship Model

| Source or group | Relationship type | Related source or group | Evidence | Delivery implication |
|---|---|---|---|---|
| sources/INSTRUCTIONS.md | instruction-to-test | sources/run.sh | INSTRUCTIONS.md "Run Harness" states run.sh is the scoring entry point with 26 checks | run.sh must be staged; the application must produce `./quakes` at its root |
| sources/run.sh | test-kit-to-implementation | quakes executable at application root | run.sh `BIN="$APP/quakes"` and `check` invocations | the executable named `quakes` must exist and be executable at the application root |
| sources/quakes_2025-01-01_07.geojson | fixture-to-implementation | run.sh report checks | run.sh `QUAKES` variable and known answers | the snapshot must be staged alongside run.sh; reports are computed from it |
| sources/INSTRUCTIONS.md | instruction-to-test | bin/test.sh (application) | INSTRUCTIONS.md "Tests" section | application-authored pytest suite is required; it is not a supplied file |
| READ-002 | parser-to-normalizer | SUM-001, TOP-001, DAY-001, REG-001, NEAR-001 | INSTRUCTIONS.md "Reading a file" steps 2 to 6 | every report depends on the shared feature reader |
| FETCH-001 | dependency | FETCH-002 | INSTRUCTIONS.md "fetch" section | FETCH-002 failure behavior extends the same request path |

## Source Roles

| Path | Role | Plan disposition | Build disposition |
|---|---|---|---|
| sources/INSTRUCTIONS.md | author intent | compass | prompt-only |
| sources/run.sh | conformance harness | context | stage |
| sources/quakes_2025-01-01_07.geojson | asset | context | stage |

## Planning Instructions

### Delivery Shape

The system is a single-process Python 3.11+ command-line tool named `quakes`, installed at the application root. Inputs are USGS FDSN HTTP responses (via `fetch`) and saved GeoJSON files (via report commands). Outputs are a saved GeoJSON file (`fetch`) and CSV reports on standard output. Execution flow: `fetch` writes a file; each report reads that file, validates it, filters by `--min-mag`, computes its rows, and prints CSV.

### Story Realization Map

| Story ID | Durable scope | Evidence | Related files | Requires |
|---|---|---|---|---|
| FETCH-001 | fetch request and file write | INSTRUCTIONS.md `fetch` | quakes executable | capability, stubbed HTTP in tests |
| FETCH-002 | fetch failure paths | INSTRUCTIONS.md `fetch`, Operational failure | quakes executable | capability, stubbed HTTP in tests |
| READ-001 | file validation | INSTRUCTIONS.md "Reading a file" step 1 | quakes executable | capability |
| READ-002 | event field extraction and null-mag exclusion | INSTRUCTIONS.md "Reading a file" steps 2 to 3 | quakes executable; snapshot | capability |
| READ-003 | filter application | INSTRUCTIONS.md "Reading a file" step 4 | quakes executable | capability |
| SUM-001 | summary report | INSTRUCTIONS.md "Reports" table | quakes executable; snapshot | capability, test harness |
| TOP-001 | top report | INSTRUCTIONS.md "Reports" table | quakes executable; snapshot | capability, test harness |
| DAY-001 | daily report | INSTRUCTIONS.md "Reports" table | quakes executable; snapshot | capability, test harness |
| REG-001 | regions report | INSTRUCTIONS.md "Reading a file" step 6, "Reports" table | quakes executable; snapshot | capability, test harness |
| NEAR-001 | near report and haversine | INSTRUCTIONS.md "Distance" section | quakes executable; snapshot | capability, test harness |
| CLI-001 | argument parsing | INSTRUCTIONS.md "Commands" section | quakes executable | capability |
| CLI-002 | exit codes and stdout/stderr discipline | INSTRUCTIONS.md "Exit codes" table | quakes executable | capability |
| FMT-001 | CSV and number formatting | INSTRUCTIONS.md "Formatting" section | quakes executable | capability |
| TEST-001 | pytest suite and bin/test.sh | INSTRUCTIONS.md "Tests" section | bin/test.sh; pytest suite | test harness |

### Test and Acceptance Strategy

Focused story tests are pytest cases under the application that run each report against small files written by the tests, and exercise `fetch` through a stubbed HTTP call. Final Sea Trial verification runs `sh sources/run.sh` against the completed application, which checks 26 report and error cases against the frozen snapshot. The terminal verification story gates on the complete supplied suite via `sh sources/run.sh`; `bin/test.sh` is required to run the full application test suite unfiltered.

### Sequencing and Dependencies

- READ-001 and READ-002 precede every report story.
- READ-003 precedes SUM-001, TOP-001, DAY-001, REG-001, and NEAR-001.
- CLI-001 and CLI-002 precede every report story and FETCH-001.
- FMT-001 precedes every report story that prints values.
- FETCH-001 precedes FETCH-002.
- TEST-001 depends on every implementation story.
- The grader `sources/run.sh` and snapshot are staged before the terminal verification story runs.

### Source Conflicts and Gaps

- No cross-source conflicts were found. The sources define one product and one command set.
- No blockers. Stack is Python 3.11+ standard library, stated in the sources.

## Analysis Notes
generated: 2026-10-24
blueprint: /mnt/c/Users/barlo/projects/drydock/uat/Quakes/runs/20261025.010423/workspace/targets/Quakes/blueprint

Quality: Ready
  blockers: 0
  questions: 0
  features: 9
  stories: 16
  stack: Python 3.11+ standard library; pytest for tests; `urllib.request` for HTTP
  display_name: not proposed
  short_description: not proposed

Observations: Resolved by narrowest reading: `--n` applies only to `top`; `near` ranking uses the same ordering rule as other reports; `fetch` leaves an existing output file untouched on failure.
