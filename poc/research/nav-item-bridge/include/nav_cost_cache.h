// SPDX-License-Identifier: GPL-2.0-only
// nav_cost_cache.h - budgeted graph reachability, path-detour pricing,
// per-agent blocked-edge memory and O(1) path-cost caching.
//
// SCOPE
//  - Zero heap allocation: fixed-size arrays only, safe on stack or in BSS.
//  - Strict per-tick A* expansion budget (`TickExpansionBudget`).
//  - Shared `navlab::NavGraph` is read-only (`const`); runtime snags/blocked
//    corridors discovered by one bot live in `LocalBlockedEdgeTable` and never
//    mutate shared state across bots.
//  - Translates real A* graph travel distances into `ItemSnapshot` effective
//    positions for `itemai::ItemPlanner` while recording exact 3D pickup
//    coordinates in `TrueItemTable` for `NavGraphSink`.

#ifndef NAV_ITEM_BRIDGE_NAV_COST_CACHE_H
#define NAV_ITEM_BRIDGE_NAV_COST_CACHE_H

#include <cmath>
#include <cstdint>

#include "upstream_seams.h"

namespace navbridge {

/* ------------------------------------------------------------------------ */
/* Small geometry & hash helpers                                             */
/* ------------------------------------------------------------------------ */

inline itemai::Vec3 MakeVec3(double x, double y, double z) {
  itemai::Vec3 v;
  v.x = x;
  v.y = y;
  v.z = z;
  return v;
}

inline double PlanarDistXZ(double x1, double z1, double x2, double z2) {
  const double dx = x1 - x2;
  const double dz = z1 - z2;
  return std::sqrt(dx * dx + dz * dz);
}

inline uint32_t MixEpoch(uint32_t graph_epoch, uint32_t local_epoch) {
  uint32_t h = graph_epoch * 0x9E3779B9u ^ (local_epoch + 0x85EBCA6Bu);
  h ^= h >> 16;
  h *= 0x7FEB352Du;
  h ^= h >> 15;
  return h ? h : 1u;
}

/* ------------------------------------------------------------------------ */
/* Budget and bridge configuration                                           */
/* ------------------------------------------------------------------------ */

struct BridgeBudgetConfig {
  int max_expansions_per_tick;   // Hard total A* node expansions per bot tick
  int max_expand_goal_search;    // Per-search cap for active goal routing
  int max_expand_cost_probe;     // Per-search cap for candidate cost probing
  int max_cost_probes_per_tick;  // Max uncached candidate items probed/tick
  double max_anchor_dist_m;      // Max planar snap distance to waypoint graph
  int blocked_edge_ttl_ticks;    // Per-agent temporary edge avoidance TTL
  int cost_cache_ttl_ticks;      // Cache entry lifetime in ticks
  bool enable_path_cost_projection;  // Price graph detours in ItemPlanner
  bool avoid_danger_edges;       // Optional: skip kEdgeDanger edges
  float route_variance;          // Per-bot deterministic route variety (0..0.5)

  BridgeBudgetConfig()
      : max_expansions_per_tick(512),
        max_expand_goal_search(256),
        max_expand_cost_probe(192),
        max_cost_probes_per_tick(8),
        max_anchor_dist_m(14.0),
        blocked_edge_ttl_ticks(200),
        cost_cache_ttl_ticks(120),
        enable_path_cost_projection(true),
        avoid_danger_edges(false),
        route_variance(0.08f) {}
};

/* ------------------------------------------------------------------------ */
/* Strict per-tick A* expansion budget                                       */
/* ------------------------------------------------------------------------ */

class TickExpansionBudget {
 public:
  explicit TickExpansionBudget(int limit = 512)
      : limit_(limit > 0 ? limit : 0),
        used_(0),
        searches_(0),
        clamped_events_(0) {}

  void Reset(int limit) {
    limit_ = limit > 0 ? limit : 0;
    used_ = 0;
    searches_ = 0;
    clamped_events_ = 0;
  }

  int limit() const { return limit_; }
  int used() const { return used_; }
  int searches() const { return searches_; }
  int clamped_events() const { return clamped_events_; }
  int Remaining() const { return used_ < limit_ ? (limit_ - used_) : 0; }

  int Grant(int desired_max) {
    if (desired_max <= 0) return 0;
    const int rem = Remaining();
    if (rem <= 0) {
      ++clamped_events_;
      return 0;
    }
    if (desired_max > rem) {
      ++clamped_events_;
      return rem;
    }
    return desired_max;
  }

