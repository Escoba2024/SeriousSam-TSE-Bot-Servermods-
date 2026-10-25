// nav_graph.h - engine-free, allocation-free waypoint graph for the
// Navigation 2.0 prototype (poc/navigation-lab).
//
// SCOPE RULES (same spirit as poc/botcore):
//  - pure data structure: no engine calls, no I/O, no heap allocation;
//  - fixed capacity, trivially copyable-free but statically sized so a
//    BotDriver can hold one instance per map without dynamic memory;
//  - routing works on the horizontal plane (x/z); y is stored for arrival
//    checks and future jump/crouch hints only;
//  - the text format is a SUPERSET of the existing botcore
//    WaypointGraph::ParseLine format ("node x y z" / "edge a b"), so one
//    .wpt file can feed both implementations during migration.
//
// UNITS: metres, degrees; the game tick is 20 Hz.
//
// LICENSING NOTE: structure and semantics are an independent implementation
// for the Alpha-Gaming project. No source code was copied from CecilBotMod
// (GPL-2.0); its navmesh remains an algorithmic reference only.

#ifndef NAVLAB_NAV_GRAPH_H
#define NAVLAB_NAV_GRAPH_H

#include <cmath>
#include <cstdint>
#include <cstdio>

namespace navlab {

/* ------------------------------------------------------------------------ */
/* Capacity and flags                                                        */
/* ------------------------------------------------------------------------ */

constexpr int kNavMaxNodes = 1024;        // per map
constexpr int kNavMaxEdgesPerNode = 12;   // directed edges stored per node
constexpr int kNavMaxPathNodes = 96;      // longest route the A* can return

// Node flags (authored + computed).
enum NavNodeFlags : uint32_t {
  kNodeNone      = 0,
  kNodeImportant = 1u << 0,  // item/objective point - patrol prefers these
  kNodeDeadEnd   = 1u << 1,  // computed by ComputeDegrees(): exactly 1 edge
  kNodeSpawn     = 1u << 2,  // player spawn area - patrol may deprioritise
};

// Edge flags. kEdgeBlocked participates in routing; the others are hints for
// later integration phases and are currently NOT evaluated by the router.
enum NavEdgeFlags : uint32_t {
  kEdgeNone    = 0,
  kEdgeBlocked = 1u << 0,  // temporarily impassable (closed door, brush)
  kEdgeJump    = 1u << 1,  // hint: jump when traversing (integration phase 3)
  kEdgeDanger  = 1u << 2,  // RESERVED: pit/ledge marker - not evaluated yet.
                           // Floor probing is gated behind a separate native
                           // sync test (see the risk analysis).
};

struct NavNode {
  float x, y, z;    // world position; routing uses x/z
  float radius;     // arrival radius [m]
  uint32_t flags;   // NavNodeFlags
  uint16_t degree;  // unblocked edge count, filled by ComputeDegrees()
};

struct NavEdge {
  int16_t to;       // destination node
  float cost;       // traversal cost >= 0, normally the planar distance [m]
  uint32_t flags;   // NavEdgeFlags
};

/* ------------------------------------------------------------------------ */
/* The graph                                                                 */
/* ------------------------------------------------------------------------ */

class NavGraph {
 public:
  NavGraph() { Clear(); }

  void Clear() {
    node_count_ = 0;
    for (int i = 0; i < kNavMaxNodes; ++i) edge_count_[i] = 0;
  }

  int node_count() const { return node_count_; }

  bool Valid(int i) const { return i >= 0 && i < node_count_; }

  int AddNode(double x, double y, double z, uint32_t flags = kNodeNone,
              double radius = 1.0) {
    if (node_count_ >= kNavMaxNodes) return -1;
    if (!std::isfinite(x) || !std::isfinite(y) || !std::isfinite(z)) return -1;
    if (!(radius > 0.0)) radius = 1.0;
    NavNode& n = nodes_[node_count_];
    n.x = static_cast<float>(x);
    n.y = static_cast<float>(y);
    n.z = static_cast<float>(z);
    n.radius = static_cast<float>(radius);
    n.flags = flags;
    n.degree = 0;
    edge_count_[node_count_] = 0;
    return node_count_++;
  }

  // Directed edge. cost < 0 -> planar distance between the nodes.
  bool AddEdge(int a, int b, uint32_t flags = kEdgeNone, double cost = -1.0) {
    if (!Valid(a) || !Valid(b) || a == b) return false;
    uint8_t& count = edge_count_[a];
    for (uint8_t e = 0; e < count; ++e) {
      if (edges_[a][e].to == static_cast<int16_t>(b)) {
        // Idempotent: refresh flags/cost, do not duplicate.
        edges_[a][e].flags = flags;
        if (cost >= 0.0) edges_[a][e].cost = static_cast<float>(cost);
        return true;
      }
    }
    if (count >= kNavMaxEdgesPerNode) return false;
    NavEdge& edge = edges_[a][count];
    edge.to = static_cast<int16_t>(b);
    edge.cost = (cost >= 0.0) ? static_cast<float>(cost) : PlanarDist(a, b);
    edge.flags = flags;
    ++count;
    return true;
  }

