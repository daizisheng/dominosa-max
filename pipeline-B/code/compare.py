#!/usr/bin/env python3
"""compare.py A_DATA A_WORK B_DATA B_WORK -- compare the results of pipeline B with those of pipeline A.
A_DATA = pipeline-A/data (Dlist.txt, fb_all.out, joint_all.out, rbound_all.out, allcand.txt),
A_WORK = pipeline-A/work (D*all.txt, the bounds written by "pipeline-A/run.sh dangerous"),
B_DATA = pipeline-B/data (res_T853985.jsonl),
B_WORK = pipeline-B/work (T853985_D.txt, T853985_boundary.txt, comp_all.out); old_joint_arrays.txt is
written there.  Only result files are read."""
import sys, os, re, json, collections
old, oldwork, mine, minework = sys.argv[1:5]
N, T = 1292697, 853985


def sym(s, b):
    r, c = divmod(b, 7)
    if s & 1: c = 6 - c
    if s & 2: r = 5 - r
    return 7 * r + c


def mask(S): return sum(1 << b for b in S)


def canon(S):
    return min(mask(sym(s, b) for b in S) for s in range(4)) if S else 0


def canon_set(S):
    m = canon(S); return tuple(b for b in range(42) if m >> b & 1)


def parse_list(txt):
    txt = txt.strip()
    if txt in ("", "-", "{}"): return ()
    return tuple(sorted(int(x) for x in txt.strip("{}").split(",") if x != ""))


# ---- my data
myD = {}; myEval = {}
for fn in ("T853985_D.txt", "T853985_boundary.txt"):
    for line in open(os.path.join(minework, fn)):
        t = line.split(); S = parse_list(re.search(r"\{[0-9,]*\}", line).group(0))
        myEval[S] = int(t[2])
        if fn.endswith("_D.txt"): myD[S] = int(t[2])
myRes = {}
for line in open(os.path.join(mine, "res_T853985.jsonl")):
    d = json.loads(line); myRes[tuple(d["B"])] = d
myComp = {}
for line in open(os.path.join(minework, "comp_all.out")):
    S = parse_list(re.search(r"\{[0-9,]*\}", line).group(0))
    m = re.search(r"live: (\d+):", line); myComp[S] = int(m.group(1)) if m else 0
rep = []
P = lambda *a: rep.append(" ".join(str(x) for x in a))

# ---- 1. Dlist
DL = [parse_list(l) for l in open(os.path.join(old, "Dlist.txt")) if l.strip()]
DLc = collections.Counter(canon_set(S) for S in DL)
mineNE = set(S for S in myD if S)
P("[Dlist] lines", len(DL), "distinct canonical", len(DLc), "dup lines", sum(v - 1 for v in DLc.values()))
P("[Dlist] level sizes A", sorted(collections.Counter(len(S) for S in DLc).items()))
P("[Dlist] level sizes B", sorted(collections.Counter(len(S) for S in mineNE).items()))
P("[Dlist] in A not B", len(set(DLc) - mineNE), sorted(set(DLc) - mineNE)[:10])
P("[Dlist] in B not A", len(mineNE - set(DLc)), sorted(mineNE - set(DLc))[:10])

# ---- 2. D*all.txt (matching bounds of evaluated candidates)
oldB = {}; nlines = 0; incons = 0; files = []
for fn in sorted(os.listdir(oldwork)):
    if re.fullmatch(r"D\d+all\.txt", fn):
        files.append(fn)
        for line in open(os.path.join(oldwork, fn)):
            m = re.match(r"B (\S+) max (\d+)", line)
            if not m: continue
            nlines += 1; S = canon_set(parse_list(m.group(1))); v = int(m.group(2))
            if S in oldB and oldB[S] != v: incons += 1
            oldB[S] = v
both = set(oldB) & set(myEval)
diff = [(S, oldB[S], myEval[S]) for S in both if oldB[S] != myEval[S]]
P("[D*all] files", files, "lines", nlines, "distinct canonical sets", len(oldB), "internal inconsistencies", incons)
P("[D*all] compared with the candidates evaluated by B:", len(both), "bound mismatches", len(diff), diff[:10])
notmine = set(oldB) - set(myEval)
P("[D*all] sets of A not evaluated by B:", len(notmine), "of which bound > T:", sum(oldB[S] > T for S in notmine))
P("[D*all] sets evaluated by B not in the files of A:", len(set(myEval) - set(oldB)), "levels", sorted(collections.Counter(len(S) for S in set(myEval) - set(oldB)).items()))

