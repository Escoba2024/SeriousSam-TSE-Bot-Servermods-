// SPDX-License-Identifier: GPL-2.0-only
// nav_item_bridge.h - unified per-bot adapter orchestrating Combat-KI
// (`botcore::HumanBotPolicy`), Item-Utility (`itemai::ItemPlanner`) and
// Navigation 2.0 (`NavGraphSink` + `navlab::NavAgent` +
// `botcore::ObstacleRecovery`).
//
// GUARANTEES
//  - Zero heap allocations: all state lives inside `NavItemBridgeAgent`.
//  - Zero shared mutable state: N agents share `const navlab::NavGraph`
//    concurrently/sequentially without interference.
//  - Deterministic: identical `(BotProfile, NavGraph, BridgeTickInput)` streams
//    produce bit-for-bit identical `BridgeTickOutput` sequences.
//  - Strict per-tick CPU budget: total A* node expansions per tick never exceed
//    `BridgeBudgetConfig::max_expansions_per_tick`.

#ifndef NAV_ITEM_BRIDGE_NAV_ITEM_BRIDGE_H
#define NAV_ITEM_BRIDGE_NAV_ITEM_BRIDGE_H

#include <cmath>
#include <cstdint>

#include "bridge_arbitrator.h"
#include "nav_cost_cache.h"
#include "nav_goal_sink.h"

namespace navbridge {

/* ------------------------------------------------------------------------ */
/* Unified profile mapping (5 skill tiers x 6 personalities)                 */
/* ------------------------------------------------------------------------ */

struct BridgeProfileBundle {
  botcore::BotProfile bot_profile;
  itemai::ItemProfile item_profile;
  navlab::NavPersonality nav_personality;
};

inline navlab::NavPersonality NavPersonalityFromBotProfile(
    const botcore::BotProfile& bp, float route_variance = 0.08f) {
  const float aggr = static_cast<float>(bp.personality.aggression);
  const float caut = static_cast<float>(bp.personality.caution);
  const float speed_scale = 1.0f - 0.15f * (caut < 0.0f ? 0.0f : (caut > 1.0f ? 1.0f : caut));
  // Mechanical steering limit comes strictly from the skill block (orthogonal
  // to personality).
  float nav_turn = static_cast<float>(bp.skill.turn_rate_deg_s);
  if (nav_turn < 90.0f) nav_turn = 90.0f;
  if (nav_turn > 340.0f) nav_turn = 340.0f;

  navlab::NavPersonality np =
      navlab::NavPersonalityFromTraits(aggr, caut, speed_scale, nav_turn);
  np.route_variance = route_variance < 0.0f
                          ? 0.0f
                          : (route_variance > 0.5f ? 0.5f : route_variance);
  return np;
}

inline bool BuildBridgeProfile(int tier, int persona, uint32_t base_seed,
                               int slot, const char* name,
                               BridgeProfileBundle* out,
                               float route_variance = 0.08f) {
  if (out == nullptr) return false;
  const uint32_t derived = botcore::DeriveSeed(base_seed, slot, tier, persona);
  if (!botcore::BuildProfile(tier, persona, derived, name, &out->bot_profile)) {
    return false;
  }
  out->item_profile = itemai::ItemProfileFrom(out->bot_profile);
  if (itemai::ValidateProfile(out->item_profile) != itemai::ProfileError::kOk) {
    return false;
  }
  out->nav_personality =
      NavPersonalityFromBotProfile(out->bot_profile, route_variance);
  return true;
}

// Verifies across all three layers (Combat, Item-Utility, Navigation) that
// changing personality at a fixed skill tier never alters mechanical skill
// parameters.
inline bool SkillOrthogonalAcrossAllLayers(int tier, int persona_a,
                                           int persona_b) {
  if (!botcore::SkillUnaffectedByPersonality(tier, persona_a, persona_b)) {
    return false;
  }
  BridgeProfileBundle a{}, b{};
  if (!BuildBridgeProfile(tier, persona_a, 0xCAFEBABEu, 0, "A", &a)) return false;
  if (!BuildBridgeProfile(tier, persona_b, 0xCAFEBABEu, 0, "B", &b)) return false;

  const itemai::ItemSkillBlock& isa = a.item_profile.skill;
  const itemai::ItemSkillBlock& isb = b.item_profile.skill;
  const bool item_skill_equal =
      (isa.tier == isb.tier) &&
      (isa.planning_horizon_s == isb.planning_horizon_s) &&
      (isa.risk_awareness == isb.risk_awareness) &&
      (isa.discipline == isb.discipline) &&
      (isa.tie_noise == isb.tie_noise);

  const bool nav_skill_equal =
      (a.nav_personality.turn_rate_deg_s == b.nav_personality.turn_rate_deg_s);

  return item_skill_equal && nav_skill_equal;
}

/* ------------------------------------------------------------------------ */
/* Per-tick input and output contracts                                       */
/* ------------------------------------------------------------------------ */

struct BridgeTickInput {
  botcore::WorldView world;
  double armor;
  double max_armor;
  uint32_t owned_weapons;
  int ammo[itemai::kWeaponCount + 1];
  double move_speed_mps;

