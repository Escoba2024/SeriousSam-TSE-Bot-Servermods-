// SPDX-License-Identifier: GPL-2.0-only
// itemai_mirror.h - exact contract-compatible mirror of PR #55
// (poc/research/item-utility, commit 72d464ff501d90ec4b69c2a131a50a06323e1909).
//
// PURPOSE
//  PR #55 is an open sibling PR and is not yet merged into `main`. Because our
//  exclusive write scope is strictly `poc/research/nav-item-bridge/**` and
//  `docs/research/nav-item-bridge/**`, we do not copy files into
//  `poc/research/item-utility/`.
//  `upstream_seams.h` automatically includes the real
//  `poc/research/item-utility/include/*.h` whenever PR #55 is present in the
//  checkout (or on the `-I` include path) and falls back to this mirror ONLY
//  when building standalone on `main`.

#ifndef NAV_ITEM_BRIDGE_UPSTREAM_ITEMAI_MIRROR_H
#define NAV_ITEM_BRIDGE_UPSTREAM_ITEMAI_MIRROR_H

#include <cmath>
#include <cstdint>
#include <cstdio>
#include <cstring>

#include "../../../../botcore/bot_loadout.h"
#include "../../../../botcore/bot_profile.h"

/* ======================================================================== */
/* item_types.h                                                             */
/* ======================================================================== */

#ifndef ITEMAI_ITEM_TYPES_H
#define ITEMAI_ITEM_TYPES_H

namespace itemai {

constexpr int kMaxItems = 64;
constexpr int kWeaponCount = 14;
constexpr int kMaxWeaponIndex = kWeaponCount;

constexpr double kTickHz = 20.0;
constexpr double kTickQuantum = 1.0 / kTickHz;
constexpr double kDefaultMoveSpeedMps = 10.0;

constexpr double kArrivalRadiusM = 1.5;
constexpr double kNeedEpsilon = 0.02;

inline double Clamp(double v, double lo, double hi) {
  return v < lo ? lo : (v > hi ? hi : v);
}

inline double Clamp01(double v) { return Clamp(v, 0.0, 1.0); }

inline bool Finite(double v) { return std::isfinite(v); }

inline int TickFromSeconds(double s) {
  if (!(s > 0.0)) return 0;
  return static_cast<int>(s * kTickHz + 0.5);
}

inline double SecondsFromTicks(int ticks) {
  return static_cast<double>(ticks) / kTickHz;
}

inline uint32_t Hash32(uint32_t x) {
  x += 0x9E3779B9u;
  x ^= x >> 16;
  x *= 0x7FEB352Du;
  x ^= x >> 15;
  x *= 0x846CA68Bu;
  x ^= x >> 16;
  return x;
}

inline double TieBreakUnit(uint32_t seed, int item_id, int slot) {
  const uint32_t h = Hash32(seed ^ (static_cast<uint32_t>(item_id) * 0x85EBCA6Bu) ^
                            (static_cast<uint32_t>(slot + 1) * 0xC2B2AE35u));
  return static_cast<double>(h & 0xFFFFFFu) / 16777215.0;
}

struct Vec3 {
  double x = 0.0;
  double y = 0.0;
  double z = 0.0;
};

inline double Distance(const Vec3& a, const Vec3& b) {
  const double dx = a.x - b.x;
  const double dy = a.y - b.y;
  const double dz = a.z - b.z;
  return std::sqrt(dx * dx + dy * dy + dz * dz);
}

enum class ItemKind : uint8_t {
  kNone = 0,
  kHealth = 1,
  kArmor = 2,
  kAmmo = 3,
  kWeapon = 4,
  kPowerup = 5,
  kStrategic = 6,
  kCount = 7
};

inline const char* ItemKindName(ItemKind k) {
  switch (k) {
    case ItemKind::kHealth: return "health";
    case ItemKind::kArmor: return "armor";
    case ItemKind::kAmmo: return "ammo";
    case ItemKind::kWeapon: return "weapon";
    case ItemKind::kPowerup: return "powerup";
    case ItemKind::kStrategic: return "strategic";
    default: return "none";
  }
}

enum class ItemAction : uint8_t {
  kNone = 0,
  kSelect = 1,
  kKeep = 2,
  kSwitch = 3,
  kAbort = 4,
  kReached = 5
};

enum class ItemReason : uint8_t {
  kNone = 0,
  kNoCandidate,
  kSelected,
  kKept,
  kSwitched,
  kReached,
  kNeedSatisfied,
  kItemGone,
  kThreatOverride,
  kDamageAbort,
  kTimeout,
  kOutOfRange,
  kCooldown,
  kCombatLock,
  kHysteresisHold,
  kUnreachable,
  kInvalidWorld,
  kAmmoStarved,
  kStalled
};

inline const char* ItemActionName(ItemAction a) {
  switch (a) {
    case ItemAction::kNone: return "none";
    case ItemAction::kSelect: return "select";
    case ItemAction::kKeep: return "keep";
    case ItemAction::kSwitch: return "switch";
    case ItemAction::kAbort: return "abort";
    case ItemAction::kReached: return "reached";
    default: return "?";
  }
}

inline const char* ItemReasonName(ItemReason r) {
  switch (r) {
    case ItemReason::kNoCandidate: return "no-candidate";
    case ItemReason::kSelected: return "selected";
    case ItemReason::kKept: return "kept";
    case ItemReason::kSwitched: return "switched";
    case ItemReason::kReached: return "reached";
    case ItemReason::kNeedSatisfied: return "need-satisfied";
    case ItemReason::kItemGone: return "item-gone";
    case ItemReason::kThreatOverride: return "threat-override";
    case ItemReason::kDamageAbort: return "damage-abort";
    case ItemReason::kTimeout: return "timeout";
    case ItemReason::kOutOfRange: return "out-of-range";
    case ItemReason::kCooldown: return "cooldown";
    case ItemReason::kCombatLock: return "combat-lock";
    case ItemReason::kHysteresisHold: return "hysteresis-hold";
    case ItemReason::kUnreachable: return "unreachable";
    case ItemReason::kInvalidWorld: return "invalid-world";
    case ItemReason::kAmmoStarved: return "ammo-starved";
    case ItemReason::kStalled: return "stalled";
    default: return "none";
  }
}

}  // namespace itemai

#endif  // ITEMAI_ITEM_TYPES_H

/* ======================================================================== */
/* item_weapons.h                                                           */
/* ======================================================================== */

#ifndef ITEMAI_ITEM_WEAPONS_H
#define ITEMAI_ITEM_WEAPONS_H

namespace itemai {

struct WeaponTraits {
  int index = 0;
  double min_m = 0.0;
  double max_m = 0.0;
  double dps_rel = 1.0;
  double acc_near = 0.8;
  double acc_far = 0.5;
  int ammo_cap = 0;
  double self_blast_m = 0.0;
};

inline const WeaponTraits& WeaponTraitAt(int index) {
  static const WeaponTraits kTable[kWeaponCount] = {
      {1, 0.0, 3.5, 1.0, 0.95, 0.20, 0, 0.0},
      {2, 0.0, 45.0, 1.6, 0.92, 0.55, 50, 0.0},
      {3, 0.0, 40.0, 2.0, 0.88, 0.45, 50, 0.0},
      {4, 0.0, 22.0, 3.9, 0.85, 0.25, 30, 0.0},
      {5, 0.0, 18.0, 5.5, 0.80, 0.15, 30, 0.0},
      {6, 0.0, 60.0, 3.2, 0.93, 0.72, 100, 0.0},
      {7, 0.0, 90.0, 3.4, 0.90, 0.62, 200, 0.0},
      {8, 12.0, 70.0, 5.0, 0.70, 0.55, 10, 5.0},
      {9, 10.0, 55.0, 3.8, 0.45, 0.30, 10, 5.0},
      {10, 0.0, 3.0, 1.2, 0.95, 0.20, 0, 0.0},
      {11, 0.0, 14.0, 3.4, 0.90, 0.35, 100, 0.0},
      {12, 0.0, 80.0, 4.4, 0.85, 0.70, 50, 0.0},
      {13, 20.0, 150.0, 5.2, 0.55, 0.97, 20, 0.0},
      {14, 14.0, 90.0, 5.6, 0.60, 0.70, 15, 4.0},
  };
  if (index < 1) index = 1;
  if (index > kWeaponCount) index = kWeaponCount;
  return kTable[index - 1];
}

inline int WeaponAmmoCap(int index) {
  if (index < 1 || index > kWeaponCount) return 0;
  return WeaponTraitAt(index).ammo_cap;
}

inline bool WeaponNeedsAmmo(int index) { return WeaponAmmoCap(index) > 0; }

inline bool WeaponHasAmmo(const int* ammo_by_index, int index) {
  if (ammo_by_index == nullptr) return false;
  if (index < 1 || index > kWeaponCount) return false;
  if (!WeaponNeedsAmmo(index)) return true;
  return ammo_by_index[index] > 0;
}

inline bool WeaponOwned(uint32_t owned_mask, int index) {
  return index >= 1 && index <= kWeaponCount &&
         (owned_mask & (1u << (index - 1))) != 0u;
}

inline double AccuracyAt(const WeaponTraits& w, double distance_m) {
  if (distance_m <= w.min_m) return w.acc_near;
  if (distance_m >= w.max_m) return w.acc_far;
  const double span = w.max_m - w.min_m;
  const double t = span > 1e-6 ? (distance_m - w.min_m) / span : 0.0;
  return w.acc_near + (w.acc_far - w.acc_near) * t;
}

inline double RangeFit(const WeaponTraits& w, double distance_m) {
  if (distance_m < w.min_m) {
    const double d = w.min_m - distance_m;
    return d >= 8.0 ? 0.0 : 1.0 - d / 8.0;
  }
  if (distance_m > w.max_m) {
    const double d = distance_m - w.max_m;
    const double falloff = w.max_m * 0.25 + 4.0;
    return d >= falloff ? 0.0 : 1.0 - d / falloff;
  }
  return 1.0;
}

inline double StandInWeaponScore(int index, double distance_m,
                                 double range_preference) {
  if (index < 1 || index > kWeaponCount || !Finite(distance_m)) return 0.0;
  const WeaponTraits& w = WeaponTraitAt(index);
  double score = w.dps_rel * AccuracyAt(w, distance_m) * RangeFit(w, distance_m);
  if (w.self_blast_m > 0.0 && distance_m < w.self_blast_m) score *= 0.05;
  double pos = (distance_m - 12.0) / 30.0;
  pos = Clamp(pos, -1.0, 1.0);
  const double tilt = 1.0 + 0.35 * range_preference * pos;
  return score * (tilt > 0.2 ? tilt : 0.2);
}

}  // namespace itemai

