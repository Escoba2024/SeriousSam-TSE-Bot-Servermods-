// SPDX-License-Identifier: GPL-2.0-only
// test_item_utility.cpp - offline acceptance tests for the item decision layer.
//
// Every check here is reproducible from fixed inputs and runs without Retail,
// SDK, Windows, a network or an engine. Nothing in this file proves runtime
// behaviour; it proves decision semantics.
//
// Covered scenarios (task list):
//   1  low health                     8  abort of a running item search
//   2  full health                    9  goal switch
//   3  missing ammunition            10  cooldowns (global, per item, blacklist)
//   4  weak weapons                  11  skill levels
//   5  competing items               12  personalities
//   6  enemy in immediate proximity  13  determinism
//   7  (see 6: break-off)            14  CPU budget
//   plus: fail-closed validation, scoring invariants, profile separation and
//   the navigation seam contract.

#include <chrono>
#include <cmath>
#include <cstdio>
#include <cstring>

#include "item_planner.h"
#include "item_profile.h"
#include "item_scoring.h"
#include "item_snapshot.h"
#include "navigation_interface.h"

using namespace itemai;

static int g_failures = 0;
static int g_checks = 0;

#define CHECK(cond, msg)                                  \
  do {                                                    \
    ++g_checks;                                           \
    if (!(cond)) {                                        \
      std::printf("FAIL: %s (line %d)\n", msg, __LINE__);  \
      ++g_failures;                                       \
    }                                                     \
  } while (0)

#define CHECK_NEAR(a, b, tol, msg)                                       \
  do {                                                                   \
    ++g_checks;                                                          \
    const double va = (a), vb = (b);                                     \
    if (!(std::fabs(va - vb) <= (tol))) {                                \
      std::printf("FAIL: %s (line %d) got %.6f expected %.6f\n", msg,     \
                  __LINE__, va, vb);                                     \
      ++g_failures;                                                      \
    }                                                                    \
  } while (0)

static bool plain_ok(const ItemWorld& w) {
  return ValidateWorld(w) == ValidationError::kOk;
}

/* ------------------------------------------------------------------------ */
/* Fixtures                                                                  */
/* ------------------------------------------------------------------------ */

constexpr int kFixtureItems = 24;

struct Scenario {
  ItemSnapshot items[kFixtureItems];
  int count = 0;
  SelfState self;
  ThreatState threat;
  CombatContext combat;

  Scenario() {
    self.eye = Vec3{0.0, 0.0, 0.0};
    self.health = 100.0;
    self.max_health = 100.0;
    self.armor = 100.0;  // full armor by default: armor items are irrelevant
    self.max_armor = 100.0;
    self.owned_weapons = 0;
    GrantWeapon(self, 1);  // knife
    GrantWeapon(self, 2);  // colt
    GrantWeapon(self, 4);  // shotgun
    SetAmmo(self, 2, 50);
    SetAmmo(self, 4, 30);
    self.move_speed_mps = 10.0;
  }

  int Add(ItemKind kind, double x, double z, double value = 0.0, int weapon = 0,
          int amount = 0) {
    if (count >= kFixtureItems) return -1;
    ItemSnapshot& it = items[count];
    it = ItemSnapshot();
    it.id = 100 + count;
    it.kind = kind;
    it.pos = Vec3{x, 0.0, z};
    it.value = value;
    it.weapon_index = weapon;
    it.amount = amount;
    it.visible = true;
    it.reachable = true;
    it.respawn_s = 0.0;
    it.staleness_s = 0.0;
    return count++;
  }

  ItemWorld World() const {
    ItemWorld w;
    w.items = items;
    w.count = count;
    w.self = self;
    w.threat = threat;
    w.combat = combat;
    return w;
  }
};

static ItemProfile Profile(int tier, int persona) {
  ItemProfile p;
  BuildItemProfile(tier, persona, DeriveItemSeed(20261025u, 0, tier, persona), &p);
  return p;
}


/* ------------------------------------------------------------------------ */
/* 1. Low health                                                             */
/* ------------------------------------------------------------------------ */

static void TestLowHealthPrioritisesHealth() {
  Scenario s;
  s.self.health = 20.0;
  const int health = s.Add(ItemKind::kHealth, 0.0, -10.0, 50.0);
  s.Add(ItemKind::kAmmo, 0.0, -3.0, 0.0, 2, 25);          // very close ammo
  s.Add(ItemKind::kStrategic, 3.0, -2.0, 0.5);            // very close marker

  ItemPlanner planner;
  planner.Configure(Profile(3, 2));
  const GoalDecision d = planner.Step(s.World());

  CHECK(d.action == ItemAction::kSelect, "low health selects a goal");
  CHECK(d.has_goal, "low health commits a goal");
  CHECK(d.goal_kind == ItemKind::kHealth, "low health selects the health item");
  CHECK(d.goal_id == s.items[health].id, "low health picks the medkit id");
  CHECK(d.utility > 0.20, "low health utility is substantial");
  CHECK(d.suppress_combat, "critical health asks the combat layer to yield");

  // The scoring terms must explain the decision, not just produce it.
  int n = 0;
  const ItemEvaluation* ev = planner.last_evaluations(&n);
  CHECK(n == 3, "all three candidates were evaluated");
  CHECK(ev[0].terms.need > 0.6, "health need is high at 20 hp");
  CHECK(ev[0].terms.capability > 0.5, "a 50 hp medkit covers most of the deficit");
  CHECK(ev[0].terms.utility > ev[1].terms.utility, "health beats close ammo");
}

static void TestHealthNeedIsConvexAndBounded() {
  ScoreContext c;
  c.health_frac = 1.0;
  CHECK(HealthNeed(c) == 0.0, "full health has exactly zero health need");
  c.health_frac = kFullHealthFrac;
  CHECK(HealthNeed(c) == 0.0, "98 % health still has zero need");
  c.health_frac = 0.95;
  const double top = HealthNeed(c);
  c.health_frac = 0.90;
  const double nine = HealthNeed(c);
  c.health_frac = 0.50;
  const double half = HealthNeed(c);
  c.health_frac = 0.10;
  const double low = HealthNeed(c);
  CHECK(top < nine && nine < half && half < low, "health need grows monotonically");
  // Convexity: the last 10 % must be worth more than an earlier 10 %.
  CHECK((half - nine) < (low - half), "health need is convex in the deficit");
  CHECK(low <= 1.0, "health need stays bounded");
}

/* ------------------------------------------------------------------------ */
/* 2. Full health                                                            */
/* ------------------------------------------------------------------------ */

static void TestFullHealthDoesNotChaseHealth() {
  Scenario s;
  s.self.health = 100.0;
  s.Add(ItemKind::kHealth, 0.0, -3.0, 100.0);

  ItemPlanner planner;
  planner.Configure(Profile(5, 1));  // expert survivor: maximal appetite
  const GoalDecision d = planner.Step(s.World());

  CHECK(!d.has_goal, "full health does not commit to a health item");
  CHECK(d.action == ItemAction::kNone, "full health produces no action");
  CHECK(d.utility == 0.0, "full health yields zero utility for health");

  int n = 0;
  const ItemEvaluation* ev = planner.last_evaluations(&n);
  CHECK(n == 1, "the health item was evaluated");
  CHECK(ev[0].reject == ItemReason::kNeedSatisfied, "reject reason is need-satisfied");
  CHECK(!ev[0].eligible, "health item is ineligible at full health");

  // 95 % health: still not worth a trip, but for a different reason (below the
  // utility floor instead of "no need at all").
  Scenario s2;
  s2.self.health = 95.0;
  s2.Add(ItemKind::kHealth, 0.0, -3.0, 100.0);
  ItemPlanner p2;
  p2.Configure(Profile(5, 1));
  const GoalDecision d2 = p2.Step(s2.World());
  CHECK(!d2.has_goal, "95 % health does not chase a medkit either");
}

