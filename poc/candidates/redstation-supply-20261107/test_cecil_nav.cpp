// GPL-2.0-only. Synthetic fixtures contain no distributed map coordinates.
#include "cecil_nav_data.h"
#include <algorithm>
#include <cmath>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <fstream>
#include <iterator>
#include <new>

static bool count_allocations=false;
static size_t allocations=0;
void* operator new(std::size_t n) {
  if(count_allocations)++allocations;
  void* p=std::malloc(n?n:1);if(!p)throw std::bad_alloc();return p;
}
void operator delete(void* p) noexcept {std::free(p);}
void operator delete(void* p,std::size_t) noexcept {std::free(p);}
using namespace botcore;
using Bytes=std::vector<unsigned char>;
static int failures=0,checks=0;
static void check(bool yes,const char* label) {
  ++checks;if(!yes){++failures;std::fprintf(stderr,"FAIL %s\n",label);}
}
static void word(Bytes& b,uint32_t x) {for(int i=0;i<4;++i)b.push_back((unsigned char)(x>>(8*i)));}
static void real(Bytes& b,float x) {uint32_t u;std::memcpy(&u,&x,4);word(b,u);}
static void tag(Bytes& b,const char* t) {b.insert(b.end(),t,t+4);}
static void put(Bytes& b,size_t at,uint32_t x) {for(int i=0;i<4;++i)b[at+i]=(unsigned char)(x>>(8*i));}
// Independent inverse checks EVERY parsed field, including float bit patterns.
static Bytes encode(const CecilNavGraph& g) {
  Bytes b;tag(b,"BNMV");word(b,g.version);word(b,g.generated);word(b,g.next_point_id);word(b,(uint32_t)g.points.size());
  for(const auto& p:g.points) {
    tag(b,"BPPH");word(b,p.id);real(b,p.x);real(b,p.y);real(b,p.z);real(b,p.radius);word(b,p.flags);
    word(b,p.important_entity);word(b,p.next_slot);word(b,p.lock_entity);
    if(p.lock_entity!=-1)for(float f:p.lock_origin)real(b,f);
    word(b,(uint32_t)p.links.size());for(int n:p.links)word(b,n);
    b.push_back(p.polygon_kind?1:0);
    if(p.polygon_kind) {
      tag(b,p.polygon_kind==1?"PPO1":"PPO2");
      if(p.polygon_kind==2)word(b,(uint32_t)p.polygon.size());
      for(const auto& v:p.polygon)for(float f:v)real(b,f);
    }
  }
  return b;
}
static CecilNavGraph chain(int n) {
  CecilNavGraph g;g.version=6;g.next_point_id=n*2+1;g.points.resize(n);
  for(int i=0;i<n;++i){auto& p=g.points[i];p.id=i*2;p.x=(float)i;if(i+1<n)p.links.push_back(i+1);}
  return g;
}
static void loader_tests() {
  auto source=chain(2);auto& p=source.points[0];
  p.id=1;p.flags=127;p.radius=2.5f;p.important_entity=5;p.next_slot=1;p.lock_entity=9;
  for(int i=0;i<6;++i)p.lock_origin[i]=(float)i-2.5f;
  p.polygon_kind=2;p.polygon={{{1,2,3}},{{4,5,6}},{{7,8,9}},{{-1,-2,-3}}};
  source.points[1].polygon_kind=1;source.points[1].polygon={{{1,2,3}},{{4,5,6}},{{7,8,9}}};
  const Bytes raw=encode(source);CecilNavGraph g;std::string error;
  const bool loaded=g.Load(raw.data(),raw.size(),&error);
  check(loaded,"valid v6 with lock, ID holes, flags and PPO1/PPO2 loads");
  if(loaded)check(encode(g)==raw,"all metadata survives exact byte reconstruction");
  check(!g.Load(nullptr,raw.size(),&error)&&g.points.empty(),"null input clears stale graph");
  check(!g.Load(raw.data(),10*1024*1024+1,&error),"input cap before reading memory");
  for(size_t n=0;n<raw.size();++n)check(!g.Load(raw.data(),n,&error),"every truncation rejected");
  Bytes bad=raw;bad.push_back(0);check(!g.Load(bad.data(),bad.size(),&error),"trailing bytes rejected");
  const std::pair<size_t,uint32_t> mutations[]={
    {0,0},{4,5},{8,2},{12,1},{16,0},{16,4097},{20,0},{24,0xffffffffu},
    {28,0x7fc00000u},{32,0x7f800000u},{40,0},{44,128},{48,0xfffffffeu},
    {52,2},{56,0xfffffffeu},{60,0x7fc00000u},{84,3},{88,2},
    {92,2},{93,0},{97,2},{97,1025}};
  for(auto m:mutations){bad=raw;put(bad,m.first,m.second);check(!g.Load(bad.data(),bad.size(),&error),"invalid header/point/link rejected");}
  source=chain(2);source.points[1].id=source.points[0].id;bad=encode(source);
  check(!g.Load(bad.data(),bad.size(),&error),"duplicate stable IDs rejected");
  source=chain(2);source.points[0].links={1,1};bad=encode(source);
  check(!g.Load(bad.data(),bad.size(),&error),"duplicate directed links rejected");
  source.points[0].links={0};bad=encode(source);
  check(!g.Load(bad.data(),bad.size(),&error),"self link rejected");
  source=chain(335);bad=encode(source);
  check(g.Load(bad.data(),bad.size(),&error)&&g.points.size()==335,"full maps above 256 not truncated");
}
static void search_tests() {
  auto g=chain(4);g.points[0].links={1,3};g.points[1].x=100;g.points[1].flags=CECIL_TELEPORT;
  g.points[1].links={2};g.points[2].x=101;g.points[2].links={3};g.points[3].x=200;
  CecilNavSearch a,b;a.Prepare(g.points.size());b.Prepare(g.points.size());
  check(a.Run(g,0),"directed search runs");
  check(a.NextHop(3)==1&&std::fabs(a.Distance(3)-199)<1e-9,"zero-cost outgoing teleport beats direct edge");
  check(a.NextHop(0)==0&&a.Distance(0)==0,"valid self path");
  check(b.Run(g,3)&&b.NextHop(0)==-1&&!std::isfinite(b.Distance(0)),"reverse one-way route unreachable");
  check(a.NextHop(3)==1,"independent bot context retains its route");
  unsigned char blocked[4]={0,1,0,0};
  check(a.Run(g,0,blocked,4)&&a.NextHop(3)==3&&a.Distance(3)==200,"lock removes route only from search");
  check(g.points[0].links.size()==2,"lock preserves original directed graph");
  blocked[0]=1;blocked[1]=0;
  check(a.Run(g,0,blocked,4)&&a.NextHop(3)==1,"locked origin may exit as in Cecil");
  check(!a.Run(g,-1)&&a.NextHop(0)==-1,"invalid origin clears previous path");
  check(!a.Run(g,4)&&a.NextHop(4)==-1,"invalid self index not accepted");
  check(!a.Run(g,0,blocked,3),"mismatched lock snapshot rejected");
  check(!a.Run(g,0,nullptr,4),"missing lock buffer rejected");
  a.Prepare(3);check(!a.Run(g,0),"unprepared capacity fails without timer allocation");
  g=chain(335);a.Prepare(335);check(a.Run(g,0)&&a.NextHop(334)==1&&a.Distance(334)==334,"path longer than 256 completes");
  allocations=0;count_allocations=true;const bool ok=a.Run(g,0);const int hop=a.NextHop(334);count_allocations=false;
  check(ok&&hop==1&&allocations==0,"Run and NextHop allocate nothing");
  g.points[0].links.push_back(9999);check(!a.Run(g,0),"invalid in-memory adjacency safely rejected");
}
// Floyd-Warshall is an independent all-pairs oracle, not the production search.
static void all_pairs(const CecilNavGraph& g,int lock) {
  const size_t n=g.points.size();const double inf=std::numeric_limits<double>::infinity();
  std::vector<double> expected(n*n,inf);std::vector<unsigned char> blocked(n,0);
  if(lock>=0)blocked[lock]=1;
  for(size_t i=0;i<n;++i){expected[i*n+i]=0;
    for(int j:g.points[i].links)if(!blocked[j]) {
      const auto& p=g.points[i];const auto& q=g.points[j];
      expected[i*n+j]=(p.flags&CECIL_TELEPORT)?0:std::hypot(std::hypot(double(p.x)-q.x,double(p.y)-q.y),double(p.z)-q.z);
    }
  }
  for(size_t k=0;k<n;++k)for(size_t i=0;i<n;++i)for(size_t j=0;j<n;++j)
    expected[i*n+j]=std::min(expected[i*n+j],expected[i*n+k]+expected[k*n+j]);
  CecilNavSearch search;search.Prepare(n);size_t reachable=0;
  for(size_t i=0;i<n;++i) {
    check(search.Run(g,(int)i,blocked.data(),n),"all-pairs search");
    for(size_t j=0;j<n;++j) {
      const double want=expected[i*n+j],got=search.Distance((int)j);const int hop=search.NextHop((int)j);
      const bool reach=std::isfinite(want);reachable+=reach;
      check(reach==std::isfinite(got)&&(!reach||std::fabs(got-want)<=1e-7*(1+want)),"all-pairs reachability and optimal cost");
      if(reach&&i!=j&&hop>=0){const auto& p=g.points[i];const auto& q=g.points[hop];
        const double edge=(p.flags&CECIL_TELEPORT)?0:std::hypot(std::hypot(double(p.x)-q.x,double(p.y)-q.y),double(p.z)-q.z);
        check(std::fabs(edge+expected[(size_t)hop*n+j]-want)<=1e-7*(1+want),"next hop belongs to an optimal full path");}
      check(reach?(hop>=0&&(i==j||std::find(g.points[i].links.begin(),g.points[i].links.end(),hop)!=g.points[i].links.end())):hop==-1,"next hop is original outgoing arc or valid self");
    }
  }
  std::printf("ALL_PAIRS nodes=%zu lock=%d pairs=%zu reachable_including_self=%zu\n",n,lock,n*n,reachable);
}
template<class T>auto avoiding(const T& s,const CecilNavGraph& g,int goal,int from,int to,const unsigned char* b,size_t n,int)
 ->decltype(s.PathAvoidsEdge(g,goal,from,to,b,n)){return s.PathAvoidsEdge(g,goal,from,to,b,n);}