#endif  // ITEMAI_ITEM_WEAPONS_H

/* ======================================================================== */
/* item_snapshot.h                                                          */
/* ======================================================================== */

#ifndef ITEMAI_ITEM_SNAPSHOT_H
#define ITEMAI_ITEM_SNAPSHOT_H

namespace itemai {

struct ItemSnapshot {
  int id = -1;
  ItemKind kind = ItemKind::kNone;
  int weapon_index = 0;
  Vec3 pos{};
  double value = 0.0;
  int amount = 0;
  double respawn_s = 0.0;
  bool visible = false;
  bool reachable = true;
  double staleness_s = 0.0;
};

struct SelfState {
  Vec3 eye{};
  double health = 100.0;
  double max_health = 100.0;
  double armor = 0.0;
  double max_armor = 100.0;
  uint32_t owned_weapons = 0;
  int ammo[kWeaponCount + 1] = {0};
  double move_speed_mps = kDefaultMoveSpeedMps;
};

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

struct ThreatState {
  int visible_enemies = 0;
  double nearest_enemy_m = -1.0;
  bool under_fire = false;
  double seconds_since_damage = 999.0;
  bool target_visible = false;
  double target_distance_m = -1.0;
  double incoming_dps = 0.0;
};

struct CombatContext {
  int tick = 0;
  double combat_priority = 0.0;
  bool engaged = false;
};

struct ItemWorld {
  const ItemSnapshot* items = nullptr;
  int count = 0;
  SelfState self{};
  ThreatState threat{};
  CombatContext combat{};
};

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

struct SelfAssessment {
  double health_frac = 1.0;
  double armor_frac = 0.0;
  int best_weapon = 0;
  double best_weapon_score = 0.0;
  int usable_weapons = 0;
  bool ammunition_starved = false;
  int starved_mask = 0;
  double reference_distance_m = 20.0;
};

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
  if (a.best_weapon == 0 && WeaponOwned(s.owned_weapons, 1)) {
    a.best_weapon = 1;
    a.best_weapon_score = StandInWeaponScore(1, a.reference_distance_m, range_preference);
  }
  if (a.usable_weapons > 0 && a.best_weapon == 1) {
    a.ammunition_starved = true;
  }
  return a;
}

}  // namespace itemai

#endif  // ITEMAI_ITEM_SNAPSHOT_H

/* ======================================================================== */
/* item_profile.h                                                           */
/* ======================================================================== */

#ifndef ITEMAI_ITEM_PROFILE_H
#define ITEMAI_ITEM_PROFILE_H