static void TestTinyHealthItemIsNotEssential() {
  // A +1 medkit at 40 hp covers 1 of 60 missing points: not worth a detour.
  Scenario s;
  s.self.health = 40.0;
  s.Add(ItemKind::kHealth, 0.0, -4.0, 1.0);
  ItemPlanner planner;
  planner.Configure(Profile(3, 1));
  const GoalDecision d = planner.Step(s.World());
  CHECK(!d.has_goal, "a +1 medkit is not worth a detour at 40 hp");

  int n = 0;
  const ItemEvaluation* ev = planner.last_evaluations(&n);
  CHECK(ev[0].terms.capability < 0.05, "capability of a +1 medkit is tiny");

  // A *substantial* medkit at 8 hp is a different matter: capability is what
  // separates "a medkit exists" from "this medkit helps".
  Scenario s2;
  s2.self.health = 8.0;
  s2.Add(ItemKind::kHealth, 0.0, -4.0, 25.0);
  ItemPlanner p2;
  p2.Configure(Profile(3, 1));
  const GoalDecision d2 = p2.Step(s2.World());
  CHECK(d2.has_goal && d2.goal_kind == ItemKind::kHealth,
        "a 25 hp medkit is taken at 8 hp");
  CHECK(d2.suppress_combat, "and it is treated as survival");
}

/* ------------------------------------------------------------------------ */
/* 3. Missing ammunition                                                     */
/* ------------------------------------------------------------------------ */

static void TestMissingAmmoSelectsAmmo() {
  Scenario s;
  s.self.health = 100.0;
  SetAmmo(s.self, 2, 0);  // colt empty
  s.Add(ItemKind::kAmmo, 0.0, -8.0, 0.0, 2, 25);
  s.Add(ItemKind::kAmmo, 0.0, -8.0, 0.0, 4, 30);  // shotgun already full
  s.Add(ItemKind::kHealth, 0.0, -8.0, 50.0);      // not needed

  ItemPlanner planner;
  planner.Configure(Profile(3, 2));
  const GoalDecision d = planner.Step(s.World());

  CHECK(d.has_goal, "empty colt triggers an ammo search");
  CHECK(d.goal_kind == ItemKind::kAmmo, "ammo item selected");
  CHECK(d.goal_weapon_index == 2, "ammo for the empty colt selected");
  CHECK(!d.suppress_combat, "an ammo trip is not a survival trip");

  int n = 0;
  const ItemEvaluation* ev = planner.last_evaluations(&n);
  CHECK(ev[0].terms.need > 0.5, "empty primary weapon has high ammo need");
  CHECK(ev[1].terms.need == 0.0, "full shotgun has no ammo need");
  CHECK(!ev[1].eligible, "full ammo is ineligible");
  CHECK(ev[2].terms.need == 0.0, "full health has no need at all");
}

static void TestAmmoForUnownedWeaponIsWorthless() {
  Scenario s;
  s.self.owned_weapons = 0;
  GrantWeapon(s.self, 1);
  GrantWeapon(s.self, 2);
  SetAmmo(s.self, 2, 50);
  s.Add(ItemKind::kAmmo, 0.0, -2.0, 0.0, 8, 5);  // rocket ammo, no rocket

  ItemPlanner planner;
  planner.Configure(Profile(3, 2));
  const GoalDecision d = planner.Step(s.World());
  CHECK(!d.has_goal, "ammo for a weapon the bot does not own is ignored");

  int n = 0;
  const ItemEvaluation* ev = planner.last_evaluations(&n);
  CHECK(ev[0].terms.need == 0.0, "unusable ammo has zero need");
}

static void TestAmmoStarvationIsReportedWhenNothingHelps() {
  // Starved, but the world offers no ammo and no weapon: the item layer must
  // say so instead of pretending that walking somewhere would help.
  Scenario s;
  s.self.owned_weapons = 0;
  GrantWeapon(s.self, 1);
  GrantWeapon(s.self, 7);  // minigun, empty
  SetAmmo(s.self, 7, 0);
  s.self.health = 80.0;
  s.Add(ItemKind::kHealth, 0.0, -20.0, 50.0);  // irrelevant, health is fine
  ItemPlanner planner;
  planner.Configure(Profile(3, 2));
  const GoalDecision d = planner.Step(s.World());
  CHECK(!d.has_goal, "no goal is invented");
  CHECK(d.reason == ItemReason::kAmmoStarved,
        "starvation without a resupply candidate is reported as ammo-starved");
}

static void TestUrgentGoalPriorityReachesNavigation() {
  // A starved bot that *can* be resupplied submits an urgent (not critical)
  // navigation goal, so the navigation layer can prioritise it accordingly.
  Scenario s;
  s.self.owned_weapons = 0;
  GrantWeapon(s.self, 1);
  GrantWeapon(s.self, 7);
  SetAmmo(s.self, 7, 0);
  s.self.health = 90.0;
  s.Add(ItemKind::kAmmo, 0.0, -7.0, 0.0, 7, 60);
  RecordingNavigationSink nav;
  ItemPlanner planner;
  planner.Configure(Profile(3, 2));
  const GoalDecision d = planner.Step(s.World(), &nav);
  CHECK(d.has_goal, "the resupply trip is committed");
  CHECK(nav.last_goal().priority == NavPriority::kUrgent,
        "a resupply trip is urgent, not survival-critical");
  CHECK(nav.last_goal().yield_to_combat, "but it still yields to combat");
}

static void TestAmmoStarvationIsAnEmergency() {
  // Bot owns a good ranged weapon but has no ammo for anything.
  Scenario s;
  s.self.owned_weapons = 0;
  GrantWeapon(s.self, 1);
  GrantWeapon(s.self, 7);  // minigun, no ammo
  SetAmmo(s.self, 7, 0);
  s.self.health = 100.0;

  const ScoreContext base = MakeContext(Profile(3, 2), s.World(), 0);
  CHECK(base.self.ammunition_starved, "no loaded ranged weapon = starved");
  CHECK_NEAR(base.ammo_pressure, 1.0, 1e-9, "starvation maximises ammo pressure");

  s.Add(ItemKind::kAmmo, 0.0, -6.0, 0.0, 7, 50);
  ItemPlanner planner;
  planner.Configure(Profile(3, 2));
  const GoalDecision d = planner.Step(s.World());
  CHECK(d.has_goal && d.goal_kind == ItemKind::kAmmo, "starved bot seeks ammo");
  CHECK(d.utility > 0.3, "starvation produces a strong utility");
}

/* ------------------------------------------------------------------------ */
/* 4. Weak weapons                                                           */
/* ------------------------------------------------------------------------ */

static void TestWeakWeaponSeeksUpgrade() {
  Scenario s;
  s.self.owned_weapons = 0;
  GrantWeapon(s.self, 1);  // knife only
  s.Add(ItemKind::kWeapon, 0.0, -12.0, 0.0, 4);  // shotgun

  ItemPlanner planner;
  planner.Configure(Profile(3, 4));  // marksman
  const GoalDecision d = planner.Step(s.World());
  CHECK(d.has_goal, "knife-only bot seeks a weapon");
  CHECK(d.goal_kind == ItemKind::kWeapon, "weapon item selected");
  CHECK(d.goal_weapon_index == 4, "shotgun is the target");
  CHECK(d.utility > 0.25, "weapon upgrade utility is substantial");
}

static void TestStrongLoadoutIgnoresWeakerWeapon() {
  Scenario s;
  s.self.owned_weapons = 0;
  GrantWeapon(s.self, 1);
  GrantWeapon(s.self, 12);  // laser
  SetAmmo(s.self, 12, 50);
  s.self.health = 100.0;
  s.Add(ItemKind::kWeapon, 0.0, -10.0, 0.0, 4);  // shotgun (worse than laser)

  ItemPlanner planner;
  planner.Configure(Profile(3, 4));
  const GoalDecision d = planner.Step(s.World());
  CHECK(!d.has_goal, "a weaker weapon is not worth a trip");

  int n = 0;
  const ItemEvaluation* ev = planner.last_evaluations(&n);
  CHECK(!ev[0].eligible, "weaker weapon is ineligible");
  CHECK(ev[0].terms.need < 0.20, "capability gain of a downgrade is small");
}

