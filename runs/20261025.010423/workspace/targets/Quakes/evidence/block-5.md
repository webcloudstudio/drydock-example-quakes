# Evidence: Block 5 · Feature (block-5)

- block type: block
- date: 2026-10-24
- resulting state: closed/verified
- story points (combined assembled cost): 4637
- execution id: 20261025.013120.456Z-eade514b

## Stories built
- Terminal gate running the supplied grader against the finished application. (verification) [story]

## Acceptance tooling authorization
- VERIFICATION.md#verification-grader: executable=sh; scope=test; authorization=existing Target environment
- VERIFICATION.md#verification-test-suite: executable=sh; scope=test; authorization=existing Target environment
- VERIFICATION.md#verification-test-suite: python-package=pytest; scope=test; authorization=existing Target environment

## Stacked context
- stack: python_compact.md (SP 921)
- compass: COMPASS.md (SP 986)
- implements: VERIFICATION.md (SP 1017)
- stack: common_compact.md (SP 1653)

## Pre-build acceptance observation
- GREEN (prepassed): verification-grader (VERIFICATION.md)
  intent: The supplied grader sources/run.sh exits zero against the finished application.
  return code: 0
  stdout:
    PASS A1: quakes summary /mnt/c/Users/barlo/projects/drydock/uat/Quakes/runs/20261025.010423/build/Quakes/sources/quakes_2025-01-01_07.geojson
    PASS A2: quakes top /mnt/c/Users/barlo/projects/drydock/uat/Quakes/runs/20261025.010423/build/Quakes/sources/quakes_2025-01-01_07.geojson
    PASS A3: quakes daily /mnt/c/Users/barlo/projects/drydock/uat/Quakes/runs/20261025.010423/build/Quakes/sources/quakes_2025-01-01_07.geojson
    PASS A4: quakes regions /mnt/c/Users/barlo/projects/drydock/uat/Quakes/runs/20261025.010423/build/Quakes/sources/quakes_2025-01-01_07.geojson
    PASS B1: quakes top --n 3 /mnt/c/Users/barlo/projects/drydock/uat/Quakes/runs/20261025.010423/build/Quakes/sources/quakes_2025-01-01_07.geojson
    PASS B2: quakes summary --min-mag 5.5 /mnt/c/Users/barlo/projects/drydock/uat/Quakes/runs/20261025.010423/build/Quakes/sources/quakes_2025-01-01_07.geojson
    PASS B3: quakes regions --min-mag 5.4 /mnt/c/Users/barlo/projects/drydock/uat/Quakes/runs/20261025.010423/build/Quakes/sources/quakes_2025-01-01_07.geojson
    PASS B4: quakes daily --min-mag 6 /mnt/c/Users/barlo/projects/drydock/uat/Quakes/runs/20261025.010423/build/Quakes/sources/quakes_2025-01-01_07.geojson
    PASS B5: quakes top --min-mag 5.1 --n 4 /mnt/c/Users/barlo/projects/drydock/uat/Quakes/runs/20261025.010423/build/Quakes/sources/quakes_2025-01-01_07.geojson
    PASS C1: quakes near --lat 27.72 --lon 85.32 --radius 800 /mnt/c/Users/barlo/projects/drydock/uat/Quakes/runs/20261025.010423/build/Quakes/sources/quakes_2025-01-01_07.geojson
    PASS C2: quakes near --lat 35.68 --lon 139.69 --radius 1500 /mnt/c/Users/barlo/projects/drydock/uat/Quakes/runs/20261025.010423/build/Quakes/sources/quakes_2025-01-01_07.geojson
    PASS C3: quakes near --lat 9.03 --lon 38.74 --radius 300 --min-mag 5.3 /mnt/c/Users/barlo/projects/drydock/uat/Quakes/runs/20261025.010423/build/Quakes/sources/quakes_2025-01-01_07.geojson
    PASS C4: quakes near --lat 0 --lon 0 --radius 100 /mnt/c/Users/barlo/projects/drydock/uat/Quakes/runs/20261025.010423/build/Quakes/sources/quakes_2025-01-01_07.geojson
    PASS D1: quakes summary --min-mag 9 /mnt/c/Users/barlo/projects/drydock/uat/Quakes/runs/20261025.010423/build/Quakes/sources/quakes_2025-01-01_07.geojson
    PASS D2: quakes daily --min-mag 9 /mnt/c/Users/barlo/projects/drydock/uat/Quakes/runs/20261025.010423/build/Quakes/sources/quakes_2025-01-01_07.geojson
    PASS E1: quakes summary /tmp/tmp.ikchuXzj9O/no-such-file.geojson
    PASS E2: quakes summary /tmp/tmp.ikchuXzj9O/garbage.json
    PASS E3: quakes summary /tmp/tmp.ikchuXzj9O/feature.json
    PASS U1: quakes 
    PASS U2: quakes frobnicate /mnt/c/Users/barlo/projects/drydock/uat/Quakes/runs/20261025.010423/build/Quakes/sources/quakes_2025-01-01_07.geojson
    PASS U3: quakes near --lat 27.72 --lon 85.32 /mnt/c/Users/barlo/projects/drydock/uat/Quakes/runs/20261025.010423/build/Quakes/sources/quakes_2025-01-01_07.geojson
    PASS U4: quakes top --n 0 /mnt/c/Users/barlo/projects/drydock/uat/Quakes/runs/20261025.010423/build/Quakes/sources/quakes_2025-01-01_07.geojson
    PASS U5: quakes summary --min-mag big /mnt/c/Users/barlo/projects/drydock/uat/Quakes/runs/20261025.010423/build/Quakes/sources/quakes_2025-01-01_07.geojson
    PASS U6: quakes near --lat 95 --lon 0 --radius 10 /mnt/c/Users/barlo/projects/drydock/uat/Quakes/runs/20261025.010423/build/Quakes/sources/quakes_2025-01-01_07.geojson
    PASS U7: quakes summary --n 3 /mnt/c/Users/barlo/projects/drydock/uat/Quakes/runs/20261025.010423/build/Quakes/sources/quakes_2025-01-01_07.geojson
    PASS U8: quakes summary
    Quakes: 26 passed, 0 failed (of 26)