namespace itemai {

constexpr int kSkillTierCount = 5;
constexpr int kPersonalityCount = 6;

struct ItemSkillBlock {
  int tier = 3;
  double planning_horizon_s = 6;
  double risk_awareness = 0.65;
  double discipline = 0.62;
  double tie_noise = 0.009;
};

struct ItemPersonalityBlock {
  double health_appetite = 1.0;
  double armor_appetite = 1.0;
  double ammo_appetite = 1.0;
  double weapon_appetite = 1.0;
  double powerup_appetite = 1.0;
  double strategic_appetite = 1.0;
  double caution = 0.5;
  double aggression = 0.5;
};

struct ItemTuning {
  double commit_margin = 0.20;
  double min_commit_s = 1.2;
  double search_cooldown_s = 1.8;
  double abort_cooldown_s = 1.4;
  double abort_damage_frac = 0.34;
  double damage_window_s = 2.0;
  double enemy_abort_radius_m = 18.0;
  double health_abort_frac = 0.55;
  double max_search_time_s = 8.0;
  double min_utility = 0.12;
  double threat_weight = 0.65;
  double time_weight = 0.55;
  double deviation_weight = 0.55;
  double combat_lock_priority = 0.80;
  double close_finish_radius_m = 2.5;
  double memory_horizon_s = 6.0;
  double weapon_reference_m = 20.0;
  double consumable_blacklist_s = 30.0;
};

struct ItemProfile {
  ItemSkillBlock skill;
  ItemPersonalityBlock persona;
  ItemTuning tuning;
  uint32_t seed = 1u;
  int tier = 3;
  int persona_index = 0;
};

inline ItemSkillBlock SkillFor(int tier) {
  static const double kHorizon[kSkillTierCount] = {2.5, 4.0, 6.0, 9.0, 13.0};
  static const double kRisk[kSkillTierCount] = {0.35, 0.50, 0.65, 0.80, 0.95};
  static const double kDisc[kSkillTierCount] = {0.30, 0.45, 0.62, 0.78, 0.90};
  static const double kNoise[kSkillTierCount] = {0.020, 0.014, 0.009, 0.005, 0.002};
  if (tier < 1) tier = 1;
  if (tier > kSkillTierCount) tier = kSkillTierCount;
  ItemSkillBlock s;
  s.tier = tier;
  s.planning_horizon_s = kHorizon[tier - 1];
  s.risk_awareness = kRisk[tier - 1];
  s.discipline = kDisc[tier - 1];
  s.tie_noise = kNoise[tier - 1];
  return s;
}

inline ItemPersonalityBlock PersonalityFor(int persona) {
  static const ItemPersonalityBlock kTable[kPersonalityCount] = {
      {0.75, 0.80, 1.10, 1.25, 1.10, 0.70, 0.25, 0.90},
      {1.45, 1.30, 1.00, 0.90, 0.80, 0.90, 0.85, 0.35},
      {1.00, 1.00, 1.05, 1.05, 1.00, 0.80, 0.50, 0.65},
      {1.00, 1.00, 0.95, 0.95, 1.00, 1.30, 0.60, 0.45},
      {0.95, 1.05, 1.20, 1.15, 0.90, 0.85, 0.60, 0.50},
      {1.00, 1.00, 1.00, 1.00, 1.00, 1.00, 0.50, 0.60},
  };
  if (persona < 0) persona = 0;
  if (persona >= kPersonalityCount) persona = kPersonalityCount - 1;
  return kTable[persona];
}

inline const char* PersonalityName(int persona) {
  static const char* kNames[kPersonalityCount] = {
      "aggressor", "survivor", "duelist", "controller", "marksman", "flaky"};
  if (persona < 0 || persona >= kPersonalityCount) return "?";
  return kNames[persona];
}

inline ItemTuning TuningFor(const ItemSkillBlock& s, const ItemPersonalityBlock& p) {
  ItemTuning t;
  t.commit_margin = Clamp(0.12 + 0.18 * p.caution + 0.10 * (1.0 - s.discipline),
                          0.10, 0.45);
  t.min_commit_s = Clamp(1.60 - 0.90 * s.discipline + 0.40 * p.caution, 0.40, 2.60);
  t.search_cooldown_s = Clamp(2.50 - 1.00 * s.discipline, 1.00, 3.00);
  t.abort_cooldown_s = Clamp(0.90 + 1.10 * p.caution, 0.80, 2.20);
  t.abort_damage_frac = Clamp(0.42 - 0.18 * p.caution, 0.20, 0.45);
  t.enemy_abort_radius_m = Clamp(12.0 + 12.0 * p.caution, 10.0, 26.0);
  t.health_abort_frac = Clamp(0.70 - 0.30 * p.caution, 0.35, 0.75);
  t.max_search_time_s = Clamp(0.65 * s.planning_horizon_s * (1.0 - 0.25 * p.caution),
                              2.5, 20.0);
  t.min_utility = Clamp(0.12 + 0.04 * p.caution, 0.10, 0.20);
  t.threat_weight = Clamp(0.55 + 0.30 * p.caution, 0.50, 0.90);
  t.time_weight = 0.55;
  t.deviation_weight = Clamp(0.35 + 0.40 * s.discipline, 0.35, 0.80);
  t.combat_lock_priority = Clamp(0.92 - 0.25 * p.aggression, 0.60, 0.92);
  t.close_finish_radius_m = 2.5;
  t.memory_horizon_s = s.planning_horizon_s;
  t.weapon_reference_m = 20.0;
  t.consumable_blacklist_s = 30.0;
  return t;
}

enum class ProfileError : uint8_t {
  kOk = 0,
  kTierOutOfRange,
  kPersonalityOutOfRange,
  kSeedZero,
  kNonFinite,
  kOutOfRange
};

inline bool InUnitRange(double v) { return Finite(v) && v >= 0.0 && v <= 1.0; }

inline ProfileError ValidateProfile(const ItemProfile& p) {
  if (p.tier < 1 || p.tier > kSkillTierCount) return ProfileError::kTierOutOfRange;
  if (p.persona_index < 0 || p.persona_index >= kPersonalityCount) {
    return ProfileError::kPersonalityOutOfRange;
  }
  if (p.seed == 0u) return ProfileError::kSeedZero;

  const ItemSkillBlock& s = p.skill;
  if (!Finite(s.planning_horizon_s) || !Finite(s.risk_awareness) ||
      !Finite(s.discipline) || !Finite(s.tie_noise)) {
    return ProfileError::kNonFinite;
  }
  if (s.planning_horizon_s < 0.5 || s.planning_horizon_s > 60.0) {
    return ProfileError::kOutOfRange;
  }
  if (!InUnitRange(s.risk_awareness) || !InUnitRange(s.discipline)) {
    return ProfileError::kOutOfRange;
  }
  if (!Finite(s.tie_noise) || s.tie_noise < 0.0 || s.tie_noise > 0.05) {
    return ProfileError::kOutOfRange;
  }

  const ItemPersonalityBlock& q = p.persona;
  const double appetites[6] = {q.health_appetite, q.armor_appetite, q.ammo_appetite,
                               q.weapon_appetite, q.powerup_appetite,
                               q.strategic_appetite};
  for (int i = 0; i < 6; ++i) {
    if (!Finite(appetites[i]) || appetites[i] < 0.0 || appetites[i] > 2.0) {
      return ProfileError::kOutOfRange;
    }
  }
  if (!InUnitRange(q.caution) || !InUnitRange(q.aggression)) {
    return ProfileError::kOutOfRange;
  }

  const ItemTuning& t = p.tuning;
  if (!Finite(t.commit_margin) || !Finite(t.min_commit_s) ||
      !Finite(t.search_cooldown_s) || !Finite(t.abort_cooldown_s) ||
      !Finite(t.abort_damage_frac) || !Finite(t.enemy_abort_radius_m) ||
      !Finite(t.health_abort_frac) || !Finite(t.max_search_time_s) ||
      !Finite(t.min_utility) || !Finite(t.threat_weight) ||
      !Finite(t.time_weight) || !Finite(t.deviation_weight) ||
      !Finite(t.combat_lock_priority) || !Finite(t.memory_horizon_s) ||
      !Finite(t.weapon_reference_m)) {
    return ProfileError::kNonFinite;
  }
  if (t.commit_margin < 0.0 || t.commit_margin > 2.0) return ProfileError::kOutOfRange;
  if (t.min_commit_s < 0.0 || t.min_commit_s > 10.0) return ProfileError::kOutOfRange;
  if (t.search_cooldown_s < 0.0 || t.search_cooldown_s > 30.0) {
    return ProfileError::kOutOfRange;
  }
  if (t.abort_cooldown_s < 0.0 || t.abort_cooldown_s > 30.0) {
    return ProfileError::kOutOfRange;
  }
  if (t.abort_damage_frac <= 0.0 || t.abort_damage_frac > 1.0) {
    return ProfileError::kOutOfRange;
  }
  if (t.enemy_abort_radius_m < 0.0 || t.enemy_abort_radius_m > 100.0) {
    return ProfileError::kOutOfRange;
  }
  if (t.health_abort_frac < 0.0 || t.health_abort_frac > 1.0) {
    return ProfileError::kOutOfRange;
  }
  if (t.max_search_time_s <= 0.0 || t.max_search_time_s > 120.0) {
    return ProfileError::kOutOfRange;
  }
  if (t.min_utility < 0.0 || t.min_utility > 0.9) return ProfileError::kOutOfRange;
  if (t.combat_lock_priority < 0.0 || t.combat_lock_priority > 1.0) {
    return ProfileError::kOutOfRange;
  }
  if (t.memory_horizon_s <= 0.0 || t.weapon_reference_m <= 0.0) {
    return ProfileError::kOutOfRange;
  }
  return ProfileError::kOk;
}

inline bool BuildItemProfile(int tier, int persona, uint32_t seed, ItemProfile* out) {
  if (out == nullptr) return false;
  if (tier < 1 || tier > kSkillTierCount) return false;
  if (persona < 0 || persona >= kPersonalityCount) return false;
  ItemProfile p;
  p.skill = SkillFor(tier);
  p.persona = PersonalityFor(persona);
  p.tuning = TuningFor(p.skill, p.persona);
  p.seed = seed ? seed : 1u;
  p.tier = tier;
  p.persona_index = persona;
  *out = p;
  return ValidateProfile(p) == ProfileError::kOk;
}

inline uint32_t DeriveItemSeed(uint32_t base, int slot, int tier, int persona) {
  uint32_t h = base ? base : 0x9E3779B9u;
  h ^= static_cast<uint32_t>(slot + 1) * 0x85EBCA6Bu;
  h ^= static_cast<uint32_t>(tier) * 0xC2B2AE35u;
  h ^= static_cast<uint32_t>(persona + 1) * 0x27D4EB2Fu;
  h = Hash32(h);
  return h ? h : 1u;
}

}  // namespace itemai

#endif  // ITEMAI_ITEM_PROFILE_H

/* ======================================================================== */
/* item_scoring.h                                                           */
/* ======================================================================== */

#ifndef ITEMAI_ITEM_SCORING_H
#define ITEMAI_ITEM_SCORING_H

namespace itemai {

constexpr double kUrgentHealthFrac = 0.35;
constexpr double kFullHealthFrac = 0.98;

struct ScoreContext {
  SelfAssessment self;
  ItemSkillBlock skill;
  ItemPersonalityBlock persona;
  ItemTuning tuning;
  uint32_t seed = 1u;
  int slot = 0;
  int tick = 0;

