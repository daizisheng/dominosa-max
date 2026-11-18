"""Core combinatorics for double-n Dominosa on an (n+1) x (n+2) board.

Cells: r*C + c (row-major), R = n+1 rows, C = n+2 columns.
Domino: (p, q) with p < q (q = p+1 horizontal, q = p+C vertical).
Block b = r*(C-1) + c, 0 <= r < R-1, 0 <= c < C-1, with cells
    a=(r,c)  b=(r,c+1)
    c=(r+1,c) d=(r+1,c+1)
A block is good for array A iff A[a]==A[d] or A[b]==A[c].
"""
import itertools, sys
from functools import lru_cache


class Board:
    def __init__(self, n):
        self.n = n
        self.R = R = n + 1
        self.C = C = n + 2
        self.N = R * C
        self.K = (n + 1) * (n + 2) // 2          # number of pieces
        self.nblocks = (R - 1) * (C - 1)
        self.tilings = self._tilings()           # list of tuples of dominoes (sorted)
        self.T = len(self.tilings)
        self.index = {t: i for i, t in enumerate(self.tilings)}
        self.edges = self._edges()               # list of (i, j, b): i has the 2 horizontals in b
        # parity (bipartition) of tilings: number of vertical dominoes in even rows? use
        # BFS 2-colouring as a check that the flip graph is bipartite
        self.color = self._two_colour()

    # ---- geometry
    def block_cells(self, b):
        C = self.C
        r, c = divmod(b, C - 1)
        p = r * C + c
        return p, p + 1, p + C, p + C + 1       # a, b, c, d

    def rc(self, p):
        return divmod(p, self.C)

    def _tilings(self):
        R, C, N = self.R, self.C, self.N
        out = []
        occ = [False] * N
        cur = []

        def rec(p):
            while p < N and occ[p]:
                p += 1
            if p == N:
                out.append(tuple(sorted(cur)))
                return
            r, c = divmod(p, C)
            if c + 1 < C and not occ[p + 1]:
                occ[p] = occ[p + 1] = True
                cur.append((p, p + 1))
                rec(p + 1)
                cur.pop()
                occ[p] = occ[p + 1] = False
            if r + 1 < R:
                occ[p] = occ[p + C] = True
                cur.append((p, p + C))
                rec(p + 1)
                cur.pop()
                occ[p] = occ[p + C] = False
        rec(0)
        out.sort()
        return out

    def _edges(self):
        E = []
        for i, t in enumerate(self.tilings):
            s = set(t)
            for b in range(self.nblocks):
                a, bb, c, d = self.block_cells(b)
                if (a, bb) in s and (c, d) in s:
                    s2 = (s - {(a, bb), (c, d)}) | {(a, c), (bb, d)}
                    j = self.index[tuple(sorted(s2))]
                    E.append((i, j, b))
        return E

    def _two_colour(self):
        adj = [[] for _ in range(self.T)]
        for i, j, b in self.edges:
            adj[i].append(j)
            adj[j].append(i)
        col = [-1] * self.T
        col[0] = 0
        st = [0]
        while st:
            u = st.pop()
            for v in adj[u]:
                if col[v] < 0:
                    col[v] = 1 - col[u]
                    st.append(v)
                elif col[v] == col[u]:
                    raise RuntimeError("flip graph not bipartite")
        assert min(col) >= 0, "flip graph not connected"
        return col

    # ---- symmetries of the rectangle (identity, lr, ud, rot180)
    def cell_syms(self):
        R, C = self.R, self.C
        res = []
        for fr in (False, True):
            for fc in (False, True):
                m = []
                for p in range(self.N):
                    r, c = divmod(p, C)
                    r2 = R - 1 - r if fr else r
                    c2 = C - 1 - c if fc else c
                    m.append(r2 * C + c2)
                res.append(m)
        return res

    def block_syms(self):
        R, C = self.R, self.C
        res = []
        for fr in (False, True):
            for fc in (False, True):
                m = []
                for b in range(self.nblocks):
                    r, c = divmod(b, C - 1)
                    r2 = R - 2 - r if fr else r
                    c2 = C - 2 - c if fc else c
                    m.append(r2 * (C - 1) + c2)
                res.append(m)
        return res

    # ---- arrays
    def parse(self, s):
        rows = s.split('/')
        assert len(rows) == self.R and all(len(x) == self.C for x in rows), s
        return [int(ch) for row in rows for ch in row]

    def fmt(self, A):
        C = self.C
        return '/'.join(''.join(str(A[r * C + c]) for c in range(C)) for r in range(self.R))

    def bad_blocks(self, A):
        out = []
        for b in range(self.nblocks):
            a, bb, c, d = self.block_cells(b)
            if not (A[a] == A[d] or A[bb] == A[c]):
                out.append(b)
        return out

    def is_solution(self, A, t):
        seen = set()
        for p, q in t:
            x, y = A[p], A[q]
            k = (min(x, y), max(x, y))
            if k in seen:
                return False
            seen.add(k)
        return True

    def solutions(self, A):
        return [i for i, t in enumerate(self.tilings) if self.is_solution(A, t)]

    def classes(self, Bset):
        """Connected components of the flip graph restricted to blocks NOT in Bset."""
        par = list(range(self.T))

        def find(x):
            while par[x] != x:
                par[x] = par[par[x]]
                x = par[x]
            return x
        for i, j, b in self.edges:
            if b not in Bset:
                ri, rj = find(i), find(j)
                if ri != rj:
                    par[ri] = rj
        comp = {}
        for i in range(self.T):
            comp.setdefault(find(i), []).append(i)
        cl = sorted(comp.values(), key=lambda c: (-len(c), c[0]))
        return cl

    def matching_bound(self, Bset):
        """T - nu(H_B), H_B = flip edges in blocks of Bset (Hopcroft-Karp)."""
        import networkx as nx
        from networkx.algorithms import bipartite
        G = nx.Graph()
        left = [i for i in range(self.T) if self.color[i] == 0]
        G.add_nodes_from(range(self.T))
        for i, j, b in self.edges:
            if b in Bset:
                G.add_edge(i, j)
        if G.number_of_edges() == 0:
            return self.T
        M = bipartite.hopcroft_karp_matching(G, top_nodes=[v for v in left])
        return self.T - len(M) // 2


def canon_relabel(A):
    """first-occurrence relabeling"""
    mp = {}
    out = []
    for v in A:
        if v not in mp:
            mp[v] = len(mp)
        out.append(mp[v])
    return tuple(out)


def canon_full(bd, A):
    """canonical form under 4 board symmetries x value relabelings: lexicographically
    smallest first-occurrence relabeling over the 4 symmetric images."""
    best = None
    for m in bd.cell_syms():
        B = [0] * bd.N
        for p in range(bd.N):
            B[m[p]] = A[p]
        c = canon_relabel(B)
        if best is None or c < best:
            best = c
    return best


if __name__ == '__main__':
    for n in range(1, 6):
        bd = Board(n)
        print(n, bd.R, 'x', bd.C, 'tilings', bd.T, 'edges', len(bd.edges), 'blocks', bd.nblocks)
        sys.stdout.flush()
