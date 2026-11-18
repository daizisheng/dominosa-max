# For a bad set B: find the maximum total size of a set of G_B components that are simultaneously realizable
# (one array, every block outside B good, each chosen component's representative tiling valid).
# Branch and bound over the individually realizable components, largest first.
# usage: python3 joint.py THR SET [SET ...]      (SET = comma-separated block ids)
import sys, os, subprocess
HERE = os.path.dirname(os.path.abspath(__file__))
from multi import solve_multi
from satb2 import solve
THR=int(sys.argv[1])
def allcomps(Bs):
    out=subprocess.run([os.path.join(HERE,'bsearch'),'listall','1'],input=Bs+'\n',capture_output=True,text=True).stdout
    p=out.split()
    return [tuple(int(x,16) if k else int(x) for k,x in enumerate(c.split(':'))) for c in p[4:]]
for Bs in sys.argv[2:]:
    B=set(int(x) for x in Bs.split(','))
    cs=allcomps(Bs)
    R=[c for c in cs if solve(B,c[1],c[2])]
    print(Bs,'components',len(cs),'individually realizable',len(R),[c[0] for c in R],flush=True)
    best=[0,None,None]; calls=[0]
    suffix=[0]*(len(R)+1)
    for i in range(len(R)-1,-1,-1): suffix[i]=suffix[i+1]+R[i][0]
    def dfs(i,chosen,tot,arr):
        if tot>best[0]: best[0]=tot; best[1]=[c[0] for c in chosen]; best[2]=arr
        if i==len(R) or tot+suffix[i]<=best[0]: return
        calls[0]+=1
        a=solve_multi(B,[(h,v) for _,h,v in chosen+[R[i]]])
        if a: dfs(i+1,chosen+[R[i]],tot+R[i][0],a)
        dfs(i+1,chosen,tot,arr)
    dfs(0,[],0,None)
    print(Bs,'MAX joint',best[0],best[1],best[2],'jointcalls',calls[0],'OK' if best[0]<=THR else 'EXCEEDS',flush=True)
