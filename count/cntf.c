// cntf.c -- read arrays from stdin (the last field of each line) and print "count array".
#include <stdio.h>
#include "count.h"
int main(){init_types();Ctx*c=ctx_new();char line[4096];int rc=0;while(fgets(line,sizeof line,stdin)){char*p=strrchr(line,' ');p=p?p+1:line;uint8_t g[N];if(parse_grid(p,g)){if(*p!='\n'){fprintf(stderr,"cntf: bad array: %s",p);rc=1;}continue;}printf("%llu %s",(unsigned long long)count_sol(c,g),p);}return rc;}
