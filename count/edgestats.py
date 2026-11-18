# edgestats.py -- in how many solutions does each of the 97 candidate placements occur?
# usage: python3 edgestats.py ARRAY [ARRAY ...]
import sys
def stats(s):
    g=[int(ch) for ch in s if ch.isdigit()]
    occ=[False]*56; used=set(); cnt={}; stack=[]; n=0
    def rec(i):
        nonlocal n
        while i<56 and occ[i]: i+=1
        if i==56:
            n+=1
            for e in stack: cnt[e]=cnt.get(e,0)+1
            return
        for j in ([i+1] if i%8<7 and not occ[i+1] else [])+([i+8] if i<48 else []):
            t=(min(g[i],g[j]),max(g[i],g[j]))
            if t in used: continue
            used.add(t); occ[i]=occ[j]=True; stack.append((i,j))
            rec(i+1)
            stack.pop(); used.discard(t); occ[i]=occ[j]=False
    rec(0)
    edges=[(i,i+1) for i in range(56) if i%8<7]+[(i,i+8) for i in range(48)]
    z=[e for e in edges if e not in cnt]
    print(s,'solutions',n,'placements used',len(cnt),'of 97; never used',z,'min occurrences',min(cnt.values()))
for a in sys.argv[1:]: stats(a)
