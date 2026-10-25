// SPDX-License-Identifier: GPL-2.0-only
// bench_item_utility.cpp - CPU benchmarks for the item decision layer.
//
// WHAT THIS MEASURES
//   Only the engine-free decision code: validation, <= 64 item evaluations,
//   goal bookkeeping and (optionally) the abstract navigation seam. It excludes
//   ray casts, entity lookups, item enumeration, action composition and
//   networking, because none of them exist in this layer.
//
// WHAT IT DOES NOT SAY
//   Nothing about GameMP.dll, a bot client process, Retail 1.07 or the Hetzner
//   fleet. The 20 Hz budget is 50 000 us per tick *per client process*; the
//   numbers below are three to four orders of magnitude below that and are
//   reported as a development gate, not as a runtime qualification.
//
// BUDGETS (development gates, deliberately loose enough for noisy CI machines)
//   sparse  6 items  <  6 us/tick
//   typical 12 items < 10 us/tick
//   dense   24 items < 15 us/tick
//   worst   64 items < 40 us/tick

#include <chrono>
#include <cmath>
#include <cstdio>

#include "item_planner.h"
#include "navigation_interface.h"

using namespace itemai;

namespace {

struct BenchWorld {
  ItemSnapshot items[kMaxItems];
  int count = 0;
  SelfState self;
  ThreatState threat;
  CombatContext combat;

  BenchWorld() {
    self.max_health = 100.0;
    self.max_armor = 100.0;
    self.health = 70.0;
    self.armor = 40.0;
    self.move_speed_mps = 10.0;
    GrantWeapon(self, 1);
    GrantWeapon(self, 2);
    GrantWeapon(self, 4);
    GrantWeapon(self, 6);
    SetAmmo(self, 2, 20);
    SetAmmo(self, 4, 10);
    SetAmmo(self, 6, 60);
    threat.visible_enemies = 1;
    threat.nearest_enemy_m = 14.0;
    threat.under_fire = true;
    threat.target_distance_m = 14.0;
    combat.engaged = true;
    combat.combat_priority = 0.35;
  }

  void Build(int count, unsigned seed) {
    uint32_t state = seed | 1u;
    auto rnd = [&state]() {
      state = state * 1664525u + 1013904223u;
      return static_cast<double>(state >> 8) / 16777216.0;
    };
    this->count = count;
    for (int i = 0; i < count; ++i) {
      ItemSnapshot& it = items[i];
      it = ItemSnapshot();
      it.id = i;
      it.kind = static_cast<ItemKind>(1 + static_cast<int>(rnd() * 6.0));
      it.pos = Vec3{rnd() * 30.0 - 15.0, rnd() * 2.0 - 1.0, -4.0 - rnd() * 30.0};
      it.value = 20.0 + rnd() * 80.0;
      it.amount = 10 + static_cast<int>(rnd() * 60.0);
      it.visible = rnd() > 0.25;
      it.staleness_s = rnd() * 3.0;
      it.reachable = rnd() > 0.05;
      it.weapon_index = (it.kind == ItemKind::kAmmo || it.kind == ItemKind::kWeapon)
                            ? 1 + static_cast<int>(rnd() * 13.0)
                            : 0;
    }
  }

