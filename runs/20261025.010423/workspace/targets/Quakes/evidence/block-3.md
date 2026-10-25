# Evidence: Block 3 · Service (block-3)

- block type: block
- date: 2026-10-24
- resulting state: closed/verified
- story points (combined assembled cost): 19525
- execution id: 20261025.011739.796Z-6a746565

## Stories built
- Parse and validate the command, options, and file argument, with usage errors exiting 2. (options) [story]
- Map usage and operational failures to exit codes 2 and 1 with silent stdout and one stderr line. (exit-codes) [story]
- Format times, magnitudes, depths, distances, and CSV output. (formatting) [story]
- Read a saved GeoJSON file and validate that it is a FeatureCollection. (feed-validation) [story]
- Extract event fields from features and exclude null-magnitude events. (event-extraction) [story]
- Apply the --min-mag filter to events. (mag-filter) [story]
- Provide bin/test.sh running the pytest suite. (test-suite) [story]

## Acceptance tooling authorization
- FEATURE-FeedValidation.md#feed-valid-collection: executable=python3; scope=test; authorization=existing Target environment
- FEATURE-FeedValidation.md#feed-unreadable-file: executable=python3; scope=test; authorization=existing Target environment
- FEATURE-FeedValidation.md#feed-not-json: executable=python3; scope=test; authorization=existing Target environment
- FEATURE-FeedValidation.md#feed-wrong-shape: executable=python3; scope=test; authorization=existing Target environment
- FEATURE-EventExtraction.md#extract-fields: executable=python3; scope=test; authorization=existing Target environment
- FEATURE-EventExtraction.md#extract-null-mag-excluded: executable=python3; scope=test; authorization=existing Target environment
- FEATURE-EventExtraction.md#extract-null-place-and-empty: executable=python3; scope=test; authorization=existing Target environment
- FEATURE-MagFilter.md#filter-threshold-inclusive: executable=python3; scope=test; authorization=existing Target environment
- FEATURE-MagFilter.md#filter-none-keeps-all: executable=python3; scope=test; authorization=existing Target environment
- FEATURE-MagFilter.md#filter-nothing-matches: executable=python3; scope=test; authorization=existing Target environment
- FEATURE-TestSuite.md#testsuite-script-exists: executable=sh; scope=test; authorization=existing Target environment
- FEATURE-TestSuite.md#testsuite-runs-green: executable=sh; scope=test; authorization=existing Target environment
- FEATURE-TestSuite.md#testsuite-runs-green: python-package=pytest; scope=test; authorization=existing Target environment
- FEATURE-TestSuite.md#testsuite-runs-from-other-directory: executable=sh; scope=test; authorization=existing Target environment
- FEATURE-TestSuite.md#testsuite-runs-from-other-directory: python-package=pytest; scope=test; authorization=existing Target environment
- FEATURE-TestSuite.md#testsuite-propagates-failure: executable=sh; scope=test; authorization=existing Target environment
- FEATURE-TestSuite.md#testsuite-propagates-failure: python-package=pytest; scope=test; authorization=existing Target environment
- FEATURE-TestSuite.md#testsuite-passes-when-tests-pass: executable=sh; scope=test; authorization=existing Target environment
- FEATURE-TestSuite.md#testsuite-passes-when-tests-pass: python-package=pytest; scope=test; authorization=existing Target environment

## Stacked context
- stack: python_compact.md (SP 921)
- compass: COMPASS.md (SP 986)
- implements: FEATURE-Options.md (SP 2305)
- context: ARCHITECTURE_compact.md (SP 741)
- stack: cli.md (SP 2689)
- implements: FEATURE-ExitCodes.md (SP 1489)
- implements: FEATURE-Formatting.md (SP 1548)
- implements: FEATURE-FeedValidation.md (SP 1732)
- implements: FEATURE-EventExtraction.md (SP 1453)
- implements: FEATURE-MagFilter.md (SP 1124)
- implements: FEATURE-TestSuite.md (SP 2200)
- stack: common_compact.md (SP 1653)

## Build directory changes
- bin/test.sh
- cli/__init__.py
- cli/errors.py
- cli/feed.py
- cli/formatting.py
- cli/options.py
- tests/test_cli_foundation.py
- tests/test_event_extraction.py
- tests/test_exit_codes.py
- tests/test_feed.py
- tests/test_formatting.py
- tests/test_mag_filter.py
- tests/test_options.py
- tests/test_test_suite.py

