# xcheck_tm.py -- cross-check of the class computation of pipeline B by the transfer matrix (Lemma 5).
#
# For every set B listed in the class file of pipeline B, the class sizes of G_B (flips in blocks
# outside B) are recomputed by tm.class_sizes, without listing any tiling, and compared with the
# class sizes found there by breadth-first search over all 1,292,697 tilings.
#
# Input (default ../pipeline-B/work/comp_all.out, written by "pipeline-B/run.sh classes"): one line per set, "k {b1,...} ncomp=.. ... live: size:rep ...",
# as written by pipeline-B/code/comp with TAILMIN = 0 (so every class is listed).  A directory of
# structure files written by "comp ... DUMPDIR" (lines "B ...", "C size rep H V", ...) is accepted too.
# That file covers the 11,326 sets of the control run with target 853,984, i.e. the 11,325 dangerous
# sets for 853,985 and the one extra set {3,17,19,26,29,31}.
#
# Also recomputes the number of flips in each of the 12 blocks (r,c), r<=2, c<=3, as (T - I({b}))/2,
# where I counts the tilings in which b is not filled by two parallel dominoes.
#
# usage: python3 xcheck_tm.py [CLASSFILE_OR_DIR] [NPROC]
import os, re, sys
from multiprocessing import Pool
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tm import class_sizes
from icount import I_count

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT = os.path.join(HERE, '..', 'pipeline-B', 'work', 'comp_all.out')


def records(src):
    if os.path.isdir(src):
        for fn in sorted(os.listdir(src)):
            lines = open(os.path.join(src, fn)).read().split('\n')
            B = [int(x) for x in lines[0].split()[1:]]
            yield B, sorted((int(l.split()[1]) for l in lines if l.startswith('C ')), reverse=True)
    else:
        for line in open(src):
            m = re.search(r'\{([0-9,]*)\}', line)
            B = [int(x) for x in m.group(1).split(',') if x]
            nc = int(re.search(r'ncomp=(\d+)', line).group(1))
            assert re.search(r'tail=0\s*$', line), 'class list truncated'
            sizes = sorted((int(x) for x in re.findall(r' (\d+):\d+', line.split('live:')[1])), reverse=True)
            assert len(sizes) == nc
            yield B, sizes


def job(rec):
    B, sizes = rec
    tm = class_sizes(6, [(b // 7, b % 7) for b in B])
    return B, sizes == tm, len(sizes)


if __name__ == '__main__':
    src = sys.argv[1] if len(sys.argv) > 1 else DEFAULT
    nproc = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    recs = list(records(src))
    if nproc > 1:
        with Pool(nproc) as P:
            res = P.map(job, recs, chunksize=50)
    else:
        res = [job(r) for r in recs]
    bad = [r for r in res if not r[1]]
    print('sets', len(res), 'mismatches', len(bad))
    for r in bad[:20]: print('  mismatch', r)
    print('total classes compared', sum(r[2] for r in res))
    T = 1292697
    print('flips per block (r,c), r<=2, c<=3:')
    for r in range(3):
        print('  r=%d:' % r, ' '.join('%8d' % ((T - I_count(6, [(r, c)])) // 2) for c in range(4)))
    sys.exit(1 if bad else 0)
