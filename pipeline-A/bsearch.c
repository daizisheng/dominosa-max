// For sets B of "allowed bad" 2x2 blocks, compute the components of the domino-tiling flip graph of
// the 7x8 board when flips at blocks in B are removed. Block id = r*7+c (r<6,c<7), top-left cell r*8+c.
// modes: bsearch one b1,b2,...   -> top component sizes + representative tilings
//        bsearch enum k thr part nparts -> all canonical B with |B|=k whose largest comp > thr
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
static int *EU,*EV,*eoff; // edges grouped by block
static int par[MAXT],sz[MAXT];
static inline int F(int x){while(par[x]!=x){par[x]=par[par[x]];x=par[x];}return x;}
static int comps(uint64_t B,int*best,int*rep){for(int i=0;i<nt;i++){par[i]=i;sz[i]=1;}
 for(int b=0;b<42;b++){if(B>>b&1)continue;for(int e=eoff[b];e<eoff[b+1];e++){int x=F(EU[e]),y=F(EV[e]);if(x!=y){if(sz[x]<sz[y]){int t=x;x=y;y=t;}par[y]=x;sz[x]+=sz[y];}}}
 int m=0,r=0;for(int i=0;i<nt;i++)if(par[i]==i&&sz[i]>m){m=sz[i];r=i;}*best=m;*rep=r;return m;}