# ---- 3. fb_all.out / joint_all.out / rbound_all.out
fb = {}
for line in open(os.path.join(old, "fb_all.out")):
    m = re.match(r"(OK|OPEN) (\S*) bound (\d+) realizable \[(.*?)\] satcalls (\d+)", line)
    if m: fb[canon_set(parse_list(m.group(2)))] = (m.group(1), int(m.group(3)), [int(x) for x in m.group(4).split(",") if x.strip()], int(m.group(5)))
P("[fb_all] sets", len(fb), collections.Counter(v[0] for v in fb.values()), "sat calls total", sum(v[3] for v in fb.values()))
P("[fb_all] sets vs D of B:", "missing in fb", len(mineNE - set(fb)), "extra in fb", len(set(fb) - mineNE))
P("[fb_all] OK sets with bound > T:", sum(1 for v in fb.values() if v[0] == "OK" and v[1] > T))


def subsets_max(S):
    """lower bound (best found) over arrays with bad set contained in S, from my exact-B results."""
    best = 0; arr = None; bs = None
    Sl = list(S)
    for k in range(1 << len(Sl)):
        U = tuple(sorted(Sl[i] for i in range(len(Sl)) if k >> i & 1))
        d = myRes.get(canon_set(U))
        if d and d.get("best_weight", 0) > best: best, arr, bs = d["best_weight"], d.get("best_array"), U
    return best, arr, bs


jt = {}
for line in open(os.path.join(old, "joint_all.out")):
    m = re.match(r"(\S+) MAX joint (\d+) \[(.*?)\] (\S+) jointcalls (\d+) (\S+)", line)
    if m: jt[canon_set(parse_list(m.group(1)))] = (int(m.group(2)), m.group(4), m.group(6), [int(x) for x in m.group(3).split(",") if x.strip()])
P("[joint_all] sets", len(jt), "status", collections.Counter(v[2] for v in jt.values()), "max", max(v[0] for v in jt.values()))
lower_viol = []; eq = 0; gt = 0
for S, v in jt.items():
    lb, arr, U = subsets_max(S)
    if lb > v[0]: lower_viol.append((S, v[0], lb, arr))
    elif lb == v[0]: eq += 1
    else: gt += 1
P("[joint_all] best found by B (over subsets, i.e. bad set contained in the set) vs MAX of A: equal", eq, "A larger", gt, "B LARGER (contradiction)", len(lower_viol), lower_viol[:5])
P("[joint_all] sets of A with MAX > T:", [(S, v[0]) for S, v in jt.items() if v[0] > T])
P("[joint_all] sets of A with MAX == T:", [(S, v[1]) for S, v in jt.items() if v[0] == T])
with open(os.path.join(minework, "old_joint_arrays.txt"), "w") as f:
    for S, v in jt.items(): f.write("%s %d {%s}\n" % (v[1], v[0], ",".join(map(str, S))))
rb = []
for line in open(os.path.join(old, "rbound_all.out")):
    m = re.match(r"(\S+) realizable comps (\d+) sum (\d+) R (\d+) nu (\d+) bound (\d+)", line)
    if m:
        S = canon_set(parse_list(m.group(1))); d = myRes.get(S)
        rb.append((S, int(m.group(6)), d["verdict"] if d else None, d["best_weight"] if d else None, d["calls"] if d else None))
P("[rbound_all] sets", len(rb), "all bounds of A <= T:", all(x[1] <= T for x in rb))
for x in rb: P("   ", x[0], "bound of A", x[1], "| B:", x[2], "best found", x[3], "SAT calls", x[4])

# ---- 4. allcand.txt (largest component per candidate set)
ac = []
for line in open(os.path.join(old, "allcand.txt")):
    m = re.match(r"B (\S+) max (\d+) rep H([0-9a-f]+) V([0-9a-f]+)", line)
    if m: ac.append((parse_list(m.group(1)), int(m.group(2))))
mm = []; cmpd = 0
for S, v in ac:
    c = canon_set(S)
    if c in myComp:
        cmpd += 1
        if myComp[c] != v: mm.append((S, v, myComp[c]))
P("[allcand] lines", len(ac), "compared (set in D of B)", cmpd, "largest-component mismatches", len(mm), mm[:10])
P("[allcand] sets not in D of B:", [(S, v) for S, v in ac if canon_set(S) not in myComp][:10])
print("\n".join(rep))
