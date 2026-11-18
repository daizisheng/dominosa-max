// Fast exact Dominosa solution counter (double-six, 7 rows x 8 columns).
// Meet-in-the-middle: cells 0..27 (row-major) are tiled by a DFS "top" part,
// whose dominoes may stick into the 8 frontier cells 28..35; the "bottom" DFS
// tiles the rest. Join on (frontier profile, 28-bit domino-usage mask).
#ifndef COUNT_H
#define COUNT_H
#include <stdint.h>
#include <string.h>
#include <stdlib.h>

#define R 7
#define C 8
#define N 56
#define FULL ((1u<<28)-1)

static int TYPE[7][7];
static void init_types(void){int k=0;for(int a=0;a<7;a++)for(int b=a;b<7;b++){TYPE[a][b]=TYPE[b][a]=k++;}}

#define HBITS 20
#define HSIZE (1u<<HBITS)
typedef struct { uint64_t key; uint64_t cnt; } HE;
typedef struct {
  HE *tab; uint32_t *used; int nused;
  const uint8_t *g; uint64_t total;
  int profcnt[256];
} Ctx;

static Ctx *ctx_new(void){Ctx*c=calloc(1,sizeof(Ctx));c->tab=calloc(HSIZE,sizeof(HE));c->used=malloc(sizeof(uint32_t)*HSIZE);
 for(uint32_t i=0;i<HSIZE;i++)c->tab[i].key=~0ull;
 return c;}

static inline uint32_t hh(uint64_t k){k*=0x9E3779B97F4A7C15ull;return (uint32_t)(k>>(64-HBITS));}
static inline void hadd(Ctx*c,uint64_t k){uint32_t h=hh(k);while(1){HE*e=&c->tab[h];if(e->key==k){e->cnt++;return;}if(e->key==~0ull){e->key=k;e->cnt=1;c->used[c->nused++]=h;return;}h=(h+1)&(HSIZE-1);}}
static inline uint64_t hget(Ctx*c,uint64_t k){uint32_t h=hh(k);while(1){HE*e=&c->tab[h];if(e->key==k)return e->cnt;if(e->key==~0ull)return 0;h=(h+1)&(HSIZE-1);}}

static void top_dfs(Ctx*c,uint64_t occ,int i,uint32_t mask){
  while(i<28 && (occ>>i&1)) i++;
  if(i>=28){int p=(int)((occ>>28)&255);c->profcnt[p]=1;hadd(c,((uint64_t)p<<28)|mask);return;}
  const uint8_t*g=c->g; int col=i&7;
  if(col<7 && !(occ>>(i+1)&1)){uint32_t b=1u<<TYPE[g[i]][g[i+1]]; if(!(mask&b)) top_dfs(c,occ|(3ull<<i),i+2,mask|b);}
  {uint32_t b=1u<<TYPE[g[i]][g[i+8]]; if(!(mask&b)) top_dfs(c,occ|(1ull<<i)|(1ull<<(i+8)),i+1,mask|b);}
}
static void bot_dfs(Ctx*c,uint64_t occ,int i,uint32_t mask,int p){
  while(i<56 && (occ>>i&1)) i++;
  if(i>=56){c->total+=hget(c,((uint64_t)p<<28)|(FULL^mask));return;}
  const uint8_t*g=c->g; int col=i&7;
  if(col<7 && !(occ>>(i+1)&1)){uint32_t b=1u<<TYPE[g[i]][g[i+1]]; if(!(mask&b)) bot_dfs(c,occ|(3ull<<i),i+2,mask|b,p);}
  if(i<48){uint32_t b=1u<<TYPE[g[i]][g[i+8]]; if(!(mask&b)) bot_dfs(c,occ|(1ull<<i)|(1ull<<(i+8)),i+1,mask|b,p);}
}
static uint64_t count_sol(Ctx*c,const uint8_t*g){
  c->g=g; c->total=0; memset(c->profcnt,0,sizeof c->profcnt);
  top_dfs(c,0,0,0);
  for(int p=0;p<256;p++) if(c->profcnt[p]) bot_dfs(c,(uint64_t)p<<28,28,0,p);
  for(int k=0;k<c->nused;k++) c->tab[c->used[k]].key=~0ull;
  c->nused=0;
  return c->total;
}
// parse an array: 7 rows of 8 digits 0..6 separated by '/' (ends at a blank or the end of the line)
static int parse_grid(const char*s,uint8_t*g){int k=0,i=0;for(;s[i]&&s[i]!='\n'&&s[i]!='\r'&&s[i]!=' ';i++){if(i%9==8){if(s[i]!='/')return -1;}else{if(s[i]<'0'||s[i]>'6'||k>=N)return -1;g[k++]=s[i]-'0';}}return (i==62&&k==N)?0:-1;}
#endif
