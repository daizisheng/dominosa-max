# Independent SAT encoding (domino-assignment based) of realizability of (B, T):
# primary vars P[d][t][o]: domino d of T carries type t in orientation o; a permutation of the 28 types.
# Cell values are derived; every block outside B must be good (a=d or b=c). Solver: Glucose4 (different from satb2's CaDiCaL).
# usage: same as satb2.py
import sys, itertools, time
from pysat.solvers import Glucose4
def solve(B,H,V):
    nv=[0]
    def new(): nv[0]+=1; return nv[0]
    D=[(i,i+1) for i in range(56) if H>>i&1]+[(i,i+8) for i in range(56) if V>>i&1]
    types=[(a,b) for a in range(7) for b in range(a,7)]
    cl=[]
    P={}
    for d in range(28):
        for t,(a,b) in enumerate(types):
            for o in ((0,) if a==b else (0,1)): P[d,t,o]=new()
    for d in range(28):
        lits=[P[k] for k in P if k[0]==d]; cl.append(lits)
        for x,y in itertools.combinations(lits,2): cl.append([-x,-y])
    for t in range(28):
        lits=[P[k] for k in P if k[1]==t]; cl.append(lits)
        for x,y in itertools.combinations(lits,2): cl.append([-x,-y])
    # derived cell values
    owner={}
    for d,(i,j) in enumerate(D): owner[i]=(d,0); owner[j]=(d,1)
    Xv=[[new() for v in range(7)] for i in range(56)]
    for i in range(56):
        d,end=owner[i]
        for v in range(7):
            sup=[]
            for (dd,t,o),p in P.items():
                if dd!=d: continue
                a,b=types[t]; val=(a,b)[(end+o)%2] if a!=b else a
                if val==v: sup.append(p)
            # Xv[i][v] <-> OR sup
            cl.append([-Xv[i][v]]+sup)
            for p in sup: cl.append([-p,Xv[i][v]])
    for r in range(6):
        for c in range(7):
            if r*7+c in B: continue
            i=r*8+c
            # (g[i]==g[i+9]) or (g[i+1]==g[i+8]); via aux
            e1,e2=new(),new(); cl.append([e1,e2])
            for e,p,q in ((e1,i,i+9),(e2,i+1,i+8)):
                for v in range(7): cl.append([-e,-Xv[p][v],Xv[q][v]])
    with Glucose4(bootstrap_with=cl) as s:
        if s.solve():
            m=set(l for l in s.get_model() if l>0)
            g=[next(v for v in range(7) if Xv[i][v] in m) for i in range(56)]
            return '/'.join(''.join(map(str,g[r*8:r*8+8])) for r in range(7))
        return None
if __name__=='__main__':
    for line in sys.stdin:
        p=line.split()
        if not p or p[0]!='B': continue
        B=set(int(x) for x in p[1].split(',')) if p[1]!='-' else set()
        t0=time.time(); a=solve(B,int(p[5][1:],16),int(p[6][1:],16))
        print('SAT' if a else 'UNSAT',p[1],p[3],a,'%.1fs'%(time.time()-t0),flush=True)
