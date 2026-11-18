# cmplines.py -- compare result files of pipeline A line by line, up to the symmetries of the
# rectangle: the set in each line is replaced by a canonical representative and the whole lines
# are compared.  Lines are matched by their set.
#   KIND fb      lines "OK|OPEN SET bound ..."           (fb_all.out)
#   KIND joint   lines "SET MAX joint ..."               (joint_all.out; other lines are ignored)
#   KIND rbound  lines "SET realizable comps ..."        (rbound_all.out)
# usage: python3 cmplines.py [--subset] KIND NEW OLD
#   without --subset both files must contain the same sets and identical lines;
#   with --subset only the sets found in both files are compared (the others are listed).
# Exit status 1 if a line differs (or, without --subset, if a set is missing on either side).
import sys

def sym(b, s):
    r, c = divmod(b, 7)
    if s & 1: r = 5 - r
    if s & 2: c = 6 - c
    return r * 7 + c

def canon(x):
    S = [] if x == '-' else [int(y) for y in x.split(',')]
    T = min(tuple(sorted(sym(b, s) for b in S)) for s in range(4))
    return ','.join(map(str, T)) if T else '-'

def load(kind, fn):
    out = {}
    for line in open(fn):
        p = line.split()
        if kind == 'fb':
            if len(p) < 2 or p[0] not in ('OK', 'OPEN'): continue
            i = 1
        elif kind == 'joint':
            if 'MAX' not in p: continue
            i = 0
        else:
            if 'realizable' not in p: continue
            i = 0
        c = canon(p[i]); p[i] = c
        out[c] = ' '.join(p)
    return out

args = sys.argv[1:]
subset = args[0] == '--subset'
if subset: args = args[1:]
kind, new, old = args
A, B = load(kind, new), load(kind, old)
both = sorted(set(A) & set(B))
diff = [S for S in both if A[S] != B[S]]
onlyA, onlyB = sorted(set(A) - set(B)), sorted(set(B) - set(A))
print('%s: %d sets in %s, %d in %s; %d in both, %d identical lines, %d different; only in the first %d, only in the second %d'
      % (kind, len(A), new, len(B), old, len(both), len(both) - len(diff), len(diff), len(onlyA), len(onlyB)))
for S in diff[:5]: print('  differs:', A[S], '|', B[S])
for S in onlyA[:12]: print('  only in %s: %s' % (new, S))
for S in onlyB[:12]: print('  only in %s: %s' % (old, S))
sys.exit(1 if diff or (not subset and (onlyA or onlyB)) else 0)
