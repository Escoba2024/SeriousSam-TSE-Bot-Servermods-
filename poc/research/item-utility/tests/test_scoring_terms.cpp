// SPDX-License-Identifier: GPL-2.0-only
// test_scoring_terms.cpp - term-by-term verification of the utility function.
//
// test_item_utility.cpp checks *decisions*; this file checks the *terms* they
// are built from, plus a deterministic property sweep over pseudo-random worlds
// (bounds, no NaN, no negative utility). Separating the two makes a regression
// easy to localise: a broken decision points here, a broken term points at one
// line.

#include <cmath>
#include <cstdio>

#include "item_profile.h"
#include "item_scoring.h"
#include "item_snapshot.h"
#include "item_types.h"

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

/* ------------------------------------------------------------------------ */
/* Helpers                                                                   */
/* ------------------------------------------------------------------------ */

struct Ctx {
  ItemWorld world;
  ItemSnapshot items[8];
  int count = 0;

  Ctx() {
    world.self.max_health = 100.0;
    world.self.health = 100.0;
    world.self.max_armor = 100.0;
    world.self.armor = 100.0;
    world.self.move_speed_mps = 10.0;
    GrantWeapon(world.self, 1);
    GrantWeapon(world.self, 2);
    GrantWeapon(world.self, 4);
    SetAmmo(world.self, 2, 50);
    SetAmmo(world.self, 4, 30);
    world.items = items;
  }

  int Add(ItemKind k, double x, double z, double value = 0.0, int weapon = 0,
          int amount = 0) {
    ItemSnapshot& it = items[count];
    it = ItemSnapshot();
    it.id = count;
    it.kind = k;
    it.pos = Vec3{x, 0.0, z};
    it.value = value;
    it.weapon_index = weapon;
    it.amount = amount;
    it.visible = true;
    world.count = count + 1;
    return count++;
  }
};

static ItemProfile Prof(int tier = 3, int persona = 2) {
  ItemProfile p;
  BuildItemProfile(tier, persona, DeriveItemSeed(7u, 0, tier, persona), &p);
  return p;
}

/* ------------------------------------------------------------------------ */
/* Threat terms                                                              */
/* ------------------------------------------------------------------------ */

static void TestExposure() {
  Ctx c;
  ScoreContext ctx = MakeContext(Prof(), c.world, 0);
  CHECK(Exposure(ctx) == 0.0, "no visible enemy means no exposure");

  ctx.visible_enemies = 1;
  double previous = -1.0;
  for (double d = 30.0; d >= 1.0; d -= 1.0) {
    ctx.nearest_enemy_m = d;
    const double e = Exposure(ctx);
    CHECK(e >= 0.0 && e <= 1.0, "exposure stays in 0..1");
    if (previous >= 0.0) CHECK(e >= previous, "exposure grows as the enemy closes");
    previous = e;
  }
  ctx.under_fire = true;
  const double under_fire = Exposure(ctx);
  ctx.under_fire = false;
  CHECK(under_fire > Exposure(ctx), "being shot at raises exposure");
}

static void TestThreatFactor() {
  Ctx c;
  ScoreContext ctx = MakeContext(Prof(), c.world, 0);
  CHECK(ThreatFactor(ctx) == 1.0, "no threat means no discount");

  ctx.visible_enemies = 1;
  ctx.nearest_enemy_m = 3.0;
  ctx.under_fire = true;
  const double tf = ThreatFactor(ctx);
  CHECK(tf >= 0.30 && tf < 1.0, "a close enemy discounts, but never to zero");

  // Expert prices risk more than beginner: same world, both contexts.
  ScoreContext expert = MakeContext(Prof(5, 2), c.world, 0);
  ScoreContext beginner = MakeContext(Prof(1, 2), c.world, 0);
  expert.visible_enemies = beginner.visible_enemies = 1;
  expert.nearest_enemy_m = beginner.nearest_enemy_m = 6.0;
  expert.under_fire = beginner.under_fire = true;
  CHECK(ThreatFactor(expert) < ThreatFactor(beginner),
        "the higher tier discounts the risky trip more");
}

