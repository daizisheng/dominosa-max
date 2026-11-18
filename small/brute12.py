"""Plain brute force for n=1,2: every array (each value n+2 times), count solutions
by checking every tiling.  Also checks Lemma 1 consequence on every array:
#solutions == total size of classes of G_{B(A)} that consist of solutions, and every
class is either all-solutions or no-solutions."""
import sys, json, itertools
from collections import Counter
from dom import Board, canon_full


def multiset_perms(counts, N):
    # all sequences of length N with value v appearing counts[v] times
    n1 = len(counts)
    cur = [0] * N
    left = list(counts)

    def rec(p):
        if p == N:
            yield tuple(cur)
            return
        for v in range(n1):
            if left[v]:
                left[v] -= 1
                cur[p] = v
                yield from rec(p + 1)
                left[v] += 1
    yield from rec(0)


def main(n):
    bd = Board(n)
    hist = Counter()
    best = -1
    maxers = []
    narr = 0
    for A in multiset_perms([n + 2] * (n + 1), bd.N):
        narr += 1
        sol = bd.solutions(A)
        s = len(sol)
        # Lemma-1 check
        cl = bd.classes(set(bd.bad_blocks(A)))
        ss = set(sol)
        tot = 0
        for c in cl:
            k = sum(1 for x in c if x in ss)
            assert k == 0 or k == len(c), (A, c)
            tot += k
        assert tot == s
        hist[s] += 1
        if s > best:
            best, maxers = s, []
        if s == best:
            maxers.append(A)
    orbits = sorted(set(canon_full(bd, A) for A in maxers))
    out = dict(n=n, board=[bd.R, bd.C], tilings=bd.T, arrays=narr, max=best,
               n_max_arrays=len(maxers), n_max_orbits=len(orbits),
               histogram={str(k): v for k, v in sorted(hist.items())},
               max_orbit_reps=[bd.fmt(o) for o in orbits],
               max_arrays=[bd.fmt(A) for A in maxers])
    json.dump(out, open(f'brute_n{n}.json', 'w'), indent=1)
    print(json.dumps({k: v for k, v in out.items() if k != 'max_arrays'}, indent=None))


if __name__ == '__main__':
    main(int(sys.argv[1]))
