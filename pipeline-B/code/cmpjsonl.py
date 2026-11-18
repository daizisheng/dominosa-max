#!/usr/bin/env python3
"""cmpjsonl.py NEW.jsonl OLD.jsonl -- compare two result files of runall.py set by set (keyed by B),
ignoring the timings (solve_s, drat_s, wall_s).  Everything else must agree: verdict, best total,
best array, numbers of calls, and for every call the classes asked for, the CNF size, the answer,
the SAT array, and for UNSAT the size, sha256 and verification of the DRAT proof.
With --subset only the sets present in NEW are compared.  Exit status 1 on any difference."""
import sys, json

TIMINGS = ("solve_s", "drat_s", "wall_s")


def load(fn):
    R = {}
    for line in open(fn):
        d = json.loads(line)
        for k in TIMINGS: d.pop(k, None)
        R[tuple(d["B"])] = d
    return R


args = sys.argv[1:]
subset = args[0] == "--subset"
if subset: args = args[1:]
A, B = load(args[0]), load(args[1])
keys = sorted(set(A) & set(B))
diff = [k for k in keys if A[k] != B[k]]
onlyA, onlyB = sorted(set(A) - set(B)), sorted(set(B) - set(A))
print("sets: %d in %s, %d in %s; compared %d, identical %d, different %d; only in the first %d, only in the second %d"
      % (len(A), args[0], len(B), args[1], len(keys), len(keys) - len(diff), len(diff), len(onlyA), len(onlyB)))
for k in diff[:5]:
    a, b = A[k], B[k]
    print("  differs: B=%s, fields %s" % (list(k), sorted(f for f in set(a) | set(b) if a.get(f) != b.get(f))))
bad = diff or onlyA or (onlyB and not subset)
sys.exit(1 if bad else 0)
