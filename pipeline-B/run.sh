#!/bin/sh
# Pipeline B: the independent second computation of the upper bound for the double-six board.
# usage (from any directory, after "make" at the top level):
#     pipeline-B/run.sh STEP
#     STEP = tables | count | example | dangerous | mcheck | classes | sat | summary | witnesses |
#            control | enctest | compare
# sat compares its result with data/res_T853985.jsonl (code/cmpjsonl.py, timings ignored).
# Generated files go to pipeline-B/work/ and are checked against data/SHA256SUMS where possible.
# T (default 853985) is the target M.  NPROC (default 1) is the number of parallel SAT jobs;
# OMP_NUM_THREADS (default 1) sets the threads of the C programs.  The SAT steps need kissat
# (KISSAT, default "kissat" on PATH) and drat-trim (DRAT_TRIM, default code/drat-trim).
set -e
cd "$(dirname "$0")"
T=${T:-853985}
NPROC=${NPROC:-1}
export OMP_NUM_THREADS=${OMP_NUM_THREADS:-1}
KISSAT=${KISSAT:-kissat}
DRAT_TRIM=${DRAT_TRIM:-$(pwd)/code/drat-trim}
export KISSAT DRAT_TRIM
mkdir -p work
check() { (cd work && grep " $1\$" ../data/SHA256SUMS | sha256sum -c -); }
need_tables() { [ -f work/nb.bin ] || code/tile work; }
need() {  # need kissat|drat-trim: stop with a clear message if the program cannot be run
  case $1 in kissat) p=$KISSAT; v=KISSAT;; *) p=$DRAT_TRIM; v=DRAT_TRIM;; esac
  command -v "$p" > /dev/null || { echo "run.sh: cannot run $1 ($p). Install it (README, section External software)" >&2;
    echo "and put it on PATH or set $v=/path/to/$1." >&2; exit 1; }
}

case "$1" in
tables)    # all tilings, flip table, bipartition (about 240 MB in work/)
  code/tile work ;;
count)     # direct counts over all tilings
  need_tables
  code/count work 00060465/20504626/52012466/45122236/51312333/11143035/61444355 \
                  06151146/66611014/56132144/55326224/53632022/34300525/33040054 \
                  66110144/26611514/52132140/55322200/53242006/36430565/33643054 ;;
example)   # one CNF, one kissat proof, one drat-trim check (S = {9}); see the README
  need kissat; need drat-trim; need_tables
  mkdir -p work/st; echo '{9}' > work/example_set.txt
  code/comp work work/example_set.txt 0 work/st > /dev/null
  python3 code/onecnf.py work/st/00000000200.txt work/example.cnf
  rc=0; "$KISSAT" -q --no-binary work/example.cnf work/example.drat || rc=$?
  echo "kissat exit code $rc (20 = unsatisfiable)"
  "$DRAT_TRIM" work/example.cnf work/example.drat | tr -d '\r' | grep '^s '
  sha256sum work/example.drat
  echo "expected: 973a2a95528dea142c6df047e467e12c936ba899e97a24e969b8f074b37812aa (data/res_T853985.jsonl, B=[9])" ;;
dangerous) # D = {B : N - nu(H_B) > T}, up to symmetry; evaluated sets outside D go to _boundary
  need_tables
  code/dset work "$T" work/T$T > work/dset_$T.log; tail -1 work/dset_$T.log
  cmp work/dset_$T.log data/dset_$T.log && echo "dset_$T.log identical to data/"
  check T${T}_D.txt; check T${T}_boundary.txt ;;
mcheck)    # Hopcroft-Karp with explicit verification for every boundary set
  code/mcheck work "$T" < work/T${T}_boundary.txt > work/mcheck.out
  check mcheck.out ;;
classes)   # classes and quotient edges of every set of the control family (a superset of D)
  [ -f work/T853984_D.txt ] || T=853984 sh ./run.sh dangerous
  mkdir -p work/st
  code/comp work work/T853984_D.txt 0 work/st > work/comp_all.out
  check comp_all.out ;;
sat)       # branch and bound with SAT; every UNSAT proof is checked by drat-trim (CNFs in work/cnf_T$T)
  need kissat; need drat-trim; mkdir -p work/cnf_T$T
  python3 code/runall.py work/T${T}_D.txt work/st "$T" work/cnf_T$T work/res_T$T.jsonl "$NPROC"
  if [ "$T" = 853985 ]; then python3 code/cmpjsonl.py work/res_T853985.jsonl data/res_T853985.jsonl; fi ;;
summary)   # totals of a SAT run (default: the shipped one)
  python3 code/summarize.py work/T${T}_D.txt "${RES:-data/res_T853985.jsonl}" work/witnesses_T$T.txt ;;
witnesses) # count the solutions of every SAT witness directly
  python3 code/summarize.py work/T853985_D.txt data/res_T853985.jsonl work/witnesses_T853985.txt > /dev/null
  check witnesses_T853985.txt
  code/check_arrays work < work/witnesses_T853985.txt > work/witcheck.out
  check witcheck.out ;;
control)   # the whole computation with target 853,984: exactly one set must exceed it
  [ -f work/T853984_D.txt ] || T=853984 sh ./run.sh dangerous
  T=853984 sh ./run.sh sat
  T=853984 RES=work/res_T853984.jsonl sh ./run.sh summary
  python3 -c "
import json, sys
R = [json.loads(l) for l in open('work/res_T853984.jsonl')]
ex = [(d['B'], d['best_weight']) for d in R if d['verdict'] == 'EXCEEDS_T']
other = sorted(set(d['verdict'] for d in R if d['verdict'] != 'EXCEEDS_T'))
print('sets', len(R), 'EXCEEDS_T:', ex, 'other verdicts:', other)
sys.exit(0 if len(R) == 11326 and ex == [([10, 15, 19, 31], 853985)] and other == ['LE_T'] else 1)" ;;
enctest)   # 220 instances known to be realizable must all be SAT
  need kissat; need_tables; mkdir -p work/enc
  python3 code/enc_test.py work work/enc 200 > work/enc_test.log; tail -1 work/enc_test.log
  cmp work/enc_test.log logs/enc_test.log && echo "enc_test.log identical to logs/" ;;
compare)   # compare with pipeline A (needs pipeline-A/run.sh dangerous, and dangerous + classes here)
  python3 code/compare.py ../pipeline-A/data ../pipeline-A/work data work > work/compare.log
  cmp work/compare.log logs/compare.log && echo "compare.log identical to logs/"
  check old_joint_arrays.txt
  code/check_arrays work < work/old_joint_arrays.txt > work/old_joint_arrays_check.out
  check old_joint_arrays_check.out ;;
*)
  echo "usage: $0 tables|count|example|dangerous|mcheck|classes|sat|summary|witnesses|control|enctest|compare" >&2; exit 1 ;;
esac
