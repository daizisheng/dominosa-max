"""Count arrays with many solutions by the block method.

usage: python3 countmax.py n L [blk json files...]
For every dangerous B (U(B) >= L) and every jointly realizable collection S of classes
of G_B with total >= L (from blk.py), enumerate by AllSAT every array with
  B(A) = B exactly,  every class of S consists of solutions,
  first-occurrence canonical labels (one array per relabeling orbit).
Each array is counted with cnt.c.  An array A with #sol(A) >= L has B(A) in the
dangerous family, its solution set is a realizable collection of classes of G_{B(A)},
so it is found from the canonical image of B(A).  Totals:
  #arrays with v solutions = (n+1)! * sum_B orbit(B) * #{found A for B: #sol(A)=v}.
Output: countmax_n{n}_L{L}.json
"""
import sys, json, math, glob, collections
from dom import Board, canon_full
from satenc import Enc1
from blk import BM, count_solutions


SPLIT = None


def main():
    global SPLIT
    import os
    if os.environ.get('SPLIT'):
        SPLIT = tuple(int(x) for x in os.environ['SPLIT'].split(':'))
    n, L = int(sys.argv[1]), int(sys.argv[2])
    files = sys.argv[3:] or [f'blk_n{n}.json']
    recs = []
    for f in files:
        recs += json.load(open(f))['records']
    bm = BM(n)
    bd = bm.bd
    hist = collections.Counter()      # weighted (all arrays)
    hist_canon = collections.Counter()
    orbit_reps = collections.defaultdict(set)
    perB = []
    for r in recs:
        B = tuple(r['B'])
        if r['U'] < L or not r['hits']:
            continue
        cl = bm.classes(B)
        assert [len(c) for c in cl] == r['class_sizes']
        found = {}
        for h in r['hits']:
            e = Enc1(bd, set(B), exact_bad=True, canon=True)
            if SPLIT:   # optional split for parallel runs: cell p has value v
                e.S.add_clause([e.x[SPLIT[0]][SPLIT[1]]])
            for i in h['idx']:
                e.add_tiling(i, bd.tilings[cl[i][0]])
            keys = h['idx']
            while e.solve(keys):
                A = e.model_array()
                found[bd.fmt(A)] = None
                e.block_array(A)
            e.S.delete()
        arrs = sorted(found)
        cnts = count_solutions(n, arrs)
        hB = collections.Counter()
        for a, c in zip(arrs, cnts):
            A = bd.parse(a)
            assert tuple(bd.bad_blocks(A)) == B
            hB[c] += 1
            orbit_reps[c].add(canon_full(bd, A))
        for c, k in hB.items():
            hist_canon[c] += k * r['orbit_size']
            hist[c] += k * r['orbit_size'] * math.factorial(n + 1)
        perB.append(dict(B=list(B), orbit_size=r['orbit_size'], canonical_arrays=len(arrs),
                         by_count={str(k): v for k, v in sorted(hB.items())},
                         arrays=[f'{a} {c}' for a, c in zip(arrs, cnts) if c >= L]))
        print(B, dict(hB), flush=True)
    out = dict(n=n, L=L,
               histogram_all_arrays={str(k): v for k, v in sorted(hist.items()) if k >= L},
               orbits_full_group={str(k): len(v) for k, v in sorted(orbit_reps.items()) if k >= L},
               orbit_reps={str(k): sorted(bd.fmt(o) for o in v) for k, v in sorted(orbit_reps.items()) if k >= L},
               perB=perB)
    out['split'] = SPLIT
    sfx = f'_split{SPLIT[0]}_{SPLIT[1]}' if SPLIT else ''
    json.dump(out, open(f'countmax_n{n}_L{L}{sfx}.json', 'w'), indent=1)
    print('histogram (all arrays, values >= L):', out['histogram_all_arrays'])
    print('orbits under 4 syms x relabel:', out['orbits_full_group'])


if __name__ == '__main__':
    main()
