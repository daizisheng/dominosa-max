# hcheck.py -- test of Lemma 5: classes of tilings under flips in blocks outside S == level sets of the
# heights at the centres of the S-blocks (random S, n = 2..5); also checks that a flip in block b changes
# the height only at the centre of b, by +-4.   usage: python3 hcheck.py
import sys, random, itertools
sys.setrecursionlimit(100000)
def tilings(R,C):
    T=[]
    def rec(occ,cur):
        p=next((i for i in range(R*C) if not occ>>i&1),None)
        if p is None: T.append(frozenset(cur)); return
        r,c=divmod(p,C)
        if c+1<C and not occ>>(p+1)&1: rec(occ|1<<p|1<<(p+1),cur+[('h',r,c)])
        if r+1<R: rec(occ|1<<p|1<<(p+C),cur+[('v',r,c)])
    rec(0,[]); return T
def height(t,r,c):
    # vertex (r,c) of the grid, 1<=r<=R-1, 1<=c<=C-1 ; sum along vertical line c from the top
    h=0
    for i in range(r):
        crossed=('h',i,c-1) in t
        s=1 if (i+c)%2==0 else -1
        h+= s*(-3 if crossed else 1)
    return h
def check(n,trials,seed=1):
    R,C=n+1,n+2; T=tilings(R,C); idx={t:i for i,t in enumerate(T)}
    blocks=[(r,c) for r in range(R-1) for c in range(C-1)]
    # flip adjacency per block
    adj={b:[] for b in blocks}
    for i,t in enumerate(T):
        for (r,c) in blocks:
            if ('h',r,c) in t and ('h',r+1,c) in t:
                u=(t-{('h',r,c),('h',r+1,c)})|{('v',r,c),('v',r,c+1)}
                adj[(r,c)].append((i,idx[u]))
    # sanity: a flip in block b changes height only at its centre (r+1,c+1)
    verts=[(r,c) for r in range(1,R) for c in range(1,C)]
    H=[{v:height(t,*v) for v in verts} for t in T]
    for (r,c),E in adj.items():
        for i,j in E:
            diff=[v for v in verts if H[i][v]!=H[j][v]]
            assert diff==[(r+1,c+1)] and abs(H[i][(r+1,c+1)]-H[j][(r+1,c+1)])==4, ((r,c),diff)
    rnd=random.Random(seed); bad=0; tested=0
    sets=[()]+[ (b,) for b in blocks]
    for _ in range(trials):
        k=rnd.randint(2,min(len(blocks),8)); sets.append(tuple(rnd.sample(blocks,k)))
    for S in sets:
        par=list(range(len(T)))
        def f(x):
            while par[x]!=x: par[x]=par[par[x]]; x=par[x]
            return x
        for b in blocks:
            if b in S: continue
            for i,j in adj[b]: par[f(i)]=f(j)
        cls={}
        for i in range(len(T)): cls.setdefault(f(i),set()).add(i)
        lev={}
        for i in range(len(T)): lev.setdefault(tuple(H[i][(r+1,c+1)] for (r,c) in S),set()).add(i)
        A=sorted(map(sorted,cls.values())); B=sorted(map(sorted,lev.values()))
        tested+=1
        if A!=B: bad+=1; print('MISMATCH',n,S,len(A),len(B))
    print(f"n={n}: tilings={len(T)} flip-height sanity ok; sets tested={tested}, mismatches={bad}")
    return bad
if __name__=='__main__':
    sys.exit(1 if sum(check(n,tr) for n,tr in ((2,200),(3,500),(4,300),(5,40))) else 0)