  // Bidirectional convenience (same semantics as botcore WaypointGraph::Link).
  bool Link(int a, int b, uint32_t flags = kEdgeNone, double cost = -1.0) {
    return AddEdge(a, b, flags, cost) && AddEdge(b, a, flags, cost);
  }

  // Toggle kEdgeBlocked on both directions of a link.
  bool SetBlocked(int a, int b, bool blocked) {
    bool changed = false;
    changed |= SetEdgeFlagOneWay(a, b, kEdgeBlocked, blocked);
    changed |= SetEdgeFlagOneWay(b, a, kEdgeBlocked, blocked);
    return changed;
  }

  bool SetEdgeFlag(int a, int b, uint32_t flag, bool on) {
    bool changed = false;
    changed |= SetEdgeFlagOneWay(a, b, flag, on);
    changed |= SetEdgeFlagOneWay(b, a, flag, on);
    return changed;
  }

  // Recompute degree (unblocked edges) and the kNodeDeadEnd flag.
  void ComputeDegrees() {
    for (int i = 0; i < node_count_; ++i) {
      uint16_t degree = 0;
      for (uint8_t e = 0; e < edge_count_[i]; ++e) {
        if (!(edges_[i][e].flags & kEdgeBlocked)) ++degree;
      }
      nodes_[i].degree = degree;
      if (degree == 1) {
        nodes_[i].flags |= kNodeDeadEnd;
      } else {
        nodes_[i].flags &= ~kNodeDeadEnd;
      }
    }
  }

  // Nearest node on the horizontal plane; -1 when the graph is empty or the
  // node is farther than max_dist.
  int NearestNode(double x, double z, double max_dist = 1e9) const {
    int best = -1;
    double best_d2 = max_dist * max_dist;
    for (int i = 0; i < node_count_; ++i) {
      const double dx = nodes_[i].x - x;
      const double dz = nodes_[i].z - z;
      const double d2 = dx * dx + dz * dz;
      // Only accept nodes inside max_dist; ties keep the lowest index.
      if (d2 < best_d2) {
        best = i;
        best_d2 = d2;
      }
    }
    return best;
  }

  const NavNode& node(int i) const { return nodes_[i]; }
  int edge_count(int i) const { return edge_count_[i]; }
  const NavEdge& edge(int i, int e) const { return edges_[i][e]; }

  float PlanarDist(int a, int b) const {
    const float dx = nodes_[a].x - nodes_[b].x;
    const float dz = nodes_[a].z - nodes_[b].z;
    return std::sqrt(dx * dx + dz * dz);
  }

  /* --- text format (superset of botcore WaypointGraph::ParseLine) -------- */
  //   node <x> <y> <z> [flags] [radius]
  //   edge <a> <b> [flags] [cost]
  //   block <a> <b> [0|1]            (default 1)
  //   '#' or "//" starts a comment; blank lines are ignored.
  // Returns false on malformed input; the caller should log and refuse the
  // file rather than navigate a half-parsed graph.
  bool ParseLine(const char* line) {
    while (*line == ' ' || *line == '\t') ++line;
    if (*line == '\0' || *line == '#' || *line == '\r' || *line == '\n' ||
        (line[0] == '/' && line[1] == '/')) {
      return true;
    }
    double x = 0.0, y = 0.0, z = 0.0, radius = 0.0;
    unsigned long nflags = 0, eflags = 0;
    int a = 0, b = 0, blocked = 1;  // bare "block a b" means: block
    double cost = 0.0;
    char extra = 0;
    // node x y z [flags [radius]]
    if (std::sscanf(line, "node %lf %lf %lf %lu %lf %c", &x, &y, &z, &nflags,
                    &radius, &extra) >= 3) {
      int n = AddNode(x, y, z,
                      nflags ? static_cast<uint32_t>(nflags) : kNodeNone,
                      radius > 0.0 ? radius : 1.0);
      return n >= 0;
    }
    // edge a b [flags [cost]]
    if (std::sscanf(line, "edge %d %d %lu %lf %c", &a, &b, &eflags, &cost,
                    &extra) >= 2) {
      return Link(a, b, eflags ? static_cast<uint32_t>(eflags) : kEdgeNone,
                  cost > 0.0 ? cost : -1.0);
    }
    // block a b [0|1]
    if (std::sscanf(line, "block %d %d %d %c", &a, &b, &blocked, &extra) >= 2) {
      return SetBlocked(a, b, blocked != 0);
    }
    return false;
  }

 private:
  bool SetEdgeFlagOneWay(int a, int b, uint32_t flag, bool on) {
    if (!Valid(a) || !Valid(b)) return false;
    for (uint8_t e = 0; e < edge_count_[a]; ++e) {
      if (edges_[a][e].to == static_cast<int16_t>(b)) {
        if (on) {
          edges_[a][e].flags |= flag;
        } else {
          edges_[a][e].flags &= ~flag;
        }
        return true;
      }
    }
    return false;
  }

  NavNode nodes_[kNavMaxNodes];
  NavEdge edges_[kNavMaxNodes][kNavMaxEdgesPerNode];
  uint8_t edge_count_[kNavMaxNodes];
  int node_count_;
};

}  // namespace navlab

#endif  // NAVLAB_NAV_GRAPH_H
