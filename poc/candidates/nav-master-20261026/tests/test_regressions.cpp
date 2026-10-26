#include <cmath>
#include <cstdio>
#include <cstring>
#include "nav_item_bridge.h"
#if !NAV_ITEM_BRIDGE_UPSTREAM_NAVLAB || !NAV_ITEM_BRIDGE_UPSTREAM_ITEMAI
#error Real PR54 and PR55 headers are required
#endif
namespace {
int failures = 0;
void Check(bool value, const char* msg) {
  if (!value) { ++failures; std::printf("FAIL %s\n", msg); }
}
void Prefix(bool constrained) {
  navlab::NavGraph g;
  navlab::maps::MakeCorridor(g, 180, 4.0);
  navbridge::ConstrainedNavSearch s;
  navbridge::TickExpansionBudget b(512);
  auto p = s.Search(g, 0, 179, 512, 0.0f, 7, nullptr, 0, constrained, &b);
  Check(p.count == navlab::kNavMaxPathNodes, "long route fills bounded prefix");
  Check(p.nodes[0] == 0, "long route starts at caller anchor, never remote suffix");
  Check(p.status == navlab::NavSearchStatus::kBudgetExhausted,
        "truncated found route reports continuation required");
  for (int i = 1; i < p.count; ++i)
    Check(p.nodes[i] == p.nodes[i - 1] + 1, "long route stays contiguous");
  Check(std::fabs(p.cost - (p.count - 1) * 4.0) < 0.01, "prefix cost matches returned prefix");
  Check(b.used() <= b.limit(), "long route respects total expansion cap");
}
void ZeroBudget(bool constrained) {
  navlab::NavGraph g;
  navlab::maps::MakeCorridor(g, 3);
  navbridge::ConstrainedNavSearch s;
  auto p = s.Search(g, 0, 2, 0, 0.0f, 7, nullptr, 0, constrained, nullptr);
  Check(p.expanded == 0, "zero search cap never expands without budget object");
  Check(p.status == navlab::NavSearchStatus::kBudgetExhausted, "zero search cap is pending");
}
void GoalReanchor() {
  navlab::NavGraph g;
  navlab::maps::MakeCorridor(g, 4, 8.0);
  navbridge::BridgeBudgetConfig cfg;
  cfg.route_variance = 0;
  navbridge::NavGraphSink sink;
  sink.Configure(cfg, navlab::NavPersonality(), 7);
  navbridge::ConstrainedNavSearch search;
  navbridge::LocalBlockedEdgeTable blocked;
  navbridge::TickExpansionBudget budget(512);
  navbridge::TrueItemTable table;
  navbridge::TrueItemEntry entry;
  entry.item_id = 4;
  entry.true_pos = navbridge::MakeVec3(24, 0, 0);
  table.Set(0, entry);
  sink.BindTickContext(&g, 1, 0, navbridge::MakeVec3(0, 0, 0), -90, &table, &search, &budget, &blocked);
  itemai::NavGoal goal;
  goal.goal_id = 4;
  goal.pos = entry.true_pos;
  goal.issued_tick = 0;
  goal.expires_tick = 300;
  Check(sink.Submit(goal) == itemai::NavStatus::kAccepted, "initial goal accepted");
  g.Clear();
  g.AddNode(0,0,0); g.AddNode(24,0,0); g.Link(0,1);
  budget.Reset(512);
  sink.BindTickContext(&g, 2, 1, navbridge::MakeVec3(0,0,0), -90, &table, &search, &budget, &blocked);
  itemai::NavFeedback feedback;
  Check(sink.Poll(4, &feedback) == itemai::NavStatus::kInProgress,
        "graph reindex reanchors active goal instead of stale node index");
}
void RecoveryClearsJump() {
  botcore::WorldView w;
  w.alive = w.deathmatch = true;
  botcore::BotCommand combat;
  combat.weapon = 4;
  itemai::GoalDecision item;
  item.has_goal = true;
  navbridge::GoalMoveCommand move;
  move.active = true; move.jump_hint = true;
  navlab::NavCommand patrol{};
  botcore::NavigationDecision recovery{};
  recovery.overrideInput = true;
  auto out = navbridge::ArbitrateCommands(w, true, combat, item, move, patrol, recovery, nullptr);
  Check(!out.jump_hint, "recovery does not retain jump from preempted route edge");
  Check(out.weapon == 4 && !out.fire, "recovery preserves combat weapon and inhibits fire");
}
}
int main(int argc, char** argv) {
  const char* select = argc > 1 ? argv[1] : "all";
  if (!std::strcmp(select,"all") || !std::strcmp(select,"prefix")) { Prefix(false); Prefix(true); }
  if (!std::strcmp(select,"all") || !std::strcmp(select,"zero")) { ZeroBudget(false); ZeroBudget(true); }
  if (!std::strcmp(select,"all") || !std::strcmp(select,"epoch")) GoalReanchor();
  if (!std::strcmp(select,"all") || !std::strcmp(select,"ownership")) RecoveryClearsJump();
  std::printf("C2 regressions: %d failures\n", failures);
  return failures ? 1 : 0;
}
