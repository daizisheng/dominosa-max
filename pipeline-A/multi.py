# For a bad-block set B: start from its largest component and greedily try to make additional components
# simultaneously valid (one array, all chosen components' representative tilings using all 28 dominoes).
# solve_multi() is the joint realizability test used by joint.py.
# usage: python3 multi.py SET [SET ...]
import sys, os, subprocess, itertools, time
HERE = os.path.dirname(os.path.abspath(__file__))
from pysat.solvers import Cadical153
from pysat.card import CardEnc, EncType
def solve_multi(B, tilings):
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
            i=r*8+c; e1,e2=new(),new(); cl.append([e1,e2])
            for (e,p,q) in ((e1,i,i+9),(e2,i+1,i+8)):
                for v in range(7):
                    cl.append([-e,-X[p][v],X[q][v]]); cl.append([-e,X[p][v],-X[q][v]])
    types=[(a,b) for a in range(7) for b in range(a,7)]
    for (H,V) in tilings:
        D=[(i,i+1) for i in range(56) if H>>i&1]+[(i,i+8) for i in range(56) if V>>i&1]
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
            col=[Y[di][ti] for di in range(28)]; cl.append(col)
            for a,b in itertools.combinations(col,2): cl.append([-a,-b])
    for v in range(7):
        enc=CardEnc.equals(lits=[X[i][v] for i in range(56)],bound=8,top_id=nv[0],encoding=EncType.seqcounter)
        nv[0]=max(nv[0],enc.nv); cl.extend(enc.clauses)
    with Cadical153(bootstrap_with=cl) as s:
        if s.solve():
            m=set(l for l in s.get_model() if l>0)
            g=[next(v for v in range(7) if X[i][v] in m) for i in range(56)]
            return '/'.join(''.join(map(str,g[r*8:r*8+8])) for r in range(7))
    return None
def comps(Bs,K=60):
    out=subprocess.run([os.path.join(HERE,'bsearch'),'one',Bs,str(K)],capture_output=True,text=True).stdout
    res=[]
    for line in out.split('\n'):
        p=line.split()
        if p and p[0]=='comp': res.append((int(p[3]),int(p[5][1:],16),int(p[6][1:],16)))
    return res
if __name__=='__main__':
    for Bs in sys.argv[1:]:
        B=set(int(x) for x in Bs.split(','))
        cs=comps(Bs)
        chosen=[cs[0]]; arr=solve_multi(B,[(h,v) for _,h,v in chosen])
        if not arr: print(Bs,'largest comp',cs[0][0],'UNREALIZABLE',flush=True); continue
        for c in cs[1:]:
            a=solve_multi(B,[(h,v) for _,h,v in chosen+[c]])
            if a: chosen.append(c); arr=a
        print(Bs,'chosen sizes',[c[0] for c in chosen],'sum',sum(c[0] for c in chosen),arr,flush=True)
