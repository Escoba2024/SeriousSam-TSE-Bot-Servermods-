// SPDX-License-Identifier: GPL-2.0-only
// botcore_adapter.h - the integration bridge to poc/botcore.
//
// STATUS: integration preparation, NOT part of the qualified build. Nothing in
// this repository calls this header yet. It exists so that the item layer can
// be wired into the existing human-AI path with a *mapping*, not a rewrite:
//
//   botcore::BotProfile           -> itemai::ItemProfile          (ItemProfileFrom)
//   replicated world / ammo mask  -> itemai::SelfState           (SelfStateFrom)
//   itemai::SelfState             -> botcore usable-weapon mask  (UsableWeaponMask)
//   itemai::ItemWorld             -> botcore::LoadoutInput       (LoadoutInputFrom)
//   itemai weapon score           -> botcore::ScoreWeapon        (see below)
//
// WHAT THIS HEADER PROVES (tested by test_botcore_adapter.cpp)
//  1. The stand-in weapon table in item_weapons.h is arithmetically identical
//     to botcore::ScoreWeapon over a full distance/preference grid. Swapping
//     the function therefore cannot change any decision - it only removes a
//     duplicated table.
//  2. Personality indices 0..5 mean the same six things in both projects.
//  3. The weapon mask convention (bit index-1) matches botcore::WeaponUsable.
//  4. Every botcore tier/persona pair yields a valid item profile.
//
// WHAT IT DELIBERATELY DOES NOT DO
//  * no engine access, no CPlayerAction, no BotDriver call,
//  * no navigation and no ray casting,
//  * no change to any file outside poc/research/item-utility/.

#ifndef ITEMAI_BOTCORE_ADAPTER_H
#define ITEMAI_BOTCORE_ADAPTER_H

#include <cstdint>
#include <cstring>

#include "item_planner.h"
#include "item_profile.h"
#include "item_snapshot.h"
#include "item_types.h"
#include "item_weapons.h"

#include "../../../botcore/bot_loadout.h"
#include "../../../botcore/bot_profile.h"

namespace itemai {

/* ------------------------------------------------------------------------ */
/* Weapon scoring hand-over                                                  */
/* ------------------------------------------------------------------------ */

// Replace itemai::StandInWeaponScore with this at integration time. Both
// functions have the same contract and the same numbers; the adapter test
// asserts equality, so this is a rename, not a behaviour change.
inline double BotcoreWeaponScore(int weapon_index, double distance_m,
                                 double range_preference) {
  return botcore::ScoreWeapon(weapon_index, distance_m, range_preference);
}

/* ------------------------------------------------------------------------ */
/* Profile mapping                                                           */
/* ------------------------------------------------------------------------ */

// botcore tier 1..5 and persona 0..5 map one-to-one. The item layer keeps its
// own tuning tables instead of copying botcore's, so both layers stay
// independently tunable; only the *identity* is shared.
inline bool PersonalityIndexesMatch() {
  for (int i = 0; i < kPersonalityCount; ++i) {
    if (std::strcmp(PersonalityName(i), botcore::PersonalityName(i)) != 0) {
      return false;
    }
  }
  return true;
}

inline ItemProfile ItemProfileFrom(const botcore::BotProfile& bp) {
  ItemProfile p;
  // The botcore seed is per-bot and never shared, so it is a good tie-break
  // stream as well.
  BuildItemProfile(bp.tier, bp.persona, bp.seed, &p);
  return p;
}

/* ------------------------------------------------------------------------ */
/* Snapshot mapping                                                          */
/* ------------------------------------------------------------------------ */

// botcore::WorldView.usable_weapons is already "after ammo filtering"; the item
// layer wants the *owned* mask plus per-weapon ammo, so that it can reason
// about refills. This helper derives the owned mask from the ammo counts the
// caller has: index 1..14 with a positive count or a melee weapon.
inline uint32_t OwnedMaskFromAmmo(const int* ammo_by_index,
                                  const uint32_t* melee_mask = nullptr) {
  uint32_t mask = 0;
  if (melee_mask != nullptr) mask |= *melee_mask;
  if (ammo_by_index != nullptr) {
    for (int i = 1; i <= kWeaponCount; ++i) {
      if (ammo_by_index[i] > 0) mask |= (1u << (i - 1));
    }
  }
  return mask;
}

// Usable = owned and (needs no ammo or has ammo). Mirrors the filtering that
// BotDriver already performs before calling the policy.
inline uint32_t UsableWeaponMask(const SelfState& s) {
  uint32_t mask = 0;
  for (int i = 1; i <= kWeaponCount; ++i) {
    if (!WeaponOwned(s.owned_weapons, i)) continue;
    if (!WeaponHasAmmo(s.ammo, i)) continue;
    mask |= (1u << (i - 1));
  }
  return mask;
}

// The loadout layer's view of the same world, so the item layer can reuse
// botcore's hysteresis and the bot never picks a weapon it cannot fire.
inline botcore::LoadoutInput LoadoutInputFrom(const SelfState& s,
                                              double distance_m,
                                              double range_preference,
                                              bool has_target) {
  botcore::LoadoutInput li;
  li.usable_mask = UsableWeaponMask(s);
  li.distance_m = distance_m;
  li.range_preference = range_preference;
  li.has_target = has_target;
  li.knife_while_travelling = false;
  return li;
}

/* ------------------------------------------------------------------------ */
/* Decision mapping                                                          */
/* ------------------------------------------------------------------------ */

// What the BotDriver needs to do with a planner decision, expressed without any
// engine type. The integration layer turns this into movement/aim intents; the
// item layer never writes a CPlayerAction itself.
struct ItemDirectorIntent {
  bool steer_to_goal = false;   // navigation should follow the goal
  bool suppress_combat = false; // combat movement must yield this tick
  int goal_id = -1;
  Vec3 goal_pos{};
  ItemAction action = ItemAction::kNone;
  ItemReason reason = ItemReason::kNone;
};

inline ItemDirectorIntent DirectorIntentFrom(const GoalDecision& d) {
  ItemDirectorIntent i;
  i.goal_id = d.goal_id;
  i.goal_pos = d.goal_pos;
  i.action = d.action;
  i.reason = d.reason;
  i.steer_to_goal = d.has_goal;
  i.suppress_combat = d.has_goal && d.suppress_combat;
  return i;
}

}  // namespace itemai

#endif  // ITEMAI_BOTCORE_ADAPTER_H
