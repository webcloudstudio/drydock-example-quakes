"""Options story: parse_args turns argv into a Parsed record or raises UsageError (exit 2)."""

import pytest

from cli.errors import UsageError
from cli.options import parse_args
from cli.testing import cli_runner

PATH = "quakes-file.geojson"
FETCH = ["fetch", "--start", "2025-01-01", "--end", "2025-01-08", "--out", "feed.geojson"]


# ── Declared acceptance assertions ──────────────────────────────────────────────────────


def test_options_valid_summary():
    parsed = parse_args(["summary", "--min-mag", "5.5", PATH])
    assert parsed.command == "summary"
    assert parsed.min_mag == 5.5
    assert parsed.file == PATH


def test_options_defaults():
    top = parse_args(["top", PATH])
    assert top.n == 10
    assert top.min_mag is None
    fetch = parse_args(["fetch", "--start", "2025-01-01", "--end", "2025-01-08", "--out", PATH])
    assert fetch.min_mag == 2.5


def test_options_any_order():
    a = parse_args(["top", "--n", "3", "--min-mag", "5.1", PATH])
    b = parse_args(["top", "--min-mag", "5.1", "--n", "3", PATH])
    assert a.n == b.n == 3
    assert a.min_mag == b.min_mag == 5.1
    assert a.file == b.file == PATH


def test_options_near_valid():
    parsed = parse_args(["near", "--lat", "90", "--lon", "-180", "--radius", "0.5", PATH])
    assert parsed.lat == 90.0
    assert parsed.lon == -180.0
    assert parsed.radius == 0.5
    negative = parse_args(["summary", "--min-mag", "-1", PATH])
    assert negative.min_mag == -1.0


def test_options_fetch_valid():
    parsed = parse_args(
        ["fetch", "--start", "2025-01-01", "--end", "2025-01-08", "--min-mag", "5", "--out", "feed.geojson"]
    )
    assert parsed.command == "fetch"
    assert parsed.start == "2025-01-01"
    assert parsed.end == "2025-01-08"
    assert parsed.out == "feed.geojson"
    assert parsed.min_mag == 5.0


def test_options_usage_errors():
    f = PATH
    bad = [
        [],
        ["frobnicate", f],
        ["near", "--lat", "27.72", "--lon", "85.32", f],
        ["near", "--lat", "95", "--lon", "0", "--radius", "10", f],
        ["near", "--lat", "0", "--lon", "181", "--radius", "10", f],
        ["near", "--lat", "0", "--lon", "0", "--radius", "0", f],
        ["top", "--n", "0", f],
        ["top", "--n", "2.5", f],
        ["summary", "--min-mag", "big", f],
        ["summary", "--min-mag", "5.", f],
        ["summary", "--min-mag", ".5", f],
        ["summary", "--n", "3", f],
        ["summary"],
        ["summary", f, f],
        ["summary", "--min-mag", f],
        ["summary", "--min-mag", "5", "--min-mag", "6", f],
        ["fetch", "--start", "2025-01-01", "--end", "2025-01-08"],
        ["fetch", "--start", "2025-01-01", "--out", f],
        ["fetch", "--start", "2025-01-01", "--end", "2025-01-08", "--out", f, f],
        ["fetch", "--start", "yesterday", "--end", "2025-01-08", "--out", f],
    ]
    for argv in bad:
        with pytest.raises(UsageError):
            parse_args(list(argv))


def test_options_exit_two():
    code_unknown, out_unknown, _ = cli_runner("frobnicate", PATH)
    code_none, out_none, _ = cli_runner()
    assert code_unknown == 2
    assert code_none == 2
    assert out_unknown == ""
    assert out_none == ""


# ── Finer coverage: every command, option, boundary, and error path ─────────────────────


@pytest.mark.parametrize("command", ["summary", "top", "daily", "regions"])
def test_report_commands_parse_their_file_argument(command):
    parsed = parse_args([command, PATH])
    assert parsed.command == command
    assert parsed.file == PATH
    assert parsed.min_mag is None


def test_parsing_does_not_require_the_file_to_exist(tmp_path):
    missing = tmp_path / "no-such-file.geojson"
    assert parse_args(["summary", str(missing)]).file == str(missing)


def test_near_parses_all_required_options_with_min_mag():
    parsed = parse_args(["near", "--lat", "27.72", "--lon", "85.32", "--radius", "800", "--min-mag", "5.3", PATH])
    assert (parsed.lat, parsed.lon, parsed.radius, parsed.min_mag) == (27.72, 85.32, 800.0, 5.3)
    assert parsed.file == PATH


@pytest.mark.parametrize("lat", ["-90", "90", "0", "-45.5"])
def test_near_latitude_accepts_the_full_range(lat):
    assert parse_args(["near", "--lat", lat, "--lon", "0", "--radius", "1", PATH]).lat == float(lat)


