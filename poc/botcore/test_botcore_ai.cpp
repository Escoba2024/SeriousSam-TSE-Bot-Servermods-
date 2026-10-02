// Standalone reference checks for the Phase-2/4/5/6 decision logic in
// botcore_ai.h. Engine-free: these verify the pure decision semantics only;
// they do NOT execute the retail action composer, replicate network state or
// prove any runtime gate (see TESTPROTOKOLL-PHASE-2.md and following).
#include "botcore_ai.h"

#include <cmath>
#include <cstdio>

using namespace botcore;

static int g_failures = 0;

#define CHECK(cond, msg)                                              \
  do {                                                                \
    if (!(cond)) {                                                    \
      std::printf("FAIL: %s (line %d)\n", msg, __LINE__);             \
      ++g_failures;                                                   \
    }                                                                 \
  } while (0)

static void TestVariants() {
  // all four local slots must behave visibly differently and reproducibly
  for (int a = 0; a < 4; ++a) {
    const BotVariant va = VariantFor(a);
    CHECK(va.heading_offset_deg == VariantFor(a).heading_offset_deg,
          "variant is deterministic");
    CHECK(va.yaw_speed_scale > 0.0, "yaw scale must keep rotation alive");
    for (int b = a + 1; b < 4; ++b) {
      const BotVariant vb = VariantFor(b);
      CHECK(va.heading_offset_deg != vb.heading_offset_deg,
            "distinct heading offsets per local slot");
      CHECK(va.yaw_speed_scale != vb.yaw_speed_scale,
            "distinct yaw scales per local slot");
    }
  }
  CHECK(VariantFor(4).heading_offset_deg == VariantFor(0).heading_offset_deg,
        "variant table wraps at four local players");
}

static void TestTargetSelection() {
  const TargetInfo players[] = {
      {0, 0.0, 0.0, -10.0, 100.0, false},   // observer, 10 m ahead
      {1, 0.0, 0.0, 0.0, 100.0, true},      // ourselves (self_index 1)
      {2, 0.0, 0.0, -5.0, 0.0, false},      // dead - must be skipped
      {3, 3.0, 0.0, 0.0, 50.0, true},       // local sibling bot, 3 m
      {4, 0.0, 0.0, 30.0, 100.0, false},    // far remote player
  };
  const int n = 5;
  CHECK(SelectTarget(players, n, 1, 0, 0, 0, true) == 0,
        "nearest living non-local player wins (dead skipped)");
  CHECK(SelectTarget(players, n, 1, 0, 0, 0, false) == 3,
        "local siblings become targets only when explicitly allowed");
  const TargetInfo lonely[] = {{1, 0, 0, 0, 100.0, true}};
  CHECK(SelectTarget(lonely, 1, 1, 0, 0, 0, true) == -1,
        "no target when alone");
  const TargetInfo all_dead[] = {{0, 1, 0, 0, 0.0, false},
                                 {1, 0, 0, 0, 100.0, true}};
  CHECK(SelectTarget(all_dead, 2, 1, 0, 0, 0, true) == -1,
        "dead players are never targets");
}

static void TestWeaponSelection() {
  // the Phase-1 combat INI drives the Colt via 2L<<14 - keep that identity
  CHECK(WeaponSelectButtons(2) == (2u << 14), "Colt selection matches Phase-1 2L<<14");
  CHECK(kPlactSelectWeaponShift == 14, "PLACT_SELECT_WEAPON_SHIFT is 14");

  const uint32_t knife_colt = (1u << 0) | (1u << 1);       // weapons 1,2
  const uint32_t plus_dshotgun = knife_colt | (1u << 4);   // + weapon 5
  const uint32_t plus_minigun = plus_dshotgun | (1u << 6); // + weapon 7
  const uint32_t plus_sniper = plus_minigun | (1u << 12);  // + weapon 13

  CHECK(SelectWeapon(knife_colt, 5.0) == 2, "colt when nothing better close");
  CHECK(SelectWeapon(plus_dshotgun, 5.0) == 5, "double shotgun up close");
  CHECK(SelectWeapon(plus_dshotgun, 20.0) == 5, "mid range falls back to owned gun");
  CHECK(SelectWeapon(plus_minigun, 20.0) == 7, "minigun at mid range");
  CHECK(SelectWeapon(plus_minigun, 50.0) == 7, "minigun at long range without sniper");
  CHECK(SelectWeapon(plus_sniper, 50.0) == 13, "sniper at long range");
  CHECK(SelectWeapon(plus_sniper, 5.0) == 5, "sniper never preferred up close");
  CHECK(SelectWeapon(0u, 15.0) == 1, "knife is the guaranteed fallback");
  // explosives must never be selected (self-damage): give rockets only
  CHECK(SelectWeapon((1u << 0) | (1u << 7), 20.0) == 1,
        "rocket launcher is excluded from auto-selection");
}

