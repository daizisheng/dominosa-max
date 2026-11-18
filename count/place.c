/* place.c -- count solutions and, for each of the 97 candidate placements (pairs of
 * adjacent cells), the number of solutions using it; prints the smallest of these counts.
 * Position ids: horizontal domino at (r,c), c<7: r*7+c (0..48); vertical at (r,c), r<6: 49+r*8+c.
 * usage: place ARRAY */
#include <stdio.h>
#include "array.h"
int g[7][8], occ[7][8], used[7][7]; long cnt; long pc[97]; int stack[28],sp=0;
void rec(int pos){
  while(pos<56 && occ[pos/8][pos%8]) pos++;
  if(pos==56){cnt++;for(int i=0;i<28;i++)pc[stack[i]]++;return;}
  int r=pos/8,c=pos%8;
  if(c<7 && !occ[r][c+1]){int a=g[r][c],b=g[r][c+1];int x=a<b?a:b,y=a<b?b:a;
    if(!used[x][y]){used[x][y]=1;occ[r][c]=occ[r][c+1]=1;stack[sp++]=r*7+c;rec(pos+1);sp--;occ[r][c]=occ[r][c+1]=0;used[x][y]=0;}}
  if(r<6){int a=g[r][c],b=g[r+1][c];int x=a<b?a:b,y=a<b?b:a;
    if(!used[x][y]){used[x][y]=1;occ[r][c]=occ[r+1][c]=1;stack[sp++]=49+r*8+c;rec(pos+1);sp--;occ[r][c]=occ[r+1][c]=0;used[x][y]=0;}}
}
int main(int argc,char**argv){need_array(argc,argv);const char*s=argv[1];int k=0;
  for(int i=0;s[i];i++) if(s[i]>='0'&&s[i]<='6'){g[k/8][k%8]=s[i]-'0';k++;}
  rec(0); long mn=1L<<60;int arg=-1;for(int i=0;i<97;i++)if(pc[i]<mn){mn=pc[i];arg=i;}
  printf("%s: %ld solutions, min placement count %ld at position %d\n",s,cnt,mn,arg);}
