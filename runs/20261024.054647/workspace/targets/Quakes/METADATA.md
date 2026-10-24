# AUTHORITATIVE PROJECT METADATA — FIELDS SHOULD BE CURRENT

name: Quakes
display_name: drydock Quakes Uat Case
short_description: Drydock uat - Quakes is the get-data-and-report kit. The source is an original brief for a Python command-line tool that downloads the USGS earthquake feed as GeoJSON and writes five CSV reports from a saved file: summary, largest events, events per day, events per region, and events within a haversine distance of a point. The supplied grader, sources/run.sh, runs 26 checks of exit code and output against a frozen real USGS snapshot of the 44 magnitude 5+ events of 2025-01-01 to 2025-01-07 (non-ASCII place names, quoted commas, the Tibet aftershock cluster). The grader never uses the network; fetch is tested against a stub. Run with drydock uat Quakes. Source Repo: none, the brief is original to this kit; data from the USGS FDSN event service.
stack: Python
version: 0.03
build_state: analyzed
build_sub_state: complete
last_analyzed: 2026-10-24
last_planned: 
last_built: 
build_dir: 
brand: 
git_repo: 
release_tag: 
updated: 2026-10-24T05:47:27+00:00
