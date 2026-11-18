# bound(B) = |R| - nu(H_B restricted to R), R = union of individually realizable components of G_B.
# usage: python3 rbound.py SET [SET ...]
import sys, os, subprocess
HERE = os.path.dirname(os.path.abspath(__file__))
from satb2 import solve
for Bs in sys.argv[1:]:
    B=set(int(x) for x in Bs.split(','))
    out=subprocess.run([os.path.join(HERE,'bsearch'),'listall','1'],input=Bs+'\n',capture_output=True,text=True).stdout.split()
    comps=[tuple(int(x,16) if k else int(x) for k,x in enumerate(c.split(':'))) for c in out[4:]]
    R=[c for c in comps if solve(B,c[1],c[2])]
    inp=Bs+'\n'+''.join('%x %x\n'%(h,v) for _,h,v in R)
    res=subprocess.run([os.path.join(HERE,'ubr'),'restrict'],input=inp,capture_output=True,text=True).stdout.strip()
    print(Bs,'realizable comps',len(R),'sum',sum(c[0] for c in R),res,flush=True)
