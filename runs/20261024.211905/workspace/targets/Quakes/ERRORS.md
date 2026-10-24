# BIG ERRORS — action required

- Command: `plan`
- Phase: plan verify
- State: Error
- Timestamp: 2026-10-24T21:30:00+00:00
- Execution ID: 20261024.212059.352Z-0dc20faf
- Challenge Execution ID: -
- Classification: plan cannot be built as written
- Evidence / logs: /mnt/c/Users/barlo/projects/drydock/uat/Quakes/runs/20261024.211905/workspace/logs

## Diagnostic

plan verify: Quakes
  1 criterion cannot run as written
  ✗  FEATURE-ExitCodes.md [exit-parse-usage-errors]: calls `cli_runner` at line(s) 19 without asserting its exit status; bind it as `code, out, err = cli_runner(...)` and assert `code` before the next call
  Run: drydock plan repair Quakes

## Recovery

Run: drydock plan repair Quakes