static void TestDuplicateWeaponIsAmmoNotUpgrade() {
  Scenario s;
  s.self.owned_weapons = 0;
  GrantWeapon(s.self, 1);
  GrantWeapon(s.self, 4);
  SetAmmo(s.self, 4, 0);  // owns shotgun but no shells
  s.Add(ItemKind::kWeapon, 0.0, -6.0, 0.0, 4);  // second shotgun = shells

  ItemPlanner planner;
  planner.Configure(Profile(3, 2));
  const GoalDecision d = planner.Step(s.World());
  CHECK(d.has_goal, "a duplicate weapon is still worth collecting for ammo");
  CHECK(d.goal_kind == ItemKind::kWeapon, "duplicate weapon picked as weapon item");
  CHECK(d.utility < 0.5, "but its utility stays below a real upgrade");
}

/* ------------------------------------------------------------------------ */
/* 5. Competing items                                                        */
/* ------------------------------------------------------------------------ */

static void TestCompetingItemsChooseHighestUtility() {
  Scenario s;
  s.self.health = 55.0;
  s.self.armor = 20.0;
  SetAmmo(s.self, 2, 30);  // no ammo emergency: this test is about preferences
  s.Add(ItemKind::kHealth, 0.0, -9.0, 50.0);
  s.Add(ItemKind::kArmor, 4.0, -16.0, 50.0);
  s.Add(ItemKind::kAmmo, -3.0, -5.0, 0.0, 2, 10);
  s.Add(ItemKind::kPowerup, 6.0, -12.0, 0.7);

  ItemPlanner planner;
  planner.Configure(Profile(3, 2));
  const GoalDecision d = planner.Step(s.World());
  CHECK(d.has_goal, "one of the competing items is selected");

  int n = 0;
  const ItemEvaluation* ev = planner.last_evaluations(&n);
  CHECK(n == 4, "all four candidates evaluated");

  double best_eligible = 0.0;
  int best_index = -1;
  int eligible_count = 0;
  for (int i = 0; i < n; ++i) {
    if (!ev[i].eligible) continue;
    ++eligible_count;
    if (ev[i].terms.utility > best_eligible) {
      best_eligible = ev[i].terms.utility;
      best_index = i;
    }
  }
  CHECK(eligible_count >= 2, "several items remain eligible");
  CHECK(best_index >= 0, "an eligible best item exists");
  CHECK(d.goal_id == ev[best_index].item_id, "planner picked the max-utility item");
  CHECK(d.candidates == 4, "candidate count is reported");

  // A different personality must be able to reach a different conclusion
  // without any change to the world.
  ItemPlanner survivor;
  survivor.Configure(Profile(3, 1));
  const GoalDecision ds = survivor.Step(s.World());
  CHECK(ds.has_goal, "survivor also commits to something");
  CHECK(ds.goal_id == ev[0].item_id, "survivor prefers the medkit");
}

/* ------------------------------------------------------------------------ */
/* 6. Enemy in immediate proximity / break-off                                */
/* ------------------------------------------------------------------------ */

static void TestEnemyInProximityAbortsSearch() {
  Scenario s;
  s.self.health = 60.0;
  s.self.armor = 100.0;
  const int health_id = s.Add(ItemKind::kHealth, 0.0, -12.0, 50.0);

  ItemPlanner planner;
  planner.Configure(Profile(3, 3));
  GoalDecision d = planner.Step(s.World());
  CHECK(d.has_goal && d.goal_id == s.items[health_id].id,
        "trip to the medkit starts unopposed");

  // Enemy appears 6 m away while health is below the abort fraction.
  s.threat.visible_enemies = 1;
  s.threat.nearest_enemy_m = 6.0;
  s.threat.under_fire = true;
  s.combat.engaged = true;
  s.combat.combat_priority = 0.4;
  s.self.health = 40.0;
  d = planner.Step(s.World());
  CHECK(d.action == ItemAction::kAbort, "close enemy aborts the item search");
  CHECK(d.reason == ItemReason::kThreatOverride, "abort reason is threat-override");
  CHECK(!planner.has_goal(), "goal is cleared after the abort");
  CHECK(planner.aborts() == 1, "abort counter incremented");
}

static void TestCloseFinishIsNotAborted() {
  Scenario s;
  s.self.health = 40.0;
  const int idx = s.Add(ItemKind::kHealth, 0.0, -2.0, 50.0);
  ItemPlanner planner;
  planner.Configure(Profile(3, 3));
  GoalDecision d = planner.Step(s.World());
  CHECK(d.has_goal && d.goal_id == s.items[idx].id,
        "medkit two metres away is taken");

  s.threat.visible_enemies = 1;
  s.threat.nearest_enemy_m = 6.0;
  s.threat.under_fire = true;
  d = planner.Step(s.World());
  CHECK(d.action != ItemAction::kAbort,
        "finishing a pickup within the close radius is not aborted");
  CHECK(planner.has_goal(), "the goal survives");
}

static void TestCombatLockSuppressesNonEssentialTrips() {
  Scenario s;
  s.self.health = 100.0;
  s.self.armor = 20.0;
  s.Add(ItemKind::kArmor, 0.0, -6.0, 50.0);
  s.combat.engaged = true;
  s.combat.combat_priority = 0.95;
  s.threat.visible_enemies = 1;
  s.threat.nearest_enemy_m = 12.0;

  ItemPlanner planner;
  planner.Configure(Profile(3, 0));  // aggressor: lock threshold ~0.70
  const GoalDecision d = planner.Step(s.World());
  CHECK(!d.has_goal, "a committed fight blocks an armor detour");
  CHECK(d.reason == ItemReason::kCombatLock, "reason is combat-lock");
  CHECK(planner.combat_lock_blocks() == 1, "combat-lock counter incremented");

  // The same fight must not block a survival pickup.
  Scenario s2;
  s2.self.health = 20.0;
  s2.self.armor = 20.0;
  s2.combat.engaged = true;
  s2.combat.combat_priority = 0.95;
  s2.threat.visible_enemies = 1;
  s2.threat.nearest_enemy_m = 25.0;  // outside the abort radius
  s2.Add(ItemKind::kHealth, 0.0, -6.0, 50.0);
  ItemPlanner p2;
  p2.Configure(Profile(3, 0));
  const GoalDecision d2 = p2.Step(s2.World());
  CHECK(d2.has_goal && d2.goal_kind == ItemKind::kHealth,
        "a dying bot may disengage for a medkit");
  CHECK(d2.suppress_combat, "and it asks combat to yield");
}

/* ------------------------------------------------------------------------ */
/* 7. Abort via damage, timeout and navigation                              */
/* ------------------------------------------------------------------------ */

static void TestDamageAbortAndGlobalCooldown() {
  Scenario s;
  s.self.health = 70.0;
  s.self.armor = 100.0;
  const int medkit = s.Add(ItemKind::kHealth, 0.0, -14.0, 50.0);

  ItemPlanner planner;
  planner.Configure(Profile(3, 1));
  GoalDecision d = planner.Step(s.World());
  CHECK(d.has_goal && d.goal_id == s.items[medkit].id, "goal committed at 70 hp");

  // 30 points of damage inside the window: abort (threshold ~0.27 of max).
  s.self.health = 40.0;
  s.combat.tick = 4;
  d = planner.Step(s.World());
  CHECK(d.action == ItemAction::kAbort, "heavy damage aborts the search");
  CHECK(d.reason == ItemReason::kDamageAbort, "reason is damage-abort");
  CHECK(planner.aborts() == 1, "abort counter incremented");

  // Immediately afterwards the global search cooldown applies.
  s.combat.tick = 6;
  d = planner.Step(s.World());
  CHECK(!d.has_goal, "search stays paused after a damage abort");
  CHECK(d.reason == ItemReason::kCooldown, "reason is cooldown");
  CHECK(planner.cooldown_blocks() >= 1, "cooldown counter incremented");

  // After both cooldowns the same item may be chosen again.
  s.combat.tick = 90;
  d = planner.Step(s.World());
  CHECK(d.has_goal && d.goal_id == s.items[medkit].id,
        "search resumes after the cooldown");
  CHECK(planner.selections() == 2, "the resumed trip is a new selection");
}

