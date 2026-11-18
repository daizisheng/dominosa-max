# The maximum number of solutions of a Dominosa array

Programs that reproduce the computations of the note by Shisheng Li, "The maximum number of
solutions of a Dominosa array (exercise 7.2.2.1–73 of Volume 4B)",
<https://shisheng.li/4b-q-7221-73-notes/notes-4b-q-7221-73.pdf>.

## The claim

Exercise 7.2.2.1–73 of *The Art of Computer Programming*, Volume 4B, asks for the largest number of
solutions of a Dominosa instance: a 7×8 array of numbers 0–6 to be covered by the 28 pieces of a
double-six set, each piece used once. The claim (computer-assisted) is that the maximum is
**853,985**, attained for example by

```
A* = 00060465/20504626/52012466/45122236/51312333/11143035/61444355     (rows separated by /)
```

## How the argument works

Call a 2×2 square of cells *good* if one of its diagonals carries two equal numbers. Turning two
parallel dominoes in a square keeps the multiset of pieces exactly when the square is good, so the
solutions of an array are whole classes of tilings under such turns, and the classes depend only
on the set S of bad squares. If S is large, a matching in the graph of turns in S bounds the
number of solutions; this leaves 11,325 sets S (up to symmetry). For each of them the classes are
computed and SAT tests show that no choice of numbers makes classes of more than 853,985 tilings
into solutions. The same method, checked by methods that use no squares at all, gives the maxima
3, 10, 88, 1012, 23929 for the double-one to double-five sets.

The upper bound was computed twice, by two separately written sets of programs (pipelines A and
B), and the classes a third time by a transfer matrix built on Thurston's height function.

## What is here

| directory | reproduces |
|---|---|
| [`count/`](count/) | the count 853,985 for A\* by four independent counters, 807,752 and 730,924 for the earlier records, placement counts, the 34 classes of A\*, and how the largest class splits for González-Morris's array |
| [`pipeline-A/`](pipeline-A/) | first computation of the upper bound: dangerous sets, classes (union–find), realizability (CaDiCaL; second encoding with Glucose); the 19,601 essentially different arrays with 853,985 solutions |
| [`pipeline-B/`](pipeline-B/) | second, independent computation: dangerous sets with verified matchings, classes (breadth-first search), exact realizability with kissat, every UNSAT answer with a DRAT proof checked by drat-trim, every SAT answer counted directly; control run with target 853,984 |
| [`heights/`](heights/) | classes by the transfer matrix, compared with all classes of pipeline B; flips per block |
| [`small/`](small/) | n = 1..5: exhaustive search (n ≤ 3), the block method (n ≤ 5), branch and bound over arrays (n = 4, 5) |

Each directory has a README and a `run.sh` with one step per computation. Results go to `work/`
subdirectories (ignored by git) and are compared with the expected outputs in `data/` and `logs/`,
or with the sha256 checksums in `data/SHA256SUMS`.

## Requirements

* gcc (13.3 was used) with OpenMP (`libgomp`), GNU make (4.3), bash, coreutils (`sha256sum`).
* Python 3 (3.12.3 was used) with the packages of `requirements.txt`. On Debian or Ubuntu, where
  the system Python refuses `pip install` (PEP 668, "externally managed environment"), use a virtual
  environment:

  ```
  sudo apt install build-essential python3-venv
  python3 -m venv venv && . venv/bin/activate
  pip install -r requirements.txt      # python-sat==1.9.dev2 numpy==2.4.2 scipy==1.17.1 networkx==3.6.1
  ```

  `python-sat` is used by pipeline A and `small/`, `numpy` and `scipy` by `small/blk.py` (and
  `numpy` by `pipeline-B/code/enc_test.py`), `networkx` by `heights/ucheck.py` and `small/dom.py`.
  No other third-party Python package is imported.
* For the SAT steps of pipeline B only: kissat 4.0.4 and drat-trim (next section).

```
make            # builds all C programs with gcc -O2
make quick      # builds, then runs run_quick.sh (about 2 minutes)
./run_all.sh 64 # everything, with 64 parallel jobs (see "Full reproduction in one command")
```

## External software