  const botcore::SenseInput* sensed_players;
  const bool* player_los;
  int sensed_count;

  const itemai::ItemSnapshot* items;
  int item_count;

  bool obstacle_avoidance_enabled;
  double obstacle_front_m;
  double obstacle_left_m;
  double obstacle_right_m;
  int preferred_recovery_dir;
  double dt;

  BridgeTickInput()
      : world(),
        armor(0.0),
        max_armor(100.0),
        owned_weapons(1u),
        move_speed_mps(itemai::kDefaultMoveSpeedMps),
        sensed_players(nullptr),
        player_los(nullptr),
        sensed_count(0),
        items(nullptr),
        item_count(0),
        obstacle_avoidance_enabled(true),
        obstacle_front_m(5.0),
        obstacle_left_m(5.0),
        obstacle_right_m(5.0),
        preferred_recovery_dir(1),
        dt(botcore::kTickQuantum) {
    for (int i = 0; i <= itemai::kWeaponCount; ++i) ammo[i] = 0;
  }
};

struct BridgeTickOutput {
  BotDriverIntent intent;
  botcore::BotCommand combat_cmd;
  itemai::GoalDecision item_decision;
  GoalMoveCommand goal_move;
  navlab::NavCommand patrol_cmd;
  botcore::NavigationDecision recovery_decision;
  EnrichmentStats enrichment;
  ArbitrationTrace trace;

  BridgeTickOutput()
      : intent(),
        combat_cmd(),
        item_decision(),
        goal_move(),
        patrol_cmd(),
        recovery_decision(),
        enrichment(),
        trace() {}
};

/* ------------------------------------------------------------------------ */
/* Complete per-bot agent                                                    */
/* ------------------------------------------------------------------------ */

class NavItemBridgeAgent {
 public:
  NavItemBridgeAgent() {
    BridgeProfileBundle def{};
    BuildBridgeProfile(3, 0, 0x1234567u, 0, "BOT-Default", &def);
    Configure(def, BridgeBudgetConfig(), 0);
  }

  void Configure(const BridgeProfileBundle& bundle,
                 const BridgeBudgetConfig& budget_cfg = BridgeBudgetConfig(),
                 int slot = 0) {
    bundle_ = bundle;
    budget_cfg_ = budget_cfg;
    budget_cfg_.route_variance = bundle.nav_personality.route_variance;
    slot_ = slot;

    human_policy_.Configure(&bundle_.bot_profile);
    item_planner_.Configure(bundle_.item_profile);
    item_planner_.set_slot(slot_);
    goal_sink_.Configure(budget_cfg_, bundle_.nav_personality,
                         bundle_.bot_profile.seed ^ 0xA5A55A5Au);
    patrol_agent_.Configure(bundle_.nav_personality,
                            bundle_.bot_profile.seed ^ 0x3C6EF372u);
    Reset();
  }

