# FEATURE: Event Normalise

| Field       | Value |
|-------------|-------|
| Version     | 20261024 V1 |
| Description | Normalise event time, date and region and provide the shared number-formatting helpers. |
| Depends On  | FEATURE-FeedReader.md, ARCHITECTURE.md |
| Provides    | format_time, region_of, format_mag, format_one_decimal, format_two_decimal |
| Consumes    | read_events(path) |

## Purpose

Turn the raw values the reader returns into the text every report writes. These are pure functions
in modules under the `cli` package, so each is unit-tested on its own.

## Interface

| Function | Input | Output |
|---|---|---|
| `format_time(ms)` | integer milliseconds since the Unix epoch | UTC `YYYY-MM-DDTHH:MM:SSZ`, truncated (not rounded) to whole seconds |
| `region_of(place)` | place text or `None` | text after the last `, ` in `place`, the whole `place` when it has none, `Unknown` for `None` |
| `format_mag(mag)` | number | one decimal place, so `5` becomes `5.0` |
| `format_one_decimal(value)` | number | one decimal place, rounded half up (depth and distance) |
| `format_two_decimal(value)` | number | two decimal places, rounded half up (mean magnitude) |

An event's date is the first 10 characters of its formatted time. Half-up rounding uses `decimal`
over `Decimal(str(value))`, never float formatting.

## Programmatic Acceptance

=== AC normalise-format-time ===
Intent: format_time writes UTC to whole seconds, truncating the milliseconds rather than rounding them.

import importlib
import pkgutil
from datetime import datetime, timezone

import cli


def find(name):
    mods = [cli]
    for info in pkgutil.walk_packages(cli.__path__, "cli."):
        try:
            mods.append(importlib.import_module(info.name))
        except Exception:
            pass
    for mod in mods:
        if hasattr(mod, name):
            return getattr(mod, name)
    raise AssertionError("no function named " + name + " under the cli package")


format_time = find("format_time")
for ms in (0, 1735706358208, 1735706358999, 1736211916000, 1767225599999):
    expected = datetime.fromtimestamp(ms // 1000, timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    assert format_time(ms) == expected, ms
=== END AC normalise-format-time ===

=== AC normalise-date-prefix ===
Intent: The date of an event is the first 10 characters of its time and follows the UTC day boundary.

import importlib
import pkgutil
from datetime import datetime, timezone

import cli


def find(name):
    mods = [cli]
    for info in pkgutil.walk_packages(cli.__path__, "cli."):
        try:
            mods.append(importlib.import_module(info.name))
        except Exception:
            pass
    for mod in mods:
        if hasattr(mod, name):
            return getattr(mod, name)
    raise AssertionError("no function named " + name + " under the cli package")


format_time = find("format_time")
last_second = 1735775999999
next_day = 1735776000000
for ms in (last_second, next_day):
    day = datetime.fromtimestamp(ms // 1000, timezone.utc).date().isoformat()
    assert format_time(ms)[:10] == day, ms
assert format_time(last_second)[:10] != format_time(next_day)[:10]
=== END AC normalise-date-prefix ===

=== AC normalise-region ===
Intent: region_of returns the text after the last comma-space, or the whole place when there is none.

import importlib
import pkgutil

import cli


def find(name):
    mods = [cli]
    for info in pkgutil.walk_packages(cli.__path__, "cli."):
        try:
            mods.append(importlib.import_module(info.name))
        except Exception:
            pass
    for mod in mods:
        if hasattr(mod, name):
            return getattr(mod, name)
    raise AssertionError("no function named " + name + " under the cli package")


region_of = find("region_of")

region = "Papua New Guinea"
assert region_of("64 km NW of Rabaul, " + region) == region

nested_region = "Japan"
assert region_of("Izu Islands, Honshu, " + nested_region) == nested_region

whole = "South Sandwich Islands region"
assert region_of(whole) == whole

comma_no_space = "Alpha,Beta"
assert region_of(comma_no_space) == comma_no_space

trailing = "Somewhere, "
assert region_of(trailing) == ""
=== END AC normalise-region ===

=== AC normalise-null-place ===
Intent: A null place has the region Unknown.

import importlib
import pkgutil

import cli


def find(name):
    mods = [cli]
    for info in pkgutil.walk_packages(cli.__path__, "cli."):
        try:
            mods.append(importlib.import_module(info.name))
        except Exception:
            pass
    for mod in mods:
        if hasattr(mod, name):
            return getattr(mod, name)
    raise AssertionError("no function named " + name + " under the cli package")


region_of = find("region_of")
assert region_of(None) == "Unknown"
=== END AC normalise-null-place ===

=== AC normalise-format-mag ===
Intent: format_mag writes one decimal place, including for whole-number magnitudes.

import importlib
import pkgutil

import cli


def find(name):
    mods = [cli]
    for info in pkgutil.walk_packages(cli.__path__, "cli."):
        try:
            mods.append(importlib.import_module(info.name))
        except Exception:
            pass
    for mod in mods:
        if hasattr(mod, name):
            return getattr(mod, name)
    raise AssertionError("no function named " + name + " under the cli package")


format_mag = find("format_mag")
for mag in (5, 5.0, 5.4, 7.1, 6):
    assert format_mag(mag) == f"{float(mag):.1f}", mag
=== END AC normalise-format-mag ===

=== AC normalise-one-decimal-half-up ===
Intent: format_one_decimal rounds half up to one decimal place.

import importlib
import pkgutil
from decimal import Decimal, ROUND_HALF_UP

import cli


def find(name):
    mods = [cli]
    for info in pkgutil.walk_packages(cli.__path__, "cli."):
        try:
            mods.append(importlib.import_module(info.name))
        except Exception:
            pass
    for mod in mods:
        if hasattr(mod, name):
            return getattr(mod, name)
    raise AssertionError("no function named " + name + " under the cli package")


format_one_decimal = find("format_one_decimal")
for value in (10.25, 2.75, 0.5, 10.0, 46, 358.0, 214.84, 0.25, 1288.35):
    expected = str(Decimal(str(value)).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP))
    assert format_one_decimal(value) == expected, value
=== END AC normalise-one-decimal-half-up ===

=== AC normalise-two-decimal-half-up ===
Intent: format_two_decimal rounds half up to two decimal places.

import importlib
import pkgutil
from decimal import Decimal, ROUND_HALF_UP

import cli


def find(name):
    mods = [cli]
    for info in pkgutil.walk_packages(cli.__path__, "cli."):
        try:
            mods.append(importlib.import_module(info.name))
        except Exception:
            pass
    for mod in mods:
        if hasattr(mod, name):
            return getattr(mod, name)
    raise AssertionError("no function named " + name + " under the cli package")


format_two_decimal = find("format_two_decimal")
for value in (5.125, 5.375, 5.0, 5.875, 5.3, 0.005):
    expected = str(Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))
    assert format_two_decimal(value) == expected, value
=== END AC normalise-two-decimal-half-up ===

## User Acceptance

- None.

## Guardrails

- Rounding uses `decimal` half up, never float formatting.
- Time is always UTC and truncated to whole seconds, never rounded.
- No value is embedded; every result is computed from the argument.
