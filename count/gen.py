# gen.py -- independent check for double-n arrays on the (n+1)x(n+2) board (any n, practical
# for n <= 5): number of tilings and solutions, bad blocks, class sizes, solution classes.
# usage: python3 gen.py ARRAY [ARRAY ...]      e.g. python3 gen.py 001/011 0001/0211/2221
import sys
sys.setrecursionlimit(10000)
def analyse(s):
    g=[list(map(int,r)) for r in s.split('/')]; R=len(g); C=len(g[0]); n=R-1
    assert C==n+2
    T=[]
    def rec(occ,cur):
        p=next((i for i in range(R*C) if not occ>>i&1),None)
        if p is None: T.append(frozenset(cur)); return
        r,c=divmod(p,C)
        if c+1<C and not occ>>(p+1)&1: rec(occ|1<<p|1<<(p+1),cur+[('h',r,c)])
        if r+1<R: rec(occ|1<<p|1<<(p+C),cur+[('v',r,c)])
    rec(0,[])
    idx={t:i for i,t in enumerate(T)}
    def pieces(t):
        out=[]
        for k,r,c in t:
            a=g[r][c]; b=g[r][c+1] if k=='h' else g[r+1][c]
            out.append((min(a,b),max(a,b)))
        return out
    issol=[len(set(pieces(t)))==len(t) for t in T]
    bad=[(r,c) for r in range(R-1) for c in range(C-1) if not (g[r][c]==g[r+1][c+1] or g[r][c+1]==g[r+1][c])]
    par=list(range(len(T)))
    def f(x):
        while par[x]!=x: par[x]=par[par[x]]; x=par[x]
        return x
    for i,t in enumerate(T):
        for r in range(R-1):
            for c in range(C-1):
                if ('h',r,c) in t and ('h',r+1,c) in t and (r,c) not in bad:
                    u=(t-{('h',r,c),('h',r+1,c)})|{('v',r,c),('v',r,c+1)}
                    j=idx[u]; par[f(i)]=f(j)
    from collections import Counter
    sz=Counter(f(i) for i in range(len(T))); so=Counter(f(i) for i in range(len(T)) if issol[i])
    allh=frozenset(('h',r,c) for r in range(R) for c in range(0,C,2)) if C%2==0 else None
    allv=frozenset(('v',r,c) for r in range(0,R,2) for c in range(C)) if R%2==0 else None
    nice=[]
    if allh in idx: nice.append(('all-horizontal',issol[idx[allh]]))
    if allv in idx: nice.append(('all-vertical',issol[idx[allv]]))
    print(f"{s}: n={n} tilings={len(T)} solutions={sum(issol)} bad={bad} classes={sorted(sz.values(),reverse=True)} solclasses={[sz[k] for k in so]} mixed={any(so[k]!=sz[k] for k in so)} nice={nice}")
for s in sys.argv[1:]: analyse(s)
