# Evidence: Block 2 · Service (block-2)

- block type: block
- date: 2026-10-24
- resulting state: closed/verified
- story points (combined assembled cost): 15132
- execution id: 20261024.065529.331Z-45c29989

## Stories built
- Summarize events from a saved GeoJSON FeatureCollection. (summary) [story]
- Report event counts and maximum magnitudes by day. (daily) [story]
- List the largest events from a saved GeoJSON FeatureCollection. (top) [story]
- Report event counts and maximum magnitudes by region. (regions) [story]
- Find events within a haversine distance of a point. (near) [story]
- Provide the automated test suite and run final conformance verification. (verify) [story]

## Missing context
- context: INSTRUCTIONS.md

## Stacked context
- stack: python_compact.md (SP 601)
- compass: COMPASS.md (SP 643)
- implements: FEATURE-Summary.md (SP 622)
- context: quakes_2025-01-01_07.geojson (SP 4689)
- stack: common_compact.md (SP 1079)
- stack: cli.md (SP 1755)
- implements: FEATURE-Daily.md (SP 603)
- implements: FEATURE-Top.md (SP 658)
- implements: FEATURE-Regions.md (SP 680)
- implements: FEATURE-Near.md (SP 917)
- implements: FEATURE-Verification.md (SP 516)
- context: run.sh (SP 2094)

## Build directory changes
- bin/test.sh
- cli/__init__.py
- cli/parser.py
- reports.py
- tests/test_reports.py

## Pre-build acceptance observation
- RED: summary-success (FEATURE-Summary.md)
  intent: The summary command succeeds on a supplied FeatureCollection.
  return code: 1
  stderr:
    --- drydock: values at failure ---
      code = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "summary-success.py", line 13, in <module>
        assert code == 0
               ^^^^^^^^^
    AssertionError
- RED: summary-invalid-file (FEATURE-Summary.md)
  intent: An unreadable or invalid input file returns the operational exit code.
  return code: 1
  stderr:
    --- drydock: values at failure ---
      code = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "summary-invalid-file.py", line 4, in <module>
        assert code == 1
               ^^^^^^^^^
    AssertionError
- RED: daily-empty (FEATURE-Daily.md)
  intent: An empty event file produces a successful daily report with an empty total maximum.
  return code: 1
  stderr:
    --- drydock: values at failure ---
      code = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "daily-empty.py", line 10, in <module>
        assert code == 0
               ^^^^^^^^^
    AssertionError
- RED: daily-filter (FEATURE-Daily.md)
  intent: The minimum magnitude option is accepted and the report succeeds.
  return code: 1
  stderr:
    --- drydock: values at failure ---
      code = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "daily-filter.py", line 13, in <module>
        assert code == 0
               ^^^^^^^^^
    AssertionError
- RED: top-options (FEATURE-Top.md)
  intent: The top command accepts its count option and succeeds on a supplied event file.
  return code: 1
  stderr:
    --- drydock: values at failure ---
      code = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "top-options.py", line 13, in <module>
        assert code == 0
               ^^^^^^^^^
    AssertionError
- GREEN (prepassed): top-invalid-count (FEATURE-Top.md)
  intent: A nonpositive count returns the usage exit code.
  return code: 0
- RED: regions-command (FEATURE-Regions.md)
  intent: The regions command succeeds for a FeatureCollection with an event.
  return code: 1
  stderr:
    --- drydock: values at failure ---
      code = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "regions-command.py", line 13, in <module>
        assert code == 0
               ^^^^^^^^^
    AssertionError
- RED: regions-filter (FEATURE-Regions.md)
  intent: The minimum magnitude option is accepted and returns success.
  return code: 1
  stderr:
    --- drydock: values at failure ---
      code = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "regions-filter.py", line 13, in <module>
        assert code == 0
               ^^^^^^^^^
    AssertionError
- RED: near-valid-request (FEATURE-Near.md)
  intent: A valid near request is accepted by the CLI.
  return code: 1
  stderr:
    --- drydock: values at failure ---
      code = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "near-valid-request.py", line 6, in <module>
        assert code == 0
               ^^^^^^^^^
    AssertionError
- GREEN (prepassed): near-required-options (FEATURE-Near.md)
  intent: A near request missing a required coordinate is rejected as a usage error.
  return code: 0
- GREEN (prepassed): near-coordinate-bounds (FEATURE-Near.md)
  intent: A latitude outside the documented range is rejected as a usage error.
  return code: 0
