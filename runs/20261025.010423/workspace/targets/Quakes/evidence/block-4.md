# Evidence: Block 4 · Service (block-4)

- block type: block
- date: 2026-10-24
- resulting state: closed/verified
- story points (combined assembled cost): 27473
- execution id: 20261025.012504.037Z-353120db

## Stories built
- The summary report. (summary) [story]
- The regions report of events per region. (regions) [story]
- The daily report of events per UTC date. (daily) [story]
- The top report listing the largest events. (top) [story]
- The fetch command that downloads a USGS date range to a file. (fetch) [story]
- Fetch fails without writing a file on network, HTTP, or body errors. (fetch-failure) [story]
- The near report using haversine distance. (near) [story]

## Acceptance tooling authorization
- FEATURE-Summary.md#summary-values: executable=python3; scope=test; authorization=existing Target environment
- FEATURE-Summary.md#summary-mean-half-up: executable=python3; scope=test; authorization=existing Target environment
- FEATURE-Summary.md#summary-min-mag-filter: executable=python3; scope=test; authorization=existing Target environment
- FEATURE-Summary.md#summary-null-mag-excluded: executable=python3; scope=test; authorization=existing Target environment
- FEATURE-Summary.md#summary-empty: executable=python3; scope=test; authorization=existing Target environment
- FEATURE-Summary.md#summary-failure-codes: executable=python3; scope=test; authorization=existing Target environment
- FEATURE-Regions.md#regions-extract-and-order: executable=python3; scope=test; authorization=existing Target environment
- FEATURE-Regions.md#regions-place-rules: executable=python3; scope=test; authorization=existing Target environment
- FEATURE-Regions.md#regions-min-mag-and-empty: executable=python3; scope=test; authorization=existing Target environment
- FEATURE-Regions.md#regions-failure-contract: executable=python3; scope=test; authorization=existing Target environment
- FEATURE-Daily.md#daily-groups-by-utc-date: executable=python3; scope=test; authorization=existing Target environment
- FEATURE-Daily.md#daily-empty-report: executable=python3; scope=test; authorization=existing Target environment
- FEATURE-Daily.md#daily-min-mag-and-null-mag: executable=python3; scope=test; authorization=existing Target environment
- FEATURE-Daily.md#daily-failure-contract: executable=python3; scope=test; authorization=existing Target environment
- FEATURE-Top.md#top-order-and-default-n: executable=python3; scope=test; authorization=existing Target environment
- FEATURE-Top.md#top-n-option: executable=python3; scope=test; authorization=existing Target environment
- FEATURE-Top.md#top-min-mag-before-cut: executable=python3; scope=test; authorization=existing Target environment
- FEATURE-Top.md#top-place-with-comma: executable=python3; scope=test; authorization=existing Target environment
- FEATURE-Top.md#top-empty-result: executable=python3; scope=test; authorization=existing Target environment
- FEATURE-Top.md#top-usage-errors: executable=python3; scope=test; authorization=existing Target environment
- FEATURE-Fetch.md#fetch-saves-body-unchanged: executable=python3; scope=test; authorization=existing Target environment
- FEATURE-Fetch.md#fetch-request-url: executable=python3; scope=test; authorization=existing Target environment
- FEATURE-Fetch.md#fetch-min-mag-passthrough: executable=python3; scope=test; authorization=existing Target environment
- FEATURE-Fetch.md#fetch-usage-errors: executable=python3; scope=test; authorization=existing Target environment
- FEATURE-Fetch.md#fetch-http-get-uses-urllib: executable=python3; scope=test; authorization=existing Target environment
- FEATURE-FetchFailure.md#fetch-failure-http-status: executable=python3; scope=test; authorization=existing Target environment
- FEATURE-FetchFailure.md#fetch-failure-bad-body: executable=python3; scope=test; authorization=existing Target environment
- FEATURE-FetchFailure.md#fetch-failure-network-error: executable=python3; scope=test; authorization=existing Target environment
- FEATURE-FetchFailure.md#fetch-failure-http-error-status: executable=python3; scope=test; authorization=existing Target environment
- FEATURE-FetchFailure.md#fetch-failure-preserves-existing-file: executable=python3; scope=test; authorization=existing Target environment
- FEATURE-Near.md#near-haversine-distance-and-radius: executable=python3; scope=test; authorization=existing Target environment
- FEATURE-Near.md#near-ordering-ties-and-quoting: executable=python3; scope=test; authorization=existing Target environment
- FEATURE-Near.md#near-min-mag-null-mag-and-empty: executable=python3; scope=test; authorization=existing Target environment
- FEATURE-Near.md#near-usage-errors: executable=python3; scope=test; authorization=existing Target environment
- FEATURE-Near.md#near-unreadable-file: executable=python3; scope=test; authorization=existing Target environment

## Stacked context
- stack: python_compact.md (SP 921)
- compass: COMPASS.md (SP 986)
- implements: FEATURE-Summary.md (SP 3268)
- context: ARCHITECTURE_compact.md (SP 741)
- stack: cli.md (SP 2689)
- implements: FEATURE-Regions.md (SP 2748)
- implements: FEATURE-Daily.md (SP 3102)
- implements: FEATURE-Top.md (SP 3122)
- implements: FEATURE-Fetch.md (SP 3286)
- implements: FEATURE-FetchFailure.md (SP 2668)
- implements: FEATURE-Near.md (SP 3376)