## Pre-build acceptance observation
- RED: options-valid-summary (FEATURE-Options.md)
  intent: A valid summary invocation parses into the expected command, filter, and file.
  return code: 1
  stderr:
    Traceback (most recent call last):
      File "options-valid-summary.py", line 1, in <module>
        from cli.options import parse_args
    ModuleNotFoundError: No module named 'cli.options'
- RED: options-defaults (FEATURE-Options.md)
  intent: top defaults n to 10, reports default min_mag to None, and fetch defaults min_mag to 2.5.
  return code: 1
  stderr:
    Traceback (most recent call last):
      File "options-defaults.py", line 1, in <module>
        from cli.options import parse_args
    ModuleNotFoundError: No module named 'cli.options'
- RED: options-any-order (FEATURE-Options.md)
  intent: Options may appear in any order and produce the same parsed values.
  return code: 1
  stderr:
    Traceback (most recent call last):
      File "options-any-order.py", line 1, in <module>
        from cli.options import parse_args
    ModuleNotFoundError: No module named 'cli.options'
- RED: options-near-valid (FEATURE-Options.md)
  intent: near parses its three required options, accepting the range boundaries and negative decimals.
  return code: 1
  stderr:
    Traceback (most recent call last):
      File "options-near-valid.py", line 1, in <module>
        from cli.options import parse_args
    ModuleNotFoundError: No module named 'cli.options'
- RED: options-fetch-valid (FEATURE-Options.md)
  intent: fetch parses start, end, out, and an explicit min-mag.
  return code: 1
  stderr:
    Traceback (most recent call last):
      File "options-fetch-valid.py", line 1, in <module>
        from cli.options import parse_args
    ModuleNotFoundError: No module named 'cli.options'
- RED: options-usage-errors (FEATURE-Options.md)
  intent: Every malformed invocation raises UsageError.
  return code: 1
  stderr:
    Traceback (most recent call last):
      File "options-usage-errors.py", line 2, in <module>
        from cli.options import parse_args
    ModuleNotFoundError: No module named 'cli.options'
- GREEN (prepassed): options-exit-two (FEATURE-Options.md)
  intent: Through the executable entry point, an unknown command and a missing command both exit 2.
  return code: 0
- GREEN (prepassed): exit-usage-code (FEATURE-ExitCodes.md)
  intent: A usage error returns exit code 2 with empty stdout and a single stderr line.
  return code: 0
- RED: exit-operational-code (FEATURE-ExitCodes.md)
  intent: An OperationalError raised by a handler returns exit code 1 with empty stdout and a single stderr line.
  return code: 1
  stderr:
    --- drydock: values at failure ---
      code = 0
    --- drydock: end values ---
    Traceback (most recent call last):
      File "exit-operational-code.py", line 17, in <module>
        assert code == 1
               ^^^^^^^^^
    AssertionError
- RED: exit-success-code (FEATURE-ExitCodes.md)
  intent: A handler that returns text yields exit 0 and that exact text on stdout, and an empty result is still success.
  return code: 1
  stderr:
    --- drydock: values at failure ---
      out = ''
      text = 'header\nrow\n'
    --- drydock: end values ---
    Traceback (most recent call last):
      File "exit-success-code.py", line 17, in <module>
        assert out == text
               ^^^^^^^^^^^
    AssertionError
- GREEN (prepassed): exit-error-classes (FEATURE-ExitCodes.md)
  intent: UsageError and OperationalError are distinct exception classes.
  return code: 0
- GREEN (prepassed): exit-launcher-status (FEATURE-ExitCodes.md)
  intent: The quakes executable surfaces exit 2 for a usage error with empty stdout.
  return code: 0
  stderr:
    error: unknown command: 'frobnicate'
- RED: fmt-time (FEATURE-Formatting.md)
  intent: format_time yields a UTC timestamp truncated to whole seconds whose first 10 characters are the date.
  return code: 1
  stderr:
    Traceback (most recent call last):
      File "fmt-time.py", line 3, in <module>
        from cli.formatting import format_time
    ModuleNotFoundError: No module named 'cli.formatting'