  double health_deficit_pts = 0.0;
  double armor_deficit_pts = 0.0;
  double health_frac = 1.0;
  double armor_frac = 0.0;
  double ammo_pressure = 0.0;
  double ammo_pressure_frac = 0.0;
  double mood = 1.0;
  double combat_priority = 0.0;
  bool engaged = false;
  int visible_enemies = 0;
  double nearest_enemy_m = -1.0;
  bool under_fire = false;
};

inline double ItemMood(const ItemProfile& p, int tick) {
  if (p.persona_index != 5) return 1.0;
  const double t = SecondsFromTicks(tick);
  const double phase = static_cast<double>(p.seed % 997u) * 0.0063;
  return 1.0 + 0.18 * std::sin(0.35 * t + phase);
}

inline ScoreContext MakeContext(const ItemProfile& p, const ItemWorld& w,
                                int slot = 0) {
  ScoreContext c;
  c.self = AssessSelf(w, p.persona.weapon_appetite >= 1.0 ? 0.15 : 0.0);
  c.skill = p.skill;
  c.persona = p.persona;
  c.tuning = p.tuning;
  c.seed = p.seed;
  c.slot = slot;
  c.tick = w.combat.tick;
  c.health_frac = c.self.health_frac;
  c.armor_frac = c.self.armor_frac;
  c.health_deficit_pts = w.self.max_health - w.self.health;
  c.armor_deficit_pts = w.self.max_armor - w.self.armor;
  c.combat_priority = w.combat.combat_priority;
  c.engaged = w.combat.engaged;
  c.visible_enemies = w.threat.visible_enemies;
  c.nearest_enemy_m = w.threat.nearest_enemy_m;
  c.under_fire = w.threat.under_fire;

  if (c.self.ammunition_starved) {
    c.ammo_pressure = 1.0;
  } else if (c.self.best_weapon > 1) {
    const int cap = WeaponAmmoCap(c.self.best_weapon);
    const double fill = cap > 0
        ? Clamp01(static_cast<double>(w.self.ammo[c.self.best_weapon]) / cap)
        : 1.0;
    c.ammo_pressure = fill < 0.35 ? 0.60 : (fill < 0.65 ? 0.35 : 0.20);
  } else {
    c.ammo_pressure = 0.85;
  }

  c.mood = ItemMood(p, w.combat.tick);
  c.ammo_pressure_frac = Clamp01(c.ammo_pressure);
  return c;
}

inline double HealthNeed(const ScoreContext& c) {
  const double hf = Clamp01(c.health_frac);
  if (hf >= kFullHealthFrac) return 0.0;
  const double linear = 1.0 - hf;
  if (hf >= kUrgentHealthFrac) return linear * 0.75;
  const double urgent = 0.55 + 0.45 * (1.0 - hf / kUrgentHealthFrac);
  const double v = linear * 0.75 > urgent ? linear * 0.75 : urgent;
  return Clamp01(v);
}

inline double ArmorNeed(const ScoreContext& c) {
  const double af = Clamp01(c.armor_frac);
  if (af >= kFullHealthFrac) return 0.0;
  return Clamp01((1.0 - af) * 0.82);
}

inline double AmmoNeed(const ScoreContext& c, const ItemWorld& w, int weapon_index) {
  if (weapon_index < 1 || weapon_index > kWeaponCount) return 0.0;
  if (!WeaponOwned(w.self.owned_weapons, weapon_index)) return 0.0;
  const int cap = WeaponAmmoCap(weapon_index);
  if (cap <= 0) return 0.0;
  const double current = static_cast<double>(w.self.ammo[weapon_index]);
  const double fill = Clamp01(current / cap);
  if (fill >= kFullHealthFrac) return 0.0;

  const double ref = c.self.reference_distance_m;
  const double score = StandInWeaponScore(weapon_index, ref, 0.0);
  const double best = c.self.best_weapon_score > 1e-6 ? c.self.best_weapon_score : 1e-6;
  const double rel = Clamp01(score / best);

  const double deficit = 1.0 - fill;
  const double pressure = 0.35 + 0.65 * c.ammo_pressure_frac;
  const double weapon_relevance = 0.30 + 0.70 * rel;
  double need = deficit * pressure * weapon_relevance;
  if (current <= 0.5 && rel > 0.75) need = need > 0.75 ? need : 0.75;
  return Clamp01(need);
}

inline double WeaponNeed(const ScoreContext& c, const ItemWorld& w, int weapon_index) {
  if (weapon_index < 1 || weapon_index > kWeaponCount) return 0.0;
  const double ref = c.self.reference_distance_m;
  const double candidate = StandInWeaponScore(weapon_index, ref, 0.0);
  const double best = c.self.best_weapon_score;

  if (WeaponOwned(w.self.owned_weapons, weapon_index)) {
    return Clamp01(0.45 * AmmoNeed(c, w, weapon_index));
  }
  if (best <= 1e-6) return 1.0;
  const double gain = (candidate - best) / best;
  if (gain <= 0.0) {
    return Clamp01(0.10 * (1.0 - c.ammo_pressure_frac));
  }
  return Clamp01(gain);
}

inline double Capability(const ScoreContext& c, const ItemWorld& w,
                         const ItemSnapshot& it) {
  switch (it.kind) {
    case ItemKind::kHealth: {
      if (it.value <= 0.0) return 1.0;
      const double deficit = c.health_deficit_pts > 1.0 ? c.health_deficit_pts : 1.0;
      const double useful = it.value < deficit ? it.value : deficit;
      return Clamp01(useful / deficit);
    }
    case ItemKind::kArmor: {
      if (it.value <= 0.0) return 1.0;
      const double deficit = c.armor_deficit_pts > 1.0 ? c.armor_deficit_pts : 1.0;
      const double useful = it.value < deficit ? it.value : deficit;
      return Clamp01(useful / deficit);
    }
    case ItemKind::kAmmo: {
      const int cap = WeaponAmmoCap(it.weapon_index);
      if (cap <= 0) return 0.0;
      const double have = static_cast<double>(w.self.ammo[it.weapon_index]);
      const double missing = cap - have > 1.0 ? cap - have : 1.0;
      const double amount = it.amount > 0 ? static_cast<double>(it.amount) : it.value;
      const double useful = amount < missing ? amount : missing;
      return Clamp01(useful / missing);
    }
    case ItemKind::kWeapon:
      return 1.0;
    case ItemKind::kPowerup:
    case ItemKind::kStrategic:
      return Clamp01(it.value > 0.0 ? it.value : 0.5);
    default:
      return 0.0;
  }
}

inline double Scarcity(const ScoreContext& c, const ItemSnapshot& it) {
  double r = 0.6;
  switch (it.kind) {
    case ItemKind::kHealth: r = 0.75; break;
    case ItemKind::kArmor: r = 0.80; break;
    case ItemKind::kAmmo: r = 0.45 + 0.85 * c.ammo_pressure_frac; break;
    case ItemKind::kWeapon: r = 0.95; break;
    case ItemKind::kPowerup: r = 1.05; break;
    case ItemKind::kStrategic: r = 0.55; break;
    default: return 1.0;
  }
  const double v = 0.75 + 0.5 * r;
  return Clamp(v, 0.5, 1.5);
}

inline double Exposure(const ScoreContext& c) {
  if (c.visible_enemies <= 0 || c.nearest_enemy_m < 0.0) return 0.0;
  const double proximity = Clamp01(1.0 - c.nearest_enemy_m / 25.0);
  const double fire = c.under_fire ? 1.0 : 0.55;
  return proximity * fire;
}

inline double ThreatFactor(const ScoreContext& c) {
  const double discount = c.tuning.threat_weight * c.skill.risk_awareness * Exposure(c);
  return Clamp(1.0 - discount, 0.30, 1.0);
}

inline double PriorityFactor(const ScoreContext& c, const ItemSnapshot& it) {
  if (!c.engaged || c.combat_priority <= 0.0) return 1.0;
  double priority = c.combat_priority;
  if ((it.kind == ItemKind::kHealth || it.kind == ItemKind::kArmor) &&
      c.health_frac < kUrgentHealthFrac) {
    priority *= 0.25;
  }
  const double f = 1.0 - c.tuning.combat_lock_priority * priority;
  return Clamp(f, 0.05, 1.0);
}

inline double TravelSeconds(const ItemWorld& w, const ItemSnapshot& it) {
  const double d = Distance(w.self.eye, it.pos);
  const double speed = w.self.move_speed_mps > 0.1 ? w.self.move_speed_mps : 0.1;
  return d / speed + 0.35;
}

inline double TimeFactor(const ScoreContext& c, double travel_s) {
  const double horizon = c.tuning.memory_horizon_s > 0.5 ? c.tuning.memory_horizon_s : 0.5;
  const double ratio = Clamp01(travel_s / horizon);
  return Clamp(1.0 - c.tuning.time_weight * ratio, 0.10, 1.0);
}

inline double DistanceFactor(const ItemWorld& w, const ItemSnapshot& it) {
  const double d = Distance(w.self.eye, it.pos);
  return 0.65 + 0.35 * Clamp01(1.0 - d / 40.0);
}

inline double FreshnessFactor(const ScoreContext& c, const ItemSnapshot& it) {
  if (it.visible) return 1.0;
  const double horizon = c.tuning.memory_horizon_s > 0.5 ? c.tuning.memory_horizon_s : 0.5;
  const double age = Clamp01(it.staleness_s / horizon);
  return Clamp(1.0 - 0.45 * age, 0.40, 1.0);
}

inline double AppetiteFor(const ScoreContext& c, ItemKind kind) {
  switch (kind) {
    case ItemKind::kHealth: return c.persona.health_appetite;
    case ItemKind::kArmor: return c.persona.armor_appetite;
    case ItemKind::kAmmo: return c.persona.ammo_appetite;
    case ItemKind::kWeapon: return c.persona.weapon_appetite;
    case ItemKind::kPowerup: return c.persona.powerup_appetite;
    case ItemKind::kStrategic: return c.persona.strategic_appetite;
    default: return 1.0;
  }
}

inline double SkillFactor(const ScoreContext& c, double travel_s) {
  const double horizon = c.skill.planning_horizon_s > 0.5 ? c.skill.planning_horizon_s : 0.5;
  const double far = Clamp01(travel_s / (horizon * 2.0));
  return Clamp(1.0 - 0.35 * c.skill.risk_awareness * far * far, 0.45, 1.0);
}

struct ScoreTerms {
  double need = 0.0;
  double scarcity = 1.0;
  double capability = 0.0;
  double base = 0.0;
  double threat = 1.0;
  double priority = 1.0;
  double time = 1.0;
  double distance = 1.0;
  double freshness = 1.0;
  double appetite = 1.0;
  double skill = 1.0;
  double travel_s = 0.0;
  double utility = 0.0;
  double tiebreak = 0.0;
};

struct ItemEvaluation {
  int item_index = -1;
  int item_id = -1;
  ItemKind kind = ItemKind::kNone;
  int weapon_index = 0;
  Vec3 pos{};
  double distance_m = 0.0;
  ScoreTerms terms;
  bool eligible = false;
  ItemReason reject = ItemReason::kNone;
  bool selected = false;
};

inline ItemEvaluation EvaluateItem(const ScoreContext& c, const ItemWorld& w,
                                   int item_index) {
  ItemEvaluation e;
  e.item_index = item_index;
  const ItemSnapshot& it = w.items[item_index];
  e.item_id = it.id;
  e.kind = it.kind;
  e.weapon_index = it.weapon_index;
  e.pos = it.pos;
  e.distance_m = Distance(w.self.eye, it.pos);

  ScoreTerms& t = e.terms;
  t.travel_s = TravelSeconds(w, it);

  switch (it.kind) {
    case ItemKind::kHealth: t.need = HealthNeed(c); break;
    case ItemKind::kArmor: t.need = ArmorNeed(c); break;
    case ItemKind::kAmmo: t.need = AmmoNeed(c, w, it.weapon_index); break;
    case ItemKind::kWeapon: t.need = WeaponNeed(c, w, it.weapon_index); break;
    case ItemKind::kPowerup:
      t.need = Clamp01(it.value) * (c.engaged ? 1.0 : 0.55);
      break;
    case ItemKind::kStrategic:
      t.need = Clamp01(it.value) * (c.engaged ? 0.35 : 1.0);
      break;
    default:
      t.need = 0.0;
      break;
  }
  t.appetite = Clamp(AppetiteFor(c, it.kind), 0.0, 2.0);
  t.need = Clamp01(t.need * t.appetite * (it.kind == ItemKind::kPowerup ||
                                         it.kind == ItemKind::kStrategic
                                             ? 1.0
                                             : c.mood));

  t.scarcity = Scarcity(c, it);
  t.capability = Capability(c, w, it);
  t.base = t.need * t.scarcity * t.capability;

  t.threat = ThreatFactor(c);
  t.priority = PriorityFactor(c, it);
  t.time = TimeFactor(c, t.travel_s);
  t.distance = DistanceFactor(w, it);
  t.freshness = FreshnessFactor(c, it);
  t.skill = SkillFactor(c, t.travel_s);
  t.utility = t.base * t.threat * t.priority * t.time * t.distance *
              t.freshness * t.skill;
  t.tiebreak = TieBreakUnit(c.seed, it.id, c.slot);

  e.eligible = true;
  if (!it.reachable) {
    e.eligible = false;
    e.reject = ItemReason::kUnreachable;
  } else if (it.respawn_s > 0.0) {
    e.eligible = false;
    e.reject = ItemReason::kItemGone;
  } else if (t.travel_s > c.tuning.max_search_time_s) {
    e.eligible = false;
    e.reject = ItemReason::kOutOfRange;
  } else if (t.base <= kNeedEpsilon) {
    e.eligible = false;
    e.reject = ItemReason::kNeedSatisfied;
  } else if (t.utility < c.tuning.min_utility) {
    e.eligible = false;
    e.reject = ItemReason::kNoCandidate;
  } else if (c.engaged && c.combat_priority > c.tuning.combat_lock_priority &&
             !(it.kind == ItemKind::kHealth && c.health_frac < kUrgentHealthFrac)) {
    e.eligible = false;
    e.reject = ItemReason::kCombatLock;
  }
  return e;
}

inline bool BetterEvaluation(const ItemEvaluation& a, const ItemEvaluation& b) {
  if (a.terms.utility > b.terms.utility + 1e-12) return true;
  if (b.terms.utility > a.terms.utility + 1e-12) return false;
  if (a.terms.tiebreak > b.terms.tiebreak + 1e-12) return true;
  if (b.terms.tiebreak > a.terms.tiebreak + 1e-12) return false;
  return a.item_id < b.item_id;
}

}  // namespace itemai

