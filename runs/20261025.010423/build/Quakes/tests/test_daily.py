"""Daily-report story: events per UTC date with the maximum magnitude, then a TOTAL row."""

import csv
import io
from datetime import datetime, timezone

from cli import reports
from cli.feed import Event

HEADER = ["date", "events", "max_mag"]


def _ms(day, hour, minute=0, second=0, milli=0):
    moment = datetime(2025, 1, day, hour, minute, second, tzinfo=timezone.utc)
    return int(moment.timestamp()) * 1000 + milli


def _feature(ident, mag, time_ms, place="P"):
    return {
        "type": "Feature",
        "properties": {"mag": mag, "place": place, "time": time_ms, "tsunami": 0},
        "geometry": {"type": "Point", "coordinates": [0.0, 0.0, 1.0]},
        "id": ident,
    }


def _rows(out):
    return list(csv.reader(io.StringIO(out)))


def _event(mag, time_ms):
    return Event(id="x", mag=mag, place="P", time_ms=time_ms, tsunami=0, lon=0.0, lat=0.0, depth_km=1.0)


# ── Declared acceptance assertions ──────────────────────────────────────────────────────


def test_daily_groups_by_utc_date(write_feed, cli_runner):
    specs = [
        (5.0, _ms(3, 1)),
        (6.1, _ms(1, 2)),
        (5.4, _ms(1, 23, 59, 59, 999)),
        (5.5, _ms(3, 12)),
        (5.2, _ms(7, 0)),
    ]
    expected = {}
    for mag, t in specs:
        label = datetime.fromtimestamp(t // 1000, timezone.utc).strftime("%Y-%m-%d")
        entry = expected.setdefault(label, [0, mag])
        entry[0] += 1
        entry[1] = max(entry[1], mag)
    path = write_feed([_feature("e" + str(i), m, t) for i, (m, t) in enumerate(specs)])
    code, out, _ = cli_runner("daily", path)
    assert code == 0
    rows = _rows(out)
    assert rows[0] == HEADER
    body = rows[1:-1]
    assert [r[0] for r in body] == sorted(expected)
    for r in body:
        assert int(r[1]) == expected[r[0]][0]
        assert float(r[2]) == expected[r[0]][1]
    total = rows[-1]
    assert total[0] == "TOTAL"
    assert int(total[1]) == len(specs)
    assert float(total[2]) == max(m for m, _ in specs)


def test_daily_empty_report(write_feed, cli_runner):
    path = write_feed([_feature("only", 5.0, 1735706358208, place="X, Y")])
    code, out, _ = cli_runner("daily", "--min-mag", "9", path)
    code2, out2, _ = cli_runner("daily", write_feed([], name="empty.geojson"))
    assert code == 0 and code2 == 0
    for text in (out, out2):
        assert _rows(text) == [HEADER, ["TOTAL", "0", ""]]


def test_daily_min_mag_and_null_mag(write_feed, cli_runner):
    threshold = 5.4
    specs = [(5.0, _ms(1, 1)), (5.4, _ms(1, 2)), (6.0, _ms(2, 3)), (None, _ms(2, 4)), (5.3, _ms(4, 5))]
    kept = [(m, t) for m, t in specs if m is not None and m >= threshold]
    path = write_feed([_feature("e" + str(i), m, t) for i, (m, t) in enumerate(specs)])
    code, out, _ = cli_runner("daily", "--min-mag", str(threshold), path)
    code_all, out_all, _ = cli_runner("daily", path)
    assert code == 0 and code_all == 0
    rows = _rows(out)
    assert int(rows[-1][1]) == len(kept)
    assert float(rows[-1][2]) == max(m for m, _ in kept)
    assert len(rows) - 2 == len({datetime.fromtimestamp(t // 1000, timezone.utc).date() for _, t in kept})
    rows_all = _rows(out_all)
    assert int(rows_all[-1][1]) == len([1 for m, _ in specs if m is not None])


def test_daily_failure_contract(tmp_path, cli_runner):
    code, out, _ = cli_runner("daily", str(tmp_path / "absent.geojson"))
    assert code == 1
    assert out == ""
    present = tmp_path / "x.geojson"
    present.write_text("{}", encoding="utf-8")
    code2, out2, _ = cli_runner("daily", "--n", "3", str(present))
    assert code2 == 2
    assert out2 == ""


# ── Finer coverage ──────────────────────────────────────────────────────────────────────


def test_daily_date_boundary_uses_utc_not_local():
    # 23:59:59.999 UTC on the 1st stays on the 1st, and 00:00:00.000 UTC on the 2nd starts the 2nd.
    rows, _ = reports.compute_daily([_event(5.0, _ms(1, 23, 59, 59, 999)), _event(5.0, _ms(2, 0))])
    assert [r[0] for r in rows] == ["2025-01-01", "2025-01-02"]


def test_daily_total_is_max_over_all_dates():
    rows, total = reports.compute_daily([_event(5.0, _ms(1, 1)), _event(7.2, _ms(3, 1)), _event(6.0, _ms(3, 2))])
    assert total == ["TOTAL", "3", "7.2"]
    assert rows == [["2025-01-01", "1", "5.0"], ["2025-01-03", "2", "7.2"]]


def test_daily_compute_empty_gives_zero_total():
    assert reports.compute_daily([]) == ([], ["TOTAL", "0", ""])