- RED: fmt-magnitude (FEATURE-Formatting.md)
  intent: Magnitudes are written with exactly one decimal place.
  return code: 1
  stderr:
    Traceback (most recent call last):
      File "fmt-magnitude.py", line 1, in <module>
        from cli.formatting import format_mag
    ModuleNotFoundError: No module named 'cli.formatting'
- RED: fmt-mean-half-up (FEATURE-Formatting.md)
  intent: mean_mag has two decimals and rounds exact halves up.
  return code: 1
  stderr:
    Traceback (most recent call last):
      File "fmt-mean-half-up.py", line 1, in <module>
        from cli.formatting import format_mean
    ModuleNotFoundError: No module named 'cli.formatting'
- RED: fmt-decimal-half-up (FEATURE-Formatting.md)
  intent: depth and distance have one decimal and round exact halves up.
  return code: 1
  stderr:
    Traceback (most recent call last):
      File "fmt-decimal-half-up.py", line 1, in <module>
        from cli.formatting import format_decimal
    ModuleNotFoundError: No module named 'cli.formatting'
- RED: fmt-csv-roundtrip (FEATURE-Formatting.md)
  intent: render_csv round-trips fields containing commas and non-ASCII characters through the csv parser with \n line endings.
  return code: 1
  stderr:
    Traceback (most recent call last):
      File "fmt-csv-roundtrip.py", line 4, in <module>
        from cli.formatting import render_csv
    ModuleNotFoundError: No module named 'cli.formatting'
- RED: fmt-write-csv (FEATURE-Formatting.md)
  intent: write_csv writes the rendered CSV to the given stream and to standard output by default.
  return code: 1
  stderr:
    Traceback (most recent call last):
      File "fmt-write-csv.py", line 4, in <module>
        from cli.formatting import render_csv, write_csv
    ModuleNotFoundError: No module named 'cli.formatting'
- RED: feed-valid-collection (FEATURE-FeedValidation.md)
  intent: A FeatureCollection file returns its features list, including an empty one.
  return code: 1
  stderr:
    Traceback (most recent call last):
      File "feed-valid-collection.py", line 5, in <module>
        from cli.feed import read_feed
    ModuleNotFoundError: No module named 'cli.feed'
- RED: feed-unreadable-file (FEATURE-FeedValidation.md)
  intent: A missing file and a directory both raise OperationalError.
  return code: 1
  stderr:
    Traceback (most recent call last):
      File "feed-unreadable-file.py", line 4, in <module>
        from cli.feed import read_feed
    ModuleNotFoundError: No module named 'cli.feed'
- RED: feed-not-json (FEATURE-FeedValidation.md)
  intent: Content that is not JSON raises OperationalError.
  return code: 1
  stderr:
    Traceback (most recent call last):
      File "feed-not-json.py", line 4, in <module>
        from cli.feed import read_feed
    ModuleNotFoundError: No module named 'cli.feed'
- RED: feed-wrong-shape (FEATURE-FeedValidation.md)
  intent: JSON that is not a FeatureCollection object with a features array raises OperationalError.
  return code: 1
  stderr:
    Traceback (most recent call last):
      File "feed-wrong-shape.py", line 5, in <module>
        from cli.feed import read_feed
    ModuleNotFoundError: No module named 'cli.feed'
- RED: extract-fields (FEATURE-EventExtraction.md)
  intent: Every needed field is read from the feature into the matching Event attribute.
  return code: 1
  stderr:
    Traceback (most recent call last):
      File "extract-fields.py", line 1, in <module>
        from cli.feed import extract_events
    ModuleNotFoundError: No module named 'cli.feed'
- RED: extract-null-mag-excluded (FEATURE-EventExtraction.md)
  intent: Features with a null magnitude are absent from the result and the rest keep feed order.
  return code: 1
  stderr:
    Traceback (most recent call last):
      File "extract-null-mag-excluded.py", line 1, in <module>
        from cli.feed import extract_events
    ModuleNotFoundError: No module named 'cli.feed'
- RED: extract-null-place-and-empty (FEATURE-EventExtraction.md)
  intent: A null place is preserved as None and an empty feature list yields no events.
  return code: 1
  stderr:
    Traceback (most recent call last):
      File "extract-null-place-and-empty.py", line 1, in <module>
        from cli.feed import extract_events
    ModuleNotFoundError: No module named 'cli.feed'