  void Reset() {
    human_policy_.Reset();
    item_planner_.Reset();
    item_planner_.set_slot(slot_);
    goal_sink_.Reset();
    patrol_agent_.Reset();
    obstacle_recovery_.Reset();
    local_blocked_.Clear();
    enricher_.Reset();
    true_items_.Clear();
    damage_tracker_.Reset();
    tick_budget_.Reset(budget_cfg_.max_expansions_per_tick);

    began_tick_ = -1000000;
    was_alive_ = false;
    last_health_ = 0.0;
    last_move_requested_ = false;
    last_goal_move_requested_ = false;
    recovery_advance_ticks_ = 0;
    budgeted_patrol_dest_ = -1;
    budgeted_patrol_len_ = 0;
    budgeted_patrol_pos_ = 0;
    total_ticks_ = 0;
    total_expansions_ = 0;
    max_tick_expansions_ = 0;
  }

  // Optional pre-step ray planning (mirrors BotDriver.cpp 2-pass LOS budget).
  void PlanLosQueries(const botcore::WorldView& w,
                      const botcore::SenseInput* sensed, int count,
                      bool* needs_ray) {
    HandleLifeAndDamage(w);
    human_policy_.BeginTick(w);
    began_tick_ = w.tick;
    human_policy_.PlanLosQueries(sensed, count, needs_ray);
  }

  void NotifyItemPicked(int item_id, int tick) {
    item_planner_.NotifyItemPicked(item_id, tick);
  }

