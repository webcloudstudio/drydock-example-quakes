import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import quakes
from cli.testing import cli_runner


class Response:
    def __init__(self, body, status=200):
        self.body, self.status = body, status

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return None

    def read(self):
        return self.body


class FetchTests(unittest.TestCase):
    def test_success_saves_exact_bytes_and_reports_count(self):
        payload = b'{"type":"FeatureCollection","features":[{"id":"a"},{"id":"b"}]}'
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "feed.json"
            with patch.object(quakes, "urlopen", return_value=Response(payload)):
                code, stdout, stderr = cli_runner("fetch", "--start", "2025-01-01", "--end", "2025-01-02", "--out", str(output))
            self.assertEqual(code, 0)
            self.assertEqual(output.read_bytes(), payload)
            self.assertEqual(stdout, "fetched,2\n")
            self.assertEqual(stderr, "")

    def test_request_contains_contract_parameters_and_default_magnitude(self):
        payload = b'{"type":"FeatureCollection","features":[]}'
        with tempfile.TemporaryDirectory() as directory:
            with patch.object(quakes, "urlopen", return_value=Response(payload)) as opened:
                code, _, _ = cli_runner("fetch", "--start", "2025-01-01", "--end", "2025-01-02", "--out", str(Path(directory) / "x"))
            self.assertEqual(code, 0)
            request = opened.call_args.args[0]
            self.assertEqual(request.full_url, "https://earthquake.usgs.gov/fdsnws/event/1/query?format=geojson&starttime=2025-01-01&endtime=2025-01-02&minmagnitude=2.5&orderby=time-asc")

    def test_network_failure_does_not_create_output(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "absent.geojson"
            with patch.object(quakes, "urlopen", side_effect=OSError("offline")):
                code, stdout, _ = cli_runner("fetch", "--start", "2025-01-01", "--end", "2025-01-02", "--out", str(output))
            self.assertEqual(code, 1)
            self.assertEqual(stdout, "")
            self.assertFalse(output.exists())

    def test_non_200_and_invalid_geojson_do_not_write(self):
        for response in (Response(b'{"type":"FeatureCollection","features":[]}', 503), Response(b'{"type":"Feature","features":[]}')):
            with self.subTest(response=response.status), tempfile.TemporaryDirectory() as directory:
                output = Path(directory) / "absent.geojson"
                with patch.object(quakes, "urlopen", return_value=response):
                    code, _, _ = cli_runner("fetch", "--start", "2025-01-01", "--end", "2025-01-02", "--out", str(output))
                self.assertEqual(code, 1)
                self.assertFalse(output.exists())

    def test_invalid_magnitude_is_usage_error(self):
        code, stdout, _ = cli_runner("fetch", "--start", "2025-01-01", "--end", "2025-01-02", "--min-mag", "2x", "--out", "unused")
        self.assertEqual(code, 2)
        self.assertEqual(stdout, "")


if __name__ == "__main__":
    unittest.main()
