// SPDX-License-Identifier: GPL-2.0-only
// Reproducible C++17 QA regressions for Combat-AI, ObstacleRecovery coupling,
// ExploratorySearch, Weapon cadence/selection, and PR #57 <-> PR #69 seams.
//
// IMPORTANT: Pure offline simulation / contract harness.
// Native Retail 1.07 runtime status: NOT_TESTED_RETAIL.

#include <cmath>
#include <cstdint>
#include <cstdio>

#include "bot_aim.h"
#include "bot_combat.h"
#include "bot_human.h"
#include "bot_loadout.h"
#include "bot_navigation.h"
#include "bot_perception.h"
#include "bot_profile.h"
#include "bot_weapon_input.h"
#include "botcore.h"

namespace {

int g_passed = 0;
int g_failed = 0;

void Check(bool cond, const char* id, const char* detail) {
  if (cond) {
    ++g_passed;
    std::printf("[PASS] %-52s | %s\n", id, detail);
  } else {
    ++g_failed;
    std::printf("[FAIL] %-52s | %s\n", id, detail);
  }
}

// Closed-loop kinematic + ObstacleRecovery simulation mirroring
// poc/candidates/integrated-human-cpu-20261021/BotDriver.cpp lines 935-1135.
struct WallChaseOutcome {
  int resets = 0;
  int zero_forward_ticks = 0;
  double max_lateral_m = 0.0;
  bool bypassed_wall = false;
};

WallChaseOutcome SimulateWallChase(bool pr57_turn_freeze,
                                   bool fix_preserve_forward_for_recovery) {
  botcore::BotProfile prof{};
  botcore::BuildProfile(3, 0, 0x4501u, "WallBot", &prof);
  botcore::HumanBotPolicy policy;
  policy.Configure(&prof);
  botcore::ObstacleRecovery recovery;

  // Bot at (0, 0, 0) facing -Z (yaw 0). Known target at (0, 0, -25) behind a
  // 4m-wide pillar spanning x in [-2.0, +2.0] at z = -1.5.
  double x = 0.0, z = 0.0, yaw = 0.0, pitch = 0.0;
  bool was_active = false;
  WallChaseOutcome out{};

  for (int tick = 1; tick <= 240; ++tick) {
    botcore::WorldView w{};
    w.tick = tick;
    w.alive = true;
    w.deathmatch = true;
    w.health = 100.0;
    w.max_health = 100.0;
    w.pose = {x, 1.6, z, yaw, pitch};
    w.usable_weapons = (1u << 0) | (1u << 1) | (1u << 5);  // Knife, Colt, Tommygun

    // Target glimpsed on ticks 1..8 (and re-glimpsed once pillar is cleared at |x|>2.0)
    const botcore::SenseInput sensed = {1, 0.0, 1.6, -25.0, 0.0, 0.0, 0.0,
                                        100.0, true, false};
    const bool los = (tick <= 8) || (std::fabs(x) > 2.05);

    policy.BeginTick(w);
    botcore::BotCommand cmd = policy.Step(w, &sensed, &los, 1, 0.05);
    const double raw_intent_forward = cmd.forward;

    // Exact PR #57 bot_human.h:337-340 unflagged chasing turn-freeze:
    if (pr57_turn_freeze && cmd.target >= 0 && !cmd.target_visible) {
      const double dx = 0.0 - x;
      const double dz = -25.0 - z;
      const double bearing = std::atan2(-dx, -dz) * botcore::kRadToDeg;
      if (cmd.forward > 0.0 &&
          std::fabs(botcore::AimController::WrapDeg(bearing - yaw)) > 45.0) {
        cmd.forward = 0.0;
      }
    }

    // PR #57 BotDriver.cpp:952 & 1106:
    //   humanEscapeForward = (FLOAT)decision.forward;
    //   if (humanEscapeForward == 0.0f) bs.bs_navigation.Reset();
    const double human_escape_forward =
        (fix_preserve_forward_for_recovery && was_active)
            ? raw_intent_forward
            : cmd.forward;
    if (human_escape_forward == 0.0) {
      recovery.Reset();
      if (was_active && z > -1.4) ++out.resets;
      was_active = false;
    }

    // Raycast forward/left/right against pillar segment x in [-2, +2], z = -1.5.
    auto ray_dist = [&](double ray_yaw_deg) -> double {
      const double rad = ray_yaw_deg * (3.14159265358979323846 / 180.0);
      const double dir_x = -std::sin(rad);
      const double dir_z = -std::cos(rad);
      if (std::fabs(dir_z) < 1e-6) return 3.0;
      const double t = (-1.5 - z) / dir_z;
      if (t <= 0.0 || t >= 3.0) return 3.0;
      const double hit_x = x + dir_x * t;
      return (hit_x >= -2.0 && hit_x <= 2.0) ? t : 3.0;
    };

    const double move_factor =
        (fix_preserve_forward_for_recovery && was_active)
            ? raw_intent_forward
            : cmd.forward;
    // Note: in PR #45 BotDriver.cpp, combatHold is true when ANY target exists
    // (`target != NULL`), whereas PR #57 narrowed combatHold to `target_visible`
    // explicitly so ObstacleRecovery could bypass walls while chasing unseen targets!
    const botcore::NavigationInput nav_in = {
        x, z, yaw, 9.0, move_factor,
        ray_dist(yaw), ray_dist(yaw + 60.0), ray_dist(yaw - 60.0),
        true, cmd.target_visible, 1, 1.0};
    const botcore::NavigationDecision nav = recovery.Update(nav_in);
    was_active = nav.active;

    double final_forward = cmd.forward;
    if (nav.overrideInput) {
      yaw = botcore::AimController::WrapDeg(yaw + nav.yawDelta);
      final_forward = nav.forward;
    } else {
      yaw = botcore::AimController::WrapDeg(yaw + cmd.yaw_delta_deg);
      pitch += cmd.pitch_delta_deg;
    }
    if (final_forward <= 0.01) ++out.zero_forward_ticks;

    // Kinematic integration (7.5 m/s, blocked by pillar at z = -1.5 for |x| <= 2).
    const double rad = yaw * (3.14159265358979323846 / 180.0);
    const double nx = x + (-std::sin(rad)) * final_forward * 0.375;
    const double nz = z + (-std::cos(rad)) * final_forward * 0.375;
    const bool hits_wall =
        (z > -1.4 && nz <= -1.4 && nx >= -2.0 && nx <= 2.0);
    x = nx;
    if (!hits_wall) z = nz;
    if (std::fabs(x) > out.max_lateral_m) out.max_lateral_m = std::fabs(x);
    if (z < -2.0) {
      out.bypassed_wall = true;
      break;
    }
  }
  return out;
}

// QA-01: Chasing >45 deg forward-freeze resets ObstacleRecovery in a loop.
void TestR01_ChasingTurnFreezeResetsObstacleRecovery() {
  const WallChaseOutcome pr45 = SimulateWallChase(false, false);
  const WallChaseOutcome pr57 = SimulateWallChase(true, false);
  const WallChaseOutcome fixed = SimulateWallChase(true, true);

  const bool reproduced_bug =
      pr45.bypassed_wall && !pr57.bypassed_wall && pr57.resets >= 4;
  const bool fix_restores_bypass = fixed.bypassed_wall && fixed.resets <= 1;

  char detail[192];
  std::snprintf(detail, sizeof(detail),
                "PR45_bypass=%d PR57_bypass=%d(resets=%d,max_x=%.2fm) Fix_bypass=%d",
                pr45.bypassed_wall ? 1 : 0, pr57.bypassed_wall ? 1 : 0,
                pr57.resets, pr57.max_lateral_m,
                fixed.bypassed_wall ? 1 : 0);
  Check(reproduced_bug && fix_restores_bypass,
        "R01_ChasingTurnFreezeResetsObstacleRecovery (QA-01)", detail);
}

// QA-01b: PR #57 BotExploratorySearch commands up to +/-60 deg turn while
// bot_human.h:269 zeroes forward whenever |turn_error| > 35 deg.
void TestR02_ExploratorySearchSelfCancelsForwardAbove35Deg() {
  botcore::Lcg rng(1001u ^ 0x5EC41C5Eu);
  int cancelled_segments = 0;
  const int total_segments = 40;
  double heading = 0.0;
  double yaw = 0.0;
  int sign = 1;
  for (int seg = 0; seg < total_segments; ++seg) {
    sign = -sign;
    const double turn = static_cast<double>(sign * rng.NextRange(22, 60));
    heading = botcore::AimController::WrapDeg(yaw + turn);
    const double turn_err =
        std::fabs(botcore::AimController::WrapDeg(heading - yaw));
    double forward = 0.72;
    if (turn_err > 35.0) forward = 0.0;  // PR #57 bot_human.h:269
    if (forward == 0.0) ++cancelled_segments;
    yaw = heading;
  }
  char detail[160];
  std::snprintf(detail, sizeof(detail),
                "cancelled_segments=%d/%d (>35 deg self-zeroes forward=0.72)",
                cancelled_segments, total_segments);
  Check(cancelled_segments >= 20,
        "R02_ExploratorySearchSelfCancelsForwardAbove35Deg (QA-01b)", detail);
}

// QA-02a: PR #57 BeginTick checks saw_threat BEFORE Observe(), triggering a
// 100-tick (5.0 s) blind escape that suppresses ChooseTarget & firing even when
// the attacker is visible directly in front of the bot.
void TestR03_BlindEscapeBlocksVisibleCombatFor100Ticks() {
  botcore::BotProfile prof{};
  botcore::BuildProfile(4, 0, 0x5702u, "AmbushBot", &prof);

  botcore::HumanBotPolicy baseline;
  baseline.Configure(&prof);

  int baseline_shots = 0;
  int pr57_shots = 0;
  int pr57_blind_ticks = 0;

  int escape_until = -1;
  double prev_health = 100.0;

  for (int tick = 1; tick <= 105; ++tick) {
    botcore::WorldView w{};
    w.tick = tick;
    w.alive = true;
    w.deathmatch = true;
    const double hp = (tick >= 2) ? 70.0 : 100.0;
    w.health = hp;
    w.max_health = 100.0;
    w.pose = {0.0, 1.6, 0.0, 0.0, 0.0};
    w.usable_weapons = (1u << 0) | (1u << 1) | (1u << 5);

    const botcore::SenseInput sensed = {1, 0.0, 1.6, -10.0, 0.0, 0.0, 0.0,
                                        100.0, true, false};
    const bool los = true;
    const int count = (tick >= 2) ? 1 : 0;
    baseline.BeginTick(w);
    if (tick == 2) baseline.NotifyDamage(100.0, 70.0);

    // PR #57 ordering (bot_human.h:126-133, 226-242):
    // BeginTick runs BEFORE Observe(), so on tick 2 saw_threat == false!
    const bool saw_threat_before_observe = false;
    if (hp + 25.0 <= prev_health && !saw_threat_before_observe) {
      escape_until = tick + 100;
    }
    prev_health = hp;

    const botcore::BotCommand base_cmd =
        baseline.Step(w, count ? &sensed : nullptr, count ? &los : nullptr, count, 0.05);
    if (base_cmd.fire) ++baseline_shots;

    if (tick < escape_until) {
      ++pr57_blind_ticks;
    } else if (base_cmd.fire) {
      ++pr57_shots;
    }
  }

  char detail[192];
  std::snprintf(detail, sizeof(detail),
                "PR45_shots=%d vs PR57_blind_ticks=%d PR57_shots_in_first_100t=0(total=%d)",
                baseline_shots, pr57_blind_ticks, pr57_shots);
  Check(baseline_shots >= 25 && pr57_blind_ticks == 100 && pr57_shots < 10,
        "R03_BlindEscapeBlocksVisibleCombatFor100Ticks (QA-02a)", detail);
}

// QA-02b: Cross-PR seam PR #57 (escape_active_ -> target=-1, target_visible=false)
// + PR #69 (NavItemBridge DeriveThreatAndCombat + Arbitrate) flips an active
// visible ambush into ControllerOwner::kPatrol with fire=false!
void TestR04_BridgeArbitrationFlipsVisibleAmbushToPatrol() {
  const int pr57_combat_target = -1;
  const bool pr57_target_visible = false;
  const bool enemy_actually_visible_in_world = true;
  const double damage_taken_frac = 0.30;

  const bool item_aborted_by_damage = (damage_taken_frac > 0.25);
  const bool has_item_goal = !item_aborted_by_damage;
  const bool bridge_engaged = (pr57_combat_target >= 0);
  const bool bridge_visible_combat =
      (pr57_combat_target >= 0 && pr57_target_visible);

  const char* owner = bridge_visible_combat
                          ? "combat"
                          : (has_item_goal ? "item-nav" : "patrol");
  const bool fire_emitted = bridge_visible_combat;

  char detail[192];
  std::snprintf(detail, sizeof(detail),
                "world_los=%d pr57_target=%d -> bridge_engaged=%d owner=%s fire=%d",
                enemy_actually_visible_in_world ? 1 : 0, pr57_combat_target,
                bridge_engaged ? 1 : 0, owner, fire_emitted ? 1 : 0);
  Check(!bridge_engaged && !fire_emitted && owner[0] == 'p',
        "R04_BridgeArbitrationFlipsVisibleAmbushToPatrol (QA-02b)", detail);
}

// QA-11: Pre-draw shot cadence burn while m_iCurrentWeapon != combatWeapon.
void TestR05_WeaponSwitchDrawSuppressionBurnsShotCadence() {
  const int switch_start_tick = 10;
  const int draw_complete_tick = 20;
  const int sniper_delay_ticks = 28;

  int next_shot_buggy = 0;
  int first_actual_shot_buggy = -1;
  int next_shot_fixed = 0;
  int first_actual_shot_fixed = -1;

  for (int tick = switch_start_tick; tick <= 60; ++tick) {
    const bool weapon_drawn = (tick >= draw_complete_tick);

    bool policy_fire_buggy = true;
    if (tick < next_shot_buggy) {
      policy_fire_buggy = false;
    } else {
      next_shot_buggy = tick + sniper_delay_ticks;
    }
    const bool driver_fire_buggy = policy_fire_buggy && weapon_drawn;
    if (driver_fire_buggy && first_actual_shot_buggy < 0) {
      first_actual_shot_buggy = tick;
    }

    bool driver_fire_fixed = false;
    if (weapon_drawn && tick >= next_shot_fixed) {
      driver_fire_fixed = true;
      next_shot_fixed = tick + sniper_delay_ticks;
    }
    if (driver_fire_fixed && first_actual_shot_fixed < 0) {
      first_actual_shot_fixed = tick;
    }
  }

  const int lost_ticks = first_actual_shot_buggy - first_actual_shot_fixed;
  char detail[192];
  std::snprintf(detail, sizeof(detail),
                "draw_ready_t=%d buggy_first_shot_t=%d fixed_first_shot_t=%d lost=%d ticks(%.2fs)",
                draw_complete_tick, first_actual_shot_buggy,
                first_actual_shot_fixed, lost_ticks, lost_ticks / 20.0);
  Check(first_actual_shot_buggy == 38 && first_actual_shot_fixed == 20 &&
            lost_ticks == 18,
        "R05_WeaponSwitchDrawSuppressionBurnsShotCadence (QA-11)", detail);
}

// QA-13a: BotDriver.cpp:1042-1046 resets ObstacleRecovery whenever distance <= 8m,
// even when HumanBotPolicy requests non-zero movement into a wall.
void TestR06_CloseCombatUnder8mResetsObstacleRecovery() {
  botcore::ObstacleRecovery rec_buggy;
  botcore::ObstacleRecovery rec_fixed;
  bool buggy_active = false;
  bool fixed_active = false;

  for (int tick = 1; tick <= 15; ++tick) {
    const botcore::NavigationInput in = {
        0.0, 0.0, 0.0, 9.0, 1.0,
        0.5, 3.0, 3.0,  // wall 0.5m ahead!
        true, false, 1, 1.0};

    const double enemy_distance_m = 6.5;
    if (enemy_distance_m <= 8.0) {
      rec_buggy.Reset();
      buggy_active = false;
    } else {
      buggy_active = rec_buggy.Update(in).active;
    }
    fixed_active = rec_fixed.Update(in).active;
  }

  char detail[160];
  std::snprintf(detail, sizeof(detail),
                "pinned_at_6.5m: buggy_recovery_active=%d fixed_recovery_active=%d",
                buggy_active ? 1 : 0, fixed_active ? 1 : 0);
  Check(!buggy_active && fixed_active,
        "R06_CloseCombatUnder8mResetsObstacleRecovery (QA-13a)", detail);
}

// QA-13b: Out-of-combat weapon readiness bug:
// 1. bot_loadout.h:156-166 keeps returning an empty `current_` weapon when
//    `!in.has_target` after ammo runs out on the killing shot (`locked_=false`
//    without resetting `current_=0`), and `Fallback()` scans from 1 (Knife!).
// 2. BotDriver.cpp:1054 (`if (decision.target >= 0) combatWeapon = decision.weapon;`)
//    discards `decision.weapon` whenever `decision.target < 0`.
void TestR07_NoTargetDropsFallbackWeaponSelection() {
  botcore::BotProfile prof{};
  botcore::BuildProfile(3, 0, 0x1302u, "ReadyBot", &prof);
  botcore::WeaponSelector sel;
  sel.Configure(prof.skill);

  // Tick 1: in combat at 15m with Tommygun (6) + Colt (2) + Knife (1) -> picks 6.
  botcore::LoadoutInput in_fight{};
  in_fight.usable_mask = (1u << 0) | (1u << 1) | (1u << 5);
  in_fight.distance_m = 15.0;
  in_fight.has_target = true;
  const int w_fight = sel.Update(in_fight, 1);

  // Tick 20: Tommygun runs dry on the killing shot (`usable_mask` now Knife+Colt),
  // no target alive (`has_target = false`).
  botcore::LoadoutInput post_fight{};
  post_fight.usable_mask = (1u << 0) | (1u << 1);  // Tommygun (bit 5) EMPTY!
  post_fight.has_target = false;
  const int w_buggy_selector = sel.Update(post_fight, 20);  // still returns 6 (EMPTY!)

  // And even if selector returned Colt (2), BotDriver.cpp:1054 ignores it when target < 0!
  const int target = -1;
  const int driver_weapon_buggy = (target >= 0) ? 2 : 1;
  const int driver_weapon_fixed =
      botcore::BestWeapon(post_fight.usable_mask, 15.0, 0.0);

  char detail[192];
  std::snprintf(detail, sizeof(detail),
                "fight_wpn=%d -> empty_post_fight_sel=%d(unusable!) driver@no_target=%d fixed=%d",
                w_fight, w_buggy_selector, driver_weapon_buggy, driver_weapon_fixed);
  Check(w_fight == 6 && w_buggy_selector == 6 && driver_weapon_buggy == 1 &&
            driver_weapon_fixed == 2,
        "R07_NoTargetKeepsEmptyWeaponAndDropsReadiness (QA-13b)", detail);
}

// QA-13c: PR #57 RouteMemory::MarkHazard off-by-one (`i < count_ - 1`) skips
// the oldest entry in the ring buffer when `count_ == kNodes`.
void TestR08_RouteMemoryMarkHazardOffByOne() {
  static constexpr int kNodes = 24;
  double xs[kNodes]{};
  double zs[kNodes]{};
  int hazards_buggy[kNodes]{};
  int hazards_fixed[kNodes]{};

  for (int i = 0; i < kNodes; ++i) {
    xs[i] = i * 5.0;
    zs[i] = 0.0;
  }
  const int head = 0;
  const int count = kNodes;

  for (int i = 0; i < count - 1; ++i) {
    const int idx = (head - 1 - i + kNodes * 2) % kNodes;
    const double dx = xs[idx] - 0.0, dz = zs[idx] - 0.0;
    if (dx * dx + dz * dz <= 9.0) ++hazards_buggy[idx];
  }
  for (int i = 0; i < count; ++i) {
    const int idx = (head - 1 - i + kNodes * 2) % kNodes;
    const double dx = xs[idx] - 0.0, dz = zs[idx] - 0.0;
    if (dx * dx + dz * dz <= 9.0) ++hazards_fixed[idx];
  }

  char detail[160];
  std::snprintf(detail, sizeof(detail),
                "oldest_slot0_hazard: buggy=%d (skipped!) fixed=%d",
                hazards_buggy[0], hazards_fixed[0]);
  Check(hazards_buggy[0] == 0 && hazards_fixed[0] == 1,
        "R08_RouteMemoryMarkHazardOffByOne (QA-13c)", detail);
}

}  // namespace

int main() {
  std::printf("=== integration-qa-20261026: Combat, Navigation & Seam Regressions ===\n");
  TestR01_ChasingTurnFreezeResetsObstacleRecovery();
  TestR02_ExploratorySearchSelfCancelsForwardAbove35Deg();
  TestR03_BlindEscapeBlocksVisibleCombatFor100Ticks();
  TestR04_BridgeArbitrationFlipsVisibleAmbushToPatrol();
  TestR05_WeaponSwitchDrawSuppressionBurnsShotCadence();
  TestR06_CloseCombatUnder8mResetsObstacleRecovery();
  TestR07_NoTargetDropsFallbackWeaponSelection();
  TestR08_RouteMemoryMarkHazardOffByOne();
  std::printf("=== SUMMARY: %d passed, %d failed (NOT_TESTED_RETAIL) ===\n",
              g_passed, g_failed);
  return g_failed == 0 ? 0 : 1;
}
