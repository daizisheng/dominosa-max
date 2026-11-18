/* mcheck.c: independent re-check of the matching bound for sets OUTSIDE D.
 * For each set B (stdin lines containing "{..}"): Hopcroft-Karp on the whole bipartite graph H_B
 * (left side = colour 0), then the matching is VERIFIED explicitly (every matched pair is a flip in
 * a block of B, mates symmetric, each vertex used once) and  N - |M|  is compared to T.
 * Prints "OK" if N-|M| <= T (so the set is correctly outside D), "INSIDE" otherwise.
 * usage: mcheck DATADIR T < sets */
#include "common.h"
#include <omp.h>
#define INF 0x3fffffff
typedef struct { int *mate, *dist, *q, *it, *stk; } hk_t;

static long hk(hk_t *w, uint64_t B) {
  int *mate = w->mate, *dist = w->dist, *q = w->q;
  for (int t = 0; t < NT; t++) mate[t] = -1;
  long M = 0;
  for (;;) {
    int qh = 0, qt = 0, found = 0;
    for (int t = 0; t < NT; t++) if (COL[t] == 0) { if (mate[t] < 0 && (FM[t] & B)) { dist[t] = 0; q[qt++] = t; } else dist[t] = INF; }
    while (qh < qt) { int u = q[qh++];
      for (uint64_t m = FM[u] & B; m; m &= m - 1) { int v = NB[(size_t)u * NBLK + __builtin_ctzll(m)]; int u2 = mate[v];
        if (u2 < 0) found = 1; else if (dist[u2] == INF) { dist[u2] = dist[u] + 1; q[qt++] = u2; } } }
    if (!found) break;
    /* iterative DFS along layers */
    for (int s = 0; s < NT; s++) {
      if (COL[s] != 0 || mate[s] >= 0 || !(FM[s] & B) || dist[s] != 0) continue;
      int sp = 0; w->stk[sp++] = s; w->it[s] = 0; int done = 0;
      while (sp && !done) {
        int u = w->stk[sp - 1]; uint64_t m = FM[u] & B; int adv = 0;
        while (w->it[u] < NBLK) { int b = w->it[u]++; if (!(m >> b & 1)) continue; int v = NB[(size_t)u * NBLK + b]; int u2 = mate[v];
          if (u2 < 0) { /* augment along stack */
            int vv = v; for (int i = sp - 1; i >= 0; i--) { int uu = w->stk[i]; int nxt = mate[uu]; mate[uu] = vv; mate[vv] = uu; vv = nxt; }
            done = 1; break; }
          if (dist[u2] == dist[u] + 1) { w->it[u2] = 0; w->stk[sp++] = u2; adv = 1; break; } }
        if (done) break;
        if (!adv) { dist[u] = INF; sp--; }
      }
      if (done) M++;
    }
  }
  /* verify */
  long cnt = 0;
  for (int t = 0; t < NT; t++) if (mate[t] >= 0) {
    int v = mate[t]; if (mate[v] != t || v == t || COL[v] == COL[t]) { fprintf(stderr, "bad matching\n"); exit(9); }
    int ok = 0; for (uint64_t m = FM[t] & B; m; m &= m - 1) if (NB[(size_t)t * NBLK + __builtin_ctzll(m)] == v) ok = 1;
    if (!ok) { fprintf(stderr, "non-edge in matching\n"); exit(9); }
    cnt++;
  }
  if (cnt != 2 * M) { fprintf(stderr, "count mismatch\n"); exit(9); }
  return M;
}
int main(int argc, char **argv) {
  if (argc != 3) { fprintf(stderr, "usage: %s DATADIR T < sets\n", argv[0]); return 2; }
  load_all(argv[1]); long T = atol(argv[2]);
  char line[4096]; uint64_t *S = xmalloc(400000 * 8); char **L = xmalloc(400000 * sizeof(char *)); int ns = 0;
  while (fgets(line, sizeof line, stdin)) { char *p = strchr(line, '{'); if (!p) continue; uint64_t B = 0; p++;
    while (*p && *p != '}') { if (*p >= '0' && *p <= '9') B |= 1ULL << strtol(p, &p, 10); else p++; } S[ns++] = B; }
  long *res = xmalloc(ns * sizeof(long));
  int nth = omp_get_max_threads(); hk_t *W = xmalloc(nth * sizeof(hk_t));
  for (int i = 0; i < nth; i++) { W[i].mate = xmalloc(NT * 4); W[i].dist = xmalloc(NT * 4); W[i].q = xmalloc(NT * 4); W[i].it = xmalloc(NT * 4); W[i].stk = xmalloc(NT * 4); }
#pragma omp parallel for schedule(dynamic, 1)
  for (int i = 0; i < ns; i++) res[i] = hk(&W[omp_get_thread_num()], S[i]);
  long ok = 0, inside = 0;
  for (int i = 0; i < ns; i++) { int o = NT - res[i] <= T; ok += o; inside += !o; printf("%s %ld %ld ", o ? "OK" : "INSIDE", res[i], NT - res[i]); print_set(stdout, S[i]); puts(""); }
  fprintf(stderr, "sets %d OK %ld INSIDE %ld\n", ns, ok, inside);
  (void)L; return 0;
}
