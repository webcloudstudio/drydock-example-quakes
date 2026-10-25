"""Parse and validate the command line into a `Parsed` record.

Parsing never touches the file system and never prints. Every malformed invocation raises
`UsageError`, which `main` maps to exit code 2. The grammar is hand-written rather than argparse so
that numeric values, repeated options, and extra positionals follow FEATURE-Options exactly.
"""

import datetime
import re
from dataclasses import dataclass

from cli.errors import UsageError

DEFAULT_TOP_COUNT = 10
DEFAULT_FETCH_MIN_MAG = 2.5

_NUMBER = re.compile(r"-?[0-9]+(\.[0-9]+)?")
_COUNT = re.compile(r"[0-9]+")
_DATE = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}")


@dataclass(frozen=True)
class Parsed:
    """A validated invocation. Options a command does not take keep their defaults."""

    command: str
    min_mag: float | None = None
    n: int = DEFAULT_TOP_COUNT
    lat: float | None = None
    lon: float | None = None
    radius: float | None = None
    start: str | None = None
    end: str | None = None
    out: str | None = None
    file: str | None = None


@dataclass(frozen=True)
class _Spec:
    """Which options a command takes, which it requires, and whether it takes the file argument."""

    options: frozenset[str]
    required: frozenset[str] = frozenset()
    takes_file: bool = True


_MIN_MAG = "--min-mag"

_SPECS: dict[str, _Spec] = {
    "fetch": _Spec(
        options=frozenset({"--start", "--end", "--min-mag", "--out"}),
        required=frozenset({"--start", "--end", "--out"}),
        takes_file=False,
    ),
    "summary": _Spec(options=frozenset({_MIN_MAG})),
    "top": _Spec(options=frozenset({_MIN_MAG, "--n"})),
    "daily": _Spec(options=frozenset({_MIN_MAG})),
    "regions": _Spec(options=frozenset({_MIN_MAG})),
    "near": _Spec(
        options=frozenset({"--lat", "--lon", "--radius", _MIN_MAG}),
        required=frozenset({"--lat", "--lon", "--radius"}),
    ),
}


def parse_args(argv: list[str]) -> Parsed:
    """Return the validated `Parsed` for `argv`, or raise `UsageError` for any malformed invocation."""
    if not argv:
        raise UsageError("missing command")
    command, rest = argv[0], argv[1:]
    spec = _SPECS.get(command)
    if spec is None:
        raise UsageError(f"unknown command: {command!r}")

    raw = _collect_options(command, spec, rest)
    positionals = _collect_positionals(rest, spec)
    missing = sorted(spec.required - raw.keys())
    if missing:
        raise UsageError(f"{command} requires {', '.join(missing)}")
    if spec.takes_file and len(positionals) != 1:
        raise UsageError(f"{command} requires exactly one file argument")
    if not spec.takes_file and positionals:
        raise UsageError(f"{command} takes no file argument: {positionals[0]!r}")

    min_mag_default = DEFAULT_FETCH_MIN_MAG if command == "fetch" else None
    return Parsed(
        command=command,
        min_mag=_number(raw[_MIN_MAG], _MIN_MAG) if _MIN_MAG in raw else min_mag_default,
        n=_count(raw["--n"]) if "--n" in raw else DEFAULT_TOP_COUNT,
        lat=_ranged(raw, "--lat", -90.0, 90.0),
        lon=_ranged(raw, "--lon", -180.0, 180.0),
        radius=_positive(raw, "--radius"),
        start=_date(raw["--start"], "--start") if "--start" in raw else None,
        end=_date(raw["--end"], "--end") if "--end" in raw else None,
        out=_non_empty(raw["--out"], "--out") if "--out" in raw else None,
        file=positionals[0] if positionals else None,
    )


def _collect_options(command: str, spec: _Spec, rest: list[str]) -> dict[str, str]:
    """Map each option the command takes to its raw value; reject unknown, repeated, or valueless ones."""
    raw: dict[str, str] = {}
    i = 0
    while i < len(rest):
        token = rest[i]
        if not token.startswith("--"):
            i += 1
            continue
        if token not in spec.options:
            raise UsageError(f"{command} does not accept {token}")
        if token in raw:
            raise UsageError(f"{token} given more than once")
        if i + 1 >= len(rest) or rest[i + 1] in spec.options:
            raise UsageError(f"{token} requires a value")
        raw[token] = rest[i + 1]
        i += 2
    return raw


def _collect_positionals(rest: list[str], spec: _Spec) -> list[str]:
    """Return the non-option tokens, skipping each option's value; a stray dash-token is malformed."""
    positionals: list[str] = []
    i = 0
    while i < len(rest):
        token = rest[i]
        if token.startswith("--"):
            i += 2
            continue
        if token.startswith("-") and token != "-":
            raise UsageError(f"unknown option: {token!r}")
        positionals.append(token)
        i += 1
    return positionals


def _number(text: str, option: str) -> float:
    if not _NUMBER.fullmatch(text):
        raise UsageError(f"{option} expects a decimal number, got {text!r}")
    return float(text)


def _count(text: str) -> int:
    if not _COUNT.fullmatch(text) or int(text) == 0:
        raise UsageError(f"--n expects a positive integer, got {text!r}")
    return int(text)


def _ranged(raw: dict[str, str], option: str, low: float, high: float) -> float | None:
    if option not in raw:
        return None
    value = _number(raw[option], option)
    if not low <= value <= high:
        raise UsageError(f"{option} must be within {low:g} to {high:g}, got {raw[option]!r}")
    return value


def _positive(raw: dict[str, str], option: str) -> float | None:
    if option not in raw:
        return None
    value = _number(raw[option], option)
    if value <= 0:
        raise UsageError(f"{option} must be greater than zero, got {raw[option]!r}")
    return value


def _date(text: str, option: str) -> str:
    if not _DATE.fullmatch(text):
        raise UsageError(f"{option} expects YYYY-MM-DD, got {text!r}")
    try:
        datetime.date.fromisoformat(text)
    except ValueError as exc:
        raise UsageError(f"{option} is not a real calendar date: {text!r}") from exc
    return text


def _non_empty(text: str, option: str) -> str:
    if not text:
        raise UsageError(f"{option} must not be empty")
    return text
