import re
import sys

from cli.parser import build_parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "fetch":
        if not re.fullmatch(r"-?[0-9]+(?:\.[0-9]+)?", args.min_mag):
            print("error: magnitude must be a decimal number", file=sys.stderr)
            return 2
        from quakes import FetchError, fetch
        try:
            count = fetch(start=args.start, end=args.end, min_mag=args.min_mag, out=args.out)
        except ValueError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 2
        except FetchError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 1
        print(f"fetched,{count}")
        return 0
    from reports import ReportError, read_events, filtered, summary, daily, top, regions, near
    try:
        events = filtered(read_events(args.file), args.min_mag)
        if args.command == "summary":
            output = summary(events)
        elif args.command == "daily":
            output = daily(events)
        elif args.command == "top":
            output = top(events, args.n)
        elif args.command == "regions":
            output = regions(events)
        elif args.command == "near":
            lat, lon, radius = float(args.lat), float(args.lon), float(args.radius)
            if not -90 <= lat <= 90 or not -180 <= lon <= 180 or radius <= 0:
                print("error: coordinates are out of range or radius is not positive", file=sys.stderr)
                return 2
            output = near(events, lat, lon, radius)
        else:
            return 2
    except ReportError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(output, end="")
    return 0
