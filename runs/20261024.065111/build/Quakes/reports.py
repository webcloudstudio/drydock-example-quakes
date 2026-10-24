"""GeoJSON event parsing and CSV reports for saved earthquake feeds."""

from __future__ import annotations

import csv
import io
import json
import math
from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from typing import Any


class ReportError(Exception):
    """Invalid or unreadable input supplied to a report command."""


@dataclass(frozen=True)
class Event:
    mag: Decimal | None
    place: str
    time_ms: int
    tsunami: int
    depth: Decimal | None
    lon: float | None
    lat: float | None
    event_id: str

    @property
    def time(self) -> datetime:
        return datetime.fromtimestamp(self.time_ms / 1000, timezone.utc)

    @property
    def timestamp(self) -> str:
        return self.time.strftime("%Y-%m-%dT%H:%M:%SZ")


def _decimal(value: Any, *, nullable: bool = False) -> Decimal | None:
    if value is None and nullable:
        return None
    if isinstance(value, bool):
        raise ValueError("boolean numeric value")
    result = Decimal(str(value))
    if not result.is_finite():
        raise ValueError("non-finite numeric value")
    return result


def read_events(path: str | Path) -> list[Event]:
    try:
        document = json.loads(Path(path).read_text(encoding="utf-8"))
        if not isinstance(document, dict) or document.get("type") != "FeatureCollection" or not isinstance(document.get("features"), list):
            raise ValueError("input is not a GeoJSON FeatureCollection")
        events = []
        for feature in document["features"]:
            if not isinstance(feature, dict) or feature.get("type") != "Feature" or not isinstance(feature.get("properties"), dict):
                raise ValueError("invalid GeoJSON feature")
            props = feature["properties"]
            raw_time = props.get("time")
            if isinstance(raw_time, bool) or not isinstance(raw_time, (int, float)) or not math.isfinite(raw_time):
                raise ValueError("feature has invalid time")
            geometry = feature.get("geometry")
            coords = geometry.get("coordinates") if isinstance(geometry, dict) and geometry.get("type") == "Point" else None
            lon = lat = None
            depth = None
            if isinstance(coords, list) and len(coords) >= 2:
                lon, lat = float(coords[0]), float(coords[1])
                if len(coords) >= 3 and coords[2] is not None:
                    depth = _decimal(coords[2])
            place = props.get("place")
            events.append(Event(
                _decimal(props.get("mag"), nullable=True),
                "Unknown" if place is None else str(place), int(raw_time),
                int(props.get("tsunami") or 0), depth, lon, lat,
                str(feature.get("id", "")),
            ))
        return events
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError, TypeError, OverflowError) as exc:
        raise ReportError(str(exc) or "invalid GeoJSON") from exc


def filtered(events: list[Event], minimum: str | None) -> list[Event]:
    threshold = Decimal(minimum) if minimum is not None else None
    return [e for e in events if e.mag is not None and (threshold is None or e.mag >= threshold)]


def fmt(value: Decimal | None, places: int = 1) -> str:
    if value is None:
        return ""
    quantum = Decimal(1).scaleb(-places)
    return str(value.quantize(quantum, rounding=ROUND_HALF_UP))


def csv_text(header: list[str], rows: list[list[Any]]) -> str:
    out = io.StringIO(newline="")
    writer = csv.writer(out, lineterminator="\n")
    writer.writerow(header)
    writer.writerows(rows)
    return out.getvalue()


def summary(events: list[Event]) -> str:
    head = ["events", "first", "last", "min_mag", "max_mag", "mean_mag", "tsunami"]
    if not events:
        return csv_text(head, [[0, "", "", "", "", "", 0]])
    mags = [e.mag for e in events if e.mag is not None]
    mean = (sum(mags, Decimal(0)) / len(mags)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    ordered = sorted(events, key=lambda e: e.time_ms)
    return csv_text(head, [[len(events), ordered[0].timestamp, ordered[-1].timestamp,
                            fmt(min(mags)), fmt(max(mags)), str(mean),
                            sum(1 for e in events if e.tsunami != 0)]])


def daily(events: list[Event]) -> str:
    groups: dict[str, list[Event]] = {}
    for event in events:
        groups.setdefault(event.timestamp[:10], []).append(event)
    rows = [[day, len(group), fmt(max(e.mag for e in group if e.mag is not None))]
            for day, group in sorted(groups.items())]
    rows.append(["TOTAL", len(events), fmt(max((e.mag for e in events if e.mag is not None), default=None))])
    return csv_text(["date", "events", "max_mag"], rows)


def top(events: list[Event], count: int) -> str:
    ordered = sorted(events, key=lambda e: (-e.mag, e.time_ms))[:count]
    rows = [[e.timestamp, fmt(e.mag), fmt(e.depth), e.place, e.event_id] for e in ordered]
    return csv_text(["time", "mag", "depth_km", "place", "id"], rows)


def region(place: str) -> str:
    return place.rsplit(", ", 1)[-1]


def regions(events: list[Event]) -> str:
    groups: dict[str, list[Event]] = {}
    for event in events:
        groups.setdefault(region(event.place), []).append(event)
    ordered = sorted(groups.items(), key=lambda pair: (-len(pair[1]), pair[0]))
    return csv_text(["region", "events", "max_mag"], [[name, len(group), fmt(max(e.mag for e in group if e.mag is not None))] for name, group in ordered])


def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    radians = math.radians
    dlat, dlon = radians(lat2 - lat1), radians(lon2 - lon1)
    a = math.sin(dlat / 2) ** 2 + math.cos(radians(lat1)) * math.cos(radians(lat2)) * math.sin(dlon / 2) ** 2
    return 6371.0 * 2 * math.asin(min(1.0, math.sqrt(a)))


def near(events: list[Event], lat: float, lon: float, radius: float) -> str:
    matches = []
    for event in events:
        if event.lat is None or event.lon is None:
            continue
        distance = haversine(lat, lon, event.lat, event.lon)
        if distance <= radius:
            matches.append((distance, event))
    matches.sort(key=lambda pair: (pair[0], pair[1].time_ms))
    rows = [[fmt(Decimal(str(distance))), event.timestamp, fmt(event.mag), event.place, event.event_id]
            for distance, event in matches]
    return csv_text(["distance_km", "time", "mag", "place", "id"], rows)
