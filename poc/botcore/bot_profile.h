// bot_profile.h - engine-free skill/personality model for the vanilla bot
// client. Companion to botcore.h / botcore_ai.h; verified in isolation by
// test_bot_human_ai.cpp and consumed by the GameMP integration patch
// (poc/patch/0008-gamemp-human-bot-ai.patch).
//
// HARD SCOPE RULES
//  - pure data + pure functions: no engine calls, no I/O, no allocation;
//  - every value is a *calibration hypothesis*, not a measured human constant;
//  - skill and personality are strictly orthogonal: personality may NEVER
//    change a perception or aim parameter. This is enforced by
//    ValidateProfilePair() and checked in the unit tests, so a "very good"
//    bot and a "beginner" bot of the same tier stay comparable in raw
//    mechanical capability regardless of temperament.
//
// UNITS AND TIME BASE
//  - angles: degrees
//  - distances: metres (Serious Engine world units are metres at 1.0 scale)
//  - speeds: metres/second, degrees/second, degrees/second^2
//  - time: seconds; the game tick is 20 Hz (kTickQuantum = 0.05 s in
//    Engine/Base/Timer.cpp), so 1 s == 20 ticks.

#ifndef BOTCORE_BOT_PROFILE_H
#define BOTCORE_BOT_PROFILE_H

#include <cmath>
#include <cstddef>
#include <cstdint>

namespace botcore {

constexpr double kPi = 3.14159265358979323846;
constexpr double kDegToRad = kPi / 180.0;
constexpr double kRadToDeg = 180.0 / kPi;

constexpr int kSkillTierCount = 5;    // 1..5
constexpr int kPersonalityCount = 6;  // 0..5
constexpr double kProfileTickHz = 20.0;

/* ------------------------------------------------------------------------ */
/* Skill tiers                                                               */
/* ------------------------------------------------------------------------ */

// 1 = beginner, 2 = casual, 3 = average, 4 = advanced, 5 = very good player.
enum class SkillTier {
  kBeginner = 1,
  kCasual = 2,
  kAverage = 3,
  kAdvanced = 4,
  kExpert = 5
};

// Every field is independent on purpose: reaction speed, tracking quality,
// trigger discipline and weapon knowledge must be able to differ in any
// combination. A slow reactor may still aim very precisely, and vice versa.
struct SkillParams {
  /* --- perception ------------------------------------------------------ */
  double reaction_s;        // continuous LOS needed before a target is usable
  double memory_s;          // how long a lost target is remembered
  double fov_half_deg;      // half-angle of the awareness cone
  double sight_range_m;     // maximum acquisition distance
  double alert_window_s;    // "what hit me?" glance after taking damage
  int    max_los_per_tick;  // hard per-tick line-of-sight budget

  /* --- aiming ---------------------------------------------------------- */
  double turn_rate_deg_s;    // maximum yaw/pitch rate
  double turn_accel_deg_s2;  // maximum angular acceleration
  double aim_sigma_deg;      // std-dev of the correlated aim bias
  double aim_corr_s;         // correlation time of that bias
  double overshoot;          // 0..1, weak braking -> overshoot past the target
  double fire_tol_deg;       // crosshair tolerance before pulling the trigger
  double settle_s;           // in-tolerance time required before firing
  double prediction_gain;    // 0..1, lead compensation competence

  /* --- loadout --------------------------------------------------------- */
  double weapon_dwell_s;     // minimum hold time before re-evaluating a weapon
  double switch_margin;      // a new weapon must score this much better

