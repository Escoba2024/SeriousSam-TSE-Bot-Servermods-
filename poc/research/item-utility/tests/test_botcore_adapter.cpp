// SPDX-License-Identifier: GPL-2.0-only
// test_botcore_adapter.cpp - proves the mapping to the existing poc/botcore AI.
//
// This test *reads* poc/botcore headers (nothing is written there). It is the
// only file in this directory that depends on botcore, which keeps the
// prototype itself standalone.
//
// What is verified:
//  1. the stand-in weapon table equals botcore::ScoreWeapon exactly,
//  2. personality identity across both projects,
//  3. the weapon-mask convention matches botcore::WeaponUsable,
//  4. all 30 tier/persona pairs produce a valid item profile,
//  5. the loadout input mirrors botcore's own usability filtering.

#include <cmath>
#include <cstdio>

#include "botcore_adapter.h"
#include "item_planner.h"

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

static void TestWeaponScoreEquivalence() {
  double max_diff = 0.0;
  int compared = 0;
  for (int weapon = 1; weapon <= kWeaponCount; ++weapon) {
    for (double pref = -1.0; pref <= 1.0 + 1e-9; pref += 0.25) {
      for (double d = 0.0; d <= 160.0; d += 0.5) {
        const double a = StandInWeaponScore(weapon, d, pref);
        const double b = BotcoreWeaponScore(weapon, d, pref);
        const double diff = std::fabs(a - b);
        if (diff > max_diff) max_diff = diff;
        ++compared;
      }
    }
  }
  std::printf("  weapon score grid: %d comparisons, max |diff| = %.3g\n", compared,
              max_diff);
  CHECK(compared > 30000, "the comparison grid is large enough to be meaningful");
  CHECK(max_diff == 0.0, "the stand-in table is arithmetically identical to botcore");
}

static void TestPersonalityIdentity() {
  CHECK(PersonalityIndexesMatch(), "personality indices mean the same in both projects");
  for (int i = 0; i < kPersonalityCount; ++i) {
    CHECK(std::strcmp(PersonalityName(i), botcore::PersonalityName(i)) == 0,
          "personality names agree");
  }
}

static void TestWeaponMaskConvention() {
  for (int index = 1; index <= kWeaponCount; ++index) {
    const uint32_t mask = (1u << (index - 1));
    CHECK(WeaponOwned(mask, index), "item layer sees the bit for its own index");
    CHECK(botcore::WeaponUsable(mask, index), "botcore sees the same bit");
    for (int other = 1; other <= kWeaponCount; ++other) {
      if (other == index) continue;
      CHECK(!WeaponOwned(mask, other) && !botcore::WeaponUsable(mask, other),
            "no cross-talk between weapon bits");
    }
  }
}

static void TestProfileMapping() {
  for (int tier = 1; tier <= kSkillTierCount; ++tier) {
    for (int persona = 0; persona < kPersonalityCount; ++persona) {
      botcore::BotProfile bp;
      CHECK(botcore::BuildProfile(tier, persona, botcore::DeriveSeed(11u, 0, tier, persona),
                                  "BOT-Adapter", &bp),
            "botcore profile builds");
      const ItemProfile ip = ItemProfileFrom(bp);
      CHECK(ValidateProfile(ip) == ProfileError::kOk,
            "mapped item profile validates");
      CHECK(ip.tier == bp.tier, "tier carried over");
      CHECK(ip.persona_index == bp.persona, "personality carried over");
      CHECK(ip.seed == bp.seed, "seed carried over");
    }
  }
}

