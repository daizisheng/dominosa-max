# pipeline-B/ — second, independent computation of the upper bound (n = 6)

Written separately from pipeline A; the two share no code. The differences that matter:

| step | pipeline A | pipeline B |
|---|---|---|
| tilings and flips | enumeration + union–find (`bsearch.c`) | enumeration, sorted (H,V) masks, 42-column flip table (`tile.c`) |
| ν(H_S) | Hopcroft–Karp on the whole graph | augmenting paths (Kuhn), component by component (`dset.c`); for the 9,530 sets found *outside* D, Hopcroft–Karp again with explicit verification of every matching (`mcheck.c`) |
| classes | union–find | breadth-first search (`comp.c`) |
| question asked | realizable: bad(A) ⊆ S | exactly realizable: bad(A) = S |
| SAT encoding | `satb2.py` / `satb3.py` | `enc.py` (one-hot cells, 28 pair variables per domino defined in both directions) |
| symmetry breaking (renaming of the numbers) | the top left cell is fixed to 0 | the seven doubles {0,0}, …, {6,6} occur in this order along the dominoes of the first tiling of the query |
| solver, certificates | CaDiCaL / Glucose 4 | kissat 4.0.4 with text DRAT proofs, every proof checked by drat-trim; every SAT model decoded and its solutions counted directly |

Exact realizability gives two further prunings without SAT: two classes joined by a flip in a block
of S cannot both consist of solutions (Lemma 2), and no class contains such a flip (heights at the
centres of S are constant on a class). `driver.py` runs the branch and bound of Section 6 over the
classes in decreasing size; an UNSAT answer is kept for all supersets, a SAT model is kept as a
witness for the whole family of classes it makes solutions.

## Requirements

* gcc with OpenMP; Python 3 (numpy only for `enc_test.py`); no Python package is needed otherwise.
* kissat 4.0.4 and drat-trim, for the steps `example`, `sat`, `control`, `enctest` only. Exact
  versions, install commands and how the scripts find them (`KISSAT`, `DRAT_TRIM`) are in the top
  README, section "External software", together with a worked example (`./run.sh example`).

Build with `make pipeline-B` in the top directory.

## Steps

`./run.sh STEP` (or `pipeline-B/run.sh STEP` from the top). Generated files go to `work/`; where
a step regenerates a file of the original run, its sha256 is checked against `data/SHA256SUMS`
(`sha256sum -c` prints `OK`). Times "here" are measured on one core of an Intel Xeon Platinum
8375C on an idle machine (a loaded or hyperthreaded machine can be 1.2–2 times slower); the original run used 12 parallel processes on a 32-thread machine of the same type, about
20.5 core-hours in all.

