# slowcount.py -- independent, slow solution counter (plain backtracking in Python).
# usage: python3 slowcount.py ARRAY [ARRAY ...]
import sys
def count(s):
    g=[int(ch) for ch in s if ch.isdigit()]; assert len(g)==56
    occ=[False]*56; used=set(); n=0
    sys.setrecursionlimit(10000)
    def rec(i):
        nonlocal n
        while i<56 and occ[i]: i+=1
        if i==56: n+=1; return
        for j in ([i+1] if i%8<7 and not occ[i+1] else [])+([i+8] if i<48 else []):
            t=(min(g[i],g[j]),max(g[i],g[j]))
            if t in used: continue
            used.add(t); occ[i]=occ[j]=True
            rec(i+1)
            used.discard(t); occ[i]=occ[j]=False
    rec(0); return n
for a in sys.argv[1:]: print(a,count(a))
