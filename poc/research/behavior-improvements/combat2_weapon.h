// combat2_weapon.h - candidate weapon scoring (research overlay, engine-free).
//
// Baseline defect (PR #62 F-1, reproduced 25.10.2026 against botcore):
//   botcore::BestWeapon(all-weapons) returns LASER from 4 m to 30 m and CANNON
//   beyond, identically for range_preference -0.55 / 0 / +0.85. Shotgun and
//   sniper are dead content; personas are indistinguishable by loadout.
// Root causes in botcore::ScoreWeapon:
//   * RangeFit() is flat 1.0 across the whole [min,max] band, so the weapon
//     with the best dps*acc product wins everywhere inside its band;
//   * the persona tilt uses the *target distance*, identical for every weapon
//     candidate, so it scales all scores equally and cannot change ranking
//     except at tilt sign flips;
//   * AccuracyAt() linear interpolation over-credits the laser at mid range.
//
// Candidate model:
//   * every weapon gets a sweet spot (optimal_m) and a band width (sigma_m);
//     effectiveness is a smooth bell around the sweet spot, so weapons own
//     niches instead of plateaus;
//   * peak effective DPS is re-balanced (laser no longer top everywhere);
//   * persona affinity is per weapon-class, derived from the weapon's own
//     optimal range AND an explicit class table (aggressor->shotguns,
//     marksman->sniper, ...), strong enough to change rankings;
//   * skill-gated weapon knowledge: tiers 1-2 deterministically sometimes keep
//     a familiar suboptimal weapon (human-like), tiers 4-5 pick near-optimal;
//   * self-blast safety kept and strengthened (hard veto below safe range
//     unless nothing else is usable);
//   * switch hysteresis reuses botcore dwell/margin semantics.
//
// Numbers are relative calibration hypotheses (same status as botcore's own
// table), NOT extracted Retail constants. NOT_TESTED_RETAIL.
#ifndef BEHAVIOR_IMPROVEMENTS_COMBAT2_WEAPON_H
#define BEHAVIOR_IMPROVEMENTS_COMBAT2_WEAPON_H

#include <cmath>
#include <cstdint>

#include "bot_loadout.h"  // WeaponName/WeaponUsable/kWeaponCount (read-only)
#include "bot_profile.h"