| step | what | expected result | time here |
|---|---|---|---|
| `tables` | all tilings, flip table, 2-colouring (writes 240 MB to `work/`) | 1,292,697 tilings, 8,828,108 flips, connected, bipartite, colour classes 646,349 / 646,348 | 3 s |
| `count` | direct counts | 853985, 807752, 730924; bad sets {10,15,19,31}, {10,15,19,31,33}, {8,10,15,19,29,31,33} | 1 s |
| `example` | one CNF, one kissat proof, one drat-trim check | see the top README; proof sha256 `973a2a95…` as in `data/res_T853985.jsonl` | 3 s |
| `dangerous` | D for T = 853,985 | `data/dset_853985.log`: 11,324 non-empty sets (12/197/1,290/3,319/3,774/2,109/534/88/1), 9,530 evaluated sets outside D; `T853985_D.txt`, `T853985_boundary.txt`: OK | 9 min |
| `mcheck` | re-check of the 9,530 boundary sets | `sets 9530 OK 9530 INSIDE 0`; `mcheck.out`: OK | 9 min |
| `classes` | classes and quotient edges of the 11,326 sets of the control family (a superset of D), one structure file per set in `work/st/` | `comp_all.out`: OK; 572,990 classes (572,904 for the 11,325 sets of D); no class contains a flip in a block of S | 45 min (use `OMP_NUM_THREADS`) |
| `sat` | branch and bound with SAT for every set of D (`NPROC` parallel jobs; CNFs and proofs in `work/cnf_T853985/`, deleted after use) | `work/res_T853985.jsonl`; `code/cmpjsonl.py` compares it with `data/res_T853985.jsonl` set by set, ignoring timings; expected: all 11,325 sets identical (answers, arrays, proof sizes and sha256) | about 9.5 core-hours (4 h in kissat, 5 h in drat-trim) |
| `summary` | totals of `data/res_T853985.jsonl` (or of `RES=work/...`) | 11,325 sets, all `LE_T`; 15,296 SAT calls, 13,786 UNSAT, all proofs `s VERIFIED`, 1,510 SAT, 0 failures; printed as `sets needing one call: 10111; max calls per set: 43`; best totals 853,985 (only {10,15,19,31}), 846,461, 839,062, 834,082, 828,810, 826,452; DRAT 102.5 GB in all, largest 34.0 MB | 1 s |
| `witnesses` | the 1,510 SAT arrays (in sorted order of B, whatever the order of the jsonl lines), counted directly | `witnesses_T853985.txt`, `witcheck.out`: OK; in each case the count equals the total size asked for, the bad set is S, no class is half solutions | 7 min |
| `control` | everything again with target 853,984 (CNFs in `work/cnf_T853984/`; D is computed only if `work/T853984_D.txt` is missing, e.g. after `classes`) | one more dangerous set, {3,17,19,26,29,31} (ν = 438,712, bound 853,985); 15,272 calls, 13,762 UNSAT (all verified), 1,510 SAT; exactly one set `EXCEEDS_T`, {10,15,19,31} with 853,985 | about 10 core-hours |
| `enctest` | 220 instances known to be realizable (200 random, 20 from A\* and González-Morris under random symmetries and renamings) | `FAILS 0`, identical to `logs/enc_test.log` | 17 s |
| `compare` | comparison with pipeline A (after `pipeline-A/run.sh dangerous` and `dangerous`, `classes` here) | identical to `logs/compare.log`: same 11,324 sets, the same 20,855 candidate sets (with the empty set) with the same bounds, the 493 joint maxima of A equal to the best totals of B over subsets, the 350 largest classes equal; the 493 arrays of A counted again (`old_joint_arrays*.txt`: OK) | 2.5 min |

To run the SAT step for one set only:

```
python3 code/driver.py work work/st/<mask>.txt 853985 work/cnf     # <mask> = block mask, 11 hex digits
```

## DRAT proofs

The 13,786 proofs of the main run took 102.5 GB and were deleted after drat-trim had verified
them. They can be regenerated: the CNF of each call is a deterministic function of S and of the
representative tilings in the structure file (the first tiling of each class in the sorted list of
all tilings), and kissat is deterministic, so `driver.py` reproduces each proof byte for byte.
The size and sha256 of every proof are in `data/res_T853985.jsonl` (fields `drat_bytes`,
`drat_sha256`). The 28 proofs for S = ∅, {9}, {10,11,12,19,22,24} (the largest, 34.0 MB) and
{10,15,19,31} (25 proofs) were regenerated for this repository, all with the recorded sha256.

## Files

* `code/common.h`: board conventions (cell 8r+c, block 7r+c, tiling = masks H, V) and loading of
  the tables written by `tile.c`.
* `code/tile.c`, `count.c`, `dset.c`, `mcheck.c`, `comp.c`, `check_arrays.c`: see the steps above.
* `code/enc.py` (CNF), `driver.py` (branch and bound for one set), `runall.py` (all sets,
  resumable; lines in order of completion), `summarize.py` (processes the sets in sorted order of B),
  `cmpjsonl.py` (comparison of two result files keyed by B, timings ignored), `enc_test.py`,
  `compare.py`, `onecnf.py` (CNF of one call).
* `data/res_T853985.jsonl`: one JSON line per set: verdict, best total and an array attaining it,
  and for every SAT call the classes asked for (`fam`, indices into the structure file; `sizes`),
  CNF size, answer, and for UNSAT the proof size, sha256 and verification result.
* `data/dset_853985.log`, `dset_853984.log`: level counts of D for the two targets.
* `data/SHA256SUMS`: checksums of the regenerated outputs named above.
* `logs/compare.log`, `logs/enc_test.log`: expected outputs of `compare` and `enctest`.
