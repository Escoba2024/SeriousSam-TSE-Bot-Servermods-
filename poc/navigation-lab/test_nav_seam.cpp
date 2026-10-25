// test_nav_seam.cpp - integration seam proof: navigation-lab <-> botcore.
//
// Includes the EXISTING botcore headers read-only (no botcore file is
// modified) and proves the three seams the integration plan relies on:
//
//   1. Map seam: the same per-map waypoint file (Scripts format) feeds both
//      botcore's WaypointGraph and navlab's NavGraph; structure and
//      reachability agree.
//   2. Personality seam: all six shipped botcore personas map onto
//      NavPersonality through NavPersonalityFromTraits() without violating
//      any navlab invariant.
//   3. Command seam: a combat BotCommand (bot_human.h) and a navlab
//      NavCommand merge deterministically - combat leads when it has a
//      target, navigation drives otherwise.
//
// Build: g++ -std=c++17 -O2 -Wall -Wextra -o test_nav_seam test_nav_seam.cpp

#include <cstdio>
#include <cmath>
#include <cstring>
#include "nav_agent.h"
#include "nav_maps.h"

// --- existing botcore interfaces, READ-ONLY ------------------------------
#include "../botcore/bot_profile.h"
#include "../botcore/bot_human.h"
#include "../botcore/botcore_ai.h"

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
using botcore::BotCommand;
using botcore::kPersonalityCount;
using botcore::PersonalityFor;
using botcore::PersonalityParams;
using botcore::WaypointGraph;

/* ------------------------------------------------------------------------ */
/* Seam 1: shared waypoint-file format                                       */
/* ------------------------------------------------------------------------ */

// Synthetic map in the exact Scripts waypoint-file format both parsers eat.
// Layout: two rooms joined by a corridor, plus an isolated island (proves
// unreachable handling across both implementations).
static const char* kWaypointFile[] = {
  "# room A (nodes 0..3)",
  "node 0 0 0",
  "node 4 0 0",
  "node 4 0 4",
  "node 0 0 4",
  "edge 0 1",
  "edge 1 2",
  "edge 2 3",
  "edge 3 0",
  "// corridor to room B",
  "node 12 0 0",
  "node 20 0 0",
  "edge 1 4",
  "edge 4 5",
  "# room B (nodes 6..9)",
  "node 24 0 0",
  "node 28 0 0",
  "node 28 0 4",
  "node 24 0 4",
  "edge 5 6",
  "edge 6 7",
  "edge 7 8",
  "edge 8 9",
  "edge 9 6",
  "# island - unreachable on purpose",
  "node 60 0 60",
  "node 64 0 60",
  "edge 10 11",
};

static void TestMapSeam() {
  WaypointGraph wg;    // botcore (read-only include)
  NavGraph ng;         // navigation-lab
  const int lines = static_cast<int>(sizeof(kWaypointFile) /
                                     sizeof(kWaypointFile[0]));
  for (int i = 0; i < lines; ++i) {
    CHECK(wg.ParseLine(kWaypointFile[i]));
    CHECK(ng.ParseLine(kWaypointFile[i]));
  }
  ng.ComputeDegrees();

  // Identical node count and positions.
  CHECK(wg.node_count() == ng.node_count());
  CHECK(ng.node_count() == 12);
  for (int i = 0; i < ng.node_count(); ++i) {
    double x = 0.0, y = 0.0, z = 0.0;
    CHECK(wg.NodePosition(i, &x, &y, &z));
    CHECK(std::fabs(x - ng.node(i).x) < 1e-9);
    CHECK(std::fabs(z - ng.node(i).z) < 1e-9);
  }

  // Reachability agreement on a full pair sweep: botcore NextHop() (BFS by
  // hop count) vs navlab A* (by cost). Same graph, same answers.
  NavAStar search;
  NavSearchConfig cfg;
  for (int a = 0; a < ng.node_count(); ++a) {
    for (int b = 0; b < ng.node_count(); ++b) {
      const bool bc_reach = wg.NextHop(a, b) >= 0;
      const NavPath p = search.Find(ng, a, b, cfg);
      const bool nl_reach = (p.status == NavSearchStatus::kFound);
      CHECK(bc_reach == nl_reach);
    }
  }

  // The island is unreachable from room A in BOTH implementations.
  CHECK(wg.NextHop(0, 10) < 0);
  const NavPath island = search.Find(ng, 0, 10, cfg);
  CHECK(island.status == NavSearchStatus::kUnreachable);
  // Room A -> room B is reachable and the navlab route is sane.
  const NavPath across = search.Find(ng, 0, 7, cfg);
  CHECK(across.status == NavSearchStatus::kFound);
  CHECK(across.nodes[0] == 0 && across.nodes[across.count - 1] == 7);
}

/* ------------------------------------------------------------------------ */
/* Seam 2: personality bridge                                                */
/* ------------------------------------------------------------------------ */

