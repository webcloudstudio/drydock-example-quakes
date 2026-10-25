<!-- Compacted from ARCHITECTURE.md sha256=a4f0e3d35e74a3a608621cd364fd70b71c5a216cf0ef99264d9f012b2fdd0b87 on 2026-10-24 by drydock build agent -->

Project: quakes (Python >=3.11, stdlib only at runtime; pytest dev-only). Executable `quakes` at root -> `cli.main(argv=None)->int`.
Modules: cli/__init__.py (main, COMMANDS: dict[str, Callable[[Parsed], str]], exit mapping); cli/errors.py (UsageError exit 2, OperationalError exit 1); cli/options.py (parse_args(argv)->Parsed); cli/formatting.py (format_time, format_mag, format_mean, format_decimal, render_csv, write_csv); cli/feed.py (read_feed(path)->list[dict], extract_events(features)->list[Event], Event, filter_events(events,min_mag)); cli/reports.py (one pure fn per report, haversine_km); cli/fetch.py (build_url, http_get, fetch command); cli/testing.py (cli_runner(*args)->(exit_code, stdout, stderr)).
Parsed dataclass: command:str, min_mag:float|None, n:int (default 10), lat, lon, radius:float|None, start, end, out, file:str|None. min_mag default None for reports, 2.5 for fetch.
Commands: fetch, summary, top, daily, regions, near.
Exit codes: 0 success (incl. empty report); 1 OperationalError (unreadable file, not FeatureCollection, fetch network/HTTP/body failure); 2 UsageError. Failing command: empty stdout, one stderr line.
Pipeline: read_feed -> extract_events (drops null magnitude) -> filter_events -> report fn returns rows of preformatted strings -> write_csv. Handlers return full stdout text; main writes only after success.
Technical: half-up rounding via Decimal(repr(x)) ROUND_HALF_UP; string ordering by code point; UTF-8 output. Tests stub cli.fetch.http_get; no network in tests. No hardcoded rows/counts/distances.
Guardrails: never modify/read sources/ from app code. Tests never open network.
Project layout: pyproject.toml + uv.lock, .venv (uv venv), conftest.py (cli_runner fixture from cli.testing), tests/, bin/test.sh (runs pytest -q).