| tool | what it does in the proof | used by | version used |
|---|---|---|---|
| **kissat** | decides every SAT question of pipeline B (is there an array with bad set exactly S for which the given classes consist of solutions?) and writes a DRAT proof for every UNSAT answer | `pipeline-B/code/driver.py` (called by `runall.py`, `run.sh sat`, `run.sh control`), `enc_test.py`, `run.sh example` | 4.0.4; the reproduction checks below used build id `8af8e56f174b778aef3aa45af9f739b2a5f492c2` (`kissat --id`) |
| **drat-trim** | checks every DRAT proof written by kissat | `pipeline-B/code/driver.py`, `run.sh example` | `drat-trim.c` with the header line "Last edit: April 21, 2024", sha256 `d834b649f437e091597f5347f259b9f681087f89ca0844d0cee250a1a1a0c2ee` |
| **CaDiCaL** (in python-sat, solver name `cadical153`, i.e. CaDiCaL 1.5.3) | the realizability tests of pipeline A (single classes, joint collections, the arrays of the record family) and the primary tests for n ≤ 5 | `pipeline-A/satb2.py`, `multi.py` (used by `joint.py`), `fullb.py`, `rbound.py`, `enumrec.py`; `small/satenc.py` (Enc1) | python-sat 1.9.dev2 |
| **Glucose 4** (in python-sat, solver name `glucose4`) | the second, independent encoding: re-checks pipeline A's single-class tests, and every UNSAT answer for n ≤ 5 | `pipeline-A/satb3.py`; `small/satenc.py` (Enc2) | python-sat 1.9.dev2 |
| python-sat cardinality encodings (`pysat.card`) | "each number occurs n+2 times" | `pipeline-A/satb2.py`, `multi.py`; `small/satenc.py` | python-sat 1.9.dev2 |

**Installing kissat**

```
git clone https://github.com/arminbiere/kissat.git
cd kissat
git checkout 8af8e56f174b778aef3aa45af9f739b2a5f492c2
./configure && make
build/kissat --version      # must print 4.0.4
build/kissat --id           # must print 8af8e56f174b778aef3aa45af9f739b2a5f492c2
```

**Installing drat-trim**

```
git clone https://github.com/marijnheule/drat-trim.git
cd drat-trim
sha256sum drat-trim.c       # must be d834b649f437e091597f5347f259b9f681087f89ca0844d0cee250a1a1a0c2ee
# if the current file differs, find a commit with that file and check it out:
#   for c in $(git log --format=%H -- drat-trim.c); do
#     [ "$(git show $c:drat-trim.c | sha256sum | cut -c1-64)" = d834b649f437e091597f5347f259b9f681087f89ca0844d0cee250a1a1a0c2ee ] && echo $c; done
gcc -O2 -o drat-trim drat-trim.c
```

**python-sat** is installed by `pip install python-sat==1.9.dev2`; check it with
`python3 -c "import pysat; print(pysat.__version__)"`, which prints `1.9.dev2`. Its solvers are
called through the Python API; no separate binaries are needed.

**How the scripts find kissat and drat-trim.** Through `KISSAT` (default: `kissat` on `PATH`) and
`DRAT_TRIM` (default: `pipeline-B/code/drat-trim`, so the binary can simply be copied there).
`pipeline-B/run.sh` and `driver.py` stop with a message naming the variable if either program
cannot be run. They are called as

```
$KISSAT -q --no-binary FILE.cnf FILE.drat       # exit code 10 = SAT (model on stdout), 20 = UNSAT
$DRAT_TRIM FILE.cnf FILE.drat -t 40000          # proof accepted if the output contains "s VERIFIED"
```

**Worked example** (`pipeline-B/run.sh example` does all of this, in 3 seconds). The first SAT test
for the set S = {9} asks whether the largest of its three classes (987,184 tilings) can consist of
solutions of an array whose only bad block is block 9.

```
make pipeline-B && cd pipeline-B
code/tile work                                        # all tilings and flips, written to work/
echo '{9}' > work/example_set.txt && mkdir -p work/st
code/comp work work/example_set.txt 0 work/st         # classes of S = {9}: work/st/00000000200.txt
python3 code/onecnf.py work/st/00000000200.txt work/example.cnf
    B=[9] classes [0] sizes [987184]: 1258 variables, 19053 clauses -> work/example.cnf
$KISSAT -q --no-binary work/example.cnf work/example.drat; echo $?
    s UNSATISFIABLE
    20
$DRAT_TRIM work/example.cnf work/example.drat | tr -d '\r' | grep '^s '
    s VERIFIED
sha256sum work/example.drat
    973a2a95528dea142c6df047e467e12c936ba899e97a24e969b8f074b37812aa  work/example.drat
```