## Build directory changes
- cli/__init__.py
- cli/feed.py
- cli/fetch.py
- cli/reports.py
- conftest.py
- tests/test_daily.py
- tests/test_fetch.py
- tests/test_fetch_failure.py
- tests/test_near.py
- tests/test_regions.py
- tests/test_summary.py
- tests/test_top.py

## Pre-build acceptance observation
- RED: summary-values (FEATURE-Summary.md)
  intent: The summary row carries count, time span, magnitude range, mean and tsunami count computed from the file.
  return code: 1
  stdout:
    error: command not available: 'summary'
  stderr:
    --- drydock: values at failure ---
      code = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "summary-values.py", line 27, in <module>
        assert code == 0
               ^^^^^^^^^
    AssertionError
- RED: summary-mean-half-up (FEATURE-Summary.md)
  intent: A mean falling exactly on a half cent is rounded up, not to even.
  return code: 1
  stdout:
    error: command not available: 'summary'
  stderr:
    --- drydock: values at failure ---
      code = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "summary-mean-half-up.py", line 18, in <module>
        assert code == 0
               ^^^^^^^^^
    AssertionError
- RED: summary-min-mag-filter (FEATURE-Summary.md)
  intent: --min-mag restricts the summary to events at or above the threshold.
  return code: 1
  stdout:
    error: command not available: 'summary'
  stderr:
    --- drydock: values at failure ---
      code = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "summary-min-mag-filter.py", line 19, in <module>
        assert code == 0
               ^^^^^^^^^
    AssertionError
- RED: summary-null-mag-excluded (FEATURE-Summary.md)
  intent: Features with a null magnitude are not counted.
  return code: 1
  stdout:
    error: command not available: 'summary'
  stderr:
    --- drydock: values at failure ---
      code = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "summary-null-mag-excluded.py", line 18, in <module>
        assert code == 0
               ^^^^^^^^^
    AssertionError
- RED: summary-empty (FEATURE-Summary.md)
  intent: When nothing matches, the report is a single row with a zero count and empty fields.
  return code: 1
  stdout:
    error: command not available: 'summary'
  stderr:
    --- drydock: values at failure ---
      code = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "summary-empty.py", line 17, in <module>
        assert code == 0
               ^^^^^^^^^
    AssertionError
- RED: summary-failure-codes (FEATURE-Summary.md)
  intent: An invalid file exits 1, an unlisted option or missing file exits 2, and stdout stays empty in both.
  return code: 1
  stderr:
    --- drydock: values at failure ---
      code = 2
      out = ''
    --- drydock: end values ---
    Traceback (most recent call last):
      File "summary-failure-codes.py", line 12, in <module>
        assert code == 1 and out == ""
               ^^^^^^^^^^^^^^^^^^^^^^^
    AssertionError
- RED: regions-extract-and-order (FEATURE-Regions.md)
  intent: Region is the text after the last comma-space, counts and maxima are per region, ordered by events descending then region by byte value.
  return code: 1
  stdout:
    error: command not available: 'regions'
  stderr:
    --- drydock: values at failure ---
      code = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "regions-extract-and-order.py", line 40, in <module>
        assert code == 0
               ^^^^^^^^^
    AssertionError
- RED: regions-place-rules (FEATURE-Regions.md)
  intent: A place with several commas splits on the last comma-space, a place without one is its own region, and a null place is Unknown.
  return code: 1
  stderr:
    --- drydock: values at failure ---
      code = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "regions-place-rules.py", line 29, in <module>
        assert code == 0
               ^^^^^^^^^
    AssertionError
- RED: regions-min-mag-and-empty (FEATURE-Regions.md)
  intent: --min-mag restricts the regions counted, null magnitudes are excluded, and an empty result is only the header with exit 0.
  return code: 1
  stderr:
    --- drydock: values at failure ---
      code = 2
      code_none = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "regions-min-mag-and-empty.py", line 28, in <module>
        assert code == 0 and code_none == 0
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    AssertionError
- RED: regions-failure-contract (FEATURE-Regions.md)
  intent: A file that is not a FeatureCollection exits 1 and an unlisted option exits 2, each with empty standard output.
  return code: 1
  stderr:
    --- drydock: values at failure ---
      code = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "regions-failure-contract.py", line 11, in <module>
        assert code == 1
               ^^^^^^^^^
    AssertionError
- RED: daily-groups-by-utc-date (FEATURE-Daily.md)
  intent: Events are grouped per UTC date with counts and maximum magnitude, ascending, followed by a TOTAL row.
  return code: 1
  stdout:
    error: command not available: 'daily'
  stderr:
    --- drydock: values at failure ---
      code = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "daily-groups-by-utc-date.py", line 47, in <module>
        assert code == 0
               ^^^^^^^^^
    AssertionError
- RED: daily-empty-report (FEATURE-Daily.md)
  intent: With no matching events the report is the header and a TOTAL row with zero events and an empty maximum, exit 0.
  return code: 1
  stderr:
    --- drydock: values at failure ---
      code = 2
      code2 = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "daily-empty-report.py", line 28, in <module>
        assert code == 0 and code2 == 0
               ^^^^^^^^^^^^^^^^^^^^^^^^
    AssertionError