#endif  // ITEMAI_ITEM_SCORING_H

/* ======================================================================== */
/* navigation_interface.h                                                   */
/* ======================================================================== */

#ifndef ITEMAI_NAVIGATION_INTERFACE_H
#define ITEMAI_NAVIGATION_INTERFACE_H

namespace itemai {

enum class NavPriority : uint8_t {
  kSoft = 0,
  kNormal = 1,
  kUrgent = 2,
  kCritical = 3
};

enum class NavStatus : uint8_t {
  kIdle = 0,
  kAccepted = 1,
  kInProgress = 2,
  kArrived = 3,
  kUnreachable = 4,
  kStalled = 5,
  kAborted = 6,
  kExpired = 7,
  kRejected = 8
};

inline const char* NavStatusName(NavStatus s) {
  switch (s) {
    case NavStatus::kIdle: return "idle";
    case NavStatus::kAccepted: return "accepted";
    case NavStatus::kInProgress: return "in-progress";
    case NavStatus::kArrived: return "arrived";
    case NavStatus::kUnreachable: return "unreachable";
    case NavStatus::kStalled: return "stalled";
    case NavStatus::kAborted: return "aborted";
    case NavStatus::kExpired: return "expired";
    case NavStatus::kRejected: return "rejected";
    default: return "?";
  }
}

inline bool NavIsTerminal(NavStatus s) {
  return s == NavStatus::kArrived || s == NavStatus::kUnreachable ||
         s == NavStatus::kStalled || s == NavStatus::kAborted ||
         s == NavStatus::kExpired || s == NavStatus::kRejected;
}

struct NavGoal {
  int goal_id = -1;
  Vec3 pos{};
  double arrive_radius_m = kArrivalRadiusM;
  NavPriority priority = NavPriority::kNormal;
  double max_speed_frac = 1.0;
  bool allow_jump = true;
  bool yield_to_combat = true;
  int issued_tick = 0;
  int expires_tick = 0;

  bool Expired(int tick) const { return tick >= expires_tick; }
  bool Valid() const {
    return goal_id >= 0 && Finite(pos.x) && Finite(pos.y) && Finite(pos.z) &&
           arrive_radius_m > 0.0 && Finite(arrive_radius_m) &&
           max_speed_frac > 0.0 && max_speed_frac <= 1.0 && expires_tick > issued_tick;
  }
};

struct NavFeedback {
  int goal_id = -1;
  NavStatus status = NavStatus::kIdle;
  Vec3 bot_pos{};
  double path_remaining_m = -1.0;
  bool line_of_sight = false;
  int tick = 0;
};

class NavigationSink {
 public:
  virtual ~NavigationSink() = default;
  virtual NavStatus Submit(const NavGoal& goal) = 0;
  virtual void Cancel(int goal_id) = 0;
  virtual NavStatus Poll(int goal_id, NavFeedback* out) = 0;
  virtual const char* Name() const = 0;
};

class RecordingNavigationSink : public NavigationSink {
 public:
  static constexpr int kSlots = 16;

  void Reset() {
    for (int i = 0; i < kSlots; ++i) slots_[i] = Slot();
    submits_ = 0;
    cancels_ = 0;
    polls_ = 0;
    rejected_all_ = false;
    arrive_after_ticks_ = 0;
    stall_after_ticks_ = -1;
    for (int i = 0; i < 8; ++i) unreachable_ids_[i] = -1;
    unreachable_count_ = 0;
  }

  RecordingNavigationSink() { Reset(); }

  void RejectEverything(bool v) { rejected_all_ = v; }
  void SetArriveAfterPolls(int polls) { arrive_after_ticks_ = polls; }
  void SetStallAfterPolls(int polls) { stall_after_ticks_ = polls; }
  void MarkUnreachable(int goal_id) {
    for (int i = 0; i < 8; ++i) {
      if (unreachable_ids_[i] == goal_id) return;
    }
    for (int i = 0; i < 8; ++i) {
      if (unreachable_ids_[i] < 0) {
        unreachable_ids_[i] = goal_id;
        ++unreachable_count_;
        return;
      }
    }
  }

