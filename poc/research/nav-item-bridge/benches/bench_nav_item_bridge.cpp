// SPDX-License-Identifier: GPL-2.0-only
// bench_nav_item_bridge.cpp - CPU latency, A* expansion budget, cache hit-rate,
// memory footprint (`sizeof`) and runtime zero-heap-allocation verification.

#include <algorithm>
#include <chrono>
#include <cmath>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <new>

#include "arena_sim.h"

/* ------------------------------------------------------------------------ */
/* Global operator new trap: proves 0 heap allocations during hot-path ticks */
/* ------------------------------------------------------------------------ */
namespace {
volatile bool g_trap_allocs = false;
long long g_alloc_calls = 0;
long long g_alloc_bytes = 0;
}  // namespace

void* operator new(std::size_t sz) {
  if (g_trap_allocs) {
    ++g_alloc_calls;
    g_alloc_bytes += static_cast<long long>(sz);
  }
  void* p = std::malloc(sz ? sz : 1);
  if (!p) throw std::bad_alloc();
  return p;
}

void* operator new[](std::size_t sz) {
  if (g_trap_allocs) {
    ++g_alloc_calls;
    g_alloc_bytes += static_cast<long long>(sz);
  }
  void* p = std::malloc(sz ? sz : 1);
  if (!p) throw std::bad_alloc();
  return p;
}

void operator delete(void* p) noexcept { std::free(p); }
void operator delete[](void* p) noexcept { std::free(p); }
#if __cplusplus >= 201402L
void operator delete(void* p, std::size_t) noexcept { std::free(p); }
void operator delete[](void* p, std::size_t) noexcept { std::free(p); }
#endif