namespace combat2 {

struct WeaponCurve {
  double optimal_m;   // sweet spot
  double sigma_m;     // bell width
  double peak_dps;    // relative effective DPS at the sweet spot
  double min_safe_m;  // self-blast veto below this (0 = none)
  double hard_max_m;  // beyond this: useless (score -> ~0)
};

inline const WeaponCurve& CurveAt(int index) {
  static const WeaponCurve kT[botcore::kWeaponCount] = {
      /* 1 knife        */ {1.5, 1.2, 2.2, 0.0, 3.5},
      /* 2 colt         */ {14.0, 12.0, 2.0, 0.0, 50.0},
      /* 3 double colt  */ {11.0, 10.0, 2.5, 0.0, 42.0},
      /* 4 shotgun      */ {6.0, 4.5, 5.2, 0.0, 24.0},
      /* 5 double shot  */ {4.5, 3.4, 6.4, 0.0, 19.0},
      /* 6 tommygun     */ {15.0, 11.0, 3.9, 0.0, 60.0},
      /* 7 minigun      */ {17.0, 13.0, 4.1, 0.0, 75.0},
      /* 8 rocket       */ {24.0, 13.0, 4.6, 9.0, 75.0},
      /* 9 grenade      */ {18.0, 9.0, 3.4, 8.0, 50.0},
      /*10 chainsaw     */ {1.5, 1.1, 2.6, 0.0, 3.0},
      /*11 flamer       */ {6.5, 3.8, 4.4, 0.0, 14.0},
      /*12 laser        */ {26.0, 15.0, 4.0, 0.0, 85.0},
      /*13 sniper       */ {55.0, 30.0, 4.8, 0.0, 160.0},
      /*14 iron cannon  */ {32.0, 17.0, 4.5, 10.0, 95.0},
  };
  if (index < 1) index = 1;
  if (index > botcore::kWeaponCount) index = botcore::kWeaponCount;
  return kT[index - 1];
}

// Explicit persona x weapon-class affinity in [-1,1]. Rows = personas
// (aggressor, survivor, duelist, controller, marksman, flaky), columns are
// weapon indices 1..14. This is *preference*, never capability.
inline double ClassAffinity(int persona, int weapon) {
  static const double kA[6][14] = {
      // knf  colt dclt shot dshot tommy mini  rock gren  saw  flam laser snip cann
      { 0.2, -0.2, 0.1, 0.9,  1.0,  0.3,  0.4,  0.2, 0.0,  0.4, 0.7, -0.3, -0.9, 0.1},  // aggressor
      {-0.4,  0.3, 0.2, 0.1, -0.1,  0.5,  0.4,  0.3, 0.2, -0.6, -0.3, 0.5,  0.4, 0.3},  // survivor
      {-0.2,  0.2, 0.5, 0.4,  0.3,  0.9,  0.8,  0.3, 0.0, -0.2, 0.1,  0.2, -0.4, 0.0},  // duelist
      {-0.3,  0.2, 0.1, 0.0, -0.2,  0.4,  0.5,  0.7, 0.5, -0.5, -0.2, 0.6,  0.5, 0.6},  // controller
      {-0.8,  0.1, -0.2,-0.7, -0.9,  0.0,  0.1,  0.2, -0.2,-0.9, -0.8, 0.7,  1.0, 0.4},  // marksman
      { 0.0,  0.0, 0.1, 0.2,  0.2,  0.2,  0.1,  0.2, 0.3,  0.0, 0.1,  0.1,  0.0, 0.2},  // flaky
  };
  if (persona < 0) persona = 0;
  if (persona > 5) persona = 5;
  if (weapon < 1 || weapon > 14) return 0.0;
  return kA[persona][weapon - 1];
}

inline double BellFit(const WeaponCurve& w, double d) {
  if (d >= w.hard_max_m) {
    const double over = d - w.hard_max_m;
    return over >= 10.0 ? 0.0 : 0.05 * (1.0 - over / 10.0);
  }
  const double z = (d - w.optimal_m) / (w.sigma_m > 0.1 ? w.sigma_m : 0.1);
  double f = std::exp(-0.5 * z * z);
  if (f < 0.02) f = 0.02;  // never mathematically zero inside hard range
  return f;
}

// Precision/splash weapons only pay off in skilled hands. A tier-3 marksman
// who always reaches for the sniper loses to a cannon/laser baseline in the
// duel battery (cross 40 m cell) - so competence per weapon family is part of
// skill, applied identically for every persona of the tier.
inline double WeaponSkillFactor(int index, int tier) {
  const int i = (tier < 1 ? 1 : (tier > 5 ? 5 : tier)) - 1;
  static const double kSniper[5] = {0.40, 0.55, 0.72, 0.90, 1.05};
  static const double kHeavy[5] = {0.65, 0.75, 0.85, 0.95, 1.00};   // rocket/grenade/cannon
  static const double kAuto[5] = {1.00, 1.00, 1.00, 1.00, 1.00};
  if (index == 13) return kSniper[i];
  if (index == 8 || index == 9 || index == 14) return kHeavy[i];
  return kAuto[i];
}

// Candidate score. persona comes from BotProfile (-1 = neutral test mode).
inline double ScoreWeapon2(int index, double distance_m, int persona,
                           double range_preference, int tier = 3) {
  if (index < 1 || index > botcore::kWeaponCount) return 0.0;
  const WeaponCurve& w = CurveAt(index);
  if (w.min_safe_m > 0.0 && distance_m < w.min_safe_m) return 0.001;  // veto-ish
  double score = w.peak_dps * BellFit(w, distance_m) * WeaponSkillFactor(index, tier);
  // Persona tilt keyed on the WEAPON's niche (fixes baseline's no-op tilt):
  double niche = (w.optimal_m - 15.0) / 30.0;
  niche = niche < -1.0 ? -1.0 : (niche > 1.0 ? 1.0 : niche);
  double persona_factor = 1.0 + 0.45 * range_preference * niche;
  if (persona >= 0) persona_factor *= 1.0 + 0.55 * ClassAffinity(persona, index);
  // Cap stacked preference: taste may tilt, never override physics/skill.
  persona_factor = persona_factor < 0.55 ? 0.55 : (persona_factor > 1.60 ? 1.60 : persona_factor);
  score *= persona_factor;
  return score > 0.0 ? score : 0.0;
}

inline int BestWeapon2(uint32_t mask, double d, int persona, double range_pref,
                       int* second_out = nullptr, int tier = 3) {
  int best = -1, second = -1;
  double sb = 0.0, ss = 0.0;
  for (int i = 1; i <= botcore::kWeaponCount; ++i) {
    if (!botcore::WeaponUsable(mask, i)) continue;
    const double s = ScoreWeapon2(i, d, persona, range_pref, tier);
    if (s > sb) { ss = sb; second = best; sb = s; best = i; }
    else if (s > ss) { ss = s; second = i; }
  }
  if (second_out) *second_out = second;
  return best;
}

// Deterministic hash for skill-gated suboptimal picks (no RNG state needed).
inline uint32_t Hash32(uint32_t x) {
  x ^= x >> 16; x *= 0x7feb352du; x ^= x >> 15; x *= 0x846ca68bu; x ^= x >> 16;
  return x;
}

// Probability that a tier keeps/picks the 2nd-best weapon at a re-evaluation:
// weapon *knowledge* is part of skill, so beginners err visibly but bounded.
inline double SuboptimalPickP(int tier) {
  static const double kP[5] = {0.35, 0.22, 0.10, 0.04, 0.0};
  const int i = (tier < 1 ? 1 : (tier > 5 ? 5 : tier)) - 1;
  return kP[i];
}

class WeaponSelector2 {
 public:
  void Configure(const botcore::SkillParams& skill, int tier, int persona,
                 double range_preference, uint32_t seed) {
    skill_ = skill; tier_ = tier; persona_ = persona;
    range_pref_ = range_preference; seed_ = seed ? seed : 1u; Reset();
  }
  void Reset() { current_ = 0; switch_tick_ = -1000000; switches_ = 0; }
  int current() const { return current_; }
  int switches() const { return switches_; }

