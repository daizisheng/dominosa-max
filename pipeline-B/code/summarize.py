#!/usr/bin/env python3
"""summarize.py SETLIST RESULTS.jsonl WITNESS_OUT -- totals + list of all SAT witness arrays.
The sets are processed in sorted order of B, so the output does not depend on the order of the
lines of RESULTS.jsonl (runall.py writes them in order of completion)."""
import sys, json, re, collections
setlist, resfn, wout = sys.argv[1:4]
want = set()
for line in open(setlist):
    m = re.search(r"\{([0-9,]*)\}", line)
    if m: want.add(tuple(int(x) for x in m.group(1).split(",") if x))
R = {}
for line in open(resfn):
    d = json.loads(line); R[tuple(d["B"])] = d
missing = want - set(R)
extra = set(R) - want
V = collections.Counter(d["verdict"] for d in R.values())
tot = collections.Counter()
bylev = collections.defaultdict(collections.Counter)
best = (0, None, None)
wit = []
proof_bytes = 0
maxproof = (0, None)
for B, d in sorted(R.items()):
    for k in ("calls", "sat", "unsat", "drat_verified"): tot[k] += d.get(k, 0)
    tot["solve_s"] += d.get("solve_s", 0); tot["drat_s"] += d.get("drat_s", 0); tot["wall_s"] += d.get("wall_s", 0)
    tot["fail"] += len(d.get("fail", []))
    lv = bylev[len(B)]; lv["sets"] += 1; lv["calls"] += d.get("calls", 0); lv["sat"] += d.get("sat", 0); lv["unsat"] += d.get("unsat", 0)
    lv[d["verdict"]] += 1
    if d.get("best_weight", 0) > best[0]: best = (d["best_weight"], B, d.get("best_array"))
    for e in d.get("log", []):
        if e["res"] == "SAT": wit.append((e["array"], e["weight"], B))
        if e["res"] == "UNSAT":
            proof_bytes += e["drat_bytes"]
            if e["drat_bytes"] > maxproof[0]: maxproof = (e["drat_bytes"], B, e["drat_sha256"])
        if e["res"] == "UNSAT" and not e["verified"]: tot["unverified"] += 1
top = sorted(((d.get("best_weight", 0), B) for B, d in R.items()), reverse=True)[:12]
print("sets wanted %d, results %d, missing %d, extra %d" % (len(want), len(R), len(missing), len(extra)))
print("verdicts", dict(V))
print("totals", dict(tot))
print("DRAT total bytes %d, largest %d (B=%s sha256=%s)" % (proof_bytes, maxproof[0], maxproof[1], maxproof[2]))
print("max best weight %d at B=%s array=%s" % best)
print("top best weights:", top)
calls = collections.Counter(d.get("calls", 0) for d in R.values())
print("sets needing one call: %d; max calls per set: %d" % (calls[1], max(calls)))
for k in sorted(bylev): print("level", k, dict(bylev[k]))
with open(wout, "w") as f:
    for a, w, B in wit: f.write("%s %d {%s}\n" % (a, w, ",".join(map(str, B))))
print("SAT witnesses written:", len(wit))
