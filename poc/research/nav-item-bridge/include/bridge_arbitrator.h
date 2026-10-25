// SPDX-License-Identifier: GPL-2.0-only
// bridge_arbitrator.h - strict three-layer priority arbitration between
// Combat-KI (`botcore::HumanBotPolicy`), Item-Utility (`itemai::ItemPlanner`)
// and Navigation 2.0 (`NavGraphSink` + `navlab::NavAgent` +
// `botcore::ObstacleRecovery`).
//
// ARCHITECTURAL INVARIANT (hard separation of responsibilities)
//  - Combat-KI decides WHEN combat takes precedence + owns aim, fire & weapon.
//  - Item-Utility decides WHICH item goal is worthwhile + owns hysteresis/abort.
//  - Navigation decides HOW to reach the active goal or patrol/recover.
//  None of the three layers reaches into the internal state of the others.

#ifndef NAV_ITEM_BRIDGE_BRIDGE_ARBITRATOR_H
#define NAV_ITEM_BRIDGE_BRIDGE_ARBITRATOR_H

#include <cmath>
#include <cstdint>
#include <cstdio>

#include "nav_goal_sink.h"

namespace navbridge {

/* ------------------------------------------------------------------------ */
/* Explicit ownership and arbitration reason vocabulary                      */
/* ------------------------------------------------------------------------ */

enum class ControllerOwner : uint8_t {
  kDeadIdle = 0,
  kCombat = 1,
  kSurvivalRetreat = 2,
  kItemNavigation = 3,
  kPatrolNavigation = 4,
  kObstacleRecovery = 5
};

inline const char* ControllerOwnerName(ControllerOwner o) {
  switch (o) {
    case ControllerOwner::kDeadIdle: return "dead-idle";
    case ControllerOwner::kCombat: return "combat";
    case ControllerOwner::kSurvivalRetreat: return "survival-retreat";
    case ControllerOwner::kItemNavigation: return "item-navigation";
    case ControllerOwner::kPatrolNavigation: return "patrol-navigation";
    case ControllerOwner::kObstacleRecovery: return "obstacle-recovery";
    default: return "?";
  }
}

enum class ArbitrationReason : uint8_t {
  kNotAlive = 0,
  kVisibleEnemyCombatLeads = 1,
  kCombatPreemptedItemGoal = 2,
  kSurvivalGoalOverridesCombat = 3,
  kItemGoalActiveNoVisibleEnemy = 4,
  kRememberedEnemyReposition = 5,
  kPatrolExplore = 6,
  kMaplessScan = 7,
  kReactiveObstacleRecovery = 8
};

inline const char* ArbitrationReasonName(ArbitrationReason r) {
  switch (r) {
    case ArbitrationReason::kNotAlive:
      return "not-alive";
    case ArbitrationReason::kVisibleEnemyCombatLeads:
      return "visible-enemy-combat-leads";
    case ArbitrationReason::kCombatPreemptedItemGoal:
      return "combat-preempted-item-goal";
    case ArbitrationReason::kSurvivalGoalOverridesCombat:
      return "survival-goal-overrides-combat";
    case ArbitrationReason::kItemGoalActiveNoVisibleEnemy:
      return "item-goal-active-no-visible-enemy";
    case ArbitrationReason::kRememberedEnemyReposition:
      return "remembered-enemy-reposition";
    case ArbitrationReason::kPatrolExplore:
      return "patrol-explore";
    case ArbitrationReason::kMaplessScan:
      return "mapless-scan";
    case ArbitrationReason::kReactiveObstacleRecovery:
      return "reactive-obstacle-recovery";
    default:
      return "?";
  }
}

/* ------------------------------------------------------------------------ */
/* Driver-facing intent (maps 1:1 onto BotDriver.cpp CPlayerAction build)    */
/* ------------------------------------------------------------------------ */

struct BotDriverIntent {
  double yaw_delta_deg;    // Added to accumulated heading `bs_aHeading`
  double pitch_delta_deg;  // Added to `bs_aPitch`
  double forward;          // [-1..+1]; BotDriver sets pa_vTranslation(3)=-fwd
  double strafe;           // [-1..+1]; BotDriver sets pa_vTranslation(1)=strafe
  bool fire;               // PLACT_FIRE request (gated by alive & weapon ready)
  int weapon;              // Desired weapon index 1..14 (always from Combat)
  bool jump_hint;          // Optional jump edge hint from waypoint flags

