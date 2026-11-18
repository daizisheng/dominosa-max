/* bb3.c -- branch and bound over arrays, independent of the block method (no 2x2
 * blocks, no flips, no classes, no SAT).  Same bound as bb.c / bb2.c:
 *   alive = tilings none of whose completed dominoes repeats a piece;
 *   #solutions of every completion <= |alive|;  prune when |alive| < THR.
 * Symmetry reduction: G = {identity, left-right mirror} x (value relabelings).
 * Cells are filled row-major; labels are first-occurrence canonical; and an array A is
 * kept only if A <=lex canon(mirror(A)), checked at the end of every row (prefix test;
 * once A is strictly smaller the test stops).  Every leaf (all its >= THR solutions)
 * is printed with its weight: number of arrays in its G-orbit = (n+1)! * (1 or 2).
 * Usage: bb3 n THR J j PREF        (slice j of J at prefix length PREF)
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

static int n, R, C, N, K, T, W;
static int occ[64], part[64];
static uint64_t *Lp[64], *Up[64];
static uint64_t *alive[64];
static uint64_t *usedcur;
static uint64_t *save[64][2];
static int A[64], cnt[8], code[8][8];
static long long THR, J, jj, PREF, pidx, nodes, leaves, fact;
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

/* compare A[0..len) with first-occurrence relabeling of the mirror image, rows 0..len/C */
static int cmp_mirror(int len) {
    int map[8]; for (int v = 0; v < 8; v++) map[v] = -1;
    int nx = 0;
    for (int i = 0; i < len; i++) {
        int r = i / C, c = i % C;
        int v = A[r * C + (C - 1 - c)];
        if (map[v] < 0) map[v] = nx++;
        int m = map[v];
        if (A[i] < m) return -1;
        if (A[i] > m) return 1;
    }
    return 0;
}

static void dfs(int p, int maxv, int less) {
    nodes++;
    if (p == PREF && (pidx++ % J) != jj) return;
    if (p > 0 && p % C == 0 && !less) {
        int c = cmp_mirror(p);
        if (c > 0) return;
        if (c < 0) less = 1;
    }
    if (p == N) {
        leaves++;
        long long s = 0; for (int i = 0; i < W; i++) s += __builtin_popcountll(alive[N][i]);
        for (int i = 0; i < N; i++) { putchar('0' + A[i]); if (i % C == C - 1 && i + 1 < N) putchar('/'); }
        printf(" %lld %lld\n", s, fact * (less ? 2 : 1));
        return;
    }
    int top = maxv + 1; if (top > n) top = n;
    for (int v = 0; v <= top; v++) {
        if (cnt[v] == n + 2) continue;
        A[p] = v; cnt[v]++;
        uint64_t *al = alive[p + 1], *a0 = alive[p];
        int kL = -1, kU = -1;
        uint64_t *uL = NULL, *uU = NULL, *mL = Lp[p], *mU = Up[p];
        if (p % C > 0) { kL = code[A[p - 1]][v]; uL = usedcur + kL * W; memcpy(save[p][0], uL, 8 * W); }
        if (p >= C)    { kU = code[A[p - C]][v]; uU = usedcur + kU * W; }
        long long s = 0;
        if (uL && uU) {
            if (kU == kL) {
                for (int i = 0; i < W; i++) {
                    uint64_t u = uL[i], x = a0[i] & ~(u & mL[i]);
                    u |= mL[i];
                    x &= ~(u & mU[i]);
                    uL[i] = u | mU[i];
                    al[i] = x; s += __builtin_popcountll(x);
                }
            } else {
                memcpy(save[p][1], uU, 8 * W);
                for (int i = 0; i < W; i++) {
                    uint64_t x = a0[i] & ~(uL[i] & mL[i]) & ~(uU[i] & mU[i]);
                    uL[i] |= mL[i]; uU[i] |= mU[i];
                    al[i] = x; s += __builtin_popcountll(x);
                }
            }
        } else if (uL) {
            for (int i = 0; i < W; i++) { uint64_t x = a0[i] & ~(uL[i] & mL[i]); uL[i] |= mL[i]; al[i] = x; s += __builtin_popcountll(x); }
        } else if (uU) {
            memcpy(save[p][1], uU, 8 * W);
            for (int i = 0; i < W; i++) { uint64_t x = a0[i] & ~(uU[i] & mU[i]); uU[i] |= mU[i]; al[i] = x; s += __builtin_popcountll(x); }
        } else {
            for (int i = 0; i < W; i++) { al[i] = a0[i]; s += __builtin_popcountll(a0[i]); }
        }
        if (s >= THR) dfs(p + 1, v > maxv ? v : maxv, less);
        if (uU && kU != kL) memcpy(uU, save[p][1], 8 * W);
        if (uL) memcpy(uL, save[p][0], 8 * W);
        else if (uU) memcpy(uU, save[p][1], 8 * W);
        cnt[v]--;
    }
}

int main(int argc, char **argv) {
    if (argc != 6 || atoi(argv[1]) < 1 || atoi(argv[1]) > 6 || atoll(argv[3]) < 1) {
        fprintf(stderr, "usage: %s n THR J j PREF   (1 <= n <= 6; slice j of J at prefix length PREF)\n", argv[0]); return 2; }
    n = atoi(argv[1]); THR = atoll(argv[2]); J = atoll(argv[3]); jj = atoll(argv[4]); PREF = atoll(argv[5]);
    R = n + 1; C = n + 2; N = R * C; K = (n + 1) * (n + 2) / 2;
    fact = 1; for (int i = 2; i <= n + 1; i++) fact *= i;
    int k = 0; for (int i = 0; i <= n; i++) for (int j = i; j <= n; j++) code[i][j] = code[j][i] = k++;
    T = 0; tilerec(0); W = (T + 63) / 64;
    for (int p = 0; p < N; p++) { Lp[p] = calloc(W, 8); Up[p] = calloc(W, 8); }
    for (int t = 0; t < T; t++) for (int p = 0; p < N; p++) {
        if (tp[t][p] == p - 1) Lp[p][t / 64] |= 1ULL << (t % 64);
        if (tp[t][p] == p - C) Up[p][t / 64] |= 1ULL << (t % 64);
    }
    for (int d = 0; d <= N; d++) { alive[d] = calloc(W, 8); save[d][0] = calloc(W, 8); save[d][1] = calloc(W, 8); }
    usedcur = calloc((size_t)(K > 0 ? K : 1) * (size_t)(W > 0 ? W : 1), 8);
    for (int t = 0; t < T; t++) alive[0][t / 64] |= 1ULL << (t % 64);
    dfs(0, -1, 0);
    fprintf(stderr, "T %d nodes %lld leaves %lld prefixes %lld\n", T, nodes, leaves, pidx);
    printf("END T %d nodes %lld leaves(>=THR) %lld prefixes %lld\n", T, nodes, leaves, pidx);
    return 0;
}