namespace {

constexpr int kMaxRecordedTicks = 12000;
double g_tick_us[kMaxRecordedTicks];

struct BenchSummary {
  const char* label;
  int nodes;
  int items;
  int bots;
  int server_ticks;
  double mean_server_tick_us;
  double p50_server_tick_us;
  double p95_server_tick_us;
  double p99_server_tick_us;
  double max_server_tick_us;
  double mean_bot_tick_us;
  double mean_expansions_per_bot_tick;
  int max_expansions_bot_tick;
  int budget_limit;
  int budget_violations;
  double cache_hit_pct;
  long long heap_allocs;
};

void BuildGridArena(navbridge::ArenaSim* sim, int side, int item_count,
                    int bot_count, int max_expansions) {
  sim->Reset();
  sim->set_combat_damage_enabled(true);
  navlab::NavGraph& g = sim->mutable_graph();

  for (int r = 0; r < side; ++r) {
    for (int c = 0; c < side; ++c) {
      g.AddNode(c * 5.0, 0.0, -r * 5.0, navlab::kNodeNone, 1.5);
    }
  }
  for (int r = 0; r < side; ++r) {
    for (int c = 0; c < side; ++c) {
      const int u = r * side + c;
      const bool pillar = ((r % 6 == 2) && (c % 5 != 0));
      const uint32_t fl = pillar ? navlab::kEdgeBlocked : navlab::kEdgeNone;
      if (c + 1 < side) g.Link(u, u + 1, fl);
      if (r + 1 < side) g.Link(u, u + side, fl);
    }
  }

  const double span = (side - 1) * 5.0;
  sim->AddWall(span * 0.25, -span * 0.30, span * 0.45, -span * 0.30, 0.4, true,
               true);
  sim->AddWall(span * 0.55, -span * 0.70, span * 0.75, -span * 0.70, 0.4, true,
               true);

  navbridge::BridgeBudgetConfig bcfg;
  bcfg.max_expansions_per_tick = max_expansions;
  bcfg.max_cost_probes_per_tick = 4;
  bcfg.max_expand_cost_probe = max_expansions / 3;
  bcfg.max_expand_goal_search = max_expansions;

  for (int b = 0; b < bot_count; ++b) {
    navbridge::BridgeProfileBundle bundle{};
    navbridge::BuildBridgeProfile(1 + (b % 5), b % 6, 0xB34C0000u + b, b,
                                  "BenchBot", &bundle);
    const int r = (b * 5) % side;
    const int c = (b * 7) % side;
    const int bi = sim->AddBot(bundle, c * 5.0, -r * 5.0, b * 45.0, bcfg);
    sim->bot(bi).health = 55.0 + (b % 3) * 15.0;
  }

  for (int i = 0; i < item_count; ++i) {
    const int r = (i * 3 + 1) % side;
    const int c = (i * 5 + 2) % side;
    itemai::ItemKind kind = itemai::ItemKind::kHealth;
    int widx = 0;
    int amt = 0;
    double val = 25.0;
    switch (i % 4) {
      case 0:
        kind = itemai::ItemKind::kHealth;
        val = (i % 8 == 0) ? 100.0 : 25.0;
        break;
      case 1:
        kind = itemai::ItemKind::kArmor;
        val = 50.0;
        break;
      case 2:
        kind = itemai::ItemKind::kWeapon;
        widx = (i % 8 == 2) ? 8 : 6;
        amt = 10;
        val = 30.0;
        break;
      case 3:
        kind = itemai::ItemKind::kAmmo;
        widx = 6;
        amt = 50;
        val = 15.0;
        break;
    }
    sim->AddItem(2000 + i, kind, c * 5.0, -r * 5.0, val, widx, amt, 140);
  }
}

BenchSummary RunWorkload(navbridge::ArenaSim* sim, const char* label, int side,
                         int items, int bots, int ticks, int max_expansions) {
  BuildGridArena(sim, side, items, bots, max_expansions);

  // Warm up 20 ticks outside timing window, then measure cleanly under alloc trap.
  for (int w = 0; w < 20; ++w) sim->StepTick();

  const long long allocs_before = g_alloc_calls;
  g_trap_allocs = true;

  long long total_expansions = 0;
  int max_exp_seen = 0;
  int violations = 0;
  long long cache_hits = 0;
  long long cache_probes = 0;
  double sum_us = 0.0;

  const int n_rec = ticks < kMaxRecordedTicks ? ticks : kMaxRecordedTicks;
  for (int t = 0; t < n_rec; ++t) {
    const auto t0 = std::chrono::steady_clock::now();

    // Extract single-agent AI cost vs full server tick (includes sim raycasts):
    // we time `StepTick()` end-to-end so raycasts + perception + item scoring +
    // A* + obstacle recovery + arbitration are ALL included conservatively!
    sim->StepTick();

    const auto t1 = std::chrono::steady_clock::now();
    const double us =
        std::chrono::duration<double, std::micro>(t1 - t0).count();
    g_tick_us[t] = us;
    sum_us += us;

    for (int b = 0; b < bots; ++b) {
      navbridge::SimBot& bot = sim->bot(b);
      if (!bot.alive && (t % 30 == 0)) {
        bot.alive = true;
        bot.health = 75.0;
      }
      const navbridge::ArbitrationTrace& tr = bot.last_output.trace;
      total_expansions += tr.expansions_used;
      if (tr.expansions_used > max_exp_seen) max_exp_seen = tr.expansions_used;
      if (tr.expansions_used > max_expansions) ++violations;
      cache_hits += tr.cost_cache_hits;
      cache_probes += tr.cost_probes;
    }
  }

  g_trap_allocs = false;
  const long long allocs_delta = g_alloc_calls - allocs_before;

  std::sort(g_tick_us, g_tick_us + n_rec);

  BenchSummary s{};
  s.label = label;
  s.nodes = sim->graph().node_count();
  s.items = items;
  s.bots = bots;
  s.server_ticks = n_rec;
  s.mean_server_tick_us = sum_us / n_rec;
  s.p50_server_tick_us = g_tick_us[static_cast<int>(n_rec * 0.50)];
  s.p95_server_tick_us = g_tick_us[static_cast<int>(n_rec * 0.95)];
  s.p99_server_tick_us = g_tick_us[static_cast<int>(n_rec * 0.99)];
  s.max_server_tick_us = g_tick_us[n_rec - 1];
  s.mean_bot_tick_us = s.mean_server_tick_us / (bots > 0 ? bots : 1);
  s.mean_expansions_per_bot_tick =
      static_cast<double>(total_expansions) / (n_rec * (bots > 0 ? bots : 1));
  s.max_expansions_bot_tick = max_exp_seen;
  s.budget_limit = max_expansions;
  s.budget_violations = violations;
  const long long lookups = cache_hits + cache_probes;
  s.cache_hit_pct =
      lookups > 0 ? (100.0 * static_cast<double>(cache_hits) / lookups) : 100.0;
  s.heap_allocs = allocs_delta;
  return s;
}

// Static arena instance so `main` stack stays tiny.
navbridge::ArenaSim g_sim;

}  // namespace

