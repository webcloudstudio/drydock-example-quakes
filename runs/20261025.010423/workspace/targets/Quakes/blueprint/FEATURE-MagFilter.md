# FEATURE: Magnitude Filter

| Field       | Value |
|-------------|-------|
| Version     | 20261025 V1 |
| Description | Keep only events whose magnitude is at least the --min-mag value. |
| Depends On  | FEATURE-EventExtraction.md |
| Provides    | filter_events |
| Consumes    | extract_events |

## Purpose

`--min-mag <m>` applies to every report. `filter_events` is the single shared implementation, so
all reports share one inclusive rule: `mag >= m`.

## Interface

- Module: `cli.feed`. Function: `filter_events(events, min_mag) -> list[Event]`.
- `min_mag` is a `float` or `None`. `None` keeps every event.
- An event whose magnitude equals `min_mag` is kept.
- Feed order is preserved. The input list is not mutated.

## Programmatic Acceptance

=== AC filter-threshold-inclusive ===
Intent: Events at or above the threshold are kept, including those exactly at it, and order is preserved.
Requires: executable=python3; scope=test

from cli.feed import extract_events, filter_events


def feature(ident, mag):
    return {"type": "Feature", "id": ident,
            "properties": {"mag": mag, "place": "P", "time": 1735706358000, "tsunami": 0},
            "geometry": {"type": "Point", "coordinates": [1.0, 2.0, 3.0]}}


mags = [5.0, 5.4, 5.5, 5.6, 7.1, 5.49]
features = [feature(f"e{i}", m) for i, m in enumerate(mags)]
events = extract_events(features)
threshold = 5.5
kept = filter_events(events, threshold)
expected_ids = [f"e{i}" for i, m in enumerate(mags) if m >= threshold]
assert [e.id for e in kept] == expected_ids
assert any(e.mag == threshold for e in kept)
=== END AC filter-threshold-inclusive ===

=== AC filter-none-keeps-all ===
Intent: A None threshold keeps every event and does not mutate the input.
Requires: executable=python3; scope=test

from cli.feed import extract_events, filter_events

features = [{"type": "Feature", "id": f"e{i}",
             "properties": {"mag": 5.0 + i, "place": "P", "time": 1735706358000, "tsunami": 0},
             "geometry": {"type": "Point", "coordinates": [1.0, 2.0, 3.0]}} for i in range(4)]
events = extract_events(features)
before = list(events)
kept = filter_events(events, None)
assert [e.id for e in kept] == [e.id for e in before]
assert events == before
=== END AC filter-none-keeps-all ===

=== AC filter-nothing-matches ===
Intent: A threshold above every magnitude yields an empty list rather than an error.
Requires: executable=python3; scope=test

from cli.feed import extract_events, filter_events

features = [{"type": "Feature", "id": "only",
             "properties": {"mag": 5.2, "place": "P", "time": 1735706358000, "tsunami": 0},
             "geometry": {"type": "Point", "coordinates": [1.0, 2.0, 3.0]}}]
events = extract_events(features)
assert filter_events(events, 9.0) == []
=== END AC filter-nothing-matches ===

## User Acceptance

- None.

## Guardrails

- The comparison is `mag >= min_mag`, never `>`.
- Standard library only.