static void TestPriorityFactor() {
  Ctx c;
  c.Add(ItemKind::kArmor, 0.0, -8.0, 50.0);
  const ItemSnapshot& armor = c.items[0];
  ScoreContext ctx = MakeContext(Prof(), c.world, 0);
  CHECK(PriorityFactor(ctx, armor) == 1.0, "no fight means no suppression");

  ctx.engaged = true;
  ctx.combat_priority = 0.2;
  const double low = PriorityFactor(ctx, armor);
  ctx.combat_priority = 0.9;
  const double high = PriorityFactor(ctx, armor);
  CHECK(high < low, "a committed fight suppresses more");
  CHECK(high >= 0.05, "suppression is bounded below");

  // Critical health relaxes the suppression for health/armor pickups.
  ctx.health_frac = 0.15;
  ctx.combat_priority = 0.9;
  CHECK(PriorityFactor(ctx, armor) > high,
        "a dying bot is allowed to disengage for a pickup");

  ItemSnapshot ammo = armor;
  ammo.kind = ItemKind::kAmmo;
  ammo.weapon_index = 2;
  CHECK(PriorityFactor(ctx, ammo) < PriorityFactor(ctx, armor),
        "the survival exemption applies to health/armor only");
}

/* ------------------------------------------------------------------------ */
/* Opportunity terms                                                         */
/* ------------------------------------------------------------------------ */

static void TestTimeAndDistanceFactors() {
  Ctx c;
  ScoreContext ctx = MakeContext(Prof(), c.world, 0);
  double previous = 1.1;
  for (double d = 0.0; d <= 100.0; d += 5.0) {
    const double travel = d / 10.0 + 0.35;
    const double f = TimeFactor(ctx, travel);
    CHECK(f <= 1.0 && f >= 0.10, "time factor stays bounded");
    CHECK(f <= previous + 1e-12, "time factor never grows with travel time");
    previous = f;

    ItemSnapshot it;
    it.kind = ItemKind::kHealth;
    it.pos = Vec3{0.0, 0.0, -d};
    const double df = DistanceFactor(c.world, it);
    CHECK(df >= 0.65 && df <= 1.0, "distance factor stays in its band");
  }
}

static void TestFreshnessFactor() {
  Ctx c;
  c.Add(ItemKind::kHealth, 0.0, -8.0, 50.0);
  ScoreContext ctx = MakeContext(Prof(), c.world, 0);
  CHECK(FreshnessFactor(ctx, c.items[0]) == 1.0, "a visible item is fully fresh");

  ItemSnapshot stale = c.items[0];
  stale.visible = false;
  double previous = 1.1;
  for (double age = 0.0; age <= 12.0; age += 1.0) {
    stale.staleness_s = age;
    const double f = FreshnessFactor(ctx, stale);
    CHECK(f <= previous + 1e-12, "staleness never increases utility");
    CHECK(f >= 0.40, "staleness is bounded");
    previous = f;
  }
}

static void TestScarcityBounds() {
  Ctx c;
  ScoreContext ctx = MakeContext(Prof(), c.world, 0);
  for (int k = 1; k < static_cast<int>(ItemKind::kCount); ++k) {
    ItemSnapshot it;
    it.kind = static_cast<ItemKind>(k);
    it.weapon_index = k == static_cast<int>(ItemKind::kAmmo) ? 2 : 0;
    const double s = Scarcity(ctx, it);
    CHECK(s >= 0.5 && s <= 1.5, "scarcity stays inside its documented band");
  }
  // Ammo becomes scarcer when pressure rises.
  ItemSnapshot ammo;
  ammo.kind = ItemKind::kAmmo;
  ammo.weapon_index = 2;
  ScoreContext starved = ctx;
  starved.ammo_pressure_frac = 1.0;
  ScoreContext relaxed = ctx;
  relaxed.ammo_pressure_frac = 0.0;
  CHECK(Scarcity(starved, ammo) > Scarcity(relaxed, ammo),
        "ammo scarcity follows the pressure");
}

/* ------------------------------------------------------------------------ */
/* Need terms                                                                */
/* ------------------------------------------------------------------------ */

static void TestArmorNeed() {
  ScoreContext ctx;
  ctx.armor_frac = 1.0;
  CHECK(ArmorNeed(ctx) == 0.0, "full armor has no need");
  ctx.armor_frac = 0.5;
  const double half = ArmorNeed(ctx);
  ctx.armor_frac = 0.0;
  const double empty = ArmorNeed(ctx);
  CHECK(half > 0.0 && empty > half, "armor need grows as armor drops");
  CHECK(empty < 1.0, "armor need stays below the health ceiling by design");
}

