"""Pure formatting for every report: UTC times, rounded numbers, and CSV text.

Rounding goes through `Decimal(repr(x))` with `ROUND_HALF_UP` (decision Q-002), never through the
built-in `round()`, so exact halves such as 0.25 and 5.125 round up on every platform.
"""

import csv
import io
import math
import sys
from datetime import datetime, timedelta, timezone
from decimal import ROUND_HALF_UP, Decimal
from typing import Any, TextIO

_EPOCH = datetime(1970, 1, 1, tzinfo=timezone.utc)
_ISO_UTC = "%Y-%m-%dT%H:%M:%SZ"
_ONE_PLACE = Decimal("0.1")
_TWO_PLACES = Decimal("0.01")


def format_time(ms: int | float) -> str:
    """Return epoch milliseconds as UTC `YYYY-MM-DDTHH:MM:SSZ`, truncated to whole seconds."""
    seconds = math.floor(ms) // 1000
    return (_EPOCH + timedelta(seconds=seconds)).strftime(_ISO_UTC)


def format_mag(x: Any) -> str:
    """Return a magnitude with exactly one decimal place, rounded half up."""
    return _quantize(x, _ONE_PLACE)


def format_mean(x: Any) -> str:
    """Return a mean magnitude with two decimal places, rounded half up."""
    return _quantize(x, _TWO_PLACES)


def format_decimal(x: Any) -> str:
    """Return a depth or distance with one decimal place, rounded half up."""
    return _quantize(x, _ONE_PLACE)


def render_csv(rows: list[list[str]]) -> str:
    """Render rows as CSV text with `\\n` line endings; fields with commas or quotes are quoted."""
    buffer = io.StringIO()
    csv.writer(buffer, lineterminator="\n").writerows(rows)
    return buffer.getvalue()


def write_csv(rows: list[list[str]], stream: TextIO | None = None) -> None:
    """Write `render_csv(rows)` to `stream`, or to standard output as UTF-8 when `stream` is None."""
    text = render_csv(rows)
    if stream is not None:
        stream.write(text)
    else:
        write_stdout(text)


def write_stdout(text: str) -> None:
    """Write `text` to standard output as UTF-8, through the binary buffer when the stream has one."""
    out = sys.stdout
    binary = getattr(out, "buffer", None)
    if binary is not None:
        out.flush()
        binary.write(text.encode("utf-8"))
        binary.flush()
    else:
        out.write(text)


def _quantize(x: Any, places: Decimal) -> str:
    return str(Decimal(repr(x)).quantize(places, rounding=ROUND_HALF_UP))
