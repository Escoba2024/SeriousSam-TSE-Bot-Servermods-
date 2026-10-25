// qa_world.h - synthetic world model for the offline bot-behavior QA harness.
//
// STATUS: OFFLINE SIMULATION ONLY.
//  - Nothing in this file is a Retail-1.07 measurement. Every constant below
//    is a documented simulation assumption (see ASSUMPTIONS) chosen so that
//    the *relative* behaviour of the engine-free botcore Human-KI components
//    (bot_profile.h / bot_perception.h / bot_aim.h / bot_loadout.h /
//    bot_human.h) becomes measurable without the game.
//  - The botcore headers are included strictly READ-ONLY from ../../botcore.
//    This harness never modifies them; it drives HumanBotPolicy exactly like
//    the GameMP integration block in poc/ai-integration/gamemp/BotDriver.cpp
//    does (BeginTick -> PlanLosQueries -> caller rays -> Step), and it mirrors
//    the integration's fire gating (weapon acknowledgement) and its default
//    strafe suppression (bot_fStrafeScale == 0).
//
// ASSUMPTIONS (all overridable via SimConfig, all reported in the JSON output)
//  A1  eye height 1.7 m, planar arena, no gravity/jumping
//  A2  player move speed 7.0 m/s, linear in the forward/strafe factor
//      (Retail plr_fSpeed* not verified here; relative only)
//  A3  target hit radius 0.6 m, scaled by the botcore AccuracyAt() hypothesis
//      table: r = 0.6 * (0.25 + 0.75 * acc)
//  A4  damage: 1 unit of botcore dps_rel == 20 sim-HP/s sustained on target;
//      per-shot damage = dps_rel * scale * weapon interval (A5)
//  A5  per-weapon fire intervals (sim hypothesis, NOT retail cadences)
//  A6  weapon switch latency 6 ticks (0.3 s) from pulse to acknowledgement
//      (Retail switch time NOT verified; the integration blocks fire until
//      m_iCurrentWeapon == m_iWantedWeapon == desired, which is mirrored here)
//  A7  sensed positions/velocities are the true state delayed by
//      latency_ticks (default 2 == 100 ms replication+network, NOT measured)
//  A8  hitscan beyond 1.5 * weapon max_m never hits (damage falloff cutoff)
//  A9  scripted enemy return fire falls off as clamp(ref/dist, 0.25, 1.0) so
//      that opening range by retreating measurably reduces damage taken
//
// UNITS: metres, seconds, degrees; tick = 1/20 s (kProfileTickHz).

#ifndef BEHAVIOR_QA_WORLD_H
#define BEHAVIOR_QA_WORLD_H

#include <algorithm>
#include <cmath>
#include <cstdint>
#include <cstring>
#include <vector>

#include "../../botcore/bot_human.h"

