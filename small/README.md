# small/ — the double-n sets, n = 1..5

Sections 3, 5 and 7–9 of the note, the subsection "The smaller boards" of Section 11, and the table of Section 12. The board
is (n+1)×(n+2), cell r·C+c with C = n+2, block r·(C−1)+c with top left cell (r,c). For every n
the maximum M_n is found twice: by the block method (the same argument as for n = 6) and by
methods that know nothing about blocks (exhaustive search for n ≤ 3, branch and bound over arrays
for n = 4, 5).

Requirements: a C compiler; Python 3 with the packages of the top-level `requirements.txt`
(`pip install -r requirements.txt`).
Build with `make small` in the top directory. Run `./run.sh STEP` (or `small/run.sh STEP` from the top);
output goes to `work/` and is compared with `data/`, directly or by the checksums in `data/SHA256SUMS`.

## Programs

| file | purpose |
|---|---|
| `dom.py` | boards, tilings, flips, classes, matching bound, canonical forms |
| `satenc.py` | two SAT encodings of realizability: Enc1 (CaDiCaL) and Enc2 (Glucose 4) |
| `blk.py` | the block method: dangerous sets (scipy matchings, each matching checked), classes, single-class SAT, exact maximum of Lemma 4 by branch and bound; every UNSAT re-checked with Enc2, every SAT model counted by `cnt` |
| `summarize.py` | the table of dangerous sets and how each is settled (`dangerous_n*.json`) |
| `countmax.py` | all optimal arrays by AllSAT on the dangerous sets, each counted by `cnt` |
| `brute12.py` | every array for n = 1, 2, checking also that every class is all solutions or none |
| `bfa.c`, `bfb.c` | two separately written exhaustive searches for n ≤ 3 (different symmetry reduction and counting) |
| `bb.c`, `bb3.c` | branch and bound over arrays: cells filled one by one, prune when fewer tilings than the threshold are still free of repeated pieces; `bb3` adds the left–right mirror reduction |
| `cnt.c` | solution counter used by the Python programs |
| `histcmp.py`, `cmpsets.py`, `bb3merge.py` | comparisons with `data/` and between methods |

## Steps, expected results, times

Times "here" are for one core of an Intel Xeon Platinum 8375C on an idle machine (a loaded or
hyperthreaded machine can be 1.2–2 times slower).

| command | expected result | time here |
|---|---|---|
| `./run.sh brute` | n=1: 20 arrays, max 3 (4 arrays); n=2: 34,650 arrays, max 10 (240 arrays, 10 up to symmetry); histograms identical to `data/histograms_n123.tsv`, `brute_n*.json` equal to `data/` | 1 s |
| `./run.sh n3full` | bfa on the whole board: 11,732,745,024 arrays, max 88 (1,536 arrays), next 83, histogram identical to `data/histograms_n123.tsv` | 20 s |
| `./run.sh n3` | the 12 slices of bfa and of bfb: OK (sha256). `J="0 5"` selects slices; runs with different J can go in parallel | 2.5 min per slice |
| `./run.sh block 1` … `block 4` | max best(S) 3, 10, 88, 1012; dangerous sets (up to symmetry) 0, 1, 2, 6, settled as in the table of Section 8 for n = 4; `D_n*`, `blk_n*`, `dangerous_n*.json` equal to `data/` apart from witness arrays | under 7 s each |
| `./run.sh block 5`, then `./run.sh block5sum` | run `J=0 ./run.sh block 5` first (it creates `D_n5_L23929.json`), then the other parts in parallel (`J=1` … `J=8`), then `block5sum`; without `J` all 9 parts run one after the other. 115 dangerous sets (1/7/35/48/21/3 of sizes 0–5): 90 with no realizable class, 15 with realizable total ≤ M, 10 needing branch and bound, with maxima 22,842, 23,189 (twice), 23,650 (twice), 23,929 (five times); all files equal to `data/` | 9 parts of 5–6 min |
| `./run.sh countmax 1` … `countmax 4` (after `block N`) | 4, 240, 1,536, 120,960 optimal arrays; 1, 10, 16, 252 up to symmetry; equal to `data/countmax_n*.json` | 1 s each |
| `./run.sh countmax 5` (after `block 5`) | 35,188 arrays with B(A) exactly {7,10,20}, one for each of the 35,188 classes of optimal arrays (101,341,440 arrays in all); `max_n5.txt`: OK | 45 s (6 parts) |
| `./run.sh bb4` (after `countmax 4`) | threshold 900: only 901, 950, 999, 1012 occur, 1,008 canonical arrays with 1,012; `bb4_900.out`, `bb4_1012.out`: OK; the same 252 classes as the block method | 15 s |
| `NPROC=k ./run.sh bb5 J0 J1` | slices J0..J1 of the 4000 slices of the n = 5 search, k at a time, each checked against `data/n5_bb3_slices.sha256` | 16 core-hours for all 4000 (about 30 s per slice) |
| `./run.sh merge5` (after `bb5 0 3999`, `countmax 5`) | nothing above 23,929; 101,341,440 arrays with 23,929, 35,188 up to symmetry, the same classes as the block method; as in `data/bb3_n5_summary.txt` | 5 s |

## Data

| file | content |
|---|---|
| `histograms_n123.tsv` | number of arrays with each number of solutions, n = 1, 2, 3 (all arrays) |
| `brute_n1.json`, `brute_n2.json` | exhaustive results for n = 1, 2, with all optimal arrays |
| `D_n*_L*.json` | dangerous sets level by level, with U(S) |
| `blk_n1..4.json`, `blk_n5_part0..8.json` | block-method records for each dangerous set |
| `dangerous_n1..5.json` | the dangerous sets and how each is settled |
| `countmax_n1..4_L*.json` | optimal arrays found by the block method |
| `bb3_n5_summary.txt` | summary of the 4000 slices of bb3 for n = 5 |
| `SHA256SUMS` | checksums of the slices of bfa and bfb for n = 3, of bb for n = 4, of `max_n5.txt` |
| `n5_bb3_slices.sha256` | checksums of the 4000 slices of bb3 for n = 5 |
