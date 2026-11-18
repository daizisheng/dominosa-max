/* Independent verifier for TAOCP 7.2.2.1-73 (Dominosa maximum).
 * Board: 7 rows x 8 cols, cell id = 8*r + c.
 * Block id = 7*r + c (top-left cell (r,c), r<6, c<7); cells (r,c),(r,c+1),(r+1,c),(r+1,c+1).
 * Tiling: H = bitmask of left cells of horizontal dominoes, V = bitmask of top cells of vertical dominoes.
 */
#ifndef COMMON_H
#define COMMON_H
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define NR 7
#define NC 8
#define NCELL 56
#define NBLK 42
#define NTIL_EXPECT 1292697

typedef struct { uint64_t H, V; } til_t;

static inline int blk_cell(int b, int k) { /* k: 0=TL 1=TR 2=BL 3=BR */
  int r = b / 7, c = b % 7;
  return 8 * (r + (k >> 1)) + c + (k & 1);
}

/* block symmetries: 0 id, 1 mirror columns, 2 mirror rows, 3 rot180 */
static inline int blk_sym(int s, int b) {
  int r = b / 7, c = b % 7;
  if (s & 1) c = 6 - c;
  if (s & 2) r = 5 - r;
  return 7 * r + c;
}
static inline uint64_t set_sym(int s, uint64_t B) {
  uint64_t R = 0;
  for (int b = 0; b < NBLK; b++) if (B >> b & 1) R |= 1ULL << blk_sym(s, b);
  return R;
}
static inline uint64_t set_canon(uint64_t B) {
  uint64_t m = B;
  for (int s = 1; s < 4; s++) { uint64_t x = set_sym(s, B); if (x < m) m = x; }
  return m;
}

#define MAYBE_UNUSED __attribute__((unused))

static void *xmalloc(size_t n) { void *p = malloc(n); if (!p) { fprintf(stderr, "oom %zu\n", n); exit(2); } return p; }

/* load data produced by tile.c */
static int NT;
static til_t *TIL;
static int32_t *NB;      /* NB[t*42+b] = neighbour by flip in block b, or -1 */
static uint64_t *FM;     /* flippable-block mask */
static uint8_t *COL;     /* bipartition colour */

MAYBE_UNUSED static void load_all(const char *dir) {
  char fn[1024]; FILE *f; long sz;
  snprintf(fn, sizeof fn, "%s/tilings.bin", dir); f = fopen(fn, "rb"); if (!f) { perror(fn); exit(1); }
  fseek(f, 0, SEEK_END); sz = ftell(f); fseek(f, 0, SEEK_SET); NT = sz / sizeof(til_t);
  TIL = xmalloc(sz); if (fread(TIL, 1, sz, f) != (size_t)sz) exit(1); fclose(f);
  snprintf(fn, sizeof fn, "%s/nb.bin", dir); f = fopen(fn, "rb"); if (!f) { perror(fn); exit(1); }
  NB = xmalloc((size_t)NT * NBLK * 4); if (fread(NB, 4, (size_t)NT * NBLK, f) != (size_t)NT * NBLK) exit(1); fclose(f);
  snprintf(fn, sizeof fn, "%s/col.bin", dir); f = fopen(fn, "rb"); if (!f) { perror(fn); exit(1); }
  COL = xmalloc(NT); if (fread(COL, 1, NT, f) != (size_t)NT) exit(1); fclose(f);
  FM = xmalloc((size_t)NT * 8);
  for (int t = 0; t < NT; t++) { uint64_t m = 0; for (int b = 0; b < NBLK; b++) if (NB[(size_t)t * NBLK + b] >= 0) m |= 1ULL << b; FM[t] = m; }
}

/* list the 28 dominoes of a tiling as cell pairs */
static inline void til_dominoes(til_t T, int u[28], int v[28]) {
  int k = 0;
  for (int c = 0; c < NCELL; c++) {
    if (T.H >> c & 1) { u[k] = c; v[k] = c + 1; k++; }
    if (T.V >> c & 1) { u[k] = c; v[k] = c + 8; k++; }
  }
}

static inline int pair_id(int a, int b) { /* unordered pair of 0..6 -> 0..27 */
  if (a > b) { int t = a; a = b; b = t; }
  return a * 7 - a * (a - 1) / 2 + (b - a);
}

/* is tiling T a solution of array A (values 0..6, 56 cells)? */
static inline int is_solution(til_t T, const int *A) {
  uint32_t seen = 0;
  for (int c = 0; c < NCELL; c++) {
    if (T.H >> c & 1) { uint32_t m = 1u << pair_id(A[c], A[c + 1]); if (seen & m) return 0; seen |= m; }
    if (T.V >> c & 1) { uint32_t m = 1u << pair_id(A[c], A[c + 8]); if (seen & m) return 0; seen |= m; }
  }
  return 1;
}

MAYBE_UNUSED static uint64_t bad_set(const int *A) {
  uint64_t B = 0;
  for (int b = 0; b < NBLK; b++) {
    int p = A[blk_cell(b, 0)], q = A[blk_cell(b, 1)], r = A[blk_cell(b, 2)], s = A[blk_cell(b, 3)];
    if (!(p == s || q == r)) B |= 1ULL << b;
  }
  return B;
}

MAYBE_UNUSED static int parse_array(const char *s, int *A) { /* 7 rows of 8 digits 0..6 separated by '/' */
  int k = 0, i = 0;
  for (; s[i]; i++) {
    if (i % 9 == 8) { if (s[i] != '/') return 0; }
    else { if (s[i] < '0' || s[i] > '6' || k >= 56) return 0; A[k++] = s[i] - '0'; }
  }
  return i == 62 && k == 56;
}

MAYBE_UNUSED static void print_set(FILE *f, uint64_t B) {
  int first = 1; fputc('{', f);
  for (int b = 0; b < NBLK; b++) if (B >> b & 1) { fprintf(f, first ? "%d" : ",%d", b); first = 0; }
  fputc('}', f);
}
#endif
