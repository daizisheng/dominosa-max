# SAT encoding (CaDiCaL) for realizability of (B, T): every block outside B good; tiling T gets all 28 types.
# usage: python3 satb2.py < lines "B set max size rep Hhex Vhex" (output of bsearch enum/list)
import sys, itertools, time
from pysat.solvers import Cadical153
from pysat.card import CardEnc, EncType
def build(B, H, V):
    nv=[0]
    def new(): nv[0]+=1; return nv[0]
    X=[[new() for v in range(7)] for i in range(56)]
    cl=[]
    for i in range(56):
        cl.append(X[i][:])
        for a,b in itertools.combinations(X[i],2): cl.append([-a,-b])
    cl.append([X[0][0]])
    for r in range(6):
        for c in range(7):
            if r*7+c in B: continue
            i=r*8+c; a,b,cc,d=i,i+1,i+8,i+9
            e1,e2=new(),new(); cl.append([e1,e2])
            for (e,p,q) in ((e1,a,d),(e2,b,cc)):
                for v in range(7):
                    cl.append([-e,-X[p][v],X[q][v]]); cl.append([-e,X[p][v],-X[q][v]])
    D=[(i,i+1) for i in range(56) if H>>i&1]+[(i,i+8) for i in range(56) if V>>i&1]
    assert len(D)==28
    types=[(a,b) for a in range(7) for b in range(a,7)]
    Y=[[new() for t in types] for d in D]
    for di,(i,j) in enumerate(D):
        for ti,(a,b) in enumerate(types):
            y=Y[di][ti]
            cl.append([-X[i][a],-X[j][b],y]); cl.append([-X[i][b],-X[j][a],y])
            if a==b: cl.append([-y,X[i][a]]); cl.append([-y,X[j][a]])
            else:
                cl.append([-y,X[i][a],X[i][b]]); cl.append([-y,X[j][a],X[j][b]])
                cl.append([-y,-X[i][a],-X[j][a]]); cl.append([-y,-X[i][b],-X[j][b]])
    for ti in range(28):
        col=[Y[di][ti] for di in range(28)]
        cl.append(col)
        for a,b in itertools.combinations(col,2): cl.append([-a,-b])
    for di in range(28):
        cl.append(Y[di][:])
    for v in range(7):
        enc=CardEnc.equals(lits=[X[i][v] for i in range(56)],bound=8,top_id=nv[0],encoding=EncType.seqcounter)
        nv[0]=max(nv[0],enc.nv); cl.extend(enc.clauses)
    return X,cl
def solve(B,H,V):
    X,cl=build(B,H,V)
    with Cadical153(bootstrap_with=cl) as s:
        if s.solve():
            m=set(l for l in s.get_model() if l>0)
            g=[next(v for v in range(7) if X[i][v] in m) for i in range(56)]
            return '/'.join(''.join(map(str,g[r*8:r*8+8])) for r in range(7))
        return None
if __name__=='__main__':
    for line in sys.stdin:
        p=line.split()
        if not p or p[0]!='B': continue
        B=set(int(x) for x in p[1].split(',')) if p[1]!='-' else set()
        t0=time.time(); a=solve(B,int(p[5][1:],16),int(p[6][1:],16))
        print('SAT' if a else 'UNSAT',p[1],p[3],a,'%.1fs'%(time.time()-t0),flush=True)