  ItemWorld World(int tick) {
    combat.tick = tick;
    self.health = 45.0 + 40.0 * std::fabs(std::sin(0.01 * tick));
    ItemWorld w;
    w.items = items;
    w.count = count;
    w.self = self;
    w.threat = threat;
    w.combat = combat;
    return w;
  }
};

struct Result {
  double us_per_tick = 0.0;
  double us_per_eval = 0.0;
  double evals_per_tick = 0.0;
};

Result Run(const char* label, int item_count, int ticks, bool with_nav, double budget_us,
           int* failures) {
  BenchWorld world;
  world.Build(item_count, 0x9E3779B9u);
  ItemProfile profile;
  BuildItemProfile(3, 2, DeriveItemSeed(20261025u, 0, 3, 2), &profile);
  ItemPlanner planner;
  planner.Configure(profile);

  RecordingNavigationSink nav;
  nav.SetArriveAfterPolls(0);
  NavigationSink* sink = with_nav ? &nav : nullptr;

  // Warm-up (branch predictors, page faults) is not measured.
  for (int t = 0; t < 1000; ++t) planner.Step(world.World(t), sink);

  ItemPlanner measured;
  measured.Configure(profile);
  const auto t0 = std::chrono::steady_clock::now();
  for (int t = 0; t < ticks; ++t) {
    measured.Step(world.World(t), sink);
  }
  const auto t1 = std::chrono::steady_clock::now();

  const double total_us =
      std::chrono::duration_cast<std::chrono::nanoseconds>(t1 - t0).count() / 1000.0;
  Result r;
  r.us_per_tick = total_us / ticks;
  const double evals = static_cast<double>(measured.evaluations());
  r.us_per_eval = evals > 0.0 ? total_us / evals : 0.0;
  r.evals_per_tick = evals / ticks;

  const bool ok = r.us_per_tick <= budget_us;
  if (!ok) ++(*failures);
  std::printf("%-26s items=%2d nav=%d  %8.3f us/tick  %7.3f us/eval  %5.1f evals/tick  %s\n",
              label, item_count, with_nav ? 1 : 0, r.us_per_tick, r.us_per_eval,
              r.evals_per_tick, ok ? "OK" : "BUDGET MISS");
  return r;
}

}  // namespace

int main() {
  std::printf("== item utility layer: decision CPU benchmark ==\n");
  std::printf("(engine-free decision code only; 20 Hz tick budget = 50000 us/process)\n");

  int failures = 0;
  const int kTicks = 200000;

  const Result idle = Run("idle (no items)", 0, kTicks, false, 1.0, &failures);
  const Result sparse = Run("sparse", 6, kTicks, false, 6.0, &failures);
  const Result typical = Run("typical", 12, kTicks, false, 10.0, &failures);
  const Result dense = Run("dense", 24, kTicks, false, 15.0, &failures);
  const Result worst = Run("worst case", kMaxItems, kTicks, false, 40.0, &failures);
  const Result with_nav = Run("dense + nav seam", 24, kTicks, true, 18.0, &failures);

  std::printf("\nsummary\n");
  std::printf("  idle        %7.3f us/tick\n", idle.us_per_tick);
  std::printf("  sparse      %7.3f us/tick  (%.2f %% of the 20 Hz tick)\n", sparse.us_per_tick,
              100.0 * sparse.us_per_tick / 50000.0);
  std::printf("  typical     %7.3f us/tick\n", typical.us_per_tick);
  std::printf("  dense       %7.3f us/tick  (%.3f %% of the 20 Hz tick)\n",
              dense.us_per_tick, 100.0 * dense.us_per_tick / 50000.0);
  std::printf("  worst case  %7.3f us/tick, %.3f us per item evaluation\n",
              worst.us_per_tick, worst.us_per_eval);
  std::printf("  nav seam    %7.3f us/tick  (+%.3f us/tick over dense)\n",
              with_nav.us_per_tick, with_nav.us_per_tick - dense.us_per_tick);
  std::printf("  throughput  %.0f item evaluations/s at %d items\n",
              worst.us_per_eval > 0.0 ? 1e6 / worst.us_per_eval : 0.0, kMaxItems);

  // Sanity bounds against absurd results (e.g. accidental O(n^2) or I/O).
  if (!(typical.us_per_tick > 0.0) || !(worst.us_per_tick > typical.us_per_tick)) {
    std::printf("FAIL: implausible scaling between typical and worst case\n");
    ++failures;
  }
  if (with_nav.us_per_tick > 3.0 * dense.us_per_tick) {
    std::printf("FAIL: the navigation seam costs more than 2x the decision itself\n");
    ++failures;
  }

  std::printf("%s\n", failures ? "ITEM UTILITY BENCH FAIL" : "ITEM UTILITY BENCH PASS");
  return failures ? 1 : 0;
}