- RED: filter-threshold-inclusive (FEATURE-MagFilter.md)
  intent: Events at or above the threshold are kept, including those exactly at it, and order is preserved.
  return code: 1
  stderr:
    Traceback (most recent call last):
      File "filter-threshold-inclusive.py", line 1, in <module>
        from cli.feed import extract_events, filter_events
    ModuleNotFoundError: No module named 'cli.feed'
- RED: filter-none-keeps-all (FEATURE-MagFilter.md)
  intent: A None threshold keeps every event and does not mutate the input.
  return code: 1
  stderr:
    Traceback (most recent call last):
      File "filter-none-keeps-all.py", line 1, in <module>
        from cli.feed import extract_events, filter_events
    ModuleNotFoundError: No module named 'cli.feed'
- RED: filter-nothing-matches (FEATURE-MagFilter.md)
  intent: A threshold above every magnitude yields an empty list rather than an error.
  return code: 1
  stderr:
    Traceback (most recent call last):
      File "filter-nothing-matches.py", line 1, in <module>
        from cli.feed import extract_events, filter_events
    ModuleNotFoundError: No module named 'cli.feed'
- GREEN (prepassed): testsuite-script-exists (FEATURE-TestSuite.md)
  intent: bin/test.sh exists at the application root and declares a POSIX sh interpreter.
  return code: 0
  stdout:
    #!/bin/sh
- GREEN (prepassed): testsuite-runs-green (FEATURE-TestSuite.md)
  intent: Running bin/test.sh over the built application's own pytest suite exits zero.
  return code: 0
  stdout:
    .......................                                                  [100%]
    23 passed in 0.21s
- GREEN (prepassed): testsuite-runs-from-other-directory (FEATURE-TestSuite.md)
  intent: bin/test.sh resolves the application root itself, so an outside working directory gives the same exit status.
  return code: 0
  stdout:
    .......................                                                  [100%]
    23 passed in 0.19s
- GREEN (prepassed): testsuite-propagates-failure (FEATURE-TestSuite.md)
  intent: bin/test.sh exits nonzero when a test in its application root fails.
  return code: 0
  stdout:
    test.sh: .venv not found; run 'uv venv && uv sync' first
- RED: testsuite-passes-when-tests-pass (FEATURE-TestSuite.md)
  intent: bin/test.sh exits zero for an application root whose only test passes.
  return code: 1
  stdout:
    test.sh: .venv not found; run 'uv venv && uv sync' first
  stderr:
    --- drydock: values at failure ---
      result = CompletedProcess(args=['sh', '/tmp/tmp5fm8t51w/bin/test.sh'], returncode=1, stdout='', stderr="test.sh: .venv not found; run 'uv venv && uv sync' first\n")
    --- drydock: end values ---
    Traceback (most recent call last):
      File "testsuite-passes-when-tests-pass.py", line 21, in <module>
        assert result.returncode == 0
               ^^^^^^^^^^^^^^^^^^^^^^
    AssertionError

## Post-build programmatic acceptance
- PASS: options-valid-summary (FEATURE-Options.md)
  intent: A valid summary invocation parses into the expected command, filter, and file.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/Quakes/runs/20261025.010423/build/Quakes/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: options-defaults (FEATURE-Options.md)
  intent: top defaults n to 10, reports default min_mag to None, and fetch defaults min_mag to 2.5.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/Quakes/runs/20261025.010423/build/Quakes/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: options-any-order (FEATURE-Options.md)
  intent: Options may appear in any order and produce the same parsed values.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/Quakes/runs/20261025.010423/build/Quakes/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: options-near-valid (FEATURE-Options.md)
  intent: near parses its three required options, accepting the range boundaries and negative decimals.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/Quakes/runs/20261025.010423/build/Quakes/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: options-fetch-valid (FEATURE-Options.md)
  intent: fetch parses start, end, out, and an explicit min-mag.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/Quakes/runs/20261025.010423/build/Quakes/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: options-usage-errors (FEATURE-Options.md)
  intent: Every malformed invocation raises UsageError.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/Quakes/runs/20261025.010423/build/Quakes/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: options-exit-two (FEATURE-Options.md)
  intent: Through the executable entry point, an unknown command and a missing command both exit 2.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/Quakes/runs/20261025.010423/build/Quakes/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: exit-usage-code (FEATURE-ExitCodes.md)
  intent: A usage error returns exit code 2 with empty stdout and a single stderr line.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/Quakes/runs/20261025.010423/build/Quakes/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: exit-operational-code (FEATURE-ExitCodes.md)
  intent: An OperationalError raised by a handler returns exit code 1 with empty stdout and a single stderr line.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/Quakes/runs/20261025.010423/build/Quakes/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: exit-success-code (FEATURE-ExitCodes.md)
  intent: A handler that returns text yields exit 0 and that exact text on stdout, and an empty result is still success.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/Quakes/runs/20261025.010423/build/Quakes/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: exit-error-classes (FEATURE-ExitCodes.md)
  intent: UsageError and OperationalError are distinct exception classes.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/Quakes/runs/20261025.010423/build/Quakes/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: exit-launcher-status (FEATURE-ExitCodes.md)
  intent: The quakes executable surfaces exit 2 for a usage error with empty stdout.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/Quakes/runs/20261025.010423/build/Quakes/.venv/bin/python
  provisioning: not required
  return code: 0
  stderr:
    error: unknown command: 'frobnicate'
