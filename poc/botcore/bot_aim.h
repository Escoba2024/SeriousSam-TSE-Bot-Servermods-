// bot_aim.h - engine-free, human-like aiming for the vanilla bot client.
//
// MODEL
//  1. Rate and acceleration limits: the crosshair is driven by a rate command
//     with a maximum angular velocity and a maximum angular acceleration. The
//     result is a smooth arc, never a per-tick snap onto the target.
//  2. Insufficient braking: `overshoot` reduces deceleration relative to
//     acceleration, so weak profiles swing past the target and have to come
//     back. This is the mechanical cause of the overshoot, not a random jitter.
//  3. Temporally correlated aim bias: an Ornstein-Uhlenbeck process with
//     correlation time `aim_corr_s`. Consecutive ticks are therefore highly
//     correlated; the aim drifts slowly instead of shaking every frame.
//  4. Per-target misjudgement: on every target change a fixed offset is drawn
//     and kept for as long as that target is held, which is why a bot may
//     consistently aim slightly high on one opponent and dead centre on the
//     next.
//  5. Trigger discipline: firing needs a fresh line of sight, a residual error
//     inside `fire_tol_deg`, and `settle_s` seconds inside that tolerance.
//
// NOT A DIFFICULTY KNOB: there is no "randomly miss N% of shots". Every miss
// has one of the four causes above and is reproducible from the seed.
//
// UNITS: degrees, degrees/second, metres, seconds. Tick rate 20 Hz.

#ifndef BOTCORE_BOT_AIM_H
#define BOTCORE_BOT_AIM_H

#include <cmath>
#include <cstdint>

#include "bot_profile.h"
#include "botcore_ai.h"  // botcore::Lcg

namespace botcore {

// Earliest positive solution of |relative_position + velocity*t| = speed*t.
// No solution or speculative flight beyond max_s: aim at the observed point.
inline double InterceptTime(double x, double y, double z, double vx, double vy,
                            double vz, double speed, double max_s = 2.0) {
  if (!std::isfinite(x) || !std::isfinite(y) || !std::isfinite(z) ||
      !std::isfinite(vx) || !std::isfinite(vy) || !std::isfinite(vz) ||
      !std::isfinite(speed) || speed <= 0 || !std::isfinite(max_s) || max_s <= 0)
    return 0;
  const double a = vx*vx + vy*vy + vz*vz - speed*speed;
  const double b = 2*(x*vx + y*vy + z*vz);
  const double c = x*x + y*y + z*z;
  double t = 0;
  if (std::fabs(a) < 1e-9) {
    if (b < -1e-9) t = -c/b;
  } else {
    const double discriminant = b*b - 4*a*c;
    if (!std::isfinite(discriminant) || discriminant < 0) return 0;
    const double root = std::sqrt(discriminant);
    const double first = (-b-root)/(2*a), second = (-b+root)/(2*a);
    if (first > 0) t = first;
    if (second > 0 && (t == 0 || second < t)) t = second;
  }
  return std::isfinite(t) && t > 0 && t <= max_s ? t : 0;
}

struct AimPose {
  double x = 0.0, y = 0.0, z = 0.0;  // eye position (absolute)
  double yaw_deg = 0.0;              // current absolute view angles
  double pitch_deg = 0.0;
};

struct AimPoint {
  bool valid = false;      // a target worth aiming at exists
  double x = 0.0, y = 0.0, z = 0.0;  // aim point (lead already applied by caller)
  bool visible_now = false;  // fresh line of sight this tick
  int target_key = -1;       // stable target identity, for the per-target offset
};

struct AimOutput {
  double yaw_delta_deg = 0.0;    // add this to the accumulated heading
  double pitch_delta_deg = 0.0;
  double residual_error_deg = 0.0;   // real angular error after this tick
  double perceived_error_deg = 0.0;  // error the bot believes it has
  double rate_deg_s = 0.0;           // applied yaw rate (telemetry)
  bool fire_allowed = false;
  bool settled = false;
  bool overshot = false;  // error changed sign this tick
};

class AimController {
 public:
  AimController() { Configure(SkillFor(3), 1u); }

  void Configure(const SkillParams& skill, uint32_t seed) {
    skill_ = skill;
    rng_ = Lcg(seed ? seed : 1u);
    Reset();
  }

  void Reset() {
    yaw_rate_ = 0.0;
    pitch_rate_ = 0.0;
    bias_yaw_ = 0.0;
    bias_pitch_ = 0.0;
    offset_yaw_ = 0.0;
    offset_pitch_ = 0.0;
    last_target_key_ = -1;
    settled_ticks_ = 0;
    last_error_ = 0.0;
    overshoot_events_ = 0;
    overshoot_total_deg_ = 0.0;
    shots_gated_ = 0;
  }