static void TestPerItemCooldownBlocksOnlyThatItem() {
  // Empty primary weapon beats a medkit at 70 hp, so the abort hits the ammo
  // trip and the medkit is the fallback.
  Scenario s;
  s.self.health = 70.0;
  const int medkit = s.Add(ItemKind::kHealth, 0.0, -14.0, 50.0);
  const int ammo = s.Add(ItemKind::kAmmo, 0.0, -6.0, 0.0, 2, 25);
  SetAmmo(s.self, 2, 0);

  ItemProfile p = Profile(3, 1);
  // Deliberately short global cooldown, long per-item cooldown: this isolates
  // the per-item timer from the global one.
  p.tuning.search_cooldown_s = 0.20;
  p.tuning.abort_cooldown_s = 3.00;
  CHECK(ValidateProfile(p) == ProfileError::kOk, "tuned profile still validates");
  ItemPlanner planner;
  planner.Configure(p);

  GoalDecision d = planner.Step(s.World());
  CHECK(d.has_goal && d.goal_id == s.items[ammo].id, "ammo trip starts first");

  s.self.health = 40.0;
  s.combat.tick = 4;
  d = planner.Step(s.World());
  CHECK(d.reason == ItemReason::kDamageAbort, "damage abort fires");

  s.combat.tick = 12;  // past the 0.2 s global cooldown (4 ticks)
  d = planner.Step(s.World());
  CHECK(d.has_goal, "another item is available after the global cooldown");
  CHECK(d.goal_id == s.items[medkit].id, "the medkit replaces the cooling ammo trip");

  // Drop the medkit: the goal disappears, and the ammo trip may be chosen
  // again once its 3 s per-item cooldown expired at tick 64.
  s.items[0] = s.items[ammo];
  s.count = 1;
  s.combat.tick = 82;
  d = planner.Step(s.World());
  CHECK(d.reason == ItemReason::kItemGone, "the vanished medkit releases the goal");
  d = planner.Step(s.World());
  CHECK(d.has_goal && d.goal_id == s.items[0].id,
        "the aborted item is selectable again after its cooldown");
}

static void TestTimeoutAbortsLongSearch() {
  Scenario s;
  s.self.health = 60.0;
  s.Add(ItemKind::kHealth, 0.0, -10.0, 100.0);

  ItemProfile p = Profile(3, 1);
  p.tuning.max_search_time_s = 2.0;  // 40 ticks
  ItemPlanner planner;
  planner.Configure(p);

  GoalDecision d = planner.Step(s.World());
  CHECK(d.has_goal, "an affordable medkit starts a trip");

  s.combat.tick = 30;
  d = planner.Step(s.World());
  CHECK(d.action == ItemAction::kKeep, "trip continues inside the time budget");

  s.combat.tick = 60;
  d = planner.Step(s.World());
  CHECK(d.reason == ItemReason::kTimeout, "trip times out");
  CHECK(planner.timeouts() == 1, "timeout counter incremented");
}

/* ------------------------------------------------------------------------ */
/* 8. Goal switch and hysteresis                                             */
/* ------------------------------------------------------------------------ */

static void TestGoalSwitchRespectsDwellAndMargin() {
  Scenario s;
  s.self.health = 20.0;
  s.self.armor = 100.0;
  SetAmmo(s.self, 2, 0);
  const int ammo = s.Add(ItemKind::kAmmo, 0.0, -12.0, 0.0, 2, 25);
  const int health = s.Add(ItemKind::kHealth, 0.0, -2.5, 100.0);
  s.items[health].respawn_s = 5.0;  // not there yet

  ItemProfile p = Profile(3, 2);
  ItemPlanner planner;
  planner.Configure(p);

  // Tick 0: only the ammo item exists in practice -> ammo trip.
  GoalDecision d = planner.Step(s.World());
  CHECK(d.has_goal && d.goal_id == s.items[ammo].id, "ammo trip starts");

  // Tick 5: the medkit respawns and is now clearly the better goal, but the
  // dwell window has not elapsed.
  s.items[health].respawn_s = 0.0;
  s.combat.tick = 5;
  d = planner.Step(s.World());
  CHECK(d.action == ItemAction::kKeep, "no switch inside the dwell window");
  CHECK(d.reason == ItemReason::kHysteresisHold, "reason is hysteresis-hold");

  // Tick 40: dwell elapsed -> switch to the medkit.
  s.combat.tick = 40;
  d = planner.Step(s.World());
  CHECK(d.action == ItemAction::kSwitch, "switch after the dwell window");
  CHECK(d.goal_id == s.items[health].id, "medkit replaces the ammo trip");
  CHECK(planner.switches() == 1, "switch counter incremented");
  CHECK(planner.selections() == 1, "the switch is not counted as a new selection");
}

static void TestCommitMarginPreventsFlapping() {
  Scenario s;
  s.self.health = 40.0;
  s.self.armor = 100.0;
  s.Add(ItemKind::kHealth, 0.0, -8.0, 100.0);
  s.Add(ItemKind::kHealth, 0.0, -14.0, 100.0);

  ItemProfile p = Profile(3, 2);
  p.tuning.commit_margin = 0.50;  // artificial: no near-tie may ever switch
  ItemPlanner planner;
  planner.Configure(p);

  GoalDecision d = planner.Step(s.World());
  CHECK(d.has_goal, "goal committed");
  const int first = d.goal_id;

  int switches = 0;
  for (int t = 1; t <= 40; ++t) {  // inside the default time budget
    s.combat.tick = t;
    d = planner.Step(s.World());
    if (d.action == ItemAction::kSwitch) ++switches;
  }
  CHECK(switches == 0, "identical needs never cause a switch");
  CHECK(planner.goal_id() == first, "the original goal is kept");
  CHECK(planner.timeouts() == 0, "no timeout inside the test window");
}

/* ------------------------------------------------------------------------ */
/* 9. Cooldowns / blacklist after pickup                                     */
/* ------------------------------------------------------------------------ */

static void TestPickedItemIsBlacklisted() {
  Scenario s;
  s.self.health = 30.0;
  s.self.armor = 100.0;
  const int medkit = s.Add(ItemKind::kHealth, 0.0, -8.0, 50.0);
  ItemPlanner planner;
  planner.Configure(Profile(3, 1));

  GoalDecision d = planner.Step(s.World());
  CHECK(d.has_goal && d.goal_id == s.items[medkit].id, "medkit trip starts");

  // The caller reports the bot's new position: it walked to the pickup.
  s.self.eye.z = -6.6;
  s.self.health = 80.0;
  s.combat.tick = 20;
  d = planner.Step(s.World());
  CHECK(d.action == ItemAction::kReached, "arrival detected by the arrival radius");
  CHECK(planner.reached() == 1, "reached counter incremented");
  CHECK(d.goal_id == s.items[medkit].id, "the reached item is reported");

  // The item is consumed and respawning: the same id must not be re-selected.
  s.items[medkit].respawn_s = 25.0;
  for (int t = 21; t <= 40; ++t) {
    s.combat.tick = t;
    d = planner.Step(s.World());
    CHECK(d.goal_id != s.items[medkit].id, "a consumed item is not re-selected");
  }

  // Even after the respawn the blacklist still holds for its own window.
  s.items[medkit].respawn_s = 0.0;
  s.combat.tick = 41;
  d = planner.Step(s.World());
  CHECK(d.goal_id != s.items[medkit].id, "the blacklist survives the respawn");
}

