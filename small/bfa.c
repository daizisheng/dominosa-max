/* bfa.c -- brute force A for double-n Dominosa, n <= 3.
 * Enumerates arrays in first-occurrence canonical form (value of each cell is at most
 * 1 + max value so far; each value exactly n+2 times).  Every relabeling orbit has
 * exactly (n+1)! members and exactly one canonical member, so
 *     histogram(all arrays) = (n+1)! * histogram(canonical arrays).
 * Counting: incremental bitsets.  used[k] = set of tilings in which piece k has already
 * appeared; alive = tilings with no repeated piece so far.  When cell p gets its value,
 * the domino of tiling t that covers p is completed iff its partner is p-1 or p-C.
 * Usage: bfa n J j PREF MINREC   (job j of J; split at prefix length PREF;
 *        print arrays with >= MINREC solutions)
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

#define MAXT 128
#define W 2
typedef struct { uint64_t w[W]; } bs;

static int n, R, C, N, K, T;
static int occ[64];
static int tilpart[MAXT][64];           /* partner cell of p in tiling t */
static bs Lp[64], Up[64];               /* tilings where p's partner is p-1 / p-C */
static int A[64], cnt[8];
static long long hist[MAXT + 1];
static long long J, jj, PREF, MINREC, prefidx;
static int pairidx[8][8];

static void tilerec(int p, int *part) {
    while (p < N && occ[p]) p++;
    if (p == N) {
        if (T >= MAXT) { fprintf(stderr, "too many tilings\n"); exit(1); }
        memcpy(tilpart[T], part, sizeof(int) * N); T++; return;
    }
    int r = p / C, c = p % C;
    if (c + 1 < C && !occ[p + 1]) {
        occ[p] = occ[p + 1] = 1; part[p] = p + 1; part[p + 1] = p;
        tilerec(p + 1, part); occ[p] = occ[p + 1] = 0;
    }
    if (r + 1 < R) {
        occ[p] = occ[p + C] = 1; part[p] = p + C; part[p + C] = p;
        tilerec(p + 1, part); occ[p] = occ[p + C] = 0;
    }
}

static inline int popc(const bs *a) { int s = 0; for (int i = 0; i < W; i++) s += __builtin_popcountll(a->w[i]); return s; }

static bs usedst[64][16];
static bs alivest[64];

static void dfs(int p, int maxv) {
    if (p == PREF) { if ((prefidx++ % J) != jj) return; }
    if (p == N) {
        int s = popc(&alivest[N]);
        hist[s]++;
        if (s >= MINREC) {
            for (int r = 0; r < R; r++) { for (int c = 0; c < C; c++) putchar('0' + A[r * C + c]); putchar(r + 1 < R ? '/' : ' '); }
            printf("%d\n", s);
        }
        return;
    }
    int top = maxv + 1; if (top > n) top = n;
    for (int v = 0; v <= top; v++) {
        if (cnt[v] == n + 2) continue;
        A[p] = v; cnt[v]++;
        bs *u0 = usedst[p], *u1 = usedst[p + 1];
        memcpy(u1, u0, sizeof(bs) * K);
        bs al = alivest[p];
        int c = p % C;
        if (c > 0) {
            int k = pairidx[A[p - 1]][v];
            for (int i = 0; i < W; i++) { al.w[i] &= ~(u1[k].w[i] & Lp[p].w[i]); u1[k].w[i] |= Lp[p].w[i]; }
        }
        if (p >= C) {
            int k = pairidx[A[p - C]][v];
            for (int i = 0; i < W; i++) { al.w[i] &= ~(u1[k].w[i] & Up[p].w[i]); u1[k].w[i] |= Up[p].w[i]; }
        }
        alivest[p + 1] = al;
        dfs(p + 1, v > maxv ? v : maxv);
        cnt[v]--;
    }
}

int main(int argc, char **argv) {
    if (argc != 6 || atoi(argv[1]) < 1 || atoi(argv[1]) > 3 || atoll(argv[2]) < 1) {
        fprintf(stderr, "usage: %s n J j PREF MINREC   (1 <= n <= 3; slice j of J at prefix length PREF)\n", argv[0]); return 2; }
    n = atoi(argv[1]); J = atoll(argv[2]); jj = atoll(argv[3]); PREF = atoll(argv[4]); MINREC = atoll(argv[5]);
    R = n + 1; C = n + 2; N = R * C; K = (n + 1) * (n + 2) / 2;
    int k = 0;
    for (int j = 0; j <= n; j++) for (int i = 0; i <= j; i++) { pairidx[i][j] = pairidx[j][i] = k++; }
    int part[64]; T = 0; memset(occ, 0, sizeof occ);
    tilerec(0, part);
    for (int t = 0; t < T; t++) for (int p = 0; p < N; p++) {
        int q = tilpart[t][p];
        if (q == p - 1) Lp[p].w[t / 64] |= 1ULL << (t % 64);
        if (q == p - C) Up[p].w[t / 64] |= 1ULL << (t % 64);
    }
    memset(usedst, 0, sizeof usedst);
    for (int t = 0; t < T; t++) alivest[0].w[t / 64] |= 1ULL << (t % 64);
    dfs(0, -1);
    long long tot = 0, s1 = 0;
    for (int s = 0; s <= T; s++) if (hist[s]) { printf("H %d %lld\n", s, hist[s]); tot += hist[s]; s1 += hist[s] * s; }
    printf("TOTAL %lld SUMSOL %lld T %d prefixes %lld\n", tot, s1, T, prefidx);
    return 0;
}
