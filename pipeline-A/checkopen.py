# checkopen.py -- the invariant that closes pipeline A: every set that fullb.py left OPEN is
# settled either by joint.py ("MAX joint" <= THR) or by rbound.py ("bound" <= THR).
# Which OPEN sets joint.py finishes within JOINT_TIMEOUT depends on the machine; the others
# must be settled by rbound.py.
# usage: python3 checkopen.py THR fb_all.out joint_all.out rbound_all.out
import sys
thr = int(sys.argv[1])
opens = [l.split()[1] for l in open(sys.argv[2]) if l.startswith('OPEN ')]
joint, rb = {}, {}
for l in open(sys.argv[3]):
    p = l.split()
    if len(p) > 3 and p[1:3] == ['MAX', 'joint']: joint[p[0]] = int(p[3])
for l in open(sys.argv[4]):
    p = l.split()
    if 'bound' in p: rb[p[0]] = int(p[p.index('bound') + 1])
bad = []
nj = nr = 0
for S in opens:
    if S in joint and joint[S] <= thr: nj += 1
    elif S in rb and rb[S] <= thr: nr += 1
    else: bad.append((S, joint.get(S), rb.get(S)))
print('OPEN sets %d: settled by joint %d, by rbound %d, not settled %d' % (len(opens), nj, nr, len(bad)))
print('largest MAX joint %d, largest rbound bound %s' % (max(joint.values()) if joint else 0, max(rb.values()) if rb else '-'))
for b in bad[:10]: print('  not settled:', b)
sys.exit(1 if bad else 0)
