"""Fetch-failure story: network, HTTP, and body errors exit 1 and never create or alter the output file."""

import io
import json
import os
import urllib.error
from unittest import mock

import pytest

from cli.errors import OperationalError
from cli.fetch import fetch_command
from cli.options import parse_args

VALID = json.dumps({"type": "FeatureCollection", "features": []}).encode("utf-8")
DATES = ["fetch", "--start", "2025-01-01", "--end", "2025-01-02"]


# ── Declared acceptance assertions ──────────────────────────────────────────────────────


def test_fetch_failure_http_status(tmp_path, cli_runner):
    out_path = os.path.join(tmp_path, "saved.geojson")
    with mock.patch("cli.fetch.http_get", return_value=(500, VALID)):
        code, out, err = cli_runner(*DATES, "--out", out_path)
    assert code == 1
    assert out == ""
    assert len(err.strip().splitlines()) == 1
    assert not os.path.exists(out_path)


def test_fetch_failure_bad_body(tmp_path, cli_runner):
    bodies = [
        b"this is not json",
        json.dumps({"type": "Feature", "properties": {}, "geometry": None}).encode("utf-8"),
        json.dumps({"type": "FeatureCollection"}).encode("utf-8"),
        json.dumps({"type": "FeatureCollection", "features": "nope"}).encode("utf-8"),
        json.dumps([1, 2, 3]).encode("utf-8"),
    ]
    for n, body in enumerate(bodies):
        out_path = os.path.join(tmp_path, "saved" + str(n) + ".geojson")
        with mock.patch("cli.fetch.http_get", return_value=(200, body)):
            code, out, _ = cli_runner(*DATES, "--out", out_path)
        assert code == 1, n
        assert out == "", n
        assert not os.path.exists(out_path), n


def test_fetch_failure_network_error(tmp_path, cli_runner):
    first = os.path.join(tmp_path, "first.geojson")
    with mock.patch("cli.fetch.http_get", side_effect=OSError("unreachable")):
        code, out, _ = cli_runner(*DATES, "--out", first)
    assert code == 1
    assert out == ""
    assert not os.path.exists(first)

    second = os.path.join(tmp_path, "second.geojson")
    with mock.patch("urllib.request.urlopen", side_effect=urllib.error.URLError("no route")) as opener:
        code2, out2, _ = cli_runner(*DATES, "--out", second)
    assert opener.call_count == 1
    assert code2 == 1
    assert out2 == ""
    assert not os.path.exists(second)


def test_fetch_failure_http_error_status(tmp_path, cli_runner):
    error = urllib.error.HTTPError("https://example.invalid", 503, "unavailable", {}, io.BytesIO(b"down"))
    out_path = os.path.join(tmp_path, "saved.geojson")
    with mock.patch("urllib.request.urlopen", side_effect=error):
        code, out, _ = cli_runner(*DATES, "--out", out_path)
    assert code == 1
    assert out == ""
    assert not os.path.exists(out_path)


def test_fetch_failure_preserves_existing_file(tmp_path, cli_runner):
    original = b"previous contents, not JSON\n"
    out_path = os.path.join(tmp_path, "saved.geojson")
    with open(out_path, "wb") as fh:
        fh.write(original)
    with mock.patch("cli.fetch.http_get", return_value=(404, b"missing")):
        code, _, _ = cli_runner(*DATES, "--out", out_path)
    assert code == 1
    with open(out_path, "rb") as fh:
        assert fh.read() == original
    with mock.patch("cli.fetch.http_get", return_value=(200, b"not json")):
        code2, _, _ = cli_runner(*DATES, "--out", out_path)
    assert code2 == 1
    with open(out_path, "rb") as fh:
        assert fh.read() == original


# ── Finer coverage ──────────────────────────────────────────────────────────────────────


@pytest.mark.parametrize("error", [OSError("reset by peer"), TimeoutError("timed out")])
def test_fetch_converts_os_errors_from_http_get(tmp_path, error):
    out_path = tmp_path / "saved.geojson"
    parsed = parse_args([*DATES, "--out", str(out_path)])
    with mock.patch("cli.fetch.http_get", side_effect=error):
        with pytest.raises(OperationalError):
            fetch_command(parsed)
    assert not out_path.exists()


def test_fetch_rejects_non_utf8_body(tmp_path, cli_runner):
    out_path = os.path.join(tmp_path, "saved.geojson")
    with mock.patch("cli.fetch.http_get", return_value=(200, b"\xff\xfe\x00bad")):
        code, out, _ = cli_runner(*DATES, "--out", out_path)
    assert code == 1
    assert out == ""
    assert not os.path.exists(out_path)


def test_fetch_unwritable_output_exits_one(tmp_path, cli_runner):
    out_path = os.path.join(tmp_path, "missing-dir", "saved.geojson")
    with mock.patch("cli.fetch.http_get", return_value=(200, VALID)):
        code, out, _ = cli_runner(*DATES, "--out", out_path)
    assert code == 1
    assert out == ""
