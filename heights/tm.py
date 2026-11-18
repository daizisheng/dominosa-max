# tm.py -- class sizes of G_S (flips in blocks outside S) by a transfer matrix over the columns, keeping
# the heights at the centres of the S-blocks (Lemma 5).  class_sizes(n, S) with S a list of blocks (r,c).
# usage: python3 tm.py      (A*, Gonzalez-Morris, n=5 optimum, and timing examples for n = 7, 8, 9)
import sys, time
from collections import defaultdict
def col_transitions(R):
    # from incoming mask (cells of this column already covered by horizontals from the left)
    # to outgoing mask (rows where a horizontal domino leaves this column to the right)
    trans=defaultdict(list)
    def rec(r,cur,out,inm):
        if r==R: trans[inm].append(out); return
        if cur>>r&1: rec(r+1,cur,out,inm); return
        rec(r+1,cur|1<<r,out|1<<r,inm)            # horizontal to the right
        if r+1<R and not cur>>(r+1)&1: rec(r+2,cur|1<<r|1<<(r+1),out,inm)  # vertical
    for m in range(1<<R): rec(0,m,0,m)
    return trans
def heights_on_line(mask,c,rows,R):
    # heights at vertices (r,c), r in rows, from crossing mask on vertical line c
    out=[];
    for r in rows:
        h=0
        for i in range(r):
            s=1 if (i+c)%2==0 else -1
            h+= s*(-3 if mask>>i&1 else 1)
        out.append(h)
    return tuple(out)
def class_sizes(n,S):
    R,C=n+1,n+2
    trans=col_transitions(R)
    # S blocks (r,c) -> centre vertex (r+1,c+1) on vertical line c+1
    lines=defaultdict(list)
    for (r,c) in S: lines[c+1].append(r+1)
    for k in lines: lines[k].sort()
    dp={(0,()):1}
    for col in range(C):
        nd=defaultdict(int)
        for (m,hs),cnt in dp.items():
            for out in trans[m]:
                if col==C-1 and out!=0: continue
                key=hs
                line=col+1
                if line in lines: key=hs+heights_on_line(out,line,lines[line],R)
                nd[(out,key)]+=cnt
        dp=nd
    res=defaultdict(int)
    for (m,hs),cnt in dp.items():
        assert m==0; res[hs]+=cnt
    return sorted(res.values(),reverse=True)
if __name__=='__main__':
    t=time.time()
    S=[(1,3),(2,1),(2,5),(4,3)]
    cs=class_sizes(6,S); print('n=6 A* bad set: classes',len(cs),'total',sum(cs),'top',cs[:5],f'{time.time()-t:.2f}s')
    t=time.time()
    S=[(1,3),(2,1),(2,5),(4,3),(4,5)]
    cs=class_sizes(6,S); print('n=6 Gonzalez-Morris bad set: classes',len(cs),'top',cs[:4],f'{time.time()-t:.2f}s')
    print('n=5 {7,10,20}:',class_sizes(5,[(1,1),(1,4),(3,2)])[:5])
    for n,S in ((7,[(1,1),(2,3),(3,5),(4,2),(5,4)]),(8,[(1,1),(2,3),(3,5),(4,2),(5,4),(6,6)]),(9,[(1,1),(2,3),(3,5),(4,2),(5,4),(6,6),(7,8)])):
        t=time.time(); cs=class_sizes(n,S); print(f'n={n}: total={sum(cs)} classes={len(cs)} top={cs[:3]} {time.time()-t:.2f}s')
