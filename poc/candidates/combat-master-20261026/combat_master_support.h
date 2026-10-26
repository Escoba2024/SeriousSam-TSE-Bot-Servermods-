// Selected PR66 mechanics; single policy/target/respawn owner stays PR57.
#ifndef SSAM_COMBAT_MASTER_SUPPORT_H
#define SSAM_COMBAT_MASTER_SUPPORT_H
#include <cmath>
#include "combat2_weapon.h"
#include "combat2_selected.h"
namespace combat_master {
// Explicit age of the observed position, never inferred from unverified RTT.
// No unconditional one-tick addition: zero/unknown age preserves hitscan aim.
inline double LeadAge(double age_s, double prediction_gain) {
  if (!std::isfinite(age_s) || age_s <= 0.0 || !std::isfinite(prediction_gain)) return 0.0;
  const double age = age_s > 0.25 ? 0.25 : age_s;
  const double gain = prediction_gain < 0.0 ? 0.0 : (prediction_gain > 1.0 ? 1.0 : prediction_gain);
  return age * gain;
}
}
#endif
