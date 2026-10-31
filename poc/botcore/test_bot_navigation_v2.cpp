// Engine-free tests for Navigation 2.0: A* pathfinding, pit avoidance and
// item utility. Deterministic, no Retail / SDK / Windows required.
#include "bot_navigation_v2.h"

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

static WaypointGraph MakeLineGraph() {
  WaypointGraph g;
  // Straight line: 0 -> 1 -> 2 -> 3
  g.AddNode(0, 0, 0);   // 0
  g.AddNode(10, 0, 0);  // 1
  g.AddNode(20, 0, 0);  // 2
  g.AddNode(30, 0, 0);  // 3
  g.Link(0, 1);
  g.Link(1, 2);
  g.Link(2, 3);
  return g;
}

static WaypointGraph MakeBranchGraph() {
  WaypointGraph g;
  // 0 -- 1 -- 2
  //        |
  //        3 -- 4
  g.AddNode(0, 0, 0);    // 0
  g.AddNode(10, 0, 0);   // 1
  g.AddNode(20, 0, 0);   // 2
  g.AddNode(20, 10, 0);  // 3
  g.AddNode(30, 10, 0);  // 4
  g.Link(0, 1);
  g.Link(1, 2);
  g.Link(2, 3);
  g.Link(3, 4);
  return g;
}

static void TestAStarPathfinding() {
  AStarPathfinder pf;
  int path[WaypointGraph::kMaxNodes];
  int len = 0;

  // Same node.
  WaypointGraph g0;
  g0.AddNode(5, 5, 5);
  CHECK(pf.FindPath(g0, 0, 0, path, &len, 16), "trivial path start==goal");
  CHECK(len == 1 && path[0] == 0, "trivial path length 1");

  // Straight line.
  WaypointGraph g1 = MakeLineGraph();
  CHECK(pf.FindPath(g1, 0, 3, path, &len, 16), "line graph path found");
  CHECK(len == 4, "line graph path uses all 4 nodes");
  for (int i = 0; i < 4; ++i) CHECK(path[i] == i, "line path order");

  // Branch: 0 to 4 should go 0-1-2-3-4.
  WaypointGraph g2 = MakeBranchGraph();
  CHECK(pf.FindPath(g2, 0, 4, path, &len, 16), "branch graph path found");
  CHECK(len == 5, "branch path length");
  CHECK(path[0] == 0 && path[1] == 1 && path[2] == 2 && path[3] == 3 && path[4] == 4,
        "branch path order");

  // Invalid goal.
  CHECK(!pf.FindPath(g2, 0, 99, path, &len, 16), "invalid goal rejected");
}

static void TestPitAvoidance() {
  NavWorld w;
  w.alive = true;
  w.yaw_deg = 0.0;
  PitAvoidance pit;
  FloorProbes safe;
  safe.front_m = safe.left_m = safe.right_m = 10.0;
  CHECK(pit.Avoid(w, safe) == 0.0, "safe floor needs no correction");
  CHECK(!pit.BlockForward(w, safe), "safe floor allows forward");

  FloorProbes front_pit;
  front_pit.front_m = 0.5;
  front_pit.left_m = front_pit.right_m = 10.0;
  double a = pit.Avoid(w, front_pit);
  CHECK(a < 0.0, "front pit steers left when right is clear");
  CHECK(pit.BlockForward(w, front_pit), "front pit blocks forward");

  FloorProbes both_bad;
  both_bad.front_m = 0.5;
  both_bad.left_m = 0.5;
  both_bad.right_m = 0.5;
  a = pit.Avoid(w, both_bad);
  CHECK(std::fabs(a - 180.0) < 1e-6, "pit on all sides turns back");
}

