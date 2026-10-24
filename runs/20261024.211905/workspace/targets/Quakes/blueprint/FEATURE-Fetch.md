# FEATURE: Fetch

| Field       | Value |
|-------------|-------|
| Version     | 20261024 V1 |
| Description | The fetch command downloads a period of the USGS event feed as GeoJSON and saves the body unchanged. |
| Depends On  | FEATURE-CliDispatch.md, FEATURE-ExitCodes.md, FEATURE-FeedReader.md |
| Provides    | quakes fetch, http_get |
| Consumes    | quakes <command> dispatch |

## Purpose

`quakes fetch --start <YYYY-MM-DD> --end <YYYY-MM-DD> [--min-mag <m>] --out <file>` saves a period
of the USGS FDSN event feed so that report commands can read it later.

## Request

GET `https://earthquake.usgs.gov/fdsnws/event/1/query` with the query parameters `format=geojson`,
`starttime=<start>`, `endtime=<end>`, `minmagnitude=<m>` (default `2.5`) and `orderby=time-asc`.

## HTTP seam

All network access goes through one replaceable function, `http_get(url)`, which returns the status
code and the body bytes. It calls `urllib.request.urlopen` through the module attribute
(`urllib.request.urlopen(...)`, never `from urllib.request import urlopen`), so a test can replace
the HTTP call with a stub. An `HTTPError` is returned as its status code. No test uses the network.

## Sequence

1. Parse and validate options (`--start`, `--end`, `--out` required; `--min-mag` optional).
2. Request the URL through `http_get`.
3. On status 200, parse the body as a GeoJSON FeatureCollection (failure handling is in
   FEATURE-FetchErrors.md).
4. Write the body bytes unchanged to `--out`.
5. Write `fetched,<count>` to standard output, where `<count>` is the number of features.

Missing `--start`, `--end` or `--out`, an extra positional argument, or a malformed `--min-mag` is a
usage error (exit 2).

## Reads

The USGS event service.

## Writes

The file named by `--out`; `fetched,<count>` on standard output.

## Programmatic Acceptance

=== AC fetch-request-and-save ===
Intent: Fetch requests the FDSN query with the given range and default magnitude, saves the body unchanged and reports the feature count.

import json
import os
import tempfile
import urllib.parse
import urllib.request
from unittest import mock
from cli.testing import cli_runner

class FakeResponse:
    def __init__(self, body, status=200):
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

start, end = "2025-01-01", "2025-01-08"
features = [{"type": "Feature", "properties": {"mag": 5.0 + i / 10, "place": "p, R", "time": 1735689600000 + i,
                                               "tsunami": 0},
             "geometry": {"type": "Point", "coordinates": [1.0, 2.0, 3.0]}, "id": "id%d" % i}
            for i in range(3)]
body = json.dumps({"type": "FeatureCollection", "features": features}, indent=3).encode("utf-8") + b"\n"
seen = []

def fake_urlopen(req, *a, **kw):
    seen.append(getattr(req, "full_url", req))
    return FakeResponse(body)

with tempfile.TemporaryDirectory() as tmp:
    out_path = os.path.join(tmp, "saved.geojson")
    with mock.patch("urllib.request.urlopen", fake_urlopen):
        code, out, err = cli_runner("fetch", "--start", start, "--end", end, "--out", out_path)
    print(out)
    print(err)
    assert code == 0
    with open(out_path, "rb") as fh:
        assert fh.read() == body
    fields = out.strip().split(",")
    assert fields[0] == "fetched"
    assert int(fields[1]) == len(features)

assert len(seen) == 1
parsed = urllib.parse.urlparse(seen[0])
assert parsed.scheme == "https"
assert parsed.netloc == "earthquake.usgs.gov"
assert parsed.path == "/fdsnws/event/1/query"
q = urllib.parse.parse_qs(parsed.query)
assert q["format"] == ["geojson"]
assert q["starttime"] == [start]
assert q["endtime"] == [end]
assert q["minmagnitude"] == ["2.5"]
assert q["orderby"] == ["time-asc"]
=== END AC fetch-request-and-save ===

=== AC fetch-min-mag-option ===
Intent: An explicit --min-mag value is sent as minmagnitude.

import json
import os
import tempfile
import urllib.parse
from unittest import mock
from cli.testing import cli_runner

class FakeResponse:
    def __init__(self, body, status=200):
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

mag = "5.5"
body = json.dumps({"type": "FeatureCollection", "features": []}).encode("utf-8")
seen = []

def fake_urlopen(req, *a, **kw):
    seen.append(getattr(req, "full_url", req))
    return FakeResponse(body)

with tempfile.TemporaryDirectory() as tmp:
    out_path = os.path.join(tmp, "saved.geojson")
    with mock.patch("urllib.request.urlopen", fake_urlopen):
        code, out, err = cli_runner("fetch", "--start", "2025-02-01", "--end", "2025-02-02",
                                    "--min-mag", mag, "--out", out_path)
    print(out, err)
    assert code == 0
    assert int(out.strip().split(",")[1]) == 0
    assert os.path.exists(out_path)
q = urllib.parse.parse_qs(urllib.parse.urlparse(seen[0]).query)
assert q["minmagnitude"] == [mag]
=== END AC fetch-min-mag-option ===

=== AC fetch-usage-errors ===
Intent: Fetch without a required option or with an extra argument is a usage error that makes no request and writes no file.

import os
import tempfile
from unittest import mock
from cli.testing import cli_runner

def boom(*a, **kw):
    raise AssertionError("network must not be used")

with tempfile.TemporaryDirectory() as tmp:
    out_path = os.path.join(tmp, "saved.geojson")
    cases = [
        ["--end", "2025-01-02", "--out", out_path],
        ["--start", "2025-01-01", "--out", out_path],
        ["--start", "2025-01-01", "--end", "2025-01-02"],
        ["--start", "2025-01-01", "--end", "2025-01-02", "--out", out_path, "extra.json"],
        ["--start", "2025-01-01", "--end", "2025-01-02", "--min-mag", "big", "--out", out_path],
    ]
    with mock.patch("urllib.request.urlopen", boom):
        for args in cases:
            code, out, err = cli_runner("fetch", *args)
            print(args, code)
            assert code == 2
            assert out == ""
    assert not os.path.exists(out_path)
=== END AC fetch-usage-errors ===

## User Acceptance

- None.

## Guardrails

- Tests replace the HTTP call with a stub and never open a network connection.
- The response body is written unchanged, byte for byte; it is never re-serialised.
- Only the Python standard library is used for HTTP.
