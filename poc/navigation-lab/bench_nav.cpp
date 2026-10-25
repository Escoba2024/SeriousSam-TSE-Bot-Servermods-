// bench_nav.cpp - measured CPU/memory benchmarks for the navigation lab.
//
// Everything printed here is MEASURED on the host at run time (steady_clock),
// never estimated. Workload per bot: patrol with deterministic reposition
// phases (target seen -> lost), kinematic simulation at 20 Hz, 10 m/s.
//
// Sections:
//   1. steady-state tick cost: 1/4/8/16 concurrent agents on 16x16 and
//      32x32 waypoint grids (1200 ticks = 60 s sim time each),
//   2. worst-case single A* search latency (budgeted and unbudgeted),
//   3. static memory footprint (sizeof) + used-bytes estimate,
//   4. heap-allocation proof: operator new is trapped during the measured
//      section - any allocation aborts the run.
//
// Build: g++ -std=c++17 -O2 -Wall -Wextra -o bench_nav bench_nav.cpp

#include <chrono>
#include <cstdio>
#include <cstdlib>
#include <cmath>
#include <new>
#include "nav_agent.h"
#include "nav_maps.h"

using namespace navlab;

/* ------------------------------------------------------------------------ */
/* Heap-allocation trap (armed only around the measured section)             */
/* ------------------------------------------------------------------------ */

static volatile bool g_alloc_armed = false;
static long g_alloc_count = 0;

void* operator new(std::size_t n) {
  if (g_alloc_armed) {
    ++g_alloc_count;
    std::fprintf(stderr, "FATAL: heap allocation (%zu bytes) in measured "
                         "section\n", n);
    std::abort();
  }
  return std::malloc(n);
}
void operator delete(void* p) noexcept { std::free(p); }
void operator delete(void* p, std::size_t) noexcept { std::free(p); }
void* operator new[](std::size_t n) { return operator new(n); }
void operator delete[](void* p) noexcept { operator delete(p); }
void operator delete[](void* p, std::size_t) noexcept { operator delete(p); }

/* ------------------------------------------------------------------------ */
/* Kinematic simulation (identical semantics to the test suite)              */
/* ------------------------------------------------------------------------ */

struct BenchBot {
  NavAgent agent;
  double x, z, yaw_deg;
  bool last_moved;
};

static void PlaceBots(BenchBot* bots, int count, int w, int h) {
  for (int b = 0; b < count; ++b) {
    bots[b].x = ((b * 7) % w) * 4.0;
    bots[b].z = ((b * 5) % h) * 4.0;
    bots[b].yaw_deg = (b * 37) % 360 - 180.0;
    bots[b].last_moved = false;
  }
}

// One measured tick over all bots. Workload: patrol + a deterministic
// 60-tick reposition phase every 300 ticks (target last seen at a fixed
// synthetic point per bot). Returns the worst single-agent Step latency
// observed this tick, in microseconds.
static double RunTick(BenchBot* bots, int count, const NavGraph& g, int tick,
                      int w, int h) {
  double worst_us = 0.0;
  for (int b = 0; b < count; ++b) {
    const bool reposition_phase = (tick % 300) >= 200;
    NavAgentInput in;
    in.tick = tick;
    in.x = bots[b].x;
    in.y = 0.0;
    in.z = bots[b].z;
    in.yaw_deg = bots[b].yaw_deg;
    in.alive = true;
    in.movement_requested = bots[b].last_moved;
    in.has_target = reposition_phase;
    in.target_visible = false;
    in.target_x = ((b * 13 + 3) % w) * 4.0;
    in.target_y = 0.0;
    in.target_z = ((b * 11 + 5) % h) * 4.0;

    const std::chrono::steady_clock::time_point t0 =
        std::chrono::steady_clock::now();
    const NavCommand c = bots[b].agent.Step(g, in);
    const std::chrono::steady_clock::time_point t1 =
        std::chrono::steady_clock::now();
    const double us =
        std::chrono::duration<double, std::micro>(t1 - t0).count();
    if (us > worst_us) worst_us = us;

    bots[b].yaw_deg += c.yaw_delta_deg;
    bots[b].last_moved = (c.active && c.forward > 0.0);
    if (bots[b].last_moved) {
      const double rad = bots[b].yaw_deg * kNavPi / 180.0;
      bots[b].x += c.forward * 0.5 * -std::sin(rad);
      bots[b].z += c.forward * 0.5 * -std::cos(rad);
    }
  }
  return worst_us;
}

struct BenchResult {
  double total_us;      // wall time of the whole tick loop
  double worst_step_us; // worst single agent Step across all ticks
  long searches;        // A* searches performed (all bots)
  long expansions;      // node expansions performed (all bots)
};

static BenchResult RunBenchmark(const NavGraph& g, int count, int w, int h,
                                int ticks) {
  static BenchBot bots[16];
  for (int b = 0; b < count; ++b) {
    NavPersonality p;
    p.route_variance = 0.12f;
    bots[b].agent.Configure(p, static_cast<uint32_t>(b + 1));
  }
  PlaceBots(bots, count, w, h);

  BenchResult r;
  r.worst_step_us = 0.0;
  const std::chrono::steady_clock::time_point t0 =
      std::chrono::steady_clock::now();
  for (int t = 0; t < ticks; ++t) {
    const double worst = RunTick(bots, count, g, t, w, h);
    if (worst > r.worst_step_us) r.worst_step_us = worst;
  }
  const std::chrono::steady_clock::time_point t1 =
      std::chrono::steady_clock::now();
  r.total_us = std::chrono::duration<double, std::micro>(t1 - t0).count();
  r.searches = 0;
  r.expansions = 0;
  for (int b = 0; b < count; ++b) {
    r.searches += bots[b].agent.searches_total();
    r.expansions += bots[b].agent.expansions_total();
  }
  return r;
}