static void TestItemUtility() {
  BotProfile profile{};
  BuildProfile(3, 0, 12345u, "BOT-Test", &profile);
  ItemUtility util;
  util.Configure(&profile);

  NavWorld w;
  w.health = 30.0;
  w.max_health = 100.0;
  w.x = w.y = w.z = 0.0;

  ItemInfo items[3];
  items[0] = {0, 10, 0, 0, ItemType::kHealth, 50, 100, true};
  items[1] = {1, 50, 0, 0, ItemType::kAmmo, 20, 100, true};   // far away
  items[2] = {2, 20, 0, 0, ItemType::kArmor, 50, 100, true};

  int best = util.SelectBestItem(items, 3, w);
  CHECK(best == 0, "low health prefers health pack");

  w.health = 100.0;
  best = util.SelectBestItem(items, 3, w);
  CHECK(best == 2, "full health prefers armor over far ammo");

  items[0].reachable = false;
  best = util.SelectBestItem(items, 3, w);
  CHECK(best == 2, "unreachable health ignored");
}

static void TestNavigationPlanner() {
  BotProfile profile{};
  BuildProfile(3, 0, 12345u, "BOT-Test", &profile);

  WaypointGraph g = MakeLineGraph();
  NavigationPlanner planner;
  planner.Configure(&profile, &g);

  // No graph -> idle.
  NavigationPlanner no_graph;
  no_graph.Configure(&profile, nullptr);
  NavWorld w;
  w.alive = true;
  w.x = w.y = w.z = 0.0;
  w.yaw_deg = 0.0;
  w.has_target = false;
  FloorProbes safe;
  safe.front_m = safe.left_m = safe.right_m = 10.0;
  NavCommand cmd = no_graph.Update(w, nullptr, 0, safe, false);
  CHECK(!cmd.active, "planner without graph stays idle");

  // With graph and no target, should start moving. Face the first real
  // waypoint (+x) so that forward motion is allowed immediately.
  w.yaw_deg = -90.0;
  cmd = planner.Update(w, nullptr, 0, safe, false);
  CHECK(cmd.active, "planner with graph activates");
  CHECK(cmd.forward > 0.0, "planner moves forward");
  CHECK(cmd.mode == NavCommand::Mode::kPathToWaypoint, "default mode is path");

  // Combat target should disable navigation.
  w.has_target = true;
  cmd = planner.Update(w, nullptr, 0, safe, false);
  CHECK(!cmd.active, "navigation yields to combat target");

  // Retreat should activate even with target.
  w.has_target = true;
  cmd = planner.Update(w, nullptr, 0, safe, true);
  CHECK(cmd.active, "retreat activates despite target");
  CHECK(cmd.mode == NavCommand::Mode::kRetreat, "retreat mode set");

  // Low health should fetch health item. Item is at waypoint 3 (+x).
  w.has_target = false;
  w.health = 20.0;
  w.yaw_deg = -90.0;
  ItemInfo health = {0, 30, 0, 0, ItemType::kHealth, 50, 100, true};
  cmd = planner.Update(w, &health, 1, safe, false);
  CHECK(cmd.active, "low health seeks item");
  CHECK(cmd.mode == NavCommand::Mode::kFetchItem, "fetch-item mode set");
}

static void TestOwnershipNoPolicyDuplication() {
  // Navigation must never pick a target or pull the trigger. Those remain the
  // exclusive responsibility of HumanBotPolicy / combat layer. NavCommand has
  // no target field and no fire bit by design; this test verifies that the
  // planner still produces movement while never touching combat state.
  BotProfile profile{};
  BuildProfile(3, 0, 12345u, "BOT-Test", &profile);
  WaypointGraph g = MakeLineGraph();
  NavigationPlanner planner;
  planner.Configure(&profile, &g);
  NavWorld w;
  w.alive = true;
  w.x = w.y = w.z = 0.0;
  w.yaw_deg = -90.0;
  w.has_target = false;
  FloorProbes safe;
  safe.front_m = safe.left_m = safe.right_m = 10.0;
  NavCommand cmd = planner.Update(w, nullptr, 0, safe, false);
  CHECK(cmd.active, "navigation produces movement");
  // No target/fire fields exist to check; ownership is enforced by type layout.
}

int main() {
  TestAStarPathfinding();
  TestPitAvoidance();
  TestItemUtility();
  TestNavigationPlanner();
  TestOwnershipNoPolicyDuplication();

  std::printf("NAVIGATION V2 %s (%d checks, %d failures)\n",
              g_failures ? "FAIL" : "PASS", g_checks, g_failures);
  return g_failures ? 1 : 0;
}
