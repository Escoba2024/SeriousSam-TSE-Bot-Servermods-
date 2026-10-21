// bot_loadout.h - engine-free weapon scoring and switch hysteresis.
//
// Replaces the fixed close/mid/far priority lists of botcore_ai.h::SelectWeapon
// for the profile-driven path. The legacy function is left untouched so that
// the qualified behaviour remains available and testable.
//
// WEAPON INDICES: EntitiesMP/PlayerWeapons.es WeaponType
//   1 knife, 2 colt, 3 double colt, 4 shotgun, 5 double shotgun, 6 tommygun,
//   7 minigun, 8 rocket, 9 grenade, 10 chainsaw, 11 flamer, 12 laser,
//   13 sniper, 14 iron cannon.
//
// THE NUMBERS BELOW ARE RELATIVE CALIBRATION HYPOTHESES, NOT EXTRACTED GAME
// CONSTANTS. They encode *ordering* knowledge (shotguns up close, sniper far,
// explosives risky near your own feet) and keep the scoring bounded. Any tuned
// damage table from the project's own measurements can replace them without
// touching the scoring code.

#ifndef BOTCORE_BOT_LOADOUT_H
#define BOTCORE_BOT_LOADOUT_H

#include <cmath>
#include <cstdint>

#include "bot_profile.h"