  NavStatus Submit(const NavGoal& goal) override {
    ++submits_;
    last_goal_ = goal;
    const int s = FindSlot(goal.goal_id, true);
    if (s < 0) return NavStatus::kRejected;
    Slot& sl = slots_[s];
    if (sl.goal_id == goal.goal_id && sl.status == NavStatus::kInProgress) {
      return sl.status;
    }
    sl.goal_id = goal.goal_id;
    sl.pos = goal.pos;
    sl.goal = goal;
    sl.polls = 0;
    sl.status = rejected_all_ || IsUnreachable(goal.goal_id) ? NavStatus::kUnreachable
                                                            : NavStatus::kAccepted;
    return sl.status;
  }

  void Cancel(int goal_id) override {
    ++cancels_;
    const int s = FindSlot(goal_id, false);
    if (s < 0) return;
    slots_[s].status = NavStatus::kAborted;
  }

  NavStatus Poll(int goal_id, NavFeedback* out) override {
    ++polls_;
    const int s = FindSlot(goal_id, false);
    if (s < 0) {
      if (out != nullptr) *out = NavFeedback();
      return NavStatus::kIdle;
    }
    Slot& sl = slots_[s];
    const int polls = ++sl.polls;

    if (sl.status == NavStatus::kAccepted) sl.status = NavStatus::kInProgress;
    if (arrive_after_ticks_ > 0 && polls >= arrive_after_ticks_) {
      sl.status = NavStatus::kArrived;
    } else if (stall_after_ticks_ >= 0 && polls >= stall_after_ticks_ &&
               sl.status == NavStatus::kInProgress) {
      sl.status = NavStatus::kStalled;
    } else if (sl.goal.expires_tick > 0 && sl.goal.Expired(sl.goal.issued_tick + polls)) {
      sl.status = NavStatus::kExpired;
    }

    if (out != nullptr) {
      out->goal_id = goal_id;
      out->status = sl.status;
      out->bot_pos = sl.pos;
      out->path_remaining_m = -1.0;
      out->line_of_sight = false;
      out->tick = sl.goal.issued_tick + polls;
    }
    return sl.status;
  }

  const char* Name() const override { return "recording"; }

  int submits() const { return submits_; }
  int cancels() const { return cancels_; }
  int polls() const { return polls_; }
  const NavGoal& last_goal() const { return last_goal_; }
  NavStatus StatusOf(int goal_id) {
    const int s = FindSlot(goal_id, false);
    return s < 0 ? NavStatus::kIdle : slots_[s].status;
  }

 private:
  struct Slot {
    int goal_id = -1;
    NavStatus status = NavStatus::kIdle;
    Vec3 pos{};
    NavGoal goal{};
    int polls = 0;
  };

  int FindSlot(int goal_id, bool create) {
    if (goal_id < 0) return -1;
    for (int i = 0; i < kSlots; ++i) {
      if (slots_[i].goal_id == goal_id) return i;
    }
    if (!create) return -1;
    for (int i = 0; i < kSlots; ++i) {
      if (slots_[i].goal_id < 0) return i;
    }
    for (int i = 0; i < kSlots; ++i) {
      if (NavIsTerminal(slots_[i].status)) return i;
    }
    return -1;
  }

  bool IsUnreachable(int goal_id) const {
    for (int i = 0; i < 8; ++i) {
      if (unreachable_ids_[i] == goal_id) return true;
    }
    return false;
  }

  Slot slots_[kSlots];
  NavGoal last_goal_{};
  int submits_ = 0;
  int cancels_ = 0;
  int polls_ = 0;
  bool rejected_all_ = false;
  int arrive_after_ticks_ = 0;
  int stall_after_ticks_ = -1;
  int unreachable_ids_[8] = {-1, -1, -1, -1, -1, -1, -1, -1};
  int unreachable_count_ = 0;
};

struct GoalTranslationInput {
  int goal_id = -1;
  Vec3 pos{};
  bool survival = false;
  bool urgent = false;
  bool combat_engaged = false;
  double utility = 0.0;
  int issued_tick = 0;
  int max_duration_ticks = 160;
  double caution = 0.5;
};

inline NavGoal MakeNavGoal(const GoalTranslationInput& in) {
  NavGoal g;
  g.goal_id = in.goal_id;
  g.pos = in.pos;
  g.arrive_radius_m = kArrivalRadiusM;
  g.issued_tick = in.issued_tick;
  g.expires_tick = in.issued_tick + (in.max_duration_ticks > 0 ? in.max_duration_ticks : 1);
  g.priority = in.survival   ? NavPriority::kCritical
               : in.urgent   ? NavPriority::kUrgent
               : in.utility > 0.55 ? NavPriority::kNormal
                                   : NavPriority::kSoft;
  g.yield_to_combat = !in.survival;
  g.max_speed_frac = Clamp(1.0 - 0.35 * in.caution, 0.6, 1.0);
  g.allow_jump = true;
  return g;
}

}  // namespace itemai

#endif  // ITEMAI_NAVIGATION_INTERFACE_H

/* ======================================================================== */
/* item_planner.h                                                           */
/* ======================================================================== */

#ifndef ITEMAI_ITEM_PLANNER_H
#define ITEMAI_ITEM_PLANNER_H

namespace itemai {

constexpr int kTimerSlots = 32;
constexpr int kStallAbortReports = 2;
constexpr int kExplainCap = 120;

struct TimerTable {
  int id[kTimerSlots];
  int until[kTimerSlots];

  void Clear() {
    for (int i = 0; i < kTimerSlots; ++i) {
      id[i] = -1;
      until[i] = 0;
    }
  }
  TimerTable() { Clear(); }

  void Set(int item_id, int until_tick) {
    if (item_id < 0) return;
    int empty_slot = -1;
    int oldest = 0;
    for (int i = 0; i < kTimerSlots; ++i) {
      if (id[i] == item_id) {
        if (until_tick > until[i]) until[i] = until_tick;
        return;
      }
      if (id[i] < 0 && empty_slot < 0) empty_slot = i;
      if (until[i] < until[oldest]) oldest = i;
    }
    const int slot = empty_slot >= 0 ? empty_slot : oldest;
    id[slot] = item_id;
    until[slot] = until_tick;
  }

  bool Active(int item_id, int tick) const {
    for (int i = 0; i < kTimerSlots; ++i) {
      if (id[i] == item_id) return tick < until[i];
    }
    return false;
  }

  int Remaining(int item_id, int tick) const {
    for (int i = 0; i < kTimerSlots; ++i) {
      if (id[i] == item_id) {
        const int r = until[i] - tick;
        return r > 0 ? r : 0;
      }
    }
    return 0;
  }

  void ClearEntry(int item_id) {
    for (int i = 0; i < kTimerSlots; ++i) {
      if (id[i] == item_id) {
        id[i] = -1;
        until[i] = 0;
      }
    }
  }
};

struct GoalDecision {
  ItemAction action = ItemAction::kNone;
  ItemReason reason = ItemReason::kNone;

  bool has_goal = false;
  int goal_id = -1;
  ItemKind goal_kind = ItemKind::kNone;
  int goal_weapon_index = 0;
  Vec3 goal_pos{};

  double utility = 0.0;
  double need = 0.0;
  double travel_s = 0.0;
  double distance_m = 0.0;

  bool suppress_combat = false;
  bool changed = false;

  int candidates = 0;
  int eligible = 0;
  char explain[kExplainCap] = {0};
};

class ItemPlanner {
 public:
  ItemPlanner() {
    ItemProfile p;
    BuildItemProfile(3, 0, 0x1234567u, &p);
    Configure(p);
  }

  void Configure(const ItemProfile& p) {
    profile_ = p;
    Reset();
  }

  void Reset() {
    has_goal_ = false;
    goal_ = GoalState();
    cooldown_.Clear();
    blacklist_.Clear();
    global_cooldown_until_ = 0;
    damage_window_tick_ = -1;
    damage_window_health_ = 0.0;
    eval_count_ = 0;
    ticks_processed_ = 0;
    selections_ = 0;
    switches_ = 0;
    aborts_ = 0;
    reached_ = 0;
    timeouts_ = 0;
    cooldown_blocks_ = 0;
    combat_lock_blocks_ = 0;
    evaluations_ = 0;
    last_tick_ = 0;
    slot_ = 0;
  }

  const ItemProfile& profile() const { return profile_; }
  void set_slot(int slot) { slot_ = slot; }

  bool has_goal() const { return has_goal_; }
  int goal_id() const { return has_goal_ ? goal_.item_id : -1; }
  ItemKind goal_kind() const { return has_goal_ ? goal_.kind : ItemKind::kNone; }
  int goal_started_tick() const { return has_goal_ ? goal_.started_tick : -1; }
  double goal_utility() const { return has_goal_ ? goal_.utility : 0.0; }
  int last_tick() const { return last_tick_; }

