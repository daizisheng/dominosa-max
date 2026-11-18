# pipeline-A/ — first computation of the upper bound (n = 6)

This is the first of the two independent computations of Section 11 of the note. It uses
union–find for the classes, Hopcroft–Karp for the matchings, and tests *realizability*
(bad(A) ⊆ S) with the SAT encoding `satb2.py` (CaDiCaL, through PySAT). A second, independent
encoding `satb3.py` (Glucose 4) was used to repeat the single-class tests and a sample of the others.

Requirements: a C compiler and Python 3 with the packages of the top-level `requirements.txt`
(`pip install -r requirements.txt`, which pins python-sat 1.9.dev2; see the top README for a
virtual environment). Build with `make pipeline-A` in the top directory.

## Conventions

* Cell 8r+c, block 7r+c with top left cell (r,c). A set of blocks is written `b1,b2,...`; `-` is the
  empty set. Sets are listed up to the four symmetries of the rectangle; `cmpsets.py` compares two
  lists up to symmetry (the files in `data/` do not all use the same representative).
* A tiling is printed as two hexadecimal masks `Hxxxx Vxxxx`: bit i of H is a horizontal domino on
  cells i, i+1, bit i of V a vertical domino on cells i, i+8.
* U(S) = T − ν(H_S) is the bound of Lemma 3, T = 1,292,697. Files of the form `B set max value`
  reuse the output format of `bsearch`; in `D*all.txt` the value is U(S).

## Programs

| file | purpose |
|---|---|
| `bsearch.c` | tilings, flips, classes of G_S by union–find. Modes `one S [K]` (largest K classes with representatives), `list THR` (sets on stdin; sets whose largest class exceeds THR), `listall MIN` (all classes of size ≥ MIN), `enum k THR part nparts` (all canonical k-sets) |
| `ub.c`, `ubv.c` | ν(H_S) by Hopcroft–Karp; `ubv` also verifies every matching (edges exist, mates consistent, sides correct). Modes `one S`, `list` |
| `ubr.c` | mode `restrict`: the refined bound \|R\| − ν(H_S[R]) of Section 10 for a set S and the union R of given classes |
| `apriori.py` | candidates of size k+1 all of whose k-subsets are in the list (both families are closed under subsets) |
| `satb2.py` | realizability of (S, one tiling): CaDiCaL, one-hot cells, piece variables per domino, each piece once, 8 copies of each number |
| `satb3.py` | the same question, independent encoding (domino → piece-and-orientation permutation) and solver (Glucose 4) |
| `fullb.py` | for each S, single-class tests in decreasing size until the realizable total is ≤ THR (`OK`) or all classes are tested (`OPEN`) |
| `multi.py`, `joint.py` | joint realizability of several classes; branch and bound for the exact maximum of Lemma 4 |
| `rbound.py` | the refined matching bound for the sets on which `joint.py` was too slow |
| `enumrec.py`, `canon.py` | arrays realizing the record class (SAT with blocking clauses), reduced up to symmetry and renaming |
| `blocks.py` | shows the good and bad blocks of an array |
| `gensets.py` | all canonical sets of k blocks (bitmask form), as enumerated by the original run for k ≤ 4 |
| `cmplines.py` | whole-line comparison of `fb_all.out`, `joint_all.out`, `rbound_all.out` with `data/`, up to symmetry |
| `checkopen.py` | the closing invariant: every `OPEN` set has `MAX joint` ≤ THR or an `rbound` bound ≤ THR |
| `cmpsets.py`, `cmpclasses.py` | comparison of set lists with `data/`, and of the classes with pipeline B |
| `run.sh` | the steps below |

## Steps, expected results and running times

Run `./run.sh STEP` (or `pipeline-A/run.sh STEP` from the top) in the order below. Results are
written to `work/`. Times "here" are for one core of an Intel Xeon Platinum 8375C (2.9 GHz) on an
idle machine (a loaded or hyperthreaded machine can be 1.2–2 times slower). `NPROC` (default 1)
sets the number of parallel jobs of `single3`, `fullb`, `joint`, `rbound`, `rbound-data`: their
input is split into chunks (one set per job for `joint` and `rbound`), and the outputs are merged
in input order. The original run used up to 6 processes on a 32-thread machine, about 37
core-hours in all, mostly in `fullb` (10.5 core-hours) and `joint` (15 core-hours).

