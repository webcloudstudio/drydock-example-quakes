# QUAKES

- Short description: Drydock uat - Quakes is the get-data-and-report kit. The source is an original brief for a Python command-line tool that downloads the USGS earthquake feed as GeoJSON and writes five CSV reports from a saved file: summary, largest events, events per day, events per region, and events within a haversine distance of a point. The supplied grader, sources/run.sh, runs 26 checks of exit code and output against a frozen real USGS snapshot of the 44 magnitude 5+ events of 2025-01-01 to 2025-01-07 (non-ASCII place names, quoted commas, the Tibet aftershock cluster). The grader never uses the network; fetch is tested against a stub. Run with drydock uat Quakes. Source Repo: none, the brief is original to this kit; data from the USGS FDSN event service.
- Status: PLAN CREATED

1 of 4 receipt claims proven. Open `index.html` for the linked proof kit; verify it with `sha256sum -c SHA256SUMS`.

## Receipt

| Claim | Verdict | Recorded outcome | Proof |
|---|---|---|---|
| Lifecycle completed | FAIL | 4 lifecycle commands executed; the run ended at 04-plan. | [result.json](result.json) |
| External conformance suite passed | UNPROVEN | No external test command is defined for this project. | — |
| Release score passed | UNPROVEN | No release score was recorded for this run. | — |
| Integrity verification passed | PASS | 146 files digested; verify with sha256sum -c SHA256SUMS. | [SHA256SUMS](SHA256SUMS) |

## Run facts

- Drydock: `0.8.0` (commit `20f9d392af1aef4fdabdd72d79158baac77fa7ac`)
- Provider and model: `codex` / `gpt-6-luna`
- Platform: `Linux-6.6.87.2-microsoft-standard-WSL2-x86_64-with-glibc2.35` on Python `3.12.13`
- Run: `20261024.054647`
- Elapsed: 197.5s
- LLM calls: 9
- Tokens: cached 103,680; uncached 430,972; output 20,555
- LLM elapsed: 179.9s
- Build passes: 0; repairs: not recorded
- Conformance: no external suite defined
- Advisory scores: none recorded

## RUN SUMMARY

- Input specification: [`sources/INSTRUCTIONS.md`](sources/INSTRUCTIONS.md)
- Delivered Code: [`build/Quakes/`](build/Quakes)
- Test Results: not recorded for this run.

## Shortfall

- Failure: Quakes: plan exited 1

## Commands

| # | Command | Exit | Elapsed | Output |
|---|---|---|---|---|
| 01-init | `/mnt/c/Users/barlo/projects/drydock/.venv/bin/python -m drydock init Quakes` | 0 | 2.3s | [stdout](evidence/commands/01-init.stdout.log) · [stderr](evidence/commands/01-init.stderr.log) |
| 02-import-sources | `/mnt/c/Users/barlo/projects/drydock/.venv/bin/python -m drydock import Quakes sources --format markdown` | 0 | 5.6s | [stdout](evidence/commands/02-import-sources.stdout.log) · [stderr](evidence/commands/02-import-sources.stderr.log) |
| 03-analyze | `/mnt/c/Users/barlo/projects/drydock/.venv/bin/python -m drydock analyze Quakes` | 0 | 33.0s | [stdout](evidence/commands/03-analyze.stdout.log) · [stderr](evidence/commands/03-analyze.stderr.log) · [llm](evidence/commands/03-analyze.llm.log) |
| 04-plan | `/mnt/c/Users/barlo/projects/drydock/.venv/bin/python -m drydock plan Quakes --override` | 1 | 153.3s | [stdout](evidence/commands/04-plan.stdout.log) · [stderr](evidence/commands/04-plan.stderr.log) · [llm](evidence/commands/04-plan.llm.log) |

## Evidence

- [`evidence/commands/`](evidence/commands) — stdout and stderr of every command
- [`evidence/prompts/`](evidence/prompts) — the assembled prompt for every LLM call
- [`evidence/provider_raw/`](evidence/provider_raw) — unmodified provider transcripts
- [`evidence/llm_logs/`](evidence/llm_logs) — call banners and token accounting
- [`result.json`](result.json) — the machine-readable record of this run
