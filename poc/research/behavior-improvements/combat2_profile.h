// combat2_profile.h - HUMAN AI 2.0 candidate profile adjustments (research).
//
// Standalone overlay on the READ-ONLY botcore profile model
// (poc/botcore/bot_profile.h). It never edits botcore: it derives an adjusted
// BotProfile value that the existing botcore::HumanBotPolicy can consume
// unchanged through Configure(). That is the integration seam Codex would use.
//
// Targets PR #62 findings:
//  F-2 beginner hit floor: tier-1 aim sigma 4.50 deg produced 20/21 timeout
//      draws in beginner mirrors. The candidate compresses the sigma curve at
//      the bottom (3.40 deg) while keeping the expert end identical, so a
//      beginner is credibly weak but functional. Monotonicity is preserved in
//      every column (asserted by tests).
//  F-3 prediction: prediction_gain floor raised (0.05 -> 0.25) so even weak
//      bots lead movers a little; hitscan latency lead itself lives in
//      combat2_tactics.h (LatencyLeadFactor).
//  F-9 mid-tier scoring compression: reaction/settle spacing widened slightly.
//
// HARD RULE kept from botcore: skill and personality stay orthogonal. Nothing
// in the persona style table (combat2_tactics.h) may change a skill value, and
// AdjustedProfile() returns byte-identical skill for every persona of a tier
// (unit-tested).
#ifndef BEHAVIOR_IMPROVEMENTS_COMBAT2_PROFILE_H
#define BEHAVIOR_IMPROVEMENTS_COMBAT2_PROFILE_H

#include "bot_profile.h"

namespace combat2 {

inline botcore::SkillParams AdjustedSkill(int tier) {
  botcore::SkillParams s = botcore::SkillFor(tier);  // start from qualified table
  // idx:              t1     t2     t3     t4     t5
  static const double kSigma[5]  = {3.40,  2.70,  2.00,  1.45,  1.00};
  static const double kReact[5]  = {0.50,  0.40,  0.30,  0.22,  0.15};
  static const double kPred[5]   = {0.25,  0.40,  0.55,  0.75,  0.92};
  static const double kFireTol[5]= {5.50,  4.20,  3.00,  2.20,  1.50};
  static const double kSettle[5] = {0.30,  0.25,  0.20,  0.155, 0.10};
  static const double kTurn[5]   = {135.0, 165.0, 205.0, 270.0, 340.0};
  static const double kOver[5]   = {0.50,  0.42,  0.33,  0.24,  0.16};
  const int i = (tier < 1 ? 1 : (tier > 5 ? 5 : tier)) - 1;
  s.aim_sigma_deg = kSigma[i];
  s.reaction_s = kReact[i];
  s.prediction_gain = kPred[i];
  s.fire_tol_deg = kFireTol[i];
  s.settle_s = kSettle[i];
  s.turn_rate_deg_s = kTurn[i];
  s.overshoot = kOver[i];
  return s;
}

// Full adjusted profile: adjusted skill + untouched qualified personality.
inline bool AdjustedProfile(int tier, int persona, uint32_t seed, const char* name,
                            botcore::BotProfile* out) {
  if (!botcore::BuildProfile(tier, persona, seed, name, out)) return false;
  out->skill = AdjustedSkill(tier);
  return botcore::ValidateProfile(*out) == botcore::ProfileError::kOk;
}

// Beginner close-range credibility: botcore aim error is angular, so a fixed
// sigma already implies "easier up close". The remaining F-2 problem is time:
// beginner preferred_range (7 m) plus slow settle meant almost no decided
// damage before timeouts. We therefore do NOT add magic accuracy; the sigma
// compression above plus the weapon re-balance (shotguns viable again) is the
// whole fix, and the duel battery must show it.

}  // namespace combat2
#endif
