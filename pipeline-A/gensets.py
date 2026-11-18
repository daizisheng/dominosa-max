# gensets.py -- all sets of k blocks that are canonical in the sense of bsearch.c / ub.c: the
# bitmask sum(2^b) is not larger than that of any of its 4 images under the symmetries of the
# rectangle.  Lexicographic order of the sorted block lists, as in "bsearch enum".  The original
# run enumerated the sets of at most 4 blocks this way (and used apriori.py from size 5 on), so
# the representatives in data/ are of this form for sizes 1..4.
# usage: python3 gensets.py k > sets
import sys, itertools

def sym(b, s):
    r, c = divmod(b, 7)
    if s & 1: r = 5 - r
    if s & 2: c = 6 - c
    return r * 7 + c

k = int(sys.argv[1])
if k == 0:
    print('-')
for S in itertools.combinations(range(42), k):
    m = sum(1 << b for b in S)
    if all(sum(1 << sym(b, s) for b in S) >= m for s in (1, 2, 3)):
        print(','.join(map(str, S)))
