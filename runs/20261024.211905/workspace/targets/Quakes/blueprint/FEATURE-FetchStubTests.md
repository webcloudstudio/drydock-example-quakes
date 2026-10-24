# FEATURE: Fetch Stub Tests

| Field       | Value |
|-------------|-------|
| Version     | 20261024 V1 |
| Description | Pytest tests that exercise fetch through a stubbed HTTP call and never open a network connection. |
| Depends On  | FEATURE-FetchErrors.md, FEATURE-TestRunner.md |
| Provides    | tests/test_fetch.py |
| Consumes    | http_get |

## Purpose

The fetch command performs its request through one replaceable function, `http_get`. The tests in `tests/test_fetch.py` replace it with a stub (monkeypatch) and cover: a successful fetch writing the body unchanged and printing the feature count, a non-200 status, a network error, and a body that is not a GeoJSON FeatureCollection. In the failure cases the tests assert exit status 1 and that no output file exists. No test opens a network connection.

## Behavior

1. Each test writes its own fixture body and output path under a temporary directory.
2. Each test replaces `http_get` with a stub; the real `urllib.request` call is never reached.
3. Failure tests assert the exit status and that the output file was not created.

## Programmatic Acceptance

=== AC fetchtests-file-collected ===
Intent: tests/test_fetch.py exists and pytest collects at least one test from it.

import subprocess
import sys
from pathlib import Path

path = Path("tests") / "test_fetch.py"
assert path.is_file()
result = subprocess.run(
    [sys.executable, "-m", "pytest", "--collect-only", "-q", str(path)],
    capture_output=True, text=True,
)
print(result.stdout)
print(result.stderr, file=sys.stderr)
assert result.returncode == 0
=== END AC fetchtests-file-collected ===

=== AC fetchtests-pass-without-network ===
Intent: The fetch tests pass while every socket connection attempt raises, proving they never use the network.

import os
import subprocess
import sys
import tempfile
from pathlib import Path

guard = (
    "import socket\n"
    "def _blocked(*a, **k):\n"
    "    raise OSError('network disabled for tests')\n"
    "socket.socket.connect = _blocked\n"
    "socket.create_connection = _blocked\n"
    "socket.getaddrinfo = _blocked\n"
)
with tempfile.TemporaryDirectory() as guard_dir:
    Path(guard_dir, "sitecustomize.py").write_text(guard)
    existing = os.environ.get("PYTHONPATH", "")
    pythonpath = guard_dir if not existing else guard_dir + os.pathsep + existing
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "-q", str(Path("tests") / "test_fetch.py")],
        capture_output=True, text=True,
        env={**os.environ, "PYTHONPATH": pythonpath},
    )
print(result.stdout)
print(result.stderr, file=sys.stderr)
assert result.returncode == 0
=== END AC fetchtests-pass-without-network ===

## User Acceptance

- None.

## Guardrails

- No test opens a network connection; the HTTP call is always replaced by a stub.
- Tests write their own fixture files and do not read anything under `sources/`.
