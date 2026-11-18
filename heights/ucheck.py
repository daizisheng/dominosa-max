# Check: for S whose block centres are pairwise non-adjacent, alpha(H_S) = T - nu(H_S) = (T + I)/2,
# I = number of tilings in which no block of S is filled by two parallel dominoes.   usage: python3 ucheck.py
import random, sys
from hcheck import tilings
import networkx as nx
def run(n,trials,seed=3):
    R,C=n+1,n+2; T=tilings(R,C); idx={t:i for i,t in enumerate(T)}
    blocks=[(r,c) for r in range(R-1) for c in range(C-1)]
    def flippable(t,b):
        r,c=b
        return (('h',r,c) in t and ('h',r+1,c) in t) or (('v',r,c) in t and ('v',r,c+1) in t)
    rnd=random.Random(seed); bad=0; done=0; adjbad=0
    for _ in range(trials):
        k=rnd.randint(1,min(8,len(blocks)))
        S=rnd.sample(blocks,k)
        adjacent=any((a[0]==b[0] and abs(a[1]-b[1])==1) or (a[1]==b[1] and abs(a[0]-b[0])==1) for a in S for b in S if a<b)
        G=nx.Graph(); G.add_nodes_from(range(len(T)))
        for i,t in enumerate(T):
            for (r,c) in S:
                if ('h',r,c) in t and ('h',r+1,c) in t:
                    u=(t-{('h',r,c),('h',r+1,c)})|{('v',r,c),('v',r,c+1)}
                    G.add_edge(i,idx[u])
        nu=len(nx.max_weight_matching(G,maxcardinality=True))
        I=sum(1 for t in T if not any(flippable(t,b) for b in S))
        lhs=len(T)-nu; rhs=(len(T)+I)/2
        done+=1
        if not adjacent and lhs!=rhs: bad+=1; print('MISMATCH',S,lhs,rhs)
        if adjacent and lhs>rhs: adjbad+=1
    print(f"n={n}: sets {done}, nonadjacent mismatches {bad}, adjacent sets where (T+I)/2 is NOT an upper bound: {adjbad}")
    return bad
if __name__=='__main__':
    sys.exit(1 if sum(run(n,tr) for n,tr in ((3,300),(4,150))) else 0)
