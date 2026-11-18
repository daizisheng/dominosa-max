"""Compare the maximizer orbit sets of two independent computations.
usage: python3 cmpsets.py n M fileA countmax_json_glob
fileA: arrays (glob allowed) (first field) with their counts (second field), e.g. bb/bfa output.
"""
import sys, json
from dom import Board, canon_full

n, M, fa, fb = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3], sys.argv[4]
bd = Board(n)
A = set()
import glob as _g
lines = [l for ff in sorted(_g.glob(fa)) for l in open(ff)]
for line in lines:
    f = line.split()
    if len(f) >= 2 and f[0][0].isdigit() and f[1].isdigit() and int(f[1]) == M:
        A.add(canon_full(bd, bd.parse(f[0])))
B = set()
import glob
perB = []
for f in sorted(glob.glob(fb)):
    perB += json.load(open(f))['perB']
for r in perB:
    for s in r['arrays']:
        a, c = s.split()
        if int(c) == M:
            B.add(canon_full(bd, bd.parse(a)))
print(f'n={n} M={M}: orbits from {fa}: {len(A)}; from block method: {len(B)}; equal: {A == B}')
