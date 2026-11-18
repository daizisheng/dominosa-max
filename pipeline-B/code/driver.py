#!/usr/bin/env python3
"""driver.py -- for each bad set B (structure file from comp.c), decide whether some array
with bad set EXACTLY B has more than T solutions.

Facts used (see the README and the note):
 * solutions of A = union of components of G_B (B = bad(A)), all tilings of a component
   carry the same pair multiset;
 * the solution set is independent in H_B, so two components joined by a B-flip
   ("quotient edge") are never both solution components;
 * whether a family F of components is jointly realizable (some A with bad(A)=B has
   all of F among its solutions) is decided by SAT on representatives (enc.py).
Branch and bound: maximise the weight of a jointly realizable family; prune when
weight(chosen) + weight(compatible candidates) <= T.  Every UNSAT is certified with a DRAT
proof checked by drat-trim; every SAT model is decoded to an array and checked directly.

usage: driver.py DATADIR STRUCTFILE T WORKDIR  -> prints one JSON line
"""
import sys, os, json, subprocess, time, hashlib, shutil
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import enc

KISSAT = os.environ.get("KISSAT", "kissat")      # kissat 4.0.4 was used
DRAT = os.environ.get("DRAT_TRIM", os.path.join(os.path.dirname(os.path.abspath(__file__)), "drat-trim"))
SAT_TIMEOUT = int(os.environ.get("SAT_TIMEOUT", "20000"))
DRAT_TIMEOUT = int(os.environ.get("DRAT_TIMEOUT", "40000"))
MAX_CALLS = int(os.environ.get("MAX_CALLS", "20000"))
KEEP_PROOF_MB = float(os.environ.get("KEEP_PROOF_MB", "0"))  # keep proofs (gzip) up to this size


def check_tools():
    """Stop with a clear message if kissat or drat-trim cannot be run."""
    for name, path, var in (("kissat", KISSAT, "KISSAT"), ("drat-trim", DRAT, "DRAT_TRIM")):
        if shutil.which(path) is None:
            sys.exit("driver.py: cannot run %s (%s). Install it (see the README, section External software)\n"
                     "and put it on PATH or set %s=/path/to/%s." % (name, path, var, name))


def read_struct(fn):
    comps, edges = [], []
    with open(fn) as f:
        for line in f:
            t = line.split()
            if t[0] == "B":
                B = frozenset(int(x) for x in t[1:])
            elif t[0] == "C":
                comps.append((int(t[1]), int(t[2]), int(t[3]), int(t[4])))
            elif t[0] == "E":
                edges.append((int(t[1]), int(t[2])))
    adj = [set() for _ in comps]
    for a, b in edges:
        adj[a].add(b); adj[b].add(a)
    return B, comps, adj


def is_solution(H, V, A):
    seen = set()
    for c in range(56):
        if H >> c & 1:
            p = tuple(sorted((A[c], A[c + 1])))
            if p in seen: return False
            seen.add(p)
        if V >> c & 1:
            p = tuple(sorted((A[c], A[c + 8])))
            if p in seen: return False
            seen.add(p)
    return len(seen) == 28


def bad_set(A):
    s = set()
    for b in range(42):
        P, Q, R, S = enc.blk_cells(b)
        if not (A[P] == A[S] or A[Q] == A[R]): s.add(b)
    return frozenset(s)


