#!/bin/bash
# run_quick.sh -- build everything and run the quick checks (about 2 minutes on one core).
# Same as "make quick".  Each check prints PASS or FAIL; the exit status is the number of failures.
# The SAT example of pipeline B runs only if kissat and drat-trim are found (KISSAT, DRAT_TRIM).
cd "$(dirname "$0")" || exit 1
make -s all || exit 1
ulimit -v 4000000 2> /dev/null
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
pass=0; fail=0; OUT=
run() { OUT=$("$@" 2>&1); }                       # run a command, keep its output in OUT
has() {                                             # has NAME PATTERN...: OUT contains every PATTERN
  local name=$1 p ok=1; shift
  for p in "$@"; do printf '%s\n' "$OUT" | grep -qF -- "$p" || { ok=0; echo "FAIL  $name: missing \"$p\""; }; done
  if [ $ok = 1 ]; then echo "PASS  $name"; pass=$((pass+1)); else fail=$((fail+1)); printf '%s\n' "$OUT" | tail -5 | sed 's/^/        /'; fi
}
hasnot() {                                          # hasnot NAME PATTERN: OUT does not contain PATTERN
  if printf '%s\n' "$OUT" | grep -qF -- "$2"; then echo "FAIL  $1: found \"$2\""; fail=$((fail+1)); printf '%s\n' "$OUT" | grep -F -- "$2" | head -5 | sed 's/^/        /'
  else echo "PASS  $1"; pass=$((pass+1)); fi
}

A=00060465/20504626/52012466/45122236/51312333/11143035/61444355
G=06151146/66611014/56132144/55326224/53632022/34300525/33040054
K=66110144/26611514/52132140/55322200/53242006/36430565/33643054

echo "== count/: direct counts on the 7x8 board"
run count/dc $A;            has "dc A* = 853985" "-> 853985"
run count/dc $G;            has "dc Gonzalez-Morris = 807752" "-> 807752"
run count/dc $K;            has "dc Keller = 730924" "-> 730924"
run count/cnt $A $G $K;     has "meet-in-the-middle counter" "$A 853985" "$G 807752" "$K 730924"
run count/tilings $A;       has "all tilings tested" "valid 853985 components 34 validcomps 1 mixed 0" "valid-valid 0"
run python3 count/slowcount.py $A;  has "Python counter" "$A 853985"
run count/place $A;         has "placements of A*: at least 37207" "min placement count 37207"
run count/place $G;         has "placements of Gonzalez-Morris: at least 35082" "min placement count 35082"
run count/classes $A;       has "34 classes of A*" "bad block 10 (1,3)" "bad block 15 (2,1)" "bad block 19 (2,5)" "bad block 31 (4,3)" \
                                "components 34, total solutions 853985" "largest components: 853985 95456 95456 60344 39800" \
                                "bad flips joining two solutions 0"
run count/split 10 15 19 31 33;  has "split by block (4,5)" "big 853985 splits into: 28239 807752 17994"
run python3 count/gen.py 001/011 0001/0211/2221 00011/20121/22313/23033 000112/201122/031342/323404/334144
has "optimal arrays n=1..4" "solutions=3 " "solutions=10 " "solutions=88 " "classes=[88, 6, 1]" "solutions=1012 " "classes=[1012, 60, 60, 21, 14, 14, 2]"

echo "== heights/: transfer matrix and Lemma 5"
run python3 heights/tm.py;  has "transfer matrix, A*" "classes 34 total 1292697 top [853985, 95456, 95456, 60344, 39800]" "classes 73 top [807752" "[23929, 2776, 1524, 1244, 540]"
run python3 heights/hcheck.py; has "Lemma 5 on random sets, n=2..5" "n=2:" "n=3:" "n=4:" "n=5:"; hasnot "Lemma 5: no mismatch" "MISMATCH"
run python3 heights/icount.py; has "I(S) by transfer matrix" "n 3 I mismatches 0" "n 4 I mismatches 0" "n 5 I mismatches 0"

echo "== small/: n = 1..4"
run small/run.sh brute;     has "brute force n=1,2" "n=1 bfa: arrays 20, max 3 (4 arrays)" "n=2 bfa: arrays 34650, max 10 (240 arrays)"; hasnot "brute force n=1,2 equal to data/" "False"
run bash -c "cd small && mkdir -p work && cd work && ../bfa 3 1 0 0 80 > bfa_n3.out && python3 ../histcmp.py 3 bfa bfa_n3.out"
has "every array for n=3" "arrays 11732745024, max 88 (1536 arrays), identical to data/histograms_n123.tsv: True"
for nm in "1 3" "2 10" "3 88" "4 1012"; do
  set -- $nm
  run small/run.sh block $1; has "block method n=$1" "max best(B): $2"; hasnot "block method n=$1 equal to data/" "False"
done
run small/run.sh countmax 4; has "optimal arrays n=4 (AllSAT)" "{'1012': 120960}" "{'1012': 252}"; hasnot "countmax n=4 equal to data/" "False"
run small/run.sh bb4;       has "branch and bound n=4" "bb4_900.out: OK" "bb4_1012.out: OK" "orbits from bb4_900.out: 252; from block method: 252; equal: True"

echo "== pipeline-B/: tables, counts, one proof"
run pipeline-B/run.sh tables; has "tilings and flips" "tilings: 1292697" "flip edges: 8828108" "same-colour edges 0" "colour classes 646349 / 646348"
run pipeline-B/run.sh count;  has "counts over all tilings" "solutions=853985 bad={10,15,19,31}" "solutions=807752 bad={10,15,19,31,33}" "solutions=730924"
KISSAT=${KISSAT:-kissat}; DRAT_TRIM=${DRAT_TRIM:-$(pwd)/pipeline-B/code/drat-trim}
if command -v "$KISSAT" > /dev/null && command -v "$DRAT_TRIM" > /dev/null; then
  run env KISSAT="$KISSAT" DRAT_TRIM="$DRAT_TRIM" pipeline-B/run.sh example
  has "CNF, kissat proof, drat-trim (S={9})" "kissat exit code 20" "s VERIFIED" "973a2a95528dea142c6df047e467e12c936ba899e97a24e969b8f074b37812aa  work/example.drat"
else
  echo "SKIP  CNF/DRAT example: kissat or drat-trim not found (set KISSAT, DRAT_TRIM)"
fi

echo "== pipeline-A/: the 19,601 essentially different arrays with 853,985 solutions"
run pipeline-A/run.sh family; has "family by SAT" "solutions 20000 distinct canonical 19601" "family.txt: OK"
run bash -c "count/cntf < pipeline-A/work/family.txt | awk '{print \$1}' | sort | uniq -c"; has "all 19601 have 853985 solutions" "19601 853985"

echo
echo "quick checks: $pass passed, $fail failed"
exit $fail