- GREEN (prepassed): verification-test-suite (VERIFICATION.md)
  intent: The application's own pytest suite, run through bin/test.sh, exits zero.
  return code: 0
  stdout:
    ........................................................................ [ 28%]
    ........................................................................ [ 56%]
    ........................................................................ [ 84%]
    ........................................                                 [100%]
    256 passed in 22.66s
- GREEN (prepassed): verification-quakes-executable (VERIFICATION.md)
  intent: The quakes executable exists at the application root and is executable, as the grader requires.
  return code: 0

## Post-build programmatic acceptance
- PASS: verification-grader (VERIFICATION.md)
  intent: The supplied grader sources/run.sh exits zero against the finished application.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/Quakes/runs/20261025.010423/build/Quakes/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    PASS A1: quakes summary /mnt/c/Users/barlo/projects/drydock/uat/Quakes/runs/20261025.010423/build/Quakes/sources/quakes_2025-01-01_07.geojson
    PASS A2: quakes top /mnt/c/Users/barlo/projects/drydock/uat/Quakes/runs/20261025.010423/build/Quakes/sources/quakes_2025-01-01_07.geojson
    PASS A3: quakes daily /mnt/c/Users/barlo/projects/drydock/uat/Quakes/runs/20261025.010423/build/Quakes/sources/quakes_2025-01-01_07.geojson
    PASS A4: quakes regions /mnt/c/Users/barlo/projects/drydock/uat/Quakes/runs/20261025.010423/build/Quakes/sources/quakes_2025-01-01_07.geojson
    PASS B1: quakes top --n 3 /mnt/c/Users/barlo/projects/drydock/uat/Quakes/runs/20261025.010423/build/Quakes/sources/quakes_2025-01-01_07.geojson
    PASS B2: quakes summary --min-mag 5.5 /mnt/c/Users/barlo/projects/drydock/uat/Quakes/runs/20261025.010423/build/Quakes/sources/quakes_2025-01-01_07.geojson
    PASS B3: quakes regions --min-mag 5.4 /mnt/c/Users/barlo/projects/drydock/uat/Quakes/runs/20261025.010423/build/Quakes/sources/quakes_2025-01-01_07.geojson
    PASS B4: quakes daily --min-mag 6 /mnt/c/Users/barlo/projects/drydock/uat/Quakes/runs/20261025.010423/build/Quakes/sources/quakes_2025-01-01_07.geojson
    PASS B5: quakes top --min-mag 5.1 --n 4 /mnt/c/Users/barlo/projects/drydock/uat/Quakes/runs/20261025.010423/build/Quakes/sources/quakes_2025-01-01_07.geojson
    PASS C1: quakes near --lat 27.72 --lon 85.32 --radius 800 /mnt/c/Users/barlo/projects/drydock/uat/Quakes/runs/20261025.010423/build/Quakes/sources/quakes_2025-01-01_07.geojson
    PASS C2: quakes near --lat 35.68 --lon 139.69 --radius 1500 /mnt/c/Users/barlo/projects/drydock/uat/Quakes/runs/20261025.010423/build/Quakes/sources/quakes_2025-01-01_07.geojson
    PASS C3: quakes near --lat 9.03 --lon 38.74 --radius 300 --min-mag 5.3 /mnt/c/Users/barlo/projects/drydock/uat/Quakes/runs/20261025.010423/build/Quakes/sources/quakes_2025-01-01_07.geojson
    PASS C4: quakes near --lat 0 --lon 0 --radius 100 /mnt/c/Users/barlo/projects/drydock/uat/Quakes/runs/20261025.010423/build/Quakes/sources/quakes_2025-01-01_07.geojson
    PASS D1: quakes summary --min-mag 9 /mnt/c/Users/barlo/projects/drydock/uat/Quakes/runs/20261025.010423/build/Quakes/sources/quakes_2025-01-01_07.geojson
    PASS D2: quakes daily --min-mag 9 /mnt/c/Users/barlo/projects/drydock/uat/Quakes/runs/20261025.010423/build/Quakes/sources/quakes_2025-01-01_07.geojson
    PASS E1: quakes summary /tmp/tmp.YXFBxf2ASl/no-such-file.geojson
    PASS E2: quakes summary /tmp/tmp.YXFBxf2ASl/garbage.json
    PASS E3: quakes summary /tmp/tmp.YXFBxf2ASl/feature.json
    PASS U1: quakes 
    PASS U2: quakes frobnicate /mnt/c/Users/barlo/projects/drydock/uat/Quakes/runs/20261025.010423/build/Quakes/sources/quakes_2025-01-01_07.geojson
    PASS U3: quakes near --lat 27.72 --lon 85.32 /mnt/c/Users/barlo/projects/drydock/uat/Quakes/runs/20261025.010423/build/Quakes/sources/quakes_2025-01-01_07.geojson
    PASS U4: quakes top --n 0 /mnt/c/Users/barlo/projects/drydock/uat/Quakes/runs/20261025.010423/build/Quakes/sources/quakes_2025-01-01_07.geojson
    PASS U5: quakes summary --min-mag big /mnt/c/Users/barlo/projects/drydock/uat/Quakes/runs/20261025.010423/build/Quakes/sources/quakes_2025-01-01_07.geojson
    PASS U6: quakes near --lat 95 --lon 0 --radius 10 /mnt/c/Users/barlo/projects/drydock/uat/Quakes/runs/20261025.010423/build/Quakes/sources/quakes_2025-01-01_07.geojson
    PASS U7: quakes summary --n 3 /mnt/c/Users/barlo/projects/drydock/uat/Quakes/runs/20261025.010423/build/Quakes/sources/quakes_2025-01-01_07.geojson
    PASS U8: quakes summary
    Quakes: 26 passed, 0 failed (of 26)