class Solver:
    def __init__(self, B, comps, work, tag, T):
        self.B, self.comps, self.work, self.tag, self.T = B, comps, work, tag, T
        self.calls = self.nsat = self.nunsat = self.nverified = 0
        self.unsat_sets = []       # frozensets proven UNSAT
        self.witness = []          # (frozenset of solution comps, array string)
        self.log = []
        self.fail = []
        self.solve_time = self.drat_time = 0.0

    def realizable(self, fam):
        fam = frozenset(fam)
        for U in self.unsat_sets:
            if U <= fam: return None
        for F, a in self.witness:
            if fam <= F: return (F, a)
        if self.calls >= MAX_CALLS:
            raise RuntimeError("MAX_CALLS")
        self.calls += 1
        order = sorted(fam)
        E, y = enc.encode(self.B, [(self.comps[i][2], self.comps[i][3]) for i in order])
        base = os.path.join(self.work, "%s_%d" % (self.tag, self.calls))
        enc.write_cnf(E, base + ".cnf")
        t0 = time.time()
        try:
            r = subprocess.run([KISSAT, "-q", "--no-binary", base + ".cnf", base + ".drat"], capture_output=True, text=True, timeout=SAT_TIMEOUT)
            rc = r.returncode
        except subprocess.TimeoutExpired:
            rc = -1
        self.solve_time += time.time() - t0
        entry = {"fam": order, "sizes": [self.comps[i][0] for i in order], "nv": E.nv, "nc": len(E.cl)}
        if rc == 10:
            lits = []
            for line in r.stdout.splitlines():
                if line.startswith("v "): lits += [int(x) for x in line[2:].split()]
            a = enc.decode(lits, y)
            A = [int(ch) for ch in a if ch != "/"]
            assert bad_set(A) == self.B, "SAT model has wrong bad set"
            for i in order:
                assert is_solution(self.comps[i][2], self.comps[i][3], A), "SAT model: tiling not a solution"
            F = frozenset(i for i, c in enumerate(self.comps) if is_solution(c[2], c[3], A))
            w = sum(self.comps[i][0] for i in F)
            self.witness.append((F, a)); self.nsat += 1
            entry.update(res="SAT", array=a, weight=w, ncomp=len(F))
            self.log.append(entry)
            os.remove(base + ".cnf"); os.remove(base + ".drat")
            return (F, a)
        elif rc == 20:
            sz = os.path.getsize(base + ".drat")
            h = hashlib.sha256(open(base + ".drat", "rb").read()).hexdigest()
            t1 = time.time()
            try:
                d = subprocess.run([DRAT, base + ".cnf", base + ".drat", "-t", str(DRAT_TIMEOUT)], capture_output=True, text=True, timeout=DRAT_TIMEOUT + 600)
                ok = "s VERIFIED" in d.stdout
            except subprocess.TimeoutExpired:
                ok = False
            self.drat_time += time.time() - t1
            entry.update(res="UNSAT", drat_bytes=sz, drat_sha256=h, verified=ok)
            self.log.append(entry)
            self.nunsat += 1
            if ok:
                self.nverified += 1
                self.unsat_sets.append(fam)
                if sz <= KEEP_PROOF_MB * 1e6:
                    subprocess.run(["gzip", "-f", base + ".drat"]); subprocess.run(["gzip", "-f", base + ".cnf"])
                else:
                    os.remove(base + ".drat"); os.remove(base + ".cnf")
                return None
            self.fail.append(entry)
            raise RuntimeError("DRAT not verified")
        else:
            entry.update(res="TIMEOUT/ERR rc=%d" % rc)
            self.log.append(entry); self.fail.append(entry)
            raise RuntimeError("solver failed")


def main():
    check_tools()
    datadir, sfile, T, work = sys.argv[1], sys.argv[2], int(sys.argv[3]), sys.argv[4]
    os.makedirs(work, exist_ok=True)
    B, comps, adj = read_struct(sfile)
    tag = os.path.basename(sfile).replace(".txt", "")
    S = Solver(B, comps, work, tag, T)
    size = [c[0] for c in comps]
    best = {"w": 0, "array": None}
    status = "OK"
    t0 = time.time()

    def search(C, wC, cand):
        # cand: list of comp ids (decreasing size), each compatible (no quotient edge) with C.
        # Loop over the "exclude" branches; recurse only into "include" branches.
        rem = sum(size[j] for j in cand)
        for idx, j in enumerate(cand):
            if wC + rem <= T:
                return
            rem -= size[j]
            r = S.realizable(C | {j})
            if r is not None:
                F, a = r
                w = sum(size[i] for i in F)
                if w > best["w"]: best["w"], best["array"] = w, a
                if w > T:
                    raise StopIteration
                search(C | {j}, wC + size[j], [k for k in cand[idx + 1:] if k not in adj[j]])

    try:
        search(frozenset(), 0, list(range(len(comps))))
        verdict = "LE_T"
    except StopIteration:
        verdict = "EXCEEDS_T"
    except RuntimeError as e:
        verdict = "UNRESOLVED:" + str(e)
    out = {"B": sorted(B), "ncomp": len(comps), "T": T, "verdict": verdict, "best_weight": best["w"], "best_array": best["array"],
           "calls": S.calls, "sat": S.nsat, "unsat": S.nunsat, "drat_verified": S.nverified, "fail": S.fail,
           "solve_s": round(S.solve_time, 2), "drat_s": round(S.drat_time, 2), "wall_s": round(time.time() - t0, 2), "log": S.log}
    print(json.dumps(out))


if __name__ == "__main__":
    main()