- RED: daily-min-mag-and-null-mag (FEATURE-Daily.md)
  intent: --min-mag keeps only events with mag at or above it, and null-magnitude events are absent from rows and TOTAL.
  return code: 1
  stderr:
    --- drydock: values at failure ---
      code = 2
      code_all = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "daily-min-mag-and-null-mag.py", line 36, in <module>
        assert code == 0 and code_all == 0
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^
    AssertionError
- RED: daily-failure-contract (FEATURE-Daily.md)
  intent: An unreadable file exits 1 and an option daily does not take exits 2, both with empty standard output.
  return code: 1
  stderr:
    --- drydock: values at failure ---
      code = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "daily-failure-contract.py", line 9, in <module>
        assert code == 1
               ^^^^^^^^^
    AssertionError
- RED: top-order-and-default-n (FEATURE-Top.md)
  intent: Rows are sorted by magnitude descending then time ascending, and the default count is ten.
  return code: 1
  stdout:
    error: command not available: 'top'
  stderr:
    --- drydock: values at failure ---
      code = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "top-order-and-default-n.py", line 23, in <module>
        assert code == 0
               ^^^^^^^^^
    AssertionError
- RED: top-n-option (FEATURE-Top.md)
  intent: --n limits the number of rows written.
  return code: 1
  stdout:
    error: command not available: 'top'
  stderr:
    --- drydock: values at failure ---
      code = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "top-n-option.py", line 19, in <module>
        assert code == 0
               ^^^^^^^^^
    AssertionError
- RED: top-min-mag-before-cut (FEATURE-Top.md)
  intent: --min-mag filters before --n cuts the list.
  return code: 1
  stdout:
    error: command not available: 'top'
  stderr:
    --- drydock: values at failure ---
      code = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "top-min-mag-before-cut.py", line 20, in <module>
        assert code == 0
               ^^^^^^^^^
    AssertionError
- RED: top-place-with-comma (FEATURE-Top.md)
  intent: A place containing a comma round-trips through CSV quoting.
  return code: 1
  stdout:
    error: command not available: 'top'
  stderr:
    --- drydock: values at failure ---
      code = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "top-place-with-comma.py", line 18, in <module>
        assert code == 0
               ^^^^^^^^^
    AssertionError
- RED: top-empty-result (FEATURE-Top.md)
  intent: When no event matches, only the header is written and the exit status is 0.
  return code: 1
  stdout:
    error: command not available: 'top'
  stderr:
    --- drydock: values at failure ---
      code = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "top-empty-result.py", line 17, in <module>
        assert code == 0
               ^^^^^^^^^
    AssertionError
- GREEN (prepassed): top-usage-errors (FEATURE-Top.md)
  intent: A non-positive or malformed --n, an unlisted option, and a missing file all exit 2 with empty stdout.
  return code: 0
- RED: fetch-saves-body-unchanged (FEATURE-Fetch.md)
  intent: fetch writes the response body byte for byte to --out and prints fetched with the feature count; the HTTP call is stubbed.
  return code: 1
  stderr:
    --- drydock: values at failure ---
      p = 'fetch'
    --- drydock: end values ---
    Traceback (most recent call last):
      File "fetch-saves-body-unchanged.py", line 18, in <module>
        with mock.patch("cli.fetch.http_get", return_value=(200, body)) as stub:
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/home/barlo/.drydock/claude-home/.local/share/uv/python/cpython-3.12.13-linux-x86_64-gnu/lib/python3.12/unittest/mock.py", line 1451, in __enter__
        self.target = self.getter()
                      ^^^^^^^^^^^^^
      File "/home/barlo/.drydock/claude-home/.local/share/uv/python/cpython-3.12.13-linux-x86_64-gnu/lib/python3.12/pkgutil.py", line 528, in resolve_name
        result = getattr(result, p)
                 ^^^^^^^^^^^^^^^^^^
    AttributeError: module 'cli' has no attribute 'fetch'
- RED: fetch-request-url (FEATURE-Fetch.md)
  intent: The request goes to the USGS FDSN query endpoint with the GeoJSON format, the given dates, the default minimum magnitude, and time ascending order.
  return code: 1
  stderr:
    --- drydock: values at failure ---
      p = 'fetch'
    --- drydock: end values ---
    Traceback (most recent call last):
      File "fetch-request-url.py", line 14, in <module>
        with mock.patch("cli.fetch.http_get", return_value=(200, body)) as stub:
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/home/barlo/.drydock/claude-home/.local/share/uv/python/cpython-3.12.13-linux-x86_64-gnu/lib/python3.12/unittest/mock.py", line 1451, in __enter__
        self.target = self.getter()
                      ^^^^^^^^^^^^^
      File "/home/barlo/.drydock/claude-home/.local/share/uv/python/cpython-3.12.13-linux-x86_64-gnu/lib/python3.12/pkgutil.py", line 528, in resolve_name
        result = getattr(result, p)
                 ^^^^^^^^^^^^^^^^^^
    AttributeError: module 'cli' has no attribute 'fetch'