  void Charge(int expanded) {
    if (expanded > 0) used_ += expanded;
    ++searches_;
  }

 private:
  int limit_;
  int used_;
  int searches_;
  int clamped_events_;
};

/* ------------------------------------------------------------------------ */
/* Per-agent temporary blocked edges (zero mutation of shared NavGraph)      */
/* ------------------------------------------------------------------------ */

class LocalBlockedEdgeTable {
 public:
  static constexpr int kMaxEntries = 16;

  LocalBlockedEdgeTable() : epoch_(1u) { Clear(); }

  void Clear() {
    for (int i = 0; i < kMaxEntries; ++i) {
      entries_[i].from = -1;
      entries_[i].to = -1;
      entries_[i].until_tick = 0;
    }
    ++epoch_;
  }

  void Expire(int tick) {
    bool changed = false;
    for (int i = 0; i < kMaxEntries; ++i) {
      if (entries_[i].from >= 0 && tick >= entries_[i].until_tick) {
        entries_[i].from = -1;
        entries_[i].to = -1;
        entries_[i].until_tick = 0;
        changed = true;
      }
    }
    if (changed) ++epoch_;
  }

  void BlockDirected(int from, int to, int until_tick) {
    if (from < 0 || to < 0 || from == to) return;
    int empty_idx = -1;
    int oldest_idx = 0;
    for (int i = 0; i < kMaxEntries; ++i) {
      if (entries_[i].from == static_cast<int16_t>(from) &&
          entries_[i].to == static_cast<int16_t>(to)) {
        if (until_tick > entries_[i].until_tick) {
          entries_[i].until_tick = until_tick;
          ++epoch_;
        }
        return;
      }
      if (entries_[i].from < 0 && empty_idx < 0) empty_idx = i;
      if (entries_[i].until_tick < entries_[oldest_idx].until_tick) {
        oldest_idx = i;
      }
    }
    const int slot = empty_idx >= 0 ? empty_idx : oldest_idx;
    entries_[slot].from = static_cast<int16_t>(from);
    entries_[slot].to = static_cast<int16_t>(to);
    entries_[slot].until_tick = until_tick;
    ++epoch_;
  }

  void BlockLink(int a, int b, int until_tick) {
    BlockDirected(a, b, until_tick);
    BlockDirected(b, a, until_tick);
  }

  void UnblockLink(int a, int b) {
    bool changed = false;
    for (int i = 0; i < kMaxEntries; ++i) {
      if ((entries_[i].from == static_cast<int16_t>(a) &&
           entries_[i].to == static_cast<int16_t>(b)) ||
          (entries_[i].from == static_cast<int16_t>(b) &&
           entries_[i].to == static_cast<int16_t>(a))) {
        entries_[i].from = -1;
        entries_[i].to = -1;
        entries_[i].until_tick = 0;
        changed = true;
      }
    }
    if (changed) ++epoch_;
  }

  bool IsBlocked(int from, int to, int tick) const {
    for (int i = 0; i < kMaxEntries; ++i) {
      if (entries_[i].from == static_cast<int16_t>(from) &&
          entries_[i].to == static_cast<int16_t>(to) &&
          tick < entries_[i].until_tick) {
        return true;
      }
    }
    return false;
  }

  bool HasActive(int tick) const {
    for (int i = 0; i < kMaxEntries; ++i) {
      if (entries_[i].from >= 0 && tick < entries_[i].until_tick) return true;
    }
    return false;
  }

  int ActiveCount(int tick) const {
    int n = 0;
    for (int i = 0; i < kMaxEntries; ++i) {
      if (entries_[i].from >= 0 && tick < entries_[i].until_tick) ++n;
    }
    return n;
  }

  uint32_t epoch() const { return epoch_; }

 private:
  struct Entry {
    int16_t from;
    int16_t to;
    int until_tick;
  };

  Entry entries_[kMaxEntries];
  uint32_t epoch_;
};

/* ------------------------------------------------------------------------ */
/* Budgeted A* wrapper supporting local blocked edges & danger avoidance     */
/* ------------------------------------------------------------------------ */

class ConstrainedNavSearch {
 public:
  ConstrainedNavSearch() : heap_count_(0), generation_(0) {
    for (int i = 0; i < navlab::kNavMaxNodes; ++i) {
      stamp_[i] = 0;
      closed_stamp_[i] = 0;
      parent_[i] = -1;
      g_[i] = 0.0f;
      f_[i] = 0.0f;
    }
  }