  int Update(uint32_t mask, double distance_m, bool has_target, int tick) {
    if (current_ != 0 && !botcore::WeaponUsable(mask, current_)) current_ = 0;
    if (!has_target) return current_ == 0 ? Fallback(mask) : current_;
    int second = -1;
    int best = BestWeapon2(mask, distance_m, persona_, range_pref_, &second, tier_);
    if (best < 0) return Fallback(mask);
    // Skill-gated knowledge error, stable per dwell window (no per-tick flicker):
    const int window = tick / 40;  // 2 s windows at 20 Hz
    const double u = (Hash32(seed_ ^ (uint32_t)window * 2654435761u) & 0xffffff) / 16777216.0;
    if (second > 0 && u < SuboptimalPickP(tier_)) best = second;
    if (current_ == 0) { current_ = best; switch_tick_ = tick; return current_; }
    if (best == current_) return current_;
    const int dwell = (int)(skill_.weapon_dwell_s * botcore::kProfileTickHz + 0.5);
    if (tick - switch_tick_ < dwell) return current_;
    const double s_now = ScoreWeapon2(current_, distance_m, persona_, range_pref_, tier_);
    const double s_best = ScoreWeapon2(best, distance_m, persona_, range_pref_, tier_);
    if (s_best > s_now * skill_.switch_margin) {
      current_ = best; switch_tick_ = tick; ++switches_;
    }
    return current_;
  }

 private:
  static int Fallback(uint32_t mask) {
    for (int i = 1; i <= botcore::kWeaponCount; ++i)
      if (botcore::WeaponUsable(mask, i)) return i;
    return 1;
  }
  botcore::SkillParams skill_{};
  int tier_ = 3, persona_ = -1, current_ = 0, switch_tick_ = -1000000, switches_ = 0;
  double range_pref_ = 0.0;
  uint32_t seed_ = 1;
};

}  // namespace combat2
#endif
