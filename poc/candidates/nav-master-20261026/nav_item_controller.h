// SPDX-License-Identifier: GPL-2.0-only
// Offline candidate. No Engine ABI, entity casts, rays, action packets or I/O.
#ifndef C2NAV_ITEM_CONTROLLER_H
#define C2NAV_ITEM_CONTROLLER_H
#include <cstring>
#include <climits>
#include "nav_item_bridge.h"
#if !NAV_ITEM_BRIDGE_UPSTREAM_NAVLAB || !NAV_ITEM_BRIDGE_UPSTREAM_ITEMAI
#error C2 requires the pinned, real Navigation and Item upstream headers
#endif
namespace c2nav {
enum class Status { kDisabled, kReady, kNativeNotQualified, kInvalidContract, kInvalidSnapshot };
struct Options {
  bool enabled = false;
  bool item_goals = false;
  bool patrol = false;
  navbridge::BridgeBudgetConfig budget;
};
// These are caller evidence declarations, not proofs of Retail ABI identity.
// Only offline_fixture=true is accepted by this unqualified candidate.
struct Contract {
  const char* map_sha256 = nullptr;
  const char* waypoints_sha256 = nullptr;
  uint64_t world_instance = 0;
  uint32_t graph_epoch = 0;
  int snapshot_tick = -1;
  bool anchors_3d_verified = false;
  bool item_entities_verified = false;
  bool offline_fixture = false;
};
struct Frame {
  Contract contract;
  botcore::WorldView world;
  botcore::BotCommand combat;       // Produced exactly once by the caller/C1.
  bool combat_movement_reserved = false; // Caller can reserve escape/travel/hold.
  itemai::ItemWorld items;          // Same pose/health/tick as `world`.
  botcore::NavigationDecision recovery{}; // Existing caller-owned recovery.
  double front_obstacle_m = 5.0;
};
struct Result {
  Status status = Status::kDisabled;
  bool override_movement = false; // Driver must ignore intent when false.
  navbridge::BotDriverIntent intent;
  navbridge::ControllerOwner owner = navbridge::ControllerOwner::kCombat;
  itemai::GoalDecision item;
  navbridge::GoalMoveCommand goal_move;
  int expansions = 0;
};
inline bool Digest(const char* s) {
  if (!s) return false;
  for (int i=0; i<64; ++i) {
    const char c=s[i];
    if (!((c>='0' && c<='9') || (c>='a' && c<='f') || (c>='A' && c<='F'))) return false;
  }
  return s[64]=='\0';
}
// PR57/C1 add escape/travel. Legacy botcore does not expose these members.
// Preserve either policy's explicit movement reservation without owning it.
template<class Command>
auto PolicyMovementReserved(const Command& cmd, int) -> decltype(bool(cmd.escape || cmd.travel)) {
  return cmd.escape || cmd.travel;
}
template<class Command>
bool PolicyMovementReserved(const Command&, long) { return false; }
class Controller {
 public:
  bool Configure(const navbridge::BridgeProfileBundle& profile, const Options& opts) {
    const auto& b=opts.budget;
    configured_=itemai::ValidateProfile(profile.item_profile)==itemai::ProfileError::kOk &&
      b.max_expansions_per_tick>=0 && b.max_expansions_per_tick<=navlab::kNavMaxNodes &&
      b.max_expand_goal_search>0 && b.max_expand_goal_search<=navlab::kNavMaxNodes &&
      b.max_expand_cost_probe>0 && b.max_expand_cost_probe<=navlab::kNavMaxNodes &&
      b.max_cost_probes_per_tick>=0 && b.max_cost_probes_per_tick<=itemai::kMaxItems &&
      std::isfinite(b.max_anchor_dist_m) && b.max_anchor_dist_m>0 &&
      b.blocked_edge_ttl_ticks>0 && b.blocked_edge_ttl_ticks<=10000 &&
      b.cost_cache_ttl_ticks>0 && b.cost_cache_ttl_ticks<=10000;
    opts_=opts; profile_=profile;
    world_instance_=0; epoch_=0; last_tick_=-1;
    ResetPlanning();
    return configured_;
  }
  void NotifyItemPicked(int id, int tick) { planner_.NotifyItemPicked(id,tick); }
  Result Step(const navlab::NavGraph& graph, const Frame& f) {
    Result out;
    out.intent.weapon=f.combat.weapon;
    if (f.world.alive && f.world.deathmatch) {
      out.intent.yaw_delta_deg=f.combat.yaw_delta_deg;
      out.intent.pitch_delta_deg=f.combat.pitch_delta_deg;
      out.intent.forward=f.combat.forward; out.intent.strafe=f.combat.strafe;
      out.intent.fire=f.combat.fire;
    }
    if (!opts_.enabled || !configured_) return out;
    if (!f.contract.offline_fixture) { out.status=Status::kNativeNotQualified; ResetPlanning(); return out; }
    const auto& c=f.contract;
    if (!Digest(c.map_sha256) || !Digest(c.waypoints_sha256) || c.world_instance==0 || c.graph_epoch==0 ||
        !c.anchors_3d_verified || (opts_.item_goals && !c.item_entities_verified) ||
        c.snapshot_tick!=f.world.tick || f.items.combat.tick!=f.world.tick ||
        f.world.tick<0 || f.world.tick>INT_MAX-100000 ||
        !std::isfinite(f.front_obstacle_m) ||
        f.world.pose.x!=f.items.self.eye.x || f.world.pose.y!=f.items.self.eye.y || f.world.pose.z!=f.items.self.eye.z ||
        f.world.health!=f.items.self.health || f.world.max_health!=f.items.self.max_health ||
        !std::isfinite(f.world.pose.yaw_deg) || !std::isfinite(f.world.pose.pitch_deg)) {
      out.status=Status::kInvalidContract; ResetPlanning(); return out;
    }
    if (itemai::ValidateWorld(f.items)!=itemai::ValidationError::kOk) {
      out.status=Status::kInvalidSnapshot; ResetPlanning(); return out;
    }
    const bool changed=world_instance_!=c.world_instance || epoch_!=c.graph_epoch ||
      std::strcmp(map_hash_,c.map_sha256)!=0 || std::strcmp(waypoint_hash_,c.waypoints_sha256)!=0;
    if (changed) {
      if (!ValidateGraph(graph)) { out.status=Status::kInvalidContract; ResetPlanning(); return out; }
      ResetPlanning(); last_tick_=-1;
      world_instance_=c.world_instance; epoch_=c.graph_epoch;
      std::memcpy(map_hash_,c.map_sha256,65); std::memcpy(waypoint_hash_,c.waypoints_sha256,65);
    }
    if (f.world.tick<=last_tick_) { out.status=Status::kInvalidContract; ResetPlanning(); return out; }
    last_tick_=f.world.tick; out.status=Status::kReady;
    if (!f.world.alive || !f.world.deathmatch) { ResetPlanning(); return out; }
    budget_.Reset(opts_.budget.max_expansions_per_tick);
    blocked_.Expire(f.world.tick);
    itemai::ItemWorld adapted=f.items;
    if (opts_.item_goals) {
      // One shared budget for cost probes + item routes + patrol routes.
      // Cost probes receive half; the remaining headroom is reserved for movement.
      navbridge::TickExpansionBudget probes(budget_.Remaining()/2);
      enricher_.Enrich(graph,c.graph_epoch,opts_.budget,profile_.bot_profile.seed,
        profile_.item_profile,planner_.goal_id(),f.items,search_,blocked_,probes,
        adapted_items_,&adapted,&true_items_);
      budget_.Charge(probes.used());
      Bind(item_sink_,graph,f,&true_items_);
      out.item=planner_.Step(adapted,&item_sink_);
      if (const auto* te=true_items_.Find(out.item.goal_id)) out.item.goal_pos=te->true_pos;
    }
    const bool visible=f.combat.target>=0 && f.combat.target_visible;
    const bool reserved=f.combat_movement_reserved || PolicyMovementReserved(f.combat,0);
    const bool item_drives=out.item.has_goal && !reserved && (!visible || out.item.suppress_combat);
    if (out.item.has_goal && item_sink_.has_active_goal())
      out.goal_move=item_sink_.StepGoalMove(item_drives,last_item_moved_,f.front_obstacle_m);
    navlab::NavCommand patrol{};
    if (!visible && !reserved && !out.item.has_goal && opts_.patrol && graph.node_count()>1) {
      Bind(patrol_sink_,graph,f,nullptr);
      itemai::NavFeedback feedback;
      const auto st=patrol_sink_.Poll(kPatrolGoal,&feedback);
      if (!patrol_sink_.has_active_goal() || itemai::NavIsTerminal(st)) {
        patrol_sink_.Cancel(kPatrolGoal);
        const int start=graph.NearestNode3D(f.world.pose.x,f.world.pose.y,f.world.pose.z,opts_.budget.max_anchor_dist_m);
        int target=static_cast<int>((profile_.bot_profile.seed+patrol_sequence_++)%static_cast<uint32_t>(graph.node_count()));
        if (target==start) target=(target+1)%graph.node_count();
        const auto& node=graph.node(target);
        itemai::NavGoal goal; goal.goal_id=kPatrolGoal; goal.pos={node.x,node.y,node.z};
        goal.issued_tick=f.world.tick; goal.expires_tick=f.world.tick+400; goal.allow_jump=false;
        goal.max_speed_frac=profile_.nav_personality.walk_factor;
        patrol_sink_.Submit(goal);
      }
      const auto move=patrol_sink_.StepGoalMove(true,last_patrol_moved_,f.front_obstacle_m);
      patrol.active=move.active; patrol.forward=move.forward; patrol.yaw_delta_deg=move.yaw_delta_deg;
      patrol.mode=navlab::NavMode::kPatrol;
    }
    navbridge::ArbitrationTrace trace;
    const auto intent=navbridge::ArbitrateCommands(f.world,graph.node_count()>0,f.combat,out.item,
      out.goal_move,patrol,f.recovery,&trace);
    // No nav controller and no recovery: retain the exact external command.
    out.override_movement=out.goal_move.active || patrol.active || f.recovery.overrideInput;
    if (out.override_movement) out.intent=intent;
    out.intent.jump_hint=false; // Jump/ground contracts remain native NOT_TESTED.
    out.owner=out.override_movement?trace.owner:navbridge::ControllerOwner::kCombat;
    last_item_moved_=out.owner==navbridge::ControllerOwner::kItemNavigation ||
                     out.owner==navbridge::ControllerOwner::kSurvivalRetreat;
    last_item_moved_=last_item_moved_ && out.intent.forward>0.05;
    last_patrol_moved_=out.owner==navbridge::ControllerOwner::kPatrolNavigation && out.intent.forward>0.05;
    out.expansions=budget_.used();
    return out;
  }
 private:
  static constexpr int kPatrolGoal=INT_MAX;
  static bool ValidateGraph(const navlab::NavGraph& g) {
    if (g.node_count()<=0) return false;
    for(int n=0;n<g.node_count();++n) {
      const auto& p=g.node(n);
      if (!std::isfinite(p.x) || !std::isfinite(p.y) || !std::isfinite(p.z) || !std::isfinite(p.radius) || p.radius<=0) return false;
      for(int e=0;e<g.edge_count(n);++e) {
        const auto& edge=g.edge(n,e);
        // A*'s planar heuristic requires edge costs >= planar distance.
        if (!g.Valid(edge.to) || !std::isfinite(edge.cost) || edge.cost<g.PlanarDist(n,edge.to)) return false;
      }
    }
    return true;
  }
  void ResetPlanning() {
    planner_.Configure(profile_.item_profile);
    item_sink_.Configure(opts_.budget,profile_.nav_personality,profile_.bot_profile.seed);
    patrol_sink_.Configure(opts_.budget,profile_.nav_personality,profile_.bot_profile.seed^0x87654321u);
    blocked_.Clear(); enricher_.Reset(); true_items_.Clear();
    last_item_moved_=last_patrol_moved_=false; patrol_sequence_=0;
  }
  void Bind(navbridge::NavGraphSink& sink,const navlab::NavGraph& g,const Frame& f,const navbridge::TrueItemTable* table) {
    sink.BindTickContext(&g,f.contract.graph_epoch,f.world.tick,f.items.self.eye,f.world.pose.yaw_deg,
      table,&search_,&budget_,&blocked_);
  }
  bool configured_=false;
  Options opts_;
  navbridge::BridgeProfileBundle profile_{};
  uint64_t world_instance_=0; uint32_t epoch_=0, patrol_sequence_=0;
  char map_hash_[65]={0}, waypoint_hash_[65]={0}; int last_tick_=-1;
  bool last_item_moved_=false, last_patrol_moved_=false;
  itemai::ItemPlanner planner_;
  navbridge::NavGraphSink item_sink_,patrol_sink_;
  navbridge::ConstrainedNavSearch search_;
  navbridge::LocalBlockedEdgeTable blocked_;
  navbridge::WorldPathEnricher enricher_;
  navbridge::TrueItemTable true_items_;
  navbridge::TickExpansionBudget budget_;
  itemai::ItemSnapshot adapted_items_[itemai::kMaxItems];
};
}
#endif