- PASS: fmt-time (FEATURE-Formatting.md)
  intent: format_time yields a UTC timestamp truncated to whole seconds whose first 10 characters are the date.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/Quakes/runs/20261025.010423/build/Quakes/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: fmt-magnitude (FEATURE-Formatting.md)
  intent: Magnitudes are written with exactly one decimal place.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/Quakes/runs/20261025.010423/build/Quakes/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: fmt-mean-half-up (FEATURE-Formatting.md)
  intent: mean_mag has two decimals and rounds exact halves up.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/Quakes/runs/20261025.010423/build/Quakes/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: fmt-decimal-half-up (FEATURE-Formatting.md)
  intent: depth and distance have one decimal and round exact halves up.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/Quakes/runs/20261025.010423/build/Quakes/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: fmt-csv-roundtrip (FEATURE-Formatting.md)
  intent: render_csv round-trips fields containing commas and non-ASCII characters through the csv parser with \n line endings.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/Quakes/runs/20261025.010423/build/Quakes/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: fmt-write-csv (FEATURE-Formatting.md)
  intent: write_csv writes the rendered CSV to the given stream and to standard output by default.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/Quakes/runs/20261025.010423/build/Quakes/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: feed-valid-collection (FEATURE-FeedValidation.md)
  intent: A FeatureCollection file returns its features list, including an empty one.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/Quakes/runs/20261025.010423/build/Quakes/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: feed-unreadable-file (FEATURE-FeedValidation.md)
  intent: A missing file and a directory both raise OperationalError.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/Quakes/runs/20261025.010423/build/Quakes/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: feed-not-json (FEATURE-FeedValidation.md)
  intent: Content that is not JSON raises OperationalError.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/Quakes/runs/20261025.010423/build/Quakes/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: feed-wrong-shape (FEATURE-FeedValidation.md)
  intent: JSON that is not a FeatureCollection object with a features array raises OperationalError.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/Quakes/runs/20261025.010423/build/Quakes/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: extract-fields (FEATURE-EventExtraction.md)
  intent: Every needed field is read from the feature into the matching Event attribute.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/Quakes/runs/20261025.010423/build/Quakes/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: extract-null-mag-excluded (FEATURE-EventExtraction.md)
  intent: Features with a null magnitude are absent from the result and the rest keep feed order.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/Quakes/runs/20261025.010423/build/Quakes/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: extract-null-place-and-empty (FEATURE-EventExtraction.md)
  intent: A null place is preserved as None and an empty feature list yields no events.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/Quakes/runs/20261025.010423/build/Quakes/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: filter-threshold-inclusive (FEATURE-MagFilter.md)
  intent: Events at or above the threshold are kept, including those exactly at it, and order is preserved.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/Quakes/runs/20261025.010423/build/Quakes/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: filter-none-keeps-all (FEATURE-MagFilter.md)
  intent: A None threshold keeps every event and does not mutate the input.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/Quakes/runs/20261025.010423/build/Quakes/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: filter-nothing-matches (FEATURE-MagFilter.md)
  intent: A threshold above every magnitude yields an empty list rather than an error.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/Quakes/runs/20261025.010423/build/Quakes/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: testsuite-script-exists (FEATURE-TestSuite.md)
  intent: bin/test.sh exists at the application root and declares a POSIX sh interpreter.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/Quakes/runs/20261025.010423/build/Quakes/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    #!/bin/sh