@pytest.mark.parametrize("lat", ["-90.1", "90.5", "100"])
def test_near_latitude_rejects_values_outside_the_range(lat):
    with pytest.raises(UsageError):
        parse_args(["near", "--lat", lat, "--lon", "0", "--radius", "1", PATH])


@pytest.mark.parametrize("lon", ["-180", "180", "0"])
def test_near_longitude_accepts_the_full_range(lon):
    assert parse_args(["near", "--lat", "0", "--lon", lon, "--radius", "1", PATH]).lon == float(lon)


@pytest.mark.parametrize("lon", ["-180.01", "180.5"])
def test_near_longitude_rejects_values_outside_the_range(lon):
    with pytest.raises(UsageError):
        parse_args(["near", "--lat", "0", "--lon", lon, "--radius", "1", PATH])


def test_near_radius_accepts_a_small_positive_value():
    assert parse_args(["near", "--lat", "0", "--lon", "0", "--radius", "0.001", PATH]).radius == 0.001


@pytest.mark.parametrize("radius", ["-5", "0", "0.0"])
def test_near_radius_rejects_zero_and_negative(radius):
    with pytest.raises(UsageError):
        parse_args(["near", "--lat", "0", "--lon", "0", "--radius", radius, PATH])


@pytest.mark.parametrize("missing", ["--lat", "--lon", "--radius"])
def test_near_requires_each_coordinate_and_radius(missing):
    values = {"--lat": "0", "--lon": "0", "--radius": "1"}
    argv = ["near"]
    for option, value in values.items():
        if option != missing:
            argv += [option, value]
    with pytest.raises(UsageError):
        parse_args([*argv, PATH])


@pytest.mark.parametrize("value", ["1e5", "+5", "--5", "5 ", "", "NaN", "inf"])
def test_numeric_options_reject_malformed_numbers(value):
    with pytest.raises(UsageError):
        parse_args(["summary", "--min-mag", value, PATH])


@pytest.mark.parametrize("value", ["-0.5", "-12", "0", "10.25"])
def test_numeric_options_accept_signed_and_decimal_values(value):
    assert parse_args(["summary", "--min-mag", value, PATH]).min_mag == float(value)


def test_top_count_defaults_to_ten_and_accepts_one():
    assert parse_args(["top", PATH]).n == 10
    assert parse_args(["top", "--n", "1", PATH]).n == 1


@pytest.mark.parametrize("value", ["-3", "0", "1.0", "ten", ""])
def test_top_count_rejects_non_positive_and_non_integer(value):
    with pytest.raises(UsageError):
        parse_args(["top", "--n", value, PATH])


def test_fetch_min_mag_is_two_point_five_by_default_and_overridable():
    assert parse_args(FETCH).min_mag == 2.5
    assert parse_args([*FETCH, "--min-mag", "4"]).min_mag == 4.0


def test_fetch_takes_no_positional_file():
    with pytest.raises(UsageError):
        parse_args([*FETCH, PATH])


@pytest.mark.parametrize("date", ["2025-1-01", "2025/01/01", "25-01-01", "2025-02-30", "2025-13-01"])
def test_fetch_dates_must_be_real_calendar_dates_in_iso_form(date):
    with pytest.raises(UsageError):
        parse_args(["fetch", "--start", date, "--end", "2025-01-08", "--out", "feed.geojson"])


def test_fetch_rejects_an_empty_output_path():
    with pytest.raises(UsageError):
        parse_args(["fetch", "--start", "2025-01-01", "--end", "2025-01-08", "--out", ""])


@pytest.mark.parametrize("option", ["--start", "--end", "--out"])
def test_fetch_option_without_a_value_is_a_usage_error(option):
    truncated = FETCH[: FETCH.index(option) + 1]
    with pytest.raises(UsageError):
        parse_args(truncated)


def test_trailing_min_mag_without_a_value_is_a_usage_error():
    with pytest.raises(UsageError):
        parse_args(["summary", PATH, "--min-mag"])


def test_option_value_may_not_be_another_option_of_the_same_command():
    with pytest.raises(UsageError):
        parse_args(["summary", "--min-mag", "--min-mag", PATH])


def test_an_option_a_command_does_not_list_is_a_usage_error():
    with pytest.raises(UsageError):
        parse_args(["daily", "--n", "3", PATH])


def test_unknown_option_is_a_usage_error():
    with pytest.raises(UsageError):
        parse_args(["summary", "--verbose", PATH])


def test_missing_file_is_a_usage_error():
    with pytest.raises(UsageError):
        parse_args(["regions", "--min-mag", "5"])


def test_usage_errors_carry_exit_code_two():
    assert UsageError.exit_code == 2
    with pytest.raises(UsageError) as info:
        parse_args([])
    assert info.value.exit_code == 2


def test_cli_runner_writes_nothing_to_stdout_for_a_parse_failure():
    code, out, err = cli_runner("summary", "--n", "3", PATH)
    assert code == 2
    assert out == ""
    assert len(err.splitlines()) == 1
