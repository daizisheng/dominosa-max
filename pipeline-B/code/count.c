/* count.c: count solutions of arrays by brute force over all tilings.
 * usage: count DATADIR array [array ...]   (array = 8 digits per row, rows separated by '/') */
#include "common.h"
int main(int argc, char **argv) {
  if (argc < 3) { fprintf(stderr, "usage: %s DATADIR ARRAY [ARRAY ...]\n", argv[0]); return 2; }
  load_all(argv[1]);
  int rc = 0;
  for (int i = 2; i < argc; i++) {
    int A[56]; if (!parse_array(argv[i], A)) { fprintf(stderr, "%s: bad array \"%s\": expected 7 rows of 8 digits 0-6 separated by '/'\n", argv[0], argv[i]); rc = 1; continue; }
    int cnt[7] = {0}; for (int c = 0; c < 56; c++) cnt[A[c]]++;
    long n = 0; for (int t = 0; t < NT; t++) n += is_solution(TIL[t], A);
    printf("%s solutions=%ld bad=", argv[i], n); print_set(stdout, bad_set(A));
    printf(" canon="); print_set(stdout, set_canon(bad_set(A)));
    printf(" valuecounts="); for (int v = 0; v < 7; v++) printf("%d", cnt[v]); puts("");
  }
  return rc;
}