static int symb(int b,int s){int r=b/7,c=b%7;if(s&1)r=5-r;if(s&2)c=6-c;return r*7+c;}
static uint64_t symB(uint64_t B,int s){uint64_t o=0;for(int b=0;b<42;b++)if(B>>b&1)o|=1ull<<symb(b,s);return o;}
static void prtile(int t){printf("H%016llx V%016llx",(unsigned long long)T[t].h,(unsigned long long)T[t].v);}
int main(int argc,char**argv){
 if(!(argc>=3&&(!strcmp(argv[1],"one")||!strcmp(argv[1],"list")||!strcmp(argv[1],"listall")))&&!(argc>=6&&!strcmp(argv[1],"enum"))){
   fprintf(stderr,"usage: %s one SET [K] | list THR | listall MIN | enum k THR part nparts   (sets on stdin for list, listall)\n",argv[0]);return 2;}
 en(0,0,0,0);qsort(T,nt,sizeof(TL),cmp);
 int cap=30000000;int*U=malloc(4*cap),*V=malloc(4*cap),*Bk=malloc(4*cap);int m=0;
 for(int t=0;t<nt;t++)for(int r=0;r<6;r++)for(int c=0;c<7;c++){int i=r*8+c;uint64_t h=T[t].h,v=T[t].v;
   if((h>>i&1)&&(h>>(i+8)&1)){uint64_t h2=h&~((1ull<<i)|(1ull<<(i+8))),v2=v|(1ull<<i)|(1ull<<(i+1));U[m]=t;V[m]=find_t(h2,v2);Bk[m]=r*7+c;m++;if(m>=cap){fprintf(stderr,"cap\n");exit(1);}}}
 eoff=calloc(43,4);for(int e=0;e<m;e++)eoff[Bk[e]+1]++;for(int b=0;b<42;b++)eoff[b+1]+=eoff[b];
 EU=malloc(4*m);EV=malloc(4*m);int*pos=calloc(42,4);for(int e=0;e<m;e++){int b=Bk[e];int k=eoff[b]+pos[b]++;EU[k]=U[e];EV[k]=V[e];}
 fprintf(stderr,"tilings %d flips %d\n",nt,m);
 if(!strcmp(argv[1],"one")){uint64_t B=0;for(char*s=strtok(argv[2],",");s;s=strtok(0,","))if(*s>='0'&&*s<='9')B|=1ull<<atoi(s);
   int best,rep;comps(B,&best,&rep);
   // list top 10 comps
   int K=argc>3?atoi(argv[3]):10;
   for(int k=0;k<K;k++){int mm=0,rr=-1;for(int i=0;i<nt;i++)if(par[i]==i&&sz[i]>mm){mm=sz[i];rr=i;}if(rr<0)break;printf("comp %d size %d rep ",k,mm);prtile(rr);puts("");sz[rr]=-sz[rr];}
   return 0;}

 if(!strcmp(argv[1],"list")){int thr=atoi(argv[2]);char line[512];
   while(fgets(line,sizeof line,stdin)){uint64_t B=0;char*q=line;while(*q==' '||*q=='B')q++;char*tok=strtok(q,", \n");int k=0;int idx[16];while(tok){if(*tok>='0'&&*tok<='9'){idx[k++]=atoi(tok);B|=1ull<<atoi(tok);}tok=strtok(0,", \n");}
     int best,rep;comps(B,&best,&rep);
     if(best>thr){// print all comps above thr
       for(int i=0;i<nt;i++)if(par[i]==i&&sz[i]>thr){printf("B");if(!k)printf(" -");for(int j=0;j<k;j++)printf("%c%d",j?',':' ',idx[j]);printf(" max %d rep ",sz[i]);prtile(i);puts("");}}
     else {printf("X");if(!k)printf(" -");for(int j=0;j<k;j++)printf("%c%d",j?',':' ',idx[j]);printf(" max %d\n",best);}
     fflush(stdout);}
   printf("END\n");return 0;}

 if(!strcmp(argv[1],"listall")){int minsz=atoi(argv[2]);char line[512];
   static int ord[MAXT];
   while(fgets(line,sizeof line,stdin)){uint64_t B=0;char*q=line;while(*q==' '||*q=='B')q++;char bs[256];sscanf(q,"%255s",bs);char tmp[256];strcpy(tmp,bs);
     for(char*tok=strtok(tmp,",");tok;tok=strtok(0,","))if(*tok>='0'&&*tok<='9')B|=1ull<<atoi(tok);
     int best,rep;comps(B,&best,&rep);int no=0;long rest=0;
     for(int i=0;i<nt;i++)if(par[i]==i){if(sz[i]>=minsz)ord[no++]=i;else rest+=sz[i];}
     // sort ord by size desc (insertion, no is small)
     for(int a=1;a<no;a++){int x=ord[a],b=a-1;while(b>=0&&sz[ord[b]]<sz[x]){ord[b+1]=ord[b];b--;}ord[b+1]=x;}
     printf("S %s %d %ld",bs,no,rest);for(int a=0;a<no;a++){printf(" %d:%llx:%llx",sz[ord[a]],(unsigned long long)T[ord[a]].h,(unsigned long long)T[ord[a]].v);}puts("");fflush(stdout);}
   return 0;}
 if(!strcmp(argv[1],"enum")){int k=atoi(argv[2]);int thr=atoi(argv[3]);int part=atoi(argv[4]),np=atoi(argv[5]);
   int idx[8];for(int i=0;i<k;i++)idx[i]=i;long cnt=0,done=0;
   while(1){uint64_t B=0;for(int i=0;i<k;i++)B|=1ull<<idx[i];
     int canon=1;for(int s=1;s<4;s++)if(symB(B,s)<B){canon=0;break;}
     if(canon){if(cnt%np==part){int best,rep;comps(B,&best,&rep);done++;
         if(best>thr){printf("B");if(!k)printf(" -");for(int i=0;i<k;i++)printf("%c%d",i?',':' ',idx[i]);printf(" max %d rep ",best);prtile(rep);puts("");fflush(stdout);}}
       cnt++;}
     int i=k-1;while(i>=0&&idx[i]==42-k+i)i--;if(i<0)break;idx[i]++;for(int j=i+1;j<k;j++)idx[j]=idx[j-1]+1;}
   fprintf(stderr,"canonical %ld done %ld\n",cnt,done);printf("END\n");}
}
