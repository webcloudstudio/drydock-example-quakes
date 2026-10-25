# Scorecard: Quakes

## Specification

> **NOT YET RUN**
> drydock score spec Quakes

## Acceptance

> **PASSED**
> drydock score ac Quakes · 2026-10-25T01:35:03.929+00:00

PASS 63   FAIL 0   UNVERIFIED 0   PREPASSED 15   (78 AC total)

## Build

> **RECORDED**
> drydock score build Quakes

Blocks: 5   Repaired: 0   Failed: 0
Tokens: 5,188,116 (cached 5,069,634, output 118,322)   Cache hit rate: 100.0%

## Release

> **RELEASED**
> drydock score release Quakes · 2026-10-25T01:37:00.399+00:00

- Verdict: PASSED

Quakes: PASSED — 8 of 8

  st-001  MET       ["sh", "sources/run.sh"] exited 0; run.sh governed gate: outcome PASS, return_code 0, stdout 'Quakes: 26 passed, 0 failed (of 26)'; sources/run.sh:204 exits 0 only when FAILED is 0; run.sh:40 compares exit code and stdout with cmp for every check, so the stdout comparison is real
  st-002  MET       bin/test.sh: run in this tree, output '256 passed in 25.37s', exit 0; bin/test.sh:1-2 is /bin/sh with `set -eu`, `$(...)`, and `.` for the venv; no bash-only constructs
  st-003  MET       run.sh A1-A4 (summary, top, daily, regions over the full snapshot): PASS, compared with cmp; run.sh B1-B5 (top --n, summary/regions/daily/top with --min-mag): PASS; cli/reports.py:48-102 builds each report's CSV from compute_* with fixed headers; formatting goes through render_csv with \n line endings
  st-004  MET       cli/reports.py:EARTH_RADIUS_KM = 6371.0; haversine_km implements the haversine formula in radians; probe near_probe.py: haversine(0,0,0,1) = 111.19492664455873 = 6371*pi/180; pole-to-equator = 10007.5434 = pi*6371/2; probe near_probe.py: max deviation from textbook over 2000 random pairs = 2.5e-11 km; probe near_probe.py: compute_near on 300 random events returned the same 11 ids as brute force, distances ascending; run.sh C1-C4 (near over the snapshot, including the zero-hit case): PASS
  st-005  MET       cli/reports.py:load_events applies filter_events(extract_events(read_feed(path)), min_mag); cli/reports.py: summary_command, top_command, daily_command, regions_command, and near_command all call load_events(parsed.file, parsed.min_mag); run.sh B2 (summary --min-mag 5.5), B3 (regions --min-mag 5.4), B4 (daily --min-mag 6), B5 (top --min-mag 5.1): PASS
  st-006  MET       cli/fetch.py:FEED_URL is https://earthquake.usgs.gov/fdsnws/event/1/query with format=geojson; probe built the URL from --start/--end; probe fetch_probe.py: with urlopen stubbed, the written file was byte-identical to the response body (including trailing whitespace and CRLF); probe fetch_probe.py: HTTP 503 raised OperationalError and left no file; URLError raised OperationalError and left no file; cli/fetch.py:fetch_command validates the body before write_bytes, so a bad body never touches the output path
  st-007  MET       run.sh E1 (missing file), E2 (non-JSON), E3 (Feature, not FeatureCollection): exit 1 expected and matched, stdout compared empty against /dev/null: PASS; run.sh U1-U8 (no command, unknown command, missing --radius, --n 0, bad --min-mag, out-of-range --lat, stray option, missing file argument): exit 2 expected and matched, stdout empty: PASS; cli/__init__.py:main writes the handler's text only after it returns, and QuakesError paths print only to stderr
  st-008  MET       probe nonet_probe.py: pytest over tests/ exit 0, 256 passed, connection attempts: []; tests/test_fetch.py:46,59,78,100: fetch tests patch cli.fetch.http_get; tests/test_fetch.py:109-113 and tests/test_fetch_failure.py:58,69: the one http_get test patches urllib.request.urlopen with a FakeResponse

## Project acceptance

