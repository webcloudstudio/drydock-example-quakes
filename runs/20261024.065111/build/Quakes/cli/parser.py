import argparse
import re


_DECIMAL = re.compile(r"-?[0-9]+(?:\.[0-9]+)?\Z")


def decimal(value: str) -> str:
    if not _DECIMAL.fullmatch(value):
        raise argparse.ArgumentTypeError("must be a decimal number")
    return value


def positive_int(value: str) -> int:
    try:
        number = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("must be a positive integer") from exc
    if number <= 0:
        raise argparse.ArgumentTypeError("must be a positive integer")
    return number


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="quakes")
    sub = parser.add_subparsers(dest="command", required=True)
    fetch = sub.add_parser("fetch", help="download a USGS GeoJSON feed")
    fetch.add_argument("--start", required=True)
    fetch.add_argument("--end", required=True)
    fetch.add_argument("--min-mag", default="2.5")
    fetch.add_argument("--out", required=True)
    for name in ("summary", "daily", "top", "regions", "near"):
        command = sub.add_parser(name)
        if name in {"summary", "daily", "top", "regions", "near"}:
            command.add_argument("--min-mag", type=decimal, default=None)
        if name == "top":
            command.add_argument("--n", type=positive_int, default=10)
        if name == "near":
            command.add_argument("--lat", type=decimal, required=True)
            command.add_argument("--lon", type=decimal, required=True)
            command.add_argument("--radius", type=decimal, required=True)
        command.add_argument("file")
    return parser
