/* classes.c -- class structure of a double-six array: enumerate all 1,292,697 tilings,
 * join two tilings when they differ by a flip in a good block of the array (a=d or b=c),
 * and report the bad blocks, the classes, which classes consist of solutions, and
 * the number of flips in bad blocks that join two solutions (always 0, Lemma 2).
 * usage: classes ARRAY */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "array.h"
typedef unsigned __int128 u128;
/* position ids: horizontal at (r,c) c<7: id = r*7+c (0..48); vertical at (r,c) r<6: id = 49 + r*8+c (49..96) */
static u128 *T; static long nt=0, cap=1<<21;
int occ[7][8]; u128 cur=0;
void rec(int pos){
  while(pos<56&&occ[pos/8][pos%8])pos++;
  if(pos==56){T[nt++]=cur;return;}
  int r=pos/8,c=pos%8;
  if(c<7&&!occ[r][c+1]){occ[r][c]=occ[r][c+1]=1;cur|=(u128)1<<(r*7+c);rec(pos+1);cur&=~((u128)1<<(r*7+c));occ[r][c]=occ[r][c+1]=0;}
  if(r<6){occ[r][c]=occ[r+1][c]=1;cur|=(u128)1<<(49+r*8+c);rec(pos+1);cur&=~((u128)1<<(49+r*8+c));occ[r][c]=occ[r+1][c]=0;}
}
int cmp(const void*a,const void*b){u128 x=*(u128*)a,y=*(u128*)b;return x<y?-1:x>y;}
long find(u128 k){long lo=0,hi=nt-1;while(lo<=hi){long m=(lo+hi)/2;if(T[m]==k)return m;if(T[m]<k)lo=m+1;else hi=m-1;}return -1;}
int *par;
int fnd(int x){while(par[x]!=x){par[x]=par[par[x]];x=par[x];}return x;}
int g[7][8];
int issol(u128 t){int used[49]={0};for(int r=0;r<7;r++)for(int c=0;c<8;c++){
  int a=-1,b=-1; if(c<7&&((t>>(r*7+c))&1)){a=g[r][c];b=g[r][c+1];} if(r<6&&((t>>(49+r*8+c))&1)){a=g[r][c];b=g[r+1][c];}
  if(a>=0){int x=a<b?a:b,y=a<b?b:a;if(used[x*7+y]++)return 0;}}return 1;}
int main(int argc,char**argv){
  need_array(argc,argv);
  T=malloc(sizeof(u128)*cap); rec(0); printf("tilings %ld\n",nt);
  qsort(T,nt,sizeof(u128),cmp);
  const char*s=argv[1];int k=0;for(int i=0;s[i];i++)if(s[i]>='0'&&s[i]<='6'){g[k/8][k%8]=s[i]-'0';k++;}
  int bad[42],nb=0;
  for(int r=0;r<6;r++)for(int c=0;c<7;c++){int A=g[r][c],B=g[r][c+1],C=g[r+1][c],D=g[r+1][c+1];bad[r*7+c]=!(A==D||B==C);if(bad[r*7+c])printf("bad block %d (%d,%d)\n",r*7+c,r,c),nb++;}
  par=malloc(sizeof(int)*nt);for(long i=0;i<nt;i++)par[i]=i;
  long edges=0,badsolsol=0;
  for(long i=0;i<nt;i++){u128 t=T[i];
    for(int r=0;r<6;r++)for(int c=0;c<7;c++){
      u128 h=((u128)1<<(r*7+c))|((u128)1<<((r+1)*7+c)); u128 v=((u128)1<<(49+r*8+c))|((u128)1<<(49+r*8+c+1));
      if((t&h)==h){u128 u=(t&~h)|v;long j=find(u);if(j<0){printf("ERR\n");return 1;}
        if(!bad[r*7+c]){edges++;int a=fnd(i),b=fnd(j);if(a!=b)par[a]=b;}
        else if(issol(t)&&issol(u))badsolsol++;}
    }}
  printf("good flip edges %ld, bad flips joining two solutions %ld\n",edges,badsolsol);
  /* component sizes and solution counts */
  long *sz=calloc(nt,sizeof(long)),*so=calloc(nt,sizeof(long));long tot=0,ncomp=0;
  for(long i=0;i<nt;i++){int r=fnd(i);sz[r]++;if(issol(T[i])){so[r]++;tot++;}}
  for(long i=0;i<nt;i++)if(sz[i]){ncomp++;if(so[i]&&so[i]!=sz[i])printf("MIXED component!\n");}
  printf("components %ld, total solutions %ld\n",ncomp,tot);
  for(long i=0;i<nt;i++)if(so[i])printf("  valid component size %ld\n",sz[i]);
  /* largest components */
  long best[5]={0};for(long i=0;i<nt;i++)if(sz[i]){long x=sz[i];for(int q=0;q<5;q++)if(x>best[q]){long y=best[q];best[q]=x;x=y;}}
  printf("largest components:");for(int q=0;q<5;q++)printf(" %ld",best[q]);printf("\n");
}
