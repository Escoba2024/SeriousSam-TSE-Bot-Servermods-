// test_nav_agent.cpp - offline behavioural tests for NavAgent.
//
// Every test drives the agent through a tiny kinematic simulator (10 m/s,
// 20 Hz tick) so route following, arrival detection, stuck handling and
// mode arbitration are exercised end to end. Deterministic: no randomness
// outside the explicit per-agent seeds.
//
// Build: g++ -std=c++17 -O2 -Wall -Wextra -o test_nav_agent test_nav_agent.cpp

#include <cstdio>
#include <cstdlib>
#include <cmath>
#include "nav_agent.h"
#include "nav_maps.h"

static int g_failures = 0;
static int g_checks = 0;

#define CHECK(cond)                                                          \
  do {                                                                       \
    ++g_checks;                                                              \
    if (!(cond)) {                                                           \
      std::printf("FAIL %s:%d: %s\n", __FILE__, __LINE__, #cond);            \
      ++g_failures;                                                          \
    }                                                                        \
  } while (0)

using namespace navlab;

/* ------------------------------------------------------------------------ */
/* Minimal kinematic simulator                                               */
/* ------------------------------------------------------------------------ */

struct SimBot {
  NavAgent agent;
  double x, z, yaw_deg;
  bool last_moved;   // feeds movement_requested (previous tick's command)
  bool frozen;       // true = bot is blocked; commands ignored (for stuck)

  SimBot() : x(0.0), z(0.0), yaw_deg(0.0), last_moved(false), frozen(false) {}

  void Configure(const NavPersonality& p, uint32_t seed) {
    agent.Configure(p, seed);
  }

  NavCommand Step(const NavGraph& g, int tick, bool has_target, bool visible,
                  double tx, double tz) {
    NavAgentInput in;
    in.tick = tick;
    in.x = x;
    in.y = 0.0;
    in.z = z;
    in.yaw_deg = yaw_deg;
    in.alive = true;
    in.movement_requested = last_moved;
    in.has_target = has_target;
    in.target_visible = visible;
    in.target_x = tx;
    in.target_y = 0.0;
    in.target_z = tz;
    const NavCommand c = agent.Step(g, in);

    yaw_deg += c.yaw_delta_deg;
    while (yaw_deg > 180.0) yaw_deg -= 360.0;
    while (yaw_deg < -180.0) yaw_deg += 360.0;
    // movement_requested mirrors botcore semantics: the caller ASKED to move.
    last_moved = (c.active && c.forward > 0.0);
    if (!frozen && last_moved) {
      // 10 m/s at 20 Hz -> 0.5 m per tick; yaw = atan2(-dx, -dz) convention.
      const double rad = yaw_deg * kNavPi / 180.0;
      x += c.forward * 0.5 * -std::sin(rad);
      z += c.forward * 0.5 * -std::cos(rad);
    }
    return c;
  }

  void Place(double nx, double nz) { x = nx; z = nz; }
};

/* ------------------------------------------------------------------------ */

// Patrol must pick far destinations, walk them, and keep going (corridor).
static void TestPatrolWalksAndReaches() {
  NavGraph g;
  maps::MakeCorridor(g, 8);  // 0..7 along +x, 4 m apart
  g.ComputeDegrees();
  SimBot bot;
  bot.Configure(NavPersonality(), 1u);
  int reached = 0;
  int moving_ticks = 0;
  for (int t = 0; t < 2000; ++t) {
    const NavCommand c = bot.Step(g, t, false, false, 0.0, 0.0);
    CHECK(c.mode != NavMode::kIdle);
    if (c.active && c.forward > 0.0) ++moving_ticks;
    if (c.reached_destination) ++reached;
  }
  CHECK(bot.agent.destinations_reached() >= 2);
  CHECK(reached == bot.agent.destinations_reached());
  CHECK(bot.agent.searches_total() >= 3);
  CHECK(bot.agent.stuck_events() == 0);
  CHECK(moving_ticks > 1000);  // mostly walking, not stuck in scan
  // Telemetry consistency: replans must all be within the 256 budget.
  CHECK(bot.agent.expansions_total() <=
        bot.agent.searches_total() * 256);
}

// Unreachable target: agent walks toward the border, then scans; no
// repeated searches for the same impossible goal (cooldown + goal memo).
static void TestUnreachableGoalScans() {
  NavGraph g;
  maps::MakeDisconnected(g, 4);  // two 4x4 grids, second far to +x
  g.ComputeDegrees();
  const double grid_extent = 3 * 4.0;  // nodes 0..12 on x
  SimBot bot;
  bot.Configure(NavPersonality(), 5u);
  // Stand in the middle of grid A, target deep inside grid B (unreachable).
  bot.Place(4.0, 4.0);
  const double tx = 100.0 + grid_extent, tz = grid_extent;
  bool scanned = false;
  for (int t = 0; t < 400; ++t) {
    const NavCommand c = bot.Step(g, t, true, false, tx, tz);
    if (c.mode == NavMode::kScan) scanned = true;
  }
  CHECK(scanned);
  CHECK(bot.agent.mode() == NavMode::kScan);
  // Made progress toward grid B (x increased), but stayed in grid A.
  CHECK(bot.x > 6.0);
  CHECK(bot.x < 50.0);
  // One search for the impossible goal; no re-search storm.
  CHECK(bot.agent.searches_total() == 1);
}

// Visible target: coarse pursuit steering (combat layer owns fine movement).
static void TestPursueSteersCoarse() {
  NavGraph g;
  maps::MakeCorridor(g, 6);
  g.ComputeDegrees();
  SimBot bot;
  bot.Configure(NavPersonality(), 3u);
  bot.Place(0.0, 0.0);
  bot.yaw_deg = 0.0;
  // Target straight to +x: desired yaw = atan2(-1, 0) = -90 deg.
  const NavCommand c = bot.Step(g, 0, true, true, 10.0, 0.0);
  CHECK(c.mode == NavMode::kPursue);
  CHECK(c.active);
  CHECK(c.yaw_delta_deg < 0.0);  // turning from 0 toward -90
  CHECK(std::fabs(c.yaw_delta_deg) <=
        NavPersonality().turn_rate_deg_s / kNavTickHz + 1e-9);
  // While visible, no route planning happens.
  CHECK(bot.agent.searches_total() == 0);
}

// Target seen once, then lost: agent repositions to the last known node,
// arriving there switches to scan; goal change mid-route forces a replan.
static void TestGoalChangeAndReposition() {
  NavGraph g;
  maps::MakeGrid(g, 8, 8);
  g.ComputeDegrees();
  SimBot bot;
  bot.Configure(NavPersonality(), 9u);
  bot.Place(0.0, 0.0);
  // Lost target far away at (28, 28) -> reposition mode, a route is planned.
  NavCommand c = bot.Step(g, 0, true, false, 28.0, 28.0);
  CHECK(c.mode == NavMode::kReposition);
  CHECK(c.replanned);
  CHECK(c.dest_node >= 0);
  CHECK(bot.agent.searches_total() == 1);
  const int first_dest = c.dest_node;
  // Walk a few ticks, then the "last known" position changes completely.
  for (int t = 1; t < 10; ++t) bot.Step(g, t, true, false, 28.0, 28.0);
  c = bot.Step(g, 10, true, false, 0.0, 28.0);  // opposite corner
  CHECK(c.replanned);
  CHECK(c.dest_node != first_dest);
  CHECK(bot.agent.searches_total() == 2);
  CHECK(bot.agent.expansions_total() > 0);
  // Walk to completion of the (shorter) route, then the agent scans.
  bool scanned = false;
  for (int t = 11; t < 400; ++t) {
    const NavCommand cc = bot.Step(g, t, true, false, 0.0, 28.0);
    if (cc.mode == NavMode::kScan) { scanned = true; break; }
  }
  CHECK(scanned);
}

// Stuck: movement requested but no progress for a full window -> stuck flag
// exactly once, then an immediate replan around the avoided node.
static void TestStuckTriggersRecovery() {
  NavGraph g;
  maps::MakeCorridor(g, 8);
  g.ComputeDegrees();
  SimBot bot;
  NavPersonality p;
  p.stuck_window = 40;
  p.stuck_min_dist = 1.0f;
  bot.Configure(p, 2u);
  int stuck_flags = 0;
  for (int t = 0; t < 120; ++t) {
    const NavCommand c = bot.Step(g, t, false, false, 0.0, 0.0);
    if (c.stuck) ++stuck_flags;
    if (t == 5) bot.frozen = true;   // hit an invisible wall...
    if (t == 90) bot.frozen = false; // ...freed again after recovery
  }
  CHECK(stuck_flags >= 1);
  CHECK(bot.agent.stuck_events() >= 1);
  // After recovery the agent walks on and eventually reaches a destination.
  int reached_after = 0;
  for (int t = 120; t < 600; ++t) {
    const NavCommand c = bot.Step(g, t, false, false, 0.0, 0.0);
    if (c.reached_destination) ++reached_after;
  }
  CHECK(reached_after >= 1);
}

// Teleport / respawn: a >8 m jump drops the stale route and replans.
static void TestTeleportGuard() {
  NavGraph g;
  maps::MakeGrid(g, 6, 6);
  g.ComputeDegrees();
  SimBot bot;
  bot.Configure(NavPersonality(), 4u);
  bot.Place(0.0, 0.0);
  for (int t = 0; t < 5; ++t) bot.Step(g, t, false, false, 0.0, 0.0);
  const int searches_before = bot.agent.searches_total();
  bot.Place(20.0, 20.0);  // instant relocation
  const NavCommand c = bot.Step(g, 5, false, false, 0.0, 0.0);
  CHECK(bot.agent.searches_total() > searches_before);
  CHECK(c.mode == NavMode::kPatrol);
  CHECK(c.dest_node >= 0);
}

// Budgeted search on the spiral: per-plan expansions stay <= 256 and the
// agent still makes progress via partial routes (no freeze at the start).
static void TestBudgetedSearchMakesProgress() {
  NavGraph g;
  maps::MakeSpiral(g, 16);  // 256 nodes, single long corridor
  g.ComputeDegrees();
  SimBot bot;
  NavPersonality p;
  p.repath_cooldown = 20;
  bot.Configure(p, 6u);
  const double x0 = bot.x, z0 = bot.z;
  int replans = 0;
  for (int t = 0; t < 1200; ++t) {
    const NavCommand c = bot.Step(g, t, false, false, 0.0, 0.0);
    if (c.replanned) ++replans;
    CHECK(c.expanded_last_search <= 256);
  }
  CHECK(bot.agent.searches_total() >= 2);
  CHECK(replans == bot.agent.searches_total());
  CHECK(bot.agent.expansions_total() <= bot.agent.searches_total() * 256);
  // The bot actually moved along the spiral instead of idling at node 0.
  const double moved = std::hypot(bot.x - x0, bot.z - z0);
  CHECK(moved > 5.0);
}

// Personalities steer patrol differently on the same map: an "explorer"
// (high explore bias, no dead-end aversion) and a "cautious" one must not
// produce identical destination sequences on a dead-end-rich map.
static void TestPersonalityAffectsChoices() {
  NavGraph g;
  maps::MakeDeadEndMap(g, 8, 2);
  g.ComputeDegrees();
  int dests_a[4], dests_b[4];
  {
    SimBot bot;
    NavPersonality p;
    p.explore_bias = 0.9f;
    p.deadend_aversion = 0.0f;
    p.important_bias = 0.0f;
    bot.Configure(p, 1u);
    int seen = 0;
    int last = -1;
    for (int t = 0; t < 4000 && seen < 4; ++t) {
      const NavCommand c = bot.Step(g, t, false, false, 0.0, 0.0);
      if (c.reached_destination && c.dest_node != last) {
        last = c.dest_node;
        dests_a[seen++] = c.dest_node;
      }
    }
  }
  {
    SimBot bot;
    NavPersonality p;
    p.explore_bias = 0.1f;
    p.deadend_aversion = 0.9f;
    p.important_bias = 0.0f;
    bot.Configure(p, 1u);
    int seen = 0;
    int last = -1;
    for (int t = 0; t < 4000 && seen < 4; ++t) {
      const NavCommand c = bot.Step(g, t, false, false, 0.0, 0.0);
      if (c.reached_destination && c.dest_node != last) {
        last = c.dest_node;
        dests_b[seen++] = c.dest_node;
      }
    }
  }
  bool differ = false;
  for (int i = 0; i < 4; ++i) {
    if (dests_a[i] != dests_b[i]) differ = true;
  }
  CHECK(differ);
}

// Determinism: same map + same seeds + same inputs => identical telemetry
// and identical final positions across two independent runs.
static void TestMultiBotDeterminism() {
  const uint32_t seeds[4] = {1u, 2u, 3u, 4u};
  double final_x[2][4], final_z[2][4];
  int searches[2][4], expansions[2][4], reached[2][4];
  for (int run = 0; run < 2; ++run) {
    NavGraph g;
    maps::MakeGrid(g, 10, 10);
    g.ComputeDegrees();
    SimBot bots[4];
    for (int b = 0; b < 4; ++b) {
      NavPersonality p;
      p.route_variance = 0.15f;
      bots[b].Configure(p, seeds[b]);
      bots[b].Place((b % 2) * 36.0, (b / 2) * 36.0);
    }
    for (int t = 0; t < 600; ++t) {
      for (int b = 0; b < 4; ++b) {
        bots[b].Step(g, t, false, false, 0.0, 0.0);
      }
    }
    for (int b = 0; b < 4; ++b) {
      final_x[run][b] = bots[b].x;
      final_z[run][b] = bots[b].z;
      searches[run][b] = bots[b].agent.searches_total();
      expansions[run][b] = bots[b].agent.expansions_total();
      reached[run][b] = bots[b].agent.destinations_reached();
    }
  }
  for (int b = 0; b < 4; ++b) {
    CHECK(final_x[0][b] == final_x[1][b]);
    CHECK(final_z[0][b] == final_z[1][b]);
    CHECK(searches[0][b] == searches[1][b]);
    CHECK(expansions[0][b] == expansions[1][b]);
    CHECK(reached[0][b] == reached[1][b]);
    CHECK(reached[0][b] >= 1);
  }
  // Different seeds should give at least two different final positions.
  bool any_differ = false;
  for (int b = 1; b < 4; ++b) {
    if (final_x[0][0] != final_x[0][b] || final_z[0][0] != final_z[0][b]) {
      any_differ = true;
    }
  }
  CHECK(any_differ);
}

// Personality bridge: monotone + clamped mapping used by the seam test.
static void TestPersonalityFromTraits() {
  const NavPersonality aggr = NavPersonalityFromTraits(0.9f, 0.1f, 1.0f, 360.0f);
  const NavPersonality caut = NavPersonalityFromTraits(0.1f, 0.9f, 0.5f, 120.0f);
  CHECK(aggr.explore_bias > caut.explore_bias);
  CHECK(caut.important_bias > aggr.important_bias);
  CHECK(caut.deadend_aversion > aggr.deadend_aversion);
  CHECK(aggr.patrol_min_dist > caut.patrol_min_dist);
  CHECK(aggr.walk_factor == 1.0f);
  CHECK(caut.walk_factor == 0.5f);
  CHECK(NavPersonalityFromTraits(5.0f, -3.0f, 0.01f, 1.0f).walk_factor == 0.2f);
  CHECK(NavPersonalityFromTraits(0.0f, 0.0f, 1.0f, 1.0f).turn_rate_deg_s == 30.0f);
}

// Dead agent must not emit movement.
static void TestDeadAgentIdle() {
  NavGraph g;
  maps::MakeCorridor(g, 4);
  g.ComputeDegrees();
  SimBot bot;
  bot.Configure(NavPersonality(), 1u);
  NavAgentInput in;
  in.tick = 0;
  in.x = 0.0;
  in.y = 0.0;
  in.z = 0.0;
  in.yaw_deg = 0.0;
  in.alive = false;
  in.movement_requested = false;
  in.has_target = false;
  in.target_visible = false;
  in.target_x = in.target_y = in.target_z = 0.0;
  const NavCommand c = bot.agent.Step(g, in);
  CHECK(!c.active);
  CHECK(c.mode == NavMode::kIdle);
  CHECK(c.forward == 0.0);
}

int main() {
  TestPatrolWalksAndReaches();
  TestUnreachableGoalScans();
  TestPursueSteersCoarse();
  TestGoalChangeAndReposition();
  TestStuckTriggersRecovery();
  TestTeleportGuard();
  TestBudgetedSearchMakesProgress();
  TestPersonalityAffectsChoices();
  TestMultiBotDeterminism();
  TestPersonalityFromTraits();
  TestDeadAgentIdle();
  if (g_failures == 0) {
    std::printf("NAV AGENT PASS (0 failures, %d checks)\n", g_checks);
    return 0;
  }
  std::printf("NAV AGENT FAIL (%d failures)\n", g_failures);
  return 1;
}
