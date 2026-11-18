"""Block method for double-n Dominosa (Lemmas 1-3).

usage: python3 blk.py n L [jobs j]      (run it in a work directory; it reads D_n{n}_L{L}.json if present)
  L = a lower bound with a witness (from search).  The program
  1. enumerates (up to the 4 rectangle symmetries) every block set B with
     U(B) = T - nu(H_B) >= L  ("dangerous at threshold L-1"; the proof's dangerous sets,
     threshold L, are the ones with U(B) > L);
  2. for each such B: classes of G_B (flips in blocks outside B), single-class
     realizability by SAT (Enc1/CaDiCaL), then exact best(B) = max total size of a
     jointly realizable collection, by branch and bound with incremental SAT;
     it also lists every jointly realizable collection with total >= L;
  3. every UNSAT verdict that the conclusion depends on is re-checked with Enc2
     (independent encoding, Glucose4); every SAT verdict is checked by counting the
     solutions of the model array with an independent counter (cnt.c).
Output: blk_n{n}.json (+ progress on stdout).  With "jobs j" only the B with
index % jobs == j are processed in step 2 (output blk_n{n}_part{j}.json).
"""
import sys, os, json, time, subprocess
import numpy as np
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import maximum_bipartite_matching, connected_components
from dom import Board
from satenc import Enc1, Enc2


class BM:
    def __init__(self, n):
        self.n = n
        self.bd = bd = Board(n)
        self.syms = bd.block_syms()
        E = np.array(bd.edges, dtype=np.int64)
        # orient every edge as (colour-0 endpoint, colour-1 endpoint)
        col = np.array(bd.color)
        u = np.where(col[E[:, 0]] == 0, E[:, 0], E[:, 1])
        w = np.where(col[E[:, 0]] == 0, E[:, 1], E[:, 0])
        self.left = np.flatnonzero(col == 0)
        self.right = np.flatnonzero(col == 1)
        lpos = -np.ones(bd.T, dtype=np.int64); lpos[self.left] = np.arange(len(self.left))
        rpos = -np.ones(bd.T, dtype=np.int64); rpos[self.right] = np.arange(len(self.right))
        self.eu, self.ew, self.eb = lpos[u], rpos[w], E[:, 2]
        self.Ei, self.Ej = E[:, 0], E[:, 1]
        self.nU = 0

    def canon(self, B):
        return min(tuple(sorted(m[b] for b in B)) for m in self.syms)

    def U(self, B):
        self.nU += 1
        bd = self.bd
        mask = np.isin(self.eb, list(B))
        if not mask.any():
            return bd.T
        g = csr_matrix((np.ones(mask.sum(), dtype=np.int8), (self.eu[mask], self.ew[mask])),
                       shape=(len(self.left), len(self.right)))
        m = maximum_bipartite_matching(g, perm_type='column')
        matched = np.flatnonzero(m >= 0)
        # validate: each matched pair is an edge of H_B, columns distinct
        cols = m[matched]
        assert len(set(cols.tolist())) == len(cols)
        assert (np.asarray(g[matched, cols]).ravel() != 0).all()
        return bd.T - len(matched)

    def classes(self, B):
        bd = self.bd
        mask = ~np.isin(self.eb, list(B))
        g = csr_matrix((np.ones(mask.sum(), dtype=np.int8), (self.Ei[mask], self.Ej[mask])),
                       shape=(bd.T, bd.T))
        nc, lab = connected_components(g, directed=False)
        cl = {}
        for i, l in enumerate(lab.tolist()):
            cl.setdefault(l, []).append(i)
        return sorted(cl.values(), key=lambda c: (-len(c), c[0]))

    def dangerous(self, L, log=print):
        """all canonical B with U(B) >= L, level by level (apriori)."""
        levels = []
        cur = {(): self.U(())}
        cur = {k: v for k, v in cur.items() if v >= L}
        levels.append(cur)
        nb = self.bd.nblocks
        while cur:
            nxt = {}
            tried = set()
            for B in cur:
                for b in range(nb):
                    if b in B:
                        continue
                    C = self.canon(B + (b,))
                    if C in tried:
                        continue
                    tried.add(C)
                    # apriori: every subset of size k dangerous
                    ok = all(self.canon(tuple(x for x in C if x != y)) in cur for y in C)
                    if not ok:
                        continue
                    u = self.U(C)
                    if u >= L:
                        nxt[C] = u
            log(f'level {len(levels)}: candidates {len(tried)} dangerous(U>={L}) {len(nxt)}')
            levels.append(nxt)
            cur = nxt
        return levels