  BridgeTickOutput Step(const navlab::NavGraph& graph, uint32_t graph_epoch,
                        const BridgeTickInput& in) {
    BridgeTickOutput out;
    ++total_ticks_;

    const int tick = in.world.tick;
    tick_budget_.Reset(budget_cfg_.max_expansions_per_tick);
    local_blocked_.Expire(tick);

    // Ensure usable_weapons reflects owned_weapons + ammo when caller leaves
    // `world.usable_weapons == 0`.
    botcore::WorldView wv = in.world;
    if (wv.usable_weapons == 0u) {
      itemai::SelfState tmp_s;
      tmp_s.owned_weapons = in.owned_weapons;
      for (int i = 0; i <= itemai::kWeaponCount; ++i) tmp_s.ammo[i] = in.ammo[i];
      wv.usable_weapons = itemai::UsableWeaponMask(tmp_s);
    }

    if (began_tick_ != tick) {
      HandleLifeAndDamage(wv);
      human_policy_.BeginTick(wv);
      began_tick_ = tick;
    }

    // ---- 1. Combat-KI (`botcore::HumanBotPolicy`) -----------------------
    out.combat_cmd = human_policy_.Step(wv, in.sensed_players, in.player_los,
                                        in.sensed_count, in.dt);

    if (!wv.alive || !wv.deathmatch) {
      out.trace.tick = tick;
      out.trace.expansion_limit = budget_cfg_.max_expansions_per_tick;
      out.intent = ArbitrateCommands(wv, graph.node_count() > 0, out.combat_cmd,
                                     out.item_decision, out.goal_move,
                                     out.patrol_cmd, out.recovery_decision,
                                     &out.trace);
      last_move_requested_ = false;
      last_goal_move_requested_ = false;
      return out;
    }

    // ---- 2. Item-Utility (`Enrich` + `ItemPlanner` + `NavGraphSink`) ----
    itemai::ItemWorld raw_iw;
    raw_iw.items = in.items;
    raw_iw.count = in.item_count;
    raw_iw.self.eye = MakeVec3(wv.pose.x, wv.pose.y, wv.pose.z);
    raw_iw.self.health = wv.health;
    raw_iw.self.max_health = wv.max_health;
    raw_iw.self.armor = in.armor;
    raw_iw.self.max_armor = in.max_armor;
    raw_iw.self.owned_weapons = in.owned_weapons;
    for (int i = 0; i <= itemai::kWeaponCount; ++i) {
      raw_iw.self.ammo[i] = in.ammo[i];
    }
    raw_iw.self.move_speed_mps =
        in.move_speed_mps > 0.1 ? in.move_speed_mps : itemai::kDefaultMoveSpeedMps;
    DeriveThreatAndCombat(wv, human_policy_, out.combat_cmd, damage_tracker_,
                          &raw_iw.threat, &raw_iw.combat);

    // Reserve headroom inside the per-tick expansion budget so an immediate
    // `NavGraphSink::Submit` can route the newly chosen goal in the same tick.
    const int total_limit = budget_cfg_.max_expansions_per_tick;
    const int goal_reserve = total_limit > 32 ? (total_limit / 2) : 0;
    const int enrich_limit = total_limit - goal_reserve;
    TickExpansionBudget enrich_budget(enrich_limit);

    out.enrichment = enricher_.Enrich(
        graph, graph_epoch, budget_cfg_, bundle_.bot_profile.seed,
        bundle_.item_profile, item_planner_.goal_id(), raw_iw, search_,
        local_blocked_, enrich_budget, adapted_items_, &adapted_world_,
        &true_items_);
    if (enrich_budget.used() > 0) {
      tick_budget_.Charge(enrich_budget.used());
    }

    goal_sink_.BindTickContext(&graph, graph_epoch, tick, raw_iw.self.eye,
                               wv.pose.yaw_deg, &true_items_, &search_,
                               &tick_budget_, &local_blocked_);
    out.item_decision = item_planner_.Step(adapted_world_, &goal_sink_);

    // Restore authoritative 3D pickup coordinates on the public decision while
    // keeping path-adjusted travel_s and recording effective_path_m.
    double goal_eff_path_m = -1.0;
    if (out.item_decision.goal_id >= 0) {
      const TrueItemEntry* te = true_items_.Find(out.item_decision.goal_id);
      if (te != nullptr) {
        out.item_decision.goal_pos = te->true_pos;
        goal_eff_path_m = te->effective_path_m;
      }
    }

    // ---- 3. Navigation 2.0 (`NavGraphSink` or `NavAgent`) ---------------
    const bool visible_combat =
        (out.combat_cmd.target >= 0 && out.combat_cmd.target_visible);
    const bool combat_preempts_goal =
        visible_combat && !out.item_decision.suppress_combat;

    if (out.item_decision.has_goal && goal_sink_.has_active_goal()) {
      out.goal_move = goal_sink_.StepGoalMove(
          !combat_preempts_goal, last_goal_move_requested_,
          in.obstacle_front_m);
    } else if (!visible_combat && graph.node_count() > 0) {
      out.patrol_cmd = StepPatrolOrReposition(graph, graph_epoch, wv);
    }

    // ---- 4. Reactive `ObstacleRecovery` underneath movement -------------
    double prelim_fwd = 0.0;
    bool combat_hold = false;
    if (visible_combat && !(out.item_decision.has_goal &&
                            out.item_decision.suppress_combat &&
                            out.goal_move.active)) {
      prelim_fwd = out.combat_cmd.forward;
      const bool melee = (out.combat_cmd.weapon == 1 || out.combat_cmd.weapon == 10);
      combat_hold = out.combat_cmd.distance_m <= (melee ? 1.5 : 8.0) &&
                    prelim_fwd <= 0.0;
    } else if (out.item_decision.has_goal && out.goal_move.active) {
      prelim_fwd = out.goal_move.forward;
    } else if (graph.node_count() > 0 && out.patrol_cmd.active) {
      prelim_fwd = out.patrol_cmd.forward;
    }

    if (in.obstacle_avoidance_enabled) {
      // When Navigation 2.0 just replanned around a blocked corridor, cancel
      // any lingering blind recovery walk so A* can immediately steer onto the
      // new detour instead of being driven 20+ m off the waypoint mesh.
      if (out.goal_move.replanned && out.goal_move.stuck) {
        obstacle_recovery_.Reset();
        recovery_advance_ticks_ = 0;
      }
      botcore::NavigationInput nav_in{};
      nav_in.x = wv.pose.x;
      nav_in.z = wv.pose.z;
      nav_in.yaw = wv.pose.yaw_deg;
      nav_in.turnLimit = 9.0;
      nav_in.forward = prelim_fwd > 0.0 ? prelim_fwd : 0.0;
      nav_in.front = in.obstacle_front_m;
      nav_in.left = in.obstacle_left_m;
      nav_in.right = in.obstacle_right_m;
      nav_in.alive = true;
      nav_in.holdPosition = combat_hold;
      nav_in.preferredDirection = in.preferred_recovery_dir >= 0 ? 1 : -1;
      nav_in.moveScale = 1.0;
      out.recovery_decision = obstacle_recovery_.Update(nav_in);

      // `botcore::ObstacleRecovery` uses a 40-tick (24 m) Advance phase built
      // for mapless bots. When a NavGraph is active, hand control back to A*
      // after 6 clear Advance ticks (~3.5 m clearance) so bots stay on-mesh.
      if (graph.node_count() > 0 && out.recovery_decision.active &&
          out.recovery_decision.phase == botcore::NavigationPhase::Advance) {
        if (in.obstacle_front_m >= 1.8) {
          ++recovery_advance_ticks_;
          if (recovery_advance_ticks_ >= 6) {
            obstacle_recovery_.Reset();
            out.recovery_decision = botcore::NavigationDecision();
            recovery_advance_ticks_ = 0;
          }
        }
      } else {
        recovery_advance_ticks_ = 0;
      }
    } else {
      obstacle_recovery_.Reset();
      recovery_advance_ticks_ = 0;
    }

    // ---- 5. Three-Layer Arbitration & Audit Trace -----------------------
    out.trace.tick = tick;
    out.trace.combat_target = out.combat_cmd.target;
    out.trace.combat_target_visible = out.combat_cmd.target_visible;
    out.trace.combat_priority = raw_iw.combat.combat_priority;
    out.trace.under_fire = raw_iw.threat.under_fire;
    out.trace.item_action = out.item_decision.action;
    out.trace.item_reason = out.item_decision.reason;
    out.trace.has_item_goal = out.item_decision.has_goal;
    out.trace.item_goal_id = out.item_decision.goal_id;
    out.trace.item_goal_kind = out.item_decision.goal_kind;
    out.trace.item_true_pos = out.item_decision.goal_pos;
    out.trace.item_utility = out.item_decision.utility;
    out.trace.item_effective_path_m = goal_eff_path_m;
    out.trace.suppress_combat = out.item_decision.suppress_combat;
    out.trace.nav_status = goal_sink_.status();
    out.trace.patrol_mode = out.patrol_cmd.mode;
    out.trace.expansions_used = tick_budget_.used();
    out.trace.expansion_limit = tick_budget_.limit();
    out.trace.cost_cache_hits = out.enrichment.cache_hits;
    out.trace.cost_probes = out.enrichment.probes_executed;
    out.trace.replanned = out.goal_move.replanned || out.patrol_cmd.replanned;
    out.trace.stuck_detected = out.goal_move.stuck || out.patrol_cmd.stuck;

    out.intent = ArbitrateCommands(wv, graph.node_count() > 0, out.combat_cmd,
                                   out.item_decision, out.goal_move,
                                   out.patrol_cmd, out.recovery_decision,
                                   &out.trace);

    last_move_requested_ = (out.intent.forward > 0.05);
    last_goal_move_requested_ =
        out.goal_move.active &&
        (out.goal_move.forward > 0.05 || out.recovery_decision.active);
    total_expansions_ += tick_budget_.used();
    if (tick_budget_.used() > max_tick_expansions_) {
      max_tick_expansions_ = tick_budget_.used();
    }
    return out;
  }

