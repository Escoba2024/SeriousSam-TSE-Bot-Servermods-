// Engine-free bridge tests: verify that BotDriverPolicy can be driven from
// plain numeric snapshots and that the resulting DriverAction uses the native
// Retail 1.07 conventions expected by BotDriver.cpp.
#include "bot_driver_policy_bridge.h"

#include <cmath>
#include <cstdio>

using namespace botcore;

static int g_failures = 0;
static int g_checks = 0;

#define CHECK(cond, msg)                                    \
  do {                                                      \
    ++g_checks;                                             \
    if (!(cond)) {                                          \
      std::printf("FAIL: %s (line %d)\n", msg, __LINE__);    \
      ++g_failures;                                         \
    }                                                       \
  } while (0)

static const double kDt = 1.0 / 20.0;

static WaypointGraph MakeLineGraph() {
  WaypointGraph g;
  g.AddNode(0, 0, 0);
  g.AddNode(10, 0, 0);
  g.AddNode(20, 0, 0);
  g.Link(0, 1);
  g.Link(1, 2);
  return g;
}

static void TestSnapshotBuilders() {
  SenseInput s = BuildSenseInput(3, 1.0, 2.0, 3.0, 0.5, 0.0, -0.5, 75.0, false);
  CHECK(s.index == 3, "snapshot preserves index");
  CHECK(s.alive, "positive health -> alive");
  CHECK(!s.local, "local flag preserved");

  SenseInput dead = BuildSenseInput(2, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, true);
  CHECK(!dead.alive, "zero health -> not alive");

  NavWorld w = BuildNavWorld(5.0, 1.5, -2.0, -90.0, 0.0, 80.0, 100.0, true);
  CHECK(std::fabs(w.x - 5.0) < 1e-9, "nav world x preserved");
  CHECK(w.alive, "nav world alive preserved");

  FloorProbes p = BuildFloorProbes(3.0, 2.5, 4.0, 1.0);
  CHECK(p.front_m == 3.0, "front probe preserved");
  CHECK(p.step_m == 1.0, "step probe preserved");
}

static void TestActionTranslation() {
  DriverCommand cmd;
  cmd.forward = 0.75;
  cmd.strafe = -0.25;
  cmd.yaw_delta_deg = 15.0;
  cmd.pitch_delta_deg = -3.0;
  cmd.fire = true;
  cmd.weapon = 8;
  cmd.active = true;

  DriverAction a = ApplyCommandToAction(cmd);
  CHECK(a.forward == 0.75, "forward copied");
  CHECK(a.strafe == -0.25, "strafe copied");
  CHECK(a.yaw_delta_deg == 15.0, "yaw delta copied");
  CHECK(a.pitch_delta_deg == -3.0, "pitch delta copied");
  CHECK(a.fire, "fire copied");
  CHECK(a.weapon == 8, "weapon copied");
  CHECK(a.active, "active copied");
}

static void TestWeaponSelectButtons() {
  CHECK(DriverWeaponSelectButtons(2) == (2u << 14), "colt select buttons");
  CHECK(DriverWeaponSelectButtons(8) == (8u << 14), "rocket select buttons");
}

static void TestEndToEndPolicyTick() {
  BotProfile profile{};
  BuildProfile(3, 0, 12345u, "BOT-Bridge", &profile);
  WaypointGraph g = MakeLineGraph();
  BotDriverPolicy policy;
  policy.Configure(&profile, &g);

  DriverWorld world;
  world.nav = BuildNavWorld(0.0, 0.0, 0.0, -90.0, 0.0, 100.0, 100.0, true);
  world.players = nullptr;
  world.player_count = 0;
  world.items = nullptr;
  world.item_count = 0;
  world.probes = BuildFloorProbes(10.0, 10.0, 10.0);
  world.retreat_requested = false;

  DriverAction a = BotDriverPolicyTick(policy, world, 0, kDt);
  CHECK(a.active, "policy tick produces active action");
  CHECK(a.forward > 0.0, "no target -> forward movement");
  CHECK(a.weapon == 2 || a.weapon == 1, "idle weapon falls back to knife/colt");

  // Add a visible enemy straight ahead (bot faces -z).
  SenseInput enemy = BuildSenseInput(1, 0.0, 0.0, -20.0, 0.0, 0.0, 0.0, 100.0, false);
  world.players = &enemy;
  world.player_count = 1;
  world.nav.yaw_deg = 0.0;

  int acquired_tick = -1;
  for (int t = 1; t <= 30; ++t) {
    a = BotDriverPolicyTick(policy, world, t, kDt);
    if (a.fire) {
      acquired_tick = t;
      break;
    }
  }
  CHECK(acquired_tick >= 0, "bridge eventually fires at visible enemy");
}

int main() {
  TestSnapshotBuilders();
  TestActionTranslation();
  TestWeaponSelectButtons();
  TestEndToEndPolicyTick();

  std::printf("BOT DRIVER POLICY BRIDGE %s (%d checks, %d failures)\n",
              g_failures ? "FAIL" : "PASS", g_checks, g_failures);
  return g_failures ? 1 : 0;
}