static void TestReachedForcesNothingAndClearsGoal() {
  Scenario s;
  s.self.health = 30.0;
  s.Add(ItemKind::kHealth, 0.0, -1.0, 50.0);
  ItemPlanner planner;
  planner.Configure(Profile(3, 1));
  const GoalDecision d = planner.Step(s.World());
  // At 1 m the item is inside the arrival radius on the very first tick: the
  // planner must commit and report, not silently swallow it.
  CHECK(d.has_goal || d.action == ItemAction::kReached,
        "an item inside the arrival radius is handled immediately");
}

/* ------------------------------------------------------------------------ */
/* 10. Skill levels                                                          */
/* ------------------------------------------------------------------------ */

static void TestSkillLevelsChangeWhatIsWorthATrip() {
  // A 60 m trip takes ~6.4 s. A beginner's time budget is far shorter than an
  // expert's, so the same pickup is rejected by tier 1 and accepted by tier 5.
  Scenario s;
  s.self.health = 40.0;
  s.Add(ItemKind::kHealth, 0.0, -60.0, 60.0);

  ItemPlanner beginner;
  beginner.Configure(Profile(1, 2));
  const GoalDecision db = beginner.Step(s.World());
  CHECK(!db.has_goal, "a beginner does not walk 60 m for a medkit");

  ItemPlanner expert;
  expert.Configure(Profile(5, 2));
  const GoalDecision de = expert.Step(s.World());
  CHECK(de.has_goal, "an expert plans the longer trip");

  int n = 0;
  const ItemEvaluation* ev = beginner.last_evaluations(&n);
  CHECK(ev[0].reject == ItemReason::kOutOfRange,
        "beginner rejects the trip for travel-time reasons");
}

static void TestSkillPricesRiskDifferently() {
  Scenario s;
  s.self.health = 50.0;
  s.threat.visible_enemies = 1;
  s.threat.nearest_enemy_m = 7.0;
  s.threat.under_fire = true;
  s.Add(ItemKind::kHealth, 0.0, -8.0, 50.0);

  const ScoreContext cb = MakeContext(Profile(1, 2), s.World(), 0);
  const ScoreContext ce = MakeContext(Profile(5, 2), s.World(), 0);
  CHECK(cb.skill.risk_awareness < ce.skill.risk_awareness,
        "risk awareness grows with tier");
  const double exposure = Exposure(cb);
  CHECK(exposure > 0.3, "a 7 m enemy is a real exposure");
  CHECK(ThreatFactor(ce) < ThreatFactor(cb),
        "an expert discounts a risky detour more, not less");
}

static void TestSkillTablesAreMonotone() {
  for (int t = 2; t <= kSkillTierCount; ++t) {
    const ItemSkillBlock a = SkillFor(t - 1);
    const ItemSkillBlock b = SkillFor(t);
    CHECK(b.planning_horizon_s > a.planning_horizon_s, "horizon increases with tier");
    CHECK(b.risk_awareness > a.risk_awareness, "risk awareness increases with tier");
    CHECK(b.discipline > a.discipline, "discipline increases with tier");
    CHECK(b.tie_noise <= a.tie_noise, "tie noise does not increase with tier");
  }
  // Tuning derived from the blocks stays inside its documented bounds.
  for (int t = 1; t <= kSkillTierCount; ++t) {
    for (int p = 0; p < kPersonalityCount; ++p) {
      const ItemProfile prof = Profile(t, p);
      CHECK(ValidateProfile(prof) == ProfileError::kOk, "derived profile validates");
      CHECK(prof.tuning.min_commit_s >= 0.40 && prof.tuning.min_commit_s <= 2.60,
            "dwell time stays bounded");
      CHECK(prof.tuning.max_search_time_s >= 2.5 && prof.tuning.max_search_time_s <= 20.0,
            "time budget stays bounded");
      CHECK(prof.tuning.min_utility > 0.0 && prof.tuning.min_utility <= 0.9,
            "utility floor stays bounded");
    }
  }
}

/* ------------------------------------------------------------------------ */
/* 11. Personalities                                                         */
/* ------------------------------------------------------------------------ */

static void TestPersonalityChangesPreferences() {
  Scenario s;
  s.self.health = 40.0;
  s.self.armor = 60.0;
  SetAmmo(s.self, 2, 10);
  const int health_i = s.Add(ItemKind::kHealth, 0.0, -10.0, 50.0);
  s.Add(ItemKind::kArmor, 2.0, -10.0, 50.0);
  const int strat_i = s.Add(ItemKind::kStrategic, -2.0, -10.0, 0.8);
  const int weapon_i = s.Add(ItemKind::kWeapon, 4.0, -10.0, 0.0, 6);

  auto utility_of = [&](const ItemProfile& p, int index) {
    const ScoreContext c = MakeContext(p, s.World(), 0);
    return EvaluateItem(c, s.World(), index).terms.utility;
  };

  const ItemProfile survivor = Profile(3, 1);
  const ItemProfile aggressor = Profile(3, 0);
  const ItemProfile controller = Profile(3, 3);

  CHECK(utility_of(survivor, health_i) > utility_of(aggressor, health_i),
        "a survivor values health more than an aggressor");
  CHECK(utility_of(aggressor, weapon_i) > utility_of(survivor, weapon_i),
        "an aggressor values a new weapon more than a survivor");
  CHECK(utility_of(controller, strat_i) > utility_of(survivor, strat_i),
        "a controller values strategic resources more");

  // Appetite must not turn into an absolute rule: a cautious survivor at full
  // health still ignores health.
  Scenario full;
  full.self.health = 100.0;
  full.Add(ItemKind::kHealth, 0.0, -5.0, 100.0);
  const ScoreContext cf = MakeContext(survivor, full.World(), 0);
  CHECK(EvaluateItem(cf, full.World(), 0).terms.utility == 0.0,
        "even the greediest survivor skips health at 100 %");

  // Personality must never touch skill parameters (block-level separation).
  for (int p = 0; p < kPersonalityCount; ++p) {
    const ItemProfile a = Profile(4, p);
    const ItemProfile b = Profile(4, 0);
    CHECK(a.skill.planning_horizon_s == b.skill.planning_horizon_s &&
              a.skill.risk_awareness == b.skill.risk_awareness &&
              a.skill.discipline == b.skill.discipline &&
              a.skill.tie_noise == b.skill.tie_noise,
          "personality leaves the skill block untouched");
  }
  for (int t = 1; t <= kSkillTierCount; ++t) {
    const ItemProfile a = Profile(t, 1);
    const ItemProfile b = Profile(1, 1);
    CHECK(a.persona.health_appetite == b.persona.health_appetite &&
              a.persona.caution == b.persona.caution,
          "tier leaves the personality block untouched");
  }
}

static void TestStrategicResourcesOnlyWithoutAFight() {
  Scenario idle;
  idle.self.health = 100.0;
  idle.self.armor = 100.0;
  idle.Add(ItemKind::kStrategic, 0.0, -8.0, 0.9);

  Scenario fighting = idle;
  fighting.combat.engaged = true;
  fighting.combat.combat_priority = 0.5;
  fighting.threat.visible_enemies = 1;
  fighting.threat.nearest_enemy_m = 30.0;

  const ItemProfile p = Profile(3, 3);
  const ScoreContext ci = MakeContext(p, idle.World(), 0);
  const ScoreContext cf = MakeContext(p, fighting.World(), 0);
  const double ui = EvaluateItem(ci, idle.World(), 0).terms.utility;
  const double uf = EvaluateItem(cf, fighting.World(), 0).terms.utility;
  CHECK(ui > 0.25, "a strategic resource is attractive while idle");
  CHECK(uf < ui, "the same resource is less attractive mid-fight");
}

