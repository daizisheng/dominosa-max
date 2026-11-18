/* bfb.c -- brute force B (independent of bfa.c) for double-n Dominosa, n <= 3.
 * Different reduction: only fix A[0] = 0 (relabeling 0<->v is a bijection between
 * arrays with A[0]=0 and A[0]=v), so histogram(all) = (n+1) * histogram(A[0]=0).
 * Different counting: at each leaf, test every tiling directly (list of dominoes,
 * bitmask of pieces seen, early exit on a repeat).
 * Arrays are generated as multiset permutations by recursion on cells.
 * Usage: bfb n J j PREF MINREC
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static int n, R, C, N, K, T;
static unsigned char dom[200][15][2];   /* tiling -> list of K dominoes (cells) */
static int code[8][8];
static int A[64], left[8];
static long long hist[256], J, jj, PREF, MINREC, pidx;

/* tilings: scan for the first empty cell (row-major) and cover it */
static int filled[64]; static int nd; static unsigned char cur[15][2];
static void gen(void) {
    int p = 0; while (p < N && filled[p]) p++;
    if (p == N) { memcpy(dom[T++], cur, sizeof cur); return; }
    int r = p / C, c = p % C;
    if (r + 1 < R) { filled[p] = filled[p + C] = 1; cur[nd][0] = p; cur[nd][1] = p + C; nd++; gen(); nd--; filled[p] = filled[p + C] = 0; }
    if (c + 1 < C && !filled[p + 1]) { filled[p] = filled[p + 1] = 1; cur[nd][0] = p; cur[nd][1] = p + 1; nd++; gen(); nd--; filled[p] = filled[p + 1] = 0; }
}

static int count(void) {
    int s = 0;
    for (int t = 0; t < T; t++) {
        unsigned m = 0; int ok = 1;
        for (int d = 0; d < K; d++) {
            unsigned b = 1u << code[A[dom[t][d][0]]][A[dom[t][d][1]]];
            if (m & b) { ok = 0; break; }
            m |= b;
        }
        s += ok;
    }
    return s;
}

static void rec(int p) {
    if (p == PREF && (pidx++ % J) != jj) return;
    if (p == N) {
        int s = count(); hist[s]++;
        if (s >= MINREC) {
            for (int i = 0; i < N; i++) { putchar('0' + A[i]); if (i % C == C - 1 && i + 1 < N) putchar('/'); }
            printf(" %d\n", s);
        }
        return;
    }
    for (int v = 0; v <= n; v++) {
        if (!left[v]) continue;
        if (p == 0 && v != 0) continue;
        left[v]--; A[p] = v; rec(p + 1); left[v]++;
    }
}

int main(int argc, char **argv) {
    if (argc != 6 || atoi(argv[1]) < 1 || atoi(argv[1]) > 3 || atoll(argv[2]) < 1) {
        fprintf(stderr, "usage: %s n J j PREF MINREC   (1 <= n <= 3; slice j of J at prefix length PREF)\n", argv[0]); return 2; }
    n = atoi(argv[1]); J = atoll(argv[2]); jj = atoll(argv[3]); PREF = atoll(argv[4]); MINREC = atoll(argv[5]);
    R = n + 1; C = n + 2; N = R * C; K = (n + 1) * (n + 2) / 2;
    int k = 0;
    for (int i = 0; i <= n; i++) for (int j = i; j <= n; j++) code[i][j] = code[j][i] = k++;
    gen();
    for (int v = 0; v <= n; v++) left[v] = n + 2;
    rec(0);
    long long tot = 0, s1 = 0, s2 = 0;
    for (int s = 0; s <= T; s++) if (hist[s]) { printf("H %d %lld\n", s, hist[s]); tot += hist[s]; s1 += hist[s] * s; s2 += hist[s] * s * s; }
    printf("TOTAL %lld SUMSOL %lld SUMSQ %lld T %d prefixes %lld\n", tot, s1, s2, T, pidx);
    return 0;
}
