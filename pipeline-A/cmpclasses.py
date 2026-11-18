# cmpclasses.py -- compare the class sizes found by pipeline A (union-find, "bsearch listall 1" output)
# with those found by pipeline B (breadth-first search, pipeline-B/work/comp_all.out), set by set.
# usage: python3 cmpclasses.py work/classes.txt ../pipeline-B/work/comp_all.out
import sys, re

def sym(b, s):
    r, c = divmod(b, 7)
    if s & 1: r = 5 - r
    if s & 2: c = 6 - c
    return r * 7 + c

def canon(S):
    return min(tuple(sorted(sym(b, s) for b in S)) for s in range(4))

A = {}
for line in open(sys.argv[1]):
    p = line.split()
    if not p or p[0] != 'S': continue
    S = canon([] if p[1] == '-' else [int(x) for x in p[1].split(',')])
    A[S] = sorted((int(c.split(':')[0]) for c in p[4:]), reverse=True)
B = {}
for line in open(sys.argv[2]):
    S = canon([int(x) for x in re.search(r'\{([0-9,]*)\}', line).group(1).split(',') if x])
    B[S] = sorted((int(x) for x in re.findall(r' (\d+):\d+', line.split('live:')[1])), reverse=True)
common = set(A) & set(B)
bad = [S for S in common if A[S] != B[S]]
print('sets in A %d, in B %d, common %d, class-size mismatches %d, classes compared %d'
      % (len(A), len(B), len(common), len(bad), sum(len(A[S]) for S in common)))
for S in sorted(bad)[:10]: print('  mismatch', S)
print('sets of A missing in B:', len(set(A) - set(B)))
sys.exit(1 if bad or set(A) - set(B) else 0)
