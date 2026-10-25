# FEATURE: Fetch

| Field       | Value |
|-------------|-------|
| Version     | 20261025 V1 |
| Description | The `fetch` command: download a USGS date range as GeoJSON and save the response unchanged to a file. |
| Depends On  | FEATURE-Options.md, FEATURE-ExitCodes.md, FEATURE-FeedValidation.md |
| Provides    | quakes fetch, build_url, http_get |
| Consumes    | parse_args, read_feed |

## Purpose

`quakes fetch --start <YYYY-MM-DD> --end <YYYY-MM-DD> [--min-mag <m>] --out <file>` saves a period of the USGS event feed so the report commands can read it.

## Trigger

Command line. `--start`, `--end`, and `--out` are required; `--min-mag` defaults to `2.5`. A missing required option, an unlisted option, or any positional argument is a usage error (exit 2) and no HTTP call is made.

## Module layout

Code lives in `cli/fetch.py`:

- `build_url(start, end, min_mag) -> str` returns `https://earthquake.usgs.gov/fdsnws/event/1/query` with query parameters `format=geojson`, `starttime=<start>`, `endtime=<end>`, `minmagnitude=<min_mag>`, `orderby=time-asc`. `min_mag` is the text given on the command line (or `2.5`).
- `http_get(url) -> tuple[int, bytes]` is the single replaceable network function. It calls `urllib.request.urlopen` through attribute access on the `urllib.request` module (so a test can patch `urllib.request.urlopen`), returns the HTTP status and body bytes, and is the only function in the product that opens a connection.
- The command handler calls `http_get` through the module global (`cli.fetch.http_get`) so tests can replace it.

## Sequence

1. Build the URL and call `http_get(url)`.
2. Validate: status 200, body parses as JSON, and is an object with `"type": "FeatureCollection"` and a list `features` (reusing the `read_feed` validation rules on the body).
3. Only after validation, write the body bytes unchanged (binary write) to `--out`.
4. Write `fetched,<count>` to standard output, where `<count>` is the number of features.

Failure handling is specified in FEATURE-FetchFailure.md.

## Output

Standard output is exactly one CSV line `fetched,<count>`; exit 0. The saved file is byte-for-byte the response body.

## Reads

The USGS FDSN event web service over HTTPS.

## Writes

The file named by `--out`, and standard output.

## Programmatic Acceptance

=== AC fetch-saves-body-unchanged ===
Intent: fetch writes the response body byte for byte to --out and prints fetched with the feature count; the HTTP call is stubbed.
Suite: scoped
Requires: executable=python3; scope=test

import csv
import io
import json
import os
import tempfile
from unittest import mock

from cli.testing import cli_runner

features = [
    {"type": "Feature", "properties": {"mag": 5.1, "place": "Awash, Ethiopia", "time": 1735706358208, "tsunami": 0},
     "geometry": {"type": "Point", "coordinates": [40.0, 9.0, 10]}, "id": "a" + str(i)}
    for i in range(3)
]
body = json.dumps({"type": "FeatureCollection", "features": features}, indent=3, ensure_ascii=False).encode("utf-8") + b"\n\n"
with tempfile.TemporaryDirectory() as tmp:
    out_path = os.path.join(tmp, "saved.geojson")
    with mock.patch("cli.fetch.http_get", return_value=(200, body)) as stub:
        code, out, err = cli_runner("fetch", "--start", "2025-01-01", "--end", "2025-01-08", "--out", out_path)
    print(out)
    print(err)
    assert code == 0
    assert stub.call_count == 1
    with open(out_path, "rb") as fh:
        assert fh.read() == body
rows = list(csv.reader(io.StringIO(out)))
assert rows == [["fetched", str(len(features))]]
=== END AC fetch-saves-body-unchanged ===

=== AC fetch-request-url ===
Intent: The request goes to the USGS FDSN query endpoint with the GeoJSON format, the given dates, the default minimum magnitude, and time ascending order.
Suite: scoped
Requires: executable=python3; scope=test

import json
import os
import tempfile
import urllib.parse
from unittest import mock

from cli.testing import cli_runner

start = "2025-01-01"
end = "2025-01-08"
body = json.dumps({"type": "FeatureCollection", "features": []}).encode("utf-8")
with tempfile.TemporaryDirectory() as tmp:
    out_path = os.path.join(tmp, "saved.geojson")
    with mock.patch("cli.fetch.http_get", return_value=(200, body)) as stub:
        code, out, err = cli_runner("fetch", "--start", start, "--end", end, "--out", out_path)
    assert code == 0
    url = stub.call_args[0][0]
