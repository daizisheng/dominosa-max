"""Two independent SAT encodings of realizability (Lemma 3).

Question: given a set Bset of blocks that may be bad and tilings t_1..t_m, is there an
array A (values 0..n, cell 0 has value 0 w.l.o.g. by relabeling) such that every block
outside Bset is good and every t_i is a solution?

Enc1 (CaDiCaL):  one-hot cells x[p][v]; per good block two equality selectors
   e_ad, e_bc with e_ad v e_bc; per tiling and domino d and piece k a variable
   y[d][k] <-> "domino d carries piece k" (unordered, no orientation variable), and for
   every piece k: OR_d y[d][k] plus pairwise AMO.
   (K dominoes cover all K pieces => bijection.)  Optional: exact value counts.
Enc2 (Glucose4/Minisat22): one-hot cells; good blocks by direct forbidding clauses
   (not x[a]=va or not x[d]=vd or not x[b]=vb or not x[c]=vc for va!=vd, vb!=vc);
   per tiling: z[d][k][o] = domino d gets piece k in orientation o, exactly one per
   domino (pairwise AMO), exactly one per piece, z -> cell values.

Both support selector literals (one per tiling group) so that several queries can be
answered with assumptions on one incremental solver.
"""
from pysat.solvers import Solver
from pysat.card import CardEnc, EncType


class _Vars:
    def __init__(self):
        self.top = 0

    def new(self):
        self.top += 1
        return self.top


def pieces(n):
    return [(i, j) for j in range(n + 1) for i in range(j + 1)]


class Enc1:
    def __init__(self, bd, Bset, solver='cadical153', exact_bad=False, canon=False, counts=True):
        self.bd = bd
        n = bd.n
        self.V = V = _Vars()
        self.cl = cl = []
        self.x = [[V.new() for v in range(n + 1)] for p in range(bd.N)]
        for p in range(bd.N):
            cl.append(self.x[p][:])
            for v in range(n + 1):
                for w in range(v + 1, n + 1):
                    cl.append([-self.x[p][v], -self.x[p][w]])
        cl.append([self.x[0][0]])
        if canon:   # first-occurrence canonical form: value v>=1 only after v-1 occurred
            for p in range(bd.N):
                for v in range(1, n + 1):
                    cl.append([-self.x[p][v]] + [self.x[q][v - 1] for q in range(p)])
        if counts:
            for v in range(n + 1):
                enc = CardEnc.equals([self.x[p][v] for p in range(bd.N)], bound=n + 2,
                                     top_id=V.top, encoding=EncType.seqcounter)
                V.top = max(V.top, enc.nv)
                cl.extend(enc.clauses)
        for b in range(bd.nblocks):
            a, bb, c, d = bd.block_cells(b)
            if b in Bset:
                if exact_bad:  # block must be bad: x[a]!=x[d] and x[bb]!=x[c]
                    for v in range(n + 1):
                        cl.append([-self.x[a][v], -self.x[d][v]])
                        cl.append([-self.x[bb][v], -self.x[c][v]])
                continue
            e1, e2 = V.new(), V.new()
            cl.append([e1, e2])
            for (e, u, w) in ((e1, a, d), (e2, bb, c)):
                for v in range(n + 1):
                    cl.append([-e, -self.x[u][v], self.x[w][v]])
                    cl.append([-e, self.x[u][v], -self.x[w][v]])
        self.S = Solver(name=solver, bootstrap_with=cl)
        self.sel = {}

    def add_tiling(self, key, t):
        """add constraints 't is a solution', guarded by selector literal for key"""
        n = self.bd.n
        V, x = self.V, self.x
        s = V.new()
        self.sel[key] = s
        P = pieces(n)
        cls = []
        ys = {k: [] for k in range(len(P))}
        for (p, q) in t:
            yd = []
            for k, (i, j) in enumerate(P):
                y = V.new()
                ys[k].append(y)
                yd.append(y)
                if i == j:
                    cls.append([-y, x[p][i]])
                    cls.append([-y, x[q][i]])
                    cls.append([y, -x[p][i], -x[q][i]])          # y <- carries
                else:
                    cls.append([-y, x[p][i], x[p][j]])
                    cls.append([-y, x[q][i], x[q][j]])
                    cls.append([-y, -x[p][i], x[q][j]])
                    cls.append([-y, -x[p][j], x[q][i]])
                    cls.append([y, -x[p][i], -x[q][j]])          # y <- carries
                    cls.append([y, -x[p][j], -x[q][i]])
            cls.append(yd)                                       # domino carries some piece
        for k in ys:
            cls.append(ys[k][:])
            # redundant AMO for propagation
            L = ys[k]
            for u in range(len(L)):
                for w in range(u + 1, len(L)):
                    cls.append([-L[u], -L[w]])
        for c in cls:
            self.S.add_clause(c + [-s])
        return s

    def solve(self, keys):
        ok = self.S.solve(assumptions=[self.sel[k] for k in keys])
        return ok

    def model_array(self):
        m = set(l for l in self.S.get_model() if l > 0)
        A = []
        for p in range(self.bd.N):
            vs = [v for v in range(self.bd.n + 1) if self.x[p][v] in m]
            assert len(vs) == 1
            A.append(vs[0])
        return A

    def block_array(self, A):
        """add clause excluding this exact array"""
        self.S.add_clause([-self.x[p][A[p]] for p in range(self.bd.N)])


