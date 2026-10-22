# Sea Trials: Quakes

## Policy

| Consequence | On FAIL | On INCONCLUSIVE |
|---|---|---|
| blocks  | fail   | attest |
| scores  | score  | score  |
| attests | report | report |

## st-001: The supplied grader passes
Type: technical
Required: yes
Criterion: The completed quakes shall make sh sources/run.sh exit zero; that script's exit status is the sole acceptance verdict.
Testability: deterministic
Consequence: blocks
Verification: proof
Command: ["sh", "sources/run.sh"]
Pattern: ubiquitous

## st-002: Test suite passes
Type: technical
Required: yes
Criterion: The application shall provide a POSIX-compatible bin/test.sh that exits zero when every automated test passes.
Testability: deterministic
Consequence: blocks
Verification: proof
Pattern: ubiquitous

## st-003: Reports match the known answers
Type: behavioral
Required: yes
Criterion: The application shall compute the summary, top, daily, and regions reports from the snapshot, matching the known answers in sources/run.sh byte for byte.
Testability: deterministic
Consequence: blocks
Verification: proof
Pattern: ubiquitous

## st-004: Distance search uses the haversine formula
Type: behavioral
Required: yes
Criterion: When near is given a point and a radius, the application shall list every event within that haversine distance on a 6371.0 km sphere, nearest first.
Testability: deterministic
Consequence: blocks
Verification: proof
Pattern: event

## st-005: The magnitude filter applies to every report
Type: behavioral
Required: yes
Criterion: When --min-mag is given, the application shall compute every report over only the events whose magnitude is at least that value.
Testability: deterministic
Consequence: blocks
Verification: proof
Pattern: event

## st-006: Fetch saves the USGS feed
Type: behavioral
Required: yes
Criterion: When fetch is given a date range, the application shall request the USGS FDSN event query in GeoJSON and write the response unchanged to the output file, writing no file on a network or HTTP failure.
Testability: deterministic
Consequence: blocks
Verification: proof
Pattern: event

## st-007: Errors map to exit codes
Type: behavioral
Required: yes
Criterion: If the file is unreadable or not a GeoJSON FeatureCollection, then the application shall exit 1; if the arguments are malformed, then the application shall exit 2; in both cases it shall write nothing to standard output.
Testability: deterministic
Consequence: blocks
Verification: proof
Pattern: unwanted

## st-008: Tests never use the network
Type: technical
Required: yes
Criterion: The application's automated tests shall exercise fetch through a stubbed HTTP call and shall not open a network connection.
Testability: judgeable
Consequence: scores
Verification: llm
Pattern: ubiquitous