static void TestWaypointGraph() {
  WaypointGraph g;
  // square 0-1-2-3 plus a dead-end 4 hanging off node 2
  CHECK(g.AddNode(0, 0, 0) == 0, "node 0");
  CHECK(g.AddNode(10, 0, 0) == 1, "node 1");
  CHECK(g.AddNode(10, 0, 10) == 2, "node 2");
  CHECK(g.AddNode(0, 0, 10) == 3, "node 3");
  CHECK(g.AddNode(20, 0, 10) == 4, "node 4");
  CHECK(g.Link(0, 1) && g.Link(1, 2) && g.Link(2, 3) && g.Link(3, 0) &&
            g.Link(2, 4),
        "edges insert");
  CHECK(!g.Link(0, 0), "self-loops rejected");
  CHECK(!g.Link(0, 99), "out-of-range edges rejected");

  CHECK(g.NearestNode(1.0, 0.0, 0.5) == 0, "nearest node resolves");
  CHECK(g.NearestNode(18.0, 0.0, 9.0) == 4, "nearest node far side");

  CHECK(g.NextHop(0, 0) == 0, "next hop to self is self");
  CHECK(g.NextHop(0, 1) == 1, "adjacent hop is the target");
  const int hop = g.NextHop(0, 2);
  CHECK(hop == 1 || hop == 3, "square offers two shortest first hops");
  CHECK(g.NextHop(0, 4) == hop || g.NextHop(0, 4) == 1 || g.NextHop(0, 4) == 3,
        "dead-end reached through the square");
  WaypointGraph disconnected;
  disconnected.AddNode(0, 0, 0);
  disconnected.AddNode(5, 0, 0);
  CHECK(disconnected.NextHop(0, 1) == -1, "unreachable returns -1");

  // file format parsing (as loaded by BotDriver from Scripts/)
  WaypointGraph parsed;
  CHECK(parsed.ParseLine("# comment"), "comment line ok");
  CHECK(parsed.ParseLine("// comment"), "slash comment ok");
  CHECK(parsed.ParseLine(""), "blank line ok");
  CHECK(parsed.ParseLine("node 1.5 0 -2.25"), "node line parses");
  CHECK(parsed.ParseLine("node 4 0 -2.25"), "second node parses");
  CHECK(parsed.ParseLine("edge 0 1"), "edge line parses");
  CHECK(!parsed.ParseLine("edge 0 7"), "edge to missing node fails loudly");
  CHECK(!parsed.ParseLine("garbage"), "malformed line fails loudly");
  CHECK(parsed.node_count() == 2, "parsed node count");
  double x, y, z;
  CHECK(parsed.NodePosition(0, &x, &y, &z) && x == 1.5 && y == 0.0 && z == -2.25,
        "parsed node position");
}

static void TestStuckDetector() {
  StuckDetector stuck(40, 1.0);
  // moving normally: never reports stuck
  bool reported = false;
  for (int t = 0; t < 200; ++t) {
    reported = stuck.Update(t * 0.5, 0.0, true) || reported;
  }
  CHECK(!reported, "a moving bot is never stuck");

  // pressing forward against a wall: reported after one full window
  stuck.Reset();
  int first_report = -1;
  for (int t = 0; t < 200; ++t) {
    if (stuck.Update(5.0, 5.0, true)) {
      first_report = t;
      break;
    }
  }
  CHECK(first_report == 39, "stuck reported after exactly one 40-tick window");

  // standing still intentionally (aim pause): not stuck
  stuck.Reset();
  reported = false;
  for (int t = 0; t < 200; ++t) {
    reported = stuck.Update(5.0, 5.0, false) || reported;
  }
  CHECK(!reported, "an intentional stop is not stuck");
}

