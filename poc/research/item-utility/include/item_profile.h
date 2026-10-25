// SPDX-License-Identifier: GPL-2.0-only
// item_profile.h - skill/personality inputs and tuning for item decisions.
//
// SEPARATION RULE (identical in spirit to botcore::SkillUnaffectedByPersonality)
//  - The SKILL block describes *decision quality*: how far ahead the bot plans,
//    how correctly it prices risk, how disciplined it is, how noisy its
//    tie-breaks are.
//  - The PERSONALITY block describes *preferences*: which kind of resource it
//    wants, and how cautious it is.
//  Nothing in the skill block depends on the persona and vice versa; the test
//  suite proves this block-wise (TestProfileSeparation).
//
// All numbers are calibration hypotheses. None of them is a retail constant,
// and none was extracted from CecilBotMod.

#ifndef ITEMAI_ITEM_PROFILE_H
#define ITEMAI_ITEM_PROFILE_H

#include <cmath>
#include <cstdint>

#include "item_types.h"

namespace itemai {

constexpr int kSkillTierCount = 5;    // 1 beginner .. 5 very good
constexpr int kPersonalityCount = 6;

/* ------------------------------------------------------------------------ */
/* Blocks                                                                    */
/* ------------------------------------------------------------------------ */

struct ItemSkillBlock {
  int tier = 3;                   // 1..5
  double planning_horizon_s = 6;  // how far ahead a pickup is valued
  double risk_awareness = 0.65;   // 0..1, correctness of danger pricing
  double discipline = 0.62;       // 0..1, sticks to a sensible plan
  double tie_noise = 0.009;       // amplitude of the deterministic tie-break
};

struct ItemPersonalityBlock {
  double health_appetite = 1.0;    // 0..1.6
  double armor_appetite = 1.0;
  double ammo_appetite = 1.0;
  double weapon_appetite = 1.0;
  double powerup_appetite = 1.0;
  double strategic_appetite = 1.0;
  double caution = 0.5;            // 0..1
  double aggression = 0.5;         // 0..1
};

struct ItemTuning {
  double commit_margin = 0.20;        // new goal must beat current by this frac
  double min_commit_s = 1.2;          // dwell before a voluntary switch
  double search_cooldown_s = 1.8;     // global pause after an abort
  double abort_cooldown_s = 1.4;      // per-item pause after an abort
  double abort_damage_frac = 0.34;    // health fraction lost in the window
  double damage_window_s = 2.0;
  double enemy_abort_radius_m = 18.0; // "enemy this close" break-off radius
  double health_abort_frac = 0.55;    // below this health a threat aborts
  double max_search_time_s = 8.0;     // per-goal time limit
  double min_utility = 0.12;          // below this nothing is worth doing
  double threat_weight = 0.65;
  double time_weight = 0.55;
  double deviation_weight = 0.55;     // cost of leaving the fight
  double combat_lock_priority = 0.80; // hard gate while this committed
  double close_finish_radius_m = 2.5; // finish a health pickup under fire
  double memory_horizon_s = 6.0;      // staleness normalisation
  double weapon_reference_m = 20.0;   // range used to value a weapon item
  double consumable_blacklist_s = 30.0;  // assume a picked item is gone
};

struct ItemProfile {
  ItemSkillBlock skill;
  ItemPersonalityBlock persona;
  ItemTuning tuning;
  uint32_t seed = 1u;
  int tier = 3;
  int persona_index = 0;
};

/* ------------------------------------------------------------------------ */
/* Tables                                                                    */
/* ------------------------------------------------------------------------ */

// Monotone in tier: a higher tier never plans less far ahead and never prices
// risk less correctly. tie_noise shrinks with skill (sloppier tie-breaks are a
// beginner trait), which is why it is a skill field and not a persona field.
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
  // health, armor, ammo, weapon, powerup, strategic, caution, aggression
  static const ItemPersonalityBlock kTable[kPersonalityCount] = {
      {0.75, 0.80, 1.10, 1.25, 1.10, 0.70, 0.25, 0.90},  // 0 aggressor
      {1.45, 1.30, 1.00, 0.90, 0.80, 0.90, 0.85, 0.35},  // 1 survivor
      {1.00, 1.00, 1.05, 1.05, 1.00, 0.80, 0.50, 0.65},  // 2 duelist
      {1.00, 1.00, 0.95, 0.95, 1.00, 1.30, 0.60, 0.45},  // 3 controller
      {0.95, 1.05, 1.20, 1.15, 0.90, 0.85, 0.60, 0.50},  // 4 marksman
      {1.00, 1.00, 1.00, 1.00, 1.00, 1.00, 0.50, 0.60},  // 5 flaky
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

/* ------------------------------------------------------------------------ */
/* Tuning derivation - documented split between skill and personality        */
/* ------------------------------------------------------------------------ */

inline ItemTuning TuningFor(const ItemSkillBlock& s, const ItemPersonalityBlock& p) {
  ItemTuning t;
  // Commitment: cautious and undisciplined bots change their mind more easily
  // and hold new goals for less time. Bounded, so no bot is paralysed.
  t.commit_margin = Clamp(0.12 + 0.18 * p.caution + 0.10 * (1.0 - s.discipline),
                          0.10, 0.45);
  t.min_commit_s = Clamp(1.60 - 0.90 * s.discipline + 0.40 * p.caution, 0.40, 2.60);
  t.search_cooldown_s = Clamp(2.50 - 1.00 * s.discipline, 1.00, 3.00);
  t.abort_cooldown_s = Clamp(0.90 + 1.10 * p.caution, 0.80, 2.20);
  // Abort sensitivity: a cautious bot breaks off earlier and at lower damage.
  t.abort_damage_frac = Clamp(0.42 - 0.18 * p.caution, 0.20, 0.45);
  t.enemy_abort_radius_m = Clamp(12.0 + 12.0 * p.caution, 10.0, 26.0);
  t.health_abort_frac = Clamp(0.70 - 0.30 * p.caution, 0.35, 0.75);
  // Time budget grows with the planning horizon, shrinks with caution.
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

/* ------------------------------------------------------------------------ */
/* Construction / validation                                                 */
/* ------------------------------------------------------------------------ */

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
  for (double a : appetites) {
    if (!Finite(a) || a < 0.0 || a > 2.0) return ProfileError::kOutOfRange;
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

// Seed derivation mirrors botcore::DeriveSeed's intent: two bots never share a
// deterministic tie-break stream, even for the same tier/persona.
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
