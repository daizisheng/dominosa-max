/* tile.c: enumerate all domino tilings of 7x8, build flip-neighbour table,
 * 2-colour the flip graph (check bipartite + connected).
 * usage: tile OUTDIR */
#include "common.h"

static til_t *L; static int nL, capL;
static uint64_t occ;
static uint64_t curH, curV;

static void rec(void) {
  if (occ == (1ULL << NCELL) - 1) {
    if (nL == capL) { capL = capL ? 2 * capL : 1 << 20; L = realloc(L, capL * sizeof(til_t)); }
    L[nL].H = curH; L[nL].V = curV; nL++; return;
  }
  int c = __builtin_ctzll(~occ);
  int r = c / 8, col = c % 8;
  if (col < 7 && !(occ >> (c + 1) & 1)) {
    occ |= 3ULL << c; curH |= 1ULL << c; rec(); curH &= ~(1ULL << c); occ &= ~(3ULL << c);
  }
  if (r < 6) { /* cell c+8 is surely empty (row-major fill) */
    occ |= (1ULL << c) | (1ULL << (c + 8)); curV |= 1ULL << c; rec(); curV &= ~(1ULL << c); occ &= ~((1ULL << c) | (1ULL << (c + 8)));
  }
}
static int cmpt(const void *a, const void *b) {
  const til_t *x = a, *y = b;
  if (x->H != y->H) return x->H < y->H ? -1 : 1;
  if (x->V != y->V) return x->V < y->V ? -1 : 1;
  return 0;
}
static int find(til_t T) {
  int lo = 0, hi = nL - 1;
  while (lo <= hi) { int m = (lo + hi) / 2; int c = cmpt(&T, &L[m]); if (!c) return m; if (c < 0) hi = m - 1; else lo = m + 1; }
  return -1;
}
int main(int argc, char **argv) {
  if (argc != 2) { fprintf(stderr, "usage: %s OUTDIR\n", argv[0]); return 2; }
  rec();
  qsort(L, nL, sizeof(til_t), cmpt);
  printf("tilings: %d (expected %d)\n", nL, NTIL_EXPECT);
  for (int i = 0; i < nL; i++) { /* sanity: 28 dominoes, disjoint, cover */
    uint64_t cov = 0; int n = 0;
    for (int c = 0; c < 56; c++) {
      if (L[i].H >> c & 1) { if (c % 8 == 7 || (cov >> c & 3)) { puts("bad H"); return 1; } cov |= 3ULL << c; n++; }
      if (L[i].V >> c & 1) { if (c >= 48 || (cov & ((1ULL << c) | (1ULL << (c + 8))))) { puts("bad V"); return 1; } cov |= (1ULL << c) | (1ULL << (c + 8)); n++; }
    }
    if (n != 28 || cov != (1ULL << 56) - 1) { puts("bad tiling"); return 1; }
    if (i && cmpt(&L[i - 1], &L[i]) >= 0) { puts("dup"); return 1; }
  }
  int32_t *nb = xmalloc((size_t)nL * NBLK * 4);
  long nedge2 = 0;
  for (int i = 0; i < nL; i++) for (int b = 0; b < NBLK; b++) {
    int p = blk_cell(b, 0), q = blk_cell(b, 1), r = blk_cell(b, 2);
    til_t T = L[i]; int ok = 0;
    if ((T.H >> p & 1) && (T.H >> r & 1)) { T.H &= ~((1ULL << p) | (1ULL << r)); T.V |= (1ULL << p) | (1ULL << q); ok = 1; }
    else if ((T.V >> p & 1) && (T.V >> q & 1)) { T.V &= ~((1ULL << p) | (1ULL << q)); T.H |= (1ULL << p) | (1ULL << r); ok = 1; }
    int j = -1;
    if (ok) { j = find(T); if (j < 0) { puts("flip target missing"); return 1; } nedge2++; }
    nb[(size_t)i * NBLK + b] = j;
  }
  /* symmetric check */
  for (int i = 0; i < nL; i++) for (int b = 0; b < NBLK; b++) { int j = nb[(size_t)i * NBLK + b]; if (j >= 0 && nb[(size_t)j * NBLK + b] != i) { puts("asym"); return 1; } }
  printf("flip edges: %ld\n", nedge2 / 2);
  /* BFS colouring */
  uint8_t *col = xmalloc(nL); memset(col, 255, nL);
  int *q = xmalloc(nL * sizeof(int)); int qh = 0, qt = 0; col[0] = 0; q[qt++] = 0;
  long conflicts = 0;
  while (qh < qt) { int x = q[qh++]; for (int b = 0; b < NBLK; b++) { int y = nb[(size_t)x * NBLK + b]; if (y < 0) continue; if (col[y] == 255) { col[y] = col[x] ^ 1; q[qt++] = y; } else if (col[y] == col[x]) conflicts++; } }
  printf("reached %d of %d; same-colour edges %ld\n", qt, nL, conflicts);
  int c0 = 0; for (int i = 0; i < nL; i++) c0 += col[i] == 0;
  printf("colour classes %d / %d\n", c0, nL - c0);
  char fn[1024]; FILE *f;
  snprintf(fn, sizeof fn, "%s/tilings.bin", argv[1]); f = fopen(fn, "wb");
  if (!f || fwrite(L, sizeof(til_t), nL, f) != (size_t)nL || fclose(f)) { perror(fn); return 1; }
  snprintf(fn, sizeof fn, "%s/nb.bin", argv[1]); f = fopen(fn, "wb");
  if (!f || fwrite(nb, 4, (size_t)nL * NBLK, f) != (size_t)nL * NBLK || fclose(f)) { perror(fn); return 1; }
  snprintf(fn, sizeof fn, "%s/col.bin", argv[1]); f = fopen(fn, "wb");
  if (!f || fwrite(col, 1, nL, f) != (size_t)nL || fclose(f)) { perror(fn); return 1; }
  return (nL == NTIL_EXPECT && qt == nL && conflicts == 0) ? 0 : 3;
}