  // dt in seconds (one tick = 0.05 s). Safe to call with the same pose twice.
  AimOutput Step(const AimPose& pose, const AimPoint& pt, double dt) {
    AimOutput out;
    if (!(dt > 0.0) || !std::isfinite(dt)) return out;

    if (!pt.valid || !std::isfinite(pt.x) || !std::isfinite(pt.y) || !std::isfinite(pt.z)) {
      // No target: let the weapon settle instead of freezing mid-swing.
      Decay(dt);
      settled_ticks_ = 0;
      last_error_ = 0.0;
      return out;
    }

    if (pt.target_key != last_target_key_) {
      last_target_key_ = pt.target_key;
      // Fresh target: draw a new fixed misjudgement and restart the trigger
      // discipline. This is the "first shot after switching" delay.
      const double s = skill_.aim_sigma_deg;
      offset_yaw_ = Gauss() * s * 0.8;
      offset_pitch_ = Gauss() * s * 0.8;
      bias_yaw_ = 0.0;
      bias_pitch_ = 0.0;
      settled_ticks_ = 0;
      last_error_ = 0.0;
    }

    UpdateBias(dt);

    const double dx = pt.x - pose.x;
    const double dy = pt.y - pose.y;
    const double dz = pt.z - pose.z;
    const double desired_yaw = std::atan2(-dx, -dz) * kRadToDeg;
    const double horiz = std::sqrt(dx * dx + dz * dz);
    const double desired_pitch = std::atan2(dy, horiz) * kRadToDeg;

    // Angular errors the bot intends to remove (its own perceived error).
    const double err_yaw =
        WrapDeg(desired_yaw + bias_yaw_ + offset_yaw_ - pose.yaw_deg);
    const double err_pitch =
        (desired_pitch + bias_pitch_ + offset_pitch_ - pose.pitch_deg);

    const double max_rate = skill_.turn_rate_deg_s;
    const double accel = skill_.turn_accel_deg_s2;
    const double brake = accel * (1.0 - 0.75 * skill_.overshoot);  // weak brakes
    const double kp = 10.0;  // 1/s, only shapes the final centimetres

    // Stop-distance planning. A player who plans with their full acceleration
    // but can only brake with a fraction of it (high `overshoot`) will swing
    // past the target - which is exactly the failure we want to model.
    const double cap_yaw = approach_cap(err_yaw, accel, max_rate);
    const double cap_pitch = approach_cap(err_pitch, accel, max_rate * 0.8);
    const double cmd_yaw = ClampD(err_yaw * kp, -cap_yaw, cap_yaw);
    const double cmd_pitch = ClampD(err_pitch * kp, -cap_pitch, cap_pitch);

    yaw_rate_ = RateStep(yaw_rate_, cmd_yaw, accel, brake, dt);
    pitch_rate_ = RateStep(pitch_rate_, cmd_pitch, accel, brake, dt);

    out.yaw_delta_deg = ClampD(yaw_rate_ * dt, -30.0, 30.0);
    out.pitch_delta_deg = ClampD(pitch_rate_ * dt, -25.0, 25.0);
    out.rate_deg_s = std::fabs(yaw_rate_);

    // Real residual error: the crosshair is where the engine will put it,
    // not where the bot thinks it is.
    const double real_yaw = WrapDeg(desired_yaw - (pose.yaw_deg + out.yaw_delta_deg));
    const double real_pitch = desired_pitch - (pose.pitch_deg + out.pitch_delta_deg);
    out.residual_error_deg =
        std::sqrt(real_yaw * real_yaw + real_pitch * real_pitch);

    // The bot perceives its own crosshair, not the true target position. An
    // overshoot is therefore "the crosshair passed the target while still
    // moving fast", not "a random error changed sign near zero".
    if (last_error_ != 0.0 && real_yaw * last_error_ < 0.0 &&
        std::fabs(yaw_rate_) > 0.15 * skill_.turn_rate_deg_s) {
      ++overshoot_events_;
      overshoot_total_deg_ += std::fabs(real_yaw);
      out.overshot = true;
    }
    last_error_ = real_yaw;

    // Trigger discipline is judged on the *perceived* error: a player pulls
    // the trigger when the crosshair looks right, not when it really is.
    // The miss then comes from the bias, which the bot cannot see.
    out.perceived_error_deg =
        std::sqrt(err_yaw * err_yaw + err_pitch * err_pitch);
    const int settle_ticks =
        static_cast<int>(skill_.settle_s / dt + 0.5) > 0
            ? static_cast<int>(skill_.settle_s / dt + 0.5)
            : 1;
    if (out.perceived_error_deg <= skill_.fire_tol_deg) {
      if (settled_ticks_ < settle_ticks) ++settled_ticks_;
    } else {
      settled_ticks_ = 0;
    }
    out.settled = settled_ticks_ >= settle_ticks;
    out.fire_allowed = pt.visible_now && out.settled;
    if (pt.visible_now && !out.fire_allowed) ++shots_gated_;
    return out;
  }

