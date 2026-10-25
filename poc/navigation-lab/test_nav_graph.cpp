// test_nav_graph.cpp - offline unit tests for navlab::NavGraph.
// Synthetic data only. Run: ./test_nav_graph  (exit 0 = PASS)
#include <cstdio>
#include <cstring>

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

static void TestBasics() {
  NavGraph g;
  CHECK(g.node_count() == 0);
  const int a = g.AddNode(0, 0, 0);
  const int b = g.AddNode(4, 0, 0);
  const int c = g.AddNode(4, 0, 3);
  CHECK(a == 0 && b == 1 && c == 2);
  CHECK(g.AddNode(0.0 / 0.0, 0, 0) == -1);  // NaN rejected
  CHECK(g.Link(a, b));
  CHECK(g.Link(b, c));
  CHECK(!g.Link(a, a));  // self link rejected
  CHECK(g.edge_count(a) == 1 && g.edge_count(b) == 2);
  // Idempotent re-link refreshes instead of duplicating.
  CHECK(g.Link(a, b));
  CHECK(g.edge_count(a) == 1);
  // Default cost = planar distance.
  CHECK(g.edge(a, 0).cost > 3.99f && g.edge(a, 0).cost < 4.01f);
  g.ComputeDegrees();
  CHECK(g.node(a).degree == 1 && (g.node(a).flags & kNodeDeadEnd));
  CHECK(g.node(b).degree == 2 && !(g.node(b).flags & kNodeDeadEnd));
  // Nearest node on the plane.
  CHECK(g.NearestNode(3.9, 0.1) == b);
  CHECK(g.NearestNode(0.0, 0.0, 0.5) == a);
  CHECK(g.NearestNode(100.0, 100.0, 1.0) == -1);
}

static void TestBlocking() {
  NavGraph g;
  maps::MakeCorridor(g, 4);  // 0-1-2-3
  g.ComputeDegrees();
  CHECK(g.node(1).degree == 2);
  CHECK(g.SetBlocked(1, 2, true));
  g.ComputeDegrees();
  CHECK(g.node(1).degree == 1 && (g.node(1).flags & kNodeDeadEnd));
  CHECK(g.node(2).degree == 1);
  // Blocking is bidirectional and reversible.
  // Node 1's edges are [to 0, to 2]; node 2's edges are [to 1, to 2].
  CHECK(g.edge(1, 1).flags & kEdgeBlocked);
  CHECK(g.edge(2, 0).flags & kEdgeBlocked);
  CHECK(g.SetBlocked(1, 2, false));
  g.ComputeDegrees();
  CHECK(g.node(1).degree == 2 && !(g.node(1).flags & kNodeDeadEnd));
}

static void TestParser() {
  NavGraph g;
  // Exactly the legacy botcore format lines.
  CHECK(g.ParseLine("node 0.0 0.0 0.0"));
  CHECK(g.ParseLine("node 5.0 0.0 0.0"));
  CHECK(g.ParseLine("node 5.0 0.0 5.0"));
  CHECK(g.ParseLine("edge 0 1"));
  CHECK(g.ParseLine("edge 1 2"));
  CHECK(g.ParseLine("# comment"));
  CHECK(g.ParseLine("// another comment"));
  CHECK(g.ParseLine("   "));
  CHECK(g.ParseLine(""));
  CHECK(g.node_count() == 3);
  CHECK(g.edge_count(0) == 1 && g.edge_count(1) == 2);
  // Superset: flags and radius.
  CHECK(g.ParseLine("node 10.0 0.0 0.0 1 2.5"));  // kNodeImportant, r=2.5
  CHECK(g.node(3).flags == kNodeImportant);
  CHECK(g.node(3).radius > 2.49f && g.node(3).radius < 2.51f);
  CHECK(g.ParseLine("edge 2 3 0 7.5"));  // explicit cost
  CHECK(g.edge(2, 1).cost > 7.49f && g.edge(2, 1).cost < 7.51f);
  // Superset: block command.
  CHECK(g.ParseLine("block 0 1"));
  CHECK(g.edge(0, 0).flags & kEdgeBlocked);
  CHECK(g.ParseLine("block 0 1 0"));
  CHECK(!(g.edge(0, 0).flags & kEdgeBlocked));
  // Malformed input is refused.
  CHECK(!g.ParseLine("nonsense"));
  CHECK(!g.ParseLine("node 1 2"));           // too few coordinates
  CHECK(!g.ParseLine("edge 99 0"));          // out of range
}

static void TestCapacity() {
  NavGraph g;
  for (int i = 0; i < kNavMaxNodes; ++i) {
    CHECK(g.AddNode(i, 0, 0) == i);
  }
  CHECK(g.AddNode(0, 0, 1) == -1);  // full
  // Edge capacity per node.
  NavGraph h;
  h.AddNode(0, 0, 0);
  for (int i = 1; i <= kNavMaxEdgesPerNode + 2; ++i) h.AddNode(i, 0, 0);
  for (int i = 1; i <= kNavMaxEdgesPerNode; ++i) CHECK(h.AddEdge(0, i));
  CHECK(!h.AddEdge(0, kNavMaxEdgesPerNode + 1));  // per-node edge cap
}

int main() {
  TestBasics();
  TestBlocking();
  TestParser();
  TestCapacity();
  if (g_failures == 0) {
    std::printf("NAV GRAPH PASS (0 failures, %d checks)\n", g_checks);
    return 0;
  }
  std::printf("NAV GRAPH FAIL (%d failures)\n", g_failures);
  return 1;
}
