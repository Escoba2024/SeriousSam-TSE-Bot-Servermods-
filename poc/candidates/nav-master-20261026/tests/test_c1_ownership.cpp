#include <cstdio>
#include "nav_item_controller.h"
#ifndef COMBAT_MASTER_AVAILABLE
#error Must compile against materialized C1 headers, not a legacy include-path fallback
#endif
int main() {
 c2nav::Controller c; c2nav::Options opts; opts.enabled=opts.item_goals=opts.patrol=true;
 navbridge::BridgeProfileBundle profile{};
 if(!navbridge::BuildBridgeProfile(4,1,12345,0,"Cross",&profile,0) || !c.Configure(profile,opts)) return 1;
 navlab::NavGraph graph; navlab::maps::MakeCorridor(graph,8,4);
 c2nav::Frame f; f.world.alive=true; f.world.health=f.items.self.health=30;
 f.world.pose.yaw_deg=-90; f.combat.weapon=4; f.combat.forward=-0.85; f.combat.yaw_delta_deg=7;
 f.contract.map_sha256="aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa";
 f.contract.waypoints_sha256="bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb";
 f.contract.world_instance=f.contract.graph_epoch=1; f.contract.offline_fixture=true;
 f.contract.anchors_3d_verified=f.contract.item_entities_verified=true;
 itemai::ItemSnapshot item; item.id=1; item.kind=itemai::ItemKind::kHealth; item.value=100; item.pos={16,0,0}; item.visible=true;
 f.items.items=&item; f.items.count=1; f.items.self.owned_weapons=1;
 for(int mode=0;mode<2;++mode) {
  f.world.tick=f.items.combat.tick=f.contract.snapshot_tick=mode+1;
  f.combat.escape=mode==0; f.combat.travel=mode==1;
  auto out=c.Step(graph,f);
  if(out.status!=c2nav::Status::kReady || out.override_movement || out.intent.forward!=-0.85 || out.intent.yaw_delta_deg!=7 || out.intent.weapon!=4) return 1;
 }
 std::puts("C1/C2 real headers: escape and travel retain external movement; health item cannot preempt");
}
