// test_nav_astar.cpp - offline unit tests for navlab::NavAStar.
// Synthetic maps only. Run: ./test_nav_astar  (exit 0 = PASS)
#include <cstdio>

#include "nav_astar.h"
#include "nav_graph.h"
#include "nav_maps.h"

using namespace navlab;

static int g_failures = 0;
static int g_checks = 0;
#define CHECK(cond)                                                        \
  do {                                                                     \
    ++g_checks;                                                            \
    if (!(cond)) {                                                         \
      std::printf("FAIL %s:%d: %s\n", __FILE__, __LINE__, #cond);          \
      ++g_failures;                                                        \
    }                                                                      \
  } while (0)

static bool PathContains(const NavPath& p, int node) {
  for (int i = 0; i < p.count; ++i) {
    if (p.nodes[i] == node) return true;
  }
  return false;
}

static void TestReachable() {
  NavGraph g;
  maps::MakeCorridor(g, 6, 4.0);  // 0..5, 4 m apart
  NavAStar search;
  NavSearchConfig cfg;  // budget 256, no variance
  const NavPath p = search.Find(g, 0, 5, cfg);
  CHECK(p.status == NavSearchStatus::kFound);
  CHECK(p.count == 6);
  CHECK(p.nodes[0] == 0 && p.nodes[5] == 5);
  CHECK(p.cost > 19.9f && p.cost < 20.1f);  // 5 hops x 4 m
  // Degenerate: start == goal.
  const NavPath d = search.Find(g, 3, 3, cfg);
  CHECK(d.status == NavSearchStatus::kFound && d.count == 1);
  // Invalid args.
  const NavPath bad = search.Find(g, -1, 5, cfg);
  CHECK(bad.status == NavSearchStatus::kInvalidArgs);
}

static void TestGridOptimality() {
  // 8x8 open grid, 4 m spacing: shortest path (0,0)->(7,7) = 14 hops = 56 m.
  NavGraph g;
  maps::MakeGrid(g, 8, 8, 4.0);
  CHECK(g.node_count() == 64);
  NavAStar search;
  NavSearchConfig cfg;
  const int from = 0;             // (0,0)
  const int to = 7 * 8 + 7;       // (7,7)
  const NavPath p = search.Find(g, from, to, cfg);
  CHECK(p.status == NavSearchStatus::kFound);
  CHECK(p.count == 15);  // 14 hops
  CHECK(p.cost > 55.9f && p.cost < 56.1f);
}

static void TestUnreachable() {
  // Two 4x4 grids, no connection.
  NavGraph g;
  maps::MakeDisconnected(g, 4, 4.0, 100.0);
  NavAStar search;
  NavSearchConfig cfg;
  const int here = 0;             // component A
  const int there = 16 + 15;      // component B
  const NavPath p = search.Find(g, here, there, cfg);
  CHECK(p.status == NavSearchStatus::kUnreachable);
  CHECK(p.count >= 1);            // partial route exists (at least the start)
  CHECK(p.nodes[0] == here);
  // The partial route stays inside component A.
  for (int i = 0; i < p.count; ++i) CHECK(p.nodes[i] < 16);
}

static void TestBlockedDetour() {
  // 6x6 grid; wall down the middle except a gate at row 0. Blocking the gate
  // must force the long way around... there is none (wall spans fully), so
  // instead: wall with TWO gates, block one, expect the other to be used.
  struct Ctx { int wall_x; int gate_a; int gate_b; };
  struct WallFn {
    static bool IsWall(int y, int x, void* ctx) {
      Ctx* c = static_cast<Ctx*>(ctx);
      return x == c->wall_x && y != c->gate_a && y != c->gate_b;
    }
  };
  Ctx ctx{3, 0, 5};
  NavGraph g;
  maps::MakeGrid(g, 6, 6, 4.0, WallFn::IsWall, &ctx);
  NavAStar search;
  NavSearchConfig cfg;
  const int from = 2 * 6 + 1;   // left of the wall, row 2
  const int to = 2 * 6 + 4;     // right of the wall, row 2

  NavPath p = search.Find(g, from, to, cfg);
  CHECK(p.status == NavSearchStatus::kFound);
  CHECK(PathContains(p, 0 * 6 + 3) || PathContains(p, 5 * 6 + 3));

  // Block the gate at row 0 -> the path must now use the row-5 gate.
  const int gate_a = 0 * 6 + 3;
  const int next_a = 0 * 6 + 2;
  CHECK(g.SetBlocked(next_a, gate_a, true));
  g.ComputeDegrees();
  p = search.Find(g, from, to, cfg);
  CHECK(p.status == NavSearchStatus::kFound);
  CHECK(!PathContains(p, gate_a));
  CHECK(PathContains(p, 5 * 6 + 3));

  // Block both gates -> unreachable.
  const int gate_b = 5 * 6 + 3;
  const int next_b = 5 * 6 + 2;
  CHECK(g.SetBlocked(next_b, gate_b, true));
  g.ComputeDegrees();
  p = search.Find(g, from, to, cfg);
  CHECK(p.status == NavSearchStatus::kUnreachable);
  for (int i = 0; i < p.count; ++i) CHECK((p.nodes[i] % 6) < 3);
}

static void TestCyclicRingAndAlternatives() {
  // Ring of 8: two equal ways around. Without variance the route is
  // deterministic; with per-bot seeds the two bots split across the ring.
  NavGraph g;
  maps::MakeRing(g, 8, 20.0);
  NavAStar search;

  NavSearchConfig plain;  // variance 0
  const NavPath a = search.Find(g, 0, 4, plain);
  const NavPath b = search.Find(g, 0, 4, plain);
  CHECK(a.status == NavSearchStatus::kFound);
  CHECK(a.count == 5);  // 4 hops either way
  // Determinism: identical repeated searches.
  CHECK(a.count == b.count && a.cost == b.cost);
  for (int i = 0; i < a.count; ++i) CHECK(a.nodes[i] == b.nodes[i]);

  NavSearchConfig va, vb;
  va.variance = 0.35f; va.variance_seed = 11u;  // picks 0-7-6-5-4
  vb.variance = 0.35f; vb.variance_seed = 7u;   // picks 0-1-2-3-4
  const NavPath pa = search.Find(g, 0, 4, va);
  const NavPath pb = search.Find(g, 0, 4, vb);
  CHECK(pa.status == NavSearchStatus::kFound && pb.status == NavSearchStatus::kFound);
  bool differ = (pa.count != pb.count);
  if (!differ) {
    for (int i = 0; i < pa.count; ++i) {
      if (pa.nodes[i] != pb.nodes[i]) { differ = true; break; }
    }
  }
  CHECK(differ);  // different seeds -> genuinely different ring side
  // Per-seed determinism holds as well.
  const NavPath pa2 = search.Find(g, 0, 4, va);
  for (int i = 0; i < pa.count; ++i) CHECK(pa.nodes[i] == pa2.nodes[i]);
  // Varied routes are still valid graph walks.
  for (int i = 0; i + 1 < pa.count; ++i) {
    bool linked = false;
    for (int e = 0; e < g.edge_count(pa.nodes[i]); ++e) {
      if (g.edge(pa.nodes[i], e).to == pa.nodes[i + 1]) linked = true;
    }
    CHECK(linked);
  }
}

static void TestBudget() {
  // 16x16 spiral: the unique corridor to the centre is long; a tiny budget
  // must stop the search and return a usable partial route.
  NavGraph g;
  maps::MakeSpiral(g, 16, 4.0);
  CHECK(g.node_count() == 256);
  NavAStar search;
  NavSearchConfig tiny;
  tiny.max_expand = 10;
  const int entrance = 0;                 // spiral start (outside)
  const int centre = 8 * 16 + 8;          // somewhere deep inside
  const NavPath p = search.Find(g, entrance, centre, tiny);
  CHECK(p.status == NavSearchStatus::kBudgetExhausted);
  CHECK(p.expanded <= 10);
  CHECK(p.count >= 2);          // walked at least one hop toward the goal
  CHECK(p.nodes[0] == entrance);
  CHECK(p.count <= kNavMaxPathNodes);

  // A large budget solves the same problem completely.
  NavSearchConfig big;
  big.max_expand = kNavMaxNodes;
  const NavPath full = search.Find(g, entrance, centre, big);
  CHECK(full.status == NavSearchStatus::kFound);
  CHECK(full.expanded <= kNavMaxNodes);
}

static void TestGoalChanges() {
  NavGraph g;
  maps::MakeGrid(g, 6, 6, 4.0);
  NavAStar search;
  NavSearchConfig cfg;
  const NavPath p1 = search.Find(g, 0, 5 * 6 + 5, cfg);
  CHECK(p1.status == NavSearchStatus::kFound);
  // Immediate re-plan to a different goal reuses the work arrays safely.
  const NavPath p2 = search.Find(g, 0, 5, cfg);
  CHECK(p2.status == NavSearchStatus::kFound);
  CHECK(p2.count == 6 && p2.nodes[5] == 5);
  // And back again - generation stamping must not leak old state.
  const NavPath p3 = search.Find(g, 0, 5 * 6 + 5, cfg);
  CHECK(p3.status == NavSearchStatus::kFound);
  CHECK(p3.count == p1.count && p3.cost == p1.cost);
}

static void TestDeterminismAcrossInstances() {
  NavGraph g;
  maps::MakeGrid(g, 10, 10, 4.0);
  NavSearchConfig cfg;
  cfg.variance = 0.25f;
  cfg.variance_seed = 7u;
  NavAStar s1, s2;
  const NavPath a = s1.Find(g, 0, 99, cfg);
  const NavPath b = s2.Find(g, 0, 99, cfg);
  CHECK(a.status == NavSearchStatus::kFound && b.status == NavSearchStatus::kFound);
  CHECK(a.count == b.count);
  for (int i = 0; i < a.count; ++i) CHECK(a.nodes[i] == b.nodes[i]);
}

int main() {
  TestReachable();
  TestGridOptimality();
  TestUnreachable();
  TestBlockedDetour();
  TestCyclicRingAndAlternatives();
  TestBudget();
  TestGoalChanges();
  TestDeterminismAcrossInstances();
  if (g_failures == 0) {
    std::printf("NAV ASTAR PASS (0 failures, %d checks)\n", g_checks);
    return 0;
  }
  std::printf("NAV ASTAR FAIL (%d failures)\n", g_failures);
  return 1;
}