namespace behaviorqa {

using botcore::AccuracyAt;
using botcore::BotCommand;
using botcore::BotProfile;
using botcore::BuildProfile;
using botcore::DeriveSeed;
using botcore::HumanBotPolicy;
using botcore::SenseInput;
using botcore::WeaponAt;
using botcore::WeaponName;
using botcore::WeaponProfile;
using botcore::WorldView;

constexpr double kDt = 1.0 / botcore::kProfileTickHz;  // 0.05 s
constexpr double kEyeHeight = 1.7;                     // A1

inline double WrapDeg(double a) {
  while (a > 180.0) a -= 360.0;
  while (a < -180.0) a += 360.0;
  return a;
}

// bot_aim.h convention: desired_yaw = atan2(-dx, -dz). Hence a body facing
// `yaw` has forward = (-sin, -cos) and (chosen perpendicular) right =
// (cos, -sin) in the (x, z) plane.
inline void FacingVectors(double yaw_deg, double* fx, double* fz, double* rx,
                          double* rz) {
  const double r = yaw_deg * botcore::kDegToRad;
  *fx = -std::sin(r);
  *fz = -std::cos(r);
  *rx = std::cos(r);
  *rz = -std::sin(r);
}

/* ------------------------------------------------------------------------ */
/* Configuration                                                             */
/* ------------------------------------------------------------------------ */

struct SimConfig {
  int latency_ticks = 2;        // A7
  double strafe_scale = 0.0;    // mirrors bot_fStrafeScale (integration default 0)
  double move_speed = 7.0;      // A2
  int switch_ticks = 6;         // A6
  double dps_scale = 20.0;      // A4
  double target_radius = 0.6;   // A3
  double arena_half = 30.0;
  bool lock_movement = false;   // gallery mode: aiming only, body frozen
  uint32_t loadout_mask = 0x3FFFu;
  int max_ticks = 600;
  int cover_gap_ticks = 30;     // used by cover_reacquire
  int latency_override = -1;    // (unused placeholder; keep JSON stable)
};

// A5: sim fire interval per WeaponType index 1..14, in seconds.
inline double WeaponIntervalS(int weapon) {
  static const double kInterval[15] = {
      0.0,   // 0 unused
      0.50,  // 1 knife
      0.15,  // 2 colt
      0.15,  // 3 double colt
      0.90,  // 4 shotgun
      0.90,  // 5 double shotgun
      0.10,  // 6 tommygun
      0.07,  // 7 minigun
      0.80,  // 8 rocket
      1.00,  // 9 grenade
      0.10,  // 10 chainsaw
      0.10,  // 11 flamer
      0.12,  // 12 laser
      1.30,  // 13 sniper
      1.20,  // 14 cannon
  };
  if (weapon < 1 || weapon > 14) return 0.5;
  return kInterval[weapon];
}

inline int IntervalTicks(int weapon) {
  const int t = static_cast<int>(WeaponIntervalS(weapon) / kDt + 0.5);
  return t > 0 ? t : 1;
}

// A3: effective hit radius at distance d for weapon w.
inline double HitRadius(const WeaponProfile& w, double d, double base_radius) {
  const double acc = AccuracyAt(w, d);
  return base_radius * (0.25 + 0.75 * acc);
}

/* ------------------------------------------------------------------------ */
/* Geometry helpers                                                          */
/* ------------------------------------------------------------------------ */

struct Rect2D {  // axis-aligned cover block on the (x, z) plane
  double x0, z0, x1, z1;
};

// 2D segment vs AABB (slab method). True when the segment intersects the box.
inline bool SegmentHitsRect(double ax, double az, double bx, double bz,
                            const Rect2D& r) {
  const double dx = bx - ax;
  const double dz = bz - az;
  double t0 = 0.0, t1 = 1.0;
  // x slab
  if (std::fabs(dx) < 1e-12) {
    if (ax < r.x0 || ax > r.x1) return false;
  } else {
    double ta = (r.x0 - ax) / dx, tb = (r.x1 - ax) / dx;
    if (ta > tb) { const double s = ta; ta = tb; tb = s; }
    t0 = ta > t0 ? ta : t0;
    t1 = tb < t1 ? tb : t1;
    if (t0 > t1) return false;
  }
  // z slab
  if (std::fabs(dz) < 1e-12) {
    if (az < r.z0 || az > r.z1) return false;
  } else {
    double ta = (r.z0 - az) / dz, tb = (r.z1 - az) / dz;
    if (ta > tb) { const double s = ta; ta = tb; tb = s; }
    t0 = ta > t0 ? ta : t0;
    t1 = tb < t1 ? tb : t1;
    if (t0 > t1) return false;
  }
  return true;
}

inline bool LosBlocked(double ax, double az, double bx, double bz,
                       const std::vector<Rect2D>& cover) {
  for (const Rect2D& r : cover) {
    if (SegmentHitsRect(ax, az, bx, bz, r)) return true;
  }
  return false;
}

// Angle (deg) between the view direction (yaw, pitch) and the direction to a
// point, and the resulting perpendicular miss distance at that point.
inline double AngularErrorDeg(double eye_x, double eye_y, double eye_z,
                              double yaw_deg, double pitch_deg, double tx,
                              double ty, double tz) {
  const double dx = tx - eye_x, dy = ty - eye_y, dz = tz - eye_z;
  const double horiz = std::sqrt(dx * dx + dz * dz);
  if (horiz < 1e-9 && std::fabs(dy) < 1e-9) return 0.0;
  // View unit vector consistent with bot_aim.h: yaw = atan2(-dx, -dz),
  // pitch = atan2(dy, horiz).
  const double yr = yaw_deg * botcore::kDegToRad;
  const double pr = pitch_deg * botcore::kDegToRad;
  const double vx = -std::sin(yr) * std::cos(pr);
  const double vz = -std::cos(yr) * std::cos(pr);
  const double vy = std::sin(pr);
  const double len = std::sqrt(dx * dx + dy * dy + dz * dz);
  if (len < 1e-9) return 0.0;
  double dot = (dx * vx + dy * vy + dz * vz) / len;
  if (dot > 1.0) dot = 1.0;
  if (dot < -1.0) dot = -1.0;
  return std::acos(dot) * botcore::kRadToDeg;
}

inline double MissDistanceM(double error_deg, double distance_m) {
  return distance_m * std::tan(error_deg * botcore::kDegToRad);
}

/* ------------------------------------------------------------------------ */
/* Deterministic digest (reproducibility evidence)                           */
/* ------------------------------------------------------------------------ */

class Digest {
 public:
  void Add(double v) {
    // Quantise to 1e-6 so that identical logic gives identical digests while
    // tiny fp reassociation on other compilers still shows up as a change.
    const int64_t q = static_cast<int64_t>(std::llround(v * 1e6));
    uint64_t x = static_cast<uint64_t>(q);
    h_ ^= x + 0x9E3779B97F4A7C15ull + (h_ << 6) + (h_ >> 2);
  }
  void AddInt(int64_t v) {
    h_ ^= static_cast<uint64_t>(v) + 0x9E3779B97F4A7C15ull + (h_ << 6) + (h_ >> 2);
  }
  uint64_t value() const { return h_; }
 private:
  uint64_t h_ = 0xCBF29CE484222325ull;
};

/* ------------------------------------------------------------------------ */
/* Percentile helper                                                         */
/* ------------------------------------------------------------------------ */

class Series {
 public:
  void Add(double v) { data_.push_back(v); }
  size_t n() const { return data_.size(); }
  double Mean() const {
    if (data_.empty()) return 0.0;
    double s = 0.0;
    for (double v : data_) s += v;
    return s / static_cast<double>(data_.size());
  }
  double Percentile(double p) {
    if (data_.empty()) return 0.0;
    std::sort(data_.begin(), data_.end());
    const double idx = p * static_cast<double>(data_.size() - 1);
    const size_t lo = static_cast<size_t>(std::floor(idx));
    const size_t hi = static_cast<size_t>(std::ceil(idx));
    const double frac = idx - static_cast<double>(lo);
    return data_[lo] * (1.0 - frac) + data_[hi] * frac;
  }
  const std::vector<double>& raw() { return data_; }
 private:
  std::vector<double> data_;
};

/* ------------------------------------------------------------------------ */
/* Latency ring buffer (A7)                                                  */
/* ------------------------------------------------------------------------ */

struct HistoryEntry {
  double x, y, z, vx, vy, vz;
  double health;
  bool alive;
};

class HistoryRing {
 public:
  void Push(const HistoryEntry& e) {
    buf_[head_] = e;
    head_ = (head_ + 1) % kCap;
    if (count_ < kCap) ++count_;
  }
  // State as observed `latency` ticks ago (clamped to the oldest sample).
  HistoryEntry Delayed(int latency) const {
    HistoryEntry out{};
    if (count_ == 0) return out;
    if (latency < 0) latency = 0;
    if (latency >= count_) latency = count_ - 1;
    // newest = head_-1, so delayed = head_-1-latency
    int idx = (head_ - 1 - latency) % kCap;
    if (idx < 0) idx += kCap;
    return buf_[idx];
  }
  int count() const { return count_; }
  void Clear() { head_ = 0; count_ = 0; }
 private:
  static const int kCap = 64;
  HistoryEntry buf_[kCap]{};
  int head_ = 0;
  int count_ = 0;
};

}  // namespace behaviorqa

#endif  // BEHAVIOR_QA_WORLD_H
