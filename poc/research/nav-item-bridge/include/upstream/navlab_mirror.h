// SPDX-License-Identifier: GPL-2.0-only
// navlab_mirror.h - exact contract-compatible mirror of PR #54
// (poc/navigation-lab, commit 3f2ba8dbf0df341b35cb157efd152fa93d1d7fd7).
//
// PURPOSE
//  PR #54 is an open sibling PR and is not yet merged into `main`. Because our
//  exclusive write scope is strictly `poc/research/nav-item-bridge/**` and
//  `docs/research/nav-item-bridge/**`, we do not copy files into
//  `poc/navigation-lab/`.
//  `upstream_seams.h` automatically includes the real `poc/navigation-lab/*.h`
//  whenever PR #54 is present in the checkout (or on the `-I` include path)
//  and falls back to this mirror ONLY when building standalone on `main`.
//  Every include guard (`NAVLAB_NAV_GRAPH_H`, `NAVLAB_NAV_ASTAR_H`,
//  `NAVLAB_NAV_AGENT_H`, `NAVLAB_NAV_MAPS_H`), type, field and algorithm
//  matches PR #54 so switching to the merged upstream headers is zero-diff.

#ifndef NAV_ITEM_BRIDGE_UPSTREAM_NAVLAB_MIRROR_H
#define NAV_ITEM_BRIDGE_UPSTREAM_NAVLAB_MIRROR_H

#include <cmath>
#include <cstdint>
#include <cstdio>

/* ======================================================================== */
/* nav_graph.h                                                              */
/* ======================================================================== */

#ifndef NAVLAB_NAV_GRAPH_H
#define NAVLAB_NAV_GRAPH_H

namespace navlab {

constexpr int kNavMaxNodes = 1024;
constexpr int kNavMaxEdgesPerNode = 12;
constexpr int kNavMaxPathNodes = 96;

enum NavNodeFlags : uint32_t {
  kNodeNone      = 0,
  kNodeImportant = 1u << 0,
  kNodeDeadEnd   = 1u << 1,
  kNodeSpawn     = 1u << 2,
};

enum NavEdgeFlags : uint32_t {
  kEdgeNone    = 0,
  kEdgeBlocked = 1u << 0,
  kEdgeJump    = 1u << 1,
  kEdgeDanger  = 1u << 2,
};

struct NavNode {
  float x, y, z;
  float radius;
  uint32_t flags;
  uint16_t degree;
};

struct NavEdge {
  int16_t to;
  float cost;
  uint32_t flags;
};

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