static void TestPersonalitySeam() {
  // Every shipped botcore persona must produce a usable NavPersonality.
  for (int persona = 0; persona < kPersonalityCount; ++persona) {
    const PersonalityParams& p = PersonalityFor(persona);
    // The integration reads the persona's turn rate from SkillParams; here
    // the bridge is exercised with the persona's aggression/caution and a
    // representative movement profile (walk 10 m/s, 240 deg/s).
    const NavPersonality np =
        NavPersonalityFromTraits(static_cast<float>(p.aggression),
                                 static_cast<float>(p.caution), 1.0f, 240.0f);
    // Navlab invariants hold for every persona.
    CHECK(np.explore_bias >= 0.0f && np.explore_bias <= 1.0f);
    CHECK(np.important_bias >= 0.0f && np.important_bias <= 1.0f);
    CHECK(np.deadend_aversion >= 0.0f && np.deadend_aversion <= 1.0f);
    CHECK(np.walk_factor >= 0.2f && np.walk_factor <= 1.0f);
    CHECK(np.turn_rate_deg_s >= 30.0f);
    CHECK(np.repath_cooldown > 0 && np.stuck_window > 1);
    CHECK(np.patrol_min_dist > 0.0f);

    // The persona must actually drive the agent: configure + one step works
    // for every persona on a synthetic map (no persona dead-locks the FSM).
    NavGraph g;
    maps::MakeGrid(g, 5, 5);
    g.ComputeDegrees();
    NavAgent agent;
    agent.Configure(np, static_cast<uint32_t>(persona + 1));
    NavAgentInput in;
    in.tick = 0;
    in.x = 0.0;
    in.y = 0.0;
    in.z = 0.0;
    in.yaw_deg = 0.0;
    in.alive = true;
    in.movement_requested = false;
    in.has_target = false;
    in.target_visible = false;
    in.target_x = in.target_y = in.target_z = 0.0;
    const NavCommand c = agent.Step(g, in);
    CHECK(c.mode == NavMode::kPatrol);
    CHECK(c.active);
  }

  // Sanity: the shipped personas span different temperaments, and the
  // bridge preserves the ordering (more aggression -> more exploration).
  const PersonalityParams& calm = PersonalityFor(0);
  const PersonalityParams& rash = PersonalityFor(kPersonalityCount - 1);
  bool any_differs = false;
  for (int i = 1; i < kPersonalityCount; ++i) {
    if (std::fabs(PersonalityFor(i).aggression -
                  PersonalityFor(0).aggression) > 1e-9) {
      any_differs = true;
    }
  }
  CHECK(any_differs);
  const NavPersonality n_calm =
      NavPersonalityFromTraits(static_cast<float>(calm.aggression),
                               static_cast<float>(calm.caution), 1.0f, 240.0f);
  const NavPersonality n_rash =
      NavPersonalityFromTraits(static_cast<float>(rash.aggression),
                               static_cast<float>(rash.caution), 1.0f, 240.0f);
  if (rash.aggression > calm.aggression) {
    CHECK(n_rash.explore_bias > n_calm.explore_bias);
  }
}

/* ------------------------------------------------------------------------ */
/* Seam 3: command merge (combat leads, navigation fills the gaps)           */
/* ------------------------------------------------------------------------ */

// Merge rule as it will live in the BotDriver tick (implemented here in
// test scope; the lab must not modify botcore):
//  - combat has a target            -> combat owns yaw/forward/fire;
//    nav contributes nothing (it only steers coarsely inside NavAgent).
//  - no combat target, nav active   -> nav yaw_delta/forward drive the bot.
//  - nothing active                 -> stand still.
static void MergeCommands(const BotCommand& combat, const NavCommand& nav,
                          bool combat_drives, BotCommand* out) {
  *out = combat;
  if (combat_drives) return;  // combat layer already set yaw/forward/fire
  out->fire = false;
  if (nav.active) {
    out->yaw_delta_deg = nav.yaw_delta_deg;
    out->forward = nav.forward;
  } else {
    out->yaw_delta_deg = 0.0;
    out->forward = 0.0;
  }
}

static void TestCommandSeam() {
  NavGraph g;
  maps::MakeCorridor(g, 6);
  g.ComputeDegrees();
  NavAgent agent;
  agent.Configure(NavPersonality(), 1u);

  NavAgentInput in;
  in.tick = 0;
  in.x = 0.0;
  in.y = 0.0;
  in.z = 0.0;
  in.yaw_deg = -90.0;  // already facing down the corridor (+x)
  in.alive = true;
  in.movement_requested = false;
  in.has_target = false;
  in.target_visible = false;
  in.target_x = in.target_y = in.target_z = 0.0;

  // --- patrol tick: navigation drives the merged BotCommand --------------
  const NavCommand nav = agent.Step(g, in);
  CHECK(nav.mode == NavMode::kPatrol && nav.active);
  BotCommand combat;  // default-constructed: target = -1 (nothing to fight)
  CHECK(combat.target == -1);
  BotCommand merged;
  MergeCommands(combat, nav, /*combat_drives=*/false, &merged);
  CHECK(merged.forward == nav.forward);
  CHECK(merged.yaw_delta_deg == nav.yaw_delta_deg);
  CHECK(!merged.fire);

  // --- combat tick: combat BotCommand wins untouched ---------------------
  BotCommand fighting;
  fighting.target = 3;
  fighting.target_visible = true;
  fighting.yaw_delta_deg = 5.0;
  fighting.fire = true;
  BotCommand merged2;
  MergeCommands(fighting, nav, /*combat_drives=*/true, &merged2);
  CHECK(merged2.target == 3);
  CHECK(merged2.yaw_delta_deg == 5.0);
  CHECK(merged2.fire);

  // --- perception hand-off: BotCommand target state maps onto nav input --
  in.has_target = (fighting.target >= 0);
  in.target_visible = fighting.target_visible;
  CHECK(in.has_target && in.target_visible);
  const NavCommand pursue = agent.Step(g, in);
  CHECK(pursue.mode == NavMode::kPursue);
}

int main() {
  TestMapSeam();
  TestPersonalitySeam();
  TestCommandSeam();
  if (g_failures == 0) {
    std::printf("NAV SEAM PASS (0 failures, %d checks)\n", g_checks);
    return 0;
  }
  std::printf("NAV SEAM FAIL (%d failures)\n", g_failures);
  return 1;
}
