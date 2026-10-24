# Soundings

Per-assertion acceptance board, one row per Blueprint Programmatic Acceptance check.
`drydock plan` projects every assertion as `— UNVERIFIED`; `drydock score ac` sets the
Status column from deterministic proof results. A rerun of `drydock plan` resets Status to
`— UNVERIFIED`; rescore to refresh.

| Status | Blueprint | AC Id | Text | Binding | Baseline | Previously Passed | Last Block | Evidence | Verified At |
|---|---|---|---|---|---|---|---|---|---|
| ✓ PASS | FEATURE-Fetch.md | fetch-success | A stubbed HTTP response is saved byte for byte and reports its feature count. | yes | VALID product-missing | yes | block-2 |  | 2026-10-24T06:57:09+00:00 |
| ✓ PASS | FEATURE-Fetch.md | fetch-failure | A failed HTTP request does not create its output file. | yes | VALID product-missing | yes | block-2 |  | 2026-10-24T06:57:09+00:00 |
| ✓ PASS | FEATURE-Summary.md | summary-success | The summary command succeeds on a supplied FeatureCollection. | yes | VALID baseline-red |  |  |  | 2026-10-24T06:57:09+00:00 |
| ✓ PASS | FEATURE-Summary.md | summary-invalid-file | An unreadable or invalid input file returns the operational exit code. | yes | VALID baseline-red |  |  |  | 2026-10-24T06:57:09+00:00 |
| ✓ PASS | FEATURE-Daily.md | daily-empty | An empty event file produces a successful daily report with an empty total maximum. | yes | VALID baseline-red |  |  |  | 2026-10-24T06:57:09+00:00 |
| ✓ PASS | FEATURE-Daily.md | daily-filter | The minimum magnitude option is accepted and the report succeeds. | yes | VALID baseline-red |  |  |  | 2026-10-24T06:57:09+00:00 |
| ✓ PASS | FEATURE-Top.md | top-options | The top command accepts its count option and succeeds on a supplied event file. | yes | VALID baseline-red |  |  |  | 2026-10-24T06:57:09+00:00 |
| ~ PREPASSED | FEATURE-Top.md | top-invalid-count | A nonpositive count returns the usage exit code. | yes | VALID existing-behavior |  |  | green at this block's baseline too, before its code existed — confirm the criterion exercises the story's work | 2026-10-24T06:57:09+00:00 |
| ✓ PASS | FEATURE-Regions.md | regions-command | The regions command succeeds for a FeatureCollection with an event. | yes | VALID baseline-red |  |  |  | 2026-10-24T06:57:09+00:00 |
| ✓ PASS | FEATURE-Regions.md | regions-filter | The minimum magnitude option is accepted and returns success. | yes | VALID baseline-red |  |  |  | 2026-10-24T06:57:09+00:00 |
| ✓ PASS | FEATURE-Near.md | near-valid-request | A valid near request is accepted by the CLI. | yes | VALID baseline-red |  |  |  | 2026-10-24T06:57:09+00:00 |
| ~ PREPASSED | FEATURE-Near.md | near-required-options | A near request missing a required coordinate is rejected as a usage error. | yes | VALID existing-behavior |  |  | green at this block's baseline too, before its code existed — confirm the criterion exercises the story's work | 2026-10-24T06:57:09+00:00 |
| ~ PREPASSED | FEATURE-Near.md | near-coordinate-bounds | A latitude outside the documented range is rejected as a usage error. | yes | VALID existing-behavior |  |  | green at this block's baseline too, before its code existed — confirm the criterion exercises the story's work | 2026-10-24T06:57:09+00:00 |
| ✓ PASS | FEATURE-Near.md | near-invalid-file | An invalid GeoJSON file is reported as an operational failure without standard output. | yes | VALID baseline-red |  |  |  | 2026-10-24T06:57:09+00:00 |
| ✓ PASS | FEATURE-Verification.md | verification-test-suite | The project test launcher succeeds after running the automated tests. | yes | VALID baseline-red |  |  |  | 2026-10-24T06:57:09+00:00 |
| ✓ PASS | FEATURE-Verification.md | verification-full-conformance | The complete supplied grader passes against the finished command set. | yes | VALID baseline-red |  |  |  | 2026-10-24T06:57:09+00:00 |
