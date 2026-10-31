// Engine-free integration test for the combat/navigation coordinator.
#include "bot_driver_policy.h"

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

static SenseInput MakeEnemy(int index, double x, double y, double z) {
  SenseInput s{};
  s.index = index;
  s.x = x;
  s.y = y;
  s.z = z;
  s.vx = s.vy = s.vz = 0.0;
  s.health = 100.0;
  s.alive = true;
  s.local = false;
  return s;
}

static WaypointGraph MakeLineGraph() {
  WaypointGraph g;
  g.AddNode(0, 0, 0);
  g.AddNode(10, 0, 0);
  g.AddNode(20, 0, 0);
  g.AddNode(30, 0, 0);
  g.Link(0, 1);
  g.Link(1, 2);
  g.Link(2, 3);
  return g;
}

static void TestCombatWinsWhenTargetVisible() {
  BotProfile profile{};
  BuildProfile(3, 0, 12345u, "BOT-Test", &profile);
  WaypointGraph g = MakeLineGraph();
  BotDriverPolicy policy;
  policy.Configure(&profile, &g);

  DriverWorld w;
  w.nav.alive = true;
  w.nav.x = w.nav.y = w.nav.z = 0.0;
  // Face the first real waypoint at +x.  In botcore yaw convention
  // (atan2(-dx,-dz)) yaw = -90 deg points to +x.
  w.nav.yaw_deg = -90.0;
  w.nav.health = 100.0;
  w.nav.max_health = 100.0;
  w.nav.has_target = false;
  w.retreat_requested = false;
  w.players = nullptr;
  w.player_count = 0;
  w.items = nullptr;
  w.item_count = 0;
  w.probes.front_m = w.probes.left_m = w.probes.right_m = 10.0;

  // No target: navigation should propose movement straight away because we
  // already face the first waypoint.
  DriverCommand cmd = policy.Update(w, 0, kDt);
  CHECK(cmd.source == DriverCommand::Source::kNavigation,
        "no target -> navigation controls movement");
  CHECK(cmd.forward > 0.0, "navigation moves forward when no target");

  // Add visible enemy straight ahead (in -z, i.e. yaw = 0).
  SenseInput enemy = MakeEnemy(1, 0, 0, -20);
  w.players = &enemy;
  w.player_count = 1;
  // Turn to face the enemy so the perception FOV gate passes.
  w.nav.yaw_deg = 0.0;
  // HumanBotPolicy enforces a reaction delay; run enough ticks for the
  // average-tier bot (reaction_s ~ 0.30 -> ~6 ticks) to accept the target.
  int acquired_tick = -1;
  for (int t = 1; t <= 30; ++t) {
    cmd = policy.Update(w, t, kDt);
    if (cmd.target == 1) {
      acquired_tick = t;
      break;
    }
  }
  CHECK(acquired_tick >= 0, "combat acquires visible enemy after reaction delay");
  CHECK(cmd.source == DriverCommand::Source::kCombat,
        "visible target -> combat controls movement");
}

static void TestRetreatOverridesCombat() {
  BotProfile profile{};
  BuildProfile(3, 0, 12345u, "BOT-Test", &profile);
  WaypointGraph g = MakeLineGraph();
  BotDriverPolicy policy;
  policy.Configure(&profile, &g);

  SenseInput enemy = MakeEnemy(1, 0, 0, -20);
  DriverWorld w;
  w.nav.alive = true;
  w.nav.x = w.nav.y = w.nav.z = 0.0;
  w.nav.yaw_deg = 0.0;
  w.nav.health = 20.0;
  w.nav.max_health = 100.0;
  w.nav.has_target = true;
  w.retreat_requested = true;
  w.players = &enemy;
  w.player_count = 1;
  w.items = nullptr;
  w.item_count = 0;
  w.probes.front_m = w.probes.left_m = w.probes.right_m = 10.0;

  DriverCommand cmd = policy.Update(w, 0, kDt);
  CHECK(cmd.source == DriverCommand::Source::kNavigation,
        "retreat -> navigation controls movement even with target");
}

static void TestNoGraphFallsBackToCombatIdle() {
  BotProfile profile{};
  BuildProfile(3, 0, 12345u, "BOT-Test", &profile);
  BotDriverPolicy policy;
  policy.Configure(&profile, nullptr);  // no graph

  DriverWorld w;
  w.nav.alive = true;
  w.nav.x = w.nav.y = w.nav.z = 0.0;
  w.nav.yaw_deg = 0.0;
  w.nav.health = 100.0;
  w.nav.max_health = 100.0;
  w.nav.has_target = false;
  w.retreat_requested = false;
  w.players = nullptr;
  w.player_count = 0;
  w.items = nullptr;
  w.item_count = 0;

  DriverCommand cmd = policy.Update(w, 0, kDt);
  CHECK(cmd.source == DriverCommand::Source::kIdle,
        "no graph and no target -> idle scanning");
}

static void TestWeaponAndFireAlwaysFromCombat() {
  BotProfile profile{};
  BuildProfile(3, 0, 12345u, "BOT-Test", &profile);
  WaypointGraph g = MakeLineGraph();
  BotDriverPolicy policy;
  policy.Configure(&profile, &g);

  // Run several ticks until the bot fires at a visible enemy.
  SenseInput enemy = MakeEnemy(1, 0, 0, -10);
  DriverWorld w;
  w.nav.alive = true;
  w.nav.x = w.nav.y = w.nav.z = 0.0;
  w.nav.yaw_deg = 0.0;
  w.nav.health = 100.0;
  w.nav.max_health = 100.0;
  w.nav.has_target = false;
  w.retreat_requested = false;
  w.players = &enemy;
  w.player_count = 1;
  w.items = nullptr;
  w.item_count = 0;
  w.probes.front_m = w.probes.left_m = w.probes.right_m = 10.0;

  bool saw_fire = false;
  for (int i = 0; i < 200; ++i) {
    DriverCommand cmd = policy.Update(w, i, kDt);
    if (cmd.fire) { saw_fire = true; break; }
  }
  CHECK(saw_fire, "coordinator eventually fires at visible enemy");
}

int main() {
  TestCombatWinsWhenTargetVisible();
  TestRetreatOverridesCombat();
  TestNoGraphFallsBackToCombatIdle();
  TestWeaponAndFireAlwaysFromCombat();

  std::printf("BOT DRIVER POLICY %s (%d checks, %d failures)\n",
              g_failures ? "FAIL" : "PASS", g_checks, g_failures);
  return g_failures ? 1 : 0;
}
