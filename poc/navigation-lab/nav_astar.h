// nav_astar.h - engine-free, allocation-free A* over navlab::NavGraph.
//
// DESIGN GOALS (Navigation 2.0 prototype):
//  1. Hard search budget (max expanded nodes) so one pathological map can
//     never stall the 20 Hz decision cycle.
//  2. Deterministic: identical graph + start + goal + config always produce
//     the identical path. Heap ties break on higher g, then lower node index;
//     no wall-clock, no rand(), no pointer ordering.
//  3. Per-bot route variance: an optional deterministic edge-cost jitter
//     (seeded per bot) makes symmetric maps yield different - still valid and
//     near-optimal - routes for different bots.
//  4. Zero heap allocation: generation-stamped work arrays are reused across
//     searches; nothing is cleared per search, nothing is allocated ever.
//  5. Graceful failure: unreachable or budget-exhausted goals return the best
//     partial route found so far, so a bot walks TOWARD a goal it cannot
//     reach instead of freezing.
//
// COMPLEXITY: binary-heap A*, O(E log V) within the expansion budget; the
// heap holds at most one entry per node (decrease-key by linear scan, which
// is bounded by the budget and stays deterministic).
//
// LICENSING NOTE: independent implementation for the Alpha-Gaming project.
// CecilBotMod's navmesh A* (Sources/Bots/PathFinding/Navmesh.cpp) was used as
// an algorithmic reference only; notably its per-search allocation of one
// CPathPoint per node and its linear open-list minimum scan are deliberately
// NOT reproduced here.

#ifndef NAVLAB_NAV_ASTAR_H
#define NAVLAB_NAV_ASTAR_H

#include <cmath>
#include <cstdint>

#include "nav_graph.h"

namespace navlab {

enum class NavSearchStatus : uint8_t {
  kIdle = 0,
  kFound,            // complete path start..goal
  kUnreachable,      // goal not reachable; partial route toward it included
  kBudgetExhausted,  // budget hit; partial route to best frontier node
  kInvalidArgs,      // bad node indices / empty graph
};

struct NavPath {
  NavSearchStatus status;
  int16_t nodes[kNavMaxPathNodes];  // route from start toward goal
  int count;                        // entries used in nodes[]
  float cost;                       // summed (unvaried) cost of the route
  int expanded;                     // expansions performed (telemetry)
};

struct NavSearchConfig {
  int max_expand;          // hard budget of expanded nodes (<= kNavMaxNodes)
  float variance;          // 0..0.5 deterministic per-edge cost jitter
  uint32_t variance_seed;  // per-bot seed; irrelevant when variance == 0

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