- RED: fetch-min-mag-passthrough (FEATURE-Fetch.md)
  intent: An explicit --min-mag value is sent as minmagnitude, and build_url builds the same query directly.
  return code: 1
  stderr:
    Traceback (most recent call last):
      File "fetch-min-mag-passthrough.py", line 7, in <module>
        from cli.fetch import build_url
    ModuleNotFoundError: No module named 'cli.fetch'
- RED: fetch-usage-errors (FEATURE-Fetch.md)
  intent: Missing required options, an unlisted option, or an extra positional argument exit 2, make no HTTP call, and write no file.
  return code: 1
  stderr:
    --- drydock: values at failure ---
      p = 'fetch'
    --- drydock: end values ---
    Traceback (most recent call last):
      File "fetch-usage-errors.py", line 17, in <module>
        with mock.patch("cli.fetch.http_get", return_value=(200, b"{}")) as stub:
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/home/barlo/.drydock/claude-home/.local/share/uv/python/cpython-3.12.13-linux-x86_64-gnu/lib/python3.12/unittest/mock.py", line 1451, in __enter__
        self.target = self.getter()
                      ^^^^^^^^^^^^^
      File "/home/barlo/.drydock/claude-home/.local/share/uv/python/cpython-3.12.13-linux-x86_64-gnu/lib/python3.12/pkgutil.py", line 528, in resolve_name
        result = getattr(result, p)
                 ^^^^^^^^^^^^^^^^^^
    AttributeError: module 'cli' has no attribute 'fetch'
- RED: fetch-http-get-uses-urllib (FEATURE-Fetch.md)
  intent: http_get returns the status and body from urllib.request.urlopen, which is stubbed so no network connection is opened.
  return code: 1
  stderr:
    Traceback (most recent call last):
      File "fetch-http-get-uses-urllib.py", line 3, in <module>
        from cli.fetch import http_get
    ModuleNotFoundError: No module named 'cli.fetch'
- RED: fetch-failure-http-status (FEATURE-FetchFailure.md)
  intent: A non-200 status exits 1 with empty standard output, one stderr line, and no file written.
  return code: 1
  stderr:
    --- drydock: values at failure ---
      p = 'fetch'
    --- drydock: end values ---
    Traceback (most recent call last):
      File "fetch-failure-http-status.py", line 12, in <module>
        with mock.patch("cli.fetch.http_get", return_value=(bad_status, valid)):
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/home/barlo/.drydock/claude-home/.local/share/uv/python/cpython-3.12.13-linux-x86_64-gnu/lib/python3.12/unittest/mock.py", line 1451, in __enter__
        self.target = self.getter()
                      ^^^^^^^^^^^^^
      File "/home/barlo/.drydock/claude-home/.local/share/uv/python/cpython-3.12.13-linux-x86_64-gnu/lib/python3.12/pkgutil.py", line 528, in resolve_name
        result = getattr(result, p)
                 ^^^^^^^^^^^^^^^^^^
    AttributeError: module 'cli' has no attribute 'fetch'
- RED: fetch-failure-bad-body (FEATURE-FetchFailure.md)
  intent: A body that is not JSON, or JSON that is not a FeatureCollection, exits 1 and writes no file.
  return code: 1
  stderr:
    --- drydock: values at failure ---
      p = 'fetch'
    --- drydock: end values ---
    Traceback (most recent call last):
      File "fetch-failure-bad-body.py", line 18, in <module>
        with mock.patch("cli.fetch.http_get", return_value=(200, body)):
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/home/barlo/.drydock/claude-home/.local/share/uv/python/cpython-3.12.13-linux-x86_64-gnu/lib/python3.12/unittest/mock.py", line 1451, in __enter__
        self.target = self.getter()
                      ^^^^^^^^^^^^^
      File "/home/barlo/.drydock/claude-home/.local/share/uv/python/cpython-3.12.13-linux-x86_64-gnu/lib/python3.12/pkgutil.py", line 528, in resolve_name
        result = getattr(result, p)
                 ^^^^^^^^^^^^^^^^^^
    AttributeError: module 'cli' has no attribute 'fetch'
- RED: fetch-failure-network-error (FEATURE-FetchFailure.md)
  intent: A network error from a stubbed http_get, and a URLError from a patched urlopen, both exit 1 with no file written.
  return code: 1
  stderr:
    --- drydock: values at failure ---
      p = 'fetch'
    --- drydock: end values ---
    Traceback (most recent call last):
      File "fetch-failure-network-error.py", line 10, in <module>
        with mock.patch("cli.fetch.http_get", side_effect=OSError("unreachable")):
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/home/barlo/.drydock/claude-home/.local/share/uv/python/cpython-3.12.13-linux-x86_64-gnu/lib/python3.12/unittest/mock.py", line 1451, in __enter__
        self.target = self.getter()
                      ^^^^^^^^^^^^^
      File "/home/barlo/.drydock/claude-home/.local/share/uv/python/cpython-3.12.13-linux-x86_64-gnu/lib/python3.12/pkgutil.py", line 528, in resolve_name
        result = getattr(result, p)
                 ^^^^^^^^^^^^^^^^^^
    AttributeError: module 'cli' has no attribute 'fetch'
- RED: fetch-failure-http-error-status (FEATURE-FetchFailure.md)
  intent: An HTTPError raised by urlopen is treated as a non-200 status, exits 1, and writes no file.
  return code: 1
  stderr:
    --- drydock: values at failure ---
      code = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "fetch-failure-http-error-status.py", line 14, in <module>
        assert code == 1
               ^^^^^^^^^
    AssertionError
