# cmpsets.py -- compare two lists of block sets up to the 4 symmetries of the rectangle.
# Each line contributes its first field of the form "a,b,c" (or "-" for the empty set); if the
# line has the form "B set max VALUE ..." or "set U VALUE", the value is compared as well.
# usage: python3 cmpsets.py FILE1 FILE2
import sys, re

def sym(b, s):
    r, c = divmod(b, 7)
    if s & 1: r = 5 - r
    if s & 2: c = 6 - c
    return r * 7 + c

def canon(S):
    return min(tuple(sorted(sym(b, s) for b in S)) for s in range(4))

def load(fn):
    out = {}
    for line in open(fn):
        p = line.split()
        for i, x in enumerate(p):
            if x == '-' or re.fullmatch(r'[0-9]+(,[0-9]+)*', x):
                S = canon([] if x == '-' else [int(y) for y in x.split(',')])
                v = int(p[i + 2]) if i + 2 < len(p) and p[i + 1] in ('max', 'U') else None
                out.setdefault(S, v)
                break
    return out

a, b = load(sys.argv[1]), load(sys.argv[2])
onlya, onlyb = set(a) - set(b), set(b) - set(a)
diff = [S for S in set(a) & set(b) if a[S] != b[S]]
print('%s: %d sets; %s: %d sets; only in first %d, only in second %d, different values %d'
      % (sys.argv[1], len(a), sys.argv[2], len(b), len(onlya), len(onlyb), len(diff)))
for S in sorted(onlya)[:5]: print('  only in first:', S)
for S in sorted(onlyb)[:5]: print('  only in second:', S)
for S in sorted(diff)[:5]: print('  value differs:', S, a[S], b[S])
sys.exit(0 if not (onlya or onlyb or diff) else 1)