| step | command | expected result | time here |
|---|---|---|---|
| dangerous sets | `./run.sh dangerous` | as in the original run: all 31,345 canonical sets of 1–4 blocks, then 12,408 candidates of sizes 5–9 by apriori; 11,324 non-empty dangerous sets (12/197/1,290/3,319/3,774/2,109/534/88/1), the same sets with the same representatives as `data/Dlist.txt`; the bound files `work/D1all.txt` … `D9all.txt`: OK (sha256) | 9 min |
| sets with a class > 853,985 | `./run.sh single`, then `./run.sh single3` | 350 sets (1/9/67/152/104/17 of sizes 0–5, none of size 6), the same as `data/allcand.txt` up to symmetry; all 350 UNSAT with satb2 (`single`) and with satb3 (`single3`) | 26 s + 103 s; `single3` about 50 min (8 s per test) |
| classes | `./run.sh classes` | 11,325 lines, 572,904 classes; after `pipeline-B/run.sh classes`, `python3 cmpclasses.py work/classes.txt ../pipeline-B/work/comp_all.out` reports 0 mismatches | 4 min |
| single-class bound | `./run.sh fullb` | 10,822 non-empty sets `OK` (10,823 with ∅, settled separately by `single`), 502 `OPEN`; every line identical to `data/fb_all.out` up to symmetry (`cmplines.py fb`) | about 10 core-hours |
| joint maximum | `./run.sh joint` | for each `OPEN` set that finishes within `JOINT_TIMEOUT` (default 3000 s): `MAX joint` ≤ 853,985, and the line identical to `data/joint_all.out` (`cmplines.py --subset joint`). In the original run 493 sets finished; the number depends on the machine | about 15 core-hours |
| refined bound | `./run.sh rbound` | the refined bound for the `OPEN` sets that `joint` did not finish, lines identical to `data/rbound_all.out` where present; then `checkopen.py`: every `OPEN` set settled, by `MAX joint` ≤ 853,985 or by a bound ≤ 853,985 | about 1.3 min per set |
| refined bound, shipped sets | `./run.sh rbound-data` | the 12 sets of `data/rbound_all.out`, lines identical, bounds 718,025 – 780,001 | 17 min (1.4 min per set) |
| record family | `./run.sh family` | 20,000 arrays → 19,601 essentially different ones, all with 853,985 solutions, A\* first; `work/family.txt`: OK (sha256 of the original list) | 30 s |

The whole-line comparison is possible because `dangerous` reproduces the representatives of the
original run (bitmask-minimal for sets of at most 4 blocks, as written by the exhaustive
enumeration, and lexicographically minimal for larger sets, as written by `apriori.py`), and the
programs are deterministic.

The family step depends on the order in which the SAT solver finds models. With python-sat
1.9.dev2 (CaDiCaL 1.5.3) it reproduces the shipped list exactly; another version may give a
different list, which can be checked with `../count/cntf`.

## Data

| file | content |
|---|---|
| `Dlist.txt` | the 11,324 non-empty dangerous sets |
| `allcand.txt` | the 350 sets having a class of more than 853,985 tilings: size and representative of that class |
| `fb_all.out` | `OK`/`OPEN`, bound, realizable class sizes, number of SAT calls, for each set of `Dlist.txt` |
| `joint_all.out` | exact maximum of Lemma 4 (`MAX joint`), its classes and an array realizing it, for 493 sets |
| `rbound_all.out` | the refined bound for 12 sets (the 9 that `joint` did not finish in the original run, and 3 more) |
| `SHA256SUMS` | checksums of `work/D1all.txt` … `D9all.txt`, `work/allcand.txt` and `work/family.txt` |

`work/D1all.txt` … `D4all.txt` are, line for line, the original run's bounds of all canonical sets
of at most 4 blocks (the original `D123all.txt` had one more first line, the empty set read as {0}
by the parser fixed since).
