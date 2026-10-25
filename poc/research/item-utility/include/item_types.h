// SPDX-License-Identifier: GPL-2.0-only
// item_types.h - shared, engine-free primitive types of the item utility layer.
//
// SCOPE (research prototype, offline only)
//  This directory is an *independent decision layer*: it answers exactly one
//  question - "which item should the bot go for, and why?" - and nothing else.
//  It contains no navigation, no pathfinding, no engine access and no I/O in
//  the decision code. Every world fact arrives as a synthetic, validated
//  snapshot; every outgoing intent leaves through navigation_interface.h.
//
// PROVENANCE
//  Original Alpha-Gaming code. CecilBotMod (GPL-2.0, DreamyCecil) was read as
//  an *algorithmic reference* only (see docs/research/item-utility/
//  2026-10-25-cecilbotmod-item-logic-analysis.md). No Cecil source text, no
//  entity class, no setting name and no numeric constant was copied.
//
// UNITS
//  metres, metres/second, degrees, seconds. Tick rate 20 Hz.

#ifndef ITEMAI_ITEM_TYPES_H
#define ITEMAI_ITEM_TYPES_H

#include <cmath>
#include <cstdint>

namespace itemai {

/* ------------------------------------------------------------------------ */
/* Limits and constants                                                      */
/* ------------------------------------------------------------------------ */

constexpr int kMaxItems = 64;        // hard cap per world snapshot
constexpr int kWeaponCount = 14;     // EntitiesMP/PlayerWeapons.es WeaponType
constexpr int kMaxWeaponIndex = kWeaponCount;

constexpr double kTickHz = 20.0;                  // Engine/Base/Timer.cpp
constexpr double kTickQuantum = 1.0 / kTickHz;
constexpr double kDefaultMoveSpeedMps = 10.0;     // plr_fSpeedForward scale

constexpr double kArrivalRadiusM = 1.5;   // navigation target tolerance
constexpr double kNeedEpsilon = 0.02;     // below this an item is "not needed"

/* ------------------------------------------------------------------------ */
/* Scalar helpers                                                            */
/* ------------------------------------------------------------------------ */

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

// SplitMix32 finalizer: deterministic, stateless, no allocation.
inline uint32_t Hash32(uint32_t x) {
  x += 0x9E3779B9u;
  x ^= x >> 16;
  x *= 0x7FEB352Du;
  x ^= x >> 15;
  x *= 0x846CA68Bu;
  x ^= x >> 16;
  return x;
}

// Deterministic per-bot, per-item tie-breaker in [0, 1). Used only for exact
// utility ties, never as a "random success chance".
inline double TieBreakUnit(uint32_t seed, int item_id, int slot) {
  const uint32_t h = Hash32(seed ^ (static_cast<uint32_t>(item_id) * 0x85EBCA6Bu) ^
                            (static_cast<uint32_t>(slot + 1) * 0xC2B2AE35u));
  return static_cast<double>(h & 0xFFFFFFu) / 16777215.0;
}

/* ------------------------------------------------------------------------ */
/* Geometry                                                                  */
/* ------------------------------------------------------------------------ */

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

/* ------------------------------------------------------------------------ */
/* Item taxonomy                                                             */
/* ------------------------------------------------------------------------ */

// One enumeration per *decision-relevant* category. The retail entity classes
// map onto these in the integration layer (see the integration plan); the
// decision code never knows a class name or a DLL pointer.
enum class ItemKind : uint8_t {
  kNone = 0,
  kHealth = 1,     // CHealthItem-like: restores health points
  kArmor = 2,      // CArmorItem-like: restores armor points
  kAmmo = 3,       // CAmmoItem/CAmmoPack-like: refills one weapon's ammo
  kWeapon = 4,     // CWeaponItem-like: grants a weapon
  kPowerup = 5,    // CPowerUpItem-like: temporary buff
  kStrategic = 6,  // marker/resource/position with caller-supplied value
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

/* ------------------------------------------------------------------------ */
/* Decision vocabulary (shared by scoring, planner and telemetry)            */
/* ------------------------------------------------------------------------ */

enum class ItemAction : uint8_t {
  kNone = 0,    // nothing to do, no goal
  kSelect = 1,  // a new goal was committed
  kKeep = 2,    // the current goal survives re-evaluation
  kSwitch = 3,  // a better goal replaced the current one
  kAbort = 4,   // the current goal was dropped
  kReached = 5  // the goal is considered arrived/consumed
};

enum class ItemReason : uint8_t {
  kNone = 0,
  kNoCandidate,      // nothing passed the utility threshold
  kSelected,         // best eligible candidate committed
  kKept,             // current goal still best / protected by hysteresis
  kSwitched,         // better candidate beat the commit margin
  kReached,          // inside the arrival radius
  kNeedSatisfied,    // the need that justified the goal is gone
  kItemGone,         // respawned away / removed / no longer in the world
  kThreatOverride,   // enemy pressure forces a break-off
  kDamageAbort,      // accumulated damage exceeded the abort budget
  kTimeout,          // max search time for this goal exceeded
  kOutOfRange,       // travel estimate exceeds the search budget
  kCooldown,         // global or per-item search cooldown active
  kCombatLock,       // combat priority forbids leaving the fight
  kHysteresisHold,   // commit/dwell window protects the current goal
  kUnreachable,      // navigation reported "no path"
  kInvalidWorld,     // snapshot failed validation (fail closed)
  kAmmoStarved,      // no ammo/no usable weapon: item search cannot fix it
  kStalled           // navigation reports no progress
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
