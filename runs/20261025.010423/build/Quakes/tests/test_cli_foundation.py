"""CLI foundation: main entry point, exit codes, command registry, cli_runner, and the quakes launcher."""

import os
import subprocess
import sys
from pathlib import Path

import cli
from cli import main
from cli.errors import OperationalError, UsageError
from cli.testing import cli_runner

ROOT = Path(__file__).resolve().parent.parent


def test_main_returns_an_integer_for_an_empty_argv():
    assert isinstance(main([]), int)


def test_main_returns_usage_exit_code_when_no_command_is_given():
    assert main([]) == 2


def test_main_returns_usage_exit_code_for_an_unknown_command():
    assert main(["no-such-command-xyz"]) == 2


def test_main_reads_sys_argv_when_argv_is_none(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["quakes", "no-such-command-xyz"])
    assert main() == 2


def test_main_returns_zero_for_a_registered_command(monkeypatch):
    monkeypatch.setitem(cli.COMMANDS, "daily", lambda parsed: "")
    assert main(["daily", "quakes-file.geojson"]) == 0


def test_command_registry_is_a_dict():
    assert isinstance(cli.COMMANDS, dict)


def test_usage_error_maps_to_exit_code_two():
    assert UsageError.exit_code == 2
    assert issubclass(UsageError, Exception)


def test_operational_error_maps_to_exit_code_one():
    assert OperationalError.exit_code == 1
    assert issubclass(OperationalError, Exception)


def test_cli_runner_returns_code_stdout_and_stderr_as_text():
    code, out, err = cli_runner("no-such-command-xyz")
    assert isinstance(code, int)
    assert isinstance(out, str)
    assert isinstance(err, str)


def test_cli_runner_agrees_with_main_on_exit_code():
    args = ["no-such-command-xyz"]
    code, _, _ = cli_runner(*args)
    assert code == main(list(args))


def test_cli_runner_leaves_stdout_empty_on_usage_error():
    _, out, _ = cli_runner("no-such-command-xyz")
    assert out == ""


def test_cli_runner_writes_a_single_diagnostic_line_on_usage_error():
    _, _, err = cli_runner("no-such-command-xyz")
    assert len(err.splitlines()) == 1


def test_cli_runner_captures_stdout_from_a_registered_command(monkeypatch):
    monkeypatch.setitem(cli.COMMANDS, "daily", lambda parsed: "")
    code, out, err = cli_runner("daily", "quakes-file.geojson")
    assert code == 0
    assert out == ""
    assert err == ""


def test_quakes_launcher_is_an_executable_file_at_the_root():
    launcher = ROOT / "quakes"
    assert launcher.is_file()
    assert os.access(launcher, os.X_OK)


def test_quakes_launcher_exits_with_the_code_main_returns():
    result = subprocess.run([str(ROOT / "quakes")], capture_output=True, text=True, cwd=ROOT)
    assert result.returncode == main([])