  int selections() const { return selections_; }
  int switches() const { return switches_; }
  int aborts() const { return aborts_; }
  int reached() const { return reached_; }
  int timeouts() const { return timeouts_; }
  int cooldown_blocks() const { return cooldown_blocks_; }
  int combat_lock_blocks() const { return combat_lock_blocks_; }
  int ticks_processed() const { return ticks_processed_; }
  long long evaluations() const { return evaluations_; }

  const ItemEvaluation* last_evaluations(int* count) const {
    if (count != nullptr) *count = eval_count_;
    return evals_;
  }

  void NotifyItemPicked(int item_id, int tick) {
    if (item_id < 0) return;
    blacklist_.Set(item_id, tick + TickFromSeconds(profile_.tuning.consumable_blacklist_s));
    if (has_goal_ && goal_.item_id == item_id) {
      ++reached_;
      CloseGoal(ItemReason::kReached);
    }
  }

  GoalDecision Step(const ItemWorld& w, NavigationSink* nav = nullptr) {
    GoalDecision d;
    nav_ = nav;
    last_tick_ = w.combat.tick;
    const int tick = w.combat.tick;

    const ValidationError ve = ValidateWorld(w);
    if (ve != ValidationError::kOk) {
      if (has_goal_) {
        CloseGoal(ItemReason::kInvalidWorld);
        d.action = ItemAction::kAbort;
      }
      d.reason = ItemReason::kInvalidWorld;
      d.changed = true;
      std::snprintf(d.explain, sizeof(d.explain), "invalid-world:%s",
                    ValidationErrorName(ve));
      return d;
    }

    ctx_ = MakeContext(profile_, w, slot_);
    ++ticks_processed_;
    UpdateDamageWindow(w);
    EvaluateAll(w);
    d.candidates = w.count;
    for (int i = 0; i < eval_count_; ++i) {
      if (evals_[i].eligible) ++d.eligible;
    }

    if (has_goal_ && nav_ != nullptr && goal_.nav_submitted) {
      NavFeedback fb{};
      const NavStatus st = nav_->Poll(goal_.item_id, &fb);
      switch (st) {
        case NavStatus::kArrived:
          if (FinishGoal(d, ItemReason::kReached)) return d;
          break;
        case NavStatus::kUnreachable:
        case NavStatus::kRejected:
          if (FinishGoal(d, ItemReason::kUnreachable)) return d;
          break;
        case NavStatus::kExpired:
          ++timeouts_;
          if (FinishGoal(d, ItemReason::kTimeout)) return d;
          break;
        case NavStatus::kStalled:
          if (++goal_.stall_reports >= kStallAbortReports) {
            if (FinishGoal(d, ItemReason::kStalled)) return d;
          }
          break;
        case NavStatus::kAborted:
          if (FinishGoal(d, ItemReason::kItemGone)) return d;
          break;
        default:
          break;
      }
    }

    if (has_goal_) {
      const int idx = IndexOfItem(w, goal_.item_id);
      if (idx < 0) {
        if (FinishGoal(d, ItemReason::kItemGone)) return d;
      } else {
        const ItemEvaluation& cur = evals_[idx];
        const double dist = Distance(w.self.eye, cur.pos);
        if (dist <= kArrivalRadiusM) {
          if (FinishGoal(d, ItemReason::kReached)) return d;
        } else if (cur.reject == ItemReason::kUnreachable) {
          if (FinishGoal(d, ItemReason::kUnreachable)) return d;
        } else if (cur.reject == ItemReason::kItemGone) {
          if (FinishGoal(d, ItemReason::kItemGone)) return d;
        } else if (cur.reject == ItemReason::kOutOfRange) {
          if (FinishGoal(d, ItemReason::kOutOfRange)) return d;
        } else if (cur.terms.base <= kNeedEpsilon) {
          if (FinishGoal(d, ItemReason::kNeedSatisfied)) return d;
        } else if (ThreatAbort(w, dist)) {
          if (FinishGoal(d, ItemReason::kThreatOverride)) return d;
        } else if (DamageAbort(w)) {
          if (FinishGoal(d, ItemReason::kDamageAbort)) return d;
        } else if (TimedOut(tick)) {
          ++timeouts_;
          if (FinishGoal(d, ItemReason::kTimeout)) return d;
        } else if (CombatLock(w)) {
          ++combat_lock_blocks_;
          if (FinishGoal(d, ItemReason::kCombatLock)) return d;
        } else {
          const ItemEvaluation* best = PickBest(ItemKind::kNone, goal_.item_id);
          const bool dwell_ok =
              (tick - goal_.started_tick) >= TickFromSeconds(profile_.tuning.min_commit_s);
          if (best != nullptr && dwell_ok &&
              best->terms.utility >
                  cur.terms.utility * (1.0 + profile_.tuning.commit_margin)) {
            if (CommitGoal(*best, tick, ItemReason::kSwitched)) {
              ++switches_;
              FillDecision(d, ItemAction::kSwitch, ItemReason::kSwitched, true);
              return d;
            }
          }
          goal_.last_update_tick = tick;
          goal_.utility = cur.terms.utility;
          goal_.need = cur.terms.need;
          FillDecision(d, ItemAction::kKeep,
                       dwell_ok ? ItemReason::kKept : ItemReason::kHysteresisHold,
                       false);
          return d;
        }
      }
    }

    if (tick < global_cooldown_until_) {
      ++cooldown_blocks_;
      d.reason = ItemReason::kCooldown;
      std::snprintf(d.explain, sizeof(d.explain), "cooldown:%dt",
                    global_cooldown_until_ - tick);
      return d;
    }
    if (CombatLock(w)) {
      ++combat_lock_blocks_;
      d.reason = ItemReason::kCombatLock;
      std::snprintf(d.explain, sizeof(d.explain), "combat-lock:%.2f/%.2f",
                    w.combat.combat_priority, profile_.tuning.combat_lock_priority);
      return d;
    }

    const ItemEvaluation* best = PickBest(ItemKind::kNone, -1);
    if (best == nullptr) {
      d.reason = ExplainNoCandidate();
      std::snprintf(d.explain, sizeof(d.explain), "no-candidate:%s",
                    ItemReasonName(d.reason));
      return d;
    }
    if (!CommitGoal(*best, tick, ItemReason::kSelected)) {
      d.reason = ItemReason::kUnreachable;
      std::snprintf(d.explain, sizeof(d.explain), "nav-refused:%d", best->item_id);
      return d;
    }
    ++selections_;
    FillDecision(d, ItemAction::kSelect, ItemReason::kSelected, true);
    return d;
  }

 private:
  struct GoalState {
    int item_id = -1;
    ItemKind kind = ItemKind::kNone;
    int weapon_index = 0;
    Vec3 pos{};
    int started_tick = 0;
    int last_update_tick = 0;
    double utility = 0.0;
    double need = 0.0;
    int stall_reports = 0;
    bool survival = false;
    bool nav_submitted = false;
  };

  void EvaluateAll(const ItemWorld& w) {
    eval_count_ = w.count;
    for (int i = 0; i < w.count; ++i) {
      evals_[i] = EvaluateItem(ctx_, w, i);
    }
    evaluations_ += w.count;
  }

  int IndexOfItem(const ItemWorld& w, int item_id) const {
    for (int i = 0; i < w.count; ++i) {
      if (w.items[i].id == item_id) return i;
    }
    return -1;
  }

  const ItemEvaluation* PickBest(ItemKind /*preferred*/, int exclude_id) {
    const ItemEvaluation* best = nullptr;
    for (int i = 0; i < eval_count_; ++i) {
      const ItemEvaluation& e = evals_[i];
      if (!e.eligible) continue;
      if (e.item_id == exclude_id) continue;
      if (cooldown_.Active(e.item_id, last_tick_)) continue;
      if (blacklist_.Active(e.item_id, last_tick_)) continue;
      if (best == nullptr || BetterEvaluation(e, *best)) best = &e;
    }
    return best;
  }

  ItemReason ExplainNoCandidate() const {
    bool out_of_range = false;
    bool combat_lock = false;
    bool cooldown = false;
    bool unreachable = false;
    bool resupply_candidate = false;
    for (int i = 0; i < eval_count_; ++i) {
      const ItemEvaluation& e = evals_[i];
      if (e.kind == ItemKind::kAmmo || e.kind == ItemKind::kWeapon) {
        resupply_candidate = true;
      }
      if (e.reject == ItemReason::kOutOfRange) out_of_range = true;
      if (e.reject == ItemReason::kCombatLock) combat_lock = true;
      if (e.reject == ItemReason::kUnreachable) unreachable = true;
      if (cooldown_.Active(e.item_id, last_tick_) ||
          blacklist_.Active(e.item_id, last_tick_)) {
        cooldown = true;
      }
    }
    if (ctx_.self.ammunition_starved && !resupply_candidate) {
      return ItemReason::kAmmoStarved;
    }
    if (unreachable) return ItemReason::kUnreachable;
    if (combat_lock) return ItemReason::kCombatLock;
    if (out_of_range) return ItemReason::kOutOfRange;
    if (cooldown) return ItemReason::kCooldown;
    return ItemReason::kNoCandidate;
  }