- RED: fetch-failure-preserves-existing-file (FEATURE-FetchFailure.md)
  intent: A failed fetch leaves a pre-existing output file byte-for-byte untouched.
  return code: 1
  stderr:
    --- drydock: values at failure ---
      p = 'fetch'
    --- drydock: end values ---
    Traceback (most recent call last):
      File "fetch-failure-preserves-existing-file.py", line 12, in <module>
        with mock.patch("cli.fetch.http_get", return_value=(404, b"missing")):
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/home/barlo/.drydock/claude-home/.local/share/uv/python/cpython-3.12.13-linux-x86_64-gnu/lib/python3.12/unittest/mock.py", line 1451, in __enter__
        self.target = self.getter()
                      ^^^^^^^^^^^^^
      File "/home/barlo/.drydock/claude-home/.local/share/uv/python/cpython-3.12.13-linux-x86_64-gnu/lib/python3.12/pkgutil.py", line 528, in resolve_name
        result = getattr(result, p)
                 ^^^^^^^^^^^^^^^^^^
    AttributeError: module 'cli' has no attribute 'fetch'
- RED: near-haversine-distance-and-radius (FEATURE-Near.md)
  intent: Reported distances match an independent haversine on a 6371.0 km sphere, and only events within the radius are listed, nearest first.
  return code: 1
  stdout:
    error: command not available: 'near'
  stderr:
    --- drydock: values at failure ---
      code = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "near-haversine-distance-and-radius.py", line 48, in <module>
        assert code == 0
               ^^^^^^^^^
    AssertionError
- RED: near-ordering-ties-and-quoting (FEATURE-Near.md)
  intent: Events at equal distance are ordered by time ascending, and a place containing a comma round-trips through CSV quoting.
  return code: 1
  stderr:
    --- drydock: values at failure ---
      code = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "near-ordering-ties-and-quoting.py", line 27, in <module>
        assert code == 0
               ^^^^^^^^^
    AssertionError
- RED: near-min-mag-null-mag-and-empty (FEATURE-Near.md)
  intent: --min-mag filters near results, null magnitudes never appear, and no match yields only the header with exit 0.
  return code: 1
  stderr:
    --- drydock: values at failure ---
      code = 2
      code_e = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "near-min-mag-null-mag-and-empty.py", line 30, in <module>
        assert code == 0 and code_e == 0
               ^^^^^^^^^^^^^^^^^^^^^^^^^
    AssertionError
- GREEN (prepassed): near-usage-errors (FEATURE-Near.md)
  intent: Missing required options and out-of-range values exit 2 with empty standard output.
  return code: 0
- RED: near-unreadable-file (FEATURE-Near.md)
  intent: An unreadable file is an operational failure: exit 1 with empty standard output.
  return code: 1
  stderr:
    --- drydock: values at failure ---
      code = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "near-unreadable-file.py", line 9, in <module>
        assert code == 1
               ^^^^^^^^^
    AssertionError

## Post-build programmatic acceptance
- PASS: summary-values (FEATURE-Summary.md)
  intent: The summary row carries count, time span, magnitude range, mean and tsunami count computed from the file.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/Quakes/runs/20261025.010423/build/Quakes/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    events,first,last,min_mag,max_mag,mean_mag,tsunami
    4,2025-01-01T01:00:00Z,2025-01-01T09:00:00Z,5.0,6.5,5.50,2
- PASS: summary-mean-half-up (FEATURE-Summary.md)
  intent: A mean falling exactly on a half cent is rounded up, not to even.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/Quakes/runs/20261025.010423/build/Quakes/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    events,first,last,min_mag,max_mag,mean_mag,tsunami
    8,2025-01-01T00:00:00Z,2025-01-01T00:00:07Z,5.0,6.0,5.13,0
- PASS: summary-min-mag-filter (FEATURE-Summary.md)
  intent: --min-mag restricts the summary to events at or above the threshold.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/Quakes/runs/20261025.010423/build/Quakes/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    events,first,last,min_mag,max_mag,mean_mag,tsunami
    3,2025-01-01T00:00:02Z,2025-01-01T00:00:04Z,5.5,7.1,6.20,0
- PASS: summary-null-mag-excluded (FEATURE-Summary.md)
  intent: Features with a null magnitude are not counted.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/Quakes/runs/20261025.010423/build/Quakes/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    events,first,last,min_mag,max_mag,mean_mag,tsunami
    2,2025-01-01T00:00:00Z,2025-01-01T00:00:02Z,5.0,6.0,5.50,0
- PASS: summary-empty (FEATURE-Summary.md)
  intent: When nothing matches, the report is a single row with a zero count and empty fields.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/Quakes/runs/20261025.010423/build/Quakes/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    events,first,last,min_mag,max_mag,mean_mag,tsunami
    0,,,,,,0
- PASS: summary-failure-codes (FEATURE-Summary.md)
  intent: An invalid file exits 1, an unlisted option or missing file exits 2, and stdout stays empty in both.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/Quakes/runs/20261025.010423/build/Quakes/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: regions-extract-and-order (FEATURE-Regions.md)
  intent: Region is the text after the last comma-space, counts and maxima are per region, ordered by events descending then region by byte value.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/Quakes/runs/20261025.010423/build/Quakes/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    region,events,max_mag
    Gamma,3,5.9
    Beta,2,5.2
    Zed,2,5.6
    Delta,1,5.4
    alpha,1,5.1