- RED: near-invalid-file (FEATURE-Near.md)
  intent: An invalid GeoJSON file is reported as an operational failure without standard output.
  return code: 1
  stderr:
    --- drydock: values at failure ---
      code = 2
    --- drydock: end values ---
    Traceback (most recent call last):
      File "near-invalid-file.py", line 10, in <module>
        assert code == 1
               ^^^^^^^^^
    AssertionError
- RED: verification-test-suite (FEATURE-Verification.md)
  intent: The project test launcher succeeds after running the automated tests.
  return code: 1
  stdout:
    sh: 0: cannot open bin/test.sh: No such file
  stderr:
    --- drydock: values at failure ---
      result = CompletedProcess(args=['sh', 'bin/test.sh'], returncode=2, stdout='', stderr='sh: 0: cannot open bin/test.sh: No such file\n')
    --- drydock: end values ---
    Traceback (most recent call last):
      File "verification-test-suite.py", line 10, in <module>
        assert result.returncode == 0
               ^^^^^^^^^^^^^^^^^^^^^^
    AssertionError
- RED: verification-full-conformance (FEATURE-Verification.md)
  intent: The complete supplied grader passes against the finished command set.
  return code: 1
  stdout:
    FAIL A1: quakes summary /mnt/c/Users/barlo/projects/drydock/uat/Quakes/runs/20261024.065111/build/Quakes/sources/quakes_2025-01-01_07.geojson
      exit: expected 0, got 2
      1,2d0
      < events,first,last,min_mag,max_mag,mean_mag,tsunami
      < 44,2025-01-01T04:39:18Z,2025-01-07T17:52:21Z,5.0,7.1,5.30,0
      stderr: usage: quakes [-h] {fetch} ...
      stderr: quakes: error: argument command: invalid choice: 'summary' (choose from fetch)
    FAIL A2: quakes top /mnt/c/Users/barlo/projects/drydock/uat/Quakes/runs/20261024.065111/build/Quakes/sources/quakes_2025-01-01_07.geojson
      exit: expected 0, got 2
      1,11d0
      < time,mag,depth_km,place,id
      < 2025-01-07T01:05:16Z,7.1,10.0,2025 Southern Tibetan Plateau Earthquake,us6000pi9w
      < 2025-01-05T17:18:45Z,6.2,46.0,"56 km SSE of La Libertad, El Salvador",us6000pi09
      < 2025-01-01T13:48:24Z,6.1,70.0,South Sandwich Islands region,us6000pgv4
      < 2025-01-02T20:43:35Z,6.1,99.0,"84 km NNW of Calama, Chile",us6000phap
      < 2025-01-04T00:52:21Z,5.7,8.0,"52 km N of Āwash, Ethiopia",us6000phrk
      < 2025-01-07T08:31:30Z,5.6,358.0,"Izu Islands, Japan region",us6000pida
      < 2025-01-01T04:39:18Z,5.5,22.0,"153 km S of Isangel, Vanuatu",us6000pgsd
      < 2025-01-02T02:54:17Z,5.5,10.0,Balleny Islands region,us6000pgzq
      < 2025-01-03T02:33:17Z,5.5,86.0,South Sandwich Islands region,us6000phce
      < 2025-01-03T17:01:46Z,5.5,10.0,"45 km NNE of Āwash, Ethiopia",us6000phnz
      stderr: usage: quakes [-h] {fetch} ...
      stderr: quakes: error: argument command: invalid choice: 'top' (choose from fetch)
    FAIL A3: quakes daily /mnt/c/Users/barlo/projects/drydock/uat/Quakes/runs/20261024.065111/build/Quakes/sources/quakes_2025-01-01_07.geojson
      exit: expected 0, got 2
      1,9d0
      < date,events,max_mag
      < 2025-01-01,7,6.1
      < 2025-01-02,8,6.1
      < 2025-01-03,6,5.5
      < 2025-01-04,3,5.7
      < 2025-01-05,3,6.2
      < 2025-01-06,5,5.2
      < 2025-01-07,12,7.1
      < TOTAL,44,7.1
      stderr: usage: quakes [-h] {fetch} ...
      stderr: quakes: error: argument command: invalid choice: 'daily' (choose from fetch)
    FAIL A4: quakes regions /mnt/c/Users/barlo/projects/drydock/uat/Quakes/runs/20261024.065111/build/Quakes/sources/quakes_2025-01-01_07.geojson
      exit: expected 0, got 2
      1,25d0
      < region,events,max_mag
      < Ethiopia,7,5.7
      < Papua New Guinea,6,5.4
      < Nepal,3,5.4
      < Southern Tibetan Plateau,3,5.2
      < Vanuatu,3,5.5
      < Indonesia,2,5.1
      < Japan region,2,5.6
      < South Sandwich Islands region,2,6.1
      < 2025 Southern Tibetan Plateau Earthquake,1,7.1
      < Balleny Islands region,1,5.5
      < Chile,1,6.1
      < El Salvador,1,6.2
      < Fiji region,1,5.0
      < India,1,5.0
      < Iran,1,5.2
      < Japan,1,5.1
      < Mid-Indian Ridge,1,5.2
      < Philippines,1,5.1
      < Solomon Islands,1,5.2
      < Southwest Indian Ridge,1,5.0
      < Tibetan Plateau,1,5.2
      < Tonga,1,5.1
      < southeast of Easter Island,1,5.3
      < southern Mid-Atlantic Ridge,1,5.2
      stderr: usage: quakes [-h] {fetch} ...
      stderr: quakes: error: argument command: invalid choice: 'regions' (choose from fetch)
    FAIL B1: quakes top --n 3 /mnt/c/Users/barlo/projects/drydock/uat/Quakes/runs/20261024.065111/build/Quakes/sources/quakes_2025-01-01_07.geojson
      exit: expected 0, got 2
      1,4d0
      < time,mag,depth_km,place,id
      < 2025-01-07T01:05:16Z,7.1,10.0,2025 Southern Tibetan Plateau Earthquake,us6000pi9w
      < 2025-01-05T17:18:45Z,6.2,46.0,"56 km SSE of La Libertad, El Salvador",us6000pi09
      < 2025-01-01T13:48:24Z,6.1,70.0,South Sandwich Islands region,us6000pgv4
      stderr: usage: quakes [-h] {fetch} ...
      stderr: quakes: error: argument command: invalid choice: 'top' (choose from fetch)
    FAIL B2: quakes summary --min-mag 5.5 /mnt/c/Users/barlo/projects/drydock/uat/Quakes/runs/20261024.065111/build/Quakes/sources/quakes_2025-01-01_07.geojson
      exit: expected 0, got 2
      1,2d0
      < events,first,last,min_mag,max_mag,mean_mag,tsunami
      < 10,2025-01-01T04:39:18Z,2025-01-07T08:31:30Z,5.5,7.1,5.88,0
      stderr: usage: quakes [-h] {fetch} ...
      stderr: quakes: error: argument command: invalid choice: 'summary' (choose from fetch)
    FAIL B3: quakes regions --min-mag 5.4 /mnt/c/Users/barlo/projects/drydock/uat/Quakes/runs/20261024.065111/build/Quakes/sources/quakes_2025-01-01_07.geojson
      exit: expected 0, got 2
      1,11d0
      < region,events,max_mag
      < Ethiopia,3,5.7
      < South Sandwich Islands region,2,6.1
      < 2025 Southern Tibetan Plateau Earthquake,1,7.1
      < Balleny Islands region,1,5.5
      < Chile,1,6.1
      < El Salvador,1,6.2
      < Japan region,1,5.6
      < Nepal,1,5.4
      < Papua New Guinea,1,5.4
      < Vanuatu,1,5.5
      stderr: usage: quakes [-h] {fetch} ...
      stderr: quakes: error: argument command: invalid choice: 'regions' (choose from fetch)
    FAIL B4: quakes daily --min-mag 6 /mnt/c/Users/barlo/projects/drydock/uat/Quakes/runs/20261024.065111/build/Quakes/sources/quakes_2025-01-01_07.geojson
      exit: expected 0, got 2
      1,6d0
      < date,events,max_mag
      < 2025-01-01,1,6.1
      < 2025-01-02,1,6.1
      < 2025-01-05,1,6.2
      < 2025-01-07,1,7.1
      < TOTAL,4,7.1
      stderr: usage: quakes [-h] {fetch} ...
      stderr: quakes: error: argument command: invalid choice: 'daily' (choose from fetch)
    FAIL B5: quakes top --min-mag 5.1 --n 4 /mnt/c/Users/barlo/projects/drydock/uat/Quakes/runs/20261024.065111/build/Quakes/sources/quakes_2025-01-01_07.geojson
      exit: expected 0, got 2
      1,5d0
      < time,mag,depth_km,place,id
      < 2025-01-07T01:05:16Z,7.1,10.0,2025 Southern Tibetan Plateau Earthquake,us6000pi9w
      < 2025-01-05T17:18:45Z,6.2,46.0,"56 km SSE of La Libertad, El Salvador",us6000pi09
      < 2025-01-01T13:48:24Z,6.1,70.0,South Sandwich Islands region,us6000pgv4
      < 2025-01-02T20:43:35Z,6.1,99.0,"84 km NNW of Calama, Chile",us6000phap
      stderr: usage: quakes [-h] {fetch} ...
      stderr: quakes: error: argument command: invalid choice: 'top' (choose from fetch)
    FAIL C1: quakes near --lat 27.72 --lon 85.32 --radius 800 /mnt/c/Users/barlo/projects/drydock/uat/Quakes/runs/20261024.065111/build/Quakes/sources/quakes_2025-01-01_07.geojson
      exit: expected 0, got 2
      1,9d0
      < distance_km,time,mag,place,id
      < 214.8,2025-01-07T01:10:54Z,5.2,"100 km NNE of Lobuche, Nepal",us6000pks6
      < 216.8,2025-01-07T01:09:13Z,5.4,"96 km NNE of Lobuche, Nepal",us6000pks1
      < 219.0,2025-01-07T01:14:42Z,5.2,"83 km NE of Lobuche, Nepal",us6000pkpp
      < 222.3,2025-01-07T01:37:13Z,5.0,Southern Tibetan Plateau,us6000piar
      < 224.4,2025-01-07T01:05:16Z,7.1,2025 Southern Tibetan Plateau Earthquake,us6000pi9w
      < 225.3,2025-01-07T01:13:27Z,5.2,Southern Tibetan Plateau,us6000pia7
      < 226.2,2025-01-07T01:24:25Z,5.0,Southern Tibetan Plateau,us6000piak
      < 655.6,2025-01-06T15:26:46Z,5.2,Tibetan Plateau,us6000pi67
      stderr: usage: quakes [-h] {fetch} ...
      stderr: quakes: error: argument command: invalid choice: 'near' (choose from fetch)
    FAIL C2: quakes near --lat 35.68 --lon 139.69 --radius 1500 /mnt/c/Users/barlo/projects/drydock/uat/Quakes/runs/20261024.065111/build/Quakes/sources/quakes_2025-01-01_07.geojson
      exit: expected 0, got 2
      1,4d0
      < distance_km,time,mag,place,id
      < 216.3,2025-01-06T16:44:39Z,5.1,"113 km E of Hasaki, Japan",us6000pi7a
      < 466.3,2025-01-07T08:31:30Z,5.6,"Izu Islands, Japan region",us6000pida
      < 1288.3,2025-01-07T17:23:48Z,5.3,"Volcano Islands, Japan region",us6000pife
      stderr: usage: quakes [-h] {fetch} ...
      stderr: quakes: error: argument command: invalid choice: 'near' (choose from fetch)
    FAIL C3: quakes near --lat 9.03 --lon 38.74 --radius 300 --min-mag 5.3 /mnt/c/Users/barlo/projects/drydock/uat/Quakes/runs/20261024.065111/build/Quakes/sources/quakes_2025-01-01_07.geojson
      exit: expected 0, got 2
      1,4d0
      < distance_km,time,mag,place,id
      < 159.0,2025-01-04T00:52:21Z,5.7,"52 km N of Āwash, Ethiopia",us6000phrk
      < 174.7,2025-01-02T21:18:26Z,5.4,"52 km NNE of Āwash, Ethiopia",us6000phb3
      < 180.0,2025-01-03T17:01:46Z,5.5,"45 km NNE of Āwash, Ethiopia",us6000phnz
      stderr: usage: quakes [-h] {fetch} ...
      stderr: quakes: error: argument command: invalid choice: 'near' (choose from fetch)
    FAIL C4: quakes near --lat 0 --lon 0 --radius 100 /mnt/c/Users/barlo/projects/drydock/uat/Quakes/runs/20261024.065111/build/Quakes/sources/quakes_2025-01-01_07.geojson
      exit: expected 0, got 2
      1d0
      < distance_km,time,mag,place,id
      stderr: usage: quakes [-h] {fetch} ...
      stderr: quakes: error: argument command: invalid choice: 'near' (choose from fetch)
    FAIL D1: quakes summary --min-mag 9 /mnt/c/Users/barlo/projects/drydock/uat/Quakes/runs/20261024.065111/build/Quakes/sources/quakes_2025-01-01_07.geojson
      exit: expected 0, got 2
      1,2d0
      < events,first,last,min_mag,max_mag,mean_mag,tsunami
      < 0,,,,,,0
      stderr: usage: quakes [-h] {fetch} ...
      stderr: quakes: error: argument command: invalid choice: 'summary' (choose from fetch)
    FAIL D2: quakes daily --min-mag 9 /mnt/c/Users/barlo/projects/drydock/uat/Quakes/runs/20261024.065111/build/Quakes/sources/quakes_2025-01-01_07.geojson
      exit: expected 0, got 2
      1,2d0
      < date,events,max_mag
      < TOTAL,0,
      stderr: usage: quakes [-h] {fetch} ...
      stderr: quakes: error: argument command: invalid choice: 'daily' (choose from fetch)
    FAIL E1: quakes summary /tmp/tmp.5TdyGQZ1CW/no-such-file.geojson
      exit: expected 1, got 2
      stderr: usage: quakes [-h] {fetch} ...
      stderr: quakes: error: argument command: invalid choice: 'summary' (choose from fetch)
    FAIL E2: quakes summary /tmp/tmp.5TdyGQZ1CW/garbage.json
      exit: expected 1, got 2
      stderr: usage: quakes [-h] {fetch} ...
      stderr: quakes: error: argument command: invalid choice: 'summary' (choose from fetch)
    FAIL E3: quakes summary /tmp/tmp.5TdyGQZ1CW/feature.json
      exit: expected 1, got 2
      stderr: usage: quakes [-h] {fetch} ...
      stderr: quakes: error: argument command: invalid choice: 'summary' (choose from fetch)
    PASS U1: quakes 
    PASS U2: quakes frobnicate /mnt/c/Users/barlo/projects/drydock/uat/Quakes/runs/20261024.065111/build/Quakes/sources/quakes_2025-01-01_07.geojson
    PASS U3: quakes near --lat 27.72 --lon 85.32 /mnt/c/Users/barlo/projects/drydock/uat/Quakes/runs/20261024.065111/build/Quakes/sources/quakes_2025-01-01_07.geojson
    PASS U4: quakes top --n 0 /mnt/c/Users/barlo/projects/drydock/uat/Quakes/runs/20261024.065111/build/Quakes/sources/quakes_2025-01-01_07.geojson
    PASS U5: quakes summary --min-mag big /mnt/c/Users/barlo/projects/drydock/uat/Quakes/runs/20261024.065111/build/Quakes/sources/quakes_2025-01-01_07.geojson
    PASS U6: quakes near --lat 95 --lon 0 --radius 10 /mnt/c/Users/barlo/projects/drydock/uat/Quakes/runs/20261024.065111/build/Quakes/sources/quakes_2025-01-01_07.geojson
    PASS U7: quakes summary --n 3 /mnt/c/Users/barlo/projects/drydock/uat/Quakes/runs/20261024.065111/build/Quakes/sources/quakes_2025-01-01_07.geojson
    PASS U8: quakes summary
    Quakes: 8 passed, 18 failed (of 26)
  stderr:
    --- drydock: values at failure ---
      result = CompletedProcess(args=['sh', 'sources/run.sh'], returncode=1, stdout='FAIL A1: quakes summary /mnt/c/Users/barlo/projects/drydock/uat/Quakes/runs/20261024.065111/build/Quakes/sources/quakes_2025-01-01_07.geojson\n  exit: expected 0, got 2\n  1,2d0\n  < events,first,last,min_mag,max_mag,mean_mag,tsunami\n  < 44,2025-01-01T04:39:18Z,2025-01-07T17:52:21Z,5.0,7.1,5.30,0\n  stderr: usage: quakes [-h] {… (+10526 chars)
    --- drydock: end values ---
    Traceback (most recent call last):
      File "verification-full-conformance.py", line 10, in <module>
        assert result.returncode == 0
               ^^^^^^^^^^^^^^^^^^^^^^
    AssertionError

## Build summary
RESULT: SUCCESS

FILES CHANGED:
- cli/__init__.py
- cli/parser.py
- reports.py
- tests/test_reports.py
- bin/test.sh

SUMMARY:
Implemented summary, daily, top, regions, and near reports with shared GeoJSON parsing, filtering, formatting, and validation. Added offline tests and the test launcher. `sh bin/test.sh` passed (11 tests, 2 subtests); `sh sources/run.sh` passed all 26 checks. Staged sources are unchanged.

BLOCKERS:
- None