class Enc2:
    def __init__(self, bd, Bset, solver='glucose4'):
        self.bd = bd
        n = bd.n
        self.V = V = _Vars()
        cl = []
        self.x = [[V.new() for v in range(n + 1)] for p in range(bd.N)]
        for p in range(bd.N):
            cl.append(self.x[p][:])
            for v in range(n + 1):
                for w in range(v + 1, n + 1):
                    cl.append([-self.x[p][v], -self.x[p][w]])
        cl.append([self.x[0][0]])
        for b in range(bd.nblocks):
            if b in Bset:
                continue
            a, bb, c, d = bd.block_cells(b)
            for va in range(n + 1):
                for vd in range(n + 1):
                    if va == vd:
                        continue
                    for vb in range(n + 1):
                        for vc in range(n + 1):
                            if vb == vc:
                                continue
                            cl.append([-self.x[a][va], -self.x[d][vd], -self.x[bb][vb], -self.x[c][vc]])
        self.S = Solver(name=solver, bootstrap_with=cl)
        self.sel = {}

    def add_tiling(self, key, t):
        n = self.bd.n
        V, x = self.V, self.x
        s = V.new()
        self.sel[key] = s
        P = pieces(n)
        cls = []
        byk = {k: [] for k in range(len(P))}
        for (p, q) in t:
            zs = []
            for k, (i, j) in enumerate(P):
                ors = [(i, j)] if i == j else [(i, j), (j, i)]
                for (u, w) in ors:
                    z = V.new()
                    zs.append(z)
                    byk[k].append(z)
                    cls.append([-z, x[p][u]])
                    cls.append([-z, x[q][w]])
            cls.append(zs)
            for a in range(len(zs)):
                for b in range(a + 1, len(zs)):
                    cls.append([-zs[a], -zs[b]])
        for k, L in byk.items():
            cls.append(L[:])
            for a in range(len(L)):
                for b in range(a + 1, len(L)):
                    cls.append([-L[a], -L[b]])
        for c in cls:
            self.S.add_clause(c + [-s])
        return s

    def solve(self, keys):
        return self.S.solve(assumptions=[self.sel[k] for k in keys])

    def model_array(self):
        m = set(l for l in self.S.get_model() if l > 0)
        return [[v for v in range(self.bd.n + 1) if self.x[p][v] in m][0] for p in range(self.bd.N)]
