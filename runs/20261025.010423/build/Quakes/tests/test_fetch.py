"""Fetch story: download a USGS date range and save the response body unchanged. HTTP is always stubbed."""

import csv
import io
import json
import os
import urllib.parse
from unittest import mock

from cli.fetch import build_url, http_get


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


def _empty_body():
    return json.dumps({"type": "FeatureCollection", "features": []}).encode("utf-8")


# ── Declared acceptance assertions ──────────────────────────────────────────────────────


def test_fetch_saves_body_unchanged(tmp_path, cli_runner):
    features = [
        {"type": "Feature", "properties": {"mag": 5.1, "place": "Awash, Ethiopia", "time": 1735706358208, "tsunami": 0},
         "geometry": {"type": "Point", "coordinates": [40.0, 9.0, 10]}, "id": "a" + str(i)}
        for i in range(3)
    ]
    body = json.dumps({"type": "FeatureCollection", "features": features}, indent=3, ensure_ascii=False).encode("utf-8") + b"\n\n"
    out_path = os.path.join(tmp_path, "saved.geojson")
    with mock.patch("cli.fetch.http_get", return_value=(200, body)) as stub:
        code, out, _ = cli_runner("fetch", "--start", "2025-01-01", "--end", "2025-01-08", "--out", out_path)
    assert code == 0
    assert stub.call_count == 1
    with open(out_path, "rb") as fh:
        assert fh.read() == body
    rows = list(csv.reader(io.StringIO(out)))
    assert rows == [["fetched", str(len(features))]]


def test_fetch_request_url(tmp_path, cli_runner):
    start, end = "2025-01-01", "2025-01-08"
    out_path = os.path.join(tmp_path, "saved.geojson")
    with mock.patch("cli.fetch.http_get", return_value=(200, _empty_body())) as stub:
        code, _, _ = cli_runner("fetch", "--start", start, "--end", end, "--out", out_path)
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


def test_fetch_min_mag_passthrough(tmp_path, cli_runner):
    start, end, min_mag = "2025-02-01", "2025-02-03", "4.5"
    out_path = os.path.join(tmp_path, "saved.geojson")
    with mock.patch("cli.fetch.http_get", return_value=(200, _empty_body())) as stub:
        code, _, _ = cli_runner("fetch", "--min-mag", min_mag, "--end", end, "--start", start, "--out", out_path)
    assert code == 0
    url = stub.call_args[0][0]
    query = urllib.parse.parse_qs(urllib.parse.urlsplit(url).query)
    assert query["minmagnitude"] == [min_mag]
    assert query["starttime"] == [start]
    assert query["endtime"] == [end]
    direct = urllib.parse.parse_qs(urllib.parse.urlsplit(build_url(start, end, min_mag)).query)
    assert direct == query


def test_fetch_usage_errors(tmp_path, cli_runner):
    out_path = os.path.join(tmp_path, "saved.geojson")
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
            code, out, _ = cli_runner(*args)
            assert code == 2, args
            assert out == "", args
        assert stub.call_count == 0
    assert not os.path.exists(out_path)


def test_fetch_http_get_uses_urllib():
    payload = b"payload bytes"
    status = 200
    with mock.patch("urllib.request.urlopen", return_value=FakeResponse(status, payload)) as opener:
        got_status, got_body = http_get("https://example.invalid/query")
    assert opener.call_count == 1
    assert got_status == status
    assert got_body == payload


# ── Finer coverage ──────────────────────────────────────────────────────────────────────


def test_build_url_default_min_mag_is_text_given():
    query = urllib.parse.parse_qs(urllib.parse.urlsplit(build_url("2025-03-01", "2025-03-02", "2.5")).query)
    assert query["minmagnitude"] == ["2.5"]


def test_fetch_reports_zero_features_for_empty_feed(tmp_path, cli_runner):
    out_path = os.path.join(tmp_path, "saved.geojson")
    with mock.patch("cli.fetch.http_get", return_value=(200, _empty_body())):
        code, out, _ = cli_runner("fetch", "--start", "2025-01-01", "--end", "2025-01-02", "--out", out_path)
    assert code == 0
    assert list(csv.reader(io.StringIO(out))) == [["fetched", "0"]]
    assert os.path.exists(out_path)


def test_fetch_overwrites_existing_file_on_success(tmp_path, cli_runner):
    out_path = os.path.join(tmp_path, "saved.geojson")
    with open(out_path, "wb") as fh:
        fh.write(b"old contents")
    body = _empty_body()
    with mock.patch("cli.fetch.http_get", return_value=(200, body)):
        code, _, _ = cli_runner("fetch", "--start", "2025-01-01", "--end", "2025-01-02", "--out", out_path)
    assert code == 0
    with open(out_path, "rb") as fh:
        assert fh.read() == body
