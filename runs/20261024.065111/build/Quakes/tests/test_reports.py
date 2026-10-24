import json
import tempfile
import unittest
from pathlib import Path

from cli.testing import cli_runner


def feature(event_id, mag, place, millis, coords=(0, 0, 2), tsunami=0):
    return {"type": "Feature", "id": event_id, "properties": {
        "mag": mag, "place": place, "time": millis, "tsunami": tsunami,
    }, "geometry": {"type": "Point", "coordinates": list(coords)}}


class ReportTests(unittest.TestCase):
    def run_report(self, command, events, *options):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "feed.json"
            path.write_text(json.dumps({"type": "FeatureCollection", "features": events}), encoding="utf-8")
            return cli_runner(command, *options, str(path))

    def test_summary_computes_statistics_and_empty(self):
        code, out, err = self.run_report("summary", [
            feature("a", 5, "A", 1735689600000, tsunami=1),
            feature("b", 6, "B", 1735693200999),
            feature("c", None, "C", 1735693200999),
        ])
        self.assertEqual((code, err), (0, ""))
        self.assertEqual(out, "events,first,last,min_mag,max_mag,mean_mag,tsunami\n2,2025-01-01T00:00:00Z,2025-01-01T01:00:00Z,5.0,6.0,5.50,1\n")
        code, out, _ = self.run_report("summary", [feature("a", None, "A", 0)])
        self.assertEqual((code, out), (0, "events,first,last,min_mag,max_mag,mean_mag,tsunami\n0,,,,,,0\n"))

    def test_daily_filter_and_total(self):
        code, out, _ = self.run_report("daily", [feature("a", 5, "A", 1735689600000), feature("b", 6, "B", 1735776000000)], "--min-mag", "5.5")
        self.assertEqual(code, 0)
        self.assertEqual(out, "date,events,max_mag\n2025-01-02,1,6.0\nTOTAL,1,6.0\n")

    def test_top_orders_magnitude_then_time_and_limits(self):
        code, out, _ = self.run_report("top", [feature("later", 6, "Later", 2000), feature("first", 6, "First", 1000), feature("big", 7, "Big", 3000)], "--n", "2")
        self.assertEqual(code, 0)
        self.assertEqual(out, "time,mag,depth_km,place,id\n1970-01-01T00:00:03Z,7.0,2.0,Big,big\n1970-01-01T00:00:01Z,6.0,2.0,First,first\n")

    def test_regions_uses_last_delimiter_and_orders(self):
        code, out, _ = self.run_report("regions", [feature("a", 5, "City, Subregion, X", 0), feature("b", 6, "Other, X", 1), feature("c", 4, None, 2)])
        self.assertEqual(code, 0)
        self.assertEqual(out, "region,events,max_mag\nX,2,6.0\nUnknown,1,4.0\n")

    def test_near_distance_and_sorted_output(self):
        code, out, _ = self.run_report("near", [feature("a", 5, "east", 2000, (1, 0)), feature("b", 5, "origin", 1000, (0, 0)), feature("c", 5, "far", 3000, (2, 0))], "--lat", "0", "--lon", "0", "--radius", "120")
        self.assertEqual(code, 0)
        self.assertEqual(out, "distance_km,time,mag,place,id\n0.0,1970-01-01T00:00:01Z,5.0,origin,b\n111.2,1970-01-01T00:00:02Z,5.0,east,a\n")

    def test_invalid_input_and_usage_errors_have_no_stdout(self):
        code, out, _ = cli_runner("summary", "missing-geojson")
        self.assertEqual((code, out), (1, ""))
        code, out, _ = cli_runner("near", "--lat", "95", "--lon", "0", "--radius", "1", "sources/quakes_2025-01-01_07.geojson")
        self.assertEqual((code, out), (2, ""))
        code, out, _ = cli_runner("top", "--n", "0", "sources/quakes_2025-01-01_07.geojson")
        self.assertEqual((code, out), (2, ""))


if __name__ == "__main__":
    unittest.main()