  // Main entry. `from`/`to` are node indices. Blocked edges are skipped.
  NavPath Find(const NavGraph& graph, int from, int to,
               const NavSearchConfig& config) {
    NavPath out;
    out.status = NavSearchStatus::kInvalidArgs;
    out.count = 0;
    out.cost = 0.0f;
    out.expanded = 0;
    if (!graph.Valid(from) || !graph.Valid(to)) return out;

    // Degenerate case: already there.
    if (from == to) {
      out.status = NavSearchStatus::kFound;
      out.nodes[0] = static_cast<int16_t>(from);
      out.count = 1;
      return out;
    }

    const int budget = ClampBudget(config.max_expand);
    const float variance = ClampVariance(config.variance);
    const float heur_scale = 1.0f - variance;  // keeps h admissible

    ++generation_;  // invalidates all stamps without clearing
    heap_count_ = 0;
    // Partial-result trackers:
    //  - deepest expanded node (max g): where the search actually got to;
    //    used on budget exhaustion so a bot walks the explored corridor
    //    instead of freezing at the start (f is not monotone-useful in
    //    corridor graphs);
    //  - expanded node nearest the goal (min h): used when the goal is
    //    provably unreachable so the bot closes the distance as far as
    //    the graph allows.
    float best_deep_g_ = -1.0f;
    int16_t best_deep_node_ = static_cast<int16_t>(from);
    float best_near_h_ = 1e30f;
    int16_t best_near_node_ = static_cast<int16_t>(from);

    Touch(from);
    g_[from] = 0.0f;
    f_[from] = Heuristic(graph, from, to, heur_scale);
    parent_[from] = -1;
    HeapPush(from);

    while (heap_count_ > 0) {
      const int current = HeapPop();
      if (IsClosed(current)) continue;  // stale entry (decrease-key leftover)
      closed_stamp_[current] = generation_;
      ++out.expanded;

      if (current == to) {
        out.status = NavSearchStatus::kFound;
        Reconstruct(out, from, to, graph);
        return out;
      }

      // Update partial-result trackers deterministically (ties -> lower idx).
      if (g_[current] > best_deep_g_) {
        best_deep_g_ = g_[current];
        best_deep_node_ = static_cast<int16_t>(current);
      }
      const float h = Heuristic(graph, current, to, 1.0f);
      if (h < best_near_h_) {
        best_near_h_ = h;
        best_near_node_ = static_cast<int16_t>(current);
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

    // Goal not proven reachable within the budget: return the best partial
    // route. Budget exhaustion -> walk as deep as the search got; exhausted
    // open set -> walk as close to the goal as the graph allows.
    const bool exhausted = (out.expanded >= budget);
    out.status = exhausted ? NavSearchStatus::kBudgetExhausted
                           : NavSearchStatus::kUnreachable;
    Reconstruct(out, from, exhausted ? best_deep_node_ : best_near_node_,
                graph);
    return out;
  }

 private:
  /* --- helpers ---------------------------------------------------------- */

  static int ClampBudget(int budget) {
    if (budget < 1) return 1;
    return budget > kNavMaxNodes ? kNavMaxNodes : budget;
  }

  static float ClampVariance(float v) {
    if (!(v > 0.0f)) return 0.0f;
    return v > 0.5f ? 0.5f : v;
  }

  // Admissible, consistent heuristic: planar distance, scaled by the minimum
  // possible cost multiplier (1 - variance).
  static float Heuristic(const NavGraph& graph, int node, int goal,
                         float scale) {
    return graph.PlanarDist(node, goal) * scale;
  }

  // Deterministic per-edge jitter in [1-v, 1+v] from an integer hash of
  // (from, to, seed). Symmetric maps + different seeds => different routes.
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
    // Walk parent pointers into a temporary reversed list, then flip.
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
    // Report the true (unvaried) cost of the chosen route.
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

  /* --- generation-stamped state (never cleared, reused across searches) -- */

  void Touch(int node) { stamp_[node] = generation_; }
  bool IsTouched(int node) const { return stamp_[node] == generation_; }
  bool IsClosed(int node) const { return closed_stamp_[node] == generation_; }

  /* --- deterministic binary min-heap ------------------------------------- */
  // Order: lower f first; tie -> higher g first (deeper node, "greedy");
  // tie -> lower node index first. One live entry per node: HeapPush on an
  // already queued node performs a decrease-key style update.

  bool HeapBetter(int a, int b) const {  // is heap slot a better than b?
    if (f_[heap_[a]] != f_[heap_[b]]) return f_[heap_[a]] < f_[heap_[b]];
    if (g_[heap_[a]] != g_[heap_[b]]) return g_[heap_[a]] > g_[heap_[b]];
    return heap_[a] < heap_[b];
  }

  void HeapPush(int node) {
    // Already queued? Update in place and sift (f may have decreased).
    for (int i = 0; i < heap_count_; ++i) {
      if (heap_[i] == node) {
        HeapSiftUp(i);
        HeapSiftDown(i);
        return;
      }
    }
    if (heap_count_ >= kNavMaxNodes) return;  // bounded; budget hits first
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

  /* --- work arrays ------------------------------------------------------- */
  float g_[kNavMaxNodes];
  float f_[kNavMaxNodes];
  int16_t parent_[kNavMaxNodes];
  uint32_t stamp_[kNavMaxNodes];
  uint32_t closed_stamp_[kNavMaxNodes];  // == generation_ when closed
  int16_t heap_[kNavMaxNodes];
  int heap_count_;
  uint32_t generation_;
};

}  // namespace navlab

#endif  // NAVLAB_NAV_ASTAR_H