  BotDriverIntent()
      : yaw_delta_deg(0.0),
        pitch_delta_deg(0.0),
        forward(0.0),
        strafe(0.0),
        fire(false),
        weapon(1),
        jump_hint(false) {}
};

/* ------------------------------------------------------------------------ */
/* Explainable per-tick trace                                                */
/* ------------------------------------------------------------------------ */

struct ArbitrationTrace {
  int tick;
  ControllerOwner owner;
  ArbitrationReason arb_reason;

  // Combat summary
  int combat_target;
  bool combat_target_visible;
  double combat_priority;
  bool under_fire;

  // Item-Utility summary
  itemai::ItemAction item_action;
  itemai::ItemReason item_reason;
  bool has_item_goal;
  int item_goal_id;
  itemai::ItemKind item_goal_kind;
  itemai::Vec3 item_true_pos;
  double item_utility;
  double item_effective_path_m;
  bool suppress_combat;

  // Navigation & budget summary
  itemai::NavStatus nav_status;
  navlab::NavMode patrol_mode;
  int expansions_used;
  int expansion_limit;
  int cost_cache_hits;
  int cost_probes;
  bool replanned;
  bool stuck_detected;
  bool obstacle_recovery_active;
  char summary[160];

  ArbitrationTrace()
      : tick(0),
        owner(ControllerOwner::kDeadIdle),
        arb_reason(ArbitrationReason::kNotAlive),
        combat_target(-1),
        combat_target_visible(false),
        combat_priority(0.0),
        under_fire(false),
        item_action(itemai::ItemAction::kNone),
        item_reason(itemai::ItemReason::kNone),
        has_item_goal(false),
        item_goal_id(-1),
        item_goal_kind(itemai::ItemKind::kNone),
        item_true_pos(),
        item_utility(0.0),
        item_effective_path_m(-1.0),
        suppress_combat(false),
        nav_status(itemai::NavStatus::kIdle),
        patrol_mode(navlab::NavMode::kIdle),
        expansions_used(0),
        expansion_limit(0),
        cost_cache_hits(0),
        cost_probes(0),
        replanned(false),
        stuck_detected(false),
        obstacle_recovery_active(false) {
    summary[0] = '\0';
  }
};

/* ------------------------------------------------------------------------ */
/* Combat -> Item ThreatState & CombatContext derivation                     */
/* ------------------------------------------------------------------------ */

struct DamageTracker {
  int last_damage_tick;
  int window_start_tick;
  double window_damage;

  DamageTracker()
      : last_damage_tick(-1000000), window_start_tick(-1), window_damage(0.0) {}

  void Reset() {
    last_damage_tick = -1000000;
    window_start_tick = -1;
    window_damage = 0.0;
  }

