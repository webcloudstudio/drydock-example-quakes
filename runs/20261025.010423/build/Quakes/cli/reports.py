"""The summary, regions, daily, top, and near reports.

`compute_*` functions are pure: they take kept events and return CSV rows (header first) of
preformatted strings. Each `*_command` handler loads the feed named on the command line, runs the
pipeline, and returns the full standard-output text; `main` writes it only after the handler returns.
"""

import math
from dataclasses import dataclass

from cli.feed import Event, extract_events, filter_events, read_feed
from cli.formatting import format_decimal, format_mag, format_mean, format_time, render_csv
from cli.options import Parsed

EARTH_RADIUS_KM = 6371.0
UNKNOWN_REGION = "Unknown"

SUMMARY_HEADER = ["events", "first", "last", "min_mag", "max_mag", "mean_mag", "tsunami"]
REGIONS_HEADER = ["region", "events", "max_mag"]
DAILY_HEADER = ["date", "events", "max_mag"]
TOP_HEADER = ["time", "mag", "depth_km", "place", "id"]
NEAR_HEADER = ["distance_km", "time", "mag", "place", "id"]


@dataclass
class _Group:
    """Running count and maximum magnitude for one region or one UTC date."""

    count: int = 0
    max_mag: float = -math.inf

    def add(self, mag: float) -> None:
        self.count += 1
        self.max_mag = max(self.max_mag, mag)


def load_events(path: str, min_mag: float | None) -> list[Event]:
    """Read the feed at `path`, drop null magnitudes, and apply `--min-mag`."""
    return filter_events(extract_events(read_feed(path)), min_mag)


# ── summary ──────────────────────────────────────────────────────────────────────────────


def compute_summary(events: list[Event]) -> list[list[str]]:
    """One row: count, first and last time, magnitude range, mean, and tsunami count."""
    if not events:
        return [SUMMARY_HEADER, ["0", "", "", "", "", "", "0"]]
    mags = [event.mag for event in events]
    return [
        SUMMARY_HEADER,
        [
            str(len(events)),
            format_time(min(event.time_ms for event in events)),
            format_time(max(event.time_ms for event in events)),
            format_mag(min(mags)),
            format_mag(max(mags)),
            format_mean(math.fsum(mags) / len(mags)),
            str(sum(1 for event in events if event.tsunami == 1)),
        ],
    ]


def summary_command(parsed: Parsed) -> str:
    return render_csv(compute_summary(load_events(parsed.file, parsed.min_mag)))


# ── regions ──────────────────────────────────────────────────────────────────────────────


def region_of(place: str | None) -> str:
    """The text after the last ", " in `place`, the whole place when there is none, `Unknown` for null."""
    if place is None:
        return UNKNOWN_REGION
    cut = place.rfind(", ")
    return place if cut < 0 else place[cut + 2 :]


def compute_regions(events: list[Event]) -> list[list[str]]:
    """Rows per region ordered by event count descending, then region name in code point order."""
    groups: dict[str, _Group] = {}
    for event in events:
        groups.setdefault(region_of(event.place), _Group()).add(event.mag)
    ordered = sorted(groups, key=lambda region: (-groups[region].count, region))
    return [REGIONS_HEADER] + [
        [region, str(groups[region].count), format_mag(groups[region].max_mag)] for region in ordered
    ]


def regions_command(parsed: Parsed) -> str:
    return render_csv(compute_regions(load_events(parsed.file, parsed.min_mag)))


# ── daily ────────────────────────────────────────────────────────────────────────────────


def compute_daily(events: list[Event]) -> tuple[list[list[str]], list[str]]:
    """Return (one row per UTC date ascending, the TOTAL row); the date is the first ten characters of the time."""
    groups: dict[str, _Group] = {}
    for event in events:
        groups.setdefault(format_time(event.time_ms)[:10], _Group()).add(event.mag)
    rows = [[day, str(group.count), format_mag(group.max_mag)] for day, group in sorted(groups.items())]
    total = ["TOTAL", str(len(events)), format_mag(max(e.mag for e in events)) if events else ""]
    return rows, total


def daily_command(parsed: Parsed) -> str:
    rows, total = compute_daily(load_events(parsed.file, parsed.min_mag))
    return render_csv([DAILY_HEADER, *rows, total])


# ── top ──────────────────────────────────────────────────────────────────────────────────


def compute_top(events: list[Event], n: int) -> list[list[str]]:
    """The first `n` events by magnitude descending, then time ascending; ties beyond that keep feed order."""
    ranked = sorted(events, key=lambda event: (-event.mag, event.time_ms))[:n]
    return [TOP_HEADER] + [
        [format_time(e.time_ms), format_mag(e.mag), format_decimal(e.depth_km), e.place or "", e.id]
        for e in ranked
    ]


def top_command(parsed: Parsed) -> str:
    return render_csv(compute_top(load_events(parsed.file, parsed.min_mag), parsed.n))


# ── near ─────────────────────────────────────────────────────────────────────────────────


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Great-circle distance in kilometres on a sphere of radius `EARTH_RADIUS_KM`; inputs in degrees."""
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    d_phi = phi2 - phi1
    d_lambda = math.radians(lon2 - lon1)
    h = math.sin(d_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2
    return 2 * EARTH_RADIUS_KM * math.asin(min(1.0, math.sqrt(h)))


def compute_near(events: list[Event], lat: float, lon: float, radius: float) -> list[list[str]]:
    """Events whose unrounded distance is at most `radius`, nearest first, then by time ascending."""
    hits = []
    for event in events:
        distance = haversine_km(lat, lon, event.lat, event.lon)
        if distance <= radius:
            hits.append((distance, event))
    hits.sort(key=lambda hit: (hit[0], hit[1].time_ms))
    return [NEAR_HEADER] + [
        [format_decimal(distance), format_time(e.time_ms), format_mag(e.mag), e.place or "", e.id]
        for distance, e in hits
    ]


def near_command(parsed: Parsed) -> str:
    events = load_events(parsed.file, parsed.min_mag)
    return render_csv(compute_near(events, parsed.lat, parsed.lon, parsed.radius))
