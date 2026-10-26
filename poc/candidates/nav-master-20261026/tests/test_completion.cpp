#include <cstdio>
#include <limits>
#include "nav_item_controller.h"
namespace {
int fails=0, checks=0;
void Check(bool ok,const char* msg){++checks;if(!ok){++fails;std::printf("FAIL %s\n",msg);}}
void Rules(){
 itemai::ItemWorld w; w.self.health=101; w.self.armor=150;
 Check(itemai::ValidateWorld(w)==itemai::ValidationError::kOk,"legal overmax health and armor validate");
 itemai::GrantWeapon(w.self,1); itemai::GrantWeapon(w.self,2);
 Check(itemai::AssessSelf(w,0).best_weapon==2,"zero-reserve Colt remains usable");
 itemai::SetAmmo(w.self,5,1);
 Check(!itemai::WeaponHasAmmo(w.self.ammo,5),"double shotgun requires two shared shells");
 Check(itemai::WeaponHasAmmo(w.self.ammo,4),"single shotgun uses same shell pool");
 itemai::SetAmmo(w.self,6,25);
 Check(itemai::WeaponHasAmmo(w.self.ammo,7),"minigun reads Tommygun shared bullets");
 itemai::SetAmmo(w.self,7,0);
 Check(!itemai::WeaponHasAmmo(w.self.ammo,6),"shared pool depletion affects Tommygun");
}
void InfiniteAndPickupLimits(){
 itemai::ItemWorld w;w.self.health=101;w.self.armor=150;w.self.infinite_ammo=true;
 itemai::GrantWeapon(w.self,7);itemai::ItemSnapshot it;it.id=10;it.kind=itemai::ItemKind::kAmmo;it.weapon_index=6;it.amount=20;it.pos={8,0,0};
 w.items=&it;w.count=1;itemai::ItemProfile prof;auto c=itemai::MakeContext(prof,w,0);
 Check(itemai::AssessSelf(w,0).best_weapon==7,"infinite ammo keeps ranged weapon usable at zero reserve");
 Check(!itemai::AssessSelf(w,0).ammunition_starved,"infinite ammo is not starvation");
 Check(itemai::EvaluateItem(c,w,0).terms.need==0,"infinite ammo forbids ammo resupply need");
 it.kind=itemai::ItemKind::kHealth;it.weapon_index=0;it.value=100;it.pickup_limit=200;
 Check(itemai::EvaluateItem(c,w,0).terms.need>0,"explicit super-health cap preserves overtop need");
 it.pickup_limit=0;
 Check(itemai::EvaluateItem(c,w,0).terms.need==0,"normal health does not chase overtop health");
 it.kind=itemai::ItemKind::kArmor;it.pickup_limit=200;
 Check(itemai::EvaluateItem(c,w,0).terms.need>0,"explicit super-armor cap preserves overtop need");
}
void FloorProgress(){
 navlab::NavGraph g;g.AddNode(0,0,0);g.AddNode(10,0,0);g.AddNode(10,8,0);g.AddNode(20,4,0);
 g.Link(0,1);g.Link(1,3);g.Link(3,2);
 Check(g.NearestNode3D(10,8,0,20)==2,"upper bot anchors to upper floor");
 Check(g.NearestNode3D(10,20,0,20)==-1,"height mismatch cannot snap through ceiling");
 Check(g.NearestNode3D(10,std::numeric_limits<double>::quiet_NaN(),0,20)==-1,"NaN anchor rejected");
 navbridge::NavGraphSink sink;navbridge::BridgeBudgetConfig cfg;cfg.route_variance=0;
 sink.Configure(cfg,navlab::NavPersonality(),7);navbridge::ConstrainedNavSearch search;
 navbridge::LocalBlockedEdgeTable blocked;navbridge::TickExpansionBudget budget(128);
 sink.BindTickContext(&g,1,0,{0,0,0},-90,nullptr,&search,&budget,&blocked);
 itemai::NavGoal goal;goal.goal_id=3;goal.pos={10,8,0};goal.issued_tick=0;goal.expires_tick=100;
 Check(sink.Submit(goal)==itemai::NavStatus::kAccepted,"stair route accepted");
 sink.StepGoalMove(true,false,5);
 sink.BindTickContext(&g,1,1,{10,0,0},-90,nullptr,&search,&budget,&blocked);
 auto move=sink.StepGoalMove(true,false,5);
 Check(move.next_node==3,"ground-floor bot follows stair connector before upper goal");
 itemai::NavFeedback feedback;
 Check(sink.Poll(3,&feedback)==itemai::NavStatus::kInProgress,"standing under item is not arrival");
 sink.BindTickContext(&g,1,2,{20,4,0},90,nullptr,&search,&budget,&blocked);
 move=sink.StepGoalMove(true,false,5);
 Check(move.next_node==2,"upper waypoint not skipped by planar projection");
 sink.BindTickContext(&g,1,3,{10,8,0},0,nullptr,&search,&budget,&blocked);
 Check(sink.Poll(3,&feedback)==itemai::NavStatus::kArrived,"actual upper-floor arrival succeeds");
}
void GoalFloorChange(){
 navlab::NavGraph g;g.AddNode(0,0,0);g.AddNode(10,0,0);g.AddNode(10,8,0);g.Link(0,1);
 navbridge::NavGraphSink sink;navbridge::BridgeBudgetConfig cfg;cfg.route_variance=0;
 sink.Configure(cfg,navlab::NavPersonality(),7);navbridge::ConstrainedNavSearch search;
 navbridge::LocalBlockedEdgeTable blocked;navbridge::TickExpansionBudget budget(128);
 sink.BindTickContext(&g,1,0,{0,0,0},-90,nullptr,&search,&budget,&blocked);
 itemai::NavGoal goal;goal.goal_id=3;goal.pos={10,0,0};goal.expires_tick=100;
 Check(sink.Submit(goal)==itemai::NavStatus::kAccepted,"ground item accepted");
 goal.pos.y=8;
 Check(sink.Submit(goal)==itemai::NavStatus::kUnreachable,"same item id changing floor requires reanchor");
}
void Enrichment(){
 navlab::NavGraph g; g.AddNode(0,0,0);g.AddNode(10,0,0);g.AddNode(10,8,0);
 navbridge::BridgeBudgetConfig cfg;cfg.max_cost_probes_per_tick=1;
 navbridge::BridgeProfileBundle prof{};navbridge::BuildBridgeProfile(4,1,7,0,"Test",&prof,0);
 itemai::ItemWorld w;w.self.health=20;w.combat.tick=1;
 itemai::ItemSnapshot items[2];for(int i=0;i<2;++i){items[i].id=i;items[i].kind=itemai::ItemKind::kHealth;items[i].value=100;items[i].pos={10,0,0};}
 items[0].pos.y=8;
 w.items=items;w.count=1;
 navbridge::WorldPathEnricher en;navbridge::ConstrainedNavSearch search;
 navbridge::LocalBlockedEdgeTable blocked;navbridge::TickExpansionBudget budget(64);
 itemai::ItemSnapshot adapted[64];itemai::ItemWorld out;navbridge::TrueItemTable table;
 g.Link(0,1);
 auto stats=en.Enrich(g,1,cfg,7,prof.item_profile,-1,w,search,blocked,budget,adapted,&out,&table);
 Check(!out.items[0].reachable,"disconnected upper-floor item is unreachable");
 Check(table.At(0).anchor_node==2,"item anchors to its actual floor");
 Check(stats.probes_executed==1,"floor separation requires actual path probe");
 // First probe is a reachable cheap item; second item has no verified route.
 en.Reset();w.count=2;items[0].pos={10,0,0};items[1].pos={10,8,0};budget.Reset(64);
 en.Enrich(g,1,cfg,7,prof.item_profile,-1,w,search,blocked,budget,adapted,&out,&table);
 Check(out.items[0].reachable,"verified reachable item remains selectable");
 Check(!out.items[1].reachable && !table.At(1).path_verified,"unprobed item cannot win by air distance");
 w.combat.tick=2;budget.Reset(64);
 en.Enrich(g,1,cfg,7,prof.item_profile,-1,w,search,blocked,budget,adapted,&out,&table);
 Check(table.At(1).path_verified && !out.items[1].reachable,"next tick probes pending item instead of starving ninth item");
 budget.Reset(0);en.Reset();
 en.Enrich(g,1,cfg,7,prof.item_profile,-1,w,search,blocked,budget,adapted,&out,&table);
 Check(!out.items[0].reachable && !out.items[1].reachable,"zero probe budget never asserts a path");
}
}
int main(){Rules();InfiniteAndPickupLimits();FloorProgress();GoalFloorChange();Enrichment();std::printf("Completion: %d checks, %d failures\n",checks,fails);return fails?1:0;}
