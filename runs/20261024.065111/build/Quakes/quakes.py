"""USGS earthquake feed retrieval."""

from __future__ import annotations

import json
import re
import urllib.request
from datetime import date
from pathlib import Path
from typing import Any

urlopen = urllib.request.urlopen
_ENDPOINT = "https://earthquake.usgs.gov/fdsnws/event/1/query"
_MAGNITUDE = re.compile(r"-?[0-9]+(?:\.[0-9]+)?\Z")


class FetchError(Exception):
    """An operational failure while retrieving or saving a feed."""


def fetch(*, start: str, end: str, out: str | Path, min_mag: str = "2.5") -> int:
    """Fetch a valid GeoJSON FeatureCollection and save its body unchanged."""
    try:
        date.fromisoformat(start)
        date.fromisoformat(end)
    except (TypeError, ValueError) as exc:
        raise ValueError("dates must use YYYY-MM-DD") from exc
    if not _MAGNITUDE.fullmatch(min_mag):
        raise ValueError("magnitude must be a decimal number")

    params = {
        "format": "geojson",
        "starttime": start,
        "endtime": end,
        "minmagnitude": min_mag,
        "orderby": "time-asc",
    }
    request = urllib.request.Request(f"{_ENDPOINT}?{urllib.parse.urlencode(params)}")
    try:
        with urlopen(request) as response:
            status = response.status
            status = status() if callable(status) else status
            body = response.read()
        if status != 200:
            raise FetchError(f"USGS returned HTTP {status}")
        document: Any = json.loads(body)
        if (not isinstance(document, dict) or document.get("type") != "FeatureCollection"
                or not isinstance(document.get("features"), list)):
            raise FetchError("response is not a GeoJSON FeatureCollection")
        count = len(document["features"])
        Path(out).write_bytes(body)
        return count
    except FetchError:
        raise
    except Exception as exc:
        raise FetchError(str(exc) or exc.__class__.__name__) from exc