  /* --- Read-only component accessors (tests / telemetry) ----------------- */
  const BridgeProfileBundle& profile_bundle() const { return bundle_; }
  const botcore::HumanBotPolicy& human_policy() const { return human_policy_; }
  const itemai::ItemPlanner& item_planner() const { return item_planner_; }
  const NavGraphSink& goal_sink() const { return goal_sink_; }
  const navlab::NavAgent& patrol_agent() const { return patrol_agent_; }
  const LocalBlockedEdgeTable& local_blocked_edges() const {
    return local_blocked_;
  }
  const WorldPathEnricher& enricher() const { return enricher_; }
  int total_ticks() const { return total_ticks_; }
  long long total_expansions() const { return total_expansions_; }
  int max_tick_expansions() const { return max_tick_expansions_; }

 private:
  void HandleLifeAndDamage(const botcore::WorldView& w) {
    if (was_alive_ && !w.alive) {
      item_planner_.Reset();
      item_planner_.set_slot(slot_);
      goal_sink_.Reset();
      patrol_agent_.Reset();
      obstacle_recovery_.Reset();
      local_blocked_.Clear();
      enricher_.Reset();
      damage_tracker_.Reset();
      last_health_ = 0.0;
      last_move_requested_ = false;
      last_goal_move_requested_ = false;
      recovery_advance_ticks_ = 0;
    } else if (was_alive_ && w.alive && last_health_ > 0.0 &&
               w.health < last_health_) {
      human_policy_.NotifyDamage(last_health_, w.health);
      damage_tracker_.RecordTick(w.tick, last_health_, w.health);
    } else if (w.alive) {
      damage_tracker_.RecordTick(w.tick, last_health_, w.health);
    }
    was_alive_ = w.alive;
    last_health_ = w.alive ? w.health : 0.0;
  }

