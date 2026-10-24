# MANIFEST: Quakes
updated: 2026-10-24T21:31:26+00:00
state: draft
blocks:      4

## story 1: Stand up the Python CLI foundation: the cli package, the executable quakes at the application root, bin launchers, and the pytest runner.
id:           foundation
summary:      Stand up the Python CLI foundation: the cli package, the executable quakes at the application root, bin launchers, and the pytest runner.
type:         foundational
kind:         capability
phase:        1
block:        1
implements:   ARCHITECTURE.md
instructions: |
  Create the project root per the Foundation Contract: pyproject.toml, .venv via uv, cli/__init__.py
  exposing main(argv) -> int, cli/testing.py with cli_runner, and conftest.py exposing the cli_runner fixture.
  Create the executable `quakes` at the application root (Python 3.11+, standard library only) that calls
  cli.main and exits with its return value.

  Lay out separate modules for reading a file, filtering, computing each report, and formatting, so each is
  an independently unit-tested function. Diagnostics go to standard error only.

  Do not read sources/run.sh or the snapshot from application code and do not embed any report value.
stack:        common.md, python.md, cli.md
stack_mode:   builder
size:         10454
provides:     quakes executable, cli.main, cli.testing.cli_runner
acceptance:   yes
state:        pending

## story 2: Dispatch the command and parse options in any order with the file last.
id: feature-cli-dispatch
summary: Dispatch the command and parse options in any order with the file last.
type: service
kind: capability
phase: 1
block: 2
implements: FEATURE-CliDispatch.md
covers: CLI-001
context: ARCHITECTURE_compact.md
stack: python.md, cli.md
stack_mode: consumer
size: 10641
provides: quakes <command> dispatch, option parser
consumes: cli.main
instructions: |
  Implement command dispatch for fetch, summary, top, daily, regions, near. The command comes first, options
  follow in any order, and the file is last. Validate option values against -?[0-9]+(\.[0-9]+)? for decimals
  and a positive integer for --n (default 10). Unknown command or option, an option the command does not
  take, a missing or malformed value, a repeated option, and a missing or extra file are usage errors.
  Report commands call the reader, filter, compute and format functions as they are built by later stories.
acceptance: yes
depends: foundation
state: pending

## story 3: Provide help text for every command.
id: feature-help
summary: Provide help text for every command.
type: service
kind: capability
phase: 1
block: 2
implements: FEATURE-Help.md
covers: CLI-003
context: ARCHITECTURE_compact.md
stack: python.md, cli.md
stack_mode: consumer
size: 8773
provides: --help for quakes and each command
consumes: quakes <command> dispatch
instructions: |
  Provide help text for the program and for each of fetch, summary, top, daily, regions and near, shown by
  --help. Help exits 0 and is written to standard output. It is the one case where an otherwise unlisted
  option is accepted.
acceptance: yes
depends: feature-cli-dispatch
state: pending

## story 4: Map outcomes to exit codes 0/1/2 and keep stdout empty on failure with one stderr line.
id: feature-exit-codes
summary: Map outcomes to exit codes 0/1/2 and keep stdout empty on failure with one stderr line.
type: service
kind: capability
phase: 1
block: 2
implements: FEATURE-ExitCodes.md
covers: CLI-002
accepts: st-007
context: ARCHITECTURE_compact.md
stack: python.md, cli.md
stack_mode: consumer
size: 9205
provides: exit code contract
consumes: quakes <command> dispatch
instructions: |
  Define the two error types (usage error, operational failure) and map them in cli.main: 0 success, 1
  operational, 2 usage. Compute the full report before writing anything, so a failing command writes
  nothing to standard output and exactly one diagnostic line to standard error.
acceptance: yes
depends: feature-cli-dispatch
state: pending

## story 5: Read a saved GeoJSON FeatureCollection into events.
id: feature-feed-reader
summary: Read a saved GeoJSON FeatureCollection into events.
type: service
kind: capability
phase: 1
block: 2
implements: FEATURE-FeedReader.md
covers: FEED-001
context: ARCHITECTURE_compact.md
stack: python.md
stack_mode: consumer
size: 7837
provides: read_events(path)
instructions: |
  Implement a reader function that parses the file as JSON and requires an object with type FeatureCollection
  and a features array; otherwise raise the operational failure. For each feature read id, properties.mag,
  place, time, tsunami and geometry.coordinates (lon, lat, depth_km). Ignore all other fields. Exclude
  features whose mag is null. The reader opens the file as UTF-8 and handles an unreadable path as an
  operational failure.
acceptance: yes
depends: foundation
state: pending

