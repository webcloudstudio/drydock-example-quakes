#!/bin/sh
# Quakes test suite runner: runs the whole pytest suite unfiltered and exits with pytest's status.
set -eu
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_DIR"
if [ -f .venv/bin/activate ]; then
    set +u
    . .venv/bin/activate
    set -u
fi
exec pytest -q
