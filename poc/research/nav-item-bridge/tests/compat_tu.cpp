// SPDX-License-Identifier: GPL-2.0-only
// compat_tu.cpp - C++11 / C++14 / C++17 translation-unit syntax & contract gate.

#include "arena_sim.h"
#include "bridge_arbitrator.h"
#include "nav_cost_cache.h"
#include "nav_goal_sink.h"
#include "nav_item_bridge.h"
#include "upstream_seams.h"

int main() {
  navbridge::ArenaSim sim;
  navbridge::BridgeProfileBundle bundle;
  if (!navbridge::BuildBridgeProfile(3, 1, 42u, 0, "CompatBot", &bundle)) {
    return 1;
  }
  sim.AddBot(bundle, 0.0, 0.0, 0.0);
  sim.StepTick();
  return sim.tick() == 1 ? 0 : 1;
}