- PASS: verification-test-suite (VERIFICATION.md)
  intent: The application's own pytest suite, run through bin/test.sh, exits zero.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/Quakes/runs/20261025.010423/build/Quakes/.venv/bin/python
  provisioning: not required
  return code: 0
  stdout:
    ........................................................................ [ 28%]
    ........................................................................ [ 56%]
    ........................................................................ [ 84%]
    ........................................                                 [100%]
    256 passed in 14.26s
- PASS: verification-quakes-executable (VERIFICATION.md)
  intent: The quakes executable exists at the application root and is executable, as the grader requires.
  target interpreter: /mnt/c/Users/barlo/projects/drydock/uat/Quakes/runs/20261025.010423/build/Quakes/.venv/bin/python
  provisioning: not required
  return code: 0

## Build summary
I'll start by checking the build directory and the current state of the application.The application appears to be in place. Next I'll run the two declared gates, the grader and the test suite, and the executable check.The grader and the application test suite both pass. This is a verification-only step, so I made no file changes.

- **Grader (`sh sources/run.sh`)**: exit 0, 26 of 26 checks passed against the 44-event snapshot.
- **Test suite (`sh bin/test.sh`)**: exit 0, 256 passed, 0 failed.
- **Executable**: `quakes` exists at the application root with the execute bit set.
- **Staged inputs**: `git status` was clean before I started, and I did not touch anything under `sources/`.

RESULT: SUCCESS

FILES CHANGED:
- (none)

SUMMARY:
Verification-only terminal gate, run once against the finished application.
- `sh sources/run.sh`: exit 0. Output reports "Quakes: 26 passed, 0 failed (of 26)".
- `sh bin/test.sh`: exit 0. 256 passed, 0 failed (pytest).
- `quakes` is a file at the application root and is executable (checked with `test -x`).
- Nothing under `sources/` was modified, and no application changes were needed.

BLOCKERS:
- None.
