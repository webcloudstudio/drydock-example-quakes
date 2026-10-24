# Scorecard: Quakes

## Specification

> **NOT YET RUN**
> drydock score spec Quakes

## Acceptance

> **PASSED**
> drydock score ac Quakes · 2026-10-24T06:57:31.660+00:00

PASS 13   FAIL 0   UNVERIFIED 0   PREPASSED 3   (16 AC total)

## Build

> **RECORDED**
> drydock score build Quakes

Blocks: 2   Repaired: 0   Failed: 0
Tokens: 572,891 (cached 496,512, output 8,148)   Cache hit rate: 87.9%

## Release

> **RELEASED**
> drydock score release Quakes · 2026-10-24T06:58:24.472+00:00

- Verdict: PASSED

Quakes: PASSED — 8 of 8

  st-001  MET       ["sh", "sources/run.sh"] exited 0; governed gate: sh sources/run.sh exited 0; 26 passed, 0 failed
  st-002  MET       bin/test.sh:1 has a #!/bin/sh shebang; probe: sh bin/test.sh exited 0; 11 passed, 2 subtests passed
  st-003  MET       sources/run.sh: A1–A4 check summary, top, daily, and regions output against expected CSV; governed gate: 26 passed, 0 failed
  st-004  MET       reports.py:149–167 computes haversine distance on a 6371.0 km sphere and sorts matches by distance; probe: near at (0,0), radius 120 km returned the 1° east event at 111.2 km and omitted the 2° event
  st-005  MET       cli/__init__.py:27 applies filtered events before dispatching reports; probe: --min-mag 5.5 excluded the magnitude 5.0 event from near; --min-mag 6 excluded lower-magnitude events from top
  st-006  MET       quakes.py:19–47 builds the USGS query, validates the response, and writes the response body bytes; probe: request parameters matched the expected URL and saved bytes matched the stub response exactly; tests/test_fetch.py:63–73 covers non-200 and invalid GeoJSON responses without creating output; probe confirmed a network failure creates no file
  st-007  MET       sources/run.sh: E1–E3 check unreadable and invalid files; U1–U8 check malformed arguments; governed gate: all 26 checks passed
  st-008  MET       tests/test_fetch.py:37–73 wraps each fetch call in patch.object(quakes, "urlopen", ...); tests/test_reports.py exercises report commands using local temporary GeoJSON files

## Project acceptance

| ID | Type | Criterion | Verdict | Observed |
|---|---|---|---|---|
| st-001 | technical | The completed quakes shall make sh sources/run.sh exit zero; that script's exit status is the sole acceptance verdict. | MET | ["sh", "sources/run.sh"] exited 0; governed gate: sh sources/run.sh exited 0; 26 passed, 0 failed |
| st-002 | technical | The application shall provide a POSIX-compatible bin/test.sh that exits zero when every automated test passes. | MET | bin/test.sh:1 has a #!/bin/sh shebang; probe: sh bin/test.sh exited 0; 11 passed, 2 subtests passed |
| st-003 | behavioral | The application shall compute the summary, top, daily, and regions reports from the snapshot, matching the known answers in sources/run.sh byte for byte. | MET | sources/run.sh: A1–A4 check summary, top, daily, and regions output against expected CSV; governed gate: 26 passed, 0 failed |
| st-004 | behavioral | When near is given a point and a radius, the application shall list every event within that haversine distance on a 6371.0 km sphere, nearest first. | MET | reports.py:149–167 computes haversine distance on a 6371.0 km sphere and sorts matches by distance; probe: near at (0,0), radius 120 km returned the 1° east event at 111.2 km and omitted the 2° event |
| st-005 | behavioral | When --min-mag is given, the application shall compute every report over only the events whose magnitude is at least that value. | MET | cli/__init__.py:27 applies filtered events before dispatching reports; probe: --min-mag 5.5 excluded the magnitude 5.0 event from near; --min-mag 6 excluded lower-magnitude events from top |
| st-006 | behavioral | When fetch is given a date range, the application shall request the USGS FDSN event query in GeoJSON and write the response unchanged to the output file, writing no file on a network or HTTP failure. | MET | quakes.py:19–47 builds the USGS query, validates the response, and writes the response body bytes; probe: request parameters matched the expected URL and saved bytes matched the stub response exactly; tests/test_fetch.py:63–73 covers non-200 and invalid GeoJSON responses without creating output; probe confirmed a network failure creates no file |
| st-007 | behavioral | If the file is unreadable or not a GeoJSON FeatureCollection, then the application shall exit 1; if the arguments are malformed, then the application shall exit 2; in both cases it shall write nothing to standard output. | MET | sources/run.sh: E1–E3 check unreadable and invalid files; U1–U8 check malformed arguments; governed gate: all 26 checks passed |
| st-008 | technical | The application's automated tests shall exercise fetch through a stubbed HTTP call and shall not open a network connection. | MET | tests/test_fetch.py:37–73 wraps each fetch call in patch.object(quakes, "urlopen", ...); tests/test_reports.py exercises report commands using local temporary GeoJSON files |

**Material decisions:**

- Authorize summary-success test tooling — 
