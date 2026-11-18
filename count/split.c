/* split.c -- given four blocks b1..b4 and a fifth block b5 (block id = 7r+c, top-left
 * cell (r,c)), take the largest class of tilings under flips in blocks outside {b1..b4}
 * and print how it splits into classes under flips in blocks outside {b1..b5}.
 * usage: split b1 b2 b3 b4 b5        e.g. split 10 15 19 31 33 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
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

int *par2;
int fnd2(int x){while(par2[x]!=x){par2[x]=par2[par2[x]];x=par2[x];}return x;}
int main(int argc,char**argv){
  if(argc!=6){fprintf(stderr,"usage: %s b1 b2 b3 b4 b5   (block ids 0..41, block 7r+c has top left cell (r,c))\n",argv[0]);return 2;}
  for(int i=1;i<6;i++){char*e;long b=strtol(argv[i],&e,10);if(*e||e==argv[i]||b<0||b>41){fprintf(stderr,"%s: bad block id \"%s\"\n",argv[0],argv[i]);return 1;}}
  T=malloc(sizeof(u128)*cap); rec(0); qsort(T,nt,sizeof(u128),cmp);
  int b1[42]={0},b2[42]={0}; int x;
  for(int i=0;i<4;i++){x=atoi(argv[1+i]);b1[x]=1;b2[x]=1;} b2[atoi(argv[5])]=1;
  par=malloc(sizeof(int)*nt);par2=malloc(sizeof(int)*nt);for(long i=0;i<nt;i++)par[i]=par2[i]=i;
  for(long i=0;i<nt;i++){u128 t=T[i];
    for(int r=0;r<6;r++)for(int c=0;c<7;c++){
      u128 h=((u128)1<<(r*7+c))|((u128)1<<((r+1)*7+c)); u128 v=((u128)1<<(49+r*8+c))|((u128)1<<(49+r*8+c+1));
      if((t&h)==h){u128 u=(t&~h)|v;long j=find(u);
        if(!b1[r*7+c]){int a=fnd(i),b=fnd(j);if(a!=b)par[a]=b;}
        if(!b2[r*7+c]){int a=fnd2(i),b=fnd2(j);if(a!=b)par2[a]=b;}}}}
  long *s1=calloc(nt,8),*s2=calloc(nt,8);for(long i=0;i<nt;i++)s1[fnd(i)]++;
  long big=0,br=-1;for(long i=0;i<nt;i++)if(s1[i]>big){big=s1[i];br=i;}
  for(long i=0;i<nt;i++)if(fnd(i)==br)s2[fnd2(i)]++;
  printf("big %ld splits into:",big);long tot=0;for(long i=0;i<nt;i++)if(s2[i]){printf(" %ld",s2[i]);tot+=s2[i];}printf(" (sum %ld)\n",tot);
}