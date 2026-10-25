# FEATURE: Fetch Failure

| Field       | Value |
|-------------|-------|
| Version     | 20261025 V1 |
| Description | Failure behavior of `fetch`: network, HTTP, and body errors exit 1 and never write or alter a file. |
| Depends On  | FEATURE-Fetch.md, FEATURE-ExitCodes.md |
| Provides    | fetch failure handling |
| Consumes    | http_get |

## Purpose

When the download cannot produce a valid GeoJSON FeatureCollection, `fetch` reports an operational failure and leaves the filesystem exactly as it found it.

## Trigger

Any of the following during `quakes fetch` (after arguments parse successfully):

- a network error (any `urllib.error.URLError`, `OSError`, or timeout from the HTTP layer);
- an HTTP status other than 200;
- a 200 body that is not JSON, or is JSON but not an object with `"type": "FeatureCollection"` and a list `features`.

## Behavior

- `http_get` returns `(status, body)` for every HTTP response, including non-200 statuses (an `HTTPError` is converted to its code and body), and raises `OperationalError` for `URLError`, `OSError`, and timeouts.
- The `fetch` handler also converts any `OSError` raised by a replaced `http_get` into `OperationalError`.
- A non-200 status or an invalid body raises `OperationalError`.
- All checks complete before `--out` is opened, so no file is created and a pre-existing file at `--out` keeps its exact bytes.
- The command exits 1, writes nothing to standard output, and writes one diagnostic line to standard error.

## Reads

The HTTP response only.

## Writes

Standard error only; never the output file on failure.

## Programmatic Acceptance

=== AC fetch-failure-http-status ===
Intent: A non-200 status exits 1 with empty standard output, one stderr line, and no file written.
Suite: scoped
Requires: executable=python3; scope=test

import json
import os
import tempfile
from unittest import mock

from cli.testing import cli_runner

valid = json.dumps({"type": "FeatureCollection", "features": []}).encode("utf-8")
bad_status = 500
with tempfile.TemporaryDirectory() as tmp:
    out_path = os.path.join(tmp, "saved.geojson")
    with mock.patch("cli.fetch.http_get", return_value=(bad_status, valid)):
        code, out, err = cli_runner("fetch", "--start", "2025-01-01", "--end", "2025-01-02", "--out", out_path)
    print(err)
    assert code == 1
    assert out == ""
    assert len(err.strip().splitlines()) == 1
    assert not os.path.exists(out_path)
=== END AC fetch-failure-http-status ===

=== AC fetch-failure-bad-body ===
Intent: A body that is not JSON, or JSON that is not a FeatureCollection, exits 1 and writes no file.
Suite: scoped
Requires: executable=python3; scope=test

import json
import os
import tempfile
from unittest import mock

from cli.testing import cli_runner

bodies = [
    b"this is not json",
    json.dumps({"type": "Feature", "properties": {}, "geometry": None}).encode("utf-8"),
    json.dumps({"type": "FeatureCollection"}).encode("utf-8"),
    json.dumps({"type": "FeatureCollection", "features": "nope"}).encode("utf-8"),
    json.dumps([1, 2, 3]).encode("utf-8"),
]
with tempfile.TemporaryDirectory() as tmp:
    for n, body in enumerate(bodies):
        out_path = os.path.join(tmp, "saved" + str(n) + ".geojson")
        with mock.patch("cli.fetch.http_get", return_value=(200, body)):
            code, out, err = cli_runner("fetch", "--start", "2025-01-01", "--end", "2025-01-02", "--out", out_path)
        assert code == 1, n
        assert out == "", n
        assert not os.path.exists(out_path), n
=== END AC fetch-failure-bad-body ===

=== AC fetch-failure-network-error ===
Intent: A network error from a stubbed http_get, and a URLError from a patched urlopen, both exit 1 with no file written.
Suite: scoped
Requires: executable=python3; scope=test

import os
import tempfile
import urllib.error
from unittest import mock

from cli.testing import cli_runner

with tempfile.TemporaryDirectory() as tmp:
    first = os.path.join(tmp, "first.geojson")
    with mock.patch("cli.fetch.http_get", side_effect=OSError("unreachable")):
        code, out, err = cli_runner("fetch", "--start", "2025-01-01", "--end", "2025-01-02", "--out", first)
    assert code == 1
    assert out == ""
    assert not os.path.exists(first)

    second = os.path.join(tmp, "second.geojson")
    with mock.patch("urllib.request.urlopen", side_effect=urllib.error.URLError("no route")) as opener:
        code2, out2, err2 = cli_runner("fetch", "--start", "2025-01-01", "--end", "2025-01-02", "--out", second)
    assert opener.call_count == 1
    assert code2 == 1
    assert out2 == ""
    assert not os.path.exists(second)
=== END AC fetch-failure-network-error ===

=== AC fetch-failure-http-error-status ===
Intent: An HTTPError raised by urlopen is treated as a non-200 status, exits 1, and writes no file.
Suite: scoped
Requires: executable=python3; scope=test

import io
import os
import tempfile
import urllib.error
from unittest import mock

from cli.testing import cli_runner

error = urllib.error.HTTPError("https://example.invalid", 503, "unavailable", {}, io.BytesIO(b"down"))
with tempfile.TemporaryDirectory() as tmp:
    out_path = os.path.join(tmp, "saved.geojson")
    with mock.patch("urllib.request.urlopen", side_effect=error):
        code, out, err = cli_runner("fetch", "--start", "2025-01-01", "--end", "2025-01-02", "--out", out_path)
    assert code == 1
    assert out == ""
    assert not os.path.exists(out_path)
=== END AC fetch-failure-http-error-status ===

=== AC fetch-failure-preserves-existing-file ===
Intent: A failed fetch leaves a pre-existing output file byte-for-byte untouched.
Suite: scoped
Requires: executable=python3; scope=test

import os
import tempfile
from unittest import mock

from cli.testing import cli_runner

original = b"previous contents, not JSON\n"
with tempfile.TemporaryDirectory() as tmp:
    out_path = os.path.join(tmp, "saved.geojson")
    with open(out_path, "wb") as fh:
        fh.write(original)
    with mock.patch("cli.fetch.http_get", return_value=(404, b"missing")):
        code, out, err = cli_runner("fetch", "--start", "2025-01-01", "--end", "2025-01-02", "--out", out_path)
    assert code == 1
    with open(out_path, "rb") as fh:
        assert fh.read() == original
    with mock.patch("cli.fetch.http_get", return_value=(200, b"not json")):
        code2, out2, err2 = cli_runner("fetch", "--start", "2025-01-01", "--end", "2025-01-02", "--out", out_path)
    assert code2 == 1
    with open(out_path, "rb") as fh:
        assert fh.read() == original
=== END AC fetch-failure-preserves-existing-file ===

## User Acceptance

- None.

## Guardrails

- A failing `fetch` never creates, truncates, or modifies the output file.
- A failing command writes nothing to standard output and exactly one diagnostic line to standard error; standard error text is never part of a contract.
- Tests exercise failure only through stubbed HTTP; no test opens a network connection.