  // Runs A* within `budget.Grant(desired_expand)`. If budget is exhausted
  // before starting (`Grant == 0`), returns `kBudgetExhausted` with 0
  // expansions so the tick cap is never violated.
  navlab::NavPath Search(const navlab::NavGraph& graph, int from, int to,
                         int desired_expand, float variance, uint32_t seed,
                         const LocalBlockedEdgeTable* local_blocked, int tick,
                         bool avoid_danger, TickExpansionBudget* budget) {
    navlab::NavPath out;
    out.status = navlab::NavSearchStatus::kInvalidArgs;
    out.count = 0;
    out.cost = 0.0f;
    out.expanded = 0;
    if (!graph.Valid(from) || !graph.Valid(to)) return out;

    if (from == to) {
      out.status = navlab::NavSearchStatus::kFound;
      out.nodes[0] = static_cast<int16_t>(from);
      out.count = 1;
      return out;
    }

    int cap = desired_expand;
    if (budget != nullptr) {
      cap = budget->Grant(desired_expand);
      if (cap <= 0) {
        out.status = navlab::NavSearchStatus::kBudgetExhausted;
        out.nodes[0] = static_cast<int16_t>(from);
        out.count = 1;
        return out;
      }
    }

    const bool has_local =
        (local_blocked != nullptr && local_blocked->HasActive(tick));
    if (!has_local && !avoid_danger) {
      navlab::NavSearchConfig cfg;
      cfg.max_expand = cap;
      cfg.variance = variance;
      cfg.variance_seed = seed;
      out = base_astar_.Find(graph, from, to, cfg);
      if (budget != nullptr) budget->Charge(out.expanded);
      return out;
    }

    out = FindConstrained(graph, from, to, cap, variance, seed, local_blocked,
                          tick, avoid_danger);
    if (budget != nullptr) budget->Charge(out.expanded);
    return out;
  }

 private:
  navlab::NavPath FindConstrained(const navlab::NavGraph& graph, int from,
                                  int to, int cap, float raw_variance,
                                  uint32_t seed,
                                  const LocalBlockedEdgeTable* local_blocked,
                                  int tick, bool avoid_danger) {
    navlab::NavPath out;
    out.status = navlab::NavSearchStatus::kInvalidArgs;
    out.count = 0;
    out.cost = 0.0f;
    out.expanded = 0;

    const int budget = cap < 1 ? 1
                               : (cap > navlab::kNavMaxNodes
                                      ? navlab::kNavMaxNodes
                                      : cap);
    const float variance =
        !(raw_variance > 0.0f) ? 0.0f
                               : (raw_variance > 0.5f ? 0.5f : raw_variance);
    const float heur_scale = 1.0f - variance;

    ++generation_;
    heap_count_ = 0;
    float best_deep_g = -1.0f;
    int16_t best_deep_node = static_cast<int16_t>(from);
    float best_near_h = 1e30f;
    int16_t best_near_node = static_cast<int16_t>(from);

    stamp_[from] = generation_;
    g_[from] = 0.0f;
    f_[from] = graph.PlanarDist(from, to) * heur_scale;
    parent_[from] = -1;
    HeapPush(from);

    while (heap_count_ > 0) {
      const int current = HeapPop();
      if (closed_stamp_[current] == generation_) continue;
      closed_stamp_[current] = generation_;
      ++out.expanded;

      if (current == to) {
        out.status = navlab::NavSearchStatus::kFound;
        Reconstruct(out, from, to, graph);
        return out;
      }

      if (g_[current] > best_deep_g) {
        best_deep_g = g_[current];
        best_deep_node = static_cast<int16_t>(current);
      }
      const float h = graph.PlanarDist(current, to);
      if (h < best_near_h) {
        best_near_h = h;
        best_near_node = static_cast<int16_t>(current);
      }

      if (out.expanded >= budget) break;

      const int count = graph.edge_count(current);
      for (int e = 0; e < count; ++e) {
        const navlab::NavEdge& edge = graph.edge(current, e);
        if (edge.flags & navlab::kEdgeBlocked) continue;
        if (avoid_danger && (edge.flags & navlab::kEdgeDanger)) continue;
        const int next = edge.to;
        if (!graph.Valid(next) || closed_stamp_[next] == generation_) continue;
        if (local_blocked != nullptr &&
            local_blocked->IsBlocked(current, next, tick)) {
          continue;
        }

        const float step = EdgeCost(edge, current, next, variance, seed);
        const float tentative = g_[current] + step;
        if (stamp_[next] != generation_ || tentative < g_[next]) {
          stamp_[next] = generation_;
          g_[next] = tentative;
          f_[next] = tentative + graph.PlanarDist(next, to) * heur_scale;
          parent_[next] = static_cast<int16_t>(current);
          HeapPush(next);
        }
      }
    }

    const bool exhausted = (out.expanded >= budget);
    out.status = exhausted ? navlab::NavSearchStatus::kBudgetExhausted
                           : navlab::NavSearchStatus::kUnreachable;
    Reconstruct(out, from, exhausted ? best_deep_node : best_near_node, graph);
    return out;
  }

