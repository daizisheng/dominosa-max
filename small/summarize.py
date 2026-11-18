"""Collect dangerous-set statistics.  usage: python3 summarize.py n M blkjson...
Prints, for threshold M:
  dangerous sets (U(B) > M) by size, and how each was settled:
    none   = no class of G_B is realizable
    sum    = total size of the individually realizable classes <= M
    joint  = needed the joint branch and bound (best(B) <= M found exactly)
  plus the sets with U(B) = M (needed only for counting maximizers).
Writes dangerous_n{n}.json (one record per canonical set).
"""
import sys, json, collections

n, M = int(sys.argv[1]), int(sys.argv[2])
recs = []
for f in sys.argv[3:]:
    d = json.load(open(f))
    recs += d['records']
    L = d['L']
assert L <= M
out = []
by = collections.defaultdict(collections.Counter)
eq = collections.Counter()
for r in recs:
    if r['U'] < M:
        continue
    if not r['realizable']:
        how = 'none'
    elif r['fullb'] <= M:
        how = 'sum'
    else:
        how = 'joint'
    assert r['best'] <= M, r
    k = len(r['B'])
    if r['U'] > M:
        by[k][how] += 1
    else:
        eq[k] += 1
    out.append(dict(B=r['B'], size=k, U=r['U'], dangerous=r['U'] > M, orbit_size=r['orbit_size'],
                    nclasses=r['nclasses'], class_sizes_top10=r['class_sizes'][:10],
                    realizable_class_sizes=r['realizable'], sum_realizable=r['fullb'],
                    best=r['best'], best_collection=r['best_collection'],
                    best_witness=r['best_witness'], best_witness_count=r['best_witness_count'],
                    settled=how, joint_sat_calls=r['joint_calls']))
out.sort(key=lambda x: (x['size'], x['B']))
json.dump(dict(n=n, M=M, computed_with_threshold=L, sets=out), open(f'dangerous_n{n}.json', 'w'), indent=1)
tot = collections.Counter()
print(f'n={n} M={M}: dangerous sets (U>M) by size  [none/sum/joint]   (+ sets with U=M)')
for k in sorted(set(by) | set(eq)):
    c = by[k]
    tot.update(c)
    print(f'  |B|={k}: {sum(c.values())}  [none {c["none"]}, sum {c["sum"]}, joint {c["joint"]}]   U=M: {eq[k]}')
print(f'  total {sum(tot.values())}  [none {tot["none"]}, sum {tot["sum"]}, joint {tot["joint"]}]  U=M: {sum(eq.values())}')
print('  max best(B):', max(x['best'] for x in out))
print('  sets with best = M:', [(x['B'], x['best_collection']) for x in out if x['best'] == M])