  bool AddEdge(int a, int b, uint32_t flags = kEdgeNone, double cost = -1.0) {
    if (!Valid(a) || !Valid(b) || a == b) return false;
    uint8_t& count = edge_count_[a];
    for (uint8_t e = 0; e < count; ++e) {
      if (edges_[a][e].to == static_cast<int16_t>(b)) {
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

  bool Link(int a, int b, uint32_t flags = kEdgeNone, double cost = -1.0) {
    return AddEdge(a, b, flags, cost) && AddEdge(b, a, flags, cost);
  }

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

  int NearestNode(double x, double z, double max_dist = 1e9) const {
    int best = -1;
    double best_d2 = max_dist * max_dist;
    for (int i = 0; i < node_count_; ++i) {
      const double dx = nodes_[i].x - x;
      const double dz = nodes_[i].z - z;
      const double d2 = dx * dx + dz * dz;
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

  bool ParseLine(const char* line) {
    while (*line == ' ' || *line == '\t') ++line;
    if (*line == '\0' || *line == '#' || *line == '\r' || *line == '\n' ||
        (line[0] == '/' && line[1] == '/')) {
      return true;
    }
    double x = 0.0, y = 0.0, z = 0.0, radius = 0.0;
    unsigned long nflags = 0, eflags = 0;
    int a = 0, b = 0, blocked = 1;
    double cost = 0.0;
    char extra = 0;
    if (std::sscanf(line, "node %lf %lf %lf %lu %lf %c", &x, &y, &z, &nflags,
                    &radius, &extra) >= 3) {
      const int n = AddNode(x, y, z,
                            nflags ? static_cast<uint32_t>(nflags) : kNodeNone,
                            radius > 0.0 ? radius : 1.0);
      return n >= 0;
    }
    if (std::sscanf(line, "edge %d %d %lu %lf %c", &a, &b, &eflags, &cost,
                    &extra) >= 2) {
      return Link(a, b, eflags ? static_cast<uint32_t>(eflags) : kEdgeNone,
                  cost > 0.0 ? cost : -1.0);
    }
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

/* ======================================================================== */
/* nav_astar.h                                                              */
/* ======================================================================== */

#ifndef NAVLAB_NAV_ASTAR_H
#define NAVLAB_NAV_ASTAR_H

namespace navlab {

enum class NavSearchStatus : uint8_t {
  kIdle = 0,
  kFound,
  kUnreachable,
  kBudgetExhausted,
  kInvalidArgs,
};

struct NavPath {
  NavSearchStatus status;
  int16_t nodes[kNavMaxPathNodes];
  int count;
  float cost;
  int expanded;
};

struct NavSearchConfig {
  int max_expand;
  float variance;
  uint32_t variance_seed;

  NavSearchConfig() : max_expand(256), variance(0.0f), variance_seed(0) {}
};

class NavAStar {
 public:
  NavAStar() : heap_count_(0), generation_(0) {
    for (int i = 0; i < kNavMaxNodes; ++i) {
      stamp_[i] = 0;
      closed_stamp_[i] = 0;
      parent_[i] = -1;
      g_[i] = 0.0f;
      f_[i] = 0.0f;
    }
  }

  NavPath Find(const NavGraph& graph, int from, int to,
               const NavSearchConfig& config) {
    NavPath out;
    out.status = NavSearchStatus::kInvalidArgs;
    out.count = 0;
    out.cost = 0.0f;
    out.expanded = 0;
    if (!graph.Valid(from) || !graph.Valid(to)) return out;

    if (from == to) {
      out.status = NavSearchStatus::kFound;
      out.nodes[0] = static_cast<int16_t>(from);
      out.count = 1;
      return out;
    }

    const int budget = ClampBudget(config.max_expand);
    const float variance = ClampVariance(config.variance);
    const float heur_scale = 1.0f - variance;

    ++generation_;
    heap_count_ = 0;
    float best_deep_g = -1.0f;
    int16_t best_deep_node = static_cast<int16_t>(from);
    float best_near_h = 1e30f;
    int16_t best_near_node = static_cast<int16_t>(from);

    Touch(from);
    g_[from] = 0.0f;
    f_[from] = Heuristic(graph, from, to, heur_scale);
    parent_[from] = -1;
    HeapPush(from);

    while (heap_count_ > 0) {
      const int current = HeapPop();
      if (IsClosed(current)) continue;
      closed_stamp_[current] = generation_;
      ++out.expanded;

      if (current == to) {
        out.status = NavSearchStatus::kFound;
        Reconstruct(out, from, to, graph);
        return out;
      }

      if (g_[current] > best_deep_g) {
        best_deep_g = g_[current];
        best_deep_node = static_cast<int16_t>(current);
      }
      const float h = Heuristic(graph, current, to, 1.0f);
      if (h < best_near_h) {
        best_near_h = h;
        best_near_node = static_cast<int16_t>(current);
      }

      if (out.expanded >= budget) break;

      const int count = graph.edge_count(current);
      for (int e = 0; e < count; ++e) {
        const NavEdge& edge = graph.edge(current, e);
        if (edge.flags & kEdgeBlocked) continue;
        const int next = edge.to;
        if (!graph.Valid(next) || IsClosed(next)) continue;

        const float step = EdgeCost(edge, current, next, config.variance,
                                    config.variance_seed);
        const float tentative = g_[current] + step;
        if (!IsTouched(next) || tentative < g_[next]) {
          Touch(next);
          g_[next] = tentative;
          f_[next] = tentative + Heuristic(graph, next, to, heur_scale);
          parent_[next] = static_cast<int16_t>(current);
          HeapPush(next);
        }
      }
    }

    const bool exhausted = (out.expanded >= budget);
    out.status = exhausted ? NavSearchStatus::kBudgetExhausted
                           : NavSearchStatus::kUnreachable;
    Reconstruct(out, from, exhausted ? best_deep_node : best_near_node, graph);
    return out;
  }

 private:
  static int ClampBudget(int budget) {
    if (budget < 1) return 1;
    return budget > kNavMaxNodes ? kNavMaxNodes : budget;
  }

  static float ClampVariance(float v) {
    if (!(v > 0.0f)) return 0.0f;
    return v > 0.5f ? 0.5f : v;
  }

  static float Heuristic(const NavGraph& graph, int node, int goal,
                         float scale) {
    return graph.PlanarDist(node, goal) * scale;
  }

  static float EdgeCost(const NavEdge& edge, int from, int to, float variance,
                        uint32_t seed) {
    const float base = edge.cost > 0.0f ? edge.cost : 0.0f;
    if (!(variance > 0.0f)) return base;
    uint32_t h = static_cast<uint32_t>(from) * 73856093u ^
                 static_cast<uint32_t>(to) * 19349663u ^ seed * 83492791u;
    h ^= h >> 13;
    h *= 0x5bd1e995u;
    h ^= h >> 15;
    const float u = static_cast<float>(h & 0xFFFFu) * (1.0f / 65535.0f);
    return base * (1.0f + (u * 2.0f - 1.0f) * variance);
  }

  void Reconstruct(NavPath& out, int from, int end, const NavGraph& graph) const {
    int16_t rev[kNavMaxPathNodes];
    int n = 0;
    int cur = end;
    while (cur >= 0 && n < kNavMaxPathNodes) {
      rev[n++] = static_cast<int16_t>(cur);
      if (cur == from) break;
      cur = parent_[cur];
    }
    out.count = 0;
    out.cost = 0.0f;
    for (int i = n - 1; i >= 0; --i) {
      out.nodes[out.count++] = rev[i];
    }
    for (int i = 0; i + 1 < out.count; ++i) {
      out.cost += EdgeCostOf(graph, out.nodes[i], out.nodes[i + 1]);
    }
  }

  static float EdgeCostOf(const NavGraph& graph, int a, int b) {
    const int count = graph.edge_count(a);
    for (int e = 0; e < count; ++e) {
      if (graph.edge(a, e).to == static_cast<int16_t>(b)) {
        return graph.edge(a, e).cost;
      }
    }
    return graph.PlanarDist(a, b);
  }

  void Touch(int node) { stamp_[node] = generation_; }
  bool IsTouched(int node) const { return stamp_[node] == generation_; }
  bool IsClosed(int node) const { return closed_stamp_[node] == generation_; }

  bool HeapBetter(int a, int b) const {
    if (f_[heap_[a]] != f_[heap_[b]]) return f_[heap_[a]] < f_[heap_[b]];
    if (g_[heap_[a]] != g_[heap_[b]]) return g_[heap_[a]] > g_[heap_[b]];
    return heap_[a] < heap_[b];
  }

  void HeapPush(int node) {
    for (int i = 0; i < heap_count_; ++i) {
      if (heap_[i] == node) {
        HeapSiftUp(i);
        HeapSiftDown(i);
        return;
      }
    }
    if (heap_count_ >= kNavMaxNodes) return;
    heap_[heap_count_] = static_cast<int16_t>(node);
    HeapSiftUp(heap_count_);
    ++heap_count_;
  }

  int HeapPop() {
    const int top = heap_[0];
    --heap_count_;
    if (heap_count_ > 0) {
      heap_[0] = heap_[heap_count_];
      HeapSiftDown(0);
    }
    return top;
  }

  void HeapSiftUp(int i) {
    while (i > 0) {
      const int parent = (i - 1) / 2;
      if (!HeapBetter(i, parent)) break;
      Swap(i, parent);
      i = parent;
    }
  }

  void HeapSiftDown(int i) {
    for (;;) {
      const int l = 2 * i + 1;
      const int r = 2 * i + 2;
      int best = i;
      if (l < heap_count_ && HeapBetter(l, best)) best = l;
      if (r < heap_count_ && HeapBetter(r, best)) best = r;
      if (best == i) break;
      Swap(i, best);
      i = best;
    }
  }

  void Swap(int a, int b) {
    const int16_t t = heap_[a];
    heap_[a] = heap_[b];
    heap_[b] = t;
  }

  float g_[kNavMaxNodes];
  float f_[kNavMaxNodes];
  int16_t parent_[kNavMaxNodes];
  uint32_t stamp_[kNavMaxNodes];
  uint32_t closed_stamp_[kNavMaxNodes];
  int16_t heap_[kNavMaxNodes];
  int heap_count_;
  uint32_t generation_;
};

}  // namespace navlab

#endif  // NAVLAB_NAV_ASTAR_H

/* ======================================================================== */
/* nav_agent.h                                                              */
/* ======================================================================== */

#ifndef NAVLAB_NAV_AGENT_H
#define NAVLAB_NAV_AGENT_H

namespace navlab {

constexpr double kNavTickHz = 20.0;
constexpr double kNavPi = 3.14159265358979323846;

enum class NavMode : uint8_t {
  kIdle = 0,
  kPatrol,
  kPursue,
  kReposition,
  kScan,
};

struct NavPersonality {
  float explore_bias;
  float important_bias;
  float deadend_aversion;
  float route_variance;
  float walk_factor;
  float patrol_min_dist;
  int   repath_cooldown;
  int   stuck_window;
  float stuck_min_dist;
  int   scan_ticks;
  float turn_rate_deg_s;
  float search_radius;

  NavPersonality()
      : explore_bias(0.5f), important_bias(0.35f), deadend_aversion(0.5f),
        route_variance(0.12f), walk_factor(1.0f), patrol_min_dist(10.0f),
        repath_cooldown(20), stuck_window(40), stuck_min_dist(1.0f),
        scan_ticks(60), turn_rate_deg_s(240.0f), search_radius(0.9f) {}
};

inline NavPersonality NavPersonalityFromTraits(float aggression, float caution,
                                               float speed_scale,
                                               float turn_rate_deg_s) {
  NavPersonality p;
  const float aggr = aggression < 0.0f ? 0.0f : (aggression > 1.0f ? 1.0f : aggression);
  const float caut = caution < 0.0f ? 0.0f : (caution > 1.0f ? 1.0f : caution);
  p.explore_bias = 0.30f + 0.40f * aggr;
  p.important_bias = 0.25f + 0.30f * caut;
  p.deadend_aversion = 0.25f + 0.60f * caut;
  p.patrol_min_dist = 6.0f + 14.0f * aggr;
  p.walk_factor = speed_scale < 0.2f ? 0.2f : (speed_scale > 1.0f ? 1.0f : speed_scale);
  p.turn_rate_deg_s = turn_rate_deg_s > 30.0f ? turn_rate_deg_s : 30.0f;
  return p;
}

struct NavAgentInput {
  int tick;
  double x, y, z;
  double yaw_deg;
  bool alive;
  bool movement_requested;
  bool has_target;
  bool target_visible;
  double target_x, target_y, target_z;
};

struct NavCommand {
  bool active;
  double desired_yaw_deg;
  double yaw_delta_deg;
  double forward;
  NavMode mode;
  int dest_node;
  int route_hops_left;
  bool replanned;
  bool stuck;
  bool reached_destination;
  int expanded_last_search;

  NavCommand()
      : active(false), desired_yaw_deg(0.0), yaw_delta_deg(0.0), forward(0.0),
        mode(NavMode::kIdle), dest_node(-1), route_hops_left(0),
        replanned(false), stuck(false), reached_destination(false),
        expanded_last_search(0) {}
};

class NavAgent {
 public:
  NavAgent() { Configure(NavPersonality(), 1u); }

  void Configure(const NavPersonality& personality, uint32_t seed) {
    p_ = personality;
    rng_state_ = seed ? seed : 1u;
    search_cfg_.max_expand = 256;
    search_cfg_.variance = p_.route_variance;
    search_cfg_.variance_seed = seed ? seed : 1u;
    Reset();
  }

  void Reset() {
    mode_ = NavMode::kIdle;
    dest_node_ = -1;
    route_len_ = 0;
    route_pos_ = 0;
    last_replan_tick_ = -1000000;
    searched_last_plan_ = false;
    force_replan_ = false;
    steer_err_ = 0.0;
    scan_until_tick_ = -1000000;
    avoid_node_ = -1;
    avoid_until_tick_ = -1000000;
    last_search_expanded_ = 0;
    searches_total_ = 0;
    expansions_total_ = 0;
    stuck_events_ = 0;
    destinations_reached_ = 0;
    stuck_ref_x_ = stuck_ref_z_ = 0.0;
    last_x_ = last_z_ = 0.0;
    stuck_ticks_ = 0;
    have_pos_ = false;
    last_target_x_ = last_target_z_ = 0.0;
    have_last_target_ = false;
    for (int i = 0; i < kNavMaxNodes; ++i) visits_[i] = 0;
  }

  int searches_total() const { return searches_total_; }
  int expansions_total() const { return expansions_total_; }
  int stuck_events() const { return stuck_events_; }
  int destinations_reached() const { return destinations_reached_; }
  NavMode mode() const { return mode_; }
  int dest_node() const { return dest_node_; }

  NavCommand Step(const NavGraph& graph, const NavAgentInput& in) {
    NavCommand cmd;
    if (!in.alive || graph.node_count() <= 0) {
      mode_ = NavMode::kIdle;
      have_pos_ = false;
      return cmd;
    }

    UpdateStuck(in, cmd);

    if (have_pos_) {
      const double dx = in.x - last_x_, dz = in.z - last_z_;
      if (dx * dx + dz * dz > 64.0) {
        route_len_ = 0;
        route_pos_ = 0;
        dest_node_ = -1;
        have_pos_ = false;
      }
    }
    last_x_ = in.x;
    last_z_ = in.z;
    have_pos_ = true;

    if (in.tick > avoid_until_tick_) avoid_node_ = -1;

    if (in.has_target && in.target_visible) {
      mode_ = NavMode::kPursue;
      last_target_x_ = in.target_x;
      last_target_z_ = in.target_z;
      have_last_target_ = true;
      SteerTowards(cmd, in, in.target_x, in.target_z);
      cmd.active = true;
      cmd.forward = (steer_err_ > 90.0) ? 0.0 : p_.walk_factor * 0.5;
      cmd.mode = mode_;
      cmd.dest_node = dest_node_;
      cmd.route_hops_left = route_len_ - route_pos_;
      return cmd;
    }

    if (in.has_target && !in.target_visible) {
      last_target_x_ = in.target_x;
      last_target_z_ = in.target_z;
      have_last_target_ = true;
      const int goal = graph.NearestNode(last_target_x_, last_target_z_);
      if (graph.Valid(goal) && (dest_node_ != goal || force_replan_)) {
        Plan(graph, in, goal);
        cmd.replanned = searched_last_plan_;
      }
      if (route_len_ > route_pos_) {
        mode_ = NavMode::kReposition;
        FollowRoute(graph, in, cmd);
        if (route_len_ == 0) {
          mode_ = NavMode::kScan;
          scan_until_tick_ = in.tick + ScanTicks();
        }
      } else if (mode_ == NavMode::kReposition && Arrived(graph, in)) {
        mode_ = NavMode::kScan;
        scan_until_tick_ = in.tick + ScanTicks();
        ScanStep(in, cmd);
      } else {
        mode_ = NavMode::kScan;
        if (in.tick >= scan_until_tick_) scan_until_tick_ = in.tick + ScanTicks();
        ScanStep(in, cmd);
      }
      cmd.mode = mode_;
      cmd.dest_node = dest_node_;
      cmd.route_hops_left = route_len_ - route_pos_;
      cmd.expanded_last_search = last_search_expanded_;
      return cmd;
    }

    if (mode_ == NavMode::kScan && in.tick < scan_until_tick_) {
      ScanStep(in, cmd);
      cmd.mode = mode_;
      return cmd;
    }

    mode_ = NavMode::kPatrol;
    if (route_len_ == 0 || route_pos_ >= route_len_) {
      const int goal = ChoosePatrolDestination(graph, in);
      if (goal < 0) {
        cmd.mode = mode_;
        return cmd;
      }
      if (!Plan(graph, in, goal)) {
        cmd.replanned = searched_last_plan_;
        cmd.mode = mode_;
        return cmd;
      }
      cmd.replanned = searched_last_plan_;
      cmd.expanded_last_search = last_search_expanded_;
    }
    const bool arrived = FollowRoute(graph, in, cmd);
    if (arrived) ++destinations_reached_;
    cmd.reached_destination = arrived;
    cmd.mode = mode_;
    cmd.dest_node = dest_node_;
    cmd.route_hops_left = route_len_ - route_pos_;
    return cmd;
  }

 private:
  bool Plan(const NavGraph& graph, const NavAgentInput& in, int goal) {
    searched_last_plan_ = false;
    if (!graph.Valid(goal)) return false;
    const int start = graph.NearestNode(in.x, in.z);
    if (start < 0) return false;

    const bool same_goal = (goal == dest_node_);
    if (same_goal && !force_replan_ &&
        in.tick - last_replan_tick_ < p_.repath_cooldown) {
      return route_len_ > route_pos_;
    }

    const int avoid = avoid_node_;
    const NavPath path = RunSearch(graph, start, goal, avoid);
    searched_last_plan_ = true;
    force_replan_ = false;
    if (path.count <= 0) return false;

    for (int i = 0; i < path.count && i < kNavMaxPathNodes; ++i) {
      route_[i] = path.nodes[i];
    }
    route_len_ = path.count;
    route_pos_ = 0;
    dest_node_ = goal;
    last_replan_tick_ = in.tick;
    last_search_expanded_ = path.expanded;
    ++searches_total_;
    expansions_total_ += path.expanded;
    MarkVisited(route_[route_len_ - 1]);
    return true;
  }

  NavPath RunSearch(const NavGraph& graph, int start, int goal, int avoid) {
    if (avoid >= 0 && avoid != goal) {
      const NavPath first = search_.Find(graph, start, goal, search_cfg_);
      if (first.count >= 2 && first.nodes[1] == avoid) {
        const NavPath alt = SearchAvoiding(graph, start, goal, avoid);
        if (alt.count >= 2 && alt.nodes[1] != avoid) return alt;
      }
      return first;
    }
    return search_.Find(graph, start, goal, search_cfg_);
  }

  NavPath SearchAvoiding(const NavGraph& graph, int start, int goal,
                         int avoid) {
    NavPath best;
    best.status = NavSearchStatus::kInvalidArgs;
    best.count = 0;
    best.cost = 0.0f;
    best.expanded = 0;
    const int count = graph.edge_count(start);
    for (int e = 0; e < count; ++e) {
      const NavEdge& edge = graph.edge(start, e);
      if (edge.flags & kEdgeBlocked) continue;
      const int next = edge.to;
      if (next == avoid || !graph.Valid(next)) continue;
      const NavPath sub = search_.Find(graph, next, goal, search_cfg_);
      if (sub.count <= 0) continue;
      if (best.count == 0 || sub.cost < best.cost) {
        best = sub;
        if (best.count < kNavMaxPathNodes) {
          for (int i = best.count; i > 0; --i) best.nodes[i] = best.nodes[i - 1];
          best.nodes[0] = static_cast<int16_t>(start);
          ++best.count;
        }
      }
    }
    return best;
  }

  int ChoosePatrolDestination(const NavGraph& graph, const NavAgentInput& in) {
    int best = -1;
    double best_score = -1e30;
    const int n = graph.node_count();
    uint8_t max_visits = 1;
    for (int i = 0; i < n; ++i) {
      if (visits_[i] > max_visits) max_visits = visits_[i];
    }
    for (int i = 0; i < n; ++i) {
      const NavNode& node = graph.node(i);
      if (node.degree == 0 && !(node.flags & kNodeImportant)) continue;
      const double dx = node.x - in.x, dz = node.z - in.z;
      const double dist = std::sqrt(dx * dx + dz * dz);
      if (dist < 2.0) continue;

      double score = 0.0;
      const double freshness =
          1.0 - static_cast<double>(visits_[i]) / static_cast<double>(max_visits);
      score += p_.explore_bias * freshness;
      if (node.flags & kNodeImportant) score += p_.important_bias;
      const double d_norm =
          dist / (p_.patrol_min_dist > 1.0 ? p_.patrol_min_dist : 1.0);
      score += 0.35 * (d_norm < 3.0 ? d_norm / 3.0 : 1.0);
      if ((node.flags & kNodeDeadEnd) && !(node.flags & kNodeImportant)) {
        score -= p_.deadend_aversion;
      }
      if (node.flags & kNodeSpawn) score -= 0.15;
      if (score > best_score) {
        best_score = score;
        best = i;
      }
    }
    return best;
  }

  bool FollowRoute(const NavGraph& graph, const NavAgentInput& in,
                   NavCommand& cmd) {
    if (route_len_ == 0 || route_pos_ >= route_len_) return false;
    bool reached_final = false;
    while (route_pos_ < route_len_) {
      const NavNode& node = graph.node(route_[route_pos_]);
      const double dx = node.x - in.x, dz = node.z - in.z;
      const double reach =
          node.radius > p_.search_radius ? node.radius : p_.search_radius;
      const double d2 = dx * dx + dz * dz;
      bool passed = false;
      if (route_pos_ > 0) {
        const NavNode& prev = graph.node(route_[route_pos_ - 1]);
        const double sx = node.x - prev.x, sz = node.z - prev.z;
        const double bx = in.x - prev.x, bz = in.z - prev.z;
        const double seg2 = sx * sx + sz * sz;
        if (seg2 > 1e-9) passed = ((bx * sx + bz * sz) / seg2) > 1.0;
      }
      if (d2 <= reach * reach || passed) {
        MarkVisited(route_[route_pos_]);
        ++route_pos_;
        if (route_pos_ >= route_len_) {
          reached_final = true;
          break;
        }
      } else {
        break;
      }
    }
    if (route_pos_ >= route_len_) {
      route_len_ = 0;
      route_pos_ = 0;
      cmd.forward = 0.0;
      return reached_final;
    }

    const NavNode& next = graph.node(route_[route_pos_]);
    SteerTowards(cmd, in, next.x, next.z);
    cmd.active = true;
    cmd.forward = (steer_err_ > 60.0) ? 0.0 : p_.walk_factor;
    return reached_final;
  }

  void SteerTowards(NavCommand& cmd, const NavAgentInput& in, double tx,
                    double tz) {
    const double dx = tx - in.x, dz = tz - in.z;
    const double desired = std::atan2(-dx, -dz) * (180.0 / kNavPi);
    cmd.desired_yaw_deg = desired;
    double delta = desired - in.yaw_deg;
    while (delta > 180.0) delta -= 360.0;
    while (delta < -180.0) delta += 360.0;
    steer_err_ = delta < 0.0 ? -delta : delta;
    const double limit = p_.turn_rate_deg_s / kNavTickHz;
    cmd.yaw_delta_deg =
        delta < -limit ? -limit : (delta > limit ? limit : delta);
    cmd.desired_yaw_deg = in.yaw_deg + cmd.yaw_delta_deg;
  }

  bool Arrived(const NavGraph& graph, const NavAgentInput& in) {
    if (route_len_ == 0) {
      if (!graph.Valid(dest_node_)) return false;
      const NavNode& node = graph.node(dest_node_);
      const double dx = node.x - in.x, dz = node.z - in.z;
      const double reach =
          node.radius > p_.search_radius ? node.radius : p_.search_radius;
      return dx * dx + dz * dz <= reach * reach;
    }
    return false;
  }

  void ScanStep(const NavAgentInput& in, NavCommand& cmd) {
    cmd.active = true;
    cmd.forward = 0.0;
    cmd.yaw_delta_deg = 3.0;
    cmd.desired_yaw_deg = in.yaw_deg + cmd.yaw_delta_deg;
  }

  int ScanTicks() const { return p_.scan_ticks > 0 ? p_.scan_ticks : 20; }

  void UpdateStuck(const NavAgentInput& in, NavCommand& cmd) {
    if (!in.movement_requested) {
      stuck_ticks_ = 0;
      return;
    }
    if (stuck_ticks_ == 0) {
      stuck_ref_x_ = in.x;
      stuck_ref_z_ = in.z;
    }
    ++stuck_ticks_;
    const int window = p_.stuck_window > 1 ? p_.stuck_window : 2;
    if (stuck_ticks_ < window) return;
    const double dx = in.x - stuck_ref_x_, dz = in.z - stuck_ref_z_;
    const double min_d = p_.stuck_min_dist > 0.0f ? p_.stuck_min_dist : 0.5f;
    const bool stuck = (dx * dx + dz * dz) < min_d * min_d;
    stuck_ticks_ = 0;
    if (!stuck) return;

    ++stuck_events_;
    cmd.stuck = true;
    if (route_pos_ < route_len_) {
      avoid_node_ = route_[route_pos_];
      avoid_until_tick_ = in.tick + 5 * static_cast<int>(kNavTickHz);
    }
    last_replan_tick_ = -1000000;
    force_replan_ = true;
    route_len_ = 0;
    route_pos_ = 0;
  }

  void MarkVisited(int node) {
    if (node >= 0 && node < kNavMaxNodes && visits_[node] < 250) ++visits_[node];
  }

  NavPersonality p_;
  NavAStar search_;
  NavSearchConfig search_cfg_;
  uint32_t rng_state_;

  NavMode mode_;
  int dest_node_;
  int16_t route_[kNavMaxPathNodes];
  int route_len_;
  int route_pos_;
  int last_replan_tick_;
  bool searched_last_plan_;
  bool force_replan_;
  double steer_err_;
  int scan_until_tick_;
  int avoid_node_;
  int avoid_until_tick_;
  int last_search_expanded_;

  int stuck_ticks_;
  double stuck_ref_x_, stuck_ref_z_;
  double last_x_, last_z_;
  bool have_pos_;
  double last_target_x_, last_target_z_;
  bool have_last_target_;

  uint8_t visits_[kNavMaxNodes];

  int searches_total_;
  int expansions_total_;
  int stuck_events_;
  int destinations_reached_;
};

}  // namespace navlab

#endif  // NAVLAB_NAV_AGENT_H

/* ======================================================================== */
/* nav_maps.h                                                               */
/* ======================================================================== */

#ifndef NAVLAB_NAV_MAPS_H
#define NAVLAB_NAV_MAPS_H

namespace navlab {
namespace maps {

inline void MakeCorridor(NavGraph& g, int count, double spacing = 4.0,
                         uint32_t flags = kNodeNone) {
  for (int i = 0; i < count; ++i) {
    g.AddNode(i * spacing, 0.0, 0.0, flags);
    if (i > 0) g.Link(i - 1, i);
  }
  g.ComputeDegrees();
}

inline void MakeGrid(NavGraph& g, int width, int height, double spacing = 4.0,
                     bool (*is_wall)(int y, int x, void* ctx) = nullptr,
                     void* ctx = nullptr) {
  for (int y = 0; y < height; ++y) {
    for (int x = 0; x < width; ++x) {
      if (is_wall && is_wall(y, x, ctx)) {
        g.AddNode(x * spacing, 0.0, y * spacing, kNodeNone, 1.0);
        continue;
      }
      g.AddNode(x * spacing, 0.0, y * spacing);
    }
  }
  for (int y = 0; y < height; ++y) {
    for (int x = 0; x < width; ++x) {
      const int i = y * width + x;
      if (is_wall && is_wall(y, x, ctx)) continue;
      if (x + 1 < width && !(is_wall && is_wall(y, x + 1, ctx))) g.Link(i, i + 1);
      if (y + 1 < height && !(is_wall && is_wall(y + 1, x, ctx))) {
        g.Link(i, i + width);
      }
    }
  }
  g.ComputeDegrees();
}

inline void MakeRing(NavGraph& g, int count, double radius = 20.0) {
  const double pi = 3.14159265358979323846;
  for (int i = 0; i < count; ++i) {
    const double a = 2.0 * pi * i / count;
    g.AddNode(radius * std::sin(a), 0.0, radius * std::cos(a));
  }
  for (int i = 0; i < count; ++i) {
    g.Link(i, (i + 1) % count);
  }
  g.ComputeDegrees();
}

inline void MakeDeadEndMap(NavGraph& g, int main_count, int branch_every,
                           double spacing = 4.0) {
  for (int i = 0; i < main_count; ++i) {
    g.AddNode(i * spacing, 0.0, 0.0);
    if (i > 0) g.Link(i - 1, i);
  }
  for (int i = 0; i < main_count; ++i) {
    if (branch_every > 0 && (i % branch_every) == 0 && i > 0 &&
        i < main_count - 1) {
      const int leaf = g.AddNode(i * spacing, 0.0, -spacing);
      g.Link(i, leaf);
    }
  }
  g.ComputeDegrees();
}

inline void MakeDisconnected(NavGraph& g, int side, double spacing = 4.0,
                             double gap = 100.0) {
  const int base = g.node_count();
  MakeGrid(g, side, side, spacing);
  for (int y = 0; y < side; ++y) {
    for (int x = 0; x < side; ++x) {
      g.AddNode(gap + x * spacing, 0.0, y * spacing);
    }
  }
  for (int y = 0; y < side; ++y) {
    for (int x = 0; x < side; ++x) {
      const int i = base + side * side + y * side + x;
      if (x + 1 < side) g.Link(i, i + 1);
      if (y + 1 < side) g.Link(i, i + side);
    }
  }
  g.ComputeDegrees();
}

inline void MakeSpiral(NavGraph& g, int side, double spacing = 4.0) {
  for (int y = 0; y < side; ++y) {
    for (int x = 0; x < side; ++x) {
      g.AddNode(x * spacing, 0.0, y * spacing);
    }
  }
  int x0 = 0, y0 = 0, x1 = side - 1, y1 = side - 1;
  int prev = -1;
  while (x0 <= x1 && y0 <= y1) {
    for (int x = x0; x <= x1; ++x) {
      const int i = y0 * side + x;
      if (prev >= 0) g.Link(prev, i);
      prev = i;
    }
    ++y0;
    for (int y = y0; y <= y1; ++y) {
      const int i = y * side + x1;
      if (prev >= 0) g.Link(prev, i);
      prev = i;
    }
    --x1;
    if (y0 <= y1) {
      for (int x = x1; x >= x0; --x) {
        const int i = y1 * side + x;
        if (prev >= 0) g.Link(prev, i);
        prev = i;
      }
      --y1;
    }
    if (x0 <= x1) {
      for (int y = y1; y >= y0; --y) {
        const int i = y * side + x0;
        if (prev >= 0) g.Link(prev, i);
        prev = i;
      }
      ++x0;
    }
  }
  g.ComputeDegrees();
}

}  // namespace maps
}  // namespace navlab

#endif  // NAVLAB_NAV_MAPS_H

#endif  // NAV_ITEM_BRIDGE_UPSTREAM_NAVLAB_MIRROR_H
