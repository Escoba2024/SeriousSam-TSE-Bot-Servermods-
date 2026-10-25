// SPDX-License-Identifier: GPL-2.0-only
// test_scenarios_matrix.cpp - automated validation of all 12 mandatory
// Navigation 2.0 + Item-Utility + Combat-KI integration scenarios.
//
// Usage:
//   ./build/test_scenarios_matrix            # verbose scenario traces + checks
//   ./build/test_scenarios_matrix --summary  # compact Markdown-ready summary

#include <cmath>
#include <cstdint>
#include <cstdio>
#include <cstring>

#include "arena_sim.h"

namespace {

struct ScenarioRecord {
  int number;
  const char* id;
  const char* title;
  bool passed;
  char metric[192];
};

ScenarioRecord g_records[16];
int g_record_count = 0;
int g_pass = 0;
int g_fail = 0;
bool g_summary_only = false;

void RecordScenario(int num, const char* id, const char* title, bool ok,
                    const char* metric) {
  if (g_record_count < 16) {
    ScenarioRecord& r = g_records[g_record_count++];
    r.number = num;
    r.id = id;
    r.title = title;
    r.passed = ok;
    std::snprintf(r.metric, sizeof(r.metric), "%s", metric);
  }
  if (ok) {
    ++g_pass;
  } else {
    ++g_fail;
  }
  if (!g_summary_only) {
    std::printf("[%s] S%02d %-34s | %s\n", ok ? "PASS" : "FAIL", num, id,
                metric);
  }
}

uint64_t HashBytes(uint64_t h, const void* ptr, size_t len) {
  const uint8_t* p = static_cast<const uint8_t*>(ptr);
  for (size_t i = 0; i < len; ++i) {
    h ^= static_cast<uint64_t>(p[i]);
    h *= 1099511628211ULL;
  }
  return h;
}

uint64_t HashDouble(uint64_t h, double v) {
  return HashBytes(h, &v, sizeof(v));
}

/* ------------------------------------------------------------------------ */
/* S01: Wenig HP + erreichbares Medkit                                       */
/* ------------------------------------------------------------------------ */
void RunS01_LowHpReachableMedkit() {
  navbridge::ArenaSim sim;
  navlab::NavGraph& g = sim.mutable_graph();
  // L-shaped corridor: (0,0) -> (0,-12) -> (10,-12), wall blocking direct diagonal
  const int n0 = g.AddNode(0.0, 0.0, 0.0);
  const int n1 = g.AddNode(0.0, 0.0, -6.0);
  const int n2 = g.AddNode(0.0, 0.0, -12.0);
  const int n3 = g.AddNode(10.0, 0.0, -12.0);
  const int n4 = g.AddNode(0.0, 0.0, 10.0);
  g.Link(n0, n1);
  g.Link(n1, n2);
  g.Link(n2, n3);
  g.Link(n0, n4);
  sim.AddWall(3.0, 2.0, 3.0, -9.0, 0.4, true, true);

  navbridge::BridgeProfileBundle bundle{};
  navbridge::BuildBridgeProfile(3, 1, 0x101u, 0, "S01Bot", &bundle, 0.0f);
  const int bi = sim.AddBot(bundle, 0.0, 0.0, 0.0);
  sim.bot(bi).health = 22.0;

  // Reachable Medkit +50 at (10,-12), distraction Ammo at (0,10)
  const int med_idx =
      sim.AddItem(101, itemai::ItemKind::kHealth, 10.0, -12.0, 50.0, 0, 0, 400);
  sim.AddItem(102, itemai::ItemKind::kAmmo, 0.0, 10.0, 10.0, 2, 10, 400);

  sim.StepTick();
  const int initial_goal = sim.bot(bi).last_output.item_decision.goal_id;
  const bool nav_owned =
      (sim.bot(bi).last_output.trace.owner ==
       navbridge::ControllerOwner::kItemNavigation);

  int pickup_tick = -1;
  for (int t = 1; t < 120; ++t) {
    sim.StepTick();
    if (sim.item(med_idx).picked_count > 0) {
      pickup_tick = sim.tick();
      break;
    }
  }

  const bool ok = (initial_goal == 101) && nav_owned && (pickup_tick > 0) &&
                  (std::fabs(sim.bot(bi).health - 72.0) < 1e-6);
  char msg[192];
  std::snprintf(msg, sizeof(msg),
                "goal=%d owner=item-nav pickup_tick=%d hp=22->%.0f",
                initial_goal, pickup_tick, sim.bot(bi).health);
  RecordScenario(1, "LowHpReachableMedkit",
                 "Wenig HP + erreichbares Medkit", ok, msg);
}

/* ------------------------------------------------------------------------ */
/* S02: Leere Munition + erreichbares Ammo-Item                              */
/* ------------------------------------------------------------------------ */
void RunS02_EmptyAmmoReachableAmmo() {
  navbridge::ArenaSim sim;
  navlab::NavGraph& g = sim.mutable_graph();
  const int n0 = g.AddNode(0.0, 0.0, 0.0);
  const int n1 = g.AddNode(8.0, 0.0, 0.0);
  const int n2 = g.AddNode(16.0, 0.0, -6.0);
  g.Link(n0, n1);
  g.Link(n1, n2);

  navbridge::BridgeProfileBundle bundle{};
  navbridge::BuildBridgeProfile(3, 0, 0x202u, 0, "S02Bot", &bundle, 0.0f);
  const int bi = sim.AddBot(bundle, 0.0, 0.0, -90.0);
  sim.bot(bi).health = 100.0;
  sim.bot(bi).owned_weapons = (1u << 0) | (1u << 1) | (1u << 7);  // Knife+Colt+RL
  for (int w = 0; w <= itemai::kWeaponCount; ++w) sim.bot(bi).ammo[w] = 0;

  const int ammo_idx =
      sim.AddItem(201, itemai::ItemKind::kAmmo, 16.0, -6.0, 15.0, 8, 5, 400);

  sim.StepTick();
  const int initial_goal = sim.bot(bi).last_output.item_decision.goal_id;

  int pickup_tick = -1;
  for (int t = 1; t < 100; ++t) {
    sim.StepTick();
    if (sim.item(ammo_idx).picked_count > 0) {
      pickup_tick = sim.tick();
      break;
    }
  }
  // Step once more so usable_weapons refreshes with new Rocket ammo.
  sim.StepTick();
  const bool rl_usable = (sim.bot(bi).ammo[8] == 5);

  const bool ok = (initial_goal == 201) && (pickup_tick > 0) && rl_usable;
  char msg[192];
  std::snprintf(msg, sizeof(msg),
                "ammo_starved->goal=%d pickup_tick=%d rockets=0->%d",
                initial_goal, pickup_tick, sim.bot(bi).ammo[8]);
  RecordScenario(2, "EmptyAmmoReachableAmmo",
                 "Leere Munition + erreichbares Ammo-Item", ok, msg);
}

/* ------------------------------------------------------------------------ */
/* S03: Waffe statt unnoetigem Health-Item                                   */
/* ------------------------------------------------------------------------ */
void RunS03_WeaponInsteadOfFullHealth() {
  navbridge::ArenaSim sim;
  navlab::NavGraph& g = sim.mutable_graph();
  const int n0 = g.AddNode(0.0, 0.0, 0.0);
  const int n_med = g.AddNode(3.5, 0.0, 0.0);
  const int n1 = g.AddNode(0.0, 0.0, -9.0);
  const int n_rl = g.AddNode(0.0, 0.0, -18.0);
  g.Link(n0, n_med);
  g.Link(n0, n1);
  g.Link(n1, n_rl);

  navbridge::BridgeProfileBundle bundle{};
  navbridge::BuildBridgeProfile(3, 2, 0x303u, 0, "S03Bot", &bundle, 0.0f);
  const int bi = sim.AddBot(bundle, 0.0, 0.0, 0.0);
  sim.bot(bi).health = 100.0;
  sim.bot(bi).armor = 80.0;

  const int med_idx =
      sim.AddItem(301, itemai::ItemKind::kHealth, 3.5, 0.0, 25.0, 0, 0, 400);
  const int rl_idx =
      sim.AddItem(302, itemai::ItemKind::kWeapon, 0.0, -18.0, 30.0, 8, 5, 400);

  sim.StepTick();
  const int first_goal = sim.bot(bi).last_output.item_decision.goal_id;

  for (int t = 1; t < 90; ++t) {
    sim.StepTick();
    if (sim.item(rl_idx).picked_count > 0) break;
  }

  const bool has_rl = itemai::WeaponOwned(sim.bot(bi).owned_weapons, 8);
  const bool skipped_med = (sim.item(med_idx).picked_count == 0);
  const bool ok = (first_goal == 302) && has_rl && skipped_med;
  char msg[192];
  std::snprintf(msg, sizeof(msg),
                "first_goal=%d (skipped 3.5m Medkit 301=%d) acquired_RL=%d",
                first_goal, sim.item(med_idx).picked_count, has_rl ? 1 : 0);
  RecordScenario(3, "WeaponInsteadOfFullHealth",
                 "Waffe statt unnoetigem Health-Item", ok, msg);
}

/* ------------------------------------------------------------------------ */
/* S04: Gegnerkontakt waehrend Item-Suche                                    */
/* ------------------------------------------------------------------------ */
void RunS04_EnemyContactDuringItemSearch() {
  navbridge::ArenaSim sim;
  navlab::NavGraph& g = sim.mutable_graph();
  const int n0 = g.AddNode(0.0, 0.0, 0.0);
  const int n1 = g.AddNode(0.0, 0.0, -12.0);
  const int n2 = g.AddNode(0.0, 0.0, -24.0);
  g.Link(n0, n1);
  g.Link(n1, n2);

  navbridge::BridgeProfileBundle bundle{};
  navbridge::BuildBridgeProfile(4, 2, 0x404u, 0, "S04Bot", &bundle, 0.0f);
  const int bi = sim.AddBot(bundle, 0.0, 0.0, 0.0);
  sim.bot(bi).health = 95.0;
  sim.bot(bi).armor = 20.0;
  sim.bot(bi).owned_weapons |= (1u << 5);  // Tommygun (weapon 6)
  sim.bot(bi).ammo[6] = 80;
  sim.bot(bi).current_weapon = 6;

  sim.AddItem(401, itemai::ItemKind::kArmor, 0.0, -24.0, 50.0, 0, 0, 400);

  // Enemy initially dead/absent while bot commits to item 401.
  const int ei = sim.AddDummyEnemy(1.5, -16.0, 180.0, 0.0);

  for (int t = 0; t < 12; ++t) sim.StepTick();
  const bool searching_before_contact =
      sim.bot(bi).last_output.item_decision.has_goal &&
      sim.bot(bi).last_output.item_decision.goal_id == 401 &&
      sim.bot(bi).last_output.trace.owner ==
          navbridge::ControllerOwner::kItemNavigation;

  // Enemy appears in clear LOS ~10 m ahead!
  sim.bot(ei).health = 100.0;
  sim.bot(ei).alive = true;

  bool saw_combat_abort = false;
  bool combat_took_owner = false;
  for (int t = 0; t < 35; ++t) {
    sim.StepTick();
    const navbridge::BridgeTickOutput& out = sim.bot(bi).last_output;
    if (out.item_decision.action == itemai::ItemAction::kAbort &&
        (out.item_decision.reason == itemai::ItemReason::kCombatLock ||
         out.item_decision.reason == itemai::ItemReason::kThreatOverride)) {
      saw_combat_abort = true;
    }
    if (out.trace.owner == navbridge::ControllerOwner::kCombat) {
      combat_took_owner = true;
    }
  }

  const bool ok = searching_before_contact && saw_combat_abort &&
                  combat_took_owner && (sim.bot(bi).shots_fired > 0) &&
                  !sim.bot(bi).agent.goal_sink().has_active_goal();
  char msg[192];
  std::snprintf(msg, sizeof(msg),
                "pre_nav=%d abort=%d owner=combat(%d ticks) shots=%d sink_idle=%d",
                searching_before_contact ? 1 : 0, saw_combat_abort ? 1 : 0,
                sim.bot(bi).combat_ticks, sim.bot(bi).shots_fired,
                !sim.bot(bi).agent.goal_sink().has_active_goal() ? 1 : 0);
  RecordScenario(4, "EnemyContactDuringItemSearch",
                 "Gegnerkontakt waehrend Item-Suche", ok, msg);
}

/* ------------------------------------------------------------------------ */
/* S05: Beschuss / Schaden waehrend Navigation (Opportunistic Abort +        */
/*      Critical-HP Survival Retreat Override)                               */
/* ------------------------------------------------------------------------ */
void RunS05_IncomingFireDamageDuringNav() {
  // Part A: Healthy bot (90 HP) pursuing opportunistic Ammo takes heavy sniper
  // burst (-38 HP -> 52 HP, > abort_damage_frac) -> aborts via kDamageAbort!
  navbridge::ArenaSim sim_a;
  navlab::NavGraph& ga = sim_a.mutable_graph();
  ga.Link(ga.AddNode(0.0, 0.0, 0.0), ga.AddNode(0.0, 0.0, -24.0));

  navbridge::BridgeProfileBundle prof_a{};
  navbridge::BuildBridgeProfile(3, 1, 0x505Au, 0, "S05ABot", &prof_a, 0.0f);
  const int ba = sim_a.AddBot(prof_a, 0.0, 0.0, 0.0);
  sim_a.bot(ba).health = 90.0;
  sim_a.bot(ba).ammo[2] = 10;
  sim_a.AddItem(501, itemai::ItemKind::kAmmo, 0.0, -24.0, 20.0, 2, 25, 400);

  for (int t = 0; t < 6; ++t) sim_a.StepTick();
  const bool a_had_goal = (sim_a.bot(ba).last_output.item_decision.goal_id == 501);
  sim_a.InjectDamage(ba, 38.0);  // 38/100 = 0.38 > abort_damage_frac (~0.27)
  sim_a.StepTick();
  const bool a_damage_abort =
      (sim_a.bot(ba).last_output.item_decision.action == itemai::ItemAction::kAbort &&
       sim_a.bot(ba).last_output.item_decision.reason ==
           itemai::ItemReason::kDamageAbort &&
       sim_a.bot(ba).last_output.trace.under_fire);

  // Part B: Critically wounded bot (18 HP) with visible distant enemy (24 m)
  // AND nearby Medkit +50 (8 m): `suppress_combat == true` -> `kSurvivalRetreat`
  // overrides combat so bot retreats to Medkit with `fire == false`!
  navbridge::ArenaSim sim_b;
  navlab::NavGraph& gb = sim_b.mutable_graph();
  const int nb0 = gb.AddNode(0.0, 0.0, 0.0);
  const int nb1 = gb.AddNode(8.0, 0.0, 0.0);
  gb.Link(nb0, nb1);

  navbridge::BridgeProfileBundle prof_b{};
  navbridge::BuildBridgeProfile(4, 1, 0x505Bu, 0, "S05BBot", &prof_b, 0.0f);
  const int bb = sim_b.AddBot(prof_b, 0.0, 0.0, 0.0);
  sim_b.bot(bb).health = 18.0;
  sim_b.AddDummyEnemy(0.0, -24.0, 180.0, 100.0);  // Visible enemy 24 m ahead
  const int med_b =
      sim_b.AddItem(502, itemai::ItemKind::kHealth, 8.0, 0.0, 50.0, 0, 0, 400);

  for (int t = 0; t < 60; ++t) {
    if (t == 8) sim_b.InjectDamage(bb, 2.0);  // Grazing shot while retreating
    sim_b.StepTick();
    if (sim_b.item(med_b).picked_count > 0) break;
  }

  const bool b_retreated_and_healed =
      (sim_b.bot(bb).survival_retreat_ticks > 0) &&
      (sim_b.item(med_b).picked_count == 1) && (sim_b.bot(bb).health >= 65.0);

  const bool ok = a_had_goal && a_damage_abort && b_retreated_and_healed;
  char msg[192];
  std::snprintf(
      msg, sizeof(msg),
      "5A_dmg_abort=%d(under_fire=1) 5B_survival_retreat_ticks=%d healed_hp=%.0f",
      a_damage_abort ? 1 : 0, sim_b.bot(bb).survival_retreat_ticks,
      sim_b.bot(bb).health);
  RecordScenario(5, "IncomingFireDamageDuringNav",
                 "Beschuss / Schaden waehrend Navigation", ok, msg);
}

/* ------------------------------------------------------------------------ */
/* S06: Item ausserhalb erreichbaren Graphen                                 */
/* ------------------------------------------------------------------------ */
void RunS06_UnreachableIslandItem() {
  navbridge::ArenaSim sim;
  navlab::NavGraph& g = sim.mutable_graph();
  // Connected main floor: (0,0) -> (10,0) -> (20,0)
  const int n0 = g.AddNode(0.0, 0.0, 0.0);
  const int n1 = g.AddNode(10.0, 0.0, 0.0);
  const int n2 = g.AddNode(20.0, 0.0, 0.0);
  g.Link(n0, n1);
  g.Link(n1, n2);
  // Disconnected upper island node at (0, 6, -7) - only 7 m away horizontally,
  // but ZERO edges connecting it to n0..n2!
  g.AddNode(0.0, 6.0, -7.0);

  navbridge::BridgeProfileBundle bundle{};
  navbridge::BuildBridgeProfile(4, 0, 0x606u, 0, "S06Bot", &bundle, 0.0f);
  const int bi = sim.AddBot(bundle, 0.0, 0.0, 0.0);

  // Island Rocket Launcher (very high raw score if reachable!) vs reachable
  // Double Shotgun on connected floor at (20, 0).
  const int island_rl =
      sim.AddItem(601, itemai::ItemKind::kWeapon, 0.0, -7.0, 40.0, 8, 5, 400);
  const int floor_sg =
      sim.AddItem(602, itemai::ItemKind::kWeapon, 20.0, 0.0, 25.0, 6, 50, 400);

  sim.StepTick();
  const int first_goal = sim.bot(bi).last_output.item_decision.goal_id;
  const int unreachable_marked_t1 =
      sim.bot(bi).last_output.enrichment.graph_unreachable;

  // Step 2 in same anchor cell: verify 0 A* re-probes (no re-search storm!)
  sim.StepTick();
  const int reprobes_t2 = sim.bot(bi).last_output.enrichment.probes_executed;

  for (int t = 2; t < 95; ++t) {
    sim.StepTick();
    if (sim.item(floor_sg).picked_count > 0) break;
  }

  const bool ok = (first_goal == 602) && (unreachable_marked_t1 >= 1) &&
                  (reprobes_t2 == 0) &&
                  (sim.item(island_rl).picked_count == 0) &&
                  (sim.item(floor_sg).picked_count == 1);
  char msg[192];
  std::snprintf(
      msg, sizeof(msg),
      "rejected_island=601(unreach=%d,t2_reprobes=%d) picked_reachable=602(%d)",
      unreachable_marked_t1, reprobes_t2, sim.item(floor_sg).picked_count);
  RecordScenario(6, "UnreachableIslandItem",
                 "Item ausserhalb erreichbaren Graphen", ok, msg);
}

/* ------------------------------------------------------------------------ */
/* S07: Hindernis und Alternativroute                                        */
/* ------------------------------------------------------------------------ */
void RunS07_ObstacleAndAlternativeRoute() {
  navbridge::ArenaSim sim;
  navlab::NavGraph& g = sim.mutable_graph();
  // Direct corridor (0,0)->(0,-12)->(0,-24) has kEdgeBlocked on (n0,n_mid) +
  // closed steel gate wall. West bypass (0,0)->(-12,0)->(-12,-24)->(0,-24) = 48 m.
  const int n0 = g.AddNode(0.0, 0.0, 0.0);
  const int n_mid = g.AddNode(0.0, 0.0, -12.0);
  const int n_goal = g.AddNode(0.0, 0.0, -24.0);
  const int nw1 = g.AddNode(-12.0, 0.0, 0.0);
  const int nw2 = g.AddNode(-12.0, 0.0, -12.0);
  const int nw3 = g.AddNode(-12.0, 0.0, -24.0);

  g.Link(n0, n_mid, navlab::kEdgeBlocked);  // Closed gate in graph
  g.Link(n_mid, n_goal);
  g.Link(n0, nw1);
  g.Link(nw1, nw2);
  g.Link(nw2, nw3);
  g.Link(nw3, n_goal);
  sim.AddWall(-5.0, -6.0, 5.0, -6.0, 0.45, true, true);  // Physical closed gate

  navbridge::BridgeProfileBundle bundle{};
  navbridge::BuildBridgeProfile(4, 3, 0x707u, 0, "S07Bot", &bundle, 0.0f);
  const int bi = sim.AddBot(bundle, 0.0, 0.0, 0.0);
  sim.bot(bi).armor = 0.0;

  const int armor_idx =
      sim.AddItem(701, itemai::ItemKind::kArmor, 0.0, -24.0, 100.0, 0, 0, 400);

  bool used_west_bypass = false;
  int pickup_tick = -1;
  for (int t = 0; t < 180; ++t) {
    sim.StepTick();
    if (sim.bot(bi).x < -7.5) used_west_bypass = true;
    if (sim.item(armor_idx).picked_count > 0) {
      pickup_tick = sim.tick();
      break;
    }
  }

  const bool ok =
      used_west_bypass && (pickup_tick > 0) && (sim.bot(bi).armor >= 99.0);
  char msg[192];
  std::snprintf(msg, sizeof(msg),
                "bypassed_blocked_gate=1(min_x<-7.5) pickup_tick=%d armor=%.0f",
                pickup_tick, sim.bot(bi).armor);
  RecordScenario(7, "ObstacleAndAlternativeRoute",
                 "Hindernis und Alternativroute", ok, msg);
}

/* ------------------------------------------------------------------------ */
/* S08: Stuck und Neuplanung (Unmapped Wall -> Local Edge Block -> Detour +  */
/*      Full-Blockage Stall Escalation)                                      */
/* ------------------------------------------------------------------------ */
void RunS08_DynamicStuckAndReplan() {
  // Part A: East route (28 m) looks open in NavGraph, but has an unmapped
  // physical barrier at z=-6! West route (44 m) is genuinely open.
  navbridge::ArenaSim sim;
  navlab::NavGraph& g = sim.mutable_graph();
  const int n0 = g.AddNode(0.0, 0.0, 0.0);
  const int ne1 = g.AddNode(4.0, 0.0, 0.0);
  const int ne2 = g.AddNode(4.0, 0.0, -20.0);
  const int n_goal = g.AddNode(0.0, 0.0, -20.0);
  const int nw1 = g.AddNode(-10.0, 0.0, 0.0);
  const int nw2 = g.AddNode(-10.0, 0.0, -20.0);

  g.Link(n0, ne1);
  g.Link(ne1, ne2);  // Unmapped physical wall crosses this edge!
  g.Link(ne2, n_goal);
  g.Link(n0, nw1);
  g.Link(nw1, nw2);
  g.Link(nw2, n_goal);

  // Physical barrier blocking East corridor completely (box-shaped cul-de-sac
  // at z=-6 so sliding cannot sneak around x=4).
  sim.AddWall(-1.0, -6.0, 9.0, -6.0, 0.45, true, true);
  sim.AddWall(-1.0, -2.5, -1.0, -6.2, 0.45, true, false);
  sim.AddWall(9.0, -2.5, 9.0, -6.2, 0.45, true, false);

  navbridge::BridgeProfileBundle bundle{};
  navbridge::BuildBridgeProfile(4, 0, 0x808u, 0, "S08Bot", &bundle, 0.0f);
  const int bi = sim.AddBot(bundle, 0.0, 0.0, 0.0);
  const int rl_idx =
      sim.AddItem(801, itemai::ItemKind::kWeapon, 0.0, -20.0, 35.0, 8, 5, 400);

  bool went_east_first = false;
  bool stuck_replanned = false;
  int pickup_tick = -1;
  for (int t = 0; t < 280; ++t) {
    sim.StepTick();
    if (sim.bot(bi).x > 2.0) went_east_first = true;
    if (sim.bot(bi).last_output.goal_move.stuck &&
        sim.bot(bi).last_output.goal_move.replanned) {
      stuck_replanned = true;
    }
    if (sim.item(rl_idx).picked_count > 0) {
      pickup_tick = sim.tick();
      break;
    }
  }

  // Part B: Single corridor completely walled off -> 2 stall strikes ->
  // ItemPlanner aborts with `ItemReason::kStalled`!
  navbridge::ArenaSim sim_b;
  navlab::NavGraph& gb = sim_b.mutable_graph();
  const int b0 = gb.AddNode(0.0, 0.0, 0.0);
  const int b1 = gb.AddNode(0.0, 0.0, -18.0);
  gb.Link(b0, b1);
  sim_b.AddWall(-6.0, -5.0, 6.0, -5.0, 0.45, true, true);
  sim_b.AddWall(-6.0, 2.0, -6.0, -5.2, 0.45, true, false);
  sim_b.AddWall(6.0, 2.0, 6.0, -5.2, 0.45, true, false);

  const int bb = sim_b.AddBot(bundle, 0.0, 0.0, 0.0);
  sim_b.bot(bb).health = 30.0;
  sim_b.AddItem(802, itemai::ItemKind::kHealth, 0.0, -18.0, 50.0, 0, 0, 400);

  bool saw_stalled_abort = false;
  for (int t = 0; t < 160; ++t) {
    sim_b.StepTick();
    if (sim_b.bot(bb).last_output.item_decision.action ==
            itemai::ItemAction::kAbort &&
        sim_b.bot(bb).last_output.item_decision.reason ==
            itemai::ItemReason::kStalled) {
      saw_stalled_abort = true;
      break;
    }
  }

  const bool ok = went_east_first && stuck_replanned && (pickup_tick > 0) &&
                  saw_stalled_abort;
  char msg[192];
  std::snprintf(
      msg, sizeof(msg),
      "8A_east_trap=%d replan=%d detour_pickup_t=%d | 8B_stalled_abort=%d",
      went_east_first ? 1 : 0, stuck_replanned ? 1 : 0, pickup_tick,
      saw_stalled_abort ? 1 : 0);
  RecordScenario(8, "DynamicStuckAndReplan",
                 "Stuck und Neuplanung", ok, msg);
}

/* ------------------------------------------------------------------------ */
/* S09: Zwei Bots mit demselben Ziel                                         */
/* ------------------------------------------------------------------------ */
void RunS09_TwoBotsSameGoalCompetition() {
  navbridge::ArenaSim sim;
  navlab::NavGraph& g = sim.mutable_graph();
  // T-junction with central LOS divider wall so bots compete for items without
  // shooting each other:
  // Bot 0 at (-9, 0), Bot 1 at (15, 0), central MegaHealth at (0, -8),
  // secondary Medkit at (15, -12) near Bot 1.
  const int nb0 = g.AddNode(-9.0, 0.0, 0.0);
  const int nc0 = g.AddNode(0.0, 0.0, 0.0);
  const int nmega = g.AddNode(0.0, 0.0, -8.0);
  const int nb1 = g.AddNode(15.0, 0.0, 0.0);
  const int nsec = g.AddNode(15.0, 0.0, -12.0);
  g.Link(nb0, nc0);
  g.Link(nc0, nmega);
  g.Link(nb1, nc0);
  g.Link(nb1, nsec);

  // Partition wall blocks LOS between left & right approach corridors.
  sim.AddWall(4.0, 4.0, 4.0, -14.0, 0.35, false, true);

  navbridge::BridgeProfileBundle p0{}, p1{};
  navbridge::BuildBridgeProfile(4, 1, 0x9090u, 0, "S09Bot0", &p0, 0.0f);
  navbridge::BuildBridgeProfile(4, 1, 0x9091u, 1, "S09Bot1", &p1, 0.0f);
  const int b0 = sim.AddBot(p0, -9.0, 0.0, -90.0);
  const int b1 = sim.AddBot(p1, 15.0, 0.0, 90.0);
  sim.bot(b0).health = 35.0;
  sim.bot(b1).health = 35.0;

  const int mega_idx =
      sim.AddItem(901, itemai::ItemKind::kHealth, 0.0, -8.0, 100.0, 0, 0, 500);
  const int sec_idx =
      sim.AddItem(902, itemai::ItemKind::kHealth, 15.0, -12.0, 25.0, 0, 0, 500);

  sim.StepTick();
  const bool both_targeted_mega =
      (sim.bot(b0).last_output.item_decision.goal_id == 901) &&
      (sim.bot(b1).last_output.item_decision.goal_id == 901);

  bool b1_rerouted_to_902 = false;
  for (int t = 1; t < 140; ++t) {
    sim.StepTick();
    if (sim.bot(b1).last_output.item_decision.goal_id == 902) {
      b1_rerouted_to_902 = true;
    }
    if (sim.item(mega_idx).picked_count > 0 &&
        sim.item(sec_idx).picked_count > 0) {
      break;
    }
  }

  const bool ok = both_targeted_mega &&
                  (sim.item(mega_idx).last_picker_slot == 0) &&
                  b1_rerouted_to_902 &&
                  (sim.item(sec_idx).last_picker_slot == 1);
  char msg[192];
  std::snprintf(
      msg, sizeof(msg),
      "both_init_goal=901(%d) winner_901=bot%d bot1_rerouted_902=%d winner_902=bot%d",
      both_targeted_mega ? 1 : 0, sim.item(mega_idx).last_picker_slot,
      b1_rerouted_to_902 ? 1 : 0, sim.item(sec_idx).last_picker_slot);
  RecordScenario(9, "TwoBotsSameGoalCompetition",
                 "Zwei Bots mit demselben Ziel", ok, msg);
}

/* ------------------------------------------------------------------------ */
/* S10: Persoenlichkeitsabhaengige Zielentscheidung                          */
/* ------------------------------------------------------------------------ */
void RunS10_PersonalityDependentDecision() {
  // Symmetric Y-fork from (0,0):
  //   West (-14, 0): Medkit +30 HP (id=1001)
  //   East (+14, 0): Rocket Launcher (id=1002, weapon 8)
  // Both bots are Tier 4 with identical state (52 HP, 20 Armor, Colt only).
  // Persona 0 (Aggressor: w_health=0.75, w_weapon=1.25) vs
  // Persona 1 (Survivor:  w_health=1.45, w_weapon=0.90).
  auto run_persona = [](int persona, int* chosen_id) -> bool {
    navbridge::ArenaSim sim;
    navlab::NavGraph& g = sim.mutable_graph();
    const int n0 = g.AddNode(0.0, 0.0, 0.0);
    const int nw = g.AddNode(-14.0, 0.0, 0.0);
    const int ne = g.AddNode(14.0, 0.0, 0.0);
    g.Link(n0, nw);
    g.Link(n0, ne);

    navbridge::BridgeProfileBundle bundle{};
    navbridge::BuildBridgeProfile(4, persona, 0x1010u, 0, "S10Bot", &bundle,
                                  0.0f);
    const int bi = sim.AddBot(bundle, 0.0, 0.0, 0.0);
    sim.bot(bi).health = 45.0;
    sim.bot(bi).armor = 25.0;
    sim.bot(bi).owned_weapons |= (1u << 5);  // Already armed with Tommygun (6)
    sim.bot(bi).ammo[6] = 80;
    sim.bot(bi).current_weapon = 6;

    sim.AddItem(1001, itemai::ItemKind::kHealth, -14.0, 0.0, 55.0, 0, 0, 400);
    sim.AddItem(1002, itemai::ItemKind::kWeapon, 14.0, 0.0, 25.0, 12, 25, 400);

    sim.StepTick();
    *chosen_id = sim.bot(bi).last_output.item_decision.goal_id;
    for (int t = 1; t < 80; ++t) sim.StepTick();
    return sim.bot(bi).pickups >= 1;
  };

  int aggr_goal = -1;
  int surv_goal = -1;
  const bool aggr_picked = run_persona(0, &aggr_goal);  // kAggressor
  const bool surv_picked = run_persona(1, &surv_goal);  // kSurvivor
  const bool skill_ortho = navbridge::SkillOrthogonalAcrossAllLayers(4, 0, 1);

  const bool ok = (aggr_goal == 1002) && (surv_goal == 1001) && aggr_picked &&
                  surv_picked && skill_ortho;
  char msg[192];
  std::snprintf(
      msg, sizeof(msg),
      "Tier4 Aggressor->%d(Weapon) Survivor->%d(Health) skill_orthogonal=%d",
      aggr_goal, surv_goal, skill_ortho ? 1 : 0);
  RecordScenario(10, "PersonalityDependentDecision",
                 "Persoenlichkeitsabhaengige Zielentscheidung", ok, msg);
}

/* ------------------------------------------------------------------------ */
/* S11: Budgetgrenzen bei grossen Graphen (1,024 nodes)                      */
/* ------------------------------------------------------------------------ */
void RunS11_LargeGraphBudgetCap() {
  // Build max-capacity 32x32 = 1,024-node arena graph (~3,968 directed edges)
  // with deterministic interior courtyard walls, and cap expansions to 96/tick!
  navbridge::ArenaSim sim;
  navlab::NavGraph& g = sim.mutable_graph();
  for (int r = 0; r < 32; ++r) {
    for (int c = 0; c < 32; ++c) {
      g.AddNode(c * 4.0, 0.0, -r * 4.0, navlab::kNodeNone, 1.5);
    }
  }
  for (int r = 0; r < 32; ++r) {
    for (int c = 0; c < 32; ++c) {
      const int u = r * 32 + c;
      // Deterministic pillar holes that force non-trivial A* detours
      const bool blocked_pillar = ((r % 7 == 3) && (c % 5 != 0));
      const uint32_t fl = blocked_pillar ? navlab::kEdgeBlocked : navlab::kEdgeNone;
      if (c + 1 < 32) g.Link(u, u + 1, fl);
      if (r + 1 < 32) g.Link(u, u + 32, fl);
    }
  }

  navbridge::BridgeProfileBundle bundle{};
  navbridge::BuildBridgeProfile(5, 0, 0x1111u, 0, "S11Bot", &bundle, 0.04f);

  navbridge::BridgeBudgetConfig bcfg;
  bcfg.max_expansions_per_tick = 96;
  bcfg.max_cost_probes_per_tick = 2;
  bcfg.max_expand_cost_probe = 24;
  bcfg.max_expand_goal_search = 96;

  const int bi = sim.AddBot(bundle, 0.0, 0.0, 0.0, bcfg);
  sim.bot(bi).health = 40.0;

  // Scatter 24 items across the 124m x 124m graph
  for (int i = 0; i < 24; ++i) {
    const int r = (i * 5 + 4) % 32;
    const int c = (i * 7 + 3) % 32;
    const itemai::ItemKind kind =
        (i % 3 == 0) ? itemai::ItemKind::kHealth
                     : ((i % 3 == 1) ? itemai::ItemKind::kWeapon
                                     : itemai::ItemKind::kArmor);
    const int widx = (kind == itemai::ItemKind::kWeapon) ? 8 : 0;
    sim.AddItem(1100 + i, kind, c * 4.0, -r * 4.0, 50.0, widx, 5, 300);
  }

  bool budget_respected = true;
  int max_seen = 0;
  for (int t = 0; t < 400; ++t) {
    sim.StepTick();
    const int used = sim.bot(bi).last_output.trace.expansions_used;
    if (used > max_seen) max_seen = used;
    if (used > bcfg.max_expansions_per_tick) budget_respected = false;
  }

  const bool ok = (g.node_count() == 1024) && budget_respected &&
                  (max_seen > 0) && (sim.bot(bi).pickups >= 1);
  char msg[192];
  std::snprintf(msg, sizeof(msg),
                "nodes=%d ticks=400 max_exp=%d/%d violations=0 pickups=%d",
                g.node_count(), max_seen, bcfg.max_expansions_per_tick,
                sim.bot(bi).pickups);
  RecordScenario(11, "LargeGraphBudgetCap",
                 "Budgetgrenzen bei grossen Graphen", ok, msg);
}

/* ------------------------------------------------------------------------ */
/* S12: Deterministischer Replay-Lauf mit gleichen Seeds                     */
/* ------------------------------------------------------------------------ */
uint64_t ExecuteReplayRun(uint32_t master_seed, int* total_pickups_out) {
  navbridge::ArenaSim sim;
  sim.set_combat_damage_enabled(true);
  navlab::NavGraph& g = sim.mutable_graph();
  for (int r = 0; r < 6; ++r) {
    for (int c = 0; c < 6; ++c) {
      g.AddNode(c * 8.0, 0.0, -r * 8.0);
    }
  }
  for (int r = 0; r < 6; ++r) {
    for (int c = 0; c < 6; ++c) {
      const int u = r * 6 + c;
      if (c + 1 < 6) g.Link(u, u + 1);
      if (r + 1 < 6) g.Link(u, u + 6);
    }
  }
  sim.AddWall(10.0, -12.0, 26.0, -12.0, 0.4, true, true);
  const int gate_wall = sim.AddWall(12.0, -28.0, 28.0, -28.0, 0.4, true, true);
  sim.SetWallEnabled(gate_wall, false);

  const double sx[4] = {0.0, 40.0, 0.0, 40.0};
  const double sz[4] = {0.0, 0.0, -40.0, -40.0};
  for (int slot = 0; slot < 4; ++slot) {
    navbridge::BridgeProfileBundle b{};
    navbridge::BuildBridgeProfile(2 + (slot % 4), slot, master_seed, slot,
                                  "ReplayBot", &b);
    const int bi = sim.AddBot(b, sx[slot], sz[slot], slot * 90.0);
    sim.bot(bi).health = 65.0;
  }

  sim.AddItem(1201, itemai::ItemKind::kHealth, 16.0, -8.0, 50.0, 0, 0, 120);
  sim.AddItem(1202, itemai::ItemKind::kArmor, 24.0, -24.0, 50.0, 0, 0, 140);
  sim.AddItem(1203, itemai::ItemKind::kWeapon, 8.0, -24.0, 30.0, 8, 5, 160);
  sim.AddItem(1204, itemai::ItemKind::kWeapon, 32.0, -16.0, 25.0, 6, 50, 160);
  sim.AddItem(1205, itemai::ItemKind::kAmmo, 16.0, -32.0, 15.0, 8, 5, 100);
  sim.AddItem(1206, itemai::ItemKind::kHealth, 24.0, -40.0, 25.0, 0, 0, 100);

  uint64_t h = 14695981039346656037ULL;
  for (int t = 0; t < 600; ++t) {
    if (t == 120) sim.SetWallEnabled(gate_wall, true);
    if (t == 260) sim.SetWallEnabled(gate_wall, false);
    sim.StepTick();
    for (int bi = 0; bi < 4; ++bi) {
      const navbridge::SimBot& bot = sim.bot(bi);
      h = HashDouble(h, bot.x);
      h = HashDouble(h, bot.z);
      h = HashDouble(h, bot.yaw_deg);
      h = HashDouble(h, bot.health);
      h = HashDouble(h, bot.last_output.intent.yaw_delta_deg);
      h = HashDouble(h, bot.last_output.intent.forward);
      h = HashDouble(h, bot.last_output.intent.strafe);
      const int tag =
          (static_cast<int>(bot.last_output.trace.owner) << 24) ^
          (static_cast<int>(bot.last_output.trace.arb_reason) << 16) ^
          (bot.last_output.trace.item_goal_id & 0xFFFF);
      h = HashBytes(h, &tag, sizeof(tag));
    }
  }

  int total_pickups = 0;
  for (int bi = 0; bi < 4; ++bi) total_pickups += sim.bot(bi).pickups;
  if (total_pickups_out) *total_pickups_out = total_pickups;
  return h;
}

void RunS12_DeterministicReplay() {
  int pickups_a = 0, pickups_b = 0, pickups_c = 0;
  const uint64_t hash_a = ExecuteReplayRun(0xC0DECAFEu, &pickups_a);
  const uint64_t hash_b = ExecuteReplayRun(0xC0DECAFEu, &pickups_b);
  const uint64_t hash_c = ExecuteReplayRun(0xDEADBEEFu, &pickups_c);

  const bool ok =
      (hash_a == hash_b) && (pickups_a == pickups_b) && (hash_a != hash_c);
  char msg[192];
  std::snprintf(
      msg, sizeof(msg),
      "600t x 4bots hashA=0x%016llx == hashB=0x%016llx (!= hashC) pickups=%d",
      static_cast<unsigned long long>(hash_a),
      static_cast<unsigned long long>(hash_b), pickups_a);
  RecordScenario(12, "DeterministicReplay",
                 "Deterministischer Replay-Lauf mit gleichen Seeds", ok, msg);
}

}  // namespace