  static float EdgeCost(const navlab::NavEdge& edge, int from, int to,
                        float variance, uint32_t seed) {
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

  void Reconstruct(navlab::NavPath& out, int from, int end,
                   const navlab::NavGraph& graph) const {
    int16_t rev[navlab::kNavMaxPathNodes];
    int n = 0;
    int cur = end;
    while (cur >= 0 && n < navlab::kNavMaxPathNodes) {
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
      out.cost += RawEdgeCost(graph, out.nodes[i], out.nodes[i + 1]);
    }
  }

  static float RawEdgeCost(const navlab::NavGraph& graph, int a, int b) {
    const int count = graph.edge_count(a);
    for (int e = 0; e < count; ++e) {
      if (graph.edge(a, e).to == static_cast<int16_t>(b)) {
        return graph.edge(a, e).cost;
      }
    }
    return graph.PlanarDist(a, b);
  }

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
    if (heap_count_ >= navlab::kNavMaxNodes) return;
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
      const int p = (i - 1) / 2;
      if (!HeapBetter(i, p)) break;
      const int16_t t = heap_[i];
      heap_[i] = heap_[p];
      heap_[p] = t;
      i = p;
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
      const int16_t t = heap_[i];
      heap_[i] = heap_[best];
      heap_[best] = t;
      i = best;
    }
  }

  navlab::NavAStar base_astar_;
  float g_[navlab::kNavMaxNodes];
  float f_[navlab::kNavMaxNodes];
  int16_t parent_[navlab::kNavMaxNodes];
  uint32_t stamp_[navlab::kNavMaxNodes];
  uint32_t closed_stamp_[navlab::kNavMaxNodes];
  int16_t heap_[navlab::kNavMaxNodes];
  int heap_count_;
  uint32_t generation_;
};

/* ------------------------------------------------------------------------ */
/* True item lookup table (maps item_id -> true 3D pos & path metrics)       */
/* ------------------------------------------------------------------------ */

struct TrueItemEntry {
  int item_id;
  itemai::Vec3 true_pos;
  double euclidean_m;
  double effective_path_m;
  int anchor_node;
  bool reachable;
  bool path_verified;

  TrueItemEntry()
      : item_id(-1),
        true_pos(),
        euclidean_m(0.0),
        effective_path_m(0.0),
        anchor_node(-1),
        reachable(true),
        path_verified(false) {}
};

class TrueItemTable {
 public:
  TrueItemTable() : count_(0) {}

  void Clear() { count_ = 0; }
  int count() const { return count_; }

  void Set(int index, const TrueItemEntry& e) {
    if (index < 0 || index >= itemai::kMaxItems) return;
    entries_[index] = e;
    if (index + 1 > count_) count_ = index + 1;
  }

  const TrueItemEntry* Find(int item_id) const {
    if (item_id < 0) return nullptr;
    for (int i = 0; i < count_; ++i) {
      if (entries_[i].item_id == item_id) return &entries_[i];
    }
    return nullptr;
  }

  const TrueItemEntry& At(int index) const { return entries_[index]; }

 private:
  TrueItemEntry entries_[itemai::kMaxItems];
  int count_;
};

/* ------------------------------------------------------------------------ */
/* Per-agent path-cost & reachability memoization                            */
/* ------------------------------------------------------------------------ */

class PathCostCache {
 public:
  static constexpr int kSlots = 64;

