#!/usr/bin/env python3
# Reference implementation of the Quakes report contract, used only to validate the grader.
# Exact decimal rounding; raises on any rounding tie so the exam never depends on a rounding mode.
import csv, datetime, json, math, re, sys
from decimal import Decimal, ROUND_HALF_UP
def die(code, m): print(m, file=sys.stderr); sys.exit(code)
REPORTS = ("summary", "top", "daily", "regions", "near")
a = sys.argv[1:]
if not a or a[0] not in REPORTS: die(2, "report")
report = a.pop(0); opts = {}
NUM = r"-?[0-9]+(\.[0-9]+)?"
allowed = {"summary": {"--min-mag"}, "top": {"--min-mag", "--n"}, "daily": {"--min-mag"},
           "regions": {"--min-mag"}, "near": {"--min-mag", "--lat", "--lon", "--radius"}}[report]
while a and a[0].startswith("--"):
    o = a.pop(0)
    if o not in allowed or not a: die(2, "option")
    v = a.pop(0)
    if o == "--n":
        if not re.fullmatch(r"[0-9]+", v) or int(v) < 1: die(2, "n")
        opts[o] = int(v)
    else:
        if not re.fullmatch(NUM, v): die(2, "number")
        opts[o] = Decimal(v)
if report == "near":
    if not {"--lat", "--lon", "--radius"} <= opts.keys(): die(2, "near needs lat lon radius")
    if not (-90 <= opts["--lat"] <= 90 and -180 <= opts["--lon"] <= 180 and opts["--radius"] > 0): die(2, "range")
if len(a) != 1: die(2, "file")
try: doc = json.load(open(a[0], encoding="utf-8"))
except OSError as e: die(1, str(e))
except ValueError as e: die(1, str(e))
if not isinstance(doc, dict) or doc.get("type") != "FeatureCollection" or not isinstance(doc.get("features"), list):
    die(1, "not a FeatureCollection")
def rnd(x, places):
    q = Decimal(1).scaleb(-places); d = Decimal(str(x)) if not isinstance(x, Decimal) else x
    if (d / q) % 1 == Decimal("0.5"): raise SystemExit(f"TIE {d}")
    return str(d.quantize(q, ROUND_HALF_UP))
ev = []
for f in doc["features"]:
    p = f.get("properties") or {}
    if p.get("mag") is None: continue
    mag = Decimal(str(p["mag"]))
    if "--min-mag" in opts and mag < opts["--min-mag"]: continue
    t = datetime.datetime.fromtimestamp(p["time"] // 1000, datetime.UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    lon, lat, depth = f["geometry"]["coordinates"][:3]
    place = p.get("place") or "Unknown"
    region = place.rsplit(", ", 1)[1] if ", " in place else place
    ev.append(dict(id=f["id"], mag=mag, time=t, ms=p["time"], lat=lat, lon=lon, depth=depth, place=place,
                   region=region, tsunami=p.get("tsunami") == 1))
w = csv.writer(sys.stdout, lineterminator="\n")
m1 = lambda m: str(m.quantize(Decimal("0.1")))
if report == "summary":
    w.writerow(["events", "first", "last", "min_mag", "max_mag", "mean_mag", "tsunami"])
    if ev:
        s = sorted(ev, key=lambda e: e["ms"])
        w.writerow([len(ev), s[0]["time"], s[-1]["time"], m1(min(e["mag"] for e in ev)), m1(max(e["mag"] for e in ev)),
                    rnd(sum(e["mag"] for e in ev) / len(ev), 2), sum(e["tsunami"] for e in ev)])
    else:
        w.writerow([0, "", "", "", "", "", 0])
elif report == "top":
    w.writerow(["time", "mag", "depth_km", "place", "id"])
    for e in sorted(ev, key=lambda e: (-e["mag"], e["ms"], e["id"]))[: opts.get("--n", 10)]:
        w.writerow([e["time"], m1(e["mag"]), rnd(e["depth"], 1), e["place"], e["id"]])
elif report == "daily":
    w.writerow(["date", "events", "max_mag"])
    g = {}
    for e in ev: g.setdefault(e["time"][:10], []).append(e)
    for d in sorted(g): w.writerow([d, len(g[d]), m1(max(e["mag"] for e in g[d]))])
    w.writerow(["TOTAL", len(ev), m1(max(e["mag"] for e in ev)) if ev else ""])
elif report == "regions":
    w.writerow(["region", "events", "max_mag"])
    g = {}
    for e in ev: g.setdefault(e["region"], []).append(e)
    for r in sorted(g, key=lambda r: (-len(g[r]), r.encode())): w.writerow([r, len(g[r]), m1(max(e["mag"] for e in g[r]))])
else:
    la, lo, rad = float(opts["--lat"]), float(opts["--lon"]), float(opts["--radius"])
    def hav(e):
        p1, p2 = math.radians(la), math.radians(e["lat"]); dp = p2 - p1; dl = math.radians(e["lon"] - lo)
        h = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
        return 2 * 6371.0 * math.asin(math.sqrt(h))
    rows = []
    for e in ev:
        d = hav(e)
        if d <= rad:
            frac = (d * 10) % 1
            if abs(frac - 0.5) < 1e-6 or abs(d - rad) < 1e-6: raise SystemExit(f"near-tie {d}")
            rows.append((d, e))
    w.writerow(["distance_km", "time", "mag", "place", "id"])
    for d, e in sorted(rows, key=lambda x: (x[0], x[1]["ms"])):
        w.writerow([f"{d:.1f}", e["time"], m1(e["mag"]), e["place"], e["id"]])