def count_solutions(n, arrays):
    if not arrays:
        return []
    inp = '\n'.join(arrays) + '\n'
    out = subprocess.run([os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cnt'), str(n)], input=inp, capture_output=True, text=True, check=True).stdout
    res = []
    for line in out.strip().split('\n'):
        a, c = line.split()[:2]
        assert 'BADCOUNTS' not in line
        res.append(int(c))
    return res


def settle(bm, B, L, verify=True, P=None, Q=None):
    P = P or Enc1   # primary (CaDiCaL)
    Q = Q or Enc2   # independent re-check of UNSAT verdicts (Glucose4)
    """returns dict with classes, realizable classes, best(B), collections >= L"""
    bd = bm.bd
    n = bm.n
    Bs = set(B)
    cl = bm.classes(B)
    sizes = [len(c) for c in cl]
    e1 = P(bd, Bs)
    e2 = Q(bd, Bs) if verify else None
    real = []
    witness = {}
    nsat = 0
    unsat_checked = 0
    for idx, c in enumerate(cl):
        es = P(bd, Bs)
        es.add_tiling(idx, bd.tilings[c[0]])
        nsat += 1
        if es.solve([idx]):
            A = es.model_array()
            witness[idx] = bd.fmt(A)
            real.append(idx)
            e1.add_tiling(idx, bd.tilings[c[0]])
        else:
            es.S.delete()
            if verify:
                e2.add_tiling(idx, bd.tilings[c[0]])
                assert not e2.solve([idx]), ('second encoding disagrees', B, idx)
                unsat_checked += 1
            continue
        es.S.delete()
    # verify single witnesses: model array's solution set contains the class, and
    # B(A) subset of B
    wl = [witness[i] for i in real]
    cnts = count_solutions(n, wl)
    for i, cc in zip(real, cnts):
        A = bd.parse(witness[i])
        assert set(bd.bad_blocks(A)) <= Bs
        assert bd.is_solution(A, bd.tilings[cl[i][0]])
        assert cc >= sizes[i]
    fullb = sum(sizes[i] for i in real)
    rec = dict(B=list(B), U=None, nclasses=len(cl), class_sizes=sizes,
               realizable=[sizes[i] for i in real], fullb=fullb)
    # branch and bound over realizable classes (sorted by size desc already)
    order = real
    suf = [0] * (len(order) + 1)
    for k in range(len(order) - 1, -1, -1):
        suf[k] = suf[k + 1] + sizes[order[k]]
    best = [0, []]
    hits = []          # collections with total >= L
    joint_calls = [0]
    unsat_joint = []

    def dfs(k, chosen, tot):
        # every subset 'chosen' is recorded exactly once: when it is created
        if k == len(order):
            return
        if tot + suf[k] < L and tot + suf[k] <= best[0]:
            return
        i = order[k]
        cand = chosen + [i]
        if len(cand) == 1:
            ok = True
        else:
            joint_calls[0] += 1
            ok = e1.solve(cand)
            if not ok:
                unsat_joint.append(cand)
        if ok:
            t2 = tot + sizes[i]
            if t2 > best[0]:
                best[0], best[1] = t2, list(cand)
            if t2 >= L:
                hits.append((t2, list(cand)))
            dfs(k + 1, cand, t2)
        dfs(k + 1, chosen, tot)

    dfs(0, [], 0)
    # note: hits may contain a collection and its subsets only if both have total >= L
    if verify:
        for cand in unsat_joint:
            for i in cand:
                if i not in e2.sel:
                    e2.add_tiling(i, bd.tilings[cl[i][0]])
            assert not e2.solve(cand), ('second encoding disagrees on joint', B, cand)
    # witness for best and for hits
    hw = []
    for tot, cand in hits + [(best[0], best[1])]:
        if not cand:
            hw.append(None)
            continue
        assert e1.solve(cand)
        A = e1.model_array()
        assert set(bd.bad_blocks(A)) <= Bs
        for i in cand:
            assert bd.is_solution(A, bd.tilings[cl[i][0]])
        hw.append(bd.fmt(A))
    cc = count_solutions(n, [h for h in hw if h])
    k = 0
    hwc = []
    for h in hw:
        if h is None:
            hwc.append(None)
        else:
            hwc.append(cc[k]); k += 1
    rec.update(best=best[0], best_collection=[sizes[i] for i in best[1]],
               best_collection_idx=best[1], best_witness=hw[-1], best_witness_count=hwc[-1],
               hits=[dict(total=t, idx=c, sizes=[sizes[i] for i in c], witness=w, witness_count=wc)
                     for (t, c), w, wc in zip(hits, hw[:-1], hwc[:-1])],
               single_unsat_rechecked=unsat_checked, joint_calls=joint_calls[0],
               joint_unsat=len(unsat_joint))
    if not real:
        rec['settled'] = 'no class realizable'
    elif fullb < L:
        rec['settled'] = 'fullb<L'
    elif fullb == L:
        rec['settled'] = 'fullb=L'
    else:
        rec['settled'] = 'joint B&B'
    return rec


def main():
    n, L = int(sys.argv[1]), int(sys.argv[2])
    jobs, j = (int(sys.argv[3]), int(sys.argv[4])) if len(sys.argv) > 4 and sys.argv[3] != 'enum' else (1, 0)
    t0 = time.time()
    bm = BM(n)
    bd = bm.bd
    print(f'n={n} T={bd.T} blocks={bd.nblocks} edges={len(bd.edges)}', flush=True)
    import os
    dfn = f'D_n{n}_L{L}.json'
    if os.path.exists(dfn):
        levels = [{tuple(x[0]): x[1] for x in lev} for lev in json.load(open(dfn))]
        print('loaded', dfn, flush=True)
    else:
        levels = bm.dangerous(L, log=lambda s: print(s, flush=True))
        json.dump([[[list(k), v] for k, v in sorted(lev.items())] for lev in levels], open(dfn, 'w'))
    if len(sys.argv) > 3 and sys.argv[3] == 'enum':
        print('levels', [len(l) for l in levels], 'strict', [sum(1 for v in l.values() if v > L) for l in levels])
        return
    allB = [(B, u) for lev in levels for B, u in sorted(lev.items())]
    print(f'dangerous sets: {len(allB)}  U computations {bm.nU}  t={time.time()-t0:.1f}s', flush=True)
    recs = []
    for idx, (B, u) in enumerate(allB):
        if idx % jobs != j:
            continue
        r = settle(bm, B, L)
        r['U'] = u
        r['strict'] = u > L
        r['orbit_size'] = len(set(tuple(sorted(m[b] for b in B)) for m in bm.syms))
        recs.append(r)
        print(f'B={B} U={u} classes={r["nclasses"]} top={r["class_sizes"][:4]} real={r["realizable"][:6]} '
              f'fullb={r["fullb"]} best={r["best"]} {r["settled"]} hits={len(r["hits"])} '
              f't={time.time()-t0:.1f}', flush=True)
    out = dict(n=n, L=L, T=bd.T, nblocks=bd.nblocks, nedges=len(bd.edges),
               edges_per_block=[int((bm.eb == b).sum()) for b in range(bd.nblocks)],
               levels=[{'size': k, 'count_U_ge_L': len(lev),
                        'count_U_gt_L': sum(1 for v in lev.values() if v > L)}
                       for k, lev in enumerate(levels)],
               nU=bm.nU, records=recs, seconds=time.time() - t0)
    fn = f'blk_n{n}.json' if jobs == 1 else f'blk_n{n}_part{j}.json'
    json.dump(out, open(fn, 'w'), indent=1)
    print('max best over dangerous sets:', max((r['best'] for r in recs), default=None), flush=True)


if __name__ == '__main__':
    main()
