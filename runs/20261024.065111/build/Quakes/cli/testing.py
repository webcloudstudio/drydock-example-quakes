import contextlib
import io
from cli import main


def cli_runner(*args: str) -> tuple[int, str, str]:
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        try:
            code = main(list(args))
        except SystemExit as exc:
            code = int(exc.code)
    return code, out.getvalue(), err.getvalue()
