"""Compare the histogram printed by bfa / bfb ("H solutions count" lines, possibly from several
slices) with data/histograms_n123.tsv.
usage: python3 histcmp.py n bfa|bfb OUTPUT [OUTPUT ...]
bfa counts first-occurrence canonical arrays (weight (n+1)!), bfb arrays with A[0]=0 (weight n+1).
"""
import sys, os, math, collections

n, prog, files = int(sys.argv[1]), sys.argv[2], sys.argv[3:]
w = math.factorial(n + 1) if prog == 'bfa' else n + 1
h = collections.Counter()
for fn in files:
    for line in open(fn):
        f = line.split()
        if f and f[0] == 'H':
            h[int(f[1])] += int(f[2]) * w
ref = {}
for line in open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'histograms_n123.tsv')):
    if line.startswith('#'): continue
    a, s, c = map(int, line.split())
    if a == n: ref[s] = c
print('n=%d %s: arrays %d, max %d (%d arrays), identical to data/histograms_n123.tsv: %s'
      % (n, prog, sum(h.values()), max(h), h[max(h)], dict(h) == ref))
sys.exit(0 if dict(h) == ref else 1)
