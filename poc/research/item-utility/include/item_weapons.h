// SPDX-License-Identifier: GPL-2.0-only
// item_weapons.h - minimal, injectable weapon knowledge for item valuation.
//
// WHY THIS EXISTS
//  The item layer must answer "is this ammo for a weapon I actually use?" and
//  "is this weapon better than the best one I already hold?". Both questions
//  need a damage/capability estimate per weapon. This header provides a
//  *stand-in table* with the same shape and ordering as
//  poc/botcore/bot_loadout.h so the prototype runs standalone. It is NOT a new
//  source of truth: at integration time the adapter in botcore_adapter.h
//  replaces the stand-in with botcore::ScoreWeapon, and
//  test_botcore_adapter.cpp measures the ranking agreement between the two.
//
// The numbers are RELATIVE CALIBRATION HYPOTHESES (see bot_loadout.h), not
// extracted retail constants. They only encode ordering knowledge: shotguns up
// close, sniper far, explosives risky near your own feet.

#ifndef ITEMAI_ITEM_WEAPONS_H
#define ITEMAI_ITEM_WEAPONS_H

#include <cmath>

#include "item_types.h"

namespace itemai {

struct WeaponTraits {
  int index = 0;
  double min_m = 0.0;    // below this the weapon is a poor choice
  double max_m = 0.0;    // beyond this it is effectively useless
  double dps_rel = 1.0;  // relative sustained damage
  double acc_near = 0.8; // hit probability near min_m
  double acc_far = 0.5;  // hit probability near max_m
  int ammo_cap = 0;      // 0 = no ammo needed (melee); else full reserve
  double self_blast_m = 0.0;  // 0 = no self-damage radius
};

inline const WeaponTraits& WeaponTraitAt(int index) {
  static const WeaponTraits kTable[kWeaponCount] = {
      /*  1 knife       */ {1, 0.0, 3.5, 1.0, 0.95, 0.20, 0, 0.0},
      /*  2 colt        */ {2, 0.0, 45.0, 1.6, 0.92, 0.55, 50, 0.0},
      /*  3 double colt */ {3, 0.0, 40.0, 2.0, 0.88, 0.45, 50, 0.0},
      /*  4 shotgun     */ {4, 0.0, 22.0, 3.9, 0.85, 0.25, 30, 0.0},
      /*  5 double shot */ {5, 0.0, 18.0, 5.5, 0.80, 0.15, 30, 0.0},
      /*  6 tommygun    */ {6, 0.0, 60.0, 3.2, 0.93, 0.72, 100, 0.0},
      /*  7 minigun     */ {7, 0.0, 90.0, 3.4, 0.90, 0.62, 200, 0.0},
      /*  8 rocket      */ {8, 12.0, 70.0, 5.0, 0.70, 0.55, 10, 5.0},
      /*  9 grenade     */ {9, 10.0, 55.0, 3.8, 0.45, 0.30, 10, 5.0},
      /* 10 chainsaw    */ {10, 0.0, 3.0, 1.2, 0.95, 0.20, 0, 0.0},
      /* 11 flamer      */ {11, 0.0, 14.0, 3.4, 0.90, 0.35, 100, 0.0},
      /* 12 laser       */ {12, 0.0, 80.0, 4.4, 0.85, 0.70, 50, 0.0},
      /* 13 sniper      */ {13, 20.0, 150.0, 5.2, 0.55, 0.97, 20, 0.0},
      /* 14 iron cannon */ {14, 14.0, 90.0, 5.6, 0.60, 0.70, 15, 4.0},
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

// `ammo_by_index` is a SelfState::ammo array with 15 entries (1..14 used).
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

// Interpolated hit probability at distance d.
inline double AccuracyAt(const WeaponTraits& w, double distance_m) {
  if (distance_m <= w.min_m) return w.acc_near;
  if (distance_m >= w.max_m) return w.acc_far;
  const double span = w.max_m - w.min_m;
  const double t = span > 1e-6 ? (distance_m - w.min_m) / span : 0.0;
  return w.acc_near + (w.acc_far - w.acc_near) * t;
}

// 1.0 inside the useful band, tapering to 0 outside it.
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

// Stand-in utility of one weapon at a distance. Same shape as
// botcore::ScoreWeapon so a swap keeps the decision semantics comparable.
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