  struct CachedRouteSummary {
    bool valid;
    bool reachable;
    int16_t second_node;       // First hop after start_node (-1 if same node)
    float cost_from_second_m;  // Graph cost from second_node .. goal_node
    float total_graph_cost_m;
  };

  PathCostCache() { Clear(); }

  void Clear() {
    for (int i = 0; i < kSlots; ++i) {
      slots_[i].used = false;
      slots_[i].start_node = -1;
      slots_[i].goal_node = -1;
      slots_[i].epoch = 0;
      slots_[i].expires_tick = 0;
      slots_[i].reachable = false;
      slots_[i].second_node = -1;
      slots_[i].cost_from_second_m = 0.0f;
      slots_[i].total_graph_cost_m = 0.0f;
    }
    hits_ = 0;
    misses_ = 0;
  }

  int hits() const { return hits_; }
  int misses() const { return misses_; }

  CachedRouteSummary Lookup(int start_node, int goal_node, uint32_t epoch,
                            int tick) {
    CachedRouteSummary res = {false, false, -1, 0.0f, 0.0f};
    if (start_node < 0 || goal_node < 0) return res;
    for (int i = 0; i < kSlots; ++i) {
      const Slot& s = slots_[i];
      if (!s.used) continue;
      if (s.start_node == static_cast<int16_t>(start_node) &&
          s.goal_node == static_cast<int16_t>(goal_node) &&
          s.epoch == epoch) {
        // Unreachable verdicts remain exact until `epoch` changes; reachable
        // path costs refresh after `expires_tick`.
        if (!s.reachable || tick < s.expires_tick) {
          ++hits_;
          res.valid = true;
          res.reachable = s.reachable;
          res.second_node = s.second_node;
          res.cost_from_second_m = s.cost_from_second_m;
          res.total_graph_cost_m = s.total_graph_cost_m;
          return res;
        }
      }
    }
    ++misses_;
    return res;
  }

  void StoreReachable(int start_node, int goal_node, uint32_t epoch,
                      int expires_tick, int second_node,
                      float cost_from_second_m, float total_graph_cost_m) {
    const int idx = AllocateSlot(start_node, goal_node, epoch, expires_tick);
    Slot& s = slots_[idx];
    s.used = true;
    s.start_node = static_cast<int16_t>(start_node);
    s.goal_node = static_cast<int16_t>(goal_node);
    s.epoch = epoch;
    s.expires_tick = expires_tick;
    s.reachable = true;
    s.second_node = static_cast<int16_t>(second_node);
    s.cost_from_second_m = cost_from_second_m;
    s.total_graph_cost_m = total_graph_cost_m;
  }

  void StoreUnreachable(int start_node, int goal_node, uint32_t epoch,
                        int tick) {
    const int idx = AllocateSlot(start_node, goal_node, epoch, tick + 100000);
    Slot& s = slots_[idx];
    s.used = true;
    s.start_node = static_cast<int16_t>(start_node);
    s.goal_node = static_cast<int16_t>(goal_node);
    s.epoch = epoch;
    s.expires_tick = tick + 100000;
    s.reachable = false;
    s.second_node = -1;
    s.cost_from_second_m = 0.0f;
    s.total_graph_cost_m = 0.0f;
  }

 private:
  struct Slot {
    bool used;
    int16_t start_node;
    int16_t goal_node;
    uint32_t epoch;
    int expires_tick;
    bool reachable;
    int16_t second_node;
    float cost_from_second_m;
    float total_graph_cost_m;
  };

  int AllocateSlot(int start_node, int goal_node, uint32_t epoch, int /*now*/) {
    int unused_idx = -1;
    int oldest_idx = 0;
    for (int i = 0; i < kSlots; ++i) {
      if (slots_[i].used &&
          slots_[i].start_node == static_cast<int16_t>(start_node) &&
          slots_[i].goal_node == static_cast<int16_t>(goal_node)) {
        return i;
      }
      if (!slots_[i].used && unused_idx < 0) unused_idx = i;
      if (slots_[i].used &&
          (slots_[i].epoch != epoch ||
           slots_[i].expires_tick < slots_[oldest_idx].expires_tick)) {
        oldest_idx = i;
      }
    }
    return unused_idx >= 0 ? unused_idx : oldest_idx;
  }

  Slot slots_[kSlots];
  int hits_;
  int misses_;
};

/* ------------------------------------------------------------------------ */
/* World Path Enricher (Graph Reachability + Detour Cost -> ItemWorld)       */
/* ------------------------------------------------------------------------ */

