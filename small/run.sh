#!/bin/sh
# The double-n cases n = 1..5.  usage (from any directory, after "make" at the top level):
#     small/run.sh STEP     STEP = brute | n3full | n3 | block N | block5sum | countmax N | bb4 |
#                                  bb5 [J0 J1] | merge5
# J selects the slices of n3 and the parts of "block 5" (e.g. J="0 1 2"); NPROC (default 1) is the
# number of parallel bb3 jobs of bb5.
# Results go to small/work/ and are compared with small/data/ (directly or by sha256).
set -e
cd "$(dirname "$0")"
mkdir -p work
export OPENBLAS_NUM_THREADS=${OPENBLAS_NUM_THREADS:-1} OMP_NUM_THREADS=${OMP_NUM_THREADS:-1}
cd work
M() { case $1 in 1) echo 3;; 2) echo 10;; 3) echo 88;; 4) echo 1012;; 5) echo 23929;; esac; }
check() { grep " $1\$" "${2:-../data/SHA256SUMS}" | sha256sum -c -; }
same_json() {  # same_json FILE: equal to data/FILE apart from witness arrays, timing and the nU counter
  python3 - "$1" <<'EOF'
import json, sys
def strip(x):
    if isinstance(x, dict): return {k: strip(v) for k, v in x.items() if 'witness' not in k and k not in ('seconds', 'nU')}
    if isinstance(x, list): return [strip(v) for v in x]
    return x
fn = sys.argv[1]
ok = strip(json.load(open(fn))) == strip(json.load(open('../data/' + fn)))
print(fn, 'equal to data/ (apart from witness arrays, timing, counters):', ok)
sys.exit(0 if ok else 1)
EOF
}

case "$1" in
brute)   # every array for n = 1, 2 (Python), and the two C programs for n = 1, 2
  for n in 1 2; do
    python3 ../brute12.py $n > /dev/null; same_json brute_n$n.json
    ../bfa $n 1 0 0 1000 > bfa_n$n.out; python3 ../histcmp.py $n bfa bfa_n$n.out
    ../bfb $n 1 0 0 1000 > bfb_n$n.out; python3 ../histcmp.py $n bfb bfb_n$n.out
  done ;;
n3full)  # every array for n = 3 by bfa in one run (20 s), histogram compared with data/
  ../bfa 3 1 0 0 80 > bfa_n3.out; python3 ../histcmp.py 3 bfa bfa_n3.out ;;
n3)      # every array for n = 3 in 12 slices, bfa and bfb (bfb 2.5 min per slice); J selects slices
  for j in ${J:-0 1 2 3 4 5 6 7 8 9 10 11}; do
    ../bfa 3 12 $j 8 80 > bfa_n3_slice$j.out; check bfa_n3_slice$j.out
    ../bfb 3 12 $j 8 80 > bfb_n3_$j.out; check bfb_n3_$j.out
  done ;;
block)   # the block method for n = $2 (Lemmas 3 and 4, two SAT encodings); for n = 5 in 9 parts
  n=$2
  if [ "$n" = 5 ]; then   # run J=0 first (it creates D_n5_L23929.json), then the other parts, then block5sum
    for j in ${J:-0 1 2 3 4 5 6 7 8}; do
      if [ ! -f D_n5_L23929.json ]; then python3 ../blk.py 5 23929 enum > /dev/null; same_json D_n5_L23929.json; fi
      python3 ../blk.py 5 23929 9 $j > blk5_part$j.log; same_json blk_n5_part$j.json
    done
    [ -n "$J" ] && exit 0
    python3 ../summarize.py 5 23929 blk_n5_part*.json
  else
    python3 ../blk.py $n $(M $n) > blk_n$n.log
    same_json D_n${n}_L$(M $n).json; same_json blk_n$n.json
    python3 ../summarize.py $n $(M $n) blk_n$n.json
  fi
  same_json dangerous_n$n.json ;;
block5sum) # after all 9 parts of "block 5": the table of dangerous sets for n = 5
  [ "$(ls blk_n5_part?.json | wc -l)" = 9 ] || { echo "block5sum: run all 9 parts of block 5 first" >&2; exit 1; }
  python3 ../summarize.py 5 23929 blk_n5_part*.json
  same_json dangerous_n5.json ;;
countmax) # all optimal arrays by the block method (AllSAT), after "block N"
  n=$2
  if [ "$n" = 5 ]; then   # in 6 parts by the value of cell 8
    for v in 0 1 2 3 4 5; do SPLIT=8:$v python3 ../countmax.py 5 23929 blk_n5_part*.json > cm5_split$v.log; done
    python3 -c "
import json, glob
A = sorted(a.split()[0] for f in glob.glob('countmax_n5_L23929_split8_*.json')
           for r in json.load(open(f))['perB'] for a in r['arrays'] if int(a.split()[1]) == 23929)
open('max_n5.txt', 'w').write(''.join(x + '\n' for x in A)); print(len(A), 'arrays with 23929 solutions')"
    check max_n5.txt
  else
    python3 ../countmax.py $n $(M $n) blk_n$n.json | tail -2; same_json countmax_n${n}_L$(M $n).json
  fi ;;
bb4)     # branch and bound over arrays for n = 4 (no blocks, no SAT), thresholds 900 and 1012
  ../bb 4 900 1 0 0 > bb4_900.out; check bb4_900.out
  ../bb 4 1012 1 0 0 > bb4_1012.out; check bb4_1012.out
  awk 'NF == 2 {print $2}' bb4_900.out | sort | uniq -c
  if [ -f countmax_n4_L1012.json ]; then python3 ../cmpsets.py 4 1012 bb4_900.out countmax_n4_L1012.json; fi ;;
bb5)     # branch and bound over arrays for n = 5, threshold 23,929: slices J0..J1 of 4000 (16 core-hours in all)
  seq "${2:-0}" "${3:-${2:-0}}" | xargs -P "${NPROC:-1}" -I{} sh -c '../bb3 5 23929 4000 {} 10 > bb3_s{}.out 2> /dev/null'
  for j in $(seq "${2:-0}" "${3:-${2:-0}}"); do echo "bb3_s$j.out"; done > bb5_list.txt
  awk 'NR==FNR {w[$1]; next} ($2 in w)' bb5_list.txt ../data/n5_bb3_slices.sha256 > bb5_sums.txt
  [ "$(wc -l < bb5_sums.txt)" = "$(wc -l < bb5_list.txt)" ]
  sha256sum -c --quiet bb5_sums.txt && echo "$(wc -l < bb5_list.txt) slices: OK" ;;
merge5)  # after "bb5 0 3999" and "countmax 5": merge the slices and compare with the block method
  python3 ../bb3merge.py 23929 max_n5.txt bb3_s*.out ;;
*)
  echo "usage: $0 brute | n3full | n3 | block N | block5sum | countmax N | bb4 | bb5 [J0 J1] | merge5" >&2; exit 2 ;;
esac