  navlab::NavCommand StepPatrolOrReposition(const navlab::NavGraph& graph,
                                            uint32_t graph_epoch,
                                            const botcore::WorldView& wv) {
    // Normal budget headroom: delegate directly to PR #54's `navlab::NavAgent`
    // (whose internal A* cap is 256 expansions).
    if (tick_budget_.Remaining() >= 256) {
      navlab::NavAgentInput nav_in{};
      nav_in.tick = wv.tick;
      nav_in.x = wv.pose.x;
      nav_in.y = wv.pose.y;
      nav_in.z = wv.pose.z;
      nav_in.yaw_deg = wv.pose.yaw_deg;
      nav_in.alive = wv.alive;
      nav_in.movement_requested = last_move_requested_;
      nav_in.has_target = (wv.alive && human_policy_.target() >= 0);
      nav_in.target_visible = false;
      nav_in.target_x = 0.0;
      nav_in.target_y = 0.0;
      nav_in.target_z = 0.0;
      if (nav_in.has_target) {
        const botcore::TrackState* tr =
            human_policy_.perception().Track(human_policy_.target());
        if (tr != nullptr) {
          nav_in.target_visible = tr->visible_now;
          nav_in.target_x = tr->x;
          nav_in.target_y = tr->y;
          nav_in.target_z = tr->z;
        } else {
          nav_in.has_target = false;
        }
      }
      navlab::NavCommand cmd = patrol_agent_.Step(graph, nav_in);
      if (cmd.replanned && cmd.expanded_last_search > 0) {
        tick_budget_.Charge(cmd.expanded_last_search);
      }
      return cmd;
    }

    // Tight-budget mode (`Remaining() < 256`): step patrol using our
    // `ConstrainedNavSearch` so `tick_budget_` is never exceeded.
    (void)graph_epoch;
    navlab::NavCommand cmd;
    cmd.mode = navlab::NavMode::kPatrol;
    const int n = graph.node_count();
    if (n <= 0) return cmd;

    // Advance budgeted patrol route if active.
    while (budgeted_patrol_pos_ < budgeted_patrol_len_) {
      const int idx = budgeted_patrol_route_[budgeted_patrol_pos_];
      if (!graph.Valid(idx)) {
        ++budgeted_patrol_pos_;
        continue;
      }
      const navlab::NavNode& nd = graph.node(idx);
      const double d = PlanarDistXZ(wv.pose.x, wv.pose.z, nd.x, nd.z);
      if (d <= (nd.radius > 1.0f ? nd.radius : 1.0f)) {
        ++budgeted_patrol_pos_;
      } else {
        break;
      }
    }

    if (budgeted_patrol_pos_ >= budgeted_patrol_len_ &&
        tick_budget_.Remaining() > 0) {
      const int start =
          graph.NearestNode(wv.pose.x, wv.pose.z, budget_cfg_.max_anchor_dist_m);
      const int goal =
          static_cast<int>((bundle_.bot_profile.seed + static_cast<uint32_t>(wv.tick / 20)) %
                           static_cast<uint32_t>(n));
      if (start >= 0 && goal >= 0 && start != goal) {
        const navlab::NavPath p = search_.Search(
            graph, start, goal, tick_budget_.Remaining(),
            budget_cfg_.route_variance, bundle_.bot_profile.seed,
            &local_blocked_, wv.tick, budget_cfg_.avoid_danger_edges,
            &tick_budget_);
        budgeted_patrol_len_ = 0;
        for (int i = 0; i < p.count && i < navlab::kNavMaxPathNodes; ++i) {
          budgeted_patrol_route_[budgeted_patrol_len_++] = p.nodes[i];
        }
        budgeted_patrol_pos_ = 0;
        budgeted_patrol_dest_ = goal;
        cmd.replanned = true;
        cmd.expanded_last_search = p.expanded;
      }
    }

    if (budgeted_patrol_pos_ < budgeted_patrol_len_ &&
        graph.Valid(budgeted_patrol_route_[budgeted_patrol_pos_])) {
      const navlab::NavNode& next =
          graph.node(budgeted_patrol_route_[budgeted_patrol_pos_]);
      const double dx = next.x - wv.pose.x;
      const double dz = next.z - wv.pose.z;
      const double desired =
          std::atan2(-dx, -dz) * (180.0 / navlab::kNavPi);
      double delta = desired - wv.pose.yaw_deg;
      while (delta > 180.0) delta -= 360.0;
      while (delta < -180.0) delta += 360.0;
      const double max_step =
          bundle_.nav_personality.turn_rate_deg_s / navlab::kNavTickHz;
      cmd.yaw_delta_deg =
          delta < -max_step ? -max_step : (delta > max_step ? max_step : delta);
      cmd.desired_yaw_deg = wv.pose.yaw_deg + cmd.yaw_delta_deg;
      cmd.forward =
          (std::fabs(delta) > 60.0) ? 0.0 : bundle_.nav_personality.walk_factor;
      cmd.active = true;
      cmd.dest_node = budgeted_patrol_dest_;
      cmd.route_hops_left = budgeted_patrol_len_ - budgeted_patrol_pos_;
    } else {
      cmd.active = true;
      cmd.forward = 0.0;
      cmd.yaw_delta_deg = 3.0;
      cmd.desired_yaw_deg = wv.pose.yaw_deg + 3.0;
    }
    return cmd;
  }