struct EnrichmentStats {
  int total_items;
  int off_mesh_unreachable;
  int graph_unreachable;
  int cache_hits;
  int probes_executed;
  int detours_projected;

  EnrichmentStats()
      : total_items(0),
        off_mesh_unreachable(0),
        graph_unreachable(0),
        cache_hits(0),
        probes_executed(0),
        detours_projected(0) {}
};

class WorldPathEnricher {
 public:
  WorldPathEnricher() {}

  void Reset() { cache_.Clear(); }

  const PathCostCache& cache() const { return cache_; }

  // Enriches `raw_world` into `adapted_world` (backed by `adapted_storage`)
  // and fills `true_table` with authoritative pickup coordinates.
  // Never modifies `ItemPlanner` rules: only populates `ItemSnapshot::reachable`
  // and projects detour travel distance along the item ray.
  EnrichmentStats Enrich(const navlab::NavGraph& graph, uint32_t graph_epoch,
                         const BridgeBudgetConfig& cfg, uint32_t bot_seed,
                         const itemai::ItemProfile& profile,
                         int active_goal_id, const itemai::ItemWorld& raw_world,
                         ConstrainedNavSearch& search,
                         const LocalBlockedEdgeTable& local_blocked,
                         TickExpansionBudget& tick_budget,
                         itemai::ItemSnapshot* adapted_storage,
                         itemai::ItemWorld* adapted_world,
                         TrueItemTable* true_table) {
    EnrichmentStats stats;
    *adapted_world = raw_world;
    true_table->Clear();

    // Preserve fail-closed behaviour on malformed snapshots.
    if (raw_world.count <= 0 || raw_world.count > itemai::kMaxItems ||
        raw_world.items == nullptr) {
      return stats;
    }

    stats.total_items = raw_world.count;
    adapted_world->items = adapted_storage;
    const int tick = raw_world.combat.tick;

    // Without a loaded waypoint graph, keep raw Euclidean world untouched.
    if (graph.node_count() <= 0) {
      for (int i = 0; i < raw_world.count; ++i) {
        adapted_storage[i] = raw_world.items[i];
        TrueItemEntry te;
        te.item_id = raw_world.items[i].id;
        te.true_pos = raw_world.items[i].pos;
        te.euclidean_m =
            itemai::Distance(raw_world.self.eye, raw_world.items[i].pos);
        te.effective_path_m = te.euclidean_m;
        te.anchor_node = -1;
        te.reachable = raw_world.items[i].reachable;
        te.path_verified = false;
        true_table->Set(i, te);
      }
      return stats;
    }

    const uint32_t epoch = MixEpoch(graph_epoch, local_blocked.epoch());
    const int bot_node = graph.NearestNode(raw_world.self.eye.x,
                                           raw_world.self.eye.z,
                                           cfg.max_anchor_dist_m);

    int uncached_indices[itemai::kMaxItems];
    double uncached_keys[itemai::kMaxItems];
    int uncached_count = 0;

    const double speed = raw_world.self.move_speed_mps > 0.1
                             ? raw_world.self.move_speed_mps
                             : 0.1;
    const double max_euclid_m =
        (profile.tuning.max_search_time_s + 0.5) * speed;

    for (int i = 0; i < raw_world.count; ++i) {
      const itemai::ItemSnapshot& raw_it = raw_world.items[i];
      adapted_storage[i] = raw_it;

      TrueItemEntry te;
      te.item_id = raw_it.id;
      te.true_pos = raw_it.pos;
      te.euclidean_m = itemai::Distance(raw_world.self.eye, raw_it.pos);
      te.effective_path_m = te.euclidean_m;
      te.reachable = raw_it.reachable;
      te.path_verified = false;

      if (!raw_it.reachable || raw_it.respawn_s > 0.0) {
        true_table->Set(i, te);
        continue;
      }

      // Immediate touch range needs no graph anchor.
      if (te.euclidean_m <= itemai::kArrivalRadiusM) {
        te.path_verified = true;
        true_table->Set(i, te);
        continue;
      }

      const int item_node = graph.NearestNode(raw_it.pos.x, raw_it.pos.z,
                                              cfg.max_anchor_dist_m);
      te.anchor_node = item_node;

      if (bot_node < 0 || item_node < 0) {
        adapted_storage[i].reachable = false;
        te.reachable = false;
        te.path_verified = true;
        ++stats.off_mesh_unreachable;
        true_table->Set(i, te);
        continue;
      }

      if (bot_node == item_node) {
        te.path_verified = true;
        true_table->Set(i, te);
        continue;
      }

      // Fast O(1) cache lookup.
      const int hits_before = cache_.hits();
      const PathCostCache::CachedRouteSummary cached =
          cache_.Lookup(bot_node, item_node, epoch, tick);
      if (cache_.hits() > hits_before) ++stats.cache_hits;

      if (cached.valid) {
        te.path_verified = true;
        if (!cached.reachable) {
          adapted_storage[i].reachable = false;
          te.reachable = false;
          ++stats.graph_unreachable;
        } else {
          const double d_eff = EffectiveDistanceFromSummary(
              graph, raw_world.self.eye, raw_it.pos, te.euclidean_m, item_node,
              cached.second_node, cached.cost_from_second_m,
              cached.total_graph_cost_m);
          te.effective_path_m = d_eff;
          if (cfg.enable_path_cost_projection && d_eff > te.euclidean_m + 0.05) {
            adapted_storage[i].pos =
                ProjectAlongRay(raw_world.self.eye, raw_it.pos, te.euclidean_m, d_eff);
            ++stats.detours_projected;
          }
        }
        true_table->Set(i, te);
        continue;
      }

      true_table->Set(i, te);

      // Candidate pre-filter before spending A* expansions:
      //  - Active goal always gets priority.
      //  - Skip items already outside straight-line max_search_time_s or with
      //    trivially zero need (e.g. health at 100% HP).
      const bool is_active_goal = (raw_it.id == active_goal_id && active_goal_id >= 0);
      if (!is_active_goal) {
        if (te.euclidean_m > max_euclid_m) continue;
        if (!QuickMaybeNeeded(raw_world, raw_it)) continue;
      }
      uncached_indices[uncached_count] = i;
      uncached_keys[uncached_count] =
          is_active_goal ? -1e9 : te.euclidean_m;
      ++uncached_count;
    }

    // Deterministic insertion sort: active goal first, then nearest Euclidean.
    for (int a = 1; a < uncached_count; ++a) {
      const int idx = uncached_indices[a];
      const double key = uncached_keys[a];
      int b = a - 1;
      while (b >= 0 && uncached_keys[b] > key) {
        uncached_indices[b + 1] = uncached_indices[b];
        uncached_keys[b + 1] = uncached_keys[b];
        --b;
      }
      uncached_indices[b + 1] = idx;
      uncached_keys[b + 1] = key;
    }

    const int max_probes = cfg.max_cost_probes_per_tick > 0
                               ? cfg.max_cost_probes_per_tick
                               : 0;
    for (int p = 0; p < uncached_count && stats.probes_executed < max_probes; ++p) {
      if (tick_budget.Remaining() < 4) break;
      const int idx = uncached_indices[p];
      const itemai::ItemSnapshot& raw_it = raw_world.items[idx];
      TrueItemEntry te = true_table->At(idx);

      const navlab::NavPath path = search.Search(
          graph, bot_node, te.anchor_node, cfg.max_expand_cost_probe,
          cfg.route_variance, bot_seed, &local_blocked, tick,
          cfg.avoid_danger_edges, &tick_budget);
      ++stats.probes_executed;

      if (path.status == navlab::NavSearchStatus::kUnreachable ||
          path.status == navlab::NavSearchStatus::kInvalidArgs) {
        cache_.StoreUnreachable(bot_node, te.anchor_node, epoch, tick);
        adapted_storage[idx].reachable = false;
        te.reachable = false;
        te.path_verified = true;
        ++stats.graph_unreachable;
      } else if (path.status == navlab::NavSearchStatus::kFound) {
        int second_node = -1;
        float cost_from_second = path.cost;
        if (path.count >= 2) {
          second_node = path.nodes[1];
          const float first_step = FirstEdgeCost(graph, path.nodes[0], path.nodes[1]);
          cost_from_second = path.cost > first_step ? (path.cost - first_step) : 0.0f;
        }
        cache_.StoreReachable(bot_node, te.anchor_node, epoch,
                              tick + cfg.cost_cache_ttl_ticks, second_node,
                              cost_from_second, path.cost);
        const double d_eff = EffectiveDistanceFromSummary(
            graph, raw_world.self.eye, raw_it.pos, te.euclidean_m,
            te.anchor_node, static_cast<int16_t>(second_node), cost_from_second,
            path.cost);
        te.effective_path_m = d_eff;
        te.path_verified = true;
        if (cfg.enable_path_cost_projection && d_eff > te.euclidean_m + 0.05) {
          adapted_storage[idx].pos =
              ProjectAlongRay(raw_world.self.eye, raw_it.pos, te.euclidean_m, d_eff);
          ++stats.detours_projected;
        }
      } else if (path.status == navlab::NavSearchStatus::kBudgetExhausted) {
        // Admissible lower-bound estimate from the frontier node without
        // falsely blacklisting a long reachable corridor.
        if (path.count >= 1) {
          const int frontier = path.nodes[path.count - 1];
          const navlab::NavNode& fn = graph.node(frontier);
          const double rem_lb =
              PlanarDistXZ(fn.x, fn.z, raw_it.pos.x, raw_it.pos.z);
          const double lb = static_cast<double>(path.cost) + rem_lb;
          if (lb > te.euclidean_m) te.effective_path_m = lb;
          if (cfg.enable_path_cost_projection &&
              te.effective_path_m > te.euclidean_m + 0.05) {
            adapted_storage[idx].pos = ProjectAlongRay(
                raw_world.self.eye, raw_it.pos, te.euclidean_m, te.effective_path_m);
            ++stats.detours_projected;
          }
        }
      }
      true_table->Set(idx, te);
    }

    return stats;
  }

