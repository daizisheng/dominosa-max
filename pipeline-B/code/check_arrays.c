/* check_arrays.c: for each array (stdin, one per line, optional second token = parent set "{..}"):
 *  - count solutions by brute force over all tilings,
 *  - compute bad set B = bad(A) and components of G_B by BFS,
 *  - check every component is all-solutions or no-solutions (the "consequence"),
 *  - print the sizes of the solution components;
 *  - if a parent set B0 (subset of B) is given: print how the largest G_B0 component
 *    containing a solution splits into G_B components.
 * usage: check_arrays DATADIR < arrays */
#include "common.h"
static int *cid, *q;
static int comps(uint64_t B, int *sizes) { /* cid[] for G_B; returns #comps */
  uint64_t nB = ~B & ((1ULL << NBLK) - 1); int nc = 0;
  for (int t = 0; t < NT; t++) cid[t] = -1;
  for (int t = 0; t < NT; t++) if (cid[t] < 0) {
    int n = 0; q[n++] = t; cid[t] = nc;
    for (int h = 0; h < n; h++) { int x = q[h]; for (uint64_t m = FM[x] & nB; m; m &= m - 1) { int y = NB[(size_t)x * NBLK + __builtin_ctzll(m)]; if (cid[y] < 0) { cid[y] = nc; q[n++] = y; } } }
    sizes[nc++] = n;
  }
  return nc;
}
static int cmpd(const void *a, const void *b) { return *(const int *)b - *(const int *)a; }
int main(int argc, char **argv) {
  if (argc != 2) { fprintf(stderr, "usage: %s DATADIR < arrays\n", argv[0]); return 2; }
  load_all(argv[1]); cid = xmalloc(NT * 4); q = xmalloc(NT * 4);
  int *sz = xmalloc(NT * 4), *sol = xmalloc(NT * 4), *nsolc = xmalloc(NT * 4), *cid0 = xmalloc(NT * 4), *sz0 = xmalloc(NT * 4);
  char line[512];
  while (fgets(line, sizeof line, stdin)) {
    char arr[128], par[256] = ""; if (sscanf(line, "%127s %255s", arr, par) < 1) continue;
    int A[56]; if (!parse_array(arr, A)) { printf("%s parse error\n", arr); continue; }
    uint64_t B = bad_set(A); int nc = comps(B, sz);
    long ns = 0; for (int c = 0; c < nc; c++) nsolc[c] = 0;
    for (int t = 0; t < NT; t++) { sol[t] = is_solution(TIL[t], A); ns += sol[t]; nsolc[cid[t]] += sol[t]; }
    int mixed = 0, k = 0; int list[4096];
    for (int c = 0; c < nc; c++) { if (nsolc[c] && nsolc[c] != sz[c]) mixed++; if (nsolc[c] == sz[c] && k < 4096) list[k++] = sz[c]; }
    qsort(list, k, 4, cmpd);
    printf("%s solutions=%ld bad=", arr, ns); print_set(stdout, B); printf(" ncomp(G_B)=%d mixed=%d solcomps=", nc, mixed);
    for (int i = 0; i < k; i++) printf(i ? "+%d" : "%d", list[i]);
    if (par[0] == '{') {
      uint64_t B0 = 0; for (char *p = par + 1; *p && *p != '}';) { if (*p >= '0' && *p <= '9') B0 |= 1ULL << strtol(p, &p, 10); else p++; }
      memcpy(cid0, cid, NT * 4); memcpy(sz0, sz, nc * 4);
      int nc0 = comps(B0, sz0); (void)nc0; /* now cid = G_B0 ids, cid0 = G_B ids */
      int t0 = -1; for (int t = 0; t < NT; t++) if (sol[t]) { t0 = t; break; }
      if (t0 >= 0) {
        int P = cid[t0]; int *cnt = calloc(nc, 4); long tot = 0;
        for (int t = 0; t < NT; t++) if (cid[t] == P) { cnt[cid0[t]]++; tot++; }
        int kk = 0; int *l2 = xmalloc(nc * 4); for (int c = 0; c < nc; c++) if (cnt[c]) l2[kk++] = cnt[c];
        qsort(l2, kk, 4, cmpd);
        printf(" | parent "); print_set(stdout, B0); printf(" comp of first solution has size %ld = ", tot);
        for (int i = 0; i < kk && i < 20; i++) printf(i ? "+%d" : "%d", l2[i]);
        if (kk > 20) printf("+...(%d parts)", kk);
        free(cnt); free(l2);
      }
    }
    puts(""); fflush(stdout);
  }
  return 0;
}
