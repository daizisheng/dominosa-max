# enumerate arrays realizing (B,T) via SAT with blocking clauses; report distinct canonical forms and counts
# usage: python3 enumrec.py SET Hhex Vhex LIMIT OUTFILE     (Hhex, Vhex as printed by 'bsearch one', e.g. H55555555550101)
# OUTFILE receives one line "count array" per canonical form found.
import sys
from pysat.solvers import Cadical153
from satb2 import build
from canon import canon
import subprocess, os
HERE = os.path.dirname(os.path.abspath(__file__))
B=set(int(x) for x in sys.argv[1].split(',')); H=int(sys.argv[2][1:],16); V=int(sys.argv[3][1:],16); lim=int(sys.argv[4])
X,cl=build(B,H,V); seen={}
with Cadical153(bootstrap_with=cl) as s:
    n=0
    while n<lim and s.solve():
        m=set(l for l in s.get_model() if l>0)
        g=[next(v for v in range(7) if X[i][v] in m) for i in range(56)]
        s.add_clause([-X[i][g[i]] for i in range(56)]); n+=1
        a='/'.join(''.join(map(str,g[r*8:r*8+8])) for r in range(7)); c=canon(a)
        seen.setdefault(c,a)
print('solutions',n,'distinct canonical',len(seen))
arrs=list(seen.values())
out=subprocess.run([os.path.join(HERE,'..','count','cntf')],input='\n'.join(arrs)+'\n',capture_output=True,text=True).stdout
open(sys.argv[5],'w').write(out)
from collections import Counter
print(Counter(int(l.split()[0]) for l in out.strip().split('\n')))

