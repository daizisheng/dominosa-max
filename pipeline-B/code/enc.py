"""enc.py -- CNF encoding of "joint realizability with bad set exactly B".

Question encoded: is there an array A (56 cells, values 0..6) such that
  (i)  bad(A) == B exactly  (blocks outside B good: TL==BR or TR==BL; blocks in B bad), and
  (ii) each of the given tilings T_1..T_m is a solution of A (its 28 dominoes carry 28
       distinct unordered pairs, i.e. each of the 28 pairs exactly once)?

Variables
  y[c][k]       cell c carries value k                      (exactly one k per cell)
  z[i][d][p]    domino d of tiling i carries unordered pair p, defined  z <-> pair(cells) == p
  e[b][0/1]     block b (not in B) is good via diagonal TL==BR (0) or anti-diagonal TR==BL (1)
Constraints per tiling i: each pair p used by exactly one domino; each domino has >=1 pair.
Value symmetry breaking (sound: permuting the values 0..6 preserves (i),(ii)):
  in tiling T_1 the double {k,k} occurs at a smaller domino index than {k+1,k+1}.
"""

PAIRS = [(a, b) for a in range(7) for b in range(a, 7)]
PID = {p: i for i, p in enumerate(PAIRS)}


def blk_cells(b):
    r, c = divmod(b, 7)
    return 8 * r + c, 8 * r + c + 1, 8 * (r + 1) + c, 8 * (r + 1) + c + 1


def dominoes(H, V):
    out = []
    for c in range(56):
        if H >> c & 1:
            out.append((c, c + 1))
        if V >> c & 1:
            out.append((c, c + 8))
    assert len(out) == 28
    return out


class Enc:
    def __init__(self):
        self.nv = 0
        self.cl = []

    def new(self):
        self.nv += 1
        return self.nv


def encode(B, tilings, symbreak=True):
    """B: set of block ids (exact bad set); tilings: list of (H,V). Returns (Enc, y)."""
    E = Enc()
    y = [[E.new() for k in range(7)] for c in range(56)]
    for c in range(56):
        E.cl.append([y[c][k] for k in range(7)])
        for k in range(7):
            for l in range(k + 1, 7):
                E.cl.append([-y[c][k], -y[c][l]])
    for b in range(42):
        P, Q, R, S = blk_cells(b)
        if b in B:  # bad: P!=S and Q!=R
            for k in range(7):
                E.cl.append([-y[P][k], -y[S][k]])
                E.cl.append([-y[Q][k], -y[R][k]])
        else:  # good: (P==S) or (Q==R)
            e0, e1 = E.new(), E.new()
            E.cl.append([e0, e1])
            for k in range(7):
                E.cl.append([-e0, -y[P][k], y[S][k]])
                E.cl.append([-e1, -y[Q][k], y[R][k]])
    first_z = None
    for ti, (H, V) in enumerate(tilings):
        doms = dominoes(H, V)
        z = [[E.new() for p in range(28)] for d in range(28)]
        if ti == 0:
            first_z = z
        for d, (u, v) in enumerate(doms):
            E.cl.append([z[d][p] for p in range(28)])
            for p, (a, b) in enumerate(PAIRS):
                zz = z[d][p]
                if a == b:
                    E.cl.append([-y[u][a], -y[v][a], zz])
                    E.cl.append([-zz, y[u][a]])
                    E.cl.append([-zz, y[v][a]])
                else:
                    E.cl.append([-y[u][a], -y[v][b], zz])
                    E.cl.append([-y[u][b], -y[v][a], zz])
                    A1, B1, A2, B2 = y[u][a], y[v][b], y[u][b], y[v][a]
                    E.cl.append([-zz, A1, A2])
                    E.cl.append([-zz, A1, B2])
                    E.cl.append([-zz, B1, A2])
                    E.cl.append([-zz, B1, B2])
        for p in range(28):
            E.cl.append([z[d][p] for d in range(28)])
            for d in range(28):
                for d2 in range(d + 1, 28):
                    E.cl.append([-z[d][p], -z[d2][p]])
    if symbreak and first_z is not None:
        dbl = [PID[(k, k)] for k in range(7)]
        for k in range(6):
            for d in range(28):
                for d2 in range(d + 1):
                    E.cl.append([-first_z[d][dbl[k]], -first_z[d2][dbl[k + 1]]])
    return E, y


def write_cnf(E, fn):
    with open(fn, "w") as f:
        f.write("p cnf %d %d\n" % (E.nv, len(E.cl)))
        for c in E.cl:
            f.write(" ".join(map(str, c)) + " 0\n")


def decode(model_lits, y):
    pos = set(l for l in model_lits if l > 0)
    A = []
    for c in range(56):
        ks = [k for k in range(7) if y[c][k] in pos]
        assert len(ks) == 1
        A.append(ks[0])
    return "/".join("".join(str(A[8 * r + c]) for c in range(8)) for r in range(7))


def load_tilings(datadir):
    import numpy as np  # only used by tests; keep it out of the driver (BLAS threads)
    a = np.fromfile(datadir + "/tilings.bin", dtype=np.uint64).reshape(-1, 2)
    return a
