"""Formatting story: UTC times, half-up rounded numbers, and CSV output."""

import contextlib
import csv
import io
import sys
from datetime import datetime, timezone

import pytest

from cli.formatting import format_decimal, format_mag, format_mean, format_time, render_csv, write_csv


# ── Declared acceptance assertions ──────────────────────────────────────────────────────


def test_fmt_time():
    seconds = 1735706358
    ms = seconds * 1000 + 999
    text = format_time(ms)
    parsed = datetime.strptime(text, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    assert int(parsed.timestamp()) == seconds
    assert len(text) == 20
    assert text[:10] == parsed.strftime("%Y-%m-%d")
    assert format_time(seconds * 1000) == text


def test_fmt_magnitude():
    assert format_mag(5) == "5.0"
    assert format_mag(7.1) == "7.1"
    assert format_mag(5.0) == "5.0"


def test_fmt_mean_half_up():
    assert format_mean(5.3) == "5.30"
    assert format_mean(5.125) == "5.13"
    assert format_mean(5.135) == "5.14"
    assert format_mean(5) == "5.00"


def test_fmt_decimal_half_up():
    assert format_decimal(0.25) == "0.3"
    assert format_decimal(10) == "10.0"
    assert format_decimal(216.25) == "216.3"
    assert format_decimal(46) == "46.0"


def test_fmt_csv_roundtrip():
    place = "Āwash, Ethiopia"
    rows = [["time", "place"], ["2025-01-01T00:00:00Z", place], ["a", "plain"]]
    text = render_csv(rows)
    parsed = list(csv.reader(io.StringIO(text, newline="")))
    assert parsed == rows
    assert text.count("\n") == len(rows)
    assert text.endswith("\n")


def test_fmt_write_csv():
    rows = [["h1", "h2"], ["x", "y, z"]]
    stream = io.StringIO()
    write_csv(rows, stream)
    assert stream.getvalue() == render_csv(rows)

    captured = io.StringIO()
    with contextlib.redirect_stdout(captured):
        write_csv(rows)
    assert captured.getvalue() == render_csv(rows)


# ── Finer coverage: boundaries, rounding, and stdout encoding ───────────────────────────


def test_format_time_is_the_epoch_at_zero():
    assert format_time(0) == "1970-01-01T00:00:00Z"


@pytest.mark.parametrize("ms", [1000, 1999, 1000.5, 1999.9])
def test_format_time_truncates_fractions_of_a_second(ms):
    assert format_time(ms) == "1970-01-01T00:00:01Z"


def test_format_time_reads_the_utc_date_at_the_day_boundary():
    assert format_time(1735689599999) == "2024-12-31T23:59:59Z"
    assert format_time(1735689600000) == "2025-01-01T00:00:00Z"


def test_format_time_output_is_always_twenty_characters():
    for ms in (0, 1735706358999, 4102444799000):
        assert len(format_time(ms)) == 20


@pytest.mark.parametrize(
    ("value", "text"),
    [(0, "0.0"), (0.05, "0.1"), (0.04, "0.0"), (9.95, "10.0"), (7.1, "7.1"), (2, "2.0")],
)
def test_format_mag_rounds_half_up_to_one_place(value, text):
    assert format_mag(value) == text


@pytest.mark.parametrize(
    ("value", "text"),
    [(5.125, "5.13"), (5.124, "5.12"), (0, "0.00"), (-0.125, "-0.13"), (4.999, "5.00")],
)
def test_format_mean_rounds_half_up_to_two_places(value, text):
    assert format_mean(value) == text


@pytest.mark.parametrize(("value", "text"), [(0.05, "0.1"), (0.149, "0.1"), (99.95, "100.0"), (0, "0.0")])
def test_format_decimal_rounds_half_up_to_one_place(value, text):
    assert format_decimal(value) == text


def test_format_decimal_is_not_banker_rounding():
    # round() would send 0.25 and 0.35 to even digits; half-up sends them up.
    assert format_decimal(0.35) == "0.4"
    assert format_decimal(0.25) == "0.3"


def test_render_csv_quotes_a_field_containing_a_comma():
    assert render_csv([["a", "b, c"]]) == 'a,"b, c"\n'


def test_render_csv_quotes_a_field_containing_a_double_quote():
    rows = [["say \"hi\"", "x"]]
    parsed = list(csv.reader(io.StringIO(render_csv(rows), newline="")))
    assert parsed == rows


def test_render_csv_of_no_rows_is_empty():
    assert render_csv([]) == ""


def test_render_csv_keeps_a_row_with_one_empty_field():
    rows = [["events", ""]]
    parsed = list(csv.reader(io.StringIO(render_csv(rows), newline="")))
    assert parsed == rows


def test_write_csv_to_stdout_writes_utf8_bytes_through_the_buffer(monkeypatch):
    raw = io.BytesIO()
    wrapper = io.TextIOWrapper(raw, encoding="utf-8", write_through=True)
    monkeypatch.setattr(sys, "stdout", wrapper)
    rows = [["place"], ["Āwash, Ethiopia"]]
    write_csv(rows)
    wrapper.flush()
    assert raw.getvalue().decode("utf-8") == render_csv(rows)
