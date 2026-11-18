// Independent-set bound. For a set B of bad blocks, flips at blocks of B join a valid tiling to an invalid one
// (a bad flip changes the domino multiset), so the set of solutions is an independent set in the graph
// H_B = (tilings, flips at blocks in B). Hence #solutions <= n - nu(H_B) =: U(B), nu = maximum matching.
// The flip graph is bipartite (2-coloured by BFS here). U is monotone decreasing in B.
// mode enum thr : list all B (any size) with U(B) > thr, by lexicographic extension (D is down-closed).
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#define MAXT 1300000
typedef struct{uint64_t h,v;} TL;
static TL T[MAXT];static int nt=0;
static void en(int i,uint64_t occ,uint64_t h,uint64_t v){while(i<56&&(occ>>i&1))i++;if(i==56){T[nt].h=h;T[nt].v=v;nt++;return;}
 if((i&7)<7&&!(occ>>(i+1)&1))en(i+2,occ|(3ull<<i),h|(1ull<<i),v);
 if(i<48)en(i+1,occ|(1ull<<i)|(1ull<<(i+8)),h,v|(1ull<<i));}
static int cmp(const void*a,const void*b){const TL*x=a,*y=b;if(x->h!=y->h)return x->h<y->h?-1:1;if(x->v!=y->v)return x->v<y->v?-1:1;return 0;}
static int find_t(uint64_t h,uint64_t v){int lo=0,hi=nt-1;while(lo<=hi){int m=(lo+hi)/2;if(T[m].h==h&&T[m].v==v)return m;if(T[m].h<h||(T[m].h==h&&T[m].v<v))lo=m+1;else hi=m-1;}return -1;}
static int *EU,*EV,eoff[43];static signed char col[MAXT];
// adjacency for HK built per B: CSR from left vertices (col 0)
static int *adjoff,*adj,*mateL,*mateR,*dist,*q;
static int hk_bfs(int nL,int*L){int qh=0,qt=0,found=0;for(int k=0;k<nL;k++){int u=L[k];if(mateL[u]<0){dist[u]=0;q[qt++]=u;}else dist[u]=-1;}
 while(qh<qt){int u=q[qh++];for(int e=adjoff[u];e<adjoff[u+1];e++){int w=adj[e];int m=mateR[w];if(m<0)found=1;else if(dist[m]<0){dist[m]=dist[u]+1;q[qt++]=m;}}}return found;}
static int hk_dfs(int u){for(int e=adjoff[u];e<adjoff[u+1];e++){int w=adj[e];int m=mateR[w];if(m<0||(dist[m]==dist[u]+1&&hk_dfs(m))){mateL[u]=w;mateR[w]=u;return 1;}}dist[u]=-1;return 0;}
static int *Lidx;
static long nu(uint64_t B){ // max matching of flips at blocks in B
 // build CSR over all tilings (left = col 0)
 static int *deg=0;if(!deg)deg=malloc(sizeof(int)*(nt+1));
 memset(deg,0,sizeof(int)*(nt+1));
 for(int b=0;b<42;b++)if(B>>b&1)for(int e=eoff[b];e<eoff[b+1];e++){int u=EU[e],w=EV[e];if(col[u])deg[w+1]++;else deg[u+1]++;}
 adjoff[0]=0;for(int i=0;i<nt;i++)adjoff[i+1]=adjoff[i]+deg[i+1];
 memset(deg,0,sizeof(int)*(nt+1));
 for(int b=0;b<42;b++)if(B>>b&1)for(int e=eoff[b];e<eoff[b+1];e++){int u=EU[e],w=EV[e];if(col[u]){int t=u;u=w;w=t;}adj[adjoff[u]+deg[u]++]=w;}
 int nL=0;for(int i=0;i<nt;i++){mateL[i]=-1;mateR[i]=-1;if(!col[i]&&adjoff[i+1]>adjoff[i])Lidx[nL++]=i;}
 // greedy init
 long m=0;for(int k=0;k<nL;k++){int u=Lidx[k];for(int e=adjoff[u];e<adjoff[u+1];e++)if(mateR[adj[e]]<0){mateL[u]=adj[e];mateR[adj[e]]=u;m++;break;}}
 while(hk_bfs(nL,Lidx)){for(int k=0;k<nL;k++){int u=Lidx[k];if(mateL[u]<0&&hk_dfs(u))m++;}}
 return m;}
