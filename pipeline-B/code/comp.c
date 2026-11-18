/* comp.c: for each set B (one per line, "{a,b,...}" anywhere on the line), compute the
 * connected components of G_B (flips in blocks NOT in B) by BFS, and classify them:
 *   dead  = component contains an H_B edge (flip in a block of B) between two of its own tilings.
 *           For an array with bad set exactly B such a component cannot consist of solutions.
 *   live  = otherwise.
 * Prints per set: #comps, #live, sum of live sizes, largest dead size, and the live
 * components in decreasing size (size:representative) as long as the remaining tail sum > TAILMIN.
 * With DUMPDIR, also writes DUMPDIR/<hex B>.txt: all components (size, rep, H, V) sorted by
 * decreasing size and the quotient edges (pairs of components joined by a flip in a block of B).
 * usage: comp DATADIR SETFILE TAILMIN [DUMPDIR] > out */
#include "common.h"
#include <omp.h>

static int parse_set(const char *s, uint64_t *B) {
  const char *p = strchr(s, '{'); if (!p) return 0; p++; *B = 0;
  while (*p && *p != '}') { if (*p >= '0' && *p <= '9') { int x = strtol(p, (char **)&p, 10); *B |= 1ULL << x; } else p++; }
  return 1;
}
typedef struct { int size, rep; } cs_t;
static int cmpu64(const void *a, const void *b) { uint64_t x = *(const uint64_t *)a, y = *(const uint64_t *)b; return x < y ? -1 : x > y; }
static int cmpcs(const void *a, const void *b) { const cs_t *x = a, *y = b; if (x->size != y->size) return y->size - x->size; return x->rep - y->rep; }

int main(int argc, char **argv) {
  if (argc < 4 || argc > 5) { fprintf(stderr, "usage: %s DATADIR SETFILE TAILMIN [DUMPDIR]\n", argv[0]); return 2; }
  load_all(argv[1]); long tailmin = atol(argv[3]); const char *dumpdir = argc > 4 ? argv[4] : NULL;
  FILE *f = fopen(argv[2], "r"); char line[4096];
  if (!f) { perror(argv[2]); return 1; }
  uint64_t *S = xmalloc(200000 * 8); int ns = 0;
  while (fgets(line, sizeof line, f)) { uint64_t B; if (parse_set(line, &B)) S[ns++] = B; }
  fclose(f);
  char **out = xmalloc(ns * sizeof(char *));
  int nth = omp_get_max_threads();
  int **CID = xmalloc(nth * sizeof(int *)), **Q = xmalloc(nth * sizeof(int *));
  for (int i = 0; i < nth; i++) { CID[i] = xmalloc(NT * 4); Q[i] = xmalloc(NT * 4); }
#pragma omp parallel for schedule(dynamic, 1)
  for (int i = 0; i < ns; i++) {
    int th = omp_get_thread_num(); int *cid = CID[th], *q = Q[th]; uint64_t B = S[i], nB = ~B & ((1ULL << NBLK) - 1);
    for (int t = 0; t < NT; t++) cid[t] = -1;
    int nc = 0; cs_t *cs = xmalloc(sizeof(cs_t) * 1024); int cap = 1024;
    for (int t = 0; t < NT; t++) if (cid[t] < 0) {
      int n = 0; q[n++] = t; cid[t] = nc;
      for (int h = 0; h < n; h++) { int x = q[h];
        for (uint64_t m = FM[x] & nB; m; m &= m - 1) { int y = NB[(size_t)x * NBLK + __builtin_ctzll(m)]; if (cid[y] < 0) { cid[y] = nc; q[n++] = y; } } }
      if (nc == cap) { cap *= 2; cs = realloc(cs, cap * sizeof(cs_t)); }
      cs[nc].size = n; cs[nc].rep = t; nc++;
    }
    char *dead = calloc(nc, 1);
    for (int x = 0; x < NT; x++) for (uint64_t m = FM[x] & B; m; m &= m - 1) { int y = NB[(size_t)x * NBLK + __builtin_ctzll(m)]; if (cid[y] == cid[x]) dead[cid[x]] = 1; }
    int nl = 0; long lsum = 0, dmax = 0, dsum = 0;
    for (int c = 0; c < nc; c++) { if (dead[c]) { dsum += cs[c].size; if (cs[c].size > dmax) dmax = cs[c].size; } else { cs[nl++] = cs[c]; lsum += cs[c].size; } }
    qsort(cs, nl, sizeof(cs_t), cmpcs);
    size_t bl = 1 << 16; char *buf = xmalloc(bl); int L = 0;
    L += sprintf(buf + L, "%d ", __builtin_popcountll(B));
    { char sb[256]; FILE *mf = fmemopen(sb, sizeof sb, "w"); print_set(mf, B); fclose(mf); L += sprintf(buf + L, "%s", sb); }
    L += sprintf(buf + L, " ncomp=%d nlive=%d livesum=%ld deadsum=%ld deadmax=%ld live:", nc, nl, lsum, dsum, dmax);
    long tail = lsum;
    for (int c = 0; c < nl && tail > tailmin && L < (int)bl - 64; c++) { L += sprintf(buf + L, " %d:%d", cs[c].size, cs[c].rep); tail -= cs[c].size; }
    L += sprintf(buf + L, " tail=%ld", tail);
    out[i] = buf;
    if (dumpdir) { /* full structure: comps sorted by size, quotient edges (H_B edges between comps) */
      int *rank = xmalloc(nc * sizeof(int)); /* cid -> rank in sorted list (all comps are live) */
      if (nl != nc) { fprintf(stderr, "dead component found\n"); exit(5); }
      /* recompute sorted order mapping: cs[] sorted; need cid of each rep */
      for (int c = 0; c < nc; c++) rank[cid[cs[c].rep]] = c;
      long ne = 0, ecap = 1 << 20; uint64_t *ed = xmalloc(ecap * 8);
      for (int x = 0; x < NT; x++) for (uint64_t m = FM[x] & B; m; m &= m - 1) { int y = NB[(size_t)x * NBLK + __builtin_ctzll(m)];
        int a = rank[cid[x]], b2 = rank[cid[y]]; if (a < b2) { if (ne == ecap) { ecap *= 2; ed = realloc(ed, ecap * 8); } ed[ne++] = (uint64_t)a << 32 | b2; } }
      qsort(ed, ne, 8, cmpu64); long m2 = 0; for (long e = 0; e < ne; e++) if (!m2 || ed[e] != ed[m2 - 1]) ed[m2++] = ed[e];
      char fn[1024]; snprintf(fn, sizeof fn, "%s/%011llx.txt", dumpdir, (unsigned long long)B); FILE *g = fopen(fn, "w");
      if (!g) { perror(fn); exit(1); }
      fprintf(g, "B"); for (int b = 0; b < NBLK; b++) if (B >> b & 1) fprintf(g, " %d", b); fprintf(g, "\nN %d %ld\n", nc, m2);
      for (int c = 0; c < nc; c++) fprintf(g, "C %d %d %llu %llu\n", cs[c].size, cs[c].rep, (unsigned long long)TIL[cs[c].rep].H, (unsigned long long)TIL[cs[c].rep].V);
      for (long e = 0; e < m2; e++) fprintf(g, "E %u %u\n", (unsigned)(ed[e] >> 32), (unsigned)(ed[e] & 0xffffffffu));
      fclose(g); free(ed); free(rank);
    }
    free(cs); free(dead);
  }
  for (int i = 0; i < ns; i++) puts(out[i]);
  return 0;
}
