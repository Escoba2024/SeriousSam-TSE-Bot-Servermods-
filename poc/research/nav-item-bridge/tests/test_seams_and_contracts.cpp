// SPDX-License-Identifier: GPL-2.0-only
// test_seams_and_contracts.cpp - seam, contract, orthogonality, fail-closed,
// cache-coherence and fuzz invariants for `nav-item-bridge`.

#include <cmath>
#include <cstdint>
#include <cstdio>
#include <cstring>

#include "arena_sim.h"

namespace {

int g_pass = 0;
int g_fail = 0;

void Check(bool ok, const char* name, const char* detail = "") {
  if (ok) {
    ++g_pass;
    std::printf("[PASS] %-44s %s\n", name, detail);
  } else {
    ++g_fail;
    std::printf("[FAIL] %-44s %s\n", name, detail);
  }
}

/* 1. 5x6 Profile matrix & strict 3-layer skill/persona orthogonality ------ */
void TestProfileOrthogonality() {
  bool build_all = true;
  for (int tier = 1; tier <= 5; ++tier) {
    for (int p = 0; p < 6; ++p) {
      navbridge::BridgeProfileBundle b{};
      if (!navbridge::BuildBridgeProfile(tier, p, 0x99887766u, p, "Bot", &b)) {
        build_all = false;
      }
    }
  }
  Check(build_all, "C01_BuildAll30Profiles", "5 tiers x 6 personas valid");

  bool ortho = true;
  for (int tier = 1; tier <= 5; ++tier) {
    for (int pa = 0; pa < 6; ++pa) {
      for (int pb = 0; pb < 6; ++pb) {
        if (!navbridge::SkillOrthogonalAcrossAllLayers(tier, pa, pb)) {
          ortho = false;
        }
      }
    }
  }
  Check(ortho, "C02_SkillOrthogonalAcross3Layers",
        "180 (tier,pa,pb) checks across Combat + Item + Nav");

  navbridge::BridgeProfileBundle bad{};
  const bool reject_bad =
      !navbridge::BuildBridgeProfile(0, 0, 1u, 0, "Bad0", &bad) &&
      !navbridge::BuildBridgeProfile(6, 0, 1u, 0, "Bad6", &bad) &&
      !navbridge::BuildBridgeProfile(3, -1, 1u, 0, "BadP", &bad) &&
      !navbridge::BuildBridgeProfile(3, 6, 1u, 0, "BadP6", &bad);
  Check(reject_bad, "C03_InvalidProfileBoundsRejected",
        "tier 0/6 and persona -1/6 rejected fail-closed");
}

/* 2. Right-handed coordinate & yaw parity across botcore / navlab / bridge - */
void TestCoordinateAndYawParity() {
  const botcore::AimAngles fwd = botcore::AimAt(0.0, 0.0, -10.0);
  const botcore::AimAngles right = botcore::AimAt(10.0, 0.0, 0.0);
  const botcore::AimAngles left = botcore::AimAt(-10.0, 0.0, 0.0);

  navbridge::ArenaSim sim;
  navlab::NavGraph& g = sim.mutable_graph();
  const int n0 = g.AddNode(0.0, 0.0, 0.0, navlab::kNodeNone, 1.5);
  const int n1 = g.AddNode(10.0, 0.0, 0.0, navlab::kNodeNone, 1.5);
  g.Link(n0, n1);

  navbridge::BridgeProfileBundle bundle{};
  navbridge::BuildBridgeProfile(4, 0, 0x1111u, 0, "CoordBot", &bundle, 0.0f);
  const int bi = sim.AddBot(bundle, 0.0, 0.0, 0.0);
  sim.bot(bi).health = 30.0;
  sim.AddItem(10, itemai::ItemKind::kHealth, 10.0, 0.0, 50.0, 0, 0, 200);

  for (int t = 0; t < 25; ++t) sim.StepTick();

  const bool moved_pos_x = (sim.bot(bi).x > 2.5 && std::fabs(sim.bot(bi).z) < 2.0);
  const bool angles_match = (std::fabs(fwd.yaw_deg - 0.0) < 1e-6) &&
                            (std::fabs(right.yaw_deg - (-90.0)) < 1e-6) &&
                            (std::fabs(left.yaw_deg - 90.0) < 1e-6);
  char msg[128];
  std::snprintf(msg, sizeof(msg), "yaw(0,-Z)=%.1f yaw(+X)=%.1f bot_x=%.2f",
                fwd.yaw_deg, right.yaw_deg, sim.bot(bi).x);
  Check(angles_match && moved_pos_x, "C04_CoordinateAndYawParity", msg);
}

/* 3. Euclidean Trap vs True Graph Path Cost & PathCostCache hits ---------- */
void TestEuclideanTrapAndCostCache() {
  navbridge::ArenaSim sim;
  navlab::NavGraph& g = sim.mutable_graph();
  const int n_bot = g.AddNode(0.0, 0.0, 0.0);
  const int n_e1 = g.AddNode(7.0, 0.0, 0.0);
  const int n_item2 = g.AddNode(14.0, 0.0, 0.0);
  const int n_w1 = g.AddNode(-12.0, 0.0, 0.0);
  const int n_w2 = g.AddNode(-12.0, 0.0, -14.0);
  const int n_w3 = g.AddNode(12.0, 0.0, -14.0);
  const int n_w4 = g.AddNode(12.0, 0.0, -4.0);
  const int n_item1 = g.AddNode(0.0, 0.0, -4.0);

  g.Link(n_bot, n_e1);
  g.Link(n_e1, n_item2);
  g.Link(n_bot, n_w1);
  g.Link(n_w1, n_w2);
  g.Link(n_w2, n_w3);
  g.Link(n_w3, n_w4);
  g.Link(n_w4, n_item1);
  sim.AddWall(-8.0, -2.0, 8.0, -2.0, 0.4, true, true);

  navbridge::BridgeProfileBundle bundle{};
  navbridge::BuildBridgeProfile(4, 1, 0x2222u, 0, "GraphCostBot", &bundle, 0.0f);
  const int bi = sim.AddBot(bundle, 0.0, 0.0, 0.0);
  sim.bot(bi).health = 35.0;

  sim.AddItem(1, itemai::ItemKind::kHealth, 0.0, -4.0, 25.0, 0, 0, 200);
  sim.AddItem(2, itemai::ItemKind::kHealth, 14.0, 0.0, 25.0, 0, 0, 200);

  sim.StepTick();
  const int chosen_tick1 = sim.bot(bi).last_output.item_decision.goal_id;
  const int probes_t1 = sim.bot(bi).last_output.enrichment.probes_executed;

  sim.StepTick();
  const int hits_t2 = sim.bot(bi).last_output.enrichment.cache_hits;
  const int probes_t2 = sim.bot(bi).last_output.enrichment.probes_executed;

  char msg[128];
  std::snprintf(msg, sizeof(msg),
                "chosen_id=%d (expect 2, not Euclidean-4m trap 1) t1_probes=%d t2_hits=%d t2_probes=%d",
                chosen_tick1, probes_t1, hits_t2, probes_t2);
  Check(chosen_tick1 == 2 && probes_t1 == 2 && hits_t2 >= 2 && probes_t2 == 0,
        "C05_TrueGraphCostBeatsEuclideanTrapAndCaches", msg);
}

/* 4. Fail-closed validation on malformed snapshots & mapless fallback ----- */
void TestFailClosedAndMaplessFallback() {
  navbridge::NavItemBridgeAgent agent;
  navlab::NavGraph g;
  g.AddNode(0.0, 0.0, 0.0);
  g.AddNode(8.0, 0.0, 0.0);
  g.Link(0, 1);

  itemai::ItemSnapshot bad_items[2];
  bad_items[0].id = 7;
  bad_items[0].kind = itemai::ItemKind::kHealth;
  bad_items[0].pos = {std::nan(""), 0.0, 0.0};
  bad_items[0].value = 25.0;
  bad_items[1].id = 7;
  bad_items[1].kind = itemai::ItemKind::kHealth;
  bad_items[1].pos = {8.0, 0.0, 0.0};
  bad_items[1].value = 25.0;

  navbridge::BridgeTickInput in;
  in.world.tick = 1;
  in.world.alive = true;
  in.world.deathmatch = true;
  in.world.health = 25.0;
  in.world.max_health = 100.0;
  in.items = bad_items;
  in.item_count = 2;

  const navbridge::BridgeTickOutput out_bad = agent.Step(g, 1u, in);
  const bool rejected =
      !out_bad.item_decision.has_goal &&
      out_bad.item_decision.reason == itemai::ItemReason::kInvalidWorld &&
      std::isfinite(out_bad.intent.yaw_delta_deg) &&
      std::isfinite(out_bad.intent.forward);
  Check(rejected, "C06_MalformedWorldFailsClosed",
        "NaN item rejected via ItemReason::kInvalidWorld; finite intent");

  navlab::NavGraph empty_g;
  in.world.tick = 2;
  in.items = nullptr;
  in.item_count = 0;
  const navbridge::BridgeTickOutput out_empty = agent.Step(empty_g, 1u, in);
  Check(out_empty.trace.arb_reason == navbridge::ArbitrationReason::kMaplessScan &&
            out_empty.trace.owner == navbridge::ControllerOwner::kPatrolNavigation,
        "C07_EmptyGraphFallsBackToMaplessScan",
        navbridge::ArbitrationReasonName(out_empty.trace.arb_reason));
}

/* 5. Death / Respawn hygiene ---------------------------------------------- */
void TestDeathRespawnHygiene() {
  navbridge::ArenaSim sim;
  navlab::NavGraph& g = sim.mutable_graph();
  const int a = g.AddNode(0.0, 0.0, 0.0);
  const int b = g.AddNode(0.0, 0.0, -15.0);
  g.Link(a, b);
  sim.AddItem(77, itemai::ItemKind::kHealth, 0.0, -15.0, 50.0, 0, 0, 200);

  navbridge::BridgeProfileBundle bundle{};
  navbridge::BuildBridgeProfile(3, 1, 0x3333u, 0, "RespawnBot", &bundle);
  const int bi = sim.AddBot(bundle, 0.0, 0.0, 0.0);
  sim.bot(bi).health = 30.0;
  sim.StepTick();
  const bool had_goal = sim.bot(bi).last_output.item_decision.has_goal;

  sim.InjectDamage(bi, 100.0);
  sim.StepTick();
  const bool dead_idle =
      !sim.bot(bi).alive &&
      sim.bot(bi).last_output.trace.owner == navbridge::ControllerOwner::kDeadIdle &&
      std::fabs(sim.bot(bi).last_output.intent.forward) < 1e-9 &&
      !sim.bot(bi).last_output.intent.fire;

  sim.bot(bi).alive = true;
  sim.bot(bi).health = 100.0;
  sim.StepTick();
  const bool clean_after_respawn =
      !sim.bot(bi).last_output.item_decision.has_goal &&
      !sim.bot(bi).last_output.trace.under_fire;

  Check(had_goal && dead_idle && clean_after_respawn,
        "C08_DeathAndRespawnStateHygiene",
        "goal, damage-alert & movement reset cleanly across death/respawn");
}

/* 6. 1,000-tick randomized fuzz / finite-output / budget invariant -------- */
void TestRandomizedFuzzInvariants() {
  navbridge::ArenaSim sim;
  navlab::NavGraph& g = sim.mutable_graph();
  for (int r = 0; r < 5; ++r) {
    for (int c = 0; c < 5; ++c) {
      g.AddNode(c * 8.0, 0.0, -r * 8.0);
    }
  }
  for (int r = 0; r < 5; ++r) {
    for (int c = 0; c < 5; ++c) {
      const int u = r * 5 + c;
      if (c + 1 < 5) g.Link(u, u + 1);
      if (r + 1 < 5) g.Link(u, u + 5);
    }
  }

  navbridge::BridgeProfileBundle bundle{};
  navbridge::BuildBridgeProfile(3, 5, 0xF0221234u, 0, "FuzzBot", &bundle);
  navbridge::BridgeBudgetConfig bcfg;
  bcfg.max_expansions_per_tick = 80;
  const int bi = sim.AddBot(bundle, 4.0, -4.0, 35.0, bcfg);
  const int ei = sim.AddDummyEnemy(20.0, -20.0, 0.0, 100.0);

  sim.AddItem(1, itemai::ItemKind::kHealth, 0.0, -24.0, 25.0, 0, 0, 60);
  sim.AddItem(2, itemai::ItemKind::kArmor, 24.0, 0.0, 50.0, 0, 0, 80);
  sim.AddItem(3, itemai::ItemKind::kWeapon, 32.0, -32.0, 1.0, 8, 5, 100);
  sim.AddItem(4, itemai::ItemKind::kAmmo, 16.0, -24.0, 1.0, 8, 5, 70);

  uint32_t rng = 0xACE12345u;
  bool all_finite = true;
  bool budget_ok = true;
  bool fire_hygiene = true;

  for (int t = 0; t < 1000; ++t) {
    rng = rng * 1664525u + 1013904223u;
    if ((t % 45) == 10) {
      sim.bot(ei).x = static_cast<double>((rng % 32));
      sim.bot(ei).z = -static_cast<double>(((rng >> 8) % 32));
      sim.bot(ei).alive = ((rng >> 16) & 3u) != 0u;
    }
    if ((t % 70) == 25 && sim.bot(bi).health > 30.0) {
      sim.InjectDamage(bi, 15.0);
    }
    sim.StepTick();
    const navbridge::BridgeTickOutput& out = sim.bot(bi).last_output;
    if (!std::isfinite(out.intent.yaw_delta_deg) ||
        !std::isfinite(out.intent.pitch_delta_deg) ||
        !std::isfinite(out.intent.forward) ||
        !std::isfinite(out.intent.strafe) ||
        std::fabs(out.intent.forward) > 1.0001 ||
        std::fabs(out.intent.strafe) > 1.0001 ||
        out.intent.weapon < 1 || out.intent.weapon > 14) {
      all_finite = false;
    }
    if (out.trace.expansions_used > bcfg.max_expansions_per_tick) {
      budget_ok = false;
    }
    if (out.trace.owner != navbridge::ControllerOwner::kCombat &&
        out.intent.fire) {
      fire_hygiene = false;
    }
  }

  char msg[128];
  std::snprintf(msg, sizeof(msg),
                "1000 ticks: max_exp=%d/%d pickups=%d finite=%d fire_hygiene=%d",
                sim.bot(bi).agent.max_tick_expansions(),
                bcfg.max_expansions_per_tick, sim.bot(bi).pickups,
                all_finite ? 1 : 0, fire_hygiene ? 1 : 0);
  Check(all_finite && budget_ok && fire_hygiene,
        "C09_Fuzz1000TicksFiniteBoundedAndFireSafe", msg);
}

}  // namespace

int main() {
  std::printf("=== nav-item-bridge: seams, contracts & invariants ===\n");
  TestProfileOrthogonality();
  TestCoordinateAndYawParity();
  TestEuclideanTrapAndCostCache();
  TestFailClosedAndMaplessFallback();
  TestDeathRespawnHygiene();
  TestRandomizedFuzzInvariants();
  std::printf("=== SUMMARY: %d passed, %d failed ===\n", g_pass, g_fail);
  return g_fail == 0 ? 0 : 1;
}