The proof has 1,230,385 bytes; its size and sha256 are those recorded for this test (`"B": [9]`,
first entry of `"log"`) in `pipeline-B/data/res_T853985.jsonl`.

## Quick checks

```
make quick          # or: ./run_quick.sh
```

builds everything and runs 34 checks in about 2 minutes on one core, printing `PASS` or `FAIL` for
each and ending with `quick checks: 34 passed, 0 failed`:

* `count/`: `dc` gives 853985 for A\*, 807752 for González-Morris's array
  (`06151146/66611014/56132144/55326224/53632022/34300525/33040054`) and 730924 for Keller's
  (`66110144/26611514/52132140/55322200/53242006/36430565/33643054`); three other counters agree;
  every placement occurs in at least 37,207 solutions of A\* (35,082 for González-Morris); A\*'s bad
  blocks (1,3), (2,1), (2,5), (4,3) give 34 classes, the largest 853985, 95456, 95456, 60344,
  39800; making block (4,5) bad as well splits the largest class into 807752 + 28239 + 17994.
* `heights/`: the transfer matrix gives the same 34 classes; Lemma 5 tested on 1,112 random sets.
* `small/`: n = 1, 2 by brute force (maxima 3 and 10); n = 3, all 11,732,745,024 arrays (maximum 88,
  attained by 1,536 arrays, next value 83); the block method for n = 1..4 (3, 10, 88, 1012); the
  120,960 optimal arrays for n = 4 (252 up to symmetry), confirmed by branch and bound.
* `pipeline-B/`: all 1,292,697 tilings and 8,828,108 flips; the worked example above if kissat and
  drat-trim are installed (otherwise `SKIP`).
* `pipeline-A/`: the 19,601 essentially different arrays with 853,985 solutions, A\* first,
  identical to the original list (sha256), each counted again.

## Full reproduction in one command

```
./run_all.sh NPROC
```

runs the quick checks, then the three long chains (pipeline A, pipeline B, small/) at the same
time with about NPROC/3 parallel jobs each, then the comparisons between the pipelines and the
transfer-matrix check of all classes. It prints `PASS`, `FAIL` or `SKIP` (kissat or drat-trim not
found) for every step, with its wall time, keeps each step's output in `run_all_logs/`, and ends
with a count of the failures. The whole computation costs about 75 core-hours; an independent
reproduction of all steps took about 75 minutes of wall time on 256 cores. The wall time cannot
drop much below an hour, because `pipeline-A/run.sh joint` gives each of its sets up to
`JOINT_TIMEOUT` = 3000 s.

## Full reproduction and the numbers to compare

Times "here" are for one core of an Intel Xeon Platinum 8375C (2.9 GHz), measured on an otherwise
idle machine; on a loaded machine, or with two processes per core (hyperthreading), expect 1.2 to 2
times longer. The original runs used a 32-thread machine of the same type: pipeline A about 37
core-hours, pipeline B about 20.5. The steps that take hours accept `NPROC`, the number of parallel
jobs (`pipeline-A/run.sh single3|fullb|joint|rbound|rbound-data`, `pipeline-B/run.sh sat|control`,
`small/run.sh bb5`); the C programs of pipeline B use `OMP_NUM_THREADS` threads.

### Dangerous sets (both pipelines)

```
pipeline-A/run.sh dangerous      # 9 min here
pipeline-B/run.sh dangerous      # 9 min here (builds the tiling tables first)
pipeline-B/run.sh mcheck         # 9 min here
```

| size of S | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | total |
|---|---|---|---|---|---|---|---|---|---|---|---|
| dangerous sets (up to symmetry) | 1 | 12 | 197 | 1,290 | 3,319 | 3,774 | 2,109 | 534 | 88 | 1 | 11,325 |

Both pipelines evaluate the same 20,854 nonempty candidate sets with the same matching bounds; the
9,530 sets found not dangerous are re-checked by an explicitly verified Hopcroft–Karp matching
(`sets 9530 OK 9530 INSIDE 0`). Flips per block (r,c), for r ≤ 2, c ≤ 3 (all 42 blocks up to
symmetry); 8,828,108 flips in all:

```
388705 183779 306167 203435
228897  85612 175534  92686
287253 115368 224589 126125
```

### Classes (three methods)

```
pipeline-B/run.sh classes        # 45 min on one core; set OMP_NUM_THREADS to use more
pipeline-A/run.sh classes        # 4 min here
python3 pipeline-A/cmpclasses.py pipeline-A/work/classes.txt pipeline-B/work/comp_all.out   # 0 mismatches
python3 heights/xcheck_tm.py     # 31 s: sets 11326 mismatches 0, total classes compared 572990
```

The 11,325 dangerous sets have 572,904 classes; the class file of pipeline B also covers the extra
set {3,17,19,26,29,31} of the control run (86 classes), 572,990 classes in all. For A\*'s bad blocks
the class sizes begin 853985, 95456, 95456, 60344, 39800.

### Realizability tests

Pipeline A (`pipeline-A/run.sh single`, `single3`, `fullb`, `joint`, `rbound`, `rbound-data`;
about 27 core-hours for `fullb` and `joint`): no class of more than 853,985 tilings is realizable
(350 sets, all UNSAT with both encodings); 10,822 non-empty dangerous sets (10,823 with ∅) are
settled by single-class tests, and the other 502 are `OPEN`. In the original run 493 of these were
settled by the exact joint maximum (all at most 853,985) and the last 9 by the refined matching
bound (718,025 to 780,001). Which `OPEN` sets `joint` finishes within `JOINT_TIMEOUT` depends on the
machine, so the invariant that is checked (`pipeline-A/checkopen.py`) is: every `OPEN` set ends with
`MAX joint` ≤ 853,985 or with an `rbound` bound ≤ 853,985. `rbound-data` computes the refined bound
for the 12 sets of `pipeline-A/data/rbound_all.out` directly. The outputs are compared with `data/`
line by line, up to symmetry (`pipeline-A/cmplines.py`).

Pipeline B (`pipeline-B/run.sh sat`, then `summary`; about 9.5 core-hours; the result is compared
with `pipeline-B/data/res_T853985.jsonl` set by set, timings ignored, by `pipeline-B/code/cmpjsonl.py`):

| quantity | value |
|---|---|
| SAT tests | 15,296 |
| unsatisfiable, each with a DRAT proof verified by drat-trim | 13,786 |
| satisfiable, each model counted directly (`run.sh witnesses`) | 1,510 |
| sets needing only one test | 10,111 (at most 43 tests for one set) |
| largest total of an exactly realizable collection | 853,985, only for A\*'s bad blocks {10,15,19,31} |
| next largest totals found | 846,461, 839,062, 834,082, 828,810, 826,452 |
| control run with target 853,984 (`run.sh control`) | one more dangerous set, {3,17,19,26,29,31}; 15,272 tests (13,762 UNSAT, all verified; 1,510 SAT); exactly one set exceeds the target, {10,15,19,31} |
| encoding completeness test (`run.sh enctest`) | 220 instances known to be realizable, all SAT |

An array with 846,461 solutions: `00211105/02221510/25233103/42335360/14343626/44456166/04555646`.

**DRAT proofs.** The 13,786 proofs of the main run took 102.5 GB (the largest 34.0 MB) and were
deleted after drat-trim had verified them. They can be regenerated: each CNF is a deterministic
function of S and of the class representatives written by `pipeline-B/run.sh classes`, kissat is
deterministic, and the size and sha256 of every proof are recorded in
`pipeline-B/data/res_T853985.jsonl`. For S = ∅, {9}, {10,11,12,19,22,24} (the largest proof) and
{10,15,19,31} (25 proofs), all 28 regenerated proofs had the recorded sha256.

### Smaller boards