int main(int argc,char**argv){
 if(!(argc>=3&&(!strcmp(argv[1],"one")||!strcmp(argv[1],"enum")))&&!(argc>=2&&!strcmp(argv[1],"list"))){fprintf(stderr,"usage: %s one SET | list (sets on stdin) | enum THR\n",argv[0]);return 2;}
 en(0,0,0,0);qsort(T,nt,sizeof(TL),cmp);
 int cap=30000000;int*U=malloc(4*cap),*V=malloc(4*cap),*Bk=malloc(4*cap);int m=0;
 for(int t=0;t<nt;t++)for(int r=0;r<6;r++)for(int c=0;c<7;c++){int i=r*8+c;uint64_t h=T[t].h,v=T[t].v;
   if((h>>i&1)&&(h>>(i+8)&1)){uint64_t h2=h&~((1ull<<i)|(1ull<<(i+8))),v2=v|(1ull<<i)|(1ull<<(i+1));U[m]=t;V[m]=find_t(h2,v2);Bk[m]=r*7+c;m++;}}
 memset(eoff,0,sizeof eoff);for(int e=0;e<m;e++)eoff[Bk[e]+1]++;for(int b=0;b<42;b++)eoff[b+1]+=eoff[b];
 EU=malloc(4*m);EV=malloc(4*m);int pos[42]={0};for(int e=0;e<m;e++){int b=Bk[e];int k=eoff[b]+pos[b]++;EU[k]=U[e];EV[k]=V[e];}
 // 2-colour via BFS over all flips
 {int*ao=calloc(nt+1,4),*aj=malloc(8*m),*dg=calloc(nt+1,4);for(int e=0;e<m;e++){dg[EU[e]+1]++;dg[EV[e]+1]++;}for(int i=0;i<nt;i++)ao[i+1]=ao[i]+dg[i+1];memset(dg,0,4*(nt+1));
  for(int e=0;e<m;e++){aj[ao[EU[e]]+dg[EU[e]]++]=EV[e];aj[ao[EV[e]]+dg[EV[e]]++]=EU[e];}
  memset(col,-1,nt);int*qq=malloc(4*nt);int qh=0,qt=0;col[0]=0;qq[qt++]=0;int bad=0;
  while(qh<qt){int u=qq[qh++];for(int k=ao[u];k<ao[u+1];k++){int w=aj[k];if(col[w]<0){col[w]=1-col[u];qq[qt++]=w;}else if(col[w]==col[u])bad=1;}}
  fprintf(stderr,"tilings %d flips %d reached %d bipartite %s\n",nt,m,qt,bad?"NO":"yes");free(ao);free(aj);free(dg);free(qq);}
 adjoff=malloc(sizeof(int)*(nt+1));adj=malloc(4*m);mateL=malloc(4*nt);mateR=malloc(4*nt);dist=malloc(4*nt);q=malloc(4*nt);Lidx=malloc(4*nt);
 if(!strcmp(argv[1],"one")){uint64_t B=0;for(char*s=strtok(argv[2],",");s;s=strtok(0,","))if(*s>='0'&&*s<='9')B|=1ull<<atoi(s);long v=nu(B);printf("nu %ld U %ld\n",v,nt-v);return 0;}

 if(!strcmp(argv[1],"list")){char line[512];while(fgets(line,sizeof line,stdin)){uint64_t B=0;char bs[256];if(sscanf(line,"%255s",bs)!=1)continue;char tmp[256];strcpy(tmp,bs);
   for(char*t=strtok(tmp,",");t;t=strtok(0,","))if(*t>='0'&&*t<='9')B|=1ull<<atoi(t);
   long v=nu(B);printf("%s U %ld\n",bs,nt-v);fflush(stdout);}return 0;}
 if(!strcmp(argv[1],"enum")){long thr=atol(argv[2]);
   // BFS over levels: arrays of B masks
   uint64_t*cur=malloc(8*4000000),*nxt=malloc(8*4000000);long nc=1,nn;cur[0]=0;
   for(int k=0;k<42&&nc;k++){nn=0;
     for(long a=0;a<nc;a++){uint64_t B=cur[a];int mx=-1;for(int b=0;b<42;b++)if(B>>b&1)mx=b;
       if(k==0){long v=nu(B);printf("D 0 - U %ld\n",nt-v);}
       for(int b=mx+1;b<42;b++){uint64_t B2=B|(1ull<<b);long v=nu(B2);if(nt-v>thr){nxt[nn++]=B2;printf("D %d ",k+1);int f=1;for(int x=0;x<42;x++)if(B2>>x&1){printf(f?"%d":",%d",x);f=0;}printf(" U %ld\n",nt-v);fflush(stdout);}}}
     fprintf(stderr,"level %d: %ld sets with U>thr\n",k+1,nn);uint64_t*t=cur;cur=nxt;nxt=t;nc=nn;}
   return 0;}
}