- PASS: regions-place-rules (FEATURE-Regions.md)
  intent: A place with several commas splits on the last comma-space, a place without one is its own region, and a null place is Unknown.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/Quakes/runs/20261025.010423/build/Quakes/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    region,events,max_mag
    "A,B",1,5.0
    Country,1,5.0
    Mid-Atlantic Ridge,1,5.0
    Unknown,1,5.0
- PASS: regions-min-mag-and-empty (FEATURE-Regions.md)
  intent: --min-mag restricts the regions counted, null magnitudes are excluded, and an empty result is only the header with exit 0.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/Quakes/runs/20261025.010423/build/Quakes/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    region,events,max_mag
    Aland,1,5.4
    Bland,1,6.0
- PASS: regions-failure-contract (FEATURE-Regions.md)
  intent: A file that is not a FeatureCollection exits 1 and an unlisted option exits 2, each with empty standard output.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/Quakes/runs/20261025.010423/build/Quakes/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: daily-groups-by-utc-date (FEATURE-Daily.md)
  intent: Events are grouped per UTC date with counts and maximum magnitude, ascending, followed by a TOTAL row.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/Quakes/runs/20261025.010423/build/Quakes/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    date,events,max_mag
    2025-01-01,2,6.1
    2025-01-03,2,5.5
    2025-01-07,1,5.2
    TOTAL,5,6.1
- PASS: daily-empty-report (FEATURE-Daily.md)
  intent: With no matching events the report is the header and a TOTAL row with zero events and an empty maximum, exit 0.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/Quakes/runs/20261025.010423/build/Quakes/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    date,events,max_mag
    TOTAL,0,
     date,events,max_mag
    TOTAL,0,
- PASS: daily-min-mag-and-null-mag (FEATURE-Daily.md)
  intent: --min-mag keeps only events with mag at or above it, and null-magnitude events are absent from rows and TOTAL.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/Quakes/runs/20261025.010423/build/Quakes/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    date,events,max_mag
    2025-01-01,1,5.4
    2025-01-02,1,6.0
    TOTAL,2,6.0
    
    date,events,max_mag
    2025-01-01,2,5.4
    2025-01-02,1,6.0
    2025-01-04,1,5.3
    TOTAL,4,6.0
- PASS: daily-failure-contract (FEATURE-Daily.md)
  intent: An unreadable file exits 1 and an option daily does not take exits 2, both with empty standard output.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/Quakes/runs/20261025.010423/build/Quakes/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: top-order-and-default-n (FEATURE-Top.md)
  intent: Rows are sorted by magnitude descending then time ascending, and the default count is ten.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/Quakes/runs/20261025.010423/build/Quakes/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    time,mag,depth_km,place,id
    2025-01-01T01:00:00Z,7.0,12.0,P,f
    2025-01-01T00:10:00Z,6.0,12.0,P,c
    2025-01-01T00:40:00Z,6.0,12.0,P,b
    2025-01-01T00:35:00Z,5.8,12.0,P,l
    2025-01-01T00:25:00Z,5.7,12.0,P,k
    2025-01-01T00:15:00Z,5.6,12.0,P,j
    2025-01-01T00:30:00Z,5.5,12.0,P,d
    2025-01-01T01:30:00Z,5.4,12.0,P,i
    2025-01-01T01:20:00Z,5.3,12.0,P,h
    2025-01-01T01:10:00Z,5.2,12.0,P,g
- PASS: top-n-option (FEATURE-Top.md)
  intent: --n limits the number of rows written.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/Quakes/runs/20261025.010423/build/Quakes/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    time,mag,depth_km,place,id
    2025-01-01T00:00:02Z,7.1,5.0,P,c
    2025-01-01T00:00:04Z,6.2,5.0,P,e
    2025-01-01T00:00:01Z,6.0,5.0,P,b
- PASS: top-min-mag-before-cut (FEATURE-Top.md)
  intent: --min-mag filters before --n cuts the list.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/Quakes/runs/20261025.010423/build/Quakes/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    time,mag,depth_km,place,id
    2025-01-01T00:00:04Z,7.0,5.0,P,e
    2025-01-01T00:00:03Z,6.0,5.0,P,d
    2025-01-01T00:00:02Z,5.2,5.0,P,c
    2025-01-01T00:00:01Z,5.1,5.0,P,b
- PASS: top-place-with-comma (FEATURE-Top.md)
  intent: A place containing a comma round-trips through CSV quoting.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/Quakes/runs/20261025.010423/build/Quakes/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    time,mag,depth_km,place,id
    2025-01-01T00:00:00Z,6.2,46.0,"56 km SSE of Some Town, Some Country",c1
- PASS: top-empty-result (FEATURE-Top.md)
  intent: When no event matches, only the header is written and the exit status is 0.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/Quakes/runs/20261025.010423/build/Quakes/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    time,mag,depth_km,place,id
