#!/usr/bin/env python3
# trim_quakes.py <usgs.geojson> <out> — freeze the 2025-01-01..07 M5+ USGS snapshot, one feature per line.
import json, sys
src = json.load(open(sys.argv[1], encoding="utf-8"))
END = 1736294400000  # 2025-01-08T00:00:00Z
KEEP = ("mag", "place", "time", "updated", "tsunami", "magType", "type", "status", "alert", "sig", "url", "title")
feats = []
for f in src["features"]:
    if f["properties"]["time"] >= END:
        continue
    feats.append({"type": "Feature", "properties": {k: f["properties"].get(k) for k in KEEP},
                  "geometry": f["geometry"], "id": f["id"]})
meta = {"generated": src["metadata"]["generated"],
        "url": "https://earthquake.usgs.gov/fdsnws/event/1/query?format=geojson&starttime=2025-01-01"
               "&endtime=2025-01-08&minmagnitude=5.0&orderby=time-asc",
        "title": "USGS Earthquakes", "status": 200, "api": src["metadata"]["api"], "count": len(feats)}
with open(sys.argv[2], "w", encoding="utf-8", newline="\n") as out:
    out.write('{"type":"FeatureCollection","metadata":' + json.dumps(meta, ensure_ascii=False, separators=(",", ":")) + ',"features":[\n')
    out.write(",\n".join(json.dumps(f, ensure_ascii=False, separators=(",", ":")) for f in feats))
    out.write("\n],\"bbox\":null}\n")