/* ------------------------------------------------------------------------ */
/* 12. Determinism                                                           */
/* ------------------------------------------------------------------------ */

struct TraceEntry {
  int action = 0;
  int reason = 0;
  int goal_id = -1;
  double utility = 0.0;
  double need = 0.0;
};

static void RunTrace(int tier, int persona, uint32_t seed, TraceEntry* out, int ticks) {
  Scenario s;
  s.self.health = 100.0;
  s.self.armor = 100.0;
  SetAmmo(s.self, 2, 20);
  s.Add(ItemKind::kHealth, 0.0, -9.0, 50.0);
  s.Add(ItemKind::kArmor, 3.0, -12.0, 50.0);
  s.Add(ItemKind::kAmmo, -2.0, -6.0, 0.0, 2, 25);
  s.Add(ItemKind::kWeapon, 5.0, -14.0, 0.0, 6);

  ItemProfile p = Profile(tier, persona);
  p.seed = seed;
  ItemPlanner planner;
  planner.Configure(p);

  for (int t = 0; t < ticks; ++t) {
    s.combat.tick = t;
    s.self.health = 100.0 - 0.25 * static_cast<double>(t % 200);
    if (t > 60 && t < 80) s.self.health = 35.0;
    if (t > 120) s.threat.visible_enemies = 1;
    if (t > 120) s.threat.nearest_enemy_m = 14.0;
    const GoalDecision d = planner.Step(s.World());
    out[t].action = static_cast<int>(d.action);
    out[t].reason = static_cast<int>(d.reason);
    out[t].goal_id = d.goal_id;
    out[t].utility = d.utility;
    out[t].need = d.need;
  }
}

static void TestDeterminism() {
  const int kTicks = 240;
  static TraceEntry a[kTicks];
  static TraceEntry b[kTicks];
  RunTrace(3, 2, 0xABCDEF01u, a, kTicks);
  RunTrace(3, 2, 0xABCDEF01u, b, kTicks);

  bool identical = true;
  for (int i = 0; i < kTicks; ++i) {
    if (a[i].action != b[i].action || a[i].reason != b[i].reason ||
        a[i].goal_id != b[i].goal_id || a[i].utility != b[i].utility ||
        a[i].need != b[i].need) {
      identical = false;
      std::printf("  divergence at tick %d\n", i);
      break;
    }
  }
  CHECK(identical, "identical inputs and seed produce a bit-identical trace");

  // A different seed may only change exact ties, never the decision structure.
  static TraceEntry c[kTicks];
  RunTrace(3, 2, 0x12345678u, c, kTicks);
  int differing_ticks = 0;
  for (int i = 0; i < kTicks; ++i) {
    if (a[i].action != c[i].action || a[i].goal_id != c[i].goal_id) ++differing_ticks;
  }
  CHECK(differing_ticks == 0,
        "without an exact tie the seed cannot change any decision");
}

static void TestTieBreakIsDeterministicAndSeedBound() {
  // Two structurally identical items: only the tie-break can decide.
  Scenario s;
  s.self.health = 30.0;
  s.items[0] = ItemSnapshot();
  s.items[0].id = 7;
  s.items[0].kind = ItemKind::kHealth;
  s.items[0].pos = Vec3{0.0, 0.0, -9.0};
  s.items[0].value = 30.0;
  s.items[0].visible = true;
  s.items[1] = s.items[0];
  s.items[1].id = 9;
  s.count = 2;

  auto decide = [&](uint32_t seed) {
    ItemProfile p = Profile(3, 2);
    p.seed = seed;
    ItemPlanner planner;
    planner.Configure(p);
    return planner.Step(s.World()).goal_id;
  };
  const int first = decide(0x11111111u);
  for (int i = 0; i < 5; ++i) {
    CHECK(decide(0x11111111u) == first, "the same seed always picks the same item");
  }
  int differing = 0;
  for (uint32_t seed = 0x22220001u; seed < 0x22220011u; ++seed) {
    if (decide(seed) != first) ++differing;
  }
  CHECK(differing > 0, "different seeds can resolve an exact tie differently");
}

/* ------------------------------------------------------------------------ */
/* 13. Fail-closed validation                                                */
/* ------------------------------------------------------------------------ */

static void TestValidationFailsClosed() {
  Scenario s;
  s.Add(ItemKind::kHealth, 0.0, -5.0, 50.0);
  ItemPlanner planner;
  planner.Configure(Profile(3, 2));
  CHECK(plain_ok(s.World()), "the baseline scenario is valid");

  Scenario bad_count = s;
  bad_count.count = kMaxItems + 1;
  CHECK(!plain_ok(bad_count.World()), "count above the cap is rejected");

  Scenario null_items = s;
  null_items.count = 2;
  CHECK(!plain_ok(null_items.World()), "null item pointer is rejected");

  Scenario nan_pos = s;
  nan_pos.items[0].pos.x = std::nan("");
  CHECK(!plain_ok(nan_pos.World()), "NaN position is rejected");

  Scenario neg_value = s;
  neg_value.items[0].value = -5.0;
  CHECK(!plain_ok(neg_value.World()), "negative value is rejected");

  Scenario dup = s;
  dup.Add(ItemKind::kHealth, 1.0, -5.0, 50.0);
  dup.items[1].id = dup.items[0].id;
  CHECK(!plain_ok(dup.World()), "duplicate item id is rejected");

  Scenario bad_kind = s;
  bad_kind.items[0].kind = ItemKind::kNone;
  CHECK(!plain_ok(bad_kind.World()), "unknown item kind is rejected");

  Scenario bad_weapon = s;
  bad_weapon.items[0].weapon_index = 99;
  CHECK(!plain_ok(bad_weapon.World()), "out-of-range weapon index is rejected");

  Scenario ammo_no_weapon = s;
  ammo_no_weapon.items[0].kind = ItemKind::kAmmo;
  ammo_no_weapon.items[0].weapon_index = 0;
  CHECK(!plain_ok(ammo_no_weapon.World()), "ammo without a weapon index is rejected");

  Scenario bad_self = s;
  bad_self.self.max_health = 0.0;
  CHECK(!plain_ok(bad_self.World()), "zero max health is rejected");

  Scenario health_over_max = s;
  health_over_max.self.health = 150.0;
  CHECK(!plain_ok(health_over_max.World()), "health above max is rejected");

  Scenario bad_priority = s;
  bad_priority.combat.combat_priority = 1.5;
  CHECK(!plain_ok(bad_priority.World()), "combat priority outside 0..1 is rejected");

  Scenario bad_threat = s;
  bad_threat.threat.incoming_dps = -1.0;
  CHECK(!plain_ok(bad_threat.World()), "negative incoming dps is rejected");

  // The planner must fail closed, not crash or guess.
  Scenario invalid = s;
  invalid.items[0].pos.z = std::nan("");
  GoalDecision d = planner.Step(invalid.World());
  CHECK(d.reason == ItemReason::kInvalidWorld, "invalid world reports invalid-world");
  CHECK(!d.has_goal, "no goal is produced from an invalid world");

  // If a goal was already running, it is dropped with the same reason.
  Scenario s2;
  s2.self.health = 30.0;
  s2.Add(ItemKind::kHealth, 0.0, -8.0, 50.0);
  ItemPlanner p2;
  p2.Configure(Profile(3, 1));
  CHECK(p2.Step(s2.World()).has_goal, "valid tick commits a goal");
  s2.items[0].value = -1.0;
  const GoalDecision drop = p2.Step(s2.World());
  CHECK(drop.action == ItemAction::kAbort, "invalid snapshot aborts the goal");
  CHECK(drop.reason == ItemReason::kInvalidWorld, "abort reason is invalid-world");
}