  BridgeProfileBundle bundle_{};
  BridgeBudgetConfig budget_cfg_{};
  int slot_ = 0;

  botcore::HumanBotPolicy human_policy_;
  itemai::ItemPlanner item_planner_;
  NavGraphSink goal_sink_;
  navlab::NavAgent patrol_agent_;
  botcore::ObstacleRecovery obstacle_recovery_;

  ConstrainedNavSearch search_;
  LocalBlockedEdgeTable local_blocked_;
  WorldPathEnricher enricher_;
  TrueItemTable true_items_;
  DamageTracker damage_tracker_;
  TickExpansionBudget tick_budget_;

  itemai::ItemSnapshot adapted_items_[itemai::kMaxItems];
  itemai::ItemWorld adapted_world_;

  int began_tick_ = -1000000;
  bool was_alive_ = false;
  double last_health_ = 0.0;
  bool last_move_requested_ = false;
  bool last_goal_move_requested_ = false;
  int recovery_advance_ticks_ = 0;

  int budgeted_patrol_dest_ = -1;
  int16_t budgeted_patrol_route_[navlab::kNavMaxPathNodes] = {0};
  int budgeted_patrol_len_ = 0;
  int budgeted_patrol_pos_ = 0;

  int total_ticks_ = 0;
  long long total_expansions_ = 0;
  int max_tick_expansions_ = 0;
};

}  // namespace navbridge

#endif  // NAV_ITEM_BRIDGE_NAV_ITEM_BRIDGE_H
