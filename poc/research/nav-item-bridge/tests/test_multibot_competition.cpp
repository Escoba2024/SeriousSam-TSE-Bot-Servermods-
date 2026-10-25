// SPDX-License-Identifier: GPL-2.0-only
// test_multibot_competition.cpp - multi-bot contention, shared `const NavGraph`
// immutability, evaluation-order independence and hysteresis anti-oscillation.

#include <cmath>
#include <cstdint>
#include <cstdio>
#include <cstring>

#include "arena_sim.h"

namespace {

int g_pass = 0;
int g_fail = 0;
bool g_summary_only = false;

void Check(bool ok, const char* name, const char* detail) {
  if (ok) {
    ++g_pass;
  } else {
    ++g_fail;
  }
  if (!g_summary_only) {
    std::printf("[%s] %-42s | %s\n", ok ? "PASS" : "FAIL", name, detail);
  }
}

uint64_t HashMemory(const void* data, size_t n) {
  uint64_t h = 14695981039346656037ULL;
  const uint8_t* p = static_cast<const uint8_t*>(data);
  for (size_t i = 0; i < n; ++i) {
    h ^= static_cast<uint64_t>(p[i]);
    h *= 1099511628211ULL;
  }
  return h;
}

/* 1. 8-Bot Deathmatch Contention + Shared Graph Bytewise Immutability ----- */
void TestEightBotDeathmatchContention() {
  navbridge::ArenaSim sim;
  sim.set_combat_damage_enabled(true);
  navlab::NavGraph& g = sim.mutable_graph();

  // 8x8 = 64-node Deathmatch arena (56 m x 56 m) with four cover pillars
  for (int r = 0; r < 8; ++r) {
    for (int c = 0; c < 8; ++c) {
      g.AddNode(c * 8.0, 0.0, -r * 8.0, navlab::kNodeNone, 1.5);
    }
  }
  for (int r = 0; r < 8; ++r) {
    for (int c = 0; c < 8; ++c) {
      const int u = r * 8 + c;
      if (c + 1 < 8) {
        // Vertical partition wall at x=28 sits between col 3 (x=24) and col 4 (x=32)
        // except through the central courtyard doorway (rows 3..4).
        const bool wall_x = (c == 3 && (r <= 2 || r >= 5));
        g.Link(u, u + 1, wall_x ? navlab::kEdgeBlocked : navlab::kEdgeNone);
      }
      if (r + 1 < 8) {
        // Horizontal partition wall at z=-28 sits between row 3 (z=-24) and row 4 (z=-32)
        // except through the central courtyard doorway (cols 3..4).
        const bool wall_z = (r == 3 && (c <= 2 || c >= 5));
        g.Link(u, u + 8, wall_z ? navlab::kEdgeBlocked : navlab::kEdgeNone);
      }
    }
  }
  // Realistic 4-room Deathmatch layout: cross-shaped corridor walls with
  // doorway openings so bots break LOS between rooms, restock items, and fight
  // in rooms/chokepoints rather than sniping across an empty 56m plane.
  sim.AddWall(28.0, 2.0, 28.0, -18.0, 0.4, true, true);
  sim.AddWall(28.0, -38.0, 28.0, -58.0, 0.4, true, true);
  sim.AddWall(-2.0, -28.0, 18.0, -28.0, 0.4, true, true);
  sim.AddWall(38.0, -28.0, 58.0, -28.0, 0.4, true, true);
  sim.AddWall(12.0, -12.0, 20.0, -12.0, 0.4, true, true);
  sim.AddWall(36.0, -44.0, 44.0, -44.0, 0.4, true, true);

  // Hash the entire NavGraph object BEFORE stepping 8 bots for 600 ticks.
  const uint64_t graph_hash_before = HashMemory(&sim.graph(), sizeof(navlab::NavGraph));

  const double spawn_x[8] = {0.0, 24.0, 56.0, 56.0, 56.0, 32.0, 0.0, 0.0};
  const double spawn_z[8] = {0.0, 0.0,  0.0,  -24.0, -56.0, -56.0, -56.0, -32.0};
  for (int i = 0; i < 8; ++i) {
    navbridge::BridgeProfileBundle b{};
    navbridge::BuildBridgeProfile(1 + (i % 5), i % 6, 0x88880000u, i, "DM8Bot",
                                  &b);
    const int bi = sim.AddBot(b, spawn_x[i], spawn_z[i], i * 45.0);
    sim.bot(bi).health = 60.0 + (i % 3) * 15.0;
  }

  // Central contested items + perimeter pickups
  sim.AddItem(1, itemai::ItemKind::kHealth, 28.0, -28.0, 100.0, 0, 0, 120);
  sim.AddItem(2, itemai::ItemKind::kArmor, 24.0, -32.0, 100.0, 0, 0, 140);
  sim.AddItem(3, itemai::ItemKind::kWeapon, 16.0, -24.0, 35.0, 8, 5, 160);
  sim.AddItem(4, itemai::ItemKind::kWeapon, 40.0, -32.0, 30.0, 12, 25, 160);
  sim.AddItem(5, itemai::ItemKind::kHealth, 8.0, -8.0, 25.0, 0, 0, 90);
  sim.AddItem(6, itemai::ItemKind::kHealth, 48.0, -48.0, 25.0, 0, 0, 90);
  sim.AddItem(7, itemai::ItemKind::kAmmo, 32.0, -16.0, 15.0, 8, 5, 80);
  sim.AddItem(8, itemai::ItemKind::kArmor, 16.0, -48.0, 50.0, 0, 0, 100);

  bool any_bad_output = false;
  for (int t = 0; t < 600; ++t) {
    sim.StepTick();
    // Auto-respawn dead bots after a short delay to keep 8-bot pressure high
    for (int bi = 0; bi < 8; ++bi) {
      navbridge::SimBot& bot = sim.bot(bi);
      if (!bot.alive && (t % 25 == 0)) {
        bot.alive = true;
        bot.health = 80.0;
        bot.x = spawn_x[bi];
        bot.z = spawn_z[bi];
      }
      const navbridge::BridgeTickOutput& out = bot.last_output;
      if (!std::isfinite(out.intent.yaw_delta_deg) ||
          !std::isfinite(out.intent.forward) ||
          out.trace.expansions_used > out.trace.expansion_limit) {
        any_bad_output = true;
      }
    }
  }

  const uint64_t graph_hash_after = HashMemory(&sim.graph(), sizeof(navlab::NavGraph));

  int sum_bot_pickups = 0;
  int bots_with_pickups = 0;
  for (int bi = 0; bi < 8; ++bi) {
    sum_bot_pickups += sim.bot(bi).pickups;
    if (sim.bot(bi).pickups > 0) ++bots_with_pickups;
  }
  int sum_item_picks = 0;
  for (int ii = 0; ii < sim.item_count(); ++ii) {
    sum_item_picks += sim.item(ii).picked_count;
  }

  const bool graph_immutable = (graph_hash_before == graph_hash_after);
  const bool conservation_exact = (sum_bot_pickups == sum_item_picks);
  const bool ok = graph_immutable && conservation_exact && !any_bad_output &&
                  (sum_bot_pickups >= 6) && (bots_with_pickups >= 3);

  char msg[192];
  std::snprintf(
      msg, sizeof(msg),
      "graph_immutable=%d pickups=%d==%d(exact_conservation) active_collectors=%d/8",
      graph_immutable ? 1 : 0, sum_bot_pickups, sum_item_picks,
      bots_with_pickups);
  Check(ok, "M01_EightBotContentionAndGraphImmutability", msg);
}

/* 2. Evaluation-Order Independence (Zero Hidden Static/Global State) ------ */
void TestAgentStepOrderIndependence() {
  navlab::NavGraph g;
  for (int i = 0; i < 6; ++i) g.AddNode(i * 6.0, 0.0, 0.0);
  for (int i = 0; i < 5; ++i) g.Link(i, i + 1);

  navbridge::BridgeProfileBundle p_a{}, p_b{};
  navbridge::BuildBridgeProfile(3, 0, 0xAAAAu, 0, "OrderA", &p_a);
  navbridge::BuildBridgeProfile(5, 1, 0xBBBBu, 1, "OrderB", &p_b);

  itemai::ItemSnapshot items[2];
  items[0].id = 10;
  items[0].kind = itemai::ItemKind::kHealth;
  items[0].pos = {18.0, 0.0, 0.0};
  items[0].value = 50.0;
  items[0].visible = true;
  items[1].id = 11;
  items[1].kind = itemai::ItemKind::kWeapon;
  items[1].weapon_index = 8;
  items[1].pos = {30.0, 0.0, 0.0};
  items[1].value = 30.0;
  items[1].visible = true;

  auto run_pair = [&](bool reverse_order, uint64_t* hash_a, uint64_t* hash_b) {
    navbridge::NavItemBridgeAgent a, b;
    a.Configure(p_a, navbridge::BridgeBudgetConfig(), 0);
    b.Configure(p_b, navbridge::BridgeBudgetConfig(), 1);
    *hash_a = 14695981039346656037ULL;
    *hash_b = 14695981039346656037ULL;

    for (int t = 1; t <= 50; ++t) {
      navbridge::BridgeTickInput in_a, in_b;
      in_a.world.tick = t;
      in_a.world.alive = true;
      in_a.world.deathmatch = true;
      in_a.world.health = 45.0;
      in_a.world.pose.x = t * 0.2;
      in_a.items = items;
      in_a.item_count = 2;

      in_b = in_a;
      in_b.world.health = 35.0;
      in_b.world.pose.x = 6.0 + t * 0.15;

      navbridge::BridgeTickOutput out_a, out_b;
      if (!reverse_order) {
        out_a = a.Step(g, 1u, in_a);
        out_b = b.Step(g, 1u, in_b);
      } else {
        out_b = b.Step(g, 1u, in_b);
        out_a = a.Step(g, 1u, in_a);
      }
      *hash_a ^= HashMemory(&out_a.intent, sizeof(out_a.intent));
      *hash_b ^= HashMemory(&out_b.intent, sizeof(out_b.intent));
    }
  };

  uint64_t a1 = 0, b1 = 0, a2 = 0, b2 = 0;
  run_pair(false, &a1, &b1);
  run_pair(true, &a2, &b2);

  const bool ok = (a1 == a2) && (b1 == b2);
  char msg[192];
  std::snprintf(msg, sizeof(msg),
                "A(first==second)=0x%016llx B(first==second)=0x%016llx",
                static_cast<unsigned long long>(a1),
                static_cast<unsigned long long>(b1));
  Check(ok, "M02_SlotStepOrderIndependence", msg);
}

/* 3. Hysteresis Anti-Oscillation Under Near-Equal Competing Goals --------- */
void TestHysteresisAntiOscillation() {
  navbridge::ArenaSim sim;
  navlab::NavGraph& g = sim.mutable_graph();
  const int n0 = g.AddNode(0.0, 0.0, 0.0);
  const int nl = g.AddNode(-12.0, 0.0, -12.0);
  const int nr = g.AddNode(12.2, 0.0, -12.0);
  g.Link(n0, nl);
  g.Link(n0, nr);

  navbridge::BridgeProfileBundle bundle{};
  navbridge::BuildBridgeProfile(3, 2, 0x7777u, 0, "HystBot", &bundle, 0.0f);
  const int bi = sim.AddBot(bundle, 0.0, 0.0, 0.0);
  sim.bot(bi).health = 40.0;

  // Two nearly identical Medkits on opposite diagonals
  sim.AddItem(50, itemai::ItemKind::kHealth, -12.0, -12.0, 50.0, 0, 0, 400);
  sim.AddItem(51, itemai::ItemKind::kHealth, 12.2, -12.0, 50.5, 0, 0, 400);

  for (int t = 0; t < 90; ++t) {
    sim.StepTick();
    if (sim.bot(bi).pickups > 0) break;
  }

  const int switches = sim.bot(bi).agent.item_planner().switches();
  const bool ok = (switches == 0) && (sim.bot(bi).pickups == 1);
  char msg[192];
  std::snprintf(msg, sizeof(msg),
                "near_equal_goals switches=%d (expect 0) pickups=%d",
                switches, sim.bot(bi).pickups);
  Check(ok, "M03_HysteresisPreventsGoalThrashing", msg);
}

}  // namespace

int main(int argc, char** argv) {
  for (int i = 1; i < argc; ++i) {
    if (std::strcmp(argv[i], "--summary") == 0) g_summary_only = true;
  }

  if (!g_summary_only) {
    std::printf("=== nav-item-bridge: multi-bot contention & isolation ===\n");
  }

  TestEightBotDeathmatchContention();
  TestAgentStepOrderIndependence();
  TestHysteresisAntiOscillation();

  std::printf("=== MULTIBOT SUMMARY: %d passed, %d failed ===\n", g_pass,
              g_fail);
  return g_fail == 0 ? 0 : 1;
}
