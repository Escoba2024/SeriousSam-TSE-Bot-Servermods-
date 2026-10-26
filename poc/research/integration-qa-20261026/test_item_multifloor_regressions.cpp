// SPDX-License-Identifier: GPL-2.0-only
// Reproducible C++17 QA regressions for Navigation 2.0 (PR #54), Item-Utility
// (PR #55), Combat 2.0 (PR #66), and Nav-Item-Bridge (PR #69).
//
// IMPORTANT: Pure offline simulation / contract harness.
// Native Retail 1.07 runtime status: NOT_TESTED_RETAIL.

#include <cmath>
#include <cstdint>
#include <cstdio>
#include <cstring>

#include "bot_combat.h"
#include "bot_loadout.h"
#include "bot_profile.h"

namespace {

int g_passed = 0;
int g_failed = 0;

void Check(bool cond, const char* id, const char* detail) {
  if (cond) {
    ++g_passed;
    std::printf("[PASS] %-54s | %s\n", id, detail);
  } else {
    ++g_failed;
    std::printf("[FAIL] %-54s | %s\n", id, detail);
  }
}

struct Node3D {
  double x, y, z;
};

// Exact PR #54 nav_graph.h:161-185 NearestNode (2D XZ planar only!) vs
// floor-aware 3D NearestNode.
int NearestNodePlanarBuggy(const Node3D* nodes, int count, double x, double z) {
  int best = -1;
  double best_d2 = 0.0;
  for (int i = 0; i < count; ++i) {
    const double dx = nodes[i].x - x;
    const double dz = nodes[i].z - z;
    const double d2 = dx * dx + dz * dz;
    if (best < 0 || d2 < best_d2) {
      best = i;
      best_d2 = d2;
    }
  }
  return best;
}

int NearestNodeFloorAwareFixed(const Node3D* nodes, int count, double x,
                               double y, double z, double max_dy = 2.5) {
  int best = -1;
  double best_d2 = 0.0;
  for (int i = 0; i < count; ++i) {
    const double dy = std::fabs(nodes[i].y - y);
    if (dy > max_dy) continue;
    const double dx = nodes[i].x - x;
    const double dz = nodes[i].z - z;
    const double d2 = dx * dx + dz * dz + 4.0 * dy * dy;
    if (best < 0 || d2 < best_d2) {
      best = i;
      best_d2 = d2;
    }
  }
  return best;
}

// QA-03: Stacked 2-story arena (e.g. Red Station lower floor y=0, upper gallery
// y=8m directly overhead). Planar NearestNode maps BOTH bot (10,0,10) and upper
// Rocket Launcher (10,8,10) to n0=(10,0,10), skipping ramp detour A*!
void TestR09_MultiFloorPlanarNearestNodeDeadlock() {
  // n0=(10,0,10) ground room, n1..n3 ramp of length 44m up to n4=(10,8,10) gallery!
  const Node3D nodes[5] = {
      {10.0, 0.0, 10.0},  // 0: ground floor under gallery
      {26.0, 2.0, 10.0},  // 1: ramp bottom
      {26.0, 6.0, 22.0},  // 2: ramp mid
      {10.0, 8.0, 22.0},  // 3: upper corridor
      {10.0, 8.0, 10.0},  // 4: upper gallery directly above node 0!
  };
  const Node3D bot = {10.0, 0.0, 10.0};
  const Node3D upper_item = {10.0, 8.0, 10.0};

  // Buggy PR #54/#69: NearestNode(10, 10) returns node 0 for BOTH (d2=0 == d2=0,
  // tie broken by strict `<` in favour of lower index 0)!
  const int buggy_bot_n = NearestNodePlanarBuggy(nodes, 5, bot.x, bot.z);
  const int buggy_item_n = NearestNodePlanarBuggy(nodes, 5, upper_item.x, upper_item.z);
  // nav_cost_cache.h:896: if (bot_node == item_node) effective_path_m = 3D snap dist = 8.0m!
  const double buggy_eff_m = (buggy_bot_n == buggy_item_n) ? 8.0 : 44.0;
  // nav_goal_sink.h:606 finishes 1-node route on tick 1 via 2D PlanarDistXZ <= 1.25m,
  // while Poll() checks 3D dist(bot, upper_item) == 8.0m <= 1.5m -> NEVER ARRIVES!
  const double planar_dist_at_n0 = 0.0;
  const double dist3d_at_n0 = 8.0;
  const bool buggy_route_finished_under_ceiling =
      (planar_dist_at_n0 <= 1.25) && (dist3d_at_n0 > 1.5);

  const int fixed_bot_n = NearestNodeFloorAwareFixed(nodes, 5, bot.x, bot.y, bot.z);
  const int fixed_item_n =
      NearestNodeFloorAwareFixed(nodes, 5, upper_item.x, upper_item.y, upper_item.z);

  char detail[192];
  std::snprintf(
      detail, sizeof(detail),
      "buggy_nodes=(%d,%d)->eff=%.0fm(deadlock=%d) fixed_nodes=(%d,%d)->ramp_A*",
      buggy_bot_n, buggy_item_n, buggy_eff_m,
      buggy_route_finished_under_ceiling ? 1 : 0, fixed_bot_n, fixed_item_n);
  Check(buggy_bot_n == 0 && buggy_item_n == 0 &&
            buggy_route_finished_under_ceiling && fixed_bot_n == 0 &&
            fixed_item_n == 4,
        "R09_MultiFloorPlanarNearestNodeDeadlock (QA-03)", detail);
}

// QA-04a: Serious Sam TSE Overheal (Pill +1 / Super Health +100 -> up to 200 HP)
// and Overarmor (Shard +1 / Strong Armor -> up to 200 Armor):
// 1. At 100/100 HP, HealthNeed returns 0.0 even for Super Health (+100 -> 200 HP).
// 2. At 101..200 HP (after 1 Health Pill!) with max_health=100, ValidateWorld
//    rejects the ENTIRE world with ValidationError::kBadSelf (s.health > s.max_health)!
void TestR10_OverhealAndOverarmorTriggerInvalidWorldAbort() {
  // Exact predicate from PR #55 item_snapshot.h:187-190:
  auto validate_self_pr55 = [](double hp, double max_hp, double ar, double max_ar) {
    return !(max_hp <= 0.0 || max_ar < 0.0 || hp < 0.0 || hp > max_hp ||
             ar < 0.0 || ar > max_ar);
  };
  // Exact HealthNeed from PR #55 item_scoring.h:138-145:
  auto health_need_pr55 = [](double hp, double max_hp) {
    const double hf = hp / max_hp;
    return (hf >= 0.98) ? 0.0 : (1.0 - hf) * 0.75;
  };

  // Bot at 100/100 HP sees MegaHealth (+100 overheal):
  const double megahealth_need_at_100hp = health_need_pr55(100.0, 100.0);
  // Bot walks over a +1 HP Health Pill -> 101 HP while BotDriver.cpp:912 passes max_health=100:
  const bool world_valid_at_101hp = validate_self_pr55(101.0, 100.0, 0.0, 100.0);
  // Bot picks up Red/Super Armor -> 200 Armor while max_armor=100:
  const bool world_valid_at_200ar = validate_self_pr55(100.0, 100.0, 200.0, 100.0);

  // Fixed TSE contract separates base_max (100) from top_max (200):
  const bool fixed_valid_at_150hp_200ar =
      (150.0 >= 0.0 && 150.0 <= 200.0 && 200.0 >= 0.0 && 200.0 <= 200.0);

  char detail[192];
  std::snprintf(
      detail, sizeof(detail),
      "mega_need@100hp=%.2f valid@101hp=%d valid@200armor=%d fixed_valid=%d",
      megahealth_need_at_100hp, world_valid_at_101hp ? 1 : 0,
      world_valid_at_200ar ? 1 : 0, fixed_valid_at_150hp_200ar ? 1 : 0);
  Check(megahealth_need_at_100hp == 0.0 && !world_valid_at_101hp &&
            !world_valid_at_200ar && fixed_valid_at_150hp_200ar,
        "R10_OverhealAndOverarmorTriggerInvalidWorldAbort (QA-04a)", detail);
}

// QA-04b/c: Colt/Double Colt infinite reserve + Double Shotgun 2-shell rule
// mismatch between bot_combat.h (Retail TSE truth) and PR #55/#69 item_weapons.h.
void TestR11_ColtInfiniteReserveAndDoubleShotgunTwoShellContract() {
  // Spawn state in TSE Deathmatch: Knife(1) + Colt(2) + DoubleShotgun(5) with ONLY 1 shell!
  const uint32_t owned = (1u << 0) | (1u << 1) | (1u << 4);
  const botcore::AmmoInfo ammo_tse = {/*bullets=*/0, /*shells=*/1, 0, 0, 0};

  // Authoritative bot_combat.h:8-16:
  // - Colt (bit 1) STAYS usable with 0 reserve!
  // - Double Shotgun (bit 4) is CLEARED because shells == 1 < 2!
  const uint32_t retail_usable = botcore::CombatUsableWeapons(owned, ammo_tse);

  // PR #55 item_weapons.h:40-73 & PR #69 nav_item_bridge.h:252-259:
  // ammo_cap[2]=50 (Colt needs ammo[2]>0!) and WeaponHasAmmo(5) checks ammo[5]>0 (1>0 == true!)
  int itemai_ammo[15] = {0};
  itemai_ammo[2] = 0;  // no finite Colt reserve exists in TSE
  itemai_ammo[5] = 1;  // 1 shell
  const int itemai_cap[15] = {0, 0, 50, 50, 30, 30, 100, 200, 10, 10, 0, 100, 50, 20, 15};
  uint32_t bridge_usable = 0;
  for (int w = 1; w <= 14; ++w) {
    if ((owned & (1u << (w - 1))) == 0) continue;
    const bool has_ammo = (itemai_cap[w] == 0) || (itemai_ammo[w] > 0);
    if (has_ammo) bridge_usable |= (1u << (w - 1));
  }

  const bool retail_colt_ok = (retail_usable & (1u << 1)) != 0;
  const bool retail_dshot_blocked = (retail_usable & (1u << 4)) == 0;
  const bool bridge_colt_wrongly_blocked = (bridge_usable & (1u << 1)) == 0;
  const bool bridge_dshot_wrongly_allowed = (bridge_usable & (1u << 4)) != 0;

  char detail[192];
  std::snprintf(detail, sizeof(detail),
                "Retail(Colt=%d,DShot@1sh=%d) vs PR55_69(Colt=%d,DShot@1sh=%d)",
                retail_colt_ok ? 1 : 0, retail_dshot_blocked ? 0 : 1,
                bridge_colt_wrongly_blocked ? 0 : 1,
                bridge_dshot_wrongly_allowed ? 1 : 0);
  Check(retail_colt_ok && retail_dshot_blocked &&
            bridge_colt_wrongly_blocked && bridge_dshot_wrongly_allowed,
        "R11_ColtInfiniteReserveAndDoubleShotgunTwoShell (QA-04b/c)", detail);
}

// QA-04d: Shared m_iBullets pool in TSE (cap 500 for BOTH Tommygun=6 and Minigun=7)
// vs PR #55 per-weapon caps (Tommygun=100, Minigun=200). At 100 bullets, a
// standard Bullets pickup tagged weapon_index=6 gets AmmoNeed == 0.0!
void TestR12_SharedBulletsPoolCapMismatchBlocksMinigunRefill() {
  const int shared_bullets = 100;
  const int pr55_tommy_cap = 100;
  const int pr55_minigun_cap = 200;
  const int tse_shared_bullets_cap = 500;

  // PR #55 item_scoring.h:162-163: fill = current / cap; if (fill >= 0.98) return 0.0;
  const double pr55_tommy_fill = static_cast<double>(shared_bullets) / pr55_tommy_cap;
  const double pr55_bullets_pack_need = (pr55_tommy_fill >= 0.98) ? 0.0 : (1.0 - pr55_tommy_fill);
  const double pr55_minigun_fill = static_cast<double>(shared_bullets) / pr55_minigun_cap;
  const double fixed_shared_fill = static_cast<double>(shared_bullets) / tse_shared_bullets_cap;
  const double fixed_bullets_pack_need = 1.0 - fixed_shared_fill;

  char detail[192];
  std::snprintf(
      detail, sizeof(detail),
      "100_bullets: PR55_AmmoNeed(6)=%.2f(minigun_fill=%.2f) Fixed_PoolNeed=%.2f",
      pr55_bullets_pack_need, pr55_minigun_fill, fixed_bullets_pack_need);
  Check(pr55_bullets_pack_need == 0.0 && pr55_minigun_fill == 0.50 &&
            fixed_bullets_pack_need == 0.80,
        "R12_SharedBulletsPoolCapMismatchBlocksMinigun (QA-04d)", detail);
}

// QA-13d: PR #55 item_scoring.h:32 documents `travel / planning_horizon`, but
// line 288 divides by `c.tuning.memory_horizon_s` (constant across skill tiers!),
// collapsing tier differentiation in TimeFactor.
void TestR13_TimeFactorUsesMemoryHorizonInsteadOfPlanningHorizon() {
  const double travel_s = 7.0;
  const double time_weight = 0.55;
  const double memory_horizon_s = 12.0;  // identical across Tier 1 and Tier 5!
  const double tier1_planning_s = 4.5;
  const double tier5_planning_s = 14.0;

  auto clamp01 = [](double v) { return v < 0.0 ? 0.0 : (v > 1.0 ? 1.0 : v); };
  const double buggy_t1 = 1.0 - time_weight * clamp01(travel_s / memory_horizon_s);
  const double buggy_t5 = 1.0 - time_weight * clamp01(travel_s / memory_horizon_s);
  const double fixed_t1 = 1.0 - time_weight * clamp01(travel_s / tier1_planning_s);
  const double fixed_t5 = 1.0 - time_weight * clamp01(travel_s / tier5_planning_s);

  char detail[192];
  std::snprintf(detail, sizeof(detail),
                "buggy(T1=%.3f == T5=%.3f) vs fixed(T1=%.3f != T5=%.3f)",
                buggy_t1, buggy_t5, fixed_t1, fixed_t5);
  Check(std::fabs(buggy_t1 - buggy_t5) < 1e-12 &&
            std::fabs(fixed_t5 - fixed_t1) > 0.20,
        "R13_TimeFactorUsesMemoryHorizonNotPlanningHorizon (QA-13d)", detail);
}

// QA-07: PR #69 WorldPathEnricher caps probes at max_cost_probes_per_tick = 8
// (nav_cost_cache.h:70, 913). Unprobed item #9 (5m behind a solid wall, true
// detour 65m or unreachable) keeps raw 5m Euclidean pos & reachable=true!
void TestR14_UnprobedItemsBeyond8ProbeCapDefaultToEuclideanReachable() {
  const int max_probes = 8;
  double effective_dist_m[10]{};
  bool reachable[10]{};
  // Items 0..7 are open 14m pickups; Item 8 is open 12m; Item 9 is 5m Euclidean
  // behind an unreachable wall (true graph unreachable!).
  int probes_used = 0;
  for (int i = 0; i < 10; ++i) {
    const double euclid_m = (i == 9) ? 5.0 : ((i == 8) ? 12.0 : 14.0);
    if (probes_used < max_probes) {
      ++probes_used;
      effective_dist_m[i] = euclid_m;  // verified A* distance
      reachable[i] = true;
    } else {
      // Exact PR #69 nav_cost_cache.h:849, 913-918 fallback when probe cap hit:
      effective_dist_m[i] = euclid_m;
      reachable[i] = true;
    }
  }
  // Item 9 (unprobed walled trap at 5m Euclidean) beats verified Item 8 (12m)!
  int best_idx = -1;
  double best_dist = 1e9;
  for (int i = 0; i < 10; ++i) {
    if (reachable[i] && effective_dist_m[i] < best_dist) {
      best_dist = effective_dist_m[i];
      best_idx = i;
    }
  }
  char detail[192];
  std::snprintf(detail, sizeof(detail),
                "probes_used=%d/8 -> item9(walled_5m) reachable=%d chosen_idx=%d(expect_trap=9)",
                probes_used, reachable[9] ? 1 : 0, best_idx);
  Check(best_idx == 9 && reachable[9],
        "R14_UnprobedItemsBeyond8CapWinViaEuclideanTrap (QA-07)", detail);
}

// QA-08: PR #69 StepPatrolOrReposition uses patrol_agent_ (which ignores
// local_blocked_!) when Remaining >= 256, and switches to budgeted_patrol_route_
// (which drops kReposition!) when Remaining < 256.
void TestR15_DualPatrolSplitAndLocalBlockedBypass() {
  const int max_expansions = 512;
  // Tick 1 (cache miss): enricher spends 256 expansions, GoalSink Submit spends
  // 20 expansions on a rejected goal -> remaining = 236 < 256 -> budgeted branch!
  const int rem_tick1 = max_expansions - 256 - 20;
  // Tick 2 (cache hit): enricher spends 0 expansions -> remaining = 512 >= 256 ->
  // patrol_agent_ branch (different route state + ignores local_blocked_)!
  const int rem_tick2 = max_expansions - 0;

  const bool tick1_uses_budgeted_patrol = (rem_tick1 < 256);
  const bool tick2_uses_nav_agent_ignoring_local_blocked = (rem_tick2 >= 256);

  char detail[192];
  std::snprintf(detail, sizeof(detail),
                "tick1_rem=%d(<256:budgeted_patrol) tick2_rem=%d(>=256:patrol_agent_no_local_block)",
                rem_tick1, rem_tick2);
  Check(tick1_uses_budgeted_patrol && tick2_uses_nav_agent_ignoring_local_blocked,
        "R15_DualPatrolSplitAndLocalBlockedBypass (QA-08)", detail);
}

// QA-09: Architectural contradiction between PR #55/#69 weapon valuation
// (`botcore::ScoreWeapon` / `StandInWeaponScore`) and PR #66 (`ScoreWeapon2` +
// `PlanRespawn` persona leak into capability timing).
void TestR16_Combat2VsItemScoringDisagreementAndPersonaLeak() {
  // At 40m neutral persona (range_pref=0), owned={Laser(12), Sniper(13)}:
  const double laser_v1 = botcore::ScoreWeapon(12, 40.0, 0.0);
  const double sniper_v1 = botcore::ScoreWeapon(13, 40.0, 0.0);
  const int item_layer_best_40m = (laser_v1 >= sniper_v1) ? 12 : 13;

  // PR #66 combat2_weapon.h CurveAt(12)={opt=22,sigma=16,dps=4.3},
  // CurveAt(13)={opt=48,sigma=22,dps=5.4}, Tier 5 WeaponSkillFactor(13)=1.05:
  auto bell = [](double d, double opt, double sig) {
    const double z = (d - opt) / sig;
    return std::exp(-0.5 * z * z);
  };
  const double laser_v2 = 4.3 * bell(40.0, 22.0, 16.0) * 1.00;
  const double sniper_v2 = 5.4 * bell(40.0, 48.0, 22.0) * 1.05;
  const int combat2_best_40m = (sniper_v2 > laser_v2) ? 13 : 12;

  // PR #66 combat2_tactics.h:279-280 PlanRespawn modifies press_delay_ticks by
  // persona (+4 survivor, -2 aggressor), violating C02 skill/persona orthogonality!
  const int tier3_aggressor_press = 15 - 2;
  const int tier3_survivor_press = 15 + 4;

  char detail[192];
  std::snprintf(detail, sizeof(detail),
                "40m_best: ItemLayer=%d(Laser=%.2f>Sniper=%.2f) vs Combat2=%d(Sniper=%.2f>Laser=%.2f) | Respawn(T3): agg=%d!=surv=%d",
                item_layer_best_40m, laser_v1, sniper_v1,
                combat2_best_40m, sniper_v2, laser_v2, tier3_aggressor_press,
                tier3_survivor_press);
  Check(item_layer_best_40m == 12 && combat2_best_40m == 13 &&
            tier3_aggressor_press != tier3_survivor_press,
        "R16_Combat2VsItemScoringDisagreementAndPersonaLeak (QA-09)", detail);
}

// QA-14: PR #69 test_multibot_competition.cpp M02 XORs identical per-tick struct
// hashes 50 (even!) times (`hash ^= h`), cancelling X ^ X == 0 back to the raw
// FNV-1a offset basis 0xcbf29ce484222325 and hashing uninitialized padding bytes!
void TestR17_VacuousEvenTickXorHashAndPaddingProof() {
  struct PaddedIntentMirror {
    double move_forward;
    double move_strafe;
    double yaw_delta_deg;
    double pitch_delta_deg;
    int weapon;
    bool fire;
    bool jump;
    bool crouch;
    // Compiler inserts 1 trailing padding byte on 32/64-bit ABI!
  };
  const size_t raw_fields = 4 * sizeof(double) + sizeof(int) + 3 * sizeof(bool);
  const bool has_uninitialized_padding = sizeof(PaddedIntentMirror) > raw_fields;

  const uint64_t fnv_basis = 14695981039346656037ULL;  // 0xcbf29ce484222325
  uint64_t forward_order_xor = fnv_basis;
  uint64_t reverse_order_xor = fnv_basis;

  // Suppose forward order produces intent hash 0x1111... while reverse order
  // produces COMPLETELY DIFFERENT intent hash 0x9999... on all 50 ticks!
  for (int t = 1; t <= 50; ++t) {
    forward_order_xor ^= 0x1111222233334444ULL;
    reverse_order_xor ^= 0x9999AAAABBBBCCCCULL;
  }
  const bool false_pass_collision =
      (forward_order_xor == reverse_order_xor) &&
      (forward_order_xor == fnv_basis);

  char detail[192];
  std::snprintf(detail, sizeof(detail),
                "sizeof=%zu>fields=%zu(pad=%d) 50x_XOR: fwd=0x%016llx == rev=0x%016llx (FALSE PASS!)",
                sizeof(PaddedIntentMirror), raw_fields,
                has_uninitialized_padding ? 1 : 0,
                static_cast<unsigned long long>(forward_order_xor),
                static_cast<unsigned long long>(reverse_order_xor));
  Check(has_uninitialized_padding && false_pass_collision,
        "R17_VacuousEvenTickXorHashAndPaddingProof (QA-14)", detail);
}

}  // namespace

int main() {
  std::printf("=== integration-qa-20261026: Item, Multi-Floor & Cross-PR Regressions ===\n");
  TestR09_MultiFloorPlanarNearestNodeDeadlock();
  TestR10_OverhealAndOverarmorTriggerInvalidWorldAbort();
  TestR11_ColtInfiniteReserveAndDoubleShotgunTwoShellContract();
  TestR12_SharedBulletsPoolCapMismatchBlocksMinigunRefill();
  TestR13_TimeFactorUsesMemoryHorizonInsteadOfPlanningHorizon();
  TestR14_UnprobedItemsBeyond8ProbeCapDefaultToEuclideanReachable();
  TestR15_DualPatrolSplitAndLocalBlockedBypass();
  TestR16_Combat2VsItemScoringDisagreementAndPersonaLeak();
  TestR17_VacuousEvenTickXorHashAndPaddingProof();
  std::printf("=== SUMMARY: %d passed, %d failed (NOT_TESTED_RETAIL) ===\n",
              g_passed, g_failed);
  return g_failed == 0 ? 0 : 1;
}
