"""Merge bb3 outputs for n=5 and compare with the block method.
usage: python3 bb3merge.py M BLOCKMETHOD_ARRAYS BB3_OUTPUT [BB3_OUTPUT ...]
BB3_OUTPUT: output of one or more bb3 slices ("array count weight" lines, one "END ..." line per slice),
e.g. data/n5_bb3_leaves.txt, which holds the 4000 slices of "bb3 5 23929 4000 j 10", j = 0..3999.
"""
import sys, collections
from dom import Board, canon_full

M, fb, outs = int(sys.argv[1]), sys.argv[2], sys.argv[3:]
bd = Board(5)
hist = collections.Counter()
orbits = set()
nodes = nleaf = nslices = 0
for fn in outs:
    for line in open(fn):
        f = line.split()
        if f[0] == 'END':
            nodes += int(f[4]); nslices += 1
            continue
        s, w = int(f[1]), int(f[2])
        hist[s] += w
        nleaf += 1
        if s == M:
            orbits.add(canon_full(bd, bd.parse(f[0])))
print('slices', nslices)
print('nodes', nodes, 'leaves', nleaf)
print('weighted histogram (all arrays, >= THR):', dict(sorted(hist.items())))
print('max', max(hist) if hist else None, 'orbits at M', len(orbits))
B = set(canon_full(bd, bd.parse(l.split()[0])) for l in open(fb) if l.strip())
print('block-method orbits', len(B), 'bb3 subset of block:', orbits <= B, 'equal:', orbits == B)
sys.exit(0 if hist and max(hist) == M and orbits == B else 1)
