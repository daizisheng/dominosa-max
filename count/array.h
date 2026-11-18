/* array.h -- argument checking shared by the programs of count/ */
#ifndef ARRAY_H
#define ARRAY_H
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
/* 1 if s is 7 rows of 8 digits 0..6 separated by '/', else 0 */
static int valid_array(const char *s) {
  if (strlen(s) != 62) return 0;
  for (int i = 0; i < 62; i++) {
    if (i % 9 == 8) { if (s[i] != '/') return 0; }
    else if (s[i] < '0' || s[i] > '6') return 0;
  }
  return 1;
}
/* exactly one argument, a valid array; otherwise print usage (exit 2) or an error (exit 1) */
static void need_array(int argc, char **argv) {
  if (argc != 2) { fprintf(stderr, "usage: %s ARRAY   (7 rows of 8 digits 0-6 separated by '/')\n", argv[0]); exit(2); }
  if (!valid_array(argv[1])) {
    fprintf(stderr, "%s: bad array \"%s\": expected 7 rows of 8 digits 0-6 separated by '/'\n", argv[0], argv[1]); exit(1);
  }
}
#endif
