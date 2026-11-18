// cnt.c -- count solutions with the meet-in-the-middle counter of count.h.
// usage: cnt ARRAY [ARRAY ...]   (each count is repeated 200 times to time it)
#include <stdio.h>
#include <time.h>
#include "count.h"
int main(int argc,char**argv){if(argc<2){fprintf(stderr,"usage: %s ARRAY [ARRAY ...]\n",argv[0]);return 2;}
 init_types();Ctx*c=ctx_new();int rc=0;
 for(int a=1;a<argc;a++){uint8_t g[N];if(parse_grid(argv[a],g)){fprintf(stderr,"%s: bad array \"%s\": expected 7 rows of 8 digits 0-6 separated by '/'\n",argv[0],argv[a]);rc=1;continue;}
  clock_t t=clock();uint64_t n=0;int reps=200;for(int r=0;r<reps;r++)n=count_sol(c,g);
  printf("%s %llu  %.3f ms/eval\n",argv[a],(unsigned long long)n,1000.0*(clock()-t)/CLOCKS_PER_SEC/reps);}
 return rc;
}
