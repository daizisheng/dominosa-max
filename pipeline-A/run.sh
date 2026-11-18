#!/bin/sh
# Pipeline A: the first computation of the upper bound for the double-six board.
# usage (from any directory, after "make" at the top level):
#     pipeline-A/run.sh STEP
#     STEP = dangerous | single | single3 | classes | fullb | joint | rbound | rbound-data | family
# Results go to pipeline-A/work/ and are compared with data/ (up to symmetry, or by sha256).
# THR (default 853985) is the target M.  NPROC (default 1) is the number of parallel jobs of the
# steps single3, fullb, joint, rbound, rbound-data.  JOINT_TIMEOUT (default 3000 s) is the time
# allowed per set in joint.
set -e
cd "$(dirname "$0")"
export LC_ALL=C
THR=${THR:-853985}
NPROC=${NPROC:-1}
JOINT_TIMEOUT=${JOINT_TIMEOUT:-3000}
export THR JOINT_TIMEOUT
mkdir -p work
check() { (cd work && grep " $1\$" ../data/SHA256SUMS | sha256sum -c -); }
chunks() {  # chunks FILE PREFIX: split FILE into about 4*NPROC pieces PREFIX.0000, PREFIX.0001, ...
  rm -f "$2".*; n=$(wc -l < "$1"); k=$((4 * NPROC)); [ "$k" -le "$n" ] || k=$n
  split -n l/$k -d -a 4 "$1" "$2".
}

case "$1" in
dangerous)
  # D = sets S with U(S) = T - nu(H_S) > THR.  As in the original run: every canonical set of at
  # most 4 blocks (gensets.py), then level by level with apriori.py; self-checking Hopcroft-Karp.
  # Expected: 11,324 non-empty sets, 12/197/1290/3319/3774/2109/534/88/1, identical to data/Dlist.txt.
  for k in 1 2 3 4; do
    python3 gensets.py $k | ./ubv list | awk '{print "B",$1,"max",$3}' > work/D${k}all.txt
  done
  k=4
  while :; do
    python3 apriori.py "$THR" work/D${k}all.txt > work/Dc$((k+1)).txt
    [ -s work/Dc$((k+1)).txt ] || break
    ./ubv list < work/Dc$((k+1)).txt | awk '{print "B",$1,"max",$3}' > work/D$((k+1))all.txt
    k=$((k+1))
  done
  cat work/D[1-9]*all.txt | awk -v t="$THR" '$4>t {print $2}' | sort > work/Dlist.txt
  sort data/Dlist.txt | cmp - work/Dlist.txt && echo "Dlist.txt: the same 11,324 sets as data/Dlist.txt, with the same representatives"
  for k in 1 2 3 4 5 6 7 8 9; do check D${k}all.txt; done
  ;;
single)
  # Sets S whose LARGEST class (under flips outside S) exceeds THR, level by level, then SAT on
  # that class with satb2 ("single3" repeats it with satb3).  Expected: 350 sets, all UNSAT.
  ./bsearch enum 0 "$THR" 0 1 > work/L0.out
  k=0
  while :; do
    grep '^B' work/L$k.out | python3 apriori.py "$THR" /dev/stdin > work/Lc$((k+1)).txt
    [ -s work/Lc$((k+1)).txt ] || break
    ./bsearch list "$THR" < work/Lc$((k+1)).txt > work/L$((k+1)).out
    k=$((k+1))
  done
  cat work/L[0-9]*.out | grep '^B' > work/allcand.txt
  python3 cmpsets.py data/allcand.txt work/allcand.txt
  check allcand.txt
  python3 satb2.py < work/allcand.txt > work/allcand_satb2.out
  awk '{print $1}' work/allcand_satb2.out | sort | uniq -c
  [ "$(grep -c '^UNSAT' work/allcand_satb2.out)" = 350 ]
  ;;
single3)
  chunks work/allcand.txt work/cand
  ls work/cand.???? | xargs -P "$NPROC" -I{} sh -c 'python3 satb3.py < {} > {}.out'
  cat work/cand.????.out > work/allcand_satb3.out
  awk '{print $1}' work/allcand_satb3.out | sort | uniq -c
  [ "$(grep -c '^UNSAT' work/allcand_satb3.out)" = 350 ]
  ;;
