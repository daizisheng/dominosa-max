# count/ — direct counts for the double-six board

Small, independent programs that need nothing but a C compiler or Python 3. They check the
statements of Sections 2 and 10 of the note that are direct computations: the number of solutions of
A\*, the placement statistics, and the class structure of A\* and of the earlier records.

An array is written row by row, 7 rows of 8 digits separated by `/`. A block is named by its top
left cell (r,c) or by its number 7r+c (0 ≤ r < 6, 0 ≤ c < 7).

| program | method | usage |
|---|---|---|
| `dc.c` | plain backtracking over cells, with a used-piece table | `./dc ARRAY` |
| `count.h`, `cnt.c`, `cntf.c` | meet in the middle: the top and bottom halves of the board are tiled separately and joined on (frontier, set of pieces used) | `./cnt ARRAY ...`, `./cntf < file` |
| `tilings.c` | lists all 1,292,697 tilings and tests each one | `./tilings ARRAY` |
| `slowcount.py` | backtracking in Python, written separately | `python3 slowcount.py ARRAY` |
| `place.c` | number of solutions using each of the 97 candidate placements; prints the minimum | `./place ARRAY` |
| `edgestats.py` | the same in Python, and lists the placements never used | `python3 edgestats.py ARRAY` |
| `classes.c` | bad blocks, classes of tilings under flips in good blocks, solution classes | `./classes ARRAY` |
| `split.c` | how the largest class for four bad blocks splits when a fifth block becomes bad | `./split b1 b2 b3 b4 b5` |
| `gen.py` | the same analysis for any double-n board (practical for n ≤ 5) | `python3 gen.py ARRAY ...` |

The 19,601 essentially different arrays with 853,985 solutions are produced by
`pipeline-A/run.sh family` (30 s) in `pipeline-A/work/family.txt`, one line `count array` each.

## Commands and expected output

Run `make count` in the top directory first; these checks are also part of `make quick`. All times are for one core of an Intel Xeon
Platinum 8375C.

```
A=00060465/20504626/52012466/45122236/51312333/11143035/61444355     # A*
G=06151146/66611014/56132144/55326224/53632022/34300525/33040054     # Gonzalez-Morris (errata, 2023)
K=66110144/26611514/52132140/55322200/53242006/36430565/33643054     # Keller (answer 73)

./dc $A; ./dc $G; ./dc $K          # -> 853985, 807752, 730924            (0.03 s each)
./cnt $A $G $K                     # same numbers, about 0.1 ms per count
./tilings $A                       # valid 853985 components 34 validcomps 1 mixed 0 ... (1.3 s)
python3 slowcount.py $A            # 853985                                 (3 s)
./place $A                         # 853985 solutions, min placement count 37207   (0.06 s)
./place $G                         # 807752 solutions, min placement count 35082
python3 edgestats.py $G            # placements used 97 of 97; never used []; min occurrences 35082
./classes $A                       # bad blocks 10 (1,3), 15 (2,1), 19 (2,5), 31 (4,3);
                                   # 34 components, one solution class of 853985;
                                   # largest components 853985 95456 95456 60344 39800;
                                   # bad flips joining two solutions 0          (1.7 s)
./split 10 15 19 31 33             # big 853985 splits into: 28239 807752 17994   (1.5 s)
./cntf < ../pipeline-A/work/family.txt | awk '{print $1}' | uniq -c   # 19601 853985   (2 s)
python3 gen.py 001/011 000/111 0001/0211/2221 00011/20121/22313/23033 000112/201122/031342/323404/334144
                                   # solutions 3, 2, 10, 88, 1012; class sizes as in Sections 3, 5, 7, 8
```

`./dc` on another array with 846,461 solutions, the next best total found
(`00211105/02221510/25233103/42335360/14343626/44456166/04555646`), gives 846461.