- PASS: top-usage-errors (FEATURE-Top.md)
  intent: A non-positive or malformed --n, an unlisted option, and a missing file all exit 2 with empty stdout.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/Quakes/runs/20261025.010423/build/Quakes/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: fetch-saves-body-unchanged (FEATURE-Fetch.md)
  intent: fetch writes the response body byte for byte to --out and prints fetched with the feature count; the HTTP call is stubbed.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/Quakes/runs/20261025.010423/build/Quakes/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    fetched,3
- PASS: fetch-request-url (FEATURE-Fetch.md)
  intent: The request goes to the USGS FDSN query endpoint with the GeoJSON format, the given dates, the default minimum magnitude, and time ascending order.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/Quakes/runs/20261025.010423/build/Quakes/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: fetch-min-mag-passthrough (FEATURE-Fetch.md)
  intent: An explicit --min-mag value is sent as minmagnitude, and build_url builds the same query directly.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/Quakes/runs/20261025.010423/build/Quakes/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: fetch-usage-errors (FEATURE-Fetch.md)
  intent: Missing required options, an unlisted option, or an extra positional argument exit 2, make no HTTP call, and write no file.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/Quakes/runs/20261025.010423/build/Quakes/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: fetch-http-get-uses-urllib (FEATURE-Fetch.md)
  intent: http_get returns the status and body from urllib.request.urlopen, which is stubbed so no network connection is opened.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/Quakes/runs/20261025.010423/build/Quakes/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: fetch-failure-http-status (FEATURE-FetchFailure.md)
  intent: A non-200 status exits 1 with empty standard output, one stderr line, and no file written.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/Quakes/runs/20261025.010423/build/Quakes/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    error: USGS responded with HTTP status 500
- PASS: fetch-failure-bad-body (FEATURE-FetchFailure.md)
  intent: A body that is not JSON, or JSON that is not a FeatureCollection, exits 1 and writes no file.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/Quakes/runs/20261025.010423/build/Quakes/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: fetch-failure-network-error (FEATURE-FetchFailure.md)
  intent: A network error from a stubbed http_get, and a URLError from a patched urlopen, both exit 1 with no file written.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/Quakes/runs/20261025.010423/build/Quakes/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: fetch-failure-http-error-status (FEATURE-FetchFailure.md)
  intent: An HTTPError raised by urlopen is treated as a non-200 status, exits 1, and writes no file.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/Quakes/runs/20261025.010423/build/Quakes/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: fetch-failure-preserves-existing-file (FEATURE-FetchFailure.md)
  intent: A failed fetch leaves a pre-existing output file byte-for-byte untouched.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/Quakes/runs/20261025.010423/build/Quakes/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: near-haversine-distance-and-radius (FEATURE-Near.md)
  intent: Reported distances match an independent haversine on a 6371.0 km sphere, and only events within the radius are listed, nearest first.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/Quakes/runs/20261025.010423/build/Quakes/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    distance_km,time,mag,place,id
    214.1,2025-01-06T21:46:42Z,5.2,Place near1,near1
    217.2,2025-01-06T21:46:43Z,5.3,Place near2,near2
    223.5,2025-01-06T21:46:41Z,5.1,Place mid,mid
- PASS: near-ordering-ties-and-quoting (FEATURE-Near.md)
  intent: Events at equal distance are ordered by time ascending, and a place containing a comma round-trips through CSV quoting.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/Quakes/runs/20261025.010423/build/Quakes/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    distance_km,time,mag,place,id
    54.8,2025-01-06T21:46:41Z,5.0,"10 km N of Somewhere, Country",t1
    54.8,2025-01-06T21:46:42Z,5.0,"10 km N of Somewhere, Country",t2
    54.8,2025-01-06T21:46:43Z,5.0,"10 km N of Somewhere, Country",t0
- PASS: near-min-mag-null-mag-and-empty (FEATURE-Near.md)
  intent: --min-mag filters near results, null magnitudes never appear, and no match yields only the header with exit 0.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/Quakes/runs/20261025.010423/build/Quakes/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    distance_km,time,mag,place,id
    0.0,2025-01-06T21:46:40Z,5.3,P1,m1
    0.0,2025-01-06T21:46:40Z,6.0,P2,m2
- PASS: near-usage-errors (FEATURE-Near.md)
  intent: Missing required options and out-of-range values exit 2 with empty standard output.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/Quakes/runs/20261025.010423/build/Quakes/.venv/bin/python
  provisioning: not required
  return code: 0
- PASS: near-unreadable-file (FEATURE-Near.md)
  intent: An unreadable file is an operational failure: exit 1 with empty standard output.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/Quakes/runs/20261025.010423/build/Quakes/.venv/bin/python
  provisioning: not required
  return code: 0

## Build summary
I'll start by inspecting the build directory to see what already exists from earlier blocks.The earlier blocks left a `cli/` package, tests, and a `quakes` launcher. I'll read those next, since this block builds on them.The handler registry `COMMANDS` is empty, so this block needs to register the six report/fetch handlers. Before writing anything, I'll check the baseline test state and the existing test-suite test.Baseline is green (191 passed). The plan, based on ARCHITECTURE and the feature specs:

- `cli/reports.py`: pure `compute_*` row builders, `region_of`, `haversine_km`, and one handler per report.
- `cli/fetch.py`: `build_url`, `http_get`, and the `fetch` handler. Body validation reuses the `read_feed` rules, so I'll pull that logic into a `features_from_text` helper in `feed.py`.
- `cli/__init__.py`: register the six handlers in `COMMANDS`.

