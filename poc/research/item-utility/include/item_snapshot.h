// SPDX-License-Identifier: GPL-2.0-only
// item_snapshot.h - synthetic, validated world snapshot for the item layer.
//
// DESIGN RULES
//  1. The decision layer never dereferences an engine pointer. Everything it
//     knows arrives in these plain structs, filled by the caller (BotDriver
//     integration) or by a test fixture.
//  2. Validation is fail-closed: a snapshot with a NaN, a negative value, an
//     out-of-range weapon index or a duplicate/negative id is rejected and the
//     planner returns "no goal" instead of guessing.
//  3. `visible` means "confirmed line of sight in this tick". `staleness_s`
//     says how old a non-visible observation is. Both are caller facts, never
//     inferred here - this layer casts no rays.
//  4. `value`/`amount` are already converted to game units by the caller
//     (health points, armor points, ammo units). `kPowerup`/`kStrategic`
//     use `value` as a normalised 0..1 usefulness supplied by the caller.

#ifndef ITEMAI_ITEM_SNAPSHOT_H
#define ITEMAI_ITEM_SNAPSHOT_H

#include <cmath>
#include <cstdint>

#include "item_types.h"
#include "item_weapons.h"

namespace itemai {

/* ------------------------------------------------------------------------ */
/* One item as the client can currently know it                              */
/* ------------------------------------------------------------------------ */

struct ItemSnapshot {
  int id = -1;                    // stable per world instance, >= 0
  ItemKind kind = ItemKind::kNone;
  int weapon_index = 0;           // 1..14 for kAmmo/kWeapon, else 0
  Vec3 pos{};
  double value = 0.0;             // health/armor points, or 0..1 usefulness
  int amount = 0;                 // ammo units for kAmmo (0 = use `value`)
  double respawn_s = 0.0;         // >0 = not there yet
  bool visible = false;           // fresh line of sight this tick
  bool reachable = true;          // coarse caller hint, false = blacklisted
  double staleness_s = 0.0;       // age of the last observation
};

/* ------------------------------------------------------------------------ */
/* Own state                                                                 */
/* ------------------------------------------------------------------------ */

struct SelfState {
  Vec3 eye{};
  double health = 100.0;
  double max_health = 100.0;
  double armor = 0.0;
  double max_armor = 100.0;
  uint32_t owned_weapons = 0;     // bit (index-1), mirrored from
                                  // CPlayerWeapons::m_iAvailableWeapons
  int ammo[kWeaponCount + 1] = {0};  // 1..14, 0 = none
  double move_speed_mps = kDefaultMoveSpeedMps;  // caller's current speed
};

// Small helper so callers do not have to remember the offset.
inline void SetAmmo(SelfState& s, int weapon_index, int amount) {
  if (weapon_index >= 1 && weapon_index <= kWeaponCount) {
    s.ammo[weapon_index] = amount < 0 ? 0 : amount;
  }
}

inline void GrantWeapon(SelfState& s, int weapon_index) {
  if (weapon_index >= 1 && weapon_index <= kWeaponCount) {
    s.owned_weapons |= (1u << (weapon_index - 1));
  }
}

/* ------------------------------------------------------------------------ */
/* Threat / combat context (produced by the combat layer)                    */
/* ------------------------------------------------------------------------ */

struct ThreatState {
  int visible_enemies = 0;
  double nearest_enemy_m = -1.0;   // <0 = unknown / none
  bool under_fire = false;         // damage inside the alert window
  double seconds_since_damage = 999.0;
  bool target_visible = false;
  double target_distance_m = -1.0; // used for weapon valuation
  double incoming_dps = 0.0;       // optional estimate, 0 = unknown
};

struct CombatContext {
  int tick = 0;                   // 20 Hz tick of the caller
  double combat_priority = 0.0;   // 0 = idle .. 1 = committed fight
  bool engaged = false;
};

/* ------------------------------------------------------------------------ */
/* Aggregate world view                                                      */
/* ------------------------------------------------------------------------ */

struct ItemWorld {
  const ItemSnapshot* items = nullptr;
  int count = 0;
  SelfState self{};
  ThreatState threat{};
  CombatContext combat{};
};

/* ------------------------------------------------------------------------ */
/* Validation (fail closed)                                                  */
/* ------------------------------------------------------------------------ */

enum class ValidationError : uint8_t {
  kOk = 0,
  kNullItems,
  kCountOutOfRange,
  kBadItemId,
  kDuplicateItemId,
  kBadKind,
  kNonFinite,
  kNegativeValue,
  kNegativeRespawn,
  kWeaponIndexOutOfRange,
  kBadSelf,
  kBadThreat,
  kBadCombat
};

inline const char* ValidationErrorName(ValidationError e) {
  switch (e) {
    case ValidationError::kOk: return "ok";
    case ValidationError::kNullItems: return "null-items";
    case ValidationError::kCountOutOfRange: return "count-out-of-range";
    case ValidationError::kBadItemId: return "bad-item-id";
    case ValidationError::kDuplicateItemId: return "duplicate-item-id";
    case ValidationError::kBadKind: return "bad-kind";
    case ValidationError::kNonFinite: return "non-finite";
    case ValidationError::kNegativeValue: return "negative-value";
    case ValidationError::kNegativeRespawn: return "negative-respawn";
    case ValidationError::kWeaponIndexOutOfRange: return "weapon-index";
    case ValidationError::kBadSelf: return "bad-self";
    case ValidationError::kBadThreat: return "bad-threat";
    case ValidationError::kBadCombat: return "bad-combat";
    default: return "?";
  }
}

inline ValidationError ValidateItem(const ItemSnapshot& it) {
  if (it.id < 0) return ValidationError::kBadItemId;
  const int kind = static_cast<int>(it.kind);
  if (kind <= 0 || kind >= static_cast<int>(ItemKind::kCount)) {
    return ValidationError::kBadKind;
  }
  if (!Finite(it.pos.x) || !Finite(it.pos.y) || !Finite(it.pos.z) ||
      !Finite(it.value) || !Finite(it.respawn_s) || !Finite(it.staleness_s)) {
    return ValidationError::kNonFinite;
  }
  if (it.value < 0.0) return ValidationError::kNegativeValue;
  if (it.respawn_s < 0.0) return ValidationError::kNegativeRespawn;
  if (it.staleness_s < 0.0) return ValidationError::kNonFinite;
  if (it.amount < 0) return ValidationError::kNegativeValue;
  if (it.weapon_index < 0 || it.weapon_index > kWeaponCount) {
    return ValidationError::kWeaponIndexOutOfRange;
  }
  if ((it.kind == ItemKind::kAmmo || it.kind == ItemKind::kWeapon) &&
      it.weapon_index == 0) {
    return ValidationError::kWeaponIndexOutOfRange;
  }
  return ValidationError::kOk;
}

inline ValidationError ValidateWorld(const ItemWorld& w) {
  if (w.count < 0 || w.count > kMaxItems) return ValidationError::kCountOutOfRange;
  if (w.count > 0 && w.items == nullptr) return ValidationError::kNullItems;
  for (int i = 0; i < w.count; ++i) {
    const ValidationError e = ValidateItem(w.items[i]);
    if (e != ValidationError::kOk) return e;
    for (int j = 0; j < i; ++j) {
      if (w.items[j].id == w.items[i].id) return ValidationError::kDuplicateItemId;
    }
  }

  const SelfState& s = w.self;
  if (!Finite(s.eye.x) || !Finite(s.eye.y) || !Finite(s.eye.z) ||
      !Finite(s.health) || !Finite(s.max_health) || !Finite(s.armor) ||
      !Finite(s.max_armor) || !Finite(s.move_speed_mps)) {
    return ValidationError::kBadSelf;
  }
  if (s.max_health <= 0.0 || s.max_armor < 0.0 || s.health < 0.0 ||
      s.health > s.max_health || s.armor < 0.0 || s.armor > s.max_armor ||
      s.move_speed_mps <= 0.0) {
    return ValidationError::kBadSelf;
  }
  for (int i = 0; i <= kWeaponCount; ++i) {
    if (s.ammo[i] < 0) return ValidationError::kBadSelf;
  }

  const ThreatState& t = w.threat;
  if (!Finite(t.nearest_enemy_m) || !Finite(t.seconds_since_damage) ||
      !Finite(t.target_distance_m) || !Finite(t.incoming_dps)) {
    return ValidationError::kBadThreat;
  }
  if (t.visible_enemies < 0 || t.visible_enemies > 32 || t.incoming_dps < 0.0) {
    return ValidationError::kBadThreat;
  }

  const CombatContext& c = w.combat;
  if (c.tick < 0 || !Finite(c.combat_priority) || c.combat_priority < 0.0 ||
      c.combat_priority > 1.0) {
    return ValidationError::kBadCombat;
  }
  return ValidationError::kOk;
}

/* ------------------------------------------------------------------------ */
/* Self assessment shared by scoring and telemetry                           */
/* ------------------------------------------------------------------------ */

struct SelfAssessment {
  double health_frac = 1.0;
  double armor_frac = 0.0;
  int best_weapon = 0;              // best owned weapon at the reference range
  double best_weapon_score = 0.0;
  int usable_weapons = 0;           // owned AND has ammo (or needs none)
  bool ammunition_starved = false;  // owned ranged weapons exist, none usable
  int starved_mask = 0;             // owned ranged weapons without ammo
  double reference_distance_m = 20.0;
};

// Distance used to value weapons when no enemy is known: the profile's
// preferred engagement range, or a neutral mid-range default.
inline double ReferenceDistance(const ItemWorld& w) {
  if (w.threat.target_distance_m > 0.0) return w.threat.target_distance_m;
  if (w.threat.nearest_enemy_m > 0.0) return w.threat.nearest_enemy_m;
  return 20.0;
}

inline SelfAssessment AssessSelf(const ItemWorld& w, double range_preference) {
  SelfAssessment a;
  const SelfState& s = w.self;
  a.health_frac = s.max_health > 0.0 ? Clamp01(s.health / s.max_health) : 0.0;
  a.armor_frac = s.max_armor > 0.0 ? Clamp01(s.armor / s.max_armor) : 0.0;
  a.reference_distance_m = ReferenceDistance(w);

  for (int i = 1; i <= kWeaponCount; ++i) {
    if (!WeaponOwned(s.owned_weapons, i)) continue;
    if (!WeaponHasAmmo(s.ammo, i)) {
      if (WeaponNeedsAmmo(i)) {
        a.starved_mask |= (1 << i);
        a.ammunition_starved = true;
      }
      continue;
    }
    ++a.usable_weapons;
    const double score = StandInWeaponScore(i, a.reference_distance_m, range_preference);
    if (score > a.best_weapon_score) {
      a.best_weapon_score = score;
      a.best_weapon = i;
    }
  }
  // Knife owns no ammo and is always available in a deathmatch spawn; it is
  // therefore "usable" but never counts as a real ranged weapon.
  if (a.best_weapon == 0 && WeaponOwned(s.owned_weapons, 1)) {
    a.best_weapon = 1;
    a.best_weapon_score = StandInWeaponScore(1, a.reference_distance_m, range_preference);
  }
  if (a.usable_weapons > 0 && a.best_weapon == 1) {
    // Only melee left: treat as starved for ranged purposes.
    a.ammunition_starved = true;
  }
  return a;
}

}  // namespace itemai

#endif  // ITEMAI_ITEM_SNAPSHOT_H