static void TestAmmoNeed() {
  Ctx c;
  c.world.self.owned_weapons = 0;
  GrantWeapon(c.world.self, 1);
  GrantWeapon(c.world.self, 2);
  SetAmmo(c.world.self, 2, 0);
  c.Add(ItemKind::kAmmo, 0.0, -5.0, 0.0, 2, 10);
  const ScoreContext ctx = MakeContext(Prof(), c.world, 0);

  CHECK(AmmoNeed(ctx, c.world, 3) == 0.0, "ammo for an unowned weapon is worthless");
  CHECK(AmmoNeed(ctx, c.world, 1) == 0.0, "melee has no ammo need");
  CHECK(AmmoNeed(ctx, c.world, 2) > 0.7, "an empty main weapon is an emergency");
  CHECK(AmmoNeed(ctx, c.world, 99) == 0.0, "an invalid index is harmless");
}

static void TestWeaponNeed() {
  Ctx c;
  c.world.self.owned_weapons = 0;
  GrantWeapon(c.world.self, 1);
  const ScoreContext helpless = MakeContext(Prof(), c.world, 0);
  CHECK(WeaponNeed(helpless, c.world, 4) == 1.0,
        "a bot with only a knife needs any weapon fully");

  Ctx full;
  full.world.self.owned_weapons = 0;
  GrantWeapon(full.world.self, 1);
  GrantWeapon(full.world.self, 12);  // laser
  SetAmmo(full.world.self, 12, 50);
  const ScoreContext armed = MakeContext(Prof(), full.world, 0);
  CHECK(WeaponNeed(armed, full.world, 4) < 0.2,
        "a downgrade is barely worth picking up");
  CHECK(WeaponNeed(armed, full.world, 12) < 0.5,
        "a duplicate of the best weapon is mostly an ammo pickup");
}

/* ------------------------------------------------------------------------ */
/* Personality and mood                                                      */
/* ------------------------------------------------------------------------ */

static void TestAppetiteTables() {
  for (int p = 0; p < kPersonalityCount; ++p) {
    const ItemPersonalityBlock b = PersonalityFor(p);
    const double all[6] = {b.health_appetite, b.armor_appetite, b.ammo_appetite,
                           b.weapon_appetite, b.powerup_appetite, b.strategic_appetite};
    for (double v : all) CHECK(v > 0.0 && v <= 2.0, "appetites stay positive and bounded");
    CHECK(b.caution >= 0.0 && b.caution <= 1.0, "caution is a unit value");
    CHECK(b.aggression >= 0.0 && b.aggression <= 1.0, "aggression is a unit value");
  }
  CHECK(PersonalityFor(1).health_appetite > PersonalityFor(0).health_appetite,
        "survivors want health more than aggressors");
  CHECK(PersonalityFor(3).strategic_appetite > PersonalityFor(1).strategic_appetite,
        "controllers want strategic resources more than survivors");
}

static void TestMood() {
  const ItemProfile normal = Prof(3, 2);
  for (int t = 0; t < 400; t += 7) {
    CHECK(ItemMood(normal, t) == 1.0, "non-flaky personalities have a flat mood");
  }
  const ItemProfile flaky = Prof(3, 5);
  double lo = 2.0, hi = 0.0;
  for (int t = 0; t < 2000; ++t) {
    const double m = ItemMood(flaky, t);
    CHECK(m >= 0.8 && m <= 1.2, "flaky mood stays inside +/-20 %");
    if (m < lo) lo = m;
    if (m > hi) hi = m;
  }
  CHECK(hi - lo > 0.2, "the flaky personality really does swing");
  CHECK(ItemMood(flaky, 123) == ItemMood(flaky, 123), "mood is a pure function");
  const ItemProfile flaky_b = Prof(3, 5);
  ItemProfile flaky_other = flaky_b;
  flaky_other.seed = flaky_b.seed ^ 0x9E37u;
  CHECK(ItemMood(flaky_b, 77) != ItemMood(flaky_other, 77),
        "mood phase is seed bound");
}

/* ------------------------------------------------------------------------ */
/* Determinism helpers                                                       */
/* ------------------------------------------------------------------------ */

static void TestTieBreakDistribution() {
  for (int item = 0; item < 4; ++item) {
    double lo = 2.0, hi = -1.0;
    for (uint32_t seed = 1; seed <= 512; ++seed) {
      const double v = TieBreakUnit(seed * 2654435761u, item, 0);
      CHECK(v >= 0.0 && v < 1.0, "tie-break stays in [0,1)");
      if (v < lo) lo = v;
      if (v > hi) hi = v;
    }
    CHECK(hi - lo > 0.5, "tie-break is spread over its range");
  }
  CHECK(TieBreakUnit(42u, 3, 1) == TieBreakUnit(42u, 3, 1), "tie-break is a pure function");
  CHECK(TieBreakUnit(42u, 3, 0) != TieBreakUnit(42u, 3, 1),
        "different local slots get different tie-breaks");
}

