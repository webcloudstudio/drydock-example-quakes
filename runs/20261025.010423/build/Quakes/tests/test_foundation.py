"""Foundation contract: project tree, dependency manifest, and pytest runner."""

import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _pyproject() -> dict:
    return tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))


def test_manifest_and_lockfile_exist_at_root():
    assert (ROOT / "pyproject.toml").is_file()
    assert (ROOT / "uv.lock").is_file()


def test_tests_directory_exists_at_root():
    assert (ROOT / "tests").is_dir()


def test_conftest_exposes_cli_runner_fixture():
    import conftest

    assert hasattr(conftest.cli_runner, "_fixture_function_marker")


def test_runtime_dependencies_are_empty():
    assert _pyproject()["project"].get("dependencies", []) == []


def test_requires_python_311_or_newer():
    assert _pyproject()["project"]["requires-python"] == ">=3.11"
    assert sys.version_info >= (3, 11)


def test_pytest_is_a_dev_dependency_only():
    data = _pyproject()
    dev = data["dependency-groups"]["dev"]
    assert any(spec.startswith("pytest") for spec in dev)


def test_pytest_is_importable():
    import importlib.util

    assert importlib.util.find_spec("pytest") is not None


def test_test_runner_script_is_executable():
    script = ROOT / "bin" / "test.sh"
    assert script.is_file()
    assert script.stat().st_mode & 0o111