## story 6: Normalise event time, date and region and provide the number formatting helpers.
id: feature-event-normalise
summary: Normalise event time, date and region and provide the number formatting helpers.
type: service
kind: capability
phase: 1
block: 2
implements: FEATURE-EventNormalise.md
covers: FEED-002
context: ARCHITECTURE_compact.md
stack: python.md
stack_mode: consumer
size: 7615
provides: format_time, region_of, format_mag, format_one_decimal, format_two_decimal
consumes: read_events(path)
instructions: |
  Time is UTC YYYY-MM-DDTHH:MM:SSZ truncated to whole seconds from milliseconds since the epoch; the date is
  its first 10 characters. Region is the text after the last ", " in place, or the whole place; a null place
  becomes Unknown, which is also its region. Provide pure formatting helpers: magnitude with one decimal,
  depth and distance with one decimal rounded half up, mean with two decimals rounded half up (use decimal,
  not float formatting).
acceptance: yes
depends: feature-feed-reader
state: pending

## story 7: Filter events by --min-mag for every report.
id: feature-min-mag
summary: Filter events by --min-mag for every report.
type: service
kind: capability
phase: 1
block: 2
implements: FEATURE-MinMagFilter.md
covers: FEED-003
accepts: st-005
context: ARCHITECTURE_compact.md
stack: python.md
stack_mode: consumer
size: 6909
provides: filter_min_mag(events, m), --min-mag option
consumes: read_events(path)
instructions: |
  Implement a pure filter keeping events with mag >= m, and wire --min-mag into every report command through
  the common pipeline: read, filter, compute, format.
acceptance: yes
depends: feature-event-normalise, feature-cli-dispatch
state: pending

## story 8: The summary report.
id: feature-summary
summary: The summary report.
type: service
kind: capability
phase: 2
block: 3
implements: FEATURE-Summary.md
covers: SUM-001
accepts: st-003
context: ARCHITECTURE_compact.md
stack: python.md
stack_mode: consumer
size: 7626
provides: quakes summary
consumes: filter_min_mag(events, m), format_time
instructions: |
  Header events,first,last,min_mag,max_mag,mean_mag,tsunami with one row. first and last are the earliest and
  latest event times; tsunami counts events with tsunami equal to 1; mean half up to 2 dp. With no events
  the row is 0,,,,,,0. Write with the csv module and \n line endings.
acceptance: yes
depends: feature-min-mag, feature-exit-codes
state: pending

## story 9: The per-region report.
id: feature-regions
summary: The per-region report.
type: service
kind: capability
phase: 2
block: 3
implements: FEATURE-Regions.md
covers: REG-001
accepts: st-003
context: ARCHITECTURE_compact.md
stack: python.md
stack_mode: consumer
size: 6860
provides: quakes regions
consumes: filter_min_mag(events, m), region_of
instructions: |
  Header region,events,max_mag. One row per region ordered by events descending then region ascending,
  comparing region text by byte value (UTF-8 encoded), written as UTF-8.
acceptance: yes
depends: feature-min-mag, feature-exit-codes
state: pending

## story 10: Fetch the USGS feed and save the body unchanged.
id: feature-fetch
summary: Fetch the USGS feed and save the body unchanged.
type: service
kind: integration
phase: 2
block: 3
implements: FEATURE-Fetch.md
covers: FETCH-001
accepts: st-006
context: ARCHITECTURE_compact.md
stack: python.md
stack_mode: consumer
size: 7252
provides: quakes fetch, http_get
consumes: quakes <command> dispatch
instructions: |
  Build the FDSN query URL https://earthquake.usgs.gov/fdsnws/event/1/query with format=geojson,
  starttime, endtime, minmagnitude (default 2.5) and orderby=time-asc. Perform the request through one
  replaceable module-level function (http_get) using urllib.request. Write the response bytes unchanged to
  --out and print fetched,<count> where count is the number of features.
acceptance: yes
depends: feature-cli-dispatch, feature-exit-codes, feature-feed-reader
state: pending

## story 11: Fail fetch without writing a file on network, HTTP or body errors.
id: feature-fetch-errors
summary: Fail fetch without writing a file on network, HTTP or body errors.
type: service
kind: integration
phase: 2
block: 3
implements: FEATURE-FetchErrors.md
covers: FETCH-002, FETCH-003
accepts: st-006, st-007
context: ARCHITECTURE_compact.md
stack: python.md
stack_mode: consumer
size: 6635
provides: fetch failure behavior
consumes: http_get
instructions: |
  A network error, an HTTP status other than 200, or a body that is not a GeoJSON FeatureCollection exits 1,
  writes no file, writes nothing to standard output and one line to standard error. Validate the body before
  opening the output path.
acceptance: yes
depends: feature-fetch
state: pending