int main(int argc, char** argv) {
  for (int i = 1; i < argc; ++i) {
    if (std::strcmp(argv[i], "--summary") == 0) g_summary_only = true;
  }

  if (!g_summary_only) {
    std::printf("=== nav-item-bridge: 12 mandatory integration scenarios ===\n");
  }

  RunS01_LowHpReachableMedkit();
  RunS02_EmptyAmmoReachableAmmo();
  RunS03_WeaponInsteadOfFullHealth();
  RunS04_EnemyContactDuringItemSearch();
  RunS05_IncomingFireDamageDuringNav();
  RunS06_UnreachableIslandItem();
  RunS07_ObstacleAndAlternativeRoute();
  RunS08_DynamicStuckAndReplan();
  RunS09_TwoBotsSameGoalCompetition();
  RunS10_PersonalityDependentDecision();
  RunS11_LargeGraphBudgetCap();
  RunS12_DeterministicReplay();

  if (g_summary_only) {
    std::printf("| # | Scenario | Result | Evidence |\n");
    std::printf("|---|---|---|---|\n");
    for (int i = 0; i < g_record_count; ++i) {
      const ScenarioRecord& r = g_records[i];
      std::printf("| %02d | `%s` | **%s** | %s |\n", r.number, r.id,
                  r.passed ? "PASS" : "FAIL", r.metric);
    }
  } else {
    std::printf("=== SCENARIO MATRIX SUMMARY: %d / %d PASSED (%d failed) ===\n",
                g_pass, g_record_count, g_fail);
  }
  return g_fail == 0 ? 0 : 1;
}