- PASS: testsuite-runs-green (FEATURE-TestSuite.md)
  intent: Running bin/test.sh over the built application's own pytest suite exits zero.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/Quakes/runs/20261025.010423/build/Quakes/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    ........................................................................ [ 37%]
    ........................................................................ [ 75%]
    ...............................................                          [100%]
    191 passed in 17.75s
- PASS: testsuite-runs-from-other-directory (FEATURE-TestSuite.md)
  intent: bin/test.sh resolves the application root itself, so an outside working directory gives the same exit status.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/Quakes/runs/20261025.010423/build/Quakes/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    ........................................................................ [ 37%]
    ........................................................................ [ 75%]
    ...............................................                          [100%]
    191 passed in 12.33s
- PASS: testsuite-propagates-failure (FEATURE-TestSuite.md)
  intent: bin/test.sh exits nonzero when a test in its application root fails.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/Quakes/runs/20261025.010423/build/Quakes/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    F                                                                        [100%]
    =================================== FAILURES ===================================
    ______________________________ test_always_fails _______________________________
    
        def test_always_fails():
    >       assert False
    E       assert False
    
    tests/test_always_fails.py:2: AssertionError
    =========================== short test summary info ============================
    FAILED tests/test_always_fails.py::test_always_fails - assert False
    1 failed in 1.66s
- PASS: testsuite-passes-when-tests-pass (FEATURE-TestSuite.md)
  intent: bin/test.sh exits zero for an application root whose only test passes.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/Quakes/runs/20261025.010423/build/Quakes/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    .                                                                        [100%]
    1 passed in 0.00s

## Build summary
I'll start by inspecting the build directory and the staged sources.The build directory already has prior-block output (`cli/`, `tests/`, `quakes`, `bin/`). I'll read what exists before changing anything.The prior blocks left a working skeleton, but `cli/__init__.py` doesn't parse arguments or write handler output yet, and `bin/test.sh` fails when `.venv` is missing (the spec says to fall back to the ambient interpreter). Next I'll check the environment and the baseline test run.Baseline is 23 passing. I'll now write the modules, starting with the error classes (adding the `QuakesError` base the exit-codes spec names).Next, the option parser. I'm hand-rolling it rather than using argparse, because argparse prints usage to stdout in some paths and its handling of numeric values like `-180` and `5.` doesn't match the grammar exactly.Next, the formatting module: UTC time, half-up decimal rounding through `Decimal(repr(x))`, and CSV via the `csv` module.Now the feed reader and event extraction, in `cli/feed.py`.One bug to fix before moving on: `UnicodeDecodeError` has no `strerror` attribute, so that message path would raise `AttributeError` instead of `OperationalError`.Next, `main` needs to parse, dispatch to the registered handler, and write handler text only on success. I'll move the UTF-8 stdout writer into `formatting.py` so `write_csv` and `main` share it.Now `bin/test.sh`: use `.venv` when present, otherwise the ambient interpreter, run `pytest -q` unfiltered, and drop the pass-through of arguments so nobody can add `-k` through it.The foundation tests register a handler named `demo`. Under the new grammar, `demo` is not a Quakes command, so I'll point those two tests at `daily` with a file argument. The assertions stay the same.Now the tests. I'm translating each declared acceptance assertion into a named pytest function and adding finer tests beside them. The options tests come first.The `test_fetch_options_must_have_a_value` test I just wrote is convoluted and doesn't test what its name says. I'll replace it with a simple truncation test, and drop the unused fixture from the file-system test.Next, the exit-code tests. They use `monkeypatch` for the handler registry instead of the manual save-and-restore in the spec, which is equivalent and cleaner.Two of those names don't match what they test. I'll fix them.Next, the formatting tests, including the write-to-buffer path for stdout.Next, the feed reader tests: the three declared assertions plus the specific failure branches.That last test asserts on message wording, which the test rules here forbid. I'll remove it.Now the event-extraction tests.Next, the magnitude-filter tests.Last, the test-suite runner tests. The spec's `runs-green` and `runs-from-other-directory` assertions would invoke `bin/test.sh` from inside the suite, which recurses without end. I'll cover the other-directory behavior on a temporary copy of the app that omits this file, and run the two recursive assertions once from the shell instead.Now I'll run the full suite and check the result.Most of these failures are my helper: `_make_root` doesn't create the parent directory. The other-directory case returned 1, so I need its output to see why.The copied app is missing the root `quakes` launcher and `uv.lock`, which the foundation tests check for. I'll copy those too.The suite passes: 191 tests, exit 0. Next I'll run the two spec assertions that recurse inside pytest, executed once from the shell. One runs `bin/test.sh` from an outside directory, and the other is the literal `runs-green` check.Both pass. Next I'll exercise the real launcher end to end, checking exit codes, empty stdout, and the single stderr line.The block is done. I'll close with the required result block and the decisions I made.