  /* --- movement -------------------------------------------------------- */
  double preferred_range_m;  // nominal engagement distance
  double retreat_health;     // 0..1, fall back below this health fraction
  double search_rate_deg_s;  // scan speed while no target is known
  double threat_weight; // visible target pointing at self
  double lowhp_weight; // opportunistic visible target priority
  double respawn_delay_s; // dead time before native fire-edge
};

/* ------------------------------------------------------------------------ */
/* Personalities                                                             */
/* ------------------------------------------------------------------------ */

enum class Personality {
  kAggressor = 0,   // closes distance, accepts trades
  kSurvivor = 1,    // keeps health, disengages early
  kDuelist = 2,     // strafes constantly, mid range
  kController = 3,  // holds space, prefers pickups and sightlines
  kMarksman = 4,    // keeps distance, wants long-range weapons
  kFlaky = 5        // inconsistent: mood swings change aggression over time
};

// Deliberately contains no perception or aim field. Everything here affects
// *what the bot wants*, never *how well it can do it*.
struct PersonalityParams {
  double aggression;        // 0..1, willingness to close in and keep fighting
  double range_bias_m;      // -10..+14, shifts preferred_range_m
  double strafe_bias;       // 0..1, lateral movement while in the band
  double caution;           // 0..1, retreats earlier and more often
  double range_preference;  // -1 close-range weapons .. +1 long-range weapons
  double mood_period_s;     // 0 = static temperament (only kFlaky > 0)
  double mood_swing;        // 0..1, amplitude of the aggression oscillation
};

/* ------------------------------------------------------------------------ */
/* Combined profile                                                          */
/* ------------------------------------------------------------------------ */

struct BotProfile {
  SkillParams skill;
  PersonalityParams personality;
  uint32_t seed;      // per-bot deterministic RNG seed, never shared
  int tier;           // 1..5, retained for logging/telemetry
  int persona;        // 0..5, retained for logging/telemetry
  char name[24];      // administrative bot label, never a human identity
  char label[32];     // "<name> t<tier> p<persona>"
};

/* ------------------------------------------------------------------------ */
/* Skill table - calibration hypotheses                                      */
/* ------------------------------------------------------------------------ */

// The columns move monotonically from tier 1 to tier 5 on purpose: a higher
// tier is never worse at anything. Personalities are applied afterwards and
// cannot override these numbers.
inline const SkillParams& SkillFor(int tier) {
  static const SkillParams kSkills[kSkillTierCount] = {
      // 1 - beginner: sees late, aims coarsely, holds the trigger anyway
      {0.55, 1.2, 55.0,  60.0, 0.35, 4,
       110.0,  320.0, 4.50, 0.55, 0.55, 5.0, 0.35, 0.05,
       2.5, 1.45,
       7.0, 0.55, 40.0, 0.5, 0.20, 2.0},
      // 2 - casual: reacts, but tracking and trigger discipline are loose
      {0.42, 1.6, 62.0,  70.0, 0.40, 5,
       150.0,  450.0, 3.20, 0.45, 0.45, 4.0, 0.28, 0.20,
       2.0, 1.35,
       9.0, 0.50, 45.0, 0.65, 0.28, 1.5},
      // 3 - average: competent, occasionally sloppy
      {0.30, 2.0, 68.0,  80.0, 0.45, 6,
       200.0,  650.0, 2.20, 0.38, 0.34, 3.0, 0.22, 0.45,
       1.6, 1.28,
       12.0, 0.42, 52.0, 0.85, 0.35, 1.0},
      // 4 - advanced: deliberate aim, real weapon knowledge
      {0.22, 2.5, 74.0,  90.0, 0.50, 7,
       270.0,  900.0, 1.50, 0.30, 0.24, 2.2, 0.16, 0.70,
       1.2, 1.22,
       16.0, 0.35, 60.0, 1.0, 0.42, 0.6},
      // 5 - very good arena player: fast, precise, patient trigger
      {0.15, 3.0, 80.0, 100.0, 0.55, 8,
       340.0, 1300.0, 1.00, 0.24, 0.16, 1.5, 0.10, 0.90,
       0.9, 1.18,
       22.0, 0.28, 70.0, 1.15, 0.50, 0.25},
  };
  const int idx = (tier < 1 ? 1 : (tier > kSkillTierCount ? kSkillTierCount : tier)) - 1;
  return kSkills[idx];
}

inline const char* SkillName(int tier) {
  static const char* kNames[kSkillTierCount] = {
      "beginner", "casual", "average", "advanced", "expert"};
  const int idx = (tier < 1 ? 1 : (tier > kSkillTierCount ? kSkillTierCount : tier)) - 1;
  return kNames[idx];
}

/* ------------------------------------------------------------------------ */
/* Personality table - calibration hypotheses                                */
/* ------------------------------------------------------------------------ */

inline const PersonalityParams& PersonalityFor(int persona) {
  static const PersonalityParams kPersonas[kPersonalityCount] = {
      // Aggressor: pushes in, seldom retreats
      {0.90, -6.0, 0.40, 0.15, -0.55, 0.0, 0.0},
      // Survivor: keeps distance, breaks off early
      {0.25,  4.0, 0.70, 0.90,  0.35, 0.0, 0.0},
      // Duelist: constant lateral movement, mid range
      {0.60,  0.0, 0.95, 0.40,  0.00, 0.0, 0.0},
      // Controller: holds sightlines, collects resources
      {0.45,  2.0, 0.60, 0.60,  0.25, 0.0, 0.0},
      // Marksman: keeps the fight far away
      {0.20, 12.0, 0.50, 0.50,  0.85, 0.0, 0.0},
      // Flaky: swings between pushing and hiding
      {0.50,  0.0, 0.55, 0.50,  0.10, 75.0, 0.45},
  };
  const int idx =
      (persona < 0 ? 0 : (persona >= kPersonalityCount ? kPersonalityCount - 1 : persona));
  return kPersonas[idx];
}

inline const char* PersonalityName(int persona) {
  static const char* kNames[kPersonalityCount] = {
      "aggressor", "survivor", "duelist", "controller", "marksman", "flaky"};
  const int idx =
      (persona < 0 ? 0 : (persona >= kPersonalityCount ? kPersonalityCount - 1 : persona));
  return kNames[idx];
}

/* ------------------------------------------------------------------------ */
/* Validation                                                                */
/* ------------------------------------------------------------------------ */

enum class ProfileError {
  kOk = 0,
  kTierOutOfRange,
  kPersonalityOutOfRange,
  kReactionOutOfRange,
  kMemoryOutOfRange,
  kFovOutOfRange,
  kSightRangeOutOfRange,
  kTurnRateOutOfRange,
  kTurnAccelOutOfRange,
  kAimSigmaOutOfRange,
  kAimCorrOutOfRange,
  kOvershootOutOfRange,
  kFireToleranceOutOfRange,
  kSettleOutOfRange,
  kPredictionOutOfRange,
  kDwellOutOfRange,
  kSwitchMarginOutOfRange,
  kPreferredRangeOutOfRange,
  kRetreatHealthOutOfRange,
  kSearchRateOutOfRange,
  kThreatWeightOutOfRange,
  kLowHealthWeightOutOfRange,
  kRespawnDelayOutOfRange,
  kNonFinite,
  kSeedZero
};

inline bool InRange(double v, double lo, double hi) {
  return std::isfinite(v) && v >= lo && v <= hi;
}

// Bounds are deliberately wide: they catch configuration typos and NaN, they
// do not pretend that 0.31 s is scientifically different from 0.30 s.
inline ProfileError ValidateSkill(const SkillParams& s) {
  if (!std::isfinite(s.reaction_s) || !std::isfinite(s.memory_s) ||
      !std::isfinite(s.fov_half_deg) || !std::isfinite(s.sight_range_m) ||
      !std::isfinite(s.alert_window_s) || !std::isfinite(s.turn_rate_deg_s) ||
      !std::isfinite(s.turn_accel_deg_s2) || !std::isfinite(s.aim_sigma_deg) ||
      !std::isfinite(s.aim_corr_s) || !std::isfinite(s.overshoot) ||
      !std::isfinite(s.fire_tol_deg) || !std::isfinite(s.settle_s) ||
      !std::isfinite(s.prediction_gain) || !std::isfinite(s.weapon_dwell_s) ||
      !std::isfinite(s.switch_margin) || !std::isfinite(s.preferred_range_m) ||
      !std::isfinite(s.retreat_health) || !std::isfinite(s.search_rate_deg_s) ||
      !std::isfinite(s.threat_weight) || !std::isfinite(s.lowhp_weight) ||
      !std::isfinite(s.respawn_delay_s)) {
    return ProfileError::kNonFinite;
  }
  if (!InRange(s.reaction_s, 0.05, 2.0)) return ProfileError::kReactionOutOfRange;
  if (!InRange(s.memory_s, 0.25, 8.0)) return ProfileError::kMemoryOutOfRange;
  if (!InRange(s.fov_half_deg, 20.0, 100.0)) return ProfileError::kFovOutOfRange;
  if (!InRange(s.sight_range_m, 10.0, 250.0)) return ProfileError::kSightRangeOutOfRange;
  if (!InRange(s.turn_rate_deg_s, 20.0, 720.0)) return ProfileError::kTurnRateOutOfRange;
  if (!InRange(s.turn_accel_deg_s2, 60.0, 8000.0)) return ProfileError::kTurnAccelOutOfRange;
  if (!InRange(s.aim_sigma_deg, 0.0, 20.0)) return ProfileError::kAimSigmaOutOfRange;
  if (!InRange(s.aim_corr_s, 0.05, 3.0)) return ProfileError::kAimCorrOutOfRange;
  if (!InRange(s.overshoot, 0.0, 1.0)) return ProfileError::kOvershootOutOfRange;
  if (!InRange(s.fire_tol_deg, 0.25, 20.0)) return ProfileError::kFireToleranceOutOfRange;
  if (!InRange(s.settle_s, 0.0, 2.0)) return ProfileError::kSettleOutOfRange;
  if (!InRange(s.prediction_gain, 0.0, 1.0)) return ProfileError::kPredictionOutOfRange;
  if (!InRange(s.weapon_dwell_s, 0.0, 10.0)) return ProfileError::kDwellOutOfRange;
  if (!InRange(s.switch_margin, 1.0, 3.0)) return ProfileError::kSwitchMarginOutOfRange;
  if (!InRange(s.preferred_range_m, 1.0, 60.0)) return ProfileError::kPreferredRangeOutOfRange;
  if (!InRange(s.retreat_health, 0.0, 0.95)) return ProfileError::kRetreatHealthOutOfRange;
  if (!InRange(s.search_rate_deg_s, 5.0, 180.0)) return ProfileError::kSearchRateOutOfRange;
  if (!InRange(s.threat_weight, 0.0, 2.0)) return ProfileError::kThreatWeightOutOfRange;
  if (!InRange(s.lowhp_weight, 0.0, 1.0)) return ProfileError::kLowHealthWeightOutOfRange;
  if (!InRange(s.respawn_delay_s, 0.0, 5.0)) return ProfileError::kRespawnDelayOutOfRange;
  if (s.max_los_per_tick < 1 || s.max_los_per_tick > 16) {
    return ProfileError::kSightRangeOutOfRange;
  }
  return ProfileError::kOk;
}

inline ProfileError ValidatePersonality(const PersonalityParams& p) {
  if (!std::isfinite(p.aggression) || !std::isfinite(p.range_bias_m) ||
      !std::isfinite(p.strafe_bias) || !std::isfinite(p.caution) ||
      !std::isfinite(p.range_preference) || !std::isfinite(p.mood_period_s) ||
      !std::isfinite(p.mood_swing)) {
    return ProfileError::kNonFinite;
  }
  if (!InRange(p.aggression, 0.0, 1.0)) return ProfileError::kOvershootOutOfRange;
  if (!InRange(p.range_bias_m, -10.0, 14.0)) return ProfileError::kPreferredRangeOutOfRange;
  if (!InRange(p.strafe_bias, 0.0, 1.0)) return ProfileError::kOvershootOutOfRange;
  if (!InRange(p.caution, 0.0, 1.0)) return ProfileError::kOvershootOutOfRange;
  if (!InRange(p.range_preference, -1.0, 1.0)) return ProfileError::kOvershootOutOfRange;
  if (!InRange(p.mood_period_s, 0.0, 600.0)) return ProfileError::kOvershootOutOfRange;
  if (!InRange(p.mood_swing, 0.0, 1.0)) return ProfileError::kOvershootOutOfRange;
  return ProfileError::kOk;
}

inline ProfileError ValidateProfile(const BotProfile& p) {
  if (p.tier < 1 || p.tier > kSkillTierCount) return ProfileError::kTierOutOfRange;
  if (p.persona < 0 || p.persona >= kPersonalityCount) {
    return ProfileError::kPersonalityOutOfRange;
  }
  if (p.seed == 0u) return ProfileError::kSeedZero;
  const ProfileError e = ValidateSkill(p.skill);
  if (e != ProfileError::kOk) return e;
  return ValidatePersonality(p.personality);
}

// Orthogonality guard: combining any tier with any personality must leave the
// skill block bit-for-bit identical. Used by the unit tests and by the
// integration when it validates a loaded profile.
inline bool SkillUnaffectedByPersonality(int tier, int persona_a, int persona_b) {
  BotProfile a{}, b{};
  a.skill = SkillFor(tier);
  b.skill = SkillFor(tier);
  a.personality = PersonalityFor(persona_a);
  b.personality = PersonalityFor(persona_b);
  const SkillParams& sa = a.skill;
  const SkillParams& sb = b.skill;
  return sa.reaction_s == sb.reaction_s && sa.turn_rate_deg_s == sb.turn_rate_deg_s &&
         sa.aim_sigma_deg == sb.aim_sigma_deg && sa.fire_tol_deg == sb.fire_tol_deg &&
         sa.memory_s == sb.memory_s && sa.prediction_gain == sb.prediction_gain &&
         sa.threat_weight == sb.threat_weight && sa.lowhp_weight == sb.lowhp_weight &&
         sa.respawn_delay_s == sb.respawn_delay_s;
}

/* ------------------------------------------------------------------------ */
/* Profile construction                                                      */
/* ------------------------------------------------------------------------ */

inline void CopyName(char* dst, size_t cap, const char* src) {
  if (cap == 0) return;
  size_t i = 0;
  for (; src[i] != '\0' && i + 1 < cap; ++i) dst[i] = src[i];
  dst[i] = '\0';
}

// Seed derivation: slot and tier/persona are mixed in, so two bots never share
// a random stream even if the caller passes the same base seed.
inline uint32_t DeriveSeed(uint32_t base, int slot, int tier, int persona) {
  uint32_t h = base ? base : 0x9E3779B9u;
  h ^= static_cast<uint32_t>(slot + 1) * 0x85EBCA6Bu;
  h ^= static_cast<uint32_t>(tier) * 0xC2B2AE35u;
  h ^= static_cast<uint32_t>(persona + 1) * 0x27D4EB2Fu;
  h ^= h >> 15;
  h *= 0x2545F491u;
  h ^= h >> 13;
  return h ? h : 1u;
}

inline bool BuildProfile(int tier, int persona, uint32_t seed, const char* name,
                         BotProfile* out) {
  if (out == nullptr) return false;
  if (tier < 1 || tier > kSkillTierCount) return false;
  if (persona < 0 || persona >= kPersonalityCount) return false;
  out->skill = SkillFor(tier);
  out->personality = PersonalityFor(persona);
  out->tier = tier;
  out->persona = persona;
  out->seed = seed ? seed : 1u;
  CopyName(out->name, sizeof(out->name), name ? name : "BOT");
  // label = "<name> t<tier>p<persona>" for administrative logs
  int n = 0;
  for (const char* s = out->name; *s != '\0' &&
       n < static_cast<int>(sizeof(out->label)) - 6; ++s) {
    out->label[n++] = *s;
  }
  if (n > 0) out->label[n++] = ' ';
  out->label[n++] = 't';
  out->label[n++] = static_cast<char>('0' + tier);
  out->label[n++] = 'p';
  out->label[n++] = static_cast<char>('0' + persona);
  out->label[n] = '\0';
  return ValidateProfile(*out) == ProfileError::kOk;
}

/* ------------------------------------------------------------------------ */
/* Mood: the only time-varying part of a personality                         */
/* ------------------------------------------------------------------------ */

// Aggression is modulated by a deterministic, per-bot phase-shifted sine. Only
// personalities with mood_period_s > 0 (currently kFlaky) actually swing; all
// others return aggression unchanged. Purely a *decision* input - it never
// touches SkillParams.
inline double EffectiveAggression(const BotProfile& p, int tick) {
  const double base = p.personality.aggression;
  if (p.personality.mood_period_s <= 0.0 || p.personality.mood_swing <= 0.0) return base;
  const double t = static_cast<double>(tick) / kProfileTickHz;
  const double phase = static_cast<double>(p.seed % 1000u) * 0.001 * 2.0 * 3.14159265358979;
  const double w = 2.0 * 3.14159265358979 / p.personality.mood_period_s;
  const double m = base + p.personality.mood_swing * 0.5 * std::sin(w * t + phase);
  return m < 0.0 ? 0.0 : (m > 1.0 ? 1.0 : m);
}

/* ------------------------------------------------------------------------ */
/* Default mixed-server roster (8 bots)                                      */
/* ------------------------------------------------------------------------ */

struct RosterEntry {
  int tier;
  int persona;
  const char* name;
};

// Start distribution for a mixed eight-bot server: 2 beginners, 2 casual,
// 2 average, 1 advanced, 1 expert. Personalities are spread so that no tier
// is represented by only one play style, and so that the beginner tier also
// contains an aggressive bot (a beginner may push; a good player may hold).
// This table is the default; the integration reads the same values from
// configuration, so an operator can change it without a rebuild.
inline const RosterEntry* DefaultRoster(int* count) {
  static const RosterEntry kRoster[8] = {
      {1, 0, "BOT-Rookie-Rush"},     // beginner  + aggressor
      {1, 1, "BOT-Rookie-Guard"},    // beginner  + survivor
      {2, 5, "BOT-Casual-Flaky"},    // casual    + flaky
      {2, 3, "BOT-Casual-Holder"},   // casual    + controller
      {3, 2, "BOT-Average-Duelist"}, // average   + duelist
      {3, 4, "BOT-Average-Rifle"},   // average   + marksman
      {4, 0, "BOT-Veteran-Push"},    // advanced  + aggressor
      {5, 4, "BOT-Expert-Rifle"},    // expert    + marksman
  };
  if (count != nullptr) *count = 8;
  return kRoster;
}

// Build the nth roster bot for a given client process. Two processes with four
// local players each use slot 0..3 and index 0..3 / 4..7.
inline bool BuildRosterProfile(int roster_index, int local_slot, uint32_t base_seed,
                               BotProfile* out) {
  int count = 0;
  const RosterEntry* roster = DefaultRoster(&count);
  if (roster_index < 0) roster_index = 0;
  if (roster_index >= count) roster_index %= count;
  if (local_slot < 0) local_slot = 0;
  const RosterEntry& e = roster[roster_index];
  const uint32_t seed = DeriveSeed(base_seed, local_slot, e.tier, e.persona);
  return BuildProfile(e.tier, e.persona, seed, e.name, out);
}

}  // namespace botcore

#endif  // BOTCORE_BOT_PROFILE_H
