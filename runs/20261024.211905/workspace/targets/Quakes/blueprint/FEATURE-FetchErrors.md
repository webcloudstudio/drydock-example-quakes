# FEATURE: Fetch Errors

| Field       | Value |
|-------------|-------|
| Version     | 20261024 V1 |
| Description | The fetch command fails with exit 1 and writes no file on network, HTTP or body errors. |
| Depends On  | FEATURE-Fetch.md |
| Provides    | fetch failure behavior |
| Consumes    | http_get |

## Purpose

Make `quakes fetch` safe: it never leaves a file behind that report commands could mistake for a
valid feed.

## Failure cases

Each of these is an operational failure: exit 1, nothing on standard output, one diagnostic line on
standard error, and no file written at `--out`.

- A network error (for example `URLError`, a timeout, or `OSError`).
- An HTTP status other than 200.
- A body that is not valid JSON (including bytes that are not UTF-8).
- A JSON body that is not an object with `"type": "FeatureCollection"` and a `features` array.

The body is validated completely before the output path is opened.

## Reads

The USGS event service through `http_get`.

## Writes

Nothing on failure.

## Programmatic Acceptance

=== AC fetch-network-and-http-errors ===
Intent: A network error or a non-200 HTTP status exits 1 and creates no output file.

import os
import tempfile
import urllib.error
from unittest import mock
from cli.testing import cli_runner

class FakeResponse:
    def __init__(self, body, status):
        self._body = body
        self.status = status
        self.headers = {}
    def read(self, *a):
        return self._body
    def getcode(self):
        return self.status
    def __enter__(self):
        return self
    def __exit__(self, *a):
        return False

def raise_url(*a, **kw):
    raise urllib.error.URLError("unreachable")

def raise_http(*a, **kw):
    raise urllib.error.HTTPError("http://example.invalid", 503, "unavailable", {}, None)

def raise_os(*a, **kw):
    raise OSError("boom")

def status_500(*a, **kw):
    return FakeResponse(b'{"type":"FeatureCollection","features":[]}', 500)

with tempfile.TemporaryDirectory() as tmp:
    for stub in (raise_url, raise_http, raise_os, status_500):
        out_path = os.path.join(tmp, "saved.geojson")
        with mock.patch("urllib.request.urlopen", stub):
            code, out, err = cli_runner("fetch", "--start", "2025-01-01", "--end", "2025-01-02",
                                        "--out", out_path)
        print(stub.__name__, code, repr(err))
        assert code == 1
        assert out == ""
        assert len(err.strip().splitlines()) == 1
        assert not os.path.exists(out_path)
=== END AC fetch-network-and-http-errors ===

=== AC fetch-rejects-bad-bodies ===
Intent: A 200 response whose body is not a GeoJSON FeatureCollection exits 1 and creates no output file.

import json
import os
import tempfile
from unittest import mock
from cli.testing import cli_runner

class FakeResponse:
    def __init__(self, body):
        self._body = body
        self.status = 200
        self.headers = {}
    def read(self, *a):
        return self._body
    def getcode(self):
        return 200
    def __enter__(self):
        return self
    def __exit__(self, *a):
        return False

bodies = [
    b"this is not json",
    b"\xff\xfe\x00 not utf-8",
    json.dumps({"type": "Feature", "properties": {}, "geometry": None}).encode("utf-8"),
    json.dumps({"type": "FeatureCollection"}).encode("utf-8"),
    json.dumps({"type": "FeatureCollection", "features": "nope"}).encode("utf-8"),
    json.dumps([1, 2, 3]).encode("utf-8"),
]

with tempfile.TemporaryDirectory() as tmp:
    for body in bodies:
        out_path = os.path.join(tmp, "saved.geojson")
        with mock.patch("urllib.request.urlopen", lambda *a, _b=body, **kw: FakeResponse(_b)):
            code, out, err = cli_runner("fetch", "--start", "2025-01-01", "--end", "2025-01-02",
                                        "--out", out_path)
        print(body[:20], code)
        assert code == 1
        assert out == ""
        assert len(err.strip().splitlines()) == 1
        assert not os.path.exists(out_path)
=== END AC fetch-rejects-bad-bodies ===

=== AC fetch-failure-leaves-existing-file ===
Intent: A failed fetch does not touch a file that already exists at the output path.

import os
import tempfile
import urllib.error
from unittest import mock
from cli.testing import cli_runner

def raise_url(*a, **kw):
    raise urllib.error.URLError("unreachable")

previous = b"previous contents\n"
with tempfile.TemporaryDirectory() as tmp:
    out_path = os.path.join(tmp, "saved.geojson")
    with open(out_path, "wb") as fh:
        fh.write(previous)
    with mock.patch("urllib.request.urlopen", raise_url):
        code, out, err = cli_runner("fetch", "--start", "2025-01-01", "--end", "2025-01-02",
                                    "--out", out_path)
    assert code == 1
    assert out == ""
    with open(out_path, "rb") as fh:
        assert fh.read() == previous
=== END AC fetch-failure-leaves-existing-file ===

## User Acceptance

- None.

## Guardrails

- A failing fetch writes nothing to standard output and no file.
- Tests stub the HTTP call and never use the network.
- Diagnostics go to standard error and are never compared.
