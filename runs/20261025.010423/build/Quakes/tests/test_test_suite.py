"""Test-suite story: bin/test.sh runs the pytest suite and exits with pytest's status.

The suite never invokes `bin/test.sh` on itself: that would recurse without end. The runner is
exercised on temporary application roots that hold only the tests each case needs.
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "bin" / "test.sh"
THIS_FILE = Path(__file__).name


def _env_with_pytest() -> dict[str, str]:
    return {**os.environ, "PATH": os.path.dirname(sys.executable) + os.pathsep + os.environ.get("PATH", "")}


def _make_root(root: Path, test_name: str, test_body: str) -> Path:
    (root / "bin").mkdir(parents=True)
    (root / "tests").mkdir()
    shutil.copy(SCRIPT, root / "bin" / "test.sh")
    (root / "tests" / test_name).write_text(test_body, encoding="utf-8")
    return root


def _run_runner(root: Path, cwd: Path) -> int:
    result = subprocess.run(
        ["sh", str(root / "bin" / "test.sh")], capture_output=True, text=True, env=_env_with_pytest(), cwd=cwd
    )
    return result.returncode


# ── Declared acceptance assertions ──────────────────────────────────────────────────────


def test_testsuite_script_exists():
    assert SCRIPT.is_file()
    first_line = SCRIPT.read_text(encoding="utf-8").splitlines()[0]
    assert first_line.startswith("#!")
    assert first_line.rstrip().endswith("sh")
    assert "bash" not in first_line


def test_testsuite_propagates_failure(tmp_path):
    root = _make_root(tmp_path / "app", "test_always_fails.py", "def test_always_fails():\n    assert False\n")
    assert _run_runner(root, root) != 0


def test_testsuite_passes_when_tests_pass(tmp_path):
    root = _make_root(tmp_path / "app", "test_always_passes.py", "def test_always_passes():\n    assert True\n")
    assert _run_runner(root, root) == 0


# ── Finer coverage: working directory, environment, and the script's own contract ───────


def test_testsuite_runs_from_another_directory_with_the_same_status(tmp_path):
    app = tmp_path / "app"
    app.mkdir()
    for name in ("cli", "bin", "tests"):
        shutil.copytree(ROOT / name, app / name, ignore=shutil.ignore_patterns("__pycache__", ".pytest_cache"))
    (app / "tests" / THIS_FILE).unlink()
    for name in ("conftest.py", "pyproject.toml", "uv.lock", "quakes"):
        shutil.copy(ROOT / name, app / name)

    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()
    assert _run_runner(app, elsewhere) == 0


def test_testsuite_fails_when_a_test_errors_at_import(tmp_path):
    root = _make_root(tmp_path / "app", "test_broken_import.py", "import no_such_module_quakes\n")
    assert _run_runner(root, root) != 0


def test_testsuite_script_parses_under_sh():
    result = subprocess.run(["sh", "-n", str(SCRIPT)], capture_output=True, text=True)
    assert result.returncode == 0
