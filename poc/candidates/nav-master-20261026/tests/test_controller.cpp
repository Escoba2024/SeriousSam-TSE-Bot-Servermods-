#include <cmath>
#include <cstdio>
#include <limits>
#include <initializer_list>
#include "nav_item_controller.h"
namespace {
int failures=0, checks=0;
void Check(bool ok,const char* msg) { ++checks; if(!ok) { ++failures; std::printf("FAIL %s\n",msg); } }
const char* shaA="aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa";
const char* shaB="bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb";
c2nav::Frame Fixture() {
 c2nav::Frame f;
 f.contract.map_sha256=shaA; f.contract.waypoints_sha256=shaB;
 f.contract.world_instance=1; f.contract.graph_epoch=1;
 f.contract.anchors_3d_verified=true; f.contract.item_entities_verified=true;
 f.contract.offline_fixture=true; f.contract.snapshot_tick=1;
 f.world.tick=1; f.world.alive=true; f.world.health=30; f.world.max_health=100;
 f.world.pose.yaw_deg=-90; f.items.self.health=30;
 f.items.self.owned_weapons=1u; f.items.combat.tick=1;
 f.combat.weapon=4; f.combat.yaw_delta_deg=2; f.combat.pitch_delta_deg=3;
 f.combat.forward=0.3; f.combat.strafe=-0.2; f.combat.fire=true;
 return f;
}
navbridge::BridgeProfileBundle Profile() {
 navbridge::BridgeProfileBundle p{};
 Check(navbridge::BuildBridgeProfile(4,1,5678,0,"Nav",&p,0),"profile valid"); return p;
}
void Tick(c2nav::Frame& f,int t) { f.world.tick=f.items.combat.tick=f.contract.snapshot_tick=t; }
void ItemKinds() {
 for(auto kind:{itemai::ItemKind::kHealth,itemai::ItemKind::kArmor,itemai::ItemKind::kAmmo,itemai::ItemKind::kWeapon}) {
  c2nav::Controller c; c2nav::Options o; o.enabled=o.item_goals=true;
  Check(c.Configure(Profile(),o),"enabled configuration valid");
  navlab::NavGraph g; navlab::maps::MakeCorridor(g,4,8);
  auto f=Fixture(); itemai::ItemSnapshot item;
  item.id=7; item.kind=kind; item.pos={16,0,0}; item.value=100; item.amount=100; item.visible=true;
  if(kind==itemai::ItemKind::kAmmo || kind==itemai::ItemKind::kWeapon) item.weapon_index=6;
  f.items.self.owned_weapons |= 1u<<5;
  if(kind==itemai::ItemKind::kWeapon) f.items.self.owned_weapons=1u;
  f.items.items=&item; f.items.count=1;
  auto out=c.Step(g,f);
  Check(out.status==c2nav::Status::kReady,"valid fixture accepted");
  Check(out.item.has_goal && out.item.goal_id==7,"health/armor/ammo/weapon can produce item goal");
  Check(out.override_movement && out.intent.weapon==f.combat.weapon && !out.intent.fire,
        "item route owns movement while combat retains weapon and fire is inhibited");
  Check(out.expansions<=o.budget.max_expansions_per_tick,"combined budget bounded");
 }
}
void Gates() {
 c2nav::Controller c; navlab::NavGraph g; navlab::maps::MakeCorridor(g,4,8);
 auto f=Fixture(); auto out=c.Step(g,f);
 Check(out.status==c2nav::Status::kDisabled && !out.override_movement,"default off never overrides");
 Check(out.intent.fire==f.combat.fire && out.intent.pitch_delta_deg==3,"disabled preserves external combat");
 c2nav::Options o; o.enabled=o.item_goals=o.patrol=true; c.Configure(Profile(),o);
 f.contract.offline_fixture=false; out=c.Step(g,f);
 Check(out.status==c2nav::Status::kNativeNotQualified && !out.override_movement,"native contract remains blocked");
 f=Fixture(); f.contract.map_sha256="unknown"; out=c.Step(g,f);
 Check(out.status==c2nav::Status::kInvalidContract && !out.override_movement,"missing map digest rejected");
 f=Fixture(); f.contract.snapshot_tick=0; out=c.Step(g,f);
 Check(out.status==c2nav::Status::kInvalidContract,"stale snapshot rejected");
 f=Fixture(); f.contract.anchors_3d_verified=false; out=c.Step(g,f);
 Check(out.status==c2nav::Status::kInvalidContract,"unproven stacked-floor anchors rejected");
 f=Fixture(); f.items.self.eye.y=2; out=c.Step(g,f);
 Check(out.status==c2nav::Status::kInvalidContract,"eye/feet mismatch rejected");
 f=Fixture(); itemai::ItemSnapshot bad; bad.id=1; bad.kind=itemai::ItemKind::kHealth;
 bad.value=25; bad.pos.x=std::numeric_limits<double>::quiet_NaN(); f.items.items=&bad; f.items.count=1;
 out=c.Step(g,f); Check(out.status==c2nav::Status::kInvalidSnapshot,"NaN item rejected before routing");
 o.budget.max_expansions_per_tick=-1; Check(!c.Configure(Profile(),o),"negative budgets rejected");
}
void OwnershipAndLifecycle() {
 c2nav::Controller c; c2nav::Options o; o.enabled=o.item_goals=o.patrol=true; o.budget.max_expansions_per_tick=24;
 c.Configure(Profile(),o); navlab::NavGraph g; navlab::maps::MakeCorridor(g,12,4);
 auto f=Fixture(); f.combat.target=3; f.combat.target_visible=true;
 auto out=c.Step(g,f);
 Check(!out.override_movement && out.intent.fire && out.intent.yaw_delta_deg==2 && out.intent.strafe==-0.2,
       "visible combat owns heading/translation/fire exactly");
 Tick(f,2); f.combat.target=-1; f.combat.target_visible=false; f.combat_movement_reserved=true; out=c.Step(g,f);
 Check(!out.override_movement && out.intent.forward==f.combat.forward,"explicit combat travel/escape reservation keeps movement");
 Tick(f,3); f.combat_movement_reserved=false; out=c.Step(g,f);
 Check(out.override_movement && out.owner==navbridge::ControllerOwner::kPatrolNavigation,"bounded patrol takes idle movement");
 out=c.Step(g,f); Check(out.status==c2nav::Status::kInvalidContract,"duplicate tick rejected");
 Tick(f,4); f.contract.world_instance=2; f.contract.graph_epoch=2;
 g.Clear(); navlab::maps::MakeCorridor(g,3,4); out=c.Step(g,f);
 Check(out.status==c2nav::Status::kReady && out.expansions<=24,"map instance resets routes and shared budget");
 Tick(f,5); f.world.alive=false; out=c.Step(g,f);
 Check(!out.intent.fire && !out.override_movement,"death clears planning, leaves respawn action to driver");
}
void DeterminismAndStuck() {
 c2nav::Controller a,b; c2nav::Options o; o.enabled=o.item_goals=true;
 o.budget.max_expansions_per_tick=32;
 auto p=Profile(); a.Configure(p,o); b.Configure(p,o);
 navlab::NavGraph g; navlab::maps::MakeCorridor(g,8,4);
 auto f=Fixture(); itemai::ItemSnapshot it; it.id=3; it.kind=itemai::ItemKind::kHealth; it.value=50; it.visible=true; it.pos={24,0,0};
 f.items.items=&it; f.items.count=1; int stuck=0;
 for(int t=1;t<=180;++t) {
  Tick(f,t); auto x=a.Step(g,f), y=b.Step(g,f); stuck+=x.goal_move.stuck?1:0;
  Check(x.expansions<=32 && y.expansions<=32,"hard per-tick A* cap");
  Check(x.intent.yaw_delta_deg==y.intent.yaw_delta_deg && x.intent.forward==y.intent.forward &&
        x.item.goal_id==y.item.goal_id && x.expansions==y.expansions,"replay decisions identical");
 }
 Check(stuck>0,"stationary requested movement triggers physical stuck");
}
}
int main() { ItemKinds(); Gates(); OwnershipAndLifecycle(); DeterminismAndStuck(); std::printf("C2 controller: %d checks, %d failures\n",checks,failures); return failures?1:0; }
