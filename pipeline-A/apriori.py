# Given canonical k-sets of blocks whose largest flip component exceeds thr ("B b1,..,bk max M ..."),
# output canonical (k+1)-sets all of whose k-subsets are (up to symmetry) in the list.
# Valid because comp_B(T) is contained in comp_{B-b}(T) for every b in B (and, for the matching bound,
# because nu(H_B) is monotone in B).  Input lines "B set max value"; "-" is the empty set.
# usage: python3 apriori.py THR LEVELFILE > candidates
import sys
def sym(b,s):
    r,c=divmod(b,7)
    if s&1: r=5-r
    if s&2: c=6-c
    return r*7+c
def canon(S):
    S=list(S)
    return min(tuple(sorted(sym(b,s) for b in S)) for s in range(4))
thr=int(sys.argv[1]); keep=set()
for line in open(sys.argv[2]):
    p=line.split()
    if p and p[0]=='B' and int(p[3])>thr: keep.add(canon(int(x) for x in p[1].split(',') if x!='-'))
full=set()
for S in keep:
    for s in range(4): full.add(tuple(sorted(sym(b,s) for b in S)))
out=set()
for S in full:
    for b in range(42):
        if b in S: continue
        T=tuple(sorted(S+(b,)))
        if canon(T)!=T or T in out: continue
        if all(canon(T[:i]+T[i+1:]) in keep for i in range(len(T))): out.add(T)
sys.stderr.write('k-sets kept %d, candidates %d\n'%(len(keep),len(out)))
for T in sorted(out): print(','.join(map(str,T)))
