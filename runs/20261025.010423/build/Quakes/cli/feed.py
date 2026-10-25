"""Read a saved USGS GeoJSON feed, extract event records, and apply the magnitude filter.

Each function here is pure apart from `read_feed`, which reads one file. Failures surface only as
`OperationalError`; nothing is written to standard output.
"""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from cli.errors import OperationalError


@dataclass(frozen=True)
class Event:
    """One earthquake, reduced to the fields the reports need."""

    id: str
    mag: float
    place: str | None
    time_ms: int
    tsunami: int
    lon: float
    lat: float
    depth_km: float


def read_feed(path: str | Path) -> list[Any]:
    """Return the `features` array of a GeoJSON FeatureCollection file, unchanged.

    Raises `OperationalError` when the file cannot be read, is not JSON, or is not a FeatureCollection
    object whose `features` value is an array.
    """
    try:
        text = Path(path).read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        raise OperationalError(f"cannot read {path}: {getattr(exc, 'strerror', None) or exc}") from exc
    return features_from_text(text, str(path))


def features_from_text(text: str, source: str) -> list[Any]:
    """Return the `features` array of GeoJSON FeatureCollection `text`; `source` names the input in errors.

    Raises `OperationalError` when the text is not JSON, or is not a FeatureCollection object whose
    `features` value is an array. `read_feed` and the `fetch` command both validate through here.
    """
    try:
        document = json.loads(text)
    except json.JSONDecodeError as exc:
        raise OperationalError(f"{source} is not valid JSON") from exc
    if not isinstance(document, dict) or document.get("type") != "FeatureCollection":
        raise OperationalError(f"{source} is not a GeoJSON FeatureCollection")
    features = document.get("features")
    if not isinstance(features, list):
        raise OperationalError(f"{source} has no features array")
    return features


def extract_events(features: list[Any]) -> list[Event]:
    """Turn feed features into `Event` records in feed order, dropping events whose magnitude is null."""
    return [event for event in (_event(feature) for feature in features) if event is not None]


def filter_events(events: list[Event], min_mag: float | None) -> list[Event]:
    """Keep events with `mag >= min_mag`, in order. `None` keeps every event."""
    if min_mag is None:
        return list(events)
    return [event for event in events if event.mag >= min_mag]


def _event(feature: Any) -> Event | None:
    try:
        props = feature["properties"]
        mag = props["mag"]
        if mag is None:
            return None
        lon, lat, depth = feature["geometry"]["coordinates"][:3]
        return Event(
            id=feature["id"],
            mag=float(mag),
            place=props.get("place"),
            time_ms=int(props["time"]),
            tsunami=int(props.get("tsunami") or 0),
            lon=float(lon),
            lat=float(lat),
            depth_km=float(depth),
        )
    except (KeyError, IndexError, TypeError, ValueError) as exc:
        raise OperationalError(f"malformed feature: {exc!r}") from exc