Starting with the `feed.py` refactor:Next, the report module with the pure row builders, `haversine_km`, and the per-command handlers.Now the fetch module. `http_get` is the only network call, and the handler writes the file only after validation passes.Registering the six handlers in `COMMANDS`, keeping the same dict object so the existing monkeypatch-based tests still apply.Next, the tests. I'll add a shared `write_feed` fixture to `conftest.py` so the per-report test files don't each repeat the file-writing code.Importing helpers out of `conftest.py` is fragile, so I'll keep only the fixture there and give each test module its own small feature builder.Now the summary tests: the declared `summary-*` acceptance assertions, plus finer checks on the empty report and the `tsunami` count.One assertion I just wrote is sloppy: the `or` makes it accept either of two values. 6.25 rounds half-up to 6.3, so I'll pin that exactly.Next, the regions tests: the declared `regions-*` assertions, plus direct checks of `region_of`.The regions test has a mid-function import, which doesn't match the file's style. I'll move it to the top.Daily tests next, covering the UTC grouping boundary and the TOTAL row, including the empty case.Top tests: the declared `top-*` assertions, plus a check that `--n` is applied after filtering and that sort ties break on time.Now the fetch tests, covering the declared `fetch-*` assertions and the `http_get` contract with `urlopen` stubbed.I left a pointless `cli.testing` import in that file. The `cli_runner` fixture already supplies the helper, so I'll remove it.Next, the fetch-failure tests. These cover the five declared assertions, which check that no file is created or altered on network, HTTP, or body errors.Last, the near tests: the declared `near-*` assertions, plus a check of `haversine_km` against known distances.One comment in the antipodal test claims a rounding cause that doesn't apply to this exact input (h is exactly 1). I'll correct it before running anything.Everything is written. Now I'll run the full project suite via its declared runner, which is the gate for every story here.The suite passes: 256 tests, up from 191 at baseline. Next I'll run the real `quakes` binary against the staged snapshot for a few reports, to confirm the output on real data. I'm not invoking `sources/run.sh` here, since no criterion in this block calls it.The real snapshot output matches the known answers I can see in the staged run.sh (A1 summary, A2 top, A3 daily totals, C1 near rows). Last, I'll confirm which files changed, without touching git history.The block 4 stories are built and the project suite is green: 256 passed (191 before this block, 65 added). `bin/test.sh` exits 0.

**What was built**

- **`cli/reports.py`**: the `summary`, `regions`, `daily`, `top`, and `near` reports. Each is a pure `compute_*` row builder plus a handler. Also `region_of` and `haversine_km` (6371.0 km sphere).
- **`cli/fetch.py`**: `build_url`, `http_get` (the only network call, via `urllib.request.urlopen`), and the `fetch` handler. The handler validates the body and writes the file only after validation passes.
- **`cli/feed.py`**: I pulled the FeatureCollection validation out of `read_feed` into `features_from_text`, so `fetch` applies the same rules to the response body. Error messages for files are unchanged.
- **`cli/__init__.py`**: registers the six handlers in `COMMANDS`. Monkeypatched tests still apply because it is the same dict object.
- **Tests**: `conftest.py` gains a `write_feed` fixture. Seven new test modules, one per story group, hold every declared acceptance assertion as a pytest function, plus finer coverage (region splitting, UTC date boundaries, haversine values, URL shape, failure cases).

**Checks run**

- `sh bin/test.sh`: 256 passed, exit 0.
- `./quakes` on the staged snapshot: the summary, daily totals, first rows of `top`, and first rows of `near` match the values in `sources/run.sh`. I did not run `sources/run.sh` itself, because no criterion in this block invokes it.

**Decision for you (Low, FEATURE-Fetch.md):** the spec says `minmagnitude` should carry the text given on the command line. `Parsed` stores a float, so I send `str(float)`. That means `--min-mag 5` goes out as `minmagnitude=5.0`. USGS accepts this, and the declared ACs (`4.5`, default `2.5`) are unaffected. If you want the exact text, `Parsed` needs a raw-text field added in `options.py`.

RESULT: SUCCESS

FILES CHANGED:
- cli/__init__.py
- cli/feed.py
- cli/fetch.py
- cli/reports.py
- conftest.py
- tests/test_summary.py
- tests/test_regions.py
- tests/test_daily.py
- tests/test_top.py
- tests/test_fetch.py
- tests/test_fetch_failure.py
- tests/test_near.py

SUMMARY:
Implemented the summary, regions, daily, top, near, and fetch commands with fetch failure handling, following FEATURE-Summary/Regions/Daily/Top/Fetch/FetchFailure/Near. Declared acceptance assertions are reproduced as pytest functions. `bin/test.sh`: 256 passed (65 new). No git history was touched.

<blueprint-decisions>
[{"spec":"FEATURE-Fetch.md","severity":"Low","subject":"minmagnitude text","decision":"The spec says minmagnitude carries the text given on the command line. Parsed stores a float, so the fetch handler sends str(float). `--min-mag 5` therefore goes out as `5.0`. The declared ACs (4.5 and the 2.5 default) pass. Acceptable, or should Parsed keep the raw text?"}]
</blueprint-decisions>
