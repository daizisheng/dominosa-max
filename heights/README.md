# heights/ — classes from Thurston's height function (Lemma 5)

A third way to find the classes, used as a cross-check of the class computations of pipelines A
and B. By Lemma 5 of the note, the classes of tilings under flips in blocks outside S are exactly the
nonempty sets of tilings on which the heights at the centres of the blocks of S take prescribed
values. Along a vertical grid line the height at each point depends only on which rows have a
horizontal domino crossing the line, so the class sizes can be computed by a transfer matrix over
the columns that carries, besides the set of crossing rows, the heights reached so far at the
centres of the blocks of S. No tiling is listed.

Requirements: Python 3; `ucheck.py` also needs `networkx` (see `requirements.txt`). All programs
exit with status 1 if a check fails.

| program | what it does | command | expected output | time |
|---|---|---|---|---|
| `tm.py` | `class_sizes(n, S)`; examples | `python3 tm.py` | A\*: 34 classes, total 1,292,697, largest 853985, 95456, 95456, 60344, 39800; González-Morris: 73 classes, largest 807752; n=5, {(1,1),(1,4),(3,2)}: 23929, 2776, 1524, 1244, 540; T_7 = 108,435,745, T_8 = 14,479,521,761, T_9 = 3,852,472,573,499 | 0.5 s |
| `xcheck_tm.py` | class sizes of every set in `../pipeline-B/work/comp_all.out` (written by `pipeline-B/run.sh classes`) recomputed by `tm.py`; flips per block | `python3 xcheck_tm.py [FILE [NPROC]]` (NPROC parallel processes, default 1) | `sets 11326 mismatches 0`, `total classes compared 572990`, and the table of flips 388705 183779 306167 203435 / 228897 85612 175534 92686 / 287253 115368 224589 126125 | 31 s |
| `hcheck.py` | Lemma 5 tested against union–find on random sets, n = 2..5; a flip in block b changes the height only at the centre of b, by ±4 | `python3 hcheck.py` | 207 + 513 + 321 + 71 = 1,112 sets, 0 mismatches | 8 s |
| `icount.py` | I(S), the number of tilings in which no block of S is filled by two parallel dominoes, by a transfer matrix; checked by brute force for n = 3..5 | `python3 icount.py` | 0 mismatches | 2 s |
| `ucheck.py` | for S whose blocks are pairwise non-adjacent, T − ν(H_S) = (T + I(S))/2 (networkx matchings, n = 3, 4); for adjacent blocks the formula is not a bound | `python3 ucheck.py` | 0 mismatches for non-adjacent sets | 27 s |

The file read by `xcheck_tm.py` (checksum in `pipeline-B/data/SHA256SUMS`) lists the classes of the 11,326 sets of the control run with target
853,984: the 11,325 dangerous sets for 853,985 (572,904 classes) and the extra set
{3,17,19,26,29,31} (86 classes). Pipeline B wrote it with `comp` (breadth-first search over all
tilings); `xcheck_tm.py DIR` also accepts the directory `pipeline-B/work/st/` of per-set structure
files written by the same step. The flips in a block b are
(T − I({b}))/2, since every tiling in which b is filled by two parallel dominoes takes part in
exactly one flip in b.