Summary of the work: I implemented the options parser, exit-code mapping, formatting, feed reading, event extraction, the magnitude filter, and the test runner. The suite has 191 tests and passes. I didn't commit anything.

**Checks run**
- `sh bin/test.sh` from the app root: 191 passed, exit 0.
- `sh bin/test.sh` from `/tmp`: exit 0 (the spec's other-directory assertion, run literally).
- The spec's `testsuite-runs-green` check, run literally: exit 0.
- `./quakes` usage paths: exit 2, empty stdout, one stderr line.
- Every declared acceptance assertion has a same-named pytest function that reads back values and compares them.
- I did not run `sources/run.sh`. It is the terminal check and needs the report commands, which belong to later blocks.

**Things you should know**
- `summary`, `top`, `daily`, `regions`, and `near` parse correctly, but no handler is registered yet, so they currently exit 2 with `command not available`. Later blocks register the handlers.
- Two spec assertions (`testsuite-runs-green` and `testsuite-runs-from-other-directory`) invoke `bin/test.sh` from inside the suite, which would recurse forever. I left them out of pytest, ran them from the shell, and covered the other-directory behavior in pytest on a temporary copy of the app.
- Two foundation tests registered a handler named `demo`, which the new grammar rejects. I changed them to use `daily` with a file argument. The assertions are unchanged.
- `bin/test.sh` no longer passes extra arguments through to pytest, so nobody can add `-k` to it.

<blueprint-decisions>
[{"spec":"FEATURE-Options.md","severity":"Low","subject":"Parser implementation and module","decision":"ARCHITECTURE names cli/options.py and the stack doc suggests argparse in parser.py. I hand-wrote the parser in cli/options.py so the number grammar, repeated options, and extra positionals follow the spec exactly and nothing prints. Is that acceptable?"},{"spec":"FEATURE-Options.md","severity":"Low","subject":"Date validation","decision":"Dates must match YYYY-MM-DD and also be real calendar dates (2025-02-30 is a usage error). The spec only states the pattern. Is that acceptable?"},{"spec":"FEATURE-EventExtraction.md","severity":"Low","subject":"Malformed feature handling","decision":"A feature missing id, properties, time, or coordinates raises OperationalError (exit 1) instead of a traceback. A null tsunami is read as 0, like a missing one. Is that acceptable?"},{"spec":"FEATURE-ExitCodes.md","severity":"Low","subject":"Valid command with no registered handler","decision":"Until report handlers are registered in later blocks, a valid command such as summary exits 2 with 'command not available'. I chose a usage error over a silent success. The later blocks will replace this when they register handlers. Is that acceptable?"}]
</blueprint-decisions>

RESULT: SUCCESS

FILES CHANGED:
- bin/test.sh
- cli/__init__.py
- cli/errors.py
- cli/feed.py
- cli/formatting.py
- cli/options.py
- tests/test_cli_foundation.py
- tests/test_event_extraction.py
- tests/test_exit_codes.py
- tests/test_feed.py
- tests/test_formatting.py
- tests/test_mag_filter.py
- tests/test_options.py
- tests/test_test_suite.py

SUMMARY:
Implemented Block 3 (Service): argument parsing with usage errors exiting 2; `main` dispatching to registered handlers, writing their output only on success, and mapping errors to exit codes 1 and 2 with one stderr line; UTC time, half-up rounding, and CSV formatting; GeoJSON feed reading and FeatureCollection validation; event extraction and the `--min-mag` filter; and `bin/test.sh` running `pytest -q` unfiltered. Verification: `sh bin/test.sh` gives 191 passed, exit 0. The other-directory and `runs-green` checks each exit 0 when run directly. `sources/` is untouched. No commit was made.

BLOCKERS:
- None.
