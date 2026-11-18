/* bb.c -- branch and bound over arrays, independent of the block method.
 * Cells are filled in row-major order with first-occurrence canonical labels (each
 * relabeling orbit has exactly (n+1)! members, one canonical), each value n+2 times.
 * alive = tilings none of whose completed dominoes repeats a piece.  #solutions of any
 * completion <= |alive|, so a node with |alive| < THR is pruned.  Every leaf with
 * >= THR solutions is printed.  Hence: no output line with count > THR-1 ... the
 * program finds ALL canonical arrays with >= THR solutions.
 * Extra pruning (still block-free): a tiling also dies if some piece has already been
 * used twice... (not needed: covered by alive).
 * Usage: bb n THR J j PREF
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

#define MAXW 512
static int n, R, C, N, K, T, W;
static int occ[64], part[64];
static uint64_t *Lp[64], *Up[64];
static uint64_t *used[64];     /* used[depth] : K*W words */
static uint64_t *alive[64];    /* W words */
static int A[64], cnt[8], code[8][8];
static long long THR, J, jj, PREF, pidx, nodes, leaves;
static int tcap = 0; static int (*tp)[64] = NULL;

static void tilerec(int p) {
    while (p < N && occ[p]) p++;
    if (p == N) {
        if (T == tcap) { tcap = tcap ? 2 * tcap : 1024; tp = realloc(tp, sizeof(int[64]) * tcap); }
        memcpy(tp[T++], part, sizeof(int) * 64); return;
    }
    int r = p / C, c = p % C;
    if (c + 1 < C && !occ[p + 1]) { occ[p] = occ[p + 1] = 1; part[p] = p + 1; part[p + 1] = p; tilerec(p + 1); occ[p] = occ[p + 1] = 0; }
    if (r + 1 < R) { occ[p] = occ[p + C] = 1; part[p] = p + C; part[p + C] = p; tilerec(p + 1); occ[p] = occ[p + C] = 0; }
}

static void dfs(int p, int maxv) {
    nodes++;
    if (p == PREF && (pidx++ % J) != jj) return;
    if (p == N) {
        leaves++;
        long long s = 0; for (int i = 0; i < W; i++) s += __builtin_popcountll(alive[N][i]);
        for (int i = 0; i < N; i++) { putchar('0' + A[i]); if (i % C == C - 1 && i + 1 < N) putchar('/'); }
        printf(" %lld\n", s);
        return;
    }
    int top = maxv + 1; if (top > n) top = n;
    for (int v = 0; v <= top; v++) {
        if (cnt[v] == n + 2) continue;
        A[p] = v; cnt[v]++;
        uint64_t *u1 = used[p + 1], *al = alive[p + 1];
        memcpy(u1, used[p], sizeof(uint64_t) * K * W);
        memcpy(al, alive[p], sizeof(uint64_t) * W);
        if (p % C > 0) {
            uint64_t *u = u1 + code[A[p - 1]][v] * W, *m = Lp[p];
            for (int i = 0; i < W; i++) { al[i] &= ~(u[i] & m[i]); u[i] |= m[i]; }
        }
        if (p >= C) {
            uint64_t *u = u1 + code[A[p - C]][v] * W, *m = Up[p];
            for (int i = 0; i < W; i++) { al[i] &= ~(u[i] & m[i]); u[i] |= m[i]; }
        }
        long long s = 0; for (int i = 0; i < W; i++) s += __builtin_popcountll(al[i]);
        if (s >= THR) dfs(p + 1, v > maxv ? v : maxv);
        cnt[v]--;
    }
}

int main(int argc, char **argv) {
    if (argc != 6 || atoi(argv[1]) < 1 || atoi(argv[1]) > 5 || atoll(argv[3]) < 1) {
        fprintf(stderr, "usage: %s n THR J j PREF   (1 <= n <= 5; slice j of J at prefix length PREF)\n", argv[0]); return 2; }
    n = atoi(argv[1]); THR = atoll(argv[2]); J = atoll(argv[3]); jj = atoll(argv[4]); PREF = atoll(argv[5]);
    R = n + 1; C = n + 2; N = R * C; K = (n + 1) * (n + 2) / 2;
    int k = 0; for (int i = 0; i <= n; i++) for (int j = i; j <= n; j++) code[i][j] = code[j][i] = k++;
    T = 0; tilerec(0); W = (T + 63) / 64;
    for (int p = 0; p < N; p++) { Lp[p] = calloc(W, 8); Up[p] = calloc(W, 8); }
    for (int t = 0; t < T; t++) for (int p = 0; p < N; p++) {
        if (tp[t][p] == p - 1) Lp[p][t / 64] |= 1ULL << (t % 64);
        if (tp[t][p] == p - C) Up[p][t / 64] |= 1ULL << (t % 64);
    }
    for (int d = 0; d <= N; d++) { used[d] = calloc((size_t)K * W, 8); alive[d] = calloc(W, 8); }
    for (int t = 0; t < T; t++) alive[0][t / 64] |= 1ULL << (t % 64);
    dfs(0, -1);
    fprintf(stderr, "T %d nodes %lld leaves %lld prefixes %lld\n", T, nodes, leaves, pidx);
    printf("END T %d nodes %lld leaves(>=THR) %lld prefixes %lld\n", T, nodes, leaves, pidx);
    return 0;
}
