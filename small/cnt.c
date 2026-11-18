/* cnt.c -- read arrays "r0/r1/.../rn" (one per line, optional trailing text) from stdin,
 * print "<array> <#solutions>".  Row-major DFS placing dominoes with a used-piece mask.
 * Usage: cnt n
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
static int n, R, C, N, A[64], occ[64], code[8][8];
static long long c;
static void dfs(int p, uint32_t used) {
    while (p < N && occ[p]) p++;
    if (p == N) { c++; return; }
    if (p % C + 1 < C && !occ[p + 1]) { uint32_t b = 1u << code[A[p]][A[p + 1]]; if (!(used & b)) { occ[p + 1] = 1; dfs(p + 1, used | b); occ[p + 1] = 0; } }
    if (p + C < N) { uint32_t b = 1u << code[A[p]][A[p + C]]; if (!(used & b)) { occ[p + C] = 1; dfs(p + 1, used | b); occ[p + C] = 0; } }
}
int main(int argc, char **argv) {
    if (argc != 2 || atoi(argv[1]) < 1 || atoi(argv[1]) > 6) { fprintf(stderr, "usage: %s n   (1 <= n <= 6; arrays on stdin)\n", argv[0]); return 2; }
    n = atoi(argv[1]); R = n + 1; C = n + 2; N = R * C;
    int rc = 0;
    int k = 0; for (int i = 0; i <= n; i++) for (int j = i; j <= n; j++) code[i][j] = code[j][i] = k++;
    char line[512];
    while (fgets(line, sizeof line, stdin)) {
        int m = 0, bad = 0, pos = 0; char *s = line;
        for (; *s && *s != ' ' && *s != '\n'; s++, pos++) {   /* R rows of C digits 0..n separated by '/' */
            if (pos % (C + 1) == C) { if (*s != '/') bad = 1; }
            else if (*s < '0' || *s > '0' + n || m >= N) bad = 1;
            else A[m++] = *s - '0';
        }
        if (bad || m != N || pos != R * (C + 1) - 1) {
            if (s != line) { *s = 0; fprintf(stderr, "cnt: bad array \"%s\" for n = %d\n", line, n); rc = 1; }
            continue;
        }
        int cnts[8] = {0}; for (int i = 0; i < N; i++) cnts[A[i]]++;
        int okc = 1; for (int v = 0; v <= n; v++) if (cnts[v] != n + 2) okc = 0;
        c = 0; memset(occ, 0, sizeof occ); dfs(0, 0);
        *s = 0; printf("%s %lld%s\n", line, c, okc ? "" : " BADCOUNTS");
    }
    return rc;
}