 private:
  static bool QuickMaybeNeeded(const itemai::ItemWorld& w,
                               const itemai::ItemSnapshot& it) {
    const double hf = w.self.max_health > 0.0
                          ? w.self.health / w.self.max_health
                          : 1.0;
    const double af = w.self.max_armor > 0.0
                          ? w.self.armor / w.self.max_armor
                          : 1.0;
    switch (it.kind) {
      case itemai::ItemKind::kHealth:
        return hf < itemai::kFullHealthFrac;
      case itemai::ItemKind::kArmor:
        return af < itemai::kFullHealthFrac;
      case itemai::ItemKind::kAmmo:
        if (it.weapon_index < 1 || it.weapon_index > itemai::kWeaponCount) {
          return false;
        }
        return itemai::WeaponOwned(w.self.owned_weapons, it.weapon_index);
      default:
        return true;
    }
  }

  static float FirstEdgeCost(const navlab::NavGraph& graph, int a, int b) {
    const int n = graph.edge_count(a);
    for (int e = 0; e < n; ++e) {
      if (graph.edge(a, e).to == static_cast<int16_t>(b)) {
        return graph.edge(a, e).cost;
      }
    }
    return graph.PlanarDist(a, b);
  }

  static double EffectiveDistanceFromSummary(
      const navlab::NavGraph& graph, const itemai::Vec3& bot_eye,
      const itemai::Vec3& item_pos, double d_euclid, int goal_node,
      int16_t second_node, float cost_from_second, float total_graph_cost) {
    const navlab::NavNode& gn = graph.node(goal_node);
    const double end_leg = PlanarDistXZ(gn.x, gn.z, item_pos.x, item_pos.z);
    double path_m = 0.0;
    if (second_node >= 0 && graph.Valid(second_node)) {
      const navlab::NavNode& sn = graph.node(second_node);
      const double first_leg = PlanarDistXZ(bot_eye.x, bot_eye.z, sn.x, sn.z);
      path_m = first_leg + static_cast<double>(cost_from_second) + end_leg;
    } else {
      path_m = static_cast<double>(total_graph_cost) + end_leg;
    }
    return path_m > d_euclid ? path_m : d_euclid;
  }

  static itemai::Vec3 ProjectAlongRay(const itemai::Vec3& origin,
                                      const itemai::Vec3& target,
                                      double d_euclid, double d_target) {
    if (d_euclid < 1e-6) {
      return MakeVec3(origin.x + d_target, origin.y, origin.z);
    }
    const double scale = d_target / d_euclid;
    return MakeVec3(origin.x + (target.x - origin.x) * scale,
                    origin.y + (target.y - origin.y) * scale,
                    origin.z + (target.z - origin.z) * scale);
  }

  PathCostCache cache_;
};

}  // namespace navbridge

#endif  // NAV_ITEM_BRIDGE_NAV_COST_CACHE_H
