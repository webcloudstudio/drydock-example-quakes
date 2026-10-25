"""Expected failures that `main` converts to exit codes instead of raising."""


class QuakesError(Exception):
    """Base for expected failures. The message is one diagnostic line; `main` prints it to stderr."""

    exit_code = 1


class UsageError(QuakesError):
    """Bad command line: unknown command, missing argument, invalid value. Exit code 2."""

    exit_code = 2


class OperationalError(QuakesError):
    """A valid command that could not complete: unreadable file, bad feed, network failure. Exit code 1."""

    exit_code = 1