static void TestInvalidProfileRejected() {
  ItemProfile p = Profile(3, 2);
  CHECK(ValidateProfile(p) == ProfileError::kOk, "default profile validates");
  p.tier = 0;
  CHECK(ValidateProfile(p) != ProfileError::kOk, "tier 0 rejected");
  p = Profile(3, 2);
  p.seed = 0;
  CHECK(ValidateProfile(p) != ProfileError::kOk, "seed 0 rejected");
  p = Profile(3, 2);
  p.tuning.min_utility = 5.0;
  CHECK(ValidateProfile(p) != ProfileError::kOk, "absurd utility floor rejected");
  p = Profile(3, 2);
  p.tuning.max_search_time_s = std::nan("");
  CHECK(ValidateProfile(p) != ProfileError::kOk, "NaN time budget rejected");
  ItemProfile out;
  CHECK(!BuildItemProfile(6, 0, 1u, &out), "tier 6 rejected");
  CHECK(!BuildItemProfile(3, 6, 1u, &out), "personality 6 rejected");
  CHECK(!BuildItemProfile(3, 0, 1u, nullptr), "null output rejected");
}

static void TestScoringInvariants() {
  // Ammo need is monotone in the remaining ammo and zero at full.
  Scenario s;
  s.self.owned_weapons = 0;
  GrantWeapon(s.self, 1);
  GrantWeapon(s.self, 2);
  SetAmmo(s.self, 2, 0);
  const int item = s.Add(ItemKind::kAmmo, 0.0, -5.0, 0.0, 2, 10);
  const ItemProfile p = Profile(3, 2);

  double previous = 2.0;
  for (int ammo = 0; ammo <= 50; ammo += 10) {
    s.self.ammo[2] = ammo;
    const ScoreContext c = MakeContext(p, s.World(), 0);
    const double need = EvaluateItem(c, s.World(), item).terms.need;
    CHECK(need <= previous + 1e-9, "ammo need never grows with more ammo");
    previous = need;
  }
  s.self.ammo[2] = 50;
  const ScoreContext full = MakeContext(p, s.World(), 0);
  CHECK(EvaluateItem(full, s.World(), item).terms.need == 0.0,
        "full ammo has zero ammo need");

  // Distance and travel time reduce utility, all else equal.
  Scenario near;
  near.self.health = 40.0;
  near.Add(ItemKind::kHealth, 0.0, -5.0, 50.0);
  Scenario far;
  far.self.health = 40.0;
  far.Add(ItemKind::kHealth, 0.0, -35.0, 50.0);
  const ScoreContext cn = MakeContext(p, near.World(), 0);
  const ScoreContext cfa = MakeContext(p, far.World(), 0);
  const double un = EvaluateItem(cn, near.World(), 0).terms.utility;
  const double uf = EvaluateItem(cfa, far.World(), 0).terms.utility;
  CHECK(un > uf, "a nearer identical pickup has higher utility");
  CHECK(uf > 0.0, "a far pickup still has positive utility");

  // A visible item is worth at least as much as a stale observation.
  Scenario stale = near;
  stale.items[0].visible = false;
  stale.items[0].staleness_s = 4.0;
  const ScoreContext cs = MakeContext(p, stale.World(), 0);
  const double us = EvaluateItem(cs, stale.World(), 0).terms.utility;
  CHECK(us < un, "a stale observation is discounted");

  // Realistic distances are never rejected purely for being far.
  for (double z = -5.0; z >= -45.0; z -= 5.0) {
    Scenario t;
    t.self.health = 30.0;
    t.Add(ItemKind::kHealth, 0.0, z, 100.0);
    const ScoreContext ct = MakeContext(Profile(5, 2), t.World(), 0);
    CHECK(EvaluateItem(ct, t.World(), 0).eligible,
          "an expert accepts a medkit inside 45 m");
  }
}

/* ------------------------------------------------------------------------ */
/* 14. Navigation seam                                                       */
/* ------------------------------------------------------------------------ */

static void TestNavigationSeamCommitsAndCancels() {
  Scenario s;
  s.self.health = 30.0;
  s.Add(ItemKind::kHealth, 0.0, -9.0, 50.0);

  RecordingNavigationSink nav;
  ItemPlanner planner;
  planner.Configure(Profile(3, 1));

  GoalDecision d = planner.Step(s.World(), &nav);
  CHECK(d.has_goal, "planner commits with a navigation sink attached");
  CHECK(nav.submits() == 1, "exactly one goal was submitted");
  CHECK(nav.last_goal().goal_id == d.goal_id, "submitted goal matches the decision");
  CHECK(nav.last_goal().priority == NavPriority::kCritical,
        "a 30 % health pickup is a survival goal");
  CHECK(!nav.last_goal().yield_to_combat, "survival goals do not yield to combat");
  CHECK(nav.last_goal().expires_tick > nav.last_goal().issued_tick,
        "a submitted goal always has a validity window");
  CHECK(nav.last_goal().Valid(), "the emitted goal is well formed");

  // Keep does not resubmit.
  s.combat.tick = 1;
  planner.Step(s.World(), &nav);
  CHECK(nav.submits() == 1, "a kept goal is not submitted again");

  // A threat abort must cancel the goal.
  s.threat.visible_enemies = 1;
  s.threat.nearest_enemy_m = 5.0;
  s.threat.under_fire = true;
  s.combat.tick = 2;
  d = planner.Step(s.World(), &nav);
  CHECK(d.reason == ItemReason::kThreatOverride, "threat abort triggered");
  CHECK(nav.cancels() >= 1, "the navigation goal was cancelled");
}

static void TestNavigationArrivalAndUnreachable() {
  Scenario s;
  s.self.health = 30.0;
  const int id = s.Add(ItemKind::kHealth, 0.0, -9.0, 50.0);

  RecordingNavigationSink nav;
  nav.SetArriveAfterPolls(3);
  ItemPlanner planner;
  planner.Configure(Profile(3, 1));
  planner.Step(s.World(), &nav);

  GoalDecision d = planner.Step(s.World(), &nav);
  CHECK(d.action == ItemAction::kKeep, "still travelling on the second poll");
  int steps = 0;
  while (d.action != ItemAction::kReached && steps < 8) {
    d = planner.Step(s.World(), &nav);
    ++steps;
  }
  CHECK(d.action == ItemAction::kReached, "arrival reported by navigation is accepted");
  CHECK(d.goal_id == s.items[id].id, "the reached item is reported");

  // Unreachable: abort and blacklist, no retry storm.
  Scenario s2;
  s2.self.health = 30.0;
  const int id2 = s2.Add(ItemKind::kHealth, 0.0, -20.0, 50.0);
  RecordingNavigationSink nav2;
  nav2.MarkUnreachable(s2.items[id2].id);
  ItemPlanner p2;
  p2.Configure(Profile(3, 1));
  GoalDecision d2 = p2.Step(s2.World(), &nav2);
  CHECK(!d2.has_goal, "an unreachable goal is not held");
  CHECK(!p2.has_goal(), "no goal after a navigation refusal");
}

static void TestNavigationStallAborts() {
  Scenario s;
  s.self.health = 30.0;
  s.Add(ItemKind::kHealth, 0.0, -20.0, 50.0);
  RecordingNavigationSink nav;
  nav.SetStallAfterPolls(1);
  ItemPlanner planner;
  planner.Configure(Profile(3, 1));
  planner.Step(s.World(), &nav);
  GoalDecision d = planner.Step(s.World(), &nav);
  if (d.action != ItemAction::kAbort) d = planner.Step(s.World(), &nav);
  CHECK(d.action == ItemAction::kAbort, "two stall reports abort the goal");
  CHECK(d.reason == ItemReason::kStalled, "abort reason is stalled");
}