int main() {
  std::printf("=== nav-item-bridge: Memory Footprint & Zero-Alloc CPU Benchmark ===\n\n");

  const size_t sz_graph = sizeof(navlab::NavGraph);
  const size_t sz_human = sizeof(botcore::HumanBotPolicy);
  const size_t sz_item = sizeof(itemai::ItemPlanner);
  const size_t sz_cache = sizeof(navbridge::PathCostCache);
  const size_t sz_sink = sizeof(navbridge::NavGraphSink);
  const size_t sz_patrol = sizeof(navlab::NavAgent);
  const size_t sz_search = sizeof(navbridge::ConstrainedNavSearch);
  const size_t sz_agent = sizeof(navbridge::NavItemBridgeAgent);

  std::printf("--- 1. Static Memory Footprint (`sizeof`, zero dynamic heap) ---\n");
  std::printf("  Shared `const navlab::NavGraph` (1x/map) : %7zu B (%6.2f KiB)\n",
              sz_graph, sz_graph / 1024.0);
  std::printf("  `botcore::HumanBotPolicy` (Combat-KI)    : %7zu B (%6.2f KiB)\n",
              sz_human, sz_human / 1024.0);
  std::printf("  `itemai::ItemPlanner` (Item-Utility)     : %7zu B (%6.2f KiB)\n",
              sz_item, sz_item / 1024.0);
  std::printf("  `navbridge::PathCostCache` (128 entries) : %7zu B (%6.2f KiB)\n",
              sz_cache, sz_cache / 1024.0);
  std::printf("  `navbridge::NavGraphSink` (Goal Nav)     : %7zu B (%6.2f KiB)\n",
              sz_sink, sz_sink / 1024.0);
  std::printf("  `navlab::NavAgent` (Patrol/Reposition)   : %7zu B (%6.2f KiB)\n",
              sz_patrol, sz_patrol / 1024.0);
  std::printf("  `navbridge::ConstrainedNavSearch`        : %7zu B (%6.2f KiB)\n",
              sz_search, sz_search / 1024.0);
  std::printf("  --------------------------------------------------------------\n");
  std::printf("  Total `NavItemBridgeAgent` (1 bot)       : %7zu B (%6.2f KiB)\n",
              sz_agent, sz_agent / 1024.0);
  std::printf("  8 Bots + 1 Shared Graph                  : %7zu B (%6.2f KiB)\n",
              sz_agent * 8 + sz_graph, (sz_agent * 8 + sz_graph) / 1024.0);
  std::printf("  16 Bots + 1 Shared Graph (full server)   : %7zu B (%6.2f KiB)\n\n",
              sz_agent * 16 + sz_graph, (sz_agent * 16 + sz_graph) / 1024.0);

  const BenchSummary w_small =
      RunWorkload(&g_sim, "A_Small_64n_16i_1b", 8, 16, 1, 5000, 192);
  const BenchSummary w_med =
      RunWorkload(&g_sim, "B_RetailDM_256n_32i_8b", 16, 32, 8, 2500, 192);
  const BenchSummary w_large =
      RunWorkload(&g_sim, "C_Cathedral_1024n_64i_8b", 32, 64, 8, 1500, 192);

  const BenchSummary runs[3] = {w_small, w_med, w_large};

  std::printf("--- 2. 20 Hz Tick Latency & Expansion Budget (50,000 us = 100%% frame) ---\n");
  std::printf("%-25s | %5s %4s %4s | %7s %7s %7s %7s | %7s | %6s %7s | %6s | %5s\n",
              "Workload", "Nodes", "Item", "Bots", "Mean us", "P50 us", "P95 us",
              "P99 us", "Bot us", "AvgExp", "Max/Cap", "Hit%", "Alloc");
  std::printf("--------------------------------------------------------------------------------------------------------------------\n");

  bool gates_ok = true;
  for (int i = 0; i < 3; ++i) {
    const BenchSummary& r = runs[i];
    std::printf(
        "%-25s | %5d %4d %4d | %7.2f %7.2f %7.2f %7.2f | %7.2f | %6.2f %3d/%-3d | %5.1f%% | %5lld\n",
        r.label, r.nodes, r.items, r.bots, r.mean_server_tick_us,
        r.p50_server_tick_us, r.p95_server_tick_us, r.p99_server_tick_us,
        r.mean_bot_tick_us, r.mean_expansions_per_bot_tick,
        r.max_expansions_bot_tick, r.budget_limit, r.cache_hit_pct,
        r.heap_allocs);
    if (r.heap_allocs != 0) gates_ok = false;
    if (r.budget_violations != 0) gates_ok = false;
    // Hard gate: 8-bot server P99 must stay well below 2,500 us (5% of 50 ms).
    if (r.p99_server_tick_us > 2500.0) gates_ok = false;
  }

  const double pct_of_frame_cathedral =
      100.0 * (w_large.p99_server_tick_us / 50000.0);
  std::printf("\n--- 3. Budget Gate Verdict ---\n");
  std::printf("  Runtime heap allocations (all workloads) : %lld (gate: == 0)\n",
              w_small.heap_allocs + w_med.heap_allocs + w_large.heap_allocs);
  std::printf("  Expansion cap violations (all workloads) : %d (gate: == 0)\n",
              w_small.budget_violations + w_med.budget_violations +
                  w_large.budget_violations);
  std::printf("  Worst-case 8-bot 1024-node P99 share     : %.3f%% of 50 ms frame (%.2f us)\n",
              pct_of_frame_cathedral, w_large.p99_server_tick_us);
  std::printf("[%s] BENCHMARK GATES\n", gates_ok ? "PASS" : "FAIL");
  return gates_ok ? 0 : 1;
}