/* ------------------------------------------------------------------------ */
/* Worst-case search microbenchmark                                          */
/* ------------------------------------------------------------------------ */

static void BenchSearch(const NavGraph& g, const char* label, int budget,
                        int iterations) {
  NavAStar search;
  NavSearchConfig cfg;
  cfg.max_expand = budget;
  const int n = g.node_count();
  // Worst realistic pair: opposite corners of the grid.
  const int from = 0;
  const int to = n - 1;
  double sum_us = 0.0;
  double max_us = 0.0;
  int found = 0;
  long expansions = 0;
  for (int i = 0; i < iterations; ++i) {
    const std::chrono::steady_clock::time_point t0 =
        std::chrono::steady_clock::now();
    const NavPath p = search.Find(g, from, to, cfg);
    const std::chrono::steady_clock::time_point t1 =
        std::chrono::steady_clock::now();
    const double us =
        std::chrono::duration<double, std::micro>(t1 - t0).count();
    sum_us += us;
    if (us > max_us) max_us = us;
    if (p.status == NavSearchStatus::kFound) ++found;
    expansions += p.expanded;
  }
  std::printf("  %-28s budget=%-5d mean=%8.2f us  max=%8.2f us  "
              "found=%d/%d  expansions=%ld\n",
              label, budget, sum_us / iterations, max_us, found, iterations,
              expansions);
}

/* ------------------------------------------------------------------------ */

int main() {
  std::printf("=== navigation-lab benchmark (measured, steady_clock) ===\n");
  std::printf("host note: run `lscpu`/`nproc` alongside for context; "
              "%%core assumes a 20 Hz tick (50 ms) budget.\n\n");

  NavGraph g16, g32;
  maps::MakeGrid(g16, 16, 16);
  g16.ComputeDegrees();
  maps::MakeGrid(g32, 32, 32);
  g32.ComputeDegrees();
  std::printf("maps: grid16 nodes=%d  grid32 nodes=%d\n\n",
              g16.node_count(), g32.node_count());

  const int kTicks = 1200;  // 60 s at 20 Hz
  const int kBotCounts[4] = {1, 4, 8, 16};

  g_alloc_armed = true;  // any heap allocation below aborts the run

  std::printf("--- 1. steady-state tick cost (%d ticks, patrol+reposition "
              "mix) ---\n", kTicks);
  std::printf("  %-8s %5s %14s %14s %9s %11s %10s %10s\n",
              "map", "bots", "us/tick/agent", "us/tick(all)", "%core",
              "worst-step", "searches", "exp/search");
  for (int map = 0; map < 2; ++map) {
    const NavGraph& g = (map == 0) ? g16 : g32;
    const char* name = (map == 0) ? "grid16" : "grid32";
    const int w = (map == 0) ? 16 : 32, h = w;
    for (int i = 0; i < 4; ++i) {
      const int bots = kBotCounts[i];
      const BenchResult r = RunBenchmark(g, bots, w, h, kTicks);
      const double per_tick_all = r.total_us / kTicks;
      const double per_tick_agent = per_tick_all / bots;
      const double pct_core = per_tick_all / 50000.0 * 100.0;
      std::printf("  %-8s %5d %14.3f %14.3f %8.4f%% %10.2f %10ld %10.1f\n",
                  name, bots, per_tick_agent, per_tick_all, pct_core,
                  r.worst_step_us, r.searches,
                  r.searches ? static_cast<double>(r.expansions) / r.searches
                             : 0.0);
    }
  }

  std::printf("\n--- 2. worst-case single A* search (corner to corner) ---\n");
  BenchSearch(g16, "grid16 (256 nodes)", 256, 2000);
  BenchSearch(g16, "grid16 (256 nodes)", 1024, 2000);
  BenchSearch(g32, "grid32 (1024 nodes)", 256, 1000);
  BenchSearch(g32, "grid32 (1024 nodes)", 1024, 1000);

  g_alloc_armed = false;

  std::printf("\n--- 3. memory footprint ---\n");
  std::printf("  sizeof(NavGraph)  = %6zu bytes (static, per map)\n",
              sizeof(NavGraph));
  std::printf("  sizeof(NavAStar)  = %6zu bytes (static, per agent)\n",
              sizeof(NavAStar));
  std::printf("  sizeof(NavAgent)  = %6zu bytes (static, per agent)\n",
              sizeof(NavAgent));
  {
    // Bytes actually occupied at 1024 nodes / 4-edge average:
    const double nodes_bytes = 1024.0 * sizeof(NavNode);
    const double edges_bytes = 1024.0 * 4.0 * sizeof(NavEdge);
    std::printf("  used estimate @1024 nodes, 4 edges/node: %.1f KB nodes + "
                "%.1f KB edges\n", nodes_bytes / 1024.0, edges_bytes / 1024.0);
    std::printf("  16 agents + 1 map (worst case static): %.1f KB\n",
                (sizeof(NavAgent) * 16.0 + sizeof(NavGraph)) / 1024.0);
  }

  std::printf("\n--- 4. heap allocations during measured section ---\n");
  std::printf("  allocations: %ld (trap armed; any allocation aborts)\n",
              g_alloc_count);
  std::printf("BENCH OK\n");
  return 0;
}