| n | board | tilings | maximum | dangerous sets (up to symmetry) | optimal arrays (up to symmetry) | steps of `small/run.sh` |
|---|---|---|---|---|---|---|
| 1 | 2×3 | 3 | 3 | 0 | 4 (1) | `brute`, `block 1` |
| 2 | 3×4 | 11 | 10 | 1 | 240 (10) | `brute`, `block 2`, `countmax 2` |
| 3 | 4×5 | 95 | 88 | 2 | 1,536 (16) | `n3full` (20 s), `n3` (12 slices, 30 min), `block 3`, `countmax 3` |
| 4 | 5×6 | 1,183 | 1,012 | 6 | 120,960 (252) | `block 4`, `countmax 4`, `bb4` (15 s) |
| 5 | 6×7 | 31,529 | 23,929 | 115 | 101,341,440 (35,188) | `block 5` (9 parts, 50 min), `block5sum`, `countmax 5`, `bb5 0 3999` (4000 slices, about 30 s each, 16 core-hours), `merge5` |

## Data shipped

Only expected outputs that are small, or that cost many core-hours to regenerate, are included;
everything else is regenerated by the `run.sh` steps and checked against `data/SHA256SUMS`.

* `pipeline-A/data/`: the 11,324 dangerous sets (`Dlist.txt`), the 350 sets with a class of more
  than 853,985 tilings (`allcand.txt`), the results of the long SAT steps (`fb_all.out`,
  `joint_all.out`, `rbound_all.out`), and checksums of the bound files and of the record family.
* `pipeline-B/data/`: `res_T853985.jsonl`, the record of all 15,296 SAT tests with the size and
  sha256 of every DRAT proof (the only record of the deleted proofs); the level counts of D;
  checksums of D, the boundary sets, the verified matchings, the classes, the witnesses and their
  counts. `pipeline-B/logs/`: expected outputs of `run.sh compare` and `run.sh enctest`.
* `small/data/`: histograms for n ≤ 3, the block-method records and dangerous-set tables for n ≤ 5,
  the optimal-array counts for n ≤ 4, the merged summary of the n = 5 branch and bound, and
  checksums of the exhaustive and branch-and-bound outputs (one per slice for n = 5).

## Build and run check (18 November 2026)

Every C file compiles with `gcc -O2 -Wall -Wextra` (gcc 13.3) without warnings. Every C program
prints a usage line and exits with status 2 when called with wrong arguments, and exits with
status 1 on an invalid array (the counters accept exactly 7 rows of 8 digits 0–6 separated by `/`,
or the right shape for n in `small/cnt`) or an unwritable output file. On one core of a Xeon 8375C,
with `ulimit -v 4000000`:

* `make quick` in a clean clone: 34 passed, 0 failed, about 2 minutes.
* `count/`: dc gives 853985, 807752, 730924 (0.03 s each); `cnt`, `tilings`, `slowcount.py` agree;
  minimum placement counts 37207 and 35082; `classes`, `split`, `gen.py` give the class sizes above.
* `heights/`: `tm.py`, `hcheck.py`, `icount.py`, `ucheck.py` report no mismatch; `xcheck_tm.py`
  agrees with all 572,990 classes and recovers the table of flips.
* `small/`: brute force n = 1, 2 and `n3full` reproduce the histograms; `n3` slice 0 (bfa and bfb)
  has the recorded checksums; the block method n = 1..4 and `countmax` n ≤ 4 reproduce `data/`;
  `bb4` has the recorded checksums; the block method for n = 5 (9 parts, 50 min) reproduces `data/`
  (115 sets: 90 / 15 / 10, best 23,929), and `countmax 5` (48 s) gives the 35,188 classes of optimal
  arrays with the recorded checksum; `J=0 block 5` creates `D_n5_L23929.json` and part 0 (equal to
  `data/`), and `block5sum` refuses to run until all 9 parts are present; `NPROC=4 bb5 0 3` gives 4 slices with the recorded checksums
  (about 30 s per slice), and a corrupted slice is reported as `FAILED`.
* `pipeline-A/`: `dangerous` (9 min) reproduces `Dlist.txt` with the original representatives, all
  20,855 bounds, and, line for line, the original bounds of all 31,345 canonical sets of at most 4
  blocks; `classes` agrees with pipeline B on all 572,904 classes; `single` reproduces the 350 sets,
  all UNSAT with satb2 (20 of them also with satb3); with `NPROC=4`, `fullb` on 16 sets (12 `OK`,
  4 `OPEN`) gives 16 lines identical to `data/fb_all.out`, `joint` with `JOINT_TIMEOUT=60` finishes
  3 of the 4 `OPEN` sets with lines identical to `data/joint_all.out`, `rbound` settles the fourth
  with the line of `data/rbound_all.out`, and `checkopen.py` finds all 4 settled; `rbound-data`
  reproduces the 12 lines of `data/rbound_all.out`; `family` reproduces the 19,601 arrays byte for
  byte.
