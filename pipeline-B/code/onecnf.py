#!/usr/bin/env python3
"""onecnf.py STRUCTFILE OUT.cnf [CLASS ...] -- write the CNF that driver.py builds for the classes
CLASS ... (indices into the structure file, default 0 = the largest class) of the set in STRUCTFILE.
The first SAT call of driver.py for every set asks for class 0 alone, so with the default this is
exactly the CNF of that call, and kissat's proof for it has the drat_sha256 recorded in the first
"log" entry of that set in data/res_T853985.jsonl."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import enc
from driver import read_struct

sfile, out = sys.argv[1], sys.argv[2]
fam = sorted(int(x) for x in sys.argv[3:]) or [0]
B, comps, adj = read_struct(sfile)
E, y = enc.encode(B, [(comps[i][2], comps[i][3]) for i in fam])
enc.write_cnf(E, out)
print("B=%s classes %s sizes %s: %d variables, %d clauses -> %s"
      % (sorted(B), fam, [comps[i][0] for i in fam], E.nv, len(E.cl), out))
