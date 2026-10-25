"""Summary-report story: one CSV row with count, time span, magnitude range, mean, and tsunami count."""

import csv
import datetime
import io

from cli import reports
from cli.feed import Event

BASE = 1735689600000


def _feature(ident, mag, k, tsunami=0):
    return {
        "type": "Feature",
        "id": ident,
        "properties": {"mag": mag, "place": "10 km N of Town, Land", "time": BASE + k * 3600000, "tsunami": tsunami},
        "geometry": {"type": "Point", "coordinates": [10.0, 20.0, 12.0]},
    }


def _rows(out):
    return list(csv.reader(io.StringIO(out)))


def _event(mag, time_ms=BASE, tsunami=0):
    return Event(id="x", mag=mag, place="P", time_ms=time_ms, tsunami=tsunami, lon=0.0, lat=0.0, depth_km=1.0)


# ── Declared acceptance assertions ──────────────────────────────────────────────────────


def test_summary_values(write_feed, cli_runner):
    specs = [("a", 5.0, 5, 0), ("b", 6.5, 1, 1), ("c", 5.5, 9, 1), ("d", 5.0, 3, 0)]
    path = write_feed([_feature(*s) for s in specs])
    code, out, _ = cli_runner("summary", path)
    assert code == 0
    rows = _rows(out)
    assert len(rows) == 2
    header, row = rows
    assert header == ["events", "first", "last", "min_mag", "max_mag", "mean_mag", "tsunami"]
    mags = [s[1] for s in specs]
    times = [BASE + s[2] * 3600000 for s in specs]
    record = dict(zip(header, row))
    assert int(record["events"]) == len(specs)

    def epoch(text):
        return int(datetime.datetime.fromisoformat(text).timestamp() * 1000)

    assert record["first"].endswith("Z") and record["last"].endswith("Z")
    assert epoch(record["first"]) == min(times)
    assert epoch(record["last"]) == max(times)
    assert float(record["min_mag"]) == min(mags)
    assert float(record["max_mag"]) == max(mags)
    assert abs(float(record["mean_mag"]) - sum(mags) / len(mags)) <= 0.005
    assert int(record["tsunami"]) == sum(s[3] for s in specs)


def test_summary_mean_half_up(write_feed, cli_runner):
    mags = [5.0] * 7 + [6.0]
    path = write_feed([_feature(f"e{i}", m, i) for i, m in enumerate(mags)])
    code, out, _ = cli_runner("summary", path)
    assert code == 0
    header, row = _rows(out)
    # 41.0 / 8 is exactly 5.125, so half-up yields 5.13 (banker's rounding would give 5.12).
    assert dict(zip(header, row))["mean_mag"] == "5.13"


def test_summary_min_mag_filter(write_feed, cli_runner):
    mags = [5.0, 5.4, 5.5, 6.0, 7.1]
    threshold = 5.5
    path = write_feed([_feature(f"e{i}", m, i) for i, m in enumerate(mags)])
    code, out, _ = cli_runner("summary", "--min-mag", str(threshold), path)
    assert code == 0
    header, row = _rows(out)
    record = dict(zip(header, row))
    kept = [m for m in mags if m >= threshold]
    assert int(record["events"]) == len(kept)
    assert float(record["min_mag"]) == min(kept)
    assert float(record["max_mag"]) == max(kept)


def test_summary_null_mag_excluded(write_feed, cli_runner):
    mags = [5.0, None, 6.0, None]
    path = write_feed([_feature(f"e{i}", m, i) for i, m in enumerate(mags)])
    code, out, _ = cli_runner("summary", path)
    assert code == 0
    header, row = _rows(out)
    assert int(dict(zip(header, row))["events"]) == len([m for m in mags if m is not None])


def test_summary_empty(write_feed, cli_runner):
    path = write_feed([_feature("e0", 5.0, 0)])
    code, out, _ = cli_runner("summary", "--min-mag", "9", path)
    assert code == 0
    rows = _rows(out)
    assert len(rows) == 2
    assert rows[1] == ["0", "", "", "", "", "", "0"]


def test_summary_failure_codes(tmp_path, cli_runner):
    garbage = tmp_path / "garbage.json"
    garbage.write_text("this is not json\n", encoding="utf-8")
    missing = tmp_path / "no-such-file.geojson"

    code, out, _ = cli_runner("summary", str(garbage))
    assert code == 1 and out == ""
    code, out, _ = cli_runner("summary", str(missing))
    assert code == 1 and out == ""
    code, out, _ = cli_runner("summary", "--n", "3", str(garbage))
    assert code == 2 and out == ""
    code, out, _ = cli_runner("summary")
    assert code == 2 and out == ""
    code, out, _ = cli_runner("summary", "--min-mag", "big", str(garbage))
    assert code == 2 and out == ""


# ── Finer coverage ──────────────────────────────────────────────────────────────────────


def test_summary_tsunami_counts_only_value_one(write_feed, cli_runner):
    path = write_feed([_feature("a", 5.0, 0, tsunami=1), _feature("b", 5.0, 1, tsunami=2), _feature("c", 5.0, 2, tsunami=0)])
    code, out, _ = cli_runner("summary", path)
    assert code == 0
    header, row = _rows(out)
    assert dict(zip(header, row))["tsunami"] == "1"


def test_summary_single_event_has_equal_extremes(write_feed, cli_runner):
    path = write_feed([_feature("a", 6.25, 4)])
    code, out, _ = cli_runner("summary", path)
    assert code == 0
    header, row = _rows(out)
    record = dict(zip(header, row))
    assert record["events"] == "1"
    assert record["min_mag"] == record["max_mag"] == "6.3"
    assert record["first"] == record["last"]


def test_summary_function_empty_input_is_zero_row():
    assert reports.compute_summary([]) == [
        ["events", "first", "last", "min_mag", "max_mag", "mean_mag", "tsunami"],
        ["0", "", "", "", "", "", "0"],
    ]


def test_summary_function_mean_has_two_decimals():
    rows = reports.compute_summary([_event(5.0), _event(5.1)])
    assert dict(zip(rows[0], rows[1]))["mean_mag"] == "5.05"
