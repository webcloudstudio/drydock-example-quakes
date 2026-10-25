"""Shared pytest configuration for the quakes test suite."""

import json

import pytest


@pytest.fixture
def cli_runner():
    """Run the `quakes` command in-process and return (exit_code, stdout, stderr).

    The implementation lives in `cli.testing`; it is imported lazily so that
    collecting the foundation tests does not depend on the CLI package.
    """
    from cli import testing

    return testing.cli_runner


@pytest.fixture
def write_feed(tmp_path):
    """Write a GeoJSON FeatureCollection holding `features` to a temporary file and return its path."""

    def _write(features, name="feed.geojson"):
        path = tmp_path / name
        path.write_text(json.dumps({"type": "FeatureCollection", "features": features}), encoding="utf-8")
        return str(path)

    return _write