template<class T>bool avoiding(const T&,const CecilNavGraph&,int,int,int,const unsigned char*,size_t,long){return false;}
template<class T>auto raw_path(const T& g,const int* p,size_t n,int start,int goal,int from,int to,int)
 ->decltype(CecilNavPathAvoidsEdge(g,p,n,start,goal,from,to,nullptr,0)){
 return CecilNavPathAvoidsEdge(g,p,n,start,goal,from,to,nullptr,0);
}
template<class T>bool raw_path(const T&,const int*,size_t,int,int,int,int,long){return false;}
static void bounded_path_tests(){
 auto g=chain(5);g.points[0].links={1};g.points[1].links={4};g.points[2].links={3};g.points[3].links={4};
 CecilNavSearch s;s.Prepare(5);s.Run(g,2);unsigned char b[5]={};
 count_allocations=true;allocations=0;const bool bypass=avoiding(s,g,4,0,1,b,5,0);count_allocations=false;
 check(bypass&&allocations==0,"prepared real parent suffix reaches actual start and avoids failed edge without allocation");
 s.Run(g,0);check(!avoiding(s,g,4,0,1,b,5,0),"different candidate whose parent suffix reuses failed edge is rejected");
 s.Run(g,2);b[3]=1;check(!avoiding(s,g,4,0,1,b,5,0),"current intermediate lock invalidates cached suffix");b[3]=0;
 check(!avoiding(s,g,0,0,1,b,5,0)&&!avoiding(s,g,6,0,1,b,5,0)&&!avoiding(s,g,4,0,1,b,4,0),
  "unreachable out of range or inconsistent blocked snapshot is not a valid bypass");
 g.points[3].links.clear();check(!avoiding(s,g,4,0,1,b,5,0),"cached parent must still be an actual original directed edge");
 auto malformed=chain(3);malformed.points[1].links={2};malformed.points[2].links={1};
 const int cycle[3]={-1,2,1},oob[3]={-1,99,1},noStart[3]={-1,-1,1};
 check(!raw_path(malformed,cycle,3,0,2,0,1,0)&&!raw_path(malformed,oob,3,0,2,0,1,0)&&
  !raw_path(malformed,noStart,3,0,2,0,1,0),"cycle OOB and disconnected parent chains cannot masquerade as failed-edge absence");
}
int main(int argc,char** argv) {
  loader_tests();if(argc==2&&std::strcmp(argv[1],"--loader")==0)return failures?1:0;
  search_tests();bounded_path_tests();
  for(int i=1;i<argc;++i) {
    std::ifstream f(argv[i],std::ios::binary);Bytes raw((std::istreambuf_iterator<char>(f)),{});
    CecilNavGraph g;std::string error;const bool ok=g.Load(raw.data(),raw.size(),&error);
    check(ok,"original NAV loads");if(!ok){std::fprintf(stderr,"%s: %s\n",argv[i],error.c_str());continue;}
    check(encode(g)==raw,"original NAV roundtrip byte-identical");
    size_t arcs=0;for(const auto& p:g.points)arcs+=p.links.size();
    std::printf("NAV %s nodes=%zu arcs=%zu roundtrip=%s\n",argv[i],g.points.size(),arcs,encode(g)==raw?"IDENTICAL":"FAIL");
    if(g.points.size()==193){check(arcs==879,"Red Station retains all 879 directed arcs");all_pairs(g,-1);all_pairs(g,2);}
  }
  std::printf("checks=%d failures=%d\n",checks,failures);return failures?1:0;
}
