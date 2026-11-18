/* dset.c: enumerate D = { B : NT - nu(H_B) > T } up to the 4 rectangle symmetries,
 * level by level (D is closed under subsets because nu(H_B) is monotone in B).
 * nu(H_B) = exact maximum matching of the bipartite graph H_B (edges = flips in blocks of B),
 * computed component by component with Kuhn's augmenting-path algorithm.
 * usage: dset DATADIR T OUTPREFIX     (OpenMP; set OMP_NUM_THREADS) */
#include "common.h"
#include <omp.h>

typedef struct { int *stamp, *mate, *vis, *comp, *stk; int st, vs; } ws_t;

static int kuhn(ws_t *w, int u, uint64_t B) {
  for (uint64_t m = FM[u] & B; m; m &= m - 1) {
    int b = __builtin_ctzll(m); int v = NB[(size_t)u * NBLK + b];
    if (w->vis[v] == w->vs) continue;
    w->vis[v] = w->vs;
    if (w->mate[v] < 0 || kuhn(w, w->mate[v], B)) { w->mate[v] = u; w->mate[u] = v; return 1; }
  }
  return 0;
}

static long nu_of(ws_t *w, uint64_t B, long *maxcomp) {
  long nu = 0; w->st++; *maxcomp = 0;
  for (int t = 0; t < NT; t++) {
    if (!(FM[t] & B) || w->stamp[t] == w->st) continue;
    int n = 0; w->stamp[t] = w->st; w->comp[n++] = t;
    for (int h = 0; h < n; h++) { int x = w->comp[h];
      for (uint64_t m = FM[x] & B; m; m &= m - 1) { int y = NB[(size_t)x * NBLK + __builtin_ctzll(m)]; if (w->stamp[y] != w->st) { w->stamp[y] = w->st; w->comp[n++] = y; } } }
    if (n > *maxcomp) *maxcomp = n;
    for (int i = 0; i < n; i++) w->mate[w->comp[i]] = -1;
    for (int i = 0; i < n; i++) if (COL[w->comp[i]] == 0) { w->vs++; nu += kuhn(w, w->comp[i], B); }
  }
  return nu;
}

static int cmpu(const void *a, const void *b) { uint64_t x = *(const uint64_t *)a, y = *(const uint64_t *)b; return x < y ? -1 : x > y; }
static int in_sorted(uint64_t *a, long n, uint64_t x) { return bsearch(&x, a, n, 8, cmpu) != NULL; }

int main(int argc, char **argv) {
  if (argc != 4) { fprintf(stderr, "usage: %s DATADIR T OUTPREFIX\n", argv[0]); return 2; }
  load_all(argv[1]); long T = atol(argv[2]);
  int nth = omp_get_max_threads();
  ws_t *W = xmalloc(nth * sizeof(ws_t));
  for (int i = 0; i < nth; i++) {
    W[i].stamp = calloc(NT, 4); W[i].mate = xmalloc(NT * 4); W[i].vis = calloc(NT, 4); W[i].comp = xmalloc(NT * 4); W[i].st = 0; W[i].vs = 0;
  }
  char fn[1024]; snprintf(fn, sizeof fn, "%s_D.txt", argv[3]); FILE *fD = fopen(fn, "w");
  snprintf(fn, sizeof fn, "%s_boundary.txt", argv[3]); FILE *fX = fopen(fn, "w");
  if (!fD || !fX) { perror(argv[3]); return 1; }
  uint64_t *cur = xmalloc(8); long ncur = 1; cur[0] = 0;
  { long mc; long nu = nu_of(&W[0], 0, &mc); fprintf(fD, "0 %ld %ld {}\n", nu, NT - nu); }
  long total = 0;
  for (int k = 1; k <= NBLK && ncur > 0; k++) {
    /* candidates */
    long cap = ncur * NBLK, nc = 0; uint64_t *cand = xmalloc(cap * 8);
    for (long i = 0; i < ncur; i++) for (int b = 0; b < NBLK; b++) if (!(cur[i] >> b & 1)) cand[nc++] = set_canon(cur[i] | 1ULL << b);
    qsort(cand, nc, 8, cmpu);
    long m = 0; for (long i = 0; i < nc; i++) if (!m || cand[i] != cand[m - 1]) cand[m++] = cand[i]; nc = m;
    /* subset closure pruning */
    long np = 0; uint64_t *pc = xmalloc((nc + 1) * 8); long pruned = 0;
    for (long i = 0; i < nc; i++) {
      int ok = 1;
      for (uint64_t r = cand[i]; r && ok; r &= r - 1) { uint64_t s = cand[i] & ~(r & -r); if (!in_sorted(cur, ncur, set_canon(s))) ok = 0; }
      if (ok) pc[np++] = cand[i]; else pruned++;
    }
    long *nus = xmalloc((np + 1) * sizeof(long)), *mcs = xmalloc((np + 1) * sizeof(long));
#pragma omp parallel for schedule(dynamic, 4)
    for (long i = 0; i < np; i++) { ws_t *w = &W[omp_get_thread_num()]; nus[i] = nu_of(w, pc[i], &mcs[i]); }
    uint64_t *nx = xmalloc((np + 1) * 8); long nn = 0;
    for (long i = 0; i < np; i++) {
      long bound = NT - nus[i];
      FILE *f = bound > T ? fD : fX;
      fprintf(f, "%d %ld %ld ", k, nus[i], bound); print_set(f, pc[i]); fprintf(f, " maxHcomp=%ld\n", mcs[i]);
      if (bound > T) nx[nn++] = pc[i];
    }
    fflush(fD); fflush(fX);
    printf("level %d: canonical candidates %ld, pruned-by-subsets %ld, evaluated %ld, in D %ld\n", k, nc, pruned, np, nn); fflush(stdout);
    total += nn;
    free(cur); cur = nx; ncur = nn; free(cand); free(pc); free(nus); free(mcs);
  }
  printf("total non-empty canonical sets in D: %ld\n", total);
  fclose(fD); fclose(fX);
  return 0;
}