namespace botcore {

constexpr int kWeaponCount = 14;  // indices 1..14

struct WeaponProfile {
  int index;
  double min_m;        // below this the weapon is a poor choice
  double max_m;        // beyond this it is effectively useless
  double dps_rel;      // relative sustained damage
  double acc_near;     // hit probability near min_m
  double acc_far;      // hit probability near max_m
  double self_blast_m; // 0 = no self-damage; else keep this distance
  double proj_speed;   // 0 = hitscan, else units/s (used for lead)
};

inline const WeaponProfile& WeaponAt(int index) {
  static const WeaponProfile kTable[kWeaponCount] = {
      /*  1 knife        */ {1, 0.0, 3.5, 1.0, 0.95, 0.20, 0.0, 0.0},
      /*  2 colt         */ {2, 0.0, 45.0, 1.6, 0.92, 0.55, 0.0, 0.0},
      /*  3 double colt  */ {3, 0.0, 40.0, 2.0, 0.88, 0.45, 0.0, 0.0},
      /*  4 shotgun      */ {4, 0.0, 22.0, 3.9, 0.85, 0.25, 0.0, 0.0},
      /*  5 double shot  */ {5, 0.0, 18.0, 5.5, 0.80, 0.15, 0.0, 0.0},
      /*  6 tommygun     */ {6, 0.0, 60.0, 3.2, 0.93, 0.72, 0.0, 0.0},
      /*  7 minigun      */ {7, 0.0, 90.0, 3.4, 0.90, 0.62, 0.0, 0.0},
      /*  8 rocket       */ {8, 12.0, 70.0, 5.0, 0.70, 0.55, 5.0, 20.0},
      /*  9 grenade      */ {9, 10.0, 55.0, 3.8, 0.45, 0.30, 5.0, 12.0},
      /* 10 chainsaw     */ {10, 0.0, 3.0, 1.2, 0.95, 0.20, 0.0, 0.0},
      /* 11 flamer       */ {11, 0.0, 14.0, 3.4, 0.90, 0.35, 0.0, 15.0},
      /* 12 laser        */ {12, 0.0, 80.0, 4.4, 0.85, 0.70, 0.0, 0.0},
      /* 13 sniper       */ {13, 20.0, 150.0, 5.2, 0.55, 0.97, 0.0, 0.0},
      /* 14 iron cannon  */ {14, 14.0, 90.0, 5.6, 0.60, 0.70, 4.0, 25.0},
  };
  if (index < 1) index = 1;
  if (index > kWeaponCount) index = kWeaponCount;
  return kTable[index - 1];
}

inline const char* WeaponName(int index) {
  static const char* kNames[kWeaponCount] = {
      "knife", "colt", "double-colt", "shotgun", "double-shotgun", "tommygun",
      "minigun", "rocket", "grenade", "chainsaw", "flamer", "laser", "sniper",
      "cannon"};
  if (index < 1 || index > kWeaponCount) return "none";
  return kNames[index - 1];
}

inline bool WeaponUsable(uint32_t usable_mask, int index) {
  return index >= 1 && index <= kWeaponCount &&
         (usable_mask & (1u << (index - 1))) != 0u;
}

// Interpolated hit probability at distance d.
inline double AccuracyAt(const WeaponProfile& w, double distance_m) {
  if (distance_m <= w.min_m) return w.acc_near;
  if (distance_m >= w.max_m) return w.acc_far;
  const double span = w.max_m - w.min_m;
  const double t = span > 1e-6 ? (distance_m - w.min_m) / span : 0.0;
  return w.acc_near + (w.acc_far - w.acc_near) * t;
}

// 1.0 inside the useful band, tapering to 0 outside it.
inline double RangeFit(const WeaponProfile& w, double distance_m) {
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

// Utility of one weapon. `range_preference` comes from the personality
// (-1 close .. +1 far) and only tilts the choice; it never changes what the
// bot is mechanically able to do.
inline double ScoreWeapon(int index, double distance_m, double range_preference) {
  if (index < 1 || index > kWeaponCount) return 0.0;
  const WeaponProfile& w = WeaponAt(index);
  double score = w.dps_rel * AccuracyAt(w, distance_m) * RangeFit(w, distance_m);
  if (w.self_blast_m > 0.0 && distance_m < w.self_blast_m) score *= 0.05;
  // Band position mapped to [-1, 1] over a plausible engagement range.
  double pos = (distance_m - 12.0) / 30.0;
  pos = pos < -1.0 ? -1.0 : (pos > 1.0 ? 1.0 : pos);
  const double tilt = 1.0 + 0.35 * range_preference * pos;
  return score * (tilt > 0.2 ? tilt : 0.2);
}

inline int BestWeapon(uint32_t usable_mask, double distance_m, double range_preference) {
  int best = -1;
  double best_score = 0.0;
  for (int i = 1; i <= kWeaponCount; ++i) {
    if (!WeaponUsable(usable_mask, i)) continue;
    const double s = ScoreWeapon(i, distance_m, range_preference);
    if (s > best_score) {
      best_score = s;
      best = i;
    }
  }
  return best;
}

/* ------------------------------------------------------------------------ */
/* Hysteresis                                                                */
/* ------------------------------------------------------------------------ */

struct LoadoutInput {
  uint32_t usable_mask = 0;       // after ammo filtering (CombatUsableWeapons)
  double distance_m = 0.0;        // to the current target, 0 if unknown
  double range_preference = 0.0;  // personality tilt
  bool has_target = false;
  // VORSCHLAG, default off: fall back to the knife while travelling, like a
  // player who wants the movement bonus. Costs a weapon-select pulse.
  bool knife_while_travelling = false;
};

class WeaponSelector {
 public:
  void Configure(const SkillParams& skill) { skill_ = skill; Reset(); }

  void Reset() {
    current_ = 0;
    switch_tick_ = -1000000;
    locked_ = false;
  }

  // Returns the weapon the bot wants to hold. Caller must still translate the
  // number into the retail select-group pulse (CombatWeaponInput).
  int Update(const LoadoutInput& in, int tick) {
    if (current_ != 0 && !WeaponUsable(in.usable_mask, current_)) {
      locked_ = false;  // out of ammo or lost the weapon: immediate rethink
    }

    if (!in.has_target) {
      if (in.knife_while_travelling && WeaponUsable(in.usable_mask, 1) &&
          current_ != 1 && DwellElapsed(tick)) {
        current_ = 1;
        switch_tick_ = tick;
      }
      return current_ == 0 ? Fallback(in.usable_mask) : current_;
    }

    const int best = BestWeapon(in.usable_mask, in.distance_m, in.range_preference);
    if (best < 0) return Fallback(in.usable_mask);
    if (current_ == 0 || !WeaponUsable(in.usable_mask, current_)) {
      current_ = best;
      switch_tick_ = tick;
      locked_ = true;
      return current_;
    }
    if (best == current_) return current_;

    // Keep the current weapon unless the alternative is clearly better AND
    // the minimum hold time has passed. This is what stops the target/weapon
    // ping-pong near a range boundary.
    const double s_now = ScoreWeapon(current_, in.distance_m, in.range_preference);
    const double s_best = ScoreWeapon(best, in.distance_m, in.range_preference);
    if (!DwellElapsed(tick)) return current_;
    if (s_best > s_now * skill_.switch_margin) {
      current_ = best;
      switch_tick_ = tick;
    }
    return current_;
  }

  int current() const { return current_; }
  void ForceWeapon(int index) {
    current_ = index;
    locked_ = index != 0;
  }

 private:
  bool DwellElapsed(int tick) const {
    const int dwell = static_cast<int>(skill_.weapon_dwell_s * kProfileTickHz + 0.5);
    return (tick - switch_tick_) >= (dwell > 0 ? dwell : 0);
  }

  static int Fallback(uint32_t mask) {
    for (int i = 1; i <= kWeaponCount; ++i) {
      if (WeaponUsable(mask, i)) return i;
    }
    return 1;  // knife is always owned in deathmatch spawns
  }

  SkillParams skill_{};
  int current_ = 0;
  int switch_tick_ = -1000000;
  bool locked_ = false;
};

}  // namespace botcore

#endif  // BOTCORE_BOT_LOADOUT_H