## story 12: Provide bin/test.sh running the pytest suite.
id: feature-test-runner
summary: Provide bin/test.sh running the pytest suite.
type: service
kind: test harness
phase: 2
block: 3
implements: FEATURE-TestRunner.md
covers: TEST-001
accepts: st-002
context: ARCHITECTURE_compact.md
stack: common.md, python.md
stack_mode: consumer
size: 7356
provides: bin/test.sh
consumes: cli.testing.cli_runner
instructions: |
  Provide a POSIX sh bin/test.sh that changes to the application root, activates the .venv launcher and runs
  pytest -q, exiting zero only when every test passes. Unit tests for each pure function (read, filter,
  compute, format) live under tests/.
acceptance: yes
depends: foundation
state: pending

## story 13: Test fetch through a stubbed HTTP call.
id: feature-fetch-stub-tests
summary: Test fetch through a stubbed HTTP call.
type: service
kind: test harness
phase: 2
block: 3
implements: FEATURE-FetchStubTests.md
covers: TEST-002
accepts: st-008
context: ARCHITECTURE_compact.md
stack: python.md
stack_mode: consumer
size: 5764
provides: tests/test_fetch.py
consumes: http_get
instructions: |
  Write pytest tests that replace http_get with a stub (monkeypatch) and cover success, count output,
  non-200, network error and non-FeatureCollection bodies. No test opens a network connection.
acceptance: yes
depends: feature-fetch-errors, feature-test-runner
state: pending

## story 14: The per-day report.
id: feature-daily
summary: The per-day report.
type: service
kind: capability
phase: 2
block: 3
implements: FEATURE-Daily.md
covers: DAY-001
accepts: st-003
context: ARCHITECTURE_compact.md
stack: python.md
stack_mode: consumer
size: 7453
provides: quakes daily
consumes: filter_min_mag(events, m), format_time
instructions: |
  Header date,events,max_mag. One row per date that has events, ascending, then TOTAL,<events>,<max_mag>.
  With no events the final row is TOTAL,0, with an empty max.
acceptance: yes
depends: feature-min-mag, feature-exit-codes
state: pending

## story 15: The top report with the --n limit.
id: feature-top
summary: The top report with the --n limit.
type: service
kind: capability
phase: 2
block: 3
implements: FEATURE-Top.md
covers: TOP-001, TOP-002
accepts: st-003
context: ARCHITECTURE_compact.md
stack: python.md
stack_mode: consumer
size: 7735
provides: quakes top
consumes: filter_min_mag(events, m), format_time
instructions: |
  Header time,mag,depth_km,place,id. The --n largest events by mag descending then time ascending; --n
  defaults to 10 and --n 0 or a non-integer is a usage error. Write with the csv module (places containing
  commas are quoted) as UTF-8.
acceptance: yes
depends: feature-min-mag, feature-exit-codes
state: pending

## story 16: The haversine distance search.
id: feature-near
summary: The haversine distance search.
type: service
kind: capability
phase: 2
block: 3
implements: FEATURE-Near.md
covers: NEAR-001
accepts: st-004
context: ARCHITECTURE_compact.md
stack: python.md
stack_mode: consumer
size: 7744
provides: quakes near, haversine_km
consumes: filter_min_mag(events, m), format_time
instructions: |
  Header distance_km,time,mag,place,id. Haversine distance on a 6371.0 km sphere from (--lat, --lon). Keep
  events with distance <= radius (compare unrounded), order by distance ascending then time ascending, and
  write distance with one decimal rounded half up. No match yields only the header.
acceptance: yes
depends: feature-min-mag, feature-exit-codes
state: pending

## story 17: Validate near coordinates and radius.
id: feature-near-validation
summary: Validate near coordinates and radius.
type: service
kind: capability
phase: 2
block: 3
implements: FEATURE-NearValidation.md
covers: NEAR-002
accepts: st-007
context: ARCHITECTURE_compact.md
stack: python.md
stack_mode: consumer
size: 6037
provides: near option validation
consumes: quakes near
instructions: |
  --lat outside -90..90, --lon outside -180..180, --radius not positive, or any of the three missing is a
  usage error (exit 2) with nothing written to standard output.
acceptance: yes
depends: feature-near
state: pending

## story 18: Terminal gate: run the supplied grader over the completed application.
id:           verification
summary:      Terminal gate: run the supplied grader over the completed application.
type:         feature
kind:         test harness
phase:        3
block:        4
implements:   VERIFICATION.md
accepts:      st-001, st-002, st-003
instructions: |
  Assembly and intent only: confirm the integrated application passes sh bin/test.sh and sh sources/run.sh,
  both exit status 0. The sources/ directory is staged read-only and must not be modified.
stack:        python.md
stack_mode:   consumer
size:         2679
consumes:     quakes executable
depends:      feature-summary, feature-top, feature-daily, feature-regions, feature-near-validation, feature-help, feature-fetch-stub-tests, feature-test-runner
acceptance:   yes
state:        pending