/* ------------------------------------------------------------------------ */
/* Property sweep over pseudo-random worlds                                  */
/* ------------------------------------------------------------------------ */

static uint32_t NextRandom(uint32_t* state) {
  *state = (*state) * 1664525u + 1013904223u;
  return *state;
}

static double Unit(uint32_t* state) {
  return static_cast<double>(NextRandom(state) >> 8) / 16777216.0;
}

static void TestPropertySweep() {
  uint32_t rng = 0xC0FFEE01u;
  ItemSnapshot items[kMaxItems];
  double max_seen = 0.0;
  int eligible_seen = 0;
  int sweeps = 4000;

  for (int s = 0; s < sweeps; ++s) {
    const int count = static_cast<int>(Unit(&rng) * 12.0);
    for (int i = 0; i < count; ++i) {
      ItemSnapshot& it = items[i];
      it = ItemSnapshot();
      it.id = i;
      it.kind = static_cast<ItemKind>(1 + static_cast<int>(Unit(&rng) * 6.0));
      it.pos = Vec3{Unit(&rng) * 80.0 - 40.0, Unit(&rng) * 6.0 - 3.0,
                    Unit(&rng) * 80.0 - 40.0};
      it.value = Unit(&rng) * 120.0;
      it.amount = static_cast<int>(Unit(&rng) * 120.0);
      it.visible = Unit(&rng) > 0.35;
      it.staleness_s = Unit(&rng) * 10.0;
      it.reachable = Unit(&rng) > 0.1;
      if (it.kind == ItemKind::kAmmo || it.kind == ItemKind::kWeapon) {
        it.weapon_index = 1 + static_cast<int>(Unit(&rng) * 14.0);
      } else {
        it.weapon_index = 0;
      }
    }

    ItemWorld w;
    w.items = items;
    w.count = count;
    w.self.max_health = 100.0;
    w.self.max_armor = 100.0;
    w.self.health = Unit(&rng) * 100.0;
    w.self.armor = Unit(&rng) * 100.0;
    w.self.move_speed_mps = 4.0 + Unit(&rng) * 12.0;
    w.self.owned_weapons = NextRandom(&rng) & 0x3FFFu;
    for (int i = 0; i <= kWeaponCount; ++i) {
      w.self.ammo[i] = static_cast<int>(Unit(&rng) * 120.0);
    }
    w.threat.visible_enemies = static_cast<int>(Unit(&rng) * 4.0);
    w.threat.nearest_enemy_m = Unit(&rng) * 40.0;
    w.threat.under_fire = Unit(&rng) > 0.6;
    w.threat.target_distance_m = Unit(&rng) * 50.0;
    w.combat.engaged = Unit(&rng) > 0.5;
    w.combat.combat_priority = Unit(&rng);
    w.combat.tick = s;

    const ItemProfile p = Prof(1 + (s % 5), s % kPersonalityCount);
    const ScoreContext ctx = MakeContext(p, w, 0);
    if (ValidateWorld(w) != ValidationError::kOk) continue;

    for (int i = 0; i < count; ++i) {
      const ItemEvaluation e = EvaluateItem(ctx, w, i);
      CHECK(Finite(e.terms.utility), "utility is always finite");
      CHECK(e.terms.utility >= 0.0, "utility is never negative");
      CHECK(e.terms.utility <= 2.0, "utility stays inside its documented bound");
      CHECK(Finite(e.terms.travel_s) && e.terms.travel_s > 0.0, "travel time is finite");
      if (e.eligible) ++eligible_seen;
      if (e.terms.utility > max_seen) max_seen = e.terms.utility;
    }
  }
  std::printf("  property sweep: %d worlds, %d eligible items, max utility %.3f\n",
              sweeps, eligible_seen, max_seen);
  CHECK(eligible_seen > 1000, "the sweep actually exercises eligible items");
  CHECK(max_seen > 0.5, "the sweep reaches high-utility states");
}

int main() {
  std::printf("== item utility layer: scoring-term tests ==\n");
  TestExposure();
  TestThreatFactor();
  TestPriorityFactor();
  TestTimeAndDistanceFactors();
  TestFreshnessFactor();
  TestScarcityBounds();
  TestArmorNeed();
  TestAmmoNeed();
  TestWeaponNeed();
  TestAppetiteTables();
  TestMood();
  TestTieBreakDistribution();
  TestPropertySweep();
  std::printf("SCORING TERMS: %d checks, %d failures\n", g_checks, g_failures);
  if (g_failures == 0) std::printf("SCORING TERMS PASS\n");
  return g_failures == 0 ? 0 : 1;
}