| ID | Type | Criterion | Verdict | Observed |
|---|---|---|---|---|
| st-001 | technical | The completed quakes shall make sh sources/run.sh exit zero; that script's exit status is the sole acceptance verdict. | MET | ["sh", "sources/run.sh"] exited 0; run.sh governed gate: outcome PASS, return_code 0, stdout 'Quakes: 26 passed, 0 failed (of 26)'; sources/run.sh:204 exits 0 only when FAILED is 0; run.sh:40 compares exit code and stdout with cmp for every check, so the stdout comparison is real |
| st-002 | technical | The application shall provide a POSIX-compatible bin/test.sh that exits zero when every automated test passes. | MET | bin/test.sh: run in this tree, output '256 passed in 25.37s', exit 0; bin/test.sh:1-2 is /bin/sh with `set -eu`, `$(...)`, and `.` for the venv; no bash-only constructs |
| st-003 | behavioral | The application shall compute the summary, top, daily, and regions reports from the snapshot, matching the known answers in sources/run.sh byte for byte. | MET | run.sh A1-A4 (summary, top, daily, regions over the full snapshot): PASS, compared with cmp; run.sh B1-B5 (top --n, summary/regions/daily/top with --min-mag): PASS; cli/reports.py:48-102 builds each report's CSV from compute_* with fixed headers; formatting goes through render_csv with \n line endings |
| st-004 | behavioral | When near is given a point and a radius, the application shall list every event within that haversine distance on a 6371.0 km sphere, nearest first. | MET | cli/reports.py:EARTH_RADIUS_KM = 6371.0; haversine_km implements the haversine formula in radians; probe near_probe.py: haversine(0,0,0,1) = 111.19492664455873 = 6371*pi/180; pole-to-equator = 10007.5434 = pi*6371/2; probe near_probe.py: max deviation from textbook over 2000 random pairs = 2.5e-11 km; probe near_probe.py: compute_near on 300 random events returned the same 11 ids as brute force, distances ascending; run.sh C1-C4 (near over the snapshot, including the zero-hit case): PASS |
| st-005 | behavioral | When --min-mag is given, the application shall compute every report over only the events whose magnitude is at least that value. | MET | cli/reports.py:load_events applies filter_events(extract_events(read_feed(path)), min_mag); cli/reports.py: summary_command, top_command, daily_command, regions_command, and near_command all call load_events(parsed.file, parsed.min_mag); run.sh B2 (summary --min-mag 5.5), B3 (regions --min-mag 5.4), B4 (daily --min-mag 6), B5 (top --min-mag 5.1): PASS |
| st-006 | behavioral | When fetch is given a date range, the application shall request the USGS FDSN event query in GeoJSON and write the response unchanged to the output file, writing no file on a network or HTTP failure. | MET | cli/fetch.py:FEED_URL is https://earthquake.usgs.gov/fdsnws/event/1/query with format=geojson; probe built the URL from --start/--end; probe fetch_probe.py: with urlopen stubbed, the written file was byte-identical to the response body (including trailing whitespace and CRLF); probe fetch_probe.py: HTTP 503 raised OperationalError and left no file; URLError raised OperationalError and left no file; cli/fetch.py:fetch_command validates the body before write_bytes, so a bad body never touches the output path |
| st-007 | behavioral | If the file is unreadable or not a GeoJSON FeatureCollection, then the application shall exit 1; if the arguments are malformed, then the application shall exit 2; in both cases it shall write nothing to standard output. | MET | run.sh E1 (missing file), E2 (non-JSON), E3 (Feature, not FeatureCollection): exit 1 expected and matched, stdout compared empty against /dev/null: PASS; run.sh U1-U8 (no command, unknown command, missing --radius, --n 0, bad --min-mag, out-of-range --lat, stray option, missing file argument): exit 2 expected and matched, stdout empty: PASS; cli/__init__.py:main writes the handler's text only after it returns, and QuakesError paths print only to stderr |
| st-008 | technical | The application's automated tests shall exercise fetch through a stubbed HTTP call and shall not open a network connection. | MET | probe nonet_probe.py: pytest over tests/ exit 0, 256 passed, connection attempts: []; tests/test_fetch.py:46,59,78,100: fetch tests patch cli.fetch.http_get; tests/test_fetch.py:109-113 and tests/test_fetch_failure.py:58,69: the one http_get test patches urllib.request.urlopen with a FakeResponse |

**Ranked improvements:**
1. Make st-007's stderr rule observable: run.sh never compares standard error, so the 'exactly one line' wording in the test suite is unchecked by the grader; add a stderr line-count check to run.sh.
2. Give st-008 a machine check, such as running the suite under a socket tripwire as the probe did, so the no-network claim does not depend on a judgement of the test code.
