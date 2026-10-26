#include <chrono>
#include <ctime>
#include <cstdio>
#include <cstdlib>
#include <new>
#include "nav_item_controller.h"
namespace { bool tracking=false; unsigned long allocations=0; }
void* operator new(std::size_t n) { if(tracking) ++allocations; if(void* p=std::malloc(n)) return p; throw std::bad_alloc(); }
void* operator new[](std::size_t n) { return ::operator new(n); }
void operator delete(void* p) noexcept { std::free(p); }
void operator delete[](void* p) noexcept { std::free(p); }
void operator delete(void* p,std::size_t) noexcept { std::free(p); }
void operator delete[](void* p,std::size_t) noexcept { std::free(p); }
namespace {
c2nav::Controller agents[16]; navlab::NavGraph graph;
uint64_t digest=1469598103934665603ull;
uint64_t Run(int bots,int ticks,int* maximum) {
 c2nav::Options o; o.enabled=o.item_goals=o.patrol=true; o.budget.max_expansions_per_tick=96;
 for(int b=0;b<bots;++b) { navbridge::BridgeProfileBundle p{}; navbridge::BuildBridgeProfile(4,b%6,0x8765,b,"Bench",&p,0); agents[b].Configure(p,o); }
 itemai::ItemSnapshot items[32];
 for(int i=0;i<32;++i) { items[i].id=i; items[i].kind=static_cast<itemai::ItemKind>(1+i%4); items[i].pos={double(4+(i%10)*4),0,double((i/10)*4)}; items[i].weapon_index=(i%4>=2)?6:0; items[i].value=50; items[i].amount=50; items[i].visible=true; }
 c2nav::Frame f; f.contract.map_sha256="aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa";
 f.contract.waypoints_sha256="bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb";
 f.contract.world_instance=f.contract.graph_epoch=1; f.contract.offline_fixture=true;
 f.contract.anchors_3d_verified=f.contract.item_entities_verified=true;
 f.world.alive=true; f.world.health=f.items.self.health=30; f.world.pose.yaw_deg=-90;
 f.items.self.owned_weapons=1u|(1u<<5); f.items.items=items; f.items.count=32;
 tracking=true; uint64_t hash=1469598103934665603ull;
 for(int t=1;t<=ticks;++t) { f.world.tick=f.items.combat.tick=f.contract.snapshot_tick=t;
  for(int b=0;b<bots;++b) {
   auto out=agents[b].Step(graph,f);
   if(out.status!=c2nav::Status::kReady || out.expansions>96) std::abort();
   if(out.expansions>*maximum) *maximum=out.expansions;
   hash^=static_cast<uint64_t>(out.item.goal_id+2)+static_cast<uint64_t>(out.expansions)*104729ull;
   hash*=1099511628211ull;
  }
 }
 tracking=false; return hash;
}
}
int main() {
 navlab::maps::MakeGrid(graph,32,32,4);
 std::printf("C2 scope: synthetic 1024-node graph, 32 items, 1000 ticks, 96 expansions/bot/tick\n");
 std::printf("sizeof_controller=%zu graph_bytes=%zu static_16_agent_bytes=%zu\n",sizeof(c2nav::Controller),sizeof(graph),sizeof(agents));
 const int counts[]={1,4,8,16};
 for(int bots:counts) {
  int maximum=0; allocations=0; auto wall=std::chrono::steady_clock::now(); auto cpu=std::clock();
  const auto h=Run(bots,1000,&maximum);
  const double cpu_ms=1000.0*(std::clock()-cpu)/CLOCKS_PER_SEC;
  const double wall_ms=std::chrono::duration<double,std::milli>(std::chrono::steady_clock::now()-wall).count();
  int replay_max=0; const auto replay=Run(bots,1000,&replay_max);
  std::printf("bots=%d cpu_ms=%.3f wall_ms=%.3f cpu_us_per_bot_tick=%.3f max_exp=%d allocations=%lu digest=%016llx deterministic=%d\n",
    bots,cpu_ms,wall_ms,cpu_ms/bots,maximum,allocations,static_cast<unsigned long long>(h),h==replay);
  if(allocations || h!=replay) return 1;
  digest^=h;
 }
 return digest==0?1:0;
}