parts = urllib.parse.urlsplit(url)
query = urllib.parse.parse_qs(parts.query)
assert parts.scheme == "https"
assert parts.netloc == "earthquake.usgs.gov"
assert parts.path == "/fdsnws/event/1/query"
assert query["format"] == ["geojson"]
assert query["starttime"] == [start]
assert query["endtime"] == [end]
assert query["minmagnitude"] == ["2.5"]
assert query["orderby"] == ["time-asc"]
=== END AC fetch-request-url ===

=== AC fetch-min-mag-passthrough ===
Intent: An explicit --min-mag value is sent as minmagnitude, and build_url builds the same query directly.
Suite: scoped
Requires: executable=python3; scope=test

import json
import os
import tempfile
import urllib.parse
from unittest import mock

from cli.fetch import build_url
from cli.testing import cli_runner

start = "2025-02-01"
end = "2025-02-03"
min_mag = "4.5"
body = json.dumps({"type": "FeatureCollection", "features": []}).encode("utf-8")
with tempfile.TemporaryDirectory() as tmp:
    out_path = os.path.join(tmp, "saved.geojson")
    with mock.patch("cli.fetch.http_get", return_value=(200, body)) as stub:
        code, out, err = cli_runner(
            "fetch", "--min-mag", min_mag, "--end", end, "--start", start, "--out", out_path
        )
    assert code == 0
    url = stub.call_args[0][0]
query = urllib.parse.parse_qs(urllib.parse.urlsplit(url).query)
assert query["minmagnitude"] == [min_mag]
assert query["starttime"] == [start]
assert query["endtime"] == [end]
direct = urllib.parse.parse_qs(urllib.parse.urlsplit(build_url(start, end, min_mag)).query)
assert direct == query
=== END AC fetch-min-mag-passthrough ===

=== AC fetch-usage-errors ===
Intent: Missing required options, an unlisted option, or an extra positional argument exit 2, make no HTTP call, and write no file.
Suite: scoped
Requires: executable=python3; scope=test

import os
import tempfile
from unittest import mock

from cli.testing import cli_runner

with tempfile.TemporaryDirectory() as tmp:
    out_path = os.path.join(tmp, "saved.geojson")
    cases = [
        ("fetch", "--end", "2025-01-08", "--out", out_path),
        ("fetch", "--start", "2025-01-01", "--out", out_path),
        ("fetch", "--start", "2025-01-01", "--end", "2025-01-08"),
        ("fetch", "--start", "2025-01-01", "--end", "2025-01-08", "--out", out_path, "extra"),
        ("fetch", "--start", "2025-01-01", "--end", "2025-01-08", "--out", out_path, "--n", "3"),
        ("fetch", "--start", "2025-01-01", "--end", "2025-01-08", "--min-mag", "big", "--out", out_path),
    ]
    with mock.patch("cli.fetch.http_get", return_value=(200, b"{}")) as stub:
        for args in cases:
            code, out, err = cli_runner(*args)
            assert code == 2, args
            assert out == "", args
        assert stub.call_count == 0
    assert not os.path.exists(out_path)
=== END AC fetch-usage-errors ===

=== AC fetch-http-get-uses-urllib ===
Intent: http_get returns the status and body from urllib.request.urlopen, which is stubbed so no network connection is opened.
Suite: scoped
Requires: executable=python3; scope=test

from unittest import mock

from cli.fetch import http_get

payload = b"payload bytes"
status = 200


class FakeResponse:
    def __init__(self, code, data):
        self.status = code
        self._data = data

    def read(self):
        return self._data

    def getcode(self):
        return self.status

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


with mock.patch("urllib.request.urlopen", return_value=FakeResponse(status, payload)) as opener:
    got_status, got_body = http_get("https://example.invalid/query")
assert opener.call_count == 1
assert got_status == status
assert got_body == payload
=== END AC fetch-http-get-uses-urllib ===

## User Acceptance

- None.

## Guardrails

- Tests never open a network connection; every fetch test replaces `cli.fetch.http_get` or `urllib.request.urlopen`.
- The saved file is the response body unchanged: no re-serialization, re-encoding, or newline translation.
- The output file is written only after the response is validated.
- Only the `fetch` command touches the network; report commands never do.
