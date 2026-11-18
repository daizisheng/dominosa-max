// tilings.c -- enumerate all 1,292,697 domino tilings of 7x8 and test each one against the array
// (a tiling is a solution if its 28 dominoes carry 28 different pieces).  Also join tilings that
// differ by a flip in a good 2x2 block (a=d or b=c) and report the classes, the classes that
// consist of solutions, and the number of flips in bad blocks that join two solutions.
// usage: tilings ARRAY
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include "array.h"
#define MAXT 1300000
typedef struct{uint64_t h,v;} TL; // h bit i: horizontal domino at cell i,i+1 ; v bit i: vertical i,i+8
static TL T[MAXT];static int nt=0;
static void en(int i,uint64_t occ,uint64_t h,uint64_t v){while(i<56&&(occ>>i&1))i++;if(i==56){T[nt].h=h;T[nt].v=v;nt++;return;}
 if((i&7)<7&&!(occ>>(i+1)&1))en(i+2,occ|(3ull<<i),h|(1ull<<i),v);
 if(i<48)en(i+1,occ|(1ull<<i)|(1ull<<(i+8)),h,v|(1ull<<i));}
static int cmp(const void*a,const void*b){const TL*x=a,*y=b;if(x->h!=y->h)return x->h<y->h?-1:1;if(x->v!=y->v)return x->v<y->v?-1:1;return 0;}
static int find_t(uint64_t h,uint64_t v){int lo=0,hi=nt-1;while(lo<=hi){int m=(lo+hi)/2;if(T[m].h==h&&T[m].v==v)return m;if(T[m].h<h||(T[m].h==h&&T[m].v<v))lo=m+1;else hi=m-1;}return -1;}
static int par[MAXT];static int F(int x){while(par[x]!=x){par[x]=par[par[x]];x=par[x];}return x;}
int TY[7][7];
int main(int argc,char**argv){need_array(argc,argv);int k=0;for(int a=0;a<7;a++)for(int b=a;b<7;b++)TY[a][b]=TY[b][a]=k++;
 uint8_t g[56];k=0;for(char*s=argv[1];*s;s++)if(*s>='0'&&*s<='6')g[k++]=*s-'0';
 en(0,0,0,0);qsort(T,nt,sizeof(TL),cmp);printf("tilings %d\n",nt);
 for(int i=0;i<nt;i++)par[i]=i;
 int good[56];for(int r=0;r<6;r++)for(int c=0;c<7;c++){int i=r*8+c;good[i]=(g[i]==g[i+9])||(g[i+1]==g[i+8]);}
 long nbad=0,nbadvv=0;
 static char valid[MAXT];long nv=0;
 for(int t=0;t<nt;t++){uint32_t m=0;int ok=1;for(int i=0;i<56;i++){if(T[t].h>>i&1){uint32_t b=1u<<TY[g[i]][g[i+1]];if(m&b)ok=0;m|=b;}if(T[t].v>>i&1){uint32_t b=1u<<TY[g[i]][g[i+8]];if(m&b)ok=0;m|=b;}}valid[t]=ok;nv+=ok;}
 for(int t=0;t<nt;t++)for(int r=0;r<6;r++)for(int c=0;c<7;c++){int i=r*8+c;uint64_t h=T[t].h,v=T[t].v;
   if((h>>i&1)&&(h>>(i+8)&1)){uint64_t h2=h&~((1ull<<i)|(1ull<<(i+8))),v2=v|(1ull<<i)|(1ull<<(i+1));int u=find_t(h2,v2);
     if(good[i]){int a=F(t),b=F(u);if(a!=b)par[a]=b;}else{nbad++;if(valid[t]&&valid[u])nbadvv++;}}}
 // component stats
 static int sz[MAXT],vs[MAXT];int nc=0,ncv=0,mixed=0;for(int t=0;t<nt;t++){int r=F(t);sz[r]++;vs[r]+=valid[t];}
 long maxc=0;for(int t=0;t<nt;t++)if(par[t]==t){nc++;if(vs[t])ncv++;if(vs[t]&&vs[t]!=sz[t])mixed++;if(vs[t]>maxc)maxc=vs[t];}
 printf("valid %ld components %d validcomps %d mixed %d largest valid comp %ld badflips %ld badflips valid-valid %ld\n",nv,nc,ncv,mixed,maxc,nbad,nbadvv);
 // list valid comp sizes
 int cnt=0;for(int t=0;t<nt&&cnt<40;t++)if(par[t]==t&&vs[t]){printf("%d ",vs[t]);cnt++;}puts("");
}