  /* --- telemetry ------------------------------------------------------- */
  int overshoot_events() const { return overshoot_events_; }
  // Total angle by which the crosshair swung past the target, in degrees.
  double overshoot_total_deg() const { return overshoot_total_deg_; }
  int gated_ticks() const { return shots_gated_; }
  double yaw_rate() const { return yaw_rate_; }
  double bias_yaw_deg() const { return bias_yaw_ + offset_yaw_; }
  double bias_pitch_deg() const { return bias_pitch_ + offset_pitch_; }

  static double WrapDeg(double a) {
    while (a > 180.0) a -= 360.0;
    while (a < -180.0) a += 360.0;
    return a;
  }

 private:
  static double ClampD(double v, double lo, double hi) {
    return v < lo ? lo : (v > hi ? hi : v);
  }

  // Highest rate from which the remaining error can still be stopped within
  // the *planned* acceleration: v <= sqrt(2*a*d).
  static double approach_cap(double error, double planned_accel, double max_rate) {
    const double d = std::fabs(error);
    const double v = std::sqrt(2.0 * planned_accel * d);
    return v < max_rate ? v : max_rate;
  }

  // Accelerate toward `cmd`; slow down with the (possibly weaker) `brake` rate.
  // The direction of travel decides which limit applies - a weak brake must
  // not also cripple acceleration in the opposite direction.
  static double RateStep(double rate, double cmd, double accel, double brake, double dt) {
    const bool reversing = (rate > 0.0 && cmd < 0.0) || (rate < 0.0 && cmd > 0.0);
    const bool speeding_up = std::fabs(cmd) >= std::fabs(rate);
    const double rate_limit = (reversing || speeding_up) ? accel : brake;
    const double limit = rate_limit * dt;
    const double diff = cmd - rate;
    const double step = diff > limit ? limit : (diff < -limit ? -limit : diff);
    return rate + step;
  }

  void Decay(double dt) {
    const double stop = skill_.turn_accel_deg_s2 * dt;
    if (yaw_rate_ > stop) yaw_rate_ -= stop;
    else if (yaw_rate_ < -stop) yaw_rate_ += stop;
    else yaw_rate_ = 0.0;
    if (pitch_rate_ > stop) pitch_rate_ -= stop;
    else if (pitch_rate_ < -stop) pitch_rate_ += stop;
    else pitch_rate_ = 0.0;
  }

  // Exact discretisation of an Ornstein-Uhlenbeck process. Consecutive ticks
  // are strongly correlated, which is what makes the error look like a hand
  // drifting rather than noise.
  void UpdateBias(double dt) {
    if (skill_.aim_sigma_deg <= 0.0) {
      bias_yaw_ = bias_pitch_ = 0.0;
      return;
    }
    const double tau = skill_.aim_corr_s > 0.01 ? skill_.aim_corr_s : 0.01;
    const double alpha = std::exp(-dt / tau);
    const double step_sigma = skill_.aim_sigma_deg * std::sqrt(1.0 - alpha * alpha);
    bias_yaw_ = bias_yaw_ * alpha + step_sigma * Gauss();
    bias_pitch_ = bias_pitch_ * alpha + step_sigma * Gauss();
  }

  double Uniform01() {
    const double u = static_cast<double>(rng_.Next() >> 8) * (1.0 / 16777216.0);
    return u > 1e-12 ? u : 1e-12;
  }

  double Gauss() {
    const double u1 = Uniform01();
    const double u2 = Uniform01();
    return std::sqrt(-2.0 * std::log(u1)) * std::cos(2.0 * kPi * u2);
  }

  SkillParams skill_{};
  Lcg rng_{1u};
  double yaw_rate_ = 0.0;
  double pitch_rate_ = 0.0;
  double bias_yaw_ = 0.0;
  double bias_pitch_ = 0.0;
  double offset_yaw_ = 0.0;
  double offset_pitch_ = 0.0;
  int last_target_key_ = -1;
  int settled_ticks_ = 0;
  double last_error_ = 0.0;
  int overshoot_events_ = 0;
  double overshoot_total_deg_ = 0.0;
  int shots_gated_ = 0;
};

}  // namespace botcore

#endif  // BOTCORE_BOT_AIM_H