* `pipeline-B/`: `tables`, `count`; `dangerous` (520 s), `mcheck` (508 s), `witnesses` (409 s),
  `classes` (2,241 s in two halves) match their checksums; `enctest` gives `FAILS 0` and the shipped
  log; `driver.py` reproduces the 28 proofs named above; `compare` (2.5 min) reproduces
  `logs/compare.log`; `cmpjsonl.py` finds a sample of 23 sets identical to the shipped jsonl and
  reports a changed proof hash in another sample; `runall.py` with 2 jobs on S = ∅, {9},
  {10,15,19,31} (27 SAT calls, CNFs in `work/cnf_T853985/`) gives results identical to the shipped
  ones; `summarize.py` gives the same witness file whatever the order of the jsonl lines; `control`
  skips the computation of D when `work/T853984_D.txt` exists.
* `run_all.sh` was not run to the end here (it is the full 75 core-hours).

## Changes from the programs as originally run

The programs are the ones that produced the original results. They were changed only as follows;
no change affects a result.

* Paths: helper programs are found relative to the script; kissat, drat-trim and the tiling tables
  are given by `KISSAT`, `DRAT_TRIM`, `DATADIR`; a clear message is printed if kissat or drat-trim
  is missing.
* Robustness: every C program checks its arguments (usage line, exit status 2) and its input
  arrays; output files are checked when opened; the `-Wall -Wextra` warnings were removed (unused
  variables, misleading indentation, unused helper functions).
* `pipeline-A/bsearch.c`, `ub.c`, `ubv.c`, `ubr.c`: a set written `-` (the empty set) was read as
  {0}; now it is read and printed as the empty set. The results do not depend on this, since the
  empty set was treated separately (U(∅) = T, and its single class was tested directly).
* `pipeline-A/enumrec.py`: the final summary line read the wrong field and crashed after its output
  file had been written. `fullb.py` takes an option `satb3` instead of a separate copy.
* `heights/hcheck.py`, `ucheck.py`: the tests ran on import; now only when run as scripts. The
  checks of `heights/`, `small/` and `pipeline-A/` exit with status 1 when they fail.
* `pipeline-B/code/summarize.py` processes the sets in sorted order of B, so that the witness file
  does not depend on the order in which `runall.py` finished the sets, and prints the number of sets
  needing one call and the largest number of calls.
* `pipeline-B/code/compare.py` reads the regenerated bound files of pipeline A, so that all 20,854
  bounds are compared (20,855 with the empty set; the original comparison covered 14,661), and labels
  the two sides A and B; `logs/compare.log` was regenerated with it.
* New: `run_quick.sh`, `run_all.sh`, the `run.sh` scripts (with `NPROC` for the long steps),
  `pipeline-A/gensets.py` (the exhaustive enumeration of the sets of at most 4 blocks, as in the
  original run), `cmplines.py`, `checkopen.py`, `cmpsets.py`, `cmpclasses.py`,
  `pipeline-B/code/cmpjsonl.py`, `onecnf.py`, `small/histcmp.py`.
* Comments were shortened or translated, and usage lines added. `pipeline-A/data/joint_all.out` had
  27 duplicated lines from a repeated run; they were removed.

## What is not reproduced exactly

* The DRAT proofs are not shipped (102.5 GB); see above.
* `pipeline-A/run.sh family` depends on the order in which CaDiCaL finds models; with python-sat
  1.9.dev2 it reproduces the original list exactly, another version may give a different list
  (which can be checked with `count/cntf`).
* The heuristic searches used along the way for lower bounds (simulated annealing, sampled branch
  and bound) are not included; they prove nothing. A\* is the first model of the SAT test on its
  four bad blocks (`pipeline-A/run.sh family` prints it first).
* The long steps (pipeline A `fullb`, `joint`; pipeline B `sat`, `control`; n = 5 `bb5`) were not
  rerun for this repository; their results are in `data/`, and samples were rerun as stated above.

## License

Programs: MIT (see `LICENSE`). Data files (`data/`, `logs/`): CC0 1.0.