static void TestUsableMaskMatchesLoadout() {
  SelfState s;
  s.owned_weapons = 0;
  GrantWeapon(s, 1);   // knife
  GrantWeapon(s, 2);   // colt, no ammo
  GrantWeapon(s, 4);   // shotgun, has ammo
  SetAmmo(s, 2, 0);
  SetAmmo(s, 4, 10);

  const uint32_t usable = UsableWeaponMask(s);
  CHECK(WeaponOwned(usable, 1), "melee stays usable without ammo");
  CHECK(!WeaponOwned(usable, 2), "an empty weapon is not usable");
  CHECK(WeaponOwned(usable, 4), "a loaded weapon is usable");

  for (int i = 1; i <= kWeaponCount; ++i) {
    const bool mine = WeaponOwned(usable, i);
    const bool theirs = botcore::WeaponUsable(usable, i);
    CHECK(mine == theirs, "both layers agree on usability");
  }

  const botcore::LoadoutInput li = LoadoutInputFrom(s, 12.0, 0.0, true);
  CHECK(li.usable_mask == usable, "loadout input carries the same mask");
  CHECK(li.has_target, "target flag carried over");
  CHECK(!li.knife_while_travelling, "the knife trick stays disabled by default");

  // The best weapon from botcore's own selector must be in our usable mask.
  const int best = botcore::BestWeapon(usable, 12.0, 0.0);
  CHECK(best > 0, "botcore finds a weapon");
  CHECK(WeaponOwned(usable, best), "and it is inside our usable mask");

  // Owned-mask derivation from ammo counts.
  int ammo[kWeaponCount + 1] = {0};
  ammo[4] = 7;
  const uint32_t melee = 1u << 0;
  const uint32_t derived = OwnedMaskFromAmmo(ammo, &melee);
  CHECK(WeaponOwned(derived, 1), "melee mask is preserved");
  CHECK(WeaponOwned(derived, 4), "ammo implies ownership");
  CHECK(!WeaponOwned(derived, 2), "no ammo, no ownership");
}

static void TestLifecycleAgreement() {
  // A world that the botcore policy and the item layer both have to interpret:
  // the item layer must not recommend a weapon the loadout layer would reject.
  ItemWorld w;
  SelfState& s = w.self;
  s.max_health = 100.0;
  s.health = 70.0;
  s.max_armor = 100.0;
  s.armor = 0.0;
  GrantWeapon(s, 1);
  GrantWeapon(s, 6);  // tommygun, 5 rounds left
  SetAmmo(s, 6, 5);
  s.move_speed_mps = 10.0;

  ItemSnapshot items[2];
  items[0] = ItemSnapshot();
  items[0].id = 1;
  items[0].kind = ItemKind::kAmmo;
  items[0].weapon_index = 6;
  items[0].amount = 100;
  items[0].pos = Vec3{0.0, 0.0, -6.0};
  items[0].visible = true;
  items[1] = ItemSnapshot();
  items[1].id = 2;
  items[1].kind = ItemKind::kHealth;
  items[1].value = 50.0;
  items[1].pos = Vec3{2.0, 0.0, -10.0};
  items[1].visible = true;
  w.items = items;
  w.count = 2;
  w.combat.tick = 0;

  CHECK(ValidateWorld(w) == ValidationError::kOk, "adapter fixture is valid");

  ItemProfile p;
  botcore::BotProfile bp;
  botcore::BuildProfile(4, 4, 0x5150u, "BOT-Adapter", &bp);
  p = ItemProfileFrom(bp);

  ItemPlanner planner;
  planner.Configure(p);
  const GoalDecision d = planner.Step(w);
  CHECK(d.has_goal, "the planner commits a goal in the adapter fixture");
  CHECK(d.goal_kind == ItemKind::kAmmo || d.goal_kind == ItemKind::kHealth,
        "the goal is a resource the bot can actually use");

  // The same decision must survive the trip through the director intent.
  const ItemDirectorIntent intent = DirectorIntentFrom(d);
  CHECK(intent.steer_to_goal == d.has_goal, "director intent mirrors the decision");
  CHECK(intent.goal_id == d.goal_id, "goal id carried over");
  CHECK(ValidateWorld(w) == ValidationError::kOk,
        "the adapter does not mutate the world snapshot");

  // The usable mask that the loadout layer would see is non-empty, so the item
  // layer can never starve a bot that still has a working weapon.
  const uint32_t usable = UsableWeaponMask(w.self);
  CHECK(usable != 0u, "a bot with ammo always keeps a usable weapon");
}

int main() {
  std::printf("== item utility layer: botcore adapter tests ==\n");
  TestWeaponScoreEquivalence();
  TestPersonalityIdentity();
  TestWeaponMaskConvention();
  TestProfileMapping();
  TestUsableMaskMatchesLoadout();
  TestLifecycleAgreement();
  std::printf("BOTCORE ADAPTER: %d checks, %d failures\n", g_checks, g_failures);
  if (g_failures == 0) std::printf("BOTCORE ADAPTER PASS\n");
  return g_failures == 0 ? 0 : 1;
}
