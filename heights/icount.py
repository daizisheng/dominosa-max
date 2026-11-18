# icount.py -- I(S): number of tilings with no block of S filled by two parallel dominoes, by a column
# transfer matrix.  usage: python3 icount.py   (checks I against brute force for n = 3..5)
import time
from collections import defaultdict
from functools import lru_cache
def make(R):
    trans=defaultdict(list)   # in_mask -> list of (out_mask, vstarts)
    def rec(r,cur,out,vs,inm):
        if r==R: trans[inm].append((out,vs)); return
        if cur>>r&1: rec(r+1,cur,out,vs,inm); return
        rec(r+1,cur|1<<r,out|1<<r,vs,inm)
        if r+1<R and not cur>>(r+1)&1: rec(r+2,cur|1<<r|1<<(r+1),out,vs|1<<r,inm)
    for m in range(1<<R): rec(0,m,0,0,m)
    return trans
def I_count(n,S):
    R,C=n+1,n+2; trans=make(R)
    bycol=defaultdict(list)
    for (r,c) in S: bycol[c].append(r)   # block (r,c) spans columns c, c+1
    dp={(0,0):1}   # (in_mask of current column, vstarts of previous column restricted)
    for col in range(C):
        nd=defaultdict(int)
        for (m,vprev),cnt in dp.items():
            for out,vs in trans[m]:
                if col==C-1 and out: continue
                ok=True
                # blocks (r,col-1): need vprev (column col-1) and vs (column col)
                for r in bycol.get(col-1,()):
                    if (vprev>>r&1) and (vs>>r&1): ok=False;break
                if not ok: continue
                # blocks (r,col): horizontals crossing line col+1 at rows r and r+1  <=> out bits r, r+1
                for r in bycol.get(col,()):
                    if (out>>r&1) and (out>>(r+1)&1): ok=False;break
                if not ok: continue
                keep=0
                for r in bycol.get(col,()): keep|=vs&(1<<r)
                nd[(out,keep)]+=cnt
        dp=nd
    return sum(dp.values())
if __name__=='__main__':
    from hcheck import tilings
    import random
    rnd=random.Random(5)
    total=0
    for n in (3,4,5):
        R,C=n+1,n+2; T=tilings(R,C); blocks=[(r,c) for r in range(R-1) for c in range(C-1)]
        bad=0
        for _ in range(40):
            S=rnd.sample(blocks,rnd.randint(1,6))
            brute=sum(1 for t in T if not any((('h',r,c) in t and ('h',r+1,c) in t) or (('v',r,c) in t and ('v',r,c+1) in t) for (r,c) in S))
            if brute!=I_count(n,S): bad+=1
        print('n',n,'I mismatches',bad); total+=bad
    for n in (7,8,9):
        S=[(1,1),(2,3),(3,5),(4,2),(5,4)]
        t=time.time(); print(n,I_count(n,S),f'{time.time()-t:.2f}s')
    import sys; sys.exit(1 if total else 0)
