"""Exit-code story: UsageError exits 2, OperationalError exits 1, success exits 0, all via `main`."""

import subprocess
from pathlib import Path

import cli
from cli import main
from cli.errors import OperationalError, UsageError
from cli.testing import cli_runner

ROOT = Path(__file__).resolve().parent.parent
PATH = "quakes-file.geojson"


def _failing(parsed):
    raise OperationalError("cannot read the file")


# ── Declared acceptance assertions ──────────────────────────────────────────────────────


def test_exit_usage_code():
    code, out, err = cli_runner("frobnicate", PATH)
    assert code == 2
    assert out == ""
    assert len(err.splitlines()) == 1


def test_exit_operational_code(monkeypatch):
    monkeypatch.setitem(cli.COMMANDS, "summary", _failing)
    code, out, err = cli_runner("summary", PATH)
    assert code == 1
    assert out == ""
    assert len(err.splitlines()) == 1


def test_exit_success_code(monkeypatch):
    text = "header\nrow\n"
    monkeypatch.setitem(cli.COMMANDS, "daily", lambda parsed: text)
    code, out, _ = cli_runner("daily", PATH)
    assert code == 0
    assert out == text

    monkeypatch.setitem(cli.COMMANDS, "daily", lambda parsed: "")
    empty_code, empty_out, _ = cli_runner("daily", PATH)
    assert empty_code == 0
    assert empty_out == ""


def test_exit_error_classes():
    assert issubclass(UsageError, Exception)
    assert issubclass(OperationalError, Exception)
    assert not issubclass(UsageError, OperationalError)
    assert not issubclass(OperationalError, UsageError)


def test_exit_launcher_status():
    result = subprocess.run([str(ROOT / "quakes"), "frobnicate", PATH], capture_output=True, text=True, cwd=ROOT)
    assert result.returncode == 2
    assert result.stdout == ""


# ── Finer coverage: failure silence, one diagnostic line, and unmapped exceptions ───────


def test_usage_exit_code_is_two_and_operational_is_one():
    assert UsageError.exit_code == 2
    assert OperationalError.exit_code == 1


def test_operational_failure_prints_exactly_one_stderr_line_without_stdout(monkeypatch, capsys):
    monkeypatch.setitem(cli.COMMANDS, "summary", _failing)
    code = main(["summary", PATH])
    captured = capsys.readouterr()
    assert code == 1
    assert captured.out == ""
    assert captured.err == "error: cannot read the file\n"


def test_multiline_message_is_squeezed_onto_one_stderr_line(monkeypatch, capsys):
    def multi(parsed):
        raise OperationalError("first line\nsecond line")

    monkeypatch.setitem(cli.COMMANDS, "summary", multi)
    code = main(["summary", PATH])
    captured = capsys.readouterr()
    assert code == 1
    assert captured.out == ""
    assert len(captured.err.splitlines()) == 1


def test_usage_failure_writes_nothing_to_stdout(capsys):
    assert main(["summary", "--n", "3", PATH]) == 2
    captured = capsys.readouterr()
    assert captured.out == ""
    assert len(captured.err.splitlines()) == 1


def test_handler_output_is_written_only_on_success(monkeypatch, capsys):
    monkeypatch.setitem(cli.COMMANDS, "summary", lambda parsed: "events\n0\n")
    assert main(["summary", PATH]) == 0
    assert capsys.readouterr().out == "events\n0\n"


def test_failing_handler_writes_no_partial_output(monkeypatch, capsys):
    def partial(parsed):
        raise OperationalError("boom")

    monkeypatch.setitem(cli.COMMANDS, "top", partial)
    assert main(["top", PATH]) == 1
    assert capsys.readouterr().out == ""


def test_unexpected_exception_is_not_mapped_to_an_exit_code(monkeypatch):
    def broken(parsed):
        raise RuntimeError("bug")

    monkeypatch.setitem(cli.COMMANDS, "summary", broken)
    try:
        main(["summary", PATH])
    except RuntimeError as exc:
        assert str(exc) == "bug"
    else:
        raise AssertionError("an unexpected exception must propagate")


def test_missing_command_is_a_usage_error_with_empty_stdout(capsys):
    assert main([]) == 2
    captured = capsys.readouterr()
    assert captured.out == ""
    assert len(captured.err.splitlines()) == 1


def test_valid_command_without_a_registered_handler_is_not_silently_successful(monkeypatch):
    monkeypatch.delitem(cli.COMMANDS, "summary", raising=False)
    assert main(["summary", PATH]) == 2


def test_launcher_exit_status_matches_main_for_a_usage_error():
    result = subprocess.run([str(ROOT / "quakes"), "frobnicate"], capture_output=True, text=True, cwd=ROOT)
    assert result.returncode == main(["frobnicate"]) == 2
