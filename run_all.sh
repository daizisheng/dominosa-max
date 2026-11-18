#!/bin/bash
# run_all.sh NPROC -- the complete reproduction in one command: every step of every directory.
#
# Runs the quick checks first, then three independent chains at the same time, each with about
# NPROC/3 parallel jobs: pipeline A, pipeline B, and small/ (n = 3 slices, n = 5).  Then the
# comparisons between the pipelines and the transfer-matrix check of all classes.  Each step prints
# PASS or FAIL with its wall time; its output is in run_all_logs/STEP.log.  The exit status is the
# number of failed steps.
#
# Cost: about 75 core-hours in all (pipeline A ~30, pipeline B ~22, n = 5 branch and bound ~16,
# the rest a few).  The steps of pipeline B that need kissat and drat-trim are reported as SKIP if
# these are not found (KISSAT, DRAT_TRIM; see README, section External software).
N=${1:?usage: run_all.sh NPROC}
cd "$(dirname "$0")" || exit 1
make -s all || exit 1
LOG=run_all_logs; mkdir -p $LOG; rm -f $LOG/*.status
P=$(( N / 3 )); [ $P -ge 1 ] || P=1
export OPENBLAS_NUM_THREADS=1
KISSAT=${KISSAT:-kissat}; DRAT_TRIM=${DRAT_TRIM:-$(pwd)/pipeline-B/code/drat-trim}; export KISSAT DRAT_TRIM
if command -v "$KISSAT" > /dev/null && command -v "$DRAT_TRIM" > /dev/null; then SAT=1; else SAT=0; fi

step() {  # step NAME COMMAND...: run, record PASS/FAIL and the time
  local name=$1 t0=$(date +%s) r; shift
  if "$@" > $LOG/$name.log 2>&1; then r=PASS; else r=FAIL; fi
  printf "%s  %-24s %6d s\n" $r $name $(( $(date +%s) - t0 )) | tee $LOG/$name.status
}
skip() { printf "SKIP  %-24s (kissat or drat-trim not found)\n" $1 | tee $LOG/$1.status; }

step quick ./run_quick.sh

chainA() {
  export NPROC=$P
  step A-dangerous   pipeline-A/run.sh dangerous
  step A-single      pipeline-A/run.sh single
  step A-single3     pipeline-A/run.sh single3
  step A-classes     pipeline-A/run.sh classes
  step A-fullb       pipeline-A/run.sh fullb
  step A-joint       pipeline-A/run.sh joint
  step A-rbound      pipeline-A/run.sh rbound
  step A-rbound-data pipeline-A/run.sh rbound-data
}
chainB() {
  export NPROC=$P OMP_NUM_THREADS=$P
  step B-dangerous   pipeline-B/run.sh dangerous
  step B-mcheck      pipeline-B/run.sh mcheck
  step B-classes     pipeline-B/run.sh classes
  step B-witnesses   pipeline-B/run.sh witnesses
  if [ $SAT = 1 ]; then
    step B-enctest   pipeline-B/run.sh enctest
    step B-sat       pipeline-B/run.sh sat
    step B-summary   env RES=work/res_T853985.jsonl pipeline-B/run.sh summary
    step B-control   pipeline-B/run.sh control
  else
    skip B-enctest; skip B-sat; skip B-summary; skip B-control
  fi
}
chainS() {
  export NPROC=$P
  step S-n3full      small/run.sh n3full
  step S-n3          bash -c "seq 0 11 | xargs -P $P -I{} env J={} small/run.sh n3"
  step S-block5-0    env J=0 small/run.sh block 5
  step S-block5      bash -c "seq 1 8 | xargs -P $P -I{} env J={} small/run.sh block 5"
  step S-block5sum   small/run.sh block5sum
  step S-countmax5   small/run.sh countmax 5
  step S-bb5         small/run.sh bb5 0 3999
  step S-merge5      small/run.sh merge5
}
chainA & chainB & chainS & wait

export NPROC=$N
step B-compare     pipeline-B/run.sh compare
step A-B-classes   python3 pipeline-A/cmpclasses.py pipeline-A/work/classes.txt pipeline-B/work/comp_all.out
step heights-xcheck python3 heights/xcheck_tm.py pipeline-B/work/comp_all.out $N

pass=$(cat $LOG/*.status | grep -c '^PASS'); fail=$(cat $LOG/*.status | grep -c '^FAIL'); sk=$(cat $LOG/*.status | grep -c '^SKIP')
echo; echo "run_all: $pass passed, $fail failed, $sk skipped (logs in $LOG/)"
exit $fail
