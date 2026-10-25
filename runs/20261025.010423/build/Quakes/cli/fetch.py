"""The `fetch` command: download a USGS date range and save the response body unchanged.

`http_get` is the only function in the product that opens a connection. The handler validates the body
with the rules `read_feed` applies to a saved file, and writes the output file only after validation.
Any failure raises `OperationalError` before the output file is touched.
"""

import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

from cli.errors import OperationalError
from cli.feed import features_from_text
from cli.formatting import render_csv
from cli.options import Parsed

FEED_URL = "https://earthquake.usgs.gov/fdsnws/event/1/query"
TIMEOUT_SECONDS = 30.0


def build_url(start: str, end: str, min_mag: str) -> str:
    """The USGS FDSN query URL for a date range, GeoJSON format, time-ascending order."""
    query = urllib.parse.urlencode(
        {
            "format": "geojson",
            "starttime": start,
            "endtime": end,
            "minmagnitude": min_mag,
            "orderby": "time-asc",
        }
    )
    return f"{FEED_URL}?{query}"


def http_get(url: str) -> tuple[int, bytes]:
    """Return (HTTP status, body bytes) for every response, including non-200 ones.

    Raises `OperationalError` for a network failure or timeout, which surface as `OSError` subclasses.
    """
    try:
        with urllib.request.urlopen(url, timeout=TIMEOUT_SECONDS) as response:
            return response.getcode(), response.read()
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read()
    except OSError as exc:
        raise OperationalError(f"network request failed: {getattr(exc, 'reason', None) or exc}") from exc


def fetch_command(parsed: Parsed) -> str:
    """Download the range, validate it, save the body unchanged to `--out`, and report the feature count."""
    url = build_url(parsed.start, parsed.end, str(parsed.min_mag))
    try:
        status, body = http_get(url)
    except OSError as exc:
        raise OperationalError(f"network request failed: {exc}") from exc
    if status != 200:
        raise OperationalError(f"USGS responded with HTTP status {status}")
    try:
        text = body.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise OperationalError("response body is not UTF-8 text") from exc
    features = features_from_text(text, "response body")
    try:
        Path(parsed.out).write_bytes(body)
    except OSError as exc:
        raise OperationalError(f"cannot write {parsed.out}: {exc.strerror or exc}") from exc
    return render_csv([["fetched", str(len(features))]])
