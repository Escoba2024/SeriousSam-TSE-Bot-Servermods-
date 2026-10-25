// combat2_tactics.h - candidate target/strafe/retreat/respawn tactics.
// Engine-free overlay modules for the existing Human-KI. Each module maps to a
// PR #62 finding and to a documented seam in botcore (see docs). Nothing here
// touches poc/botcore/**, navigation, items or sessions.
#ifndef BEHAVIOR_IMPROVEMENTS_COMBAT2_TACTICS_H
#define BEHAVIOR_IMPROVEMENTS_COMBAT2_TACTICS_H

#include <cmath>
#include <cstdint>

#include "bot_profile.h"
#include "combat2_weapon.h"  // Hash32

namespace combat2 {

inline double Clamp(double v, double lo, double hi) { return v < lo ? lo : (v > hi ? hi : v); }

/* ------------------------------------------------------------------ */
/* Persona combat style (preference only - never capability)           */
/* ------------------------------------------------------------------ */
struct CombatStyle {
  double strafe_flip_s;   // base ADAD half-period
  double strafe_amp;      // multiplies personality.strafe_bias
  double close_strafe;    // strafe share while closing distance (diagonal)
  double threat_weight;   // target scoring: who can hurt me
  double finish_weight;   // target scoring: low-health finish bonus
  double retreat_mult;    // multiplies skill*caution retreat threshold
  double band_tolerance_m;// how loosely the preferred band is held
};
inline const CombatStyle& StyleFor(int persona) {
  static const CombatStyle kS[6] = {
      /*aggressor*/ {1.10, 0.85, 0.45, 0.7, 1.3, 0.75, 4.0},
      /*survivor */ {0.85, 1.00, 0.60, 1.3, 0.6, 1.35, 5.0},
      /*duelist  */ {0.55, 1.15, 0.75, 1.0, 1.0, 1.00, 3.0},
      /*controller*/{0.95, 0.90, 0.50, 1.1, 0.9, 1.15, 4.0},
      /*marksman */ {1.25, 0.80, 0.35, 0.9, 1.1, 1.10, 6.0},
      /*flaky    */ {0.80, 0.95, 0.55, 0.9, 0.9, 1.00, 4.5},
  };
  if (persona < 0) persona = 0;
  if (persona > 5) persona = 5;
  return kS[persona];
}

/* ------------------------------------------------------------------ */
/* F-7 target prioritisation                                           */
/* Baseline ChooseTarget scores 1/(dist+1) only and requires a new     */
/* target to be 1.4x closer; PR #62 measured mid tiers ignoring the    */
/* nearest threat ~18% of the time. Candidate: distance + threat       */
/* (recent damager / close & facing) + finish bonus, with a hard       */
/* nearest-threat override inside a danger radius.                     */
/* Seam: replace the score inside botcore HumanBotPolicy::ChooseTarget */
/* (Codex integration), inputs already exist in TrackState + health.   */
/* ------------------------------------------------------------------ */
struct TargetCandidate {
  int index = -1;
  double distance_m = 1e9;
  double health_frac = 1.0;      // replicated health 0..1
  bool visible_now = false;
  bool damaged_me_recently = false;
  double facing_me = 0.0;        // 0..1 dot(eye dir, to me) if known else 0
  double confidence = 0.0;
};

inline double TargetScore2(const TargetCandidate& c, const CombatStyle& st,
                           int current_target) {
  if (!c.visible_now && c.confidence <= 0.5) return -1.0;
  double s = 10.0 / (c.distance_m + 2.0);                       // proximity
  const double threat = (c.damaged_me_recently ? 1.0 : 0.0) * 0.8 + c.facing_me * 0.5 +
                        (c.distance_m < 8.0 ? 0.6 : 0.0);
  s += st.threat_weight * threat;
  s += st.finish_weight * (1.0 - Clamp(c.health_frac, 0.0, 1.0)) * 0.7;  // finish
  if (c.index == current_target) s *= 1.25;                     // stickiness
  return s;
}

// Returns chosen index or -1. Hard override: a visible damager or any visible
// opponent inside 6 m pre-empts stickiness (the F-7 fix).
inline int ChooseTarget2(const TargetCandidate* cands, int count, const CombatStyle& st,
                         int current_target) {
  int best = -1; double bs = -1.0;
  int danger = -1; double danger_dist = 1e9;
  for (int i = 0; i < count; ++i) {
    const double s = TargetScore2(cands[i], st, current_target);
    if (s > bs) { bs = s; best = cands[i].index; }
    if (cands[i].visible_now &&
        (cands[i].damaged_me_recently || cands[i].distance_m < 6.0) &&
        cands[i].distance_m < danger_dist) {
      danger_dist = cands[i].distance_m; danger = cands[i].index;
    }
  }
  if (danger >= 0 && danger != current_target) return danger;
  return best;
}

/* ------------------------------------------------------------------ */
/* F-3 hitscan latency lead + iterative projectile lead                */
/* Baseline leads only projectiles, once, by dist/speed. At 200 ms     */
/* effective latency PR #62 saw expert hitscan accuracy 0.58 -> 0.31.  */
/* Seam: bot_human.h aim_point block - apply for proj_speed==0 too,    */
/* with lead_time = latency + tick, scaled by prediction_gain.        */
/* ------------------------------------------------------------------ */
inline double LatencyLeadFactor(const botcore::SkillParams& skill) {
  return Clamp(skill.prediction_gain, 0.0, 1.0);
}
// Extra angular error (deg) a lateral mover creates over `latency_s`.
// lateral_speed relative to line of sight.
inline double LatencyAngularErrorDeg(double lateral_speed_m_s, double distance_m,
                                     double latency_s, double lead_factor) {
  if (distance_m < 0.5) distance_m = 0.5;
  const double disp = lateral_speed_m_s * latency_s * (1.0 - Clamp(lead_factor, 0.0, 1.0));
  return std::atan2(disp, distance_m) * botcore::kRadToDeg;
}
// Two-iteration projectile intercept time (target keeps moving while the
// projectile flies to the led point). Returns seconds.
inline double ProjectileLeadTime(double distance_m, double closing_speed_m_s,
                                 double proj_speed_m_s) {
  if (proj_speed_m_s <= 1.0) return 0.0;
  double t = distance_m / proj_speed_m_s;
  for (int i = 0; i < 2; ++i) {
    const double d2 = distance_m + closing_speed_m_s * t;  // + = opening
    t = (d2 > 0.0 ? d2 : 0.0) / proj_speed_m_s;
  }
  return t;
}

/* ------------------------------------------------------------------ */
/* F-5/F-8 perception alert cone + search                              */
/* Baseline: alerted() bypasses the FOV gate entirely (~360 deg) and   */
/* ReactionTicks drops to 1/3. Candidate: alert widens the cone by a   */
/* bounded amount and reaction keeps a floor.                          */
/* Seam: Perception::NeedsLineOfSight alert branch + ReactionTicks.    */
/* ------------------------------------------------------------------ */
inline double AlertHalfAngleDeg(const botcore::SkillParams& skill) {
  return skill.fov_half_deg + 45.0 > 125.0 ? 125.0 : skill.fov_half_deg + 45.0;
}
inline bool AlertGatePasses(double off_axis_deg, const botcore::SkillParams& skill) {
  return std::fabs(off_axis_deg) <= AlertHalfAngleDeg(skill);
}
inline int AlertReactionTicks(const botcore::SkillParams& skill) {
  int t = (int)(skill.reaction_s * botcore::kProfileTickHz * 0.6 + 0.5);
  return t > 2 ? t : 2;  // >=100 ms even when alerted: no instant snaps
}
// F-6: baseline search always turns one way at a fixed rate. Candidate search
// alternates sweep direction per 2.5 s block (seed-phase), like a player
// checking both sides. Returns signed yaw delta for one tick.
inline double SearchYawDeltaDeg(const botcore::SkillParams& skill, int tick,
                                uint32_t seed, double dt) {
  const int block = (tick + (int)(seed % 37u)) / 50;  // 2.5 s blocks
  const double dir = (Hash32(seed ^ (uint32_t)block * 40503u) & 1u) ? 1.0 : -1.0;
  return dir * skill.search_rate_deg_s * dt;
}

/* ------------------------------------------------------------------ */
/* F-5 strafe / dodge controller                                       */
/* Baseline MoveIntent: strafe only inside the band, sin-shaped, fixed */
/* flip period 60..121 ticks, and bot_fStrafeScale=0 disables it all  */
/* in patch 0008. Candidate: persona ADAD with jittered flips,         */
/* diagonal strafing while closing, instant flip on taking damage.    */
/* Own-strafe aim cost is a botcore aim property; compensation factor  */
/* for integration: scale fire tolerance while strafing by tier.      */
/* ------------------------------------------------------------------ */
class StrafeController {
 public:
  void Configure(int persona, double strafe_bias, uint32_t seed) {
    style_ = StyleFor(persona); bias_ = Clamp(strafe_bias, 0.0, 1.0);
    seed_ = seed ? seed : 1u; sign_ = (seed & 1u) ? 1.0 : -1.0;
    next_flip_tick_ = 0; flips_ = 0; ScheduleFlip(0);
  }
  void NotifyDamage(int tick) {  // dodge: reverse now, reschedule
    sign_ = -sign_; ++flips_; ScheduleFlip(tick);
  }
  // mode: 0 approach, 1 in-band, 2 back-off/retreat
  double Step(int tick, int mode) {
    if (tick >= next_flip_tick_) { sign_ = -sign_; ++flips_; ScheduleFlip(tick); }
    double amp = bias_ * style_.strafe_amp;
    if (mode == 0) amp *= style_.close_strafe;
    if (mode == 2) amp *= 0.9;
    return Clamp(sign_ * amp, -1.0, 1.0);
  }
  int flips() const { return flips_; }
  double sign() const { return sign_; }
 private:
  void ScheduleFlip(int tick) {
    const double u = (Hash32(seed_ ^ (uint32_t)(tick + flips_ * 7919)) & 0xffffff) / 16777216.0;
    const double half = style_.strafe_flip_s * (0.65 + 0.7 * u);  // jittered
    int dt = (int)(half * botcore::kProfileTickHz + 0.5);
    if (dt < 4) dt = 4;
    next_flip_tick_ = tick + dt;
  }
  CombatStyle style_{1.0, 1.0, 0.5, 1.0, 1.0, 1.0, 4.0};
  double bias_ = 0.5, sign_ = 1.0;
  uint32_t seed_ = 1;
  int next_flip_tick_ = 0, flips_ = 0;
};
// While strafing fast, weak tiers should fire less (their own movement hurts
// aim); strong tiers compensate. Multiplier for fire_tol at integration.
inline double StrafeFireTolMult(int tier, double strafe_abs) {
  static const double kComp[5] = {0.35, 0.55, 0.75, 0.9, 1.0};  // compensation skill
  const int i = (tier < 1 ? 1 : (tier > 5 ? 5 : tier)) - 1;
  return 1.0 + (1.0 - kComp[i]) * Clamp(strafe_abs, 0.0, 1.0) * 0.8;
}

/* ------------------------------------------------------------------ */
/* F-4 retreat that breaks line of sight                               */
/* Baseline: forward=-0.85 straight backwards along view. Candidate    */
/* takes cover candidate points from the navigation layer (A3 owns     */
/* nav; this is only the documented interface) and picks the point     */
/* minimising time-exposed: score = dist(cover) - 2*dist gain from     */
/* threat, preferring points the caller flagged as LOS-blocking. With  */
/* no cover data it emits a zig-zag backpedal direction instead.       */
/* ------------------------------------------------------------------ */
struct CoverPoint { double x, z; bool blocks_los; };
struct RetreatPlan {
  bool retreat = false;
  double dir_x = 0.0, dir_z = 0.0;  // desired world move direction (unit)
  int cover_index = -1;
};
inline bool ShouldRetreat(double health_frac, const botcore::BotProfile& p,
                          int visible_threats) {
  const CombatStyle& st = StyleFor(p.persona);
  double below = p.skill.retreat_health * (0.6 + 0.9 * p.personality.caution) * st.retreat_mult;
  if (visible_threats >= 2) below += 0.12;  // outnumbered: leave earlier
  if (below > 0.85) below = 0.85;
  return health_frac < below;
}
inline RetreatPlan PlanRetreat(double self_x, double self_z, double threat_x,
                               double threat_z, const CoverPoint* covers, int count,
                               double strafe_sign) {
  RetreatPlan rp; rp.retreat = true;
  double ax = self_x - threat_x, az = self_z - threat_z;
  const double al = std::sqrt(ax * ax + az * az);
  if (al > 1e-6) { ax /= al; az /= al; }
  int best = -1; double bs = 1e18;
  for (int i = 0; i < count; ++i) {
    const double dx = covers[i].x - self_x, dz = covers[i].z - self_z;
    const double d_self = std::sqrt(dx * dx + dz * dz);
    const double tx = covers[i].x - threat_x, tz = covers[i].z - threat_z;
    const double d_threat = std::sqrt(tx * tx + tz * tz);
    double score = d_self - 0.6 * (d_threat - (al > 1e-6 ? al : 0.0));
    if (!covers[i].blocks_los) score += 25.0;  // strong preference for real cover
    if (score < bs) { bs = score; best = i; }
  }
  if (best >= 0) {
    double dx = covers[best].x - self_x, dz = covers[best].z - self_z;
    const double l = std::sqrt(dx * dx + dz * dz);
    if (l > 1e-6) { dx /= l; dz /= l; }
    // Blend cover direction with directly-away so we never run *toward* threat.
    double bx = 0.7 * dx + 0.3 * ax, bz = 0.7 * dz + 0.3 * az;
    const double bl = std::sqrt(bx * bx + bz * bz);
    if (bl > 1e-6) { bx /= bl; bz /= bl; }
    rp.dir_x = bx; rp.dir_z = bz; rp.cover_index = best;
  } else {
    // Zig-zag: away + perpendicular alternating with strafe sign.
    const double px = -az * strafe_sign, pz = ax * strafe_sign;
    double bx = ax + 0.7 * px, bz = az + 0.7 * pz;
    const double bl = std::sqrt(bx * bx + bz * bz);
    if (bl > 1e-6) { bx /= bl; bz /= bl; }
    rp.dir_x = bx; rp.dir_z = bz;
  }
  return rp;
}

/* ------------------------------------------------------------------ */
/* Respawn behaviour (task 9; complements PR #57 tier delays)          */
/* Deterministic per-tier re-engage plan: press delay, initial scan,   */
/* weapon-check pause. Values at 20 Hz. Human-like, never instant.    */
/* ------------------------------------------------------------------ */
struct RespawnPlan2 {
  int press_delay_ticks;
  int scan_ticks;        // look around before moving out
  double scan_yaw_deg;   // first glance offset (seeded, kills spawn-camping self)
  int weapon_ready_tick; // no fire before this tick after spawn
};
inline RespawnPlan2 PlanRespawn(int tier, int persona, uint32_t seed, int death_count) {
  static const int kPress[5] = {26, 20, 15, 11, 8};    // 1.3 s .. 0.4 s
  static const int kScan[5] = {16, 13, 10, 7, 5};
  const int i = (tier < 1 ? 1 : (tier > 5 ? 5 : tier)) - 1;
  RespawnPlan2 r;
  r.press_delay_ticks = kPress[i] + (persona == 1 ? 4 : 0);  // survivor: cautious
  if (persona == 0 && r.press_delay_ticks > 4) r.press_delay_ticks -= 2;  // aggressor rushes back
  r.scan_ticks = kScan[i];
  const double u = (Hash32(seed ^ (uint32_t)death_count * 2246822519u) & 0xffffff) / 16777216.0;
  r.scan_yaw_deg = -70.0 + 140.0 * u;
  r.weapon_ready_tick = r.press_delay_ticks + 3;
  return r;
}

/* ------------------------------------------------------------------ */
/* Desired engagement range (coherence between weapon + movement)      */
/* botcore PreferredRange blends the *old* weapon band; if selection   */
/* follows CurveAt the movement band must follow the same curve or     */
/* the bot picks a shotgun and then stands 20 m away.                  */
/* ------------------------------------------------------------------ */
inline double DesiredRange2(int weapon, const botcore::BotProfile& p) {
  const WeaponCurve& w = CurveAt(weapon);
  const double persona_pref = p.skill.preferred_range_m + p.personality.range_bias_m;
  // Weak bots do not know the textbook band: they drift to their comfort
  // range (beginners closer, which also lifts their hit floor, F-2).
  const double w_opt = 0.35 + 0.05 * (p.tier < 1 ? 1 : (p.tier > 5 ? 5 : p.tier));
  double r = w_opt * w.optimal_m + (1.0 - w_opt) * persona_pref;
  return Clamp(r, 3.0, 50.0);
}

}  // namespace combat2
#endif