  void RecordTick(int tick, double health_before, double health_after) {
    if (window_start_tick < 0 || (tick - window_start_tick) >= 40) {
      window_start_tick = tick;
      window_damage = 0.0;
    }
    if (health_before > 0.0 && health_after < health_before) {
      const double loss = health_before - health_after;
      window_damage += loss;
      last_damage_tick = tick;
    }
  }
};

inline void DeriveThreatAndCombat(const botcore::WorldView& w,
                                  const botcore::HumanBotPolicy& policy,
                                  const botcore::BotCommand& combat_cmd,
                                  const DamageTracker& dmg,
                                  itemai::ThreatState* out_threat,
                                  itemai::CombatContext* out_combat) {
  itemai::ThreatState ts;
  itemai::CombatContext cc;
  cc.tick = w.tick >= 0 ? w.tick : 0;

  int vis_count = 0;
  double nearest_m = -1.0;
  const botcore::Perception& perc = policy.perception();
  for (int slot = 0; slot < botcore::kMaxPlayers; ++slot) {
    if (!perc.Visible(slot)) continue;
    const botcore::TrackState* tr = perc.Track(slot);
    if (tr == nullptr) continue;
    ++vis_count;
    const double dx = tr->x - w.pose.x;
    const double dy = tr->y - w.pose.y;
    const double dz = tr->z - w.pose.z;
    const double d = std::sqrt(dx * dx + dy * dy + dz * dz);
    if (nearest_m < 0.0 || d < nearest_m) nearest_m = d;
  }

  ts.visible_enemies = vis_count;
  ts.nearest_enemy_m = nearest_m;
  ts.under_fire = perc.alerted() || (w.tick == dmg.last_damage_tick);
  ts.seconds_since_damage =
      (dmg.last_damage_tick >= 0 && w.tick >= dmg.last_damage_tick)
          ? static_cast<double>(w.tick - dmg.last_damage_tick) *
                botcore::kTickQuantum
          : 999.0;
  ts.target_visible = (combat_cmd.target >= 0 && combat_cmd.target_visible);
  ts.target_distance_m =
      (combat_cmd.target >= 0 && combat_cmd.distance_m > 0.0)
          ? combat_cmd.distance_m
          : nearest_m;
  ts.incoming_dps = dmg.window_damage > 0.0 ? (dmg.window_damage / 2.0) : 0.0;

  // Combat priority (WHEN fight leads):
  //  - 0.0 when no visible enemy is active.
  //  - Scales smoothly with proximity vs preferred engagement range + incoming
  //    fire so close/active duels lock out non-survival detours while poke-range
  //    sightings differentiate personas via `combat_lock_priority`.
  if (ts.target_visible || vis_count > 0) {
    cc.engaged = true;
    const double pref = combat_cmd.preferred_range_m > 4.0
                            ? combat_cmd.preferred_range_m
                            : 15.0;
    const double d = ts.target_distance_m > 0.0 ? ts.target_distance_m : 20.0;
    double prio = 0.88;
    if (d > pref * 1.5) {
      const double excess = (d - pref * 1.5) / (pref * 2.0);
      prio = 0.88 - 0.34 * itemai::Clamp01(excess);
    }
    if (ts.under_fire) prio += 0.08;
    cc.combat_priority = itemai::Clamp01(prio);
  } else {
    cc.engaged = false;
    cc.combat_priority = 0.0;
  }

  *out_threat = ts;
  *out_combat = cc;
}

/* ------------------------------------------------------------------------ */
/* Three-layer command merge                                                 */
/* ------------------------------------------------------------------------ */

inline BotDriverIntent ArbitrateCommands(
    const botcore::WorldView& w, bool has_waypoint_graph,
    const botcore::BotCommand& combat_cmd,
    const itemai::GoalDecision& item_dec, const GoalMoveCommand& goal_move,
    const navlab::NavCommand& patrol_cmd,
    const botcore::NavigationDecision& recovery_dec,
    ArbitrationTrace* trace) {
  BotDriverIntent out;
  out.weapon = combat_cmd.weapon > 0 ? combat_cmd.weapon : 1;

  if (!w.alive || !w.deathmatch) {
    if (trace != nullptr) {
      trace->owner = ControllerOwner::kDeadIdle;
      trace->arb_reason = ArbitrationReason::kNotAlive;
    }
    return out;
  }

  const bool visible_combat =
      (combat_cmd.target >= 0 && combat_cmd.target_visible);
  const bool survival_override =
      (item_dec.has_goal && item_dec.suppress_combat && goal_move.active);

  ControllerOwner owner = ControllerOwner::kPatrolNavigation;
  ArbitrationReason reason = ArbitrationReason::kPatrolExplore;

  if (survival_override && visible_combat) {
    // Survival retreat (`kCritical` medkit/armor): ItemPlanner confirmed no
    // close-range ThreatAbort/DamageAbort triggered, so movement retreats along
    // the A* route to heal. Weapon selection stays with Combat.
    owner = ControllerOwner::kSurvivalRetreat;
    reason = ArbitrationReason::kSurvivalGoalOverridesCombat;
    out.yaw_delta_deg = goal_move.yaw_delta_deg;
    out.pitch_delta_deg = 0.0;
    out.forward = goal_move.forward;
    out.strafe = 0.0;
    out.fire = false;  // Heading is escape route heading, not aim heading.
    out.jump_hint = goal_move.jump_hint;
  } else if (visible_combat) {
    // Combat-KI leads: owns aim, fire, weapon and combat movement/strafing.
    owner = ControllerOwner::kCombat;
    reason = item_dec.has_goal ? ArbitrationReason::kCombatPreemptedItemGoal
                               : ArbitrationReason::kVisibleEnemyCombatLeads;
    out.yaw_delta_deg = combat_cmd.yaw_delta_deg;
    out.pitch_delta_deg = combat_cmd.pitch_delta_deg;
    out.forward = combat_cmd.forward;
    out.strafe = combat_cmd.strafe;
    out.fire = combat_cmd.fire;
    out.jump_hint = false;
  } else if (item_dec.has_goal && goal_move.active) {
    // No visible enemy; Item-Utility selected a worthwhile goal and
    // NavGraphSink drives the A* route toward it.
    owner = ControllerOwner::kItemNavigation;
    reason = ArbitrationReason::kItemGoalActiveNoVisibleEnemy;
    out.yaw_delta_deg = goal_move.yaw_delta_deg;
    out.pitch_delta_deg = 0.0;
    out.forward = goal_move.forward;
    out.strafe = 0.0;
    out.fire = false;
    out.jump_hint = goal_move.jump_hint;
  } else if (has_waypoint_graph && patrol_cmd.active) {
    // No item goal and no visible enemy: Navigation 2.0 drives Patrol,
    // Reposition (toward remembered enemy) or Scan.
    owner = ControllerOwner::kPatrolNavigation;
    reason = (combat_cmd.target >= 0)
                 ? ArbitrationReason::kRememberedEnemyReposition
                 : ArbitrationReason::kPatrolExplore;
    out.yaw_delta_deg = patrol_cmd.yaw_delta_deg;
    out.pitch_delta_deg = 0.0;
    out.forward = patrol_cmd.forward;
    out.strafe = 0.0;
    out.fire = false;
    out.jump_hint = false;
  } else {
    // Mapless fallback: preserve existing HumanBotPolicy scan rotation.
    owner = ControllerOwner::kPatrolNavigation;
    reason = ArbitrationReason::kMaplessScan;
    out.yaw_delta_deg = combat_cmd.yaw_delta_deg;
    out.pitch_delta_deg = 0.0;
    out.forward = 0.0;
    out.strafe = 0.0;
    out.fire = false;
  }

  // Reactive ObstacleRecovery sits underneath movement (identical to
  // BotDriver.cpp:1114): clears immediate wall/corner collisions without
  // altering weapon state and disables fire while steering away from the wall.
  if (recovery_dec.overrideInput) {
    owner = ControllerOwner::kObstacleRecovery;
    reason = ArbitrationReason::kReactiveObstacleRecovery;
    out.yaw_delta_deg = recovery_dec.yawDelta;
    out.pitch_delta_deg = 0.0;
    out.forward = recovery_dec.forward;
    out.strafe = 0.0;
    out.fire = false;
  }

  if (trace != nullptr) {
    trace->owner = owner;
    trace->arb_reason = reason;
    trace->obstacle_recovery_active = recovery_dec.active;
    std::snprintf(trace->summary, sizeof(trace->summary),
                  "owner=%s(%s) tgt=%d(vis=%d) goal=%d(%s:%s) nav=%s exp=%d/%d",
                  ControllerOwnerName(owner), ArbitrationReasonName(reason),
                  trace->combat_target, trace->combat_target_visible ? 1 : 0,
                  trace->item_goal_id,
                  itemai::ItemActionName(trace->item_action),
                  itemai::ItemReasonName(trace->item_reason),
                  itemai::NavStatusName(trace->nav_status),
                  trace->expansions_used, trace->expansion_limit);
  }
  return out;
}

}  // namespace navbridge

#endif  // NAV_ITEM_BRIDGE_BRIDGE_ARBITRATOR_H
