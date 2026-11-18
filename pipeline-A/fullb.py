# Full bound for each bad set B (including multi-component solution sets):
# #solutions(A) <= sum of sizes of the G_B-components that are individually realizable (SAT) for B.
# Components are checked in decreasing size until the bound drops to <= THR.
# usage: python3 fullb.py THR [satb3] < lines "S set ncomp rest size:H:V ..." (output of bsearch listall 1)
#        with the optional argument satb3 the second, independent encoding is used.
import sys
if len(sys.argv)>2 and sys.argv[2]=='satb3': from satb3 import solve
else: from satb2 import solve
THR=int(sys.argv[1])
for line in sys.stdin:
    p=line.split()
    if not p or p[0]!='S': continue
    Bs=p[1]; B=set(int(x) for x in Bs.split(',')) if Bs!='-' else set()
    rest=int(p[3]); comps=[tuple(int(x,16) if k else int(x) for k,x in enumerate(c.split(':'))) for c in p[4:]]
    unchecked=sum(c[0] for c in comps); real=0; nsat=0; realizable=[]
    for (s,h,v) in comps:
        if real+unchecked+rest<=THR: break
        unchecked-=s; nsat+=1
        if solve(B,h,v): real+=s; realizable.append(s)
    bound=real+unchecked+rest
    print('OK' if bound<=THR else 'OPEN',Bs,'bound',bound,'realizable',realizable[:10],'satcalls',nsat,flush=True)