static void TestNavigationGoalTranslation() {
  GoalTranslationInput in;
  in.goal_id = 3;
  in.pos = Vec3{1.0, 2.0, 3.0};
  in.survival = false;
  in.utility = 0.30;
  in.issued_tick = 100;
  in.max_duration_ticks = 200;
  in.caution = 0.20;
  NavGoal soft = MakeNavGoal(in);
  CHECK(soft.priority == NavPriority::kSoft, "low utility stays a soft detour");
  CHECK(soft.yield_to_combat, "a soft detour yields to combat");
  CHECK_NEAR(soft.max_speed_frac, 1.0 - 0.35 * 0.20, 1e-12, "speed follows caution");
  CHECK(soft.expires_tick == 300, "expiry is issue tick plus duration");
  CHECK(soft.Valid(), "translated goal validates");

  in.urgent = true;  // starved / half health, but not survival
  in.survival = false;
  NavGoal urgent = MakeNavGoal(in);
  CHECK(urgent.priority == NavPriority::kUrgent,
        "an urgent but not critical need maps to kUrgent");

  in.survival = true;
  in.utility = 0.9;
  in.caution = 1.0;
  NavGoal hard = MakeNavGoal(in);
  CHECK(hard.priority == NavPriority::kCritical, "survival goals are critical");
  CHECK(!hard.yield_to_combat, "survival goals do not yield");
  CHECK(hard.max_speed_frac >= 0.6, "a cautious bot never crawls below 60 %");
}

static void TestPlannerDoesNotImplementNavigation() {
  // The seam is abstract: a sink that refuses everything must leave the
  // planner without a goal instead of producing its own movement.
  Scenario s;
  s.self.health = 30.0;
  s.Add(ItemKind::kHealth, 0.0, -9.0, 50.0);
  RecordingNavigationSink nav;
  nav.RejectEverything(true);
  ItemPlanner planner;
  planner.Configure(Profile(3, 1));
  const GoalDecision d = planner.Step(s.World(), &nav);
  CHECK(!d.has_goal, "a refusing navigation leaves no goal behind");
  CHECK(d.reason == ItemReason::kUnreachable,
        "a refusing navigation is reported as unreachable, not as a movement command");
  CHECK(d.action == ItemAction::kNone, "and no action is invented");
}

/* ------------------------------------------------------------------------ */
/* 15. CPU budget                                                            */
/* ------------------------------------------------------------------------ */

static double MeasureTicks(ItemPlanner& planner, const Scenario& base, int ticks,
                           long long* evaluations) {
  const auto t0 = std::chrono::steady_clock::now();
  Scenario s = base;
  for (int t = 0; t < ticks; ++t) {
    s.combat.tick = t;
    s.self.health = 100.0 - 0.3 * static_cast<double>(t % 150);
    if ((t % 400) > 200) {
      s.threat.visible_enemies = 1;
      s.threat.nearest_enemy_m = 12.0;
      s.threat.under_fire = true;
      s.combat.engaged = true;
      s.combat.combat_priority = 0.5;
    } else {
      s.threat = ThreatState();
      s.combat.engaged = false;
      s.combat.combat_priority = 0.0;
    }
    planner.Step(s.World());
  }
  const auto t1 = std::chrono::steady_clock::now();
  const double total_us =
      std::chrono::duration_cast<std::chrono::nanoseconds>(t1 - t0).count() / 1000.0;
  if (evaluations != nullptr) *evaluations = planner.evaluations();
  return total_us / ticks;
}

static void TestCpuBudget() {
  Scenario s;
  s.self.health = 60.0;
  s.self.armor = 40.0;
  SetAmmo(s.self, 2, 10);
  // 24 items, i.e. far above the realistic number of nearby pickups.
  for (int i = 0; i < 24; ++i) {
    const ItemKind kind = static_cast<ItemKind>(1 + (i % 6));
    const double x = (i % 5) * 2.0 - 4.0;
    const double z = -6.0 - (i / 5) * 3.0;
    if (kind == ItemKind::kAmmo) {
      s.Add(kind, x, z, 0.0, 1 + (i % 12), 10);
    } else if (kind == ItemKind::kWeapon) {
      s.Add(kind, x, z, 0.0, 1 + (i % 12));
    } else {
      s.Add(kind, x, z, 40.0);
    }
  }
  CHECK(s.count == 24, "24-item fixture built");

  ItemPlanner planner;
  planner.Configure(Profile(3, 2));
  long long evals = 0;
  const double us_per_tick = MeasureTicks(planner, s, 20000, &evals);
  const double us_per_eval =
      evals > 0 ? (us_per_tick * 20000.0) / static_cast<double>(evals) : 0.0;
  std::printf("  cpu: 24 items, %.3f us/tick, %.4f us/item-evaluation, %lld evals\n",
              us_per_tick, us_per_eval, evals);
  CHECK(us_per_tick < 50.0, "per-tick decision cost stays below the 50 us budget");
  CHECK(us_per_eval < 2.0, "per-item evaluation stays below 2 us");
  CHECK(us_per_tick > 0.0, "the measurement is non-zero (sanity)");
}

int main() {
  std::printf("== item utility layer: offline acceptance tests ==\n");

  std::printf("[1] low health\n");
  TestLowHealthPrioritisesHealth();
  TestHealthNeedIsConvexAndBounded();
  std::printf("[2] full health\n");
  TestFullHealthDoesNotChaseHealth();
  TestTinyHealthItemIsNotEssential();
  std::printf("[3] missing ammo\n");
  TestMissingAmmoSelectsAmmo();
  TestAmmoForUnownedWeaponIsWorthless();
  TestAmmoStarvationIsAnEmergency();
  TestAmmoStarvationIsReportedWhenNothingHelps();
  TestUrgentGoalPriorityReachesNavigation();
  std::printf("[4] weak weapons\n");
  TestWeakWeaponSeeksUpgrade();
  TestStrongLoadoutIgnoresWeakerWeapon();
  TestDuplicateWeaponIsAmmoNotUpgrade();
  std::printf("[5] competing items\n");
  TestCompetingItemsChooseHighestUtility();
  std::printf("[6] threats\n");
  TestEnemyInProximityAbortsSearch();
  TestCloseFinishIsNotAborted();
  TestCombatLockSuppressesNonEssentialTrips();
  std::printf("[7] aborts\n");
  TestDamageAbortAndGlobalCooldown();
  TestPerItemCooldownBlocksOnlyThatItem();
  TestTimeoutAbortsLongSearch();
  std::printf("[8] goal switch\n");
  TestGoalSwitchRespectsDwellAndMargin();
  TestCommitMarginPreventsFlapping();
  std::printf("[9] cooldowns\n");
  TestPickedItemIsBlacklisted();
  TestReachedForcesNothingAndClearsGoal();
  std::printf("[10] skill levels\n");
  TestSkillLevelsChangeWhatIsWorthATrip();
  TestSkillPricesRiskDifferently();
  TestSkillTablesAreMonotone();
  std::printf("[11] personalities\n");
  TestPersonalityChangesPreferences();
  TestStrategicResourcesOnlyWithoutAFight();
  std::printf("[12] determinism\n");
  TestDeterminism();
  TestTieBreakIsDeterministicAndSeedBound();
  std::printf("[13] validation and invariants\n");
  TestValidationFailsClosed();
  TestInvalidProfileRejected();
  TestScoringInvariants();
  std::printf("[14] navigation seam\n");
  TestNavigationSeamCommitsAndCancels();
  TestNavigationArrivalAndUnreachable();
  TestNavigationStallAborts();
  TestNavigationGoalTranslation();
  TestPlannerDoesNotImplementNavigation();
  std::printf("[15] cpu budget\n");
  TestCpuBudget();

  std::printf("ITEM UTILITY: %d checks, %d failures\n", g_checks, g_failures);
  if (g_failures == 0) std::printf("ITEM UTILITY PASS\n");
  return g_failures == 0 ? 0 : 1;
}