  bool CommitGoal(const ItemEvaluation& e, int tick, ItemReason reason) {
    GoalState next;
    next.item_id = e.item_id;
    next.kind = e.kind;
    next.weapon_index = e.weapon_index;
    next.pos = e.pos;
    next.started_tick = tick;
    next.last_update_tick = tick;
    next.utility = e.terms.utility;
    next.need = e.terms.need;
    next.survival = (e.kind == ItemKind::kHealth || e.kind == ItemKind::kArmor) &&
                    ctx_.health_frac < kUrgentHealthFrac;

    if (nav_ != nullptr) {
      GoalTranslationInput ti;
      ti.goal_id = e.item_id;
      ti.pos = e.pos;
      ti.survival = next.survival;
      ti.urgent = ctx_.self.ammunition_starved || ctx_.health_frac < 0.50;
      ti.combat_engaged = ctx_.engaged;
      ti.utility = e.terms.utility;
      ti.issued_tick = tick;
      ti.max_duration_ticks = TickFromSeconds(profile_.tuning.max_search_time_s) + 20;
      ti.caution = profile_.persona.caution;
      const NavGoal g = MakeNavGoal(ti);
      const NavStatus st = nav_->Submit(g);
      if (st != NavStatus::kAccepted && st != NavStatus::kInProgress) {
        blacklist_.Set(e.item_id, tick + 300 * static_cast<int>(kTickHz));
        return false;
      }
      next.nav_submitted = true;
    }
    if (has_goal_ && nav_ != nullptr && goal_.nav_submitted) {
      nav_->Cancel(goal_.item_id);
    }
    goal_ = next;
    has_goal_ = true;
    (void)reason;
    return true;
  }

  bool FinishGoal(GoalDecision& d, ItemReason reason) {
    if (!has_goal_) return false;
    const int id = goal_.item_id;
    const ItemKind kind = goal_.kind;
    const Vec3 pos = goal_.pos;
    const double utility = goal_.utility;
    const int tick = last_tick_;

    switch (reason) {
      case ItemReason::kReached:
        ++reached_;
        blacklist_.Set(id,
                       tick + TickFromSeconds(profile_.tuning.consumable_blacklist_s));
        break;
      case ItemReason::kUnreachable:
        blacklist_.Set(id, tick + TickFromSeconds(profile_.tuning.consumable_blacklist_s) +
                               600);
        break;
      case ItemReason::kNeedSatisfied:
      case ItemReason::kItemGone:
        break;
      default:
        cooldown_.Set(id, tick + TickFromSeconds(profile_.tuning.abort_cooldown_s));
        global_cooldown_until_ =
            tick + TickFromSeconds(profile_.tuning.search_cooldown_s);
        ++aborts_;
        break;
    }

    CloseGoal(reason);
    d.action = reason == ItemReason::kReached ? ItemAction::kReached
                                              : ItemAction::kAbort;
    d.reason = reason;
    d.changed = true;
    d.has_goal = false;
    d.goal_id = id;
    d.goal_kind = kind;
    d.goal_pos = pos;
    d.utility = utility;
    std::snprintf(d.explain, sizeof(d.explain), "%s:%s(%d)", ItemActionName(d.action),
                  ItemReasonName(reason), id);
    return true;
  }

  void CloseGoal(ItemReason reason) {
    if (!has_goal_) return;
    if (nav_ != nullptr && goal_.nav_submitted) nav_->Cancel(goal_.item_id);
    has_goal_ = false;
    goal_ = GoalState();
    (void)reason;
  }

  void FillDecision(GoalDecision& d, ItemAction action, ItemReason reason, bool changed) {
    d.action = action;
    d.reason = reason;
    d.changed = changed;
    d.has_goal = has_goal_;
    if (!has_goal_) return;
    d.goal_id = goal_.item_id;
    d.goal_kind = goal_.kind;
    d.goal_weapon_index = goal_.weapon_index;
    d.goal_pos = goal_.pos;
    d.utility = goal_.utility;
    d.need = goal_.need;
    d.suppress_combat = goal_.survival;
    for (int i = 0; i < eval_count_; ++i) {
      if (evals_[i].item_id == goal_.item_id) {
        d.travel_s = evals_[i].terms.travel_s;
        d.distance_m = evals_[i].distance_m;
        break;
      }
    }
    std::snprintf(d.explain, sizeof(d.explain), "%s %s id=%d need=%.2f u=%.2f t=%.1fs",
                  ItemActionName(action), ItemKindName(goal_.kind), goal_.item_id,
                  goal_.need, goal_.utility, d.travel_s);
  }

  bool ThreatAbort(const ItemWorld& w, double distance_to_goal_m) const {
    const ThreatState& t = w.threat;
    if (t.visible_enemies <= 0 || t.nearest_enemy_m < 0.0) return false;
    if (distance_to_goal_m <= profile_.tuning.close_finish_radius_m) return false;
    if (ctx_.health_frac >= profile_.tuning.health_abort_frac) return false;
    return t.nearest_enemy_m <= profile_.tuning.enemy_abort_radius_m;
  }

  bool DamageAbort(const ItemWorld& w) const {
    if (damage_window_tick_ < 0) return false;
    const double lost = damage_window_health_ - w.self.health;
    if (lost <= 0.0) return false;
    const double frac = lost / (w.self.max_health > 0.0 ? w.self.max_health : 100.0);
    return frac > profile_.tuning.abort_damage_frac;
  }

  bool TimedOut(int tick) const {
    const int limit = TickFromSeconds(profile_.tuning.max_search_time_s);
    return (tick - goal_.started_tick) > (limit > 0 ? limit : 1);
  }

  bool CombatLock(const ItemWorld& w) const {
    if (!w.combat.engaged) return false;
    if (w.combat.combat_priority <= profile_.tuning.combat_lock_priority) return false;
    return ctx_.health_frac >= kUrgentHealthFrac;
  }

  void UpdateDamageWindow(const ItemWorld& w) {
    const int window = TickFromSeconds(profile_.tuning.damage_window_s);
    const int tick = w.combat.tick;
    if (damage_window_tick_ < 0 || (tick - damage_window_tick_) >= (window > 0 ? window : 1) ||
        w.self.health > damage_window_health_) {
      damage_window_tick_ = tick;
      damage_window_health_ = w.self.health;
    }
  }

  ItemProfile profile_{};
  ScoreContext ctx_{};
  GoalState goal_{};
  bool has_goal_ = false;
  NavigationSink* nav_ = nullptr;
  TimerTable cooldown_;
  TimerTable blacklist_;
  int global_cooldown_until_ = 0;
  int damage_window_tick_ = -1;
  double damage_window_health_ = 0.0;
  int eval_count_ = 0;
  ItemEvaluation evals_[kMaxItems];
  int last_tick_ = 0;
  int slot_ = 0;

  int ticks_processed_ = 0;
  int selections_ = 0;
  int switches_ = 0;
  int aborts_ = 0;
  int reached_ = 0;
  int timeouts_ = 0;
  int cooldown_blocks_ = 0;
  int combat_lock_blocks_ = 0;
  long long evaluations_ = 0;
};

}  // namespace itemai

#endif  // ITEMAI_ITEM_PLANNER_H

/* ======================================================================== */
/* botcore_adapter.h                                                        */
/* ======================================================================== */

#ifndef ITEMAI_BOTCORE_ADAPTER_H
#define ITEMAI_BOTCORE_ADAPTER_H

namespace itemai {

inline double BotcoreWeaponScore(int weapon_index, double distance_m,
                                 double range_preference) {
  return botcore::ScoreWeapon(weapon_index, distance_m, range_preference);
}

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
  BuildItemProfile(bp.tier, bp.persona, bp.seed, &p);
  return p;
}

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

inline uint32_t UsableWeaponMask(const SelfState& s) {
  uint32_t mask = 0;
  for (int i = 1; i <= kWeaponCount; ++i) {
    if (!WeaponOwned(s.owned_weapons, i)) continue;
    if (!WeaponHasAmmo(s.ammo, i)) continue;
    mask |= (1u << (i - 1));
  }
  return mask;
}

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

struct ItemDirectorIntent {
  bool steer_to_goal = false;
  bool suppress_combat = false;
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

#endif  // NAV_ITEM_BRIDGE_UPSTREAM_ITEMAI_MIRROR_H
