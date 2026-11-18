#!/usr/bin/env python3
"""enc_test.py DATADIR WORK NRAND -- completeness tests of the CNF encoding (an UNSAT answer is
only meaningful if the CNF does not over-constrain).  Every instance below is KNOWN to be
realizable, so kissat must answer SAT:
 (1) random tiling T + random bijection dominoes->pairs + random orientations gives array A;
     query (bad(A), [T]).
 (2) known arrays (record, Gonzalez-Morris): query (bad(A), [T1,T2,T3]) for random solutions T_i,
     also after a random value permutation and a random rectangle symmetry of A."""
import sys, os, random, subprocess, shutil
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import enc
from driver import is_solution, bad_set

datadir, work, nrand = sys.argv[1], sys.argv[2], int(sys.argv[3])
KISSAT = os.environ.get("KISSAT", "kissat")
if shutil.which(KISSAT) is None:
    sys.exit("enc_test.py: cannot run kissat (%s); install it or set KISSAT=/path/to/kissat." % KISSAT)
os.makedirs(work, exist_ok=True)
TL = enc.load_tilings(datadir)
rng = random.Random(20261118)


def sat(B, tilings, name):
    E, y = enc.encode(B, tilings)
    fn = os.path.join(work, name + ".cnf"); enc.write_cnf(E, fn)
    r = subprocess.run([KISSAT, "-q", fn], capture_output=True, text=True, timeout=1800)
    os.remove(fn)
    if r.returncode != 10: return None
    lits = [int(x) for l in r.stdout.splitlines() if l.startswith("v ") for x in l[2:].split()]
    a = enc.decode(lits, y); A = [int(c) for c in a if c != "/"]
    assert bad_set(A) == frozenset(B) and all(is_solution(H, V, A) for H, V in tilings)
    return a


fails = 0
for it in range(nrand):
    t = rng.randrange(len(TL)); H, V = int(TL[t][0]), int(TL[t][1])
    doms = enc.dominoes(H, V); pairs = enc.PAIRS[:]; rng.shuffle(pairs)
    A = [0] * 56
    for (u, v), (a, b) in zip(doms, pairs):
        if rng.random() < .5: a, b = b, a
        A[u], A[v] = a, b
    B = bad_set(A)
    ok = sat(B, [(H, V)], "r%d" % it) is not None
    fails += not ok
    print("rand %d |B|=%d %s" % (it, len(B), "SAT" if ok else "FAIL"), flush=True)


def sym(A, s):
    out = [0] * 56
    for r in range(7):
        for c in range(8):
            rr = 6 - r if s & 2 else r; cc = 7 - c if s & 1 else c
            out[8 * rr + cc] = A[8 * r + c]
    return out


known = ["00060465/20504626/52012466/45122236/51312333/11143035/61444355",
         "06151146/66611014/56132144/55326224/53632022/34300525/33040054"]
for a0 in known:
    A0 = [int(c) for c in a0 if c != "/"]
    for it in range(10):
        perm = list(range(7)); rng.shuffle(perm); s = rng.randrange(4)
        A = sym([perm[x] for x in A0], s)
        sols = []
        while len(sols) < 3:
            t = rng.randrange(len(TL)); H, V = int(TL[t][0]), int(TL[t][1])
            if is_solution(H, V, A): sols.append((H, V))
        ok = sat(bad_set(A), sols, "k%d" % it) is not None
        fails += not ok
        print("known %s perm=%s sym=%d |B|=%d %s" % (a0[:8], perm, s, len(bad_set(A)), "SAT" if ok else "FAIL"), flush=True)
print("FAILS", fails)