static void TestPopulationController() {
  // 16-slot fragmatch, 12 desired players, 2 slots always free for humans
  PopulationInput in{16, 0, 0, 12, 2};
  CHECK(DesiredBots(in) == 12, "empty server fills to target");
  CHECK(PopulationStep(in) == PopulationAction::kStartBot, "start first bot");

  in.bots = 12;
  CHECK(PopulationStep(in) == PopulationAction::kNone, "target reached");

  in.humans = 3;  // humans join -> bots make room down to target
  CHECK(DesiredBots(in) == 9, "humans count against the target");
  CHECK(PopulationStep(in) == PopulationAction::kStopBot, "bots yield to humans");

  // humans above target: every remaining bot leaves
  in.humans = 13;
  in.bots = 3;
  CHECK(DesiredBots(in) == 0, "humans above target leave no room for bots");
  CHECK(PopulationStep(in) == PopulationAction::kStopBot, "shrink to zero");
  in.bots = 0;
  CHECK(PopulationStep(in) == PopulationAction::kNone, "zero bots is stable");

  // capacity (not target) is the binding constraint here:
  // 8 humans, reserve 2 -> capacity 6, target wants 4 -> 4 bots
  PopulationInput mid{16, 8, 2, 12, 2};
  CHECK(DesiredBots(mid) == 4, "target minus humans below capacity");
  CHECK(PopulationStep(mid) == PopulationAction::kStartBot, "fill toward target");

  // full of humans: no bots, never negative
  in.humans = 16;
  in.bots = 0;
  CHECK(DesiredBots(in) == 0, "full server wants zero bots");
  CHECK(PopulationStep(in) == PopulationAction::kNone, "nothing to do when full");

  // target above capacity is clamped
  PopulationInput greedy{16, 0, 0, 99, 2};
  CHECK(DesiredBots(greedy) == 14, "target clamped to capacity minus reserve");

  // never start into the reserved slots even if below target
  PopulationInput tight{16, 14, 0, 16, 2};
  CHECK(DesiredBots(tight) == 0, "no bot may take a reserved slot");
  CHECK(PopulationStep(tight) == PopulationAction::kNone, "reserve blocks start");
}

static void TestPresenceSchedule() {
  PresenceSchedule a(1234, 0);
  PresenceSchedule a2(1234, 0);
  PresenceSchedule b(1234, 1);

  // deterministic per seed+index, different across bot indices
  const int ja = a.JoinDelaySeconds();
  CHECK(ja == a2.JoinDelaySeconds(), "join delay reproducible for same seed");
  bool diverged = false;
  PresenceSchedule a3(1234, 0), b3(1234, 1);
  for (int i = 0; i < 8 && !diverged; ++i) {
    diverged = a3.JoinDelaySeconds() != b3.JoinDelaySeconds();
  }
  CHECK(diverged, "bot indices produce different presence patterns");

  // bounds
  PresenceSchedule s(42, 2);
  for (int i = 0; i < 1000; ++i) {
    const int join = s.JoinDelaySeconds(5, 90);
    CHECK(join >= 5 && join <= 90, "join delay within bounds");
    const int leave = s.LeaveDelaySeconds(2, 30);
    CHECK(leave >= 2 && leave <= 30, "leave delay within bounds");
    const int chat = s.NextChatDelayTicks(120.0);  // 2 min base period
    CHECK(chat >= 1200 && chat <= 3600, "chat cadence jitters +/-50%");
  }
  CHECK(s.NextChatDelayTicks(0.0) == -1, "chat period <=0 disables chat");

  // chat line picker: in range, never the same line twice in a row
  PresenceSchedule c(7, 3);
  int prev = -1;
  for (int i = 0; i < 500; ++i) {
    const int line = c.NextChatLine(6);
    CHECK(line >= 0 && line < 6, "chat line within file bounds");
    CHECK(line != prev, "no immediate chat line repetition");
    prev = line;
  }
  CHECK(c.NextChatLine(0) == -1, "empty chat file yields no line");
  CHECK(c.NextChatLine(1) == 0, "single-line file always line 0");

  // variance check: cadence must not be constant (anti-pattern requirement)
  PresenceSchedule v(99, 1);
  const int first = v.NextChatDelayTicks(60.0);
  bool varies = false;
  for (int i = 0; i < 16 && !varies; ++i) {
    varies = v.NextChatDelayTicks(60.0) != first;
  }
  CHECK(varies, "chat cadence is jittered, not constant");
}

int main() {
  TestVariants();
  TestTargetSelection();
  TestWeaponSelection();
  TestWaypointGraph();
  TestStuckDetector();
  TestPopulationController();
  TestPresenceSchedule();

  std::printf(g_failures == 0 ? "ALL AI CHECKS PASSED\n" : "%d AI CHECKS FAILED\n",
              g_failures);
  return g_failures == 0 ? 0 : 1;
}
