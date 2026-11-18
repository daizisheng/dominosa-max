/* dc.c -- count the solutions of a double-six Dominosa array (7 rows x 8 columns)
 * by plain backtracking: cover the first empty cell (row-major) by a horizontal or a
 * vertical domino whose piece has not been used yet.
 * usage: dc ARRAY        ARRAY = 7 rows of 8 digits, rows separated by '/'
 * prints "ARRAY -> number_of_solutions" (and a warning if some value does not occur 8 times) */
#include <stdio.h>
#include <string.h>
#include "array.h"
int g[7][8], occ[7][8], used[7][7]; long cnt;
void rec(int pos){
  while(pos<56 && occ[pos/8][pos%8]) pos++;
  if(pos==56){cnt++;return;}
  int r=pos/8,c=pos%8;
  if(c<7 && !occ[r][c+1]){int a=g[r][c],b=g[r][c+1];int x=a<b?a:b,y=a<b?b:a;
    if(!used[x][y]){used[x][y]=1;occ[r][c]=occ[r][c+1]=1;rec(pos+1);occ[r][c]=occ[r][c+1]=0;used[x][y]=0;}}
  if(r<6){int a=g[r][c],b=g[r+1][c];int x=a<b?a:b,y=a<b?b:a;
    if(!used[x][y]){used[x][y]=1;occ[r][c]=occ[r+1][c]=1;rec(pos+1);occ[r][c]=occ[r+1][c]=0;used[x][y]=0;}}
}
int main(int argc,char**argv){
  need_array(argc,argv);
  const char*s=argv[1]; int k=0;
  for(int i=0;s[i];i++) if(s[i]>='0'&&s[i]<='6'){g[k/8][k%8]=s[i]-'0';k++;}
  int h[7]={0}; for(int i=0;i<56;i++) h[g[i/8][i%8]]++;
  for(int v=0;v<7;v++) if(h[v]!=8) printf("value %d appears %d times\n",v,h[v]);
  rec(0); printf("%s -> %ld\n",s,cnt);
}