classes)
  # All classes of G_S for every S in D (and the empty set), with a representative tiling each.
  (echo -; cat work/Dlist.txt) | ./bsearch listall 1 > work/classes.txt
  ;;
fullb)
  # Single-class SAT tests, largest class first, until the realizable total is <= THR.
  # Expected: identical to data/fb_all.out (10,822 OK, 502 OPEN).
  grep -v '^S - ' work/classes.txt > work/fb_in.txt
  chunks work/fb_in.txt work/fb
  ls work/fb.???? | xargs -P "$NPROC" -I{} sh -c 'python3 fullb.py "$THR" < {} > {}.out'
  cat work/fb.????.out > work/fb_all.out
  python3 cmplines.py fb work/fb_all.out data/fb_all.out
  ;;
joint)
  # Exact maximum of Lemma 4 for the OPEN sets (one job per set, JOINT_TIMEOUT seconds each).
  # Which sets finish depends on the machine; the others are settled by "rbound".
  mkdir -p work/joint
  awk '$1=="OPEN" {print $2}' work/fb_all.out > work/open.txt
  xargs -P "$NPROC" -I{} sh -c 'timeout "$JOINT_TIMEOUT" python3 joint.py "$THR" {} > work/joint/{}.out || true' < work/open.txt
  while read s; do grep 'MAX joint' "work/joint/$s.out" || true; done < work/open.txt > work/joint_all.out
  echo "$(wc -l < work/joint_all.out) of $(wc -l < work/open.txt) OPEN sets finished"
  python3 cmplines.py --subset joint work/joint_all.out data/joint_all.out
  ;;
rbound)
  # Refined matching bound |R| - nu(H_S[R]) for the OPEN sets that joint did not finish, then the
  # invariant: every OPEN set has MAX joint <= THR or an rbound bound <= THR.
  grep 'MAX joint' work/joint_all.out | awk '{print $1}' | sort > work/joint_done.txt
  sort work/open.txt | comm -23 - work/joint_done.txt > work/rbound_sets.txt
  mkdir -p work/rbound
  xargs -P "$NPROC" -I{} sh -c 'python3 rbound.py {} > work/rbound/{}.out' < work/rbound_sets.txt
  while read s; do cat "work/rbound/$s.out"; done < work/rbound_sets.txt > work/rbound_all.out
  python3 cmplines.py --subset rbound work/rbound_all.out data/rbound_all.out
  python3 checkopen.py "$THR" work/fb_all.out work/joint_all.out work/rbound_all.out
  ;;
rbound-data)
  # The refined bound for the 12 sets of data/rbound_all.out, whatever joint did here.
  mkdir -p work/rbound
  awk '{print $1}' data/rbound_all.out > work/rbound_data_sets.txt
  xargs -P "$NPROC" -I{} sh -c 'python3 rbound.py {} > work/rbound/{}.out' < work/rbound_data_sets.txt
  while read s; do cat "work/rbound/$s.out"; done < work/rbound_data_sets.txt > work/rbound_data.out
  python3 cmplines.py rbound work/rbound_data.out data/rbound_all.out
  awk -v t="$THR" '{b = $NF; if (b > m) m = b; if (b > t) bad = 1} END {print NR " sets, largest bound " m; exit bad}' work/rbound_data.out
  ;;
family)
  # 20,000 arrays realizing the record class, reduced to essentially different ones.
  # Expected: 19,601 arrays, all with 853,985 solutions, A* first (checksum in data/SHA256SUMS).
  rep=$(./bsearch one 10,15,19,31 1 | awk '$1=="comp" {print $6, $7}')
  python3 enumrec.py 10,15,19,31 $rep 20000 work/family.txt
  check family.txt
  ;;
*)
  echo "usage: $0 dangerous|single|single3|classes|fullb|joint|rbound|rbound-data|family" >&2; exit 2 ;;
esac
