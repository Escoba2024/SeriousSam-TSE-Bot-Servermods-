// bot_perception.h - engine-free perception and target memory for the vanilla
// bot client. The caller performs the actual world ray casts; this module
// decides *which* candidates are worth a ray, what the bot remembers, and how
// quickly it may act on a sighting.
//
// DELIBERATE LIMITS
//  - only information the bot client actually receives is used: replicated
//    player positions/velocities/health and the bot's own health;
//  - no omniscient wall tracking: after losing line of sight the last known
//    position is frozen (velocity is not extrapolated) and confidence decays
//    to zero within memory_s;
//  - the only "sound-like" cue is the bot's own health decreasing, which the
//    client really does observe. It grants a short glance, never a position.
//
// UNITS: degrees, metres, seconds; ticks are 20 Hz.

#ifndef BOTCORE_BOT_PERCEPTION_H
#define BOTCORE_BOT_PERCEPTION_H

#include <cmath>
#include <cstdint>

#include "bot_profile.h"

namespace botcore {

constexpr int kMaxPlayers = 16;

// One candidate as the client can currently see it in replicated state.
struct SenseInput {
  int index;          // replicated player index 0..15
  double x, y, z;     // eye position (viewpoint, absolute)
  double vx, vy, vz;  // world velocity, units/s
  double health;      // replicated health
  bool alive;         // health > 0 and not respawning
  bool local;         // sibling bot of the same client process
  double yaw_deg = 0.0;
  bool facing_known = false;
};

struct TrackState {
  bool occupied = false;
  int index = -1;
  int first_seen_tick = 0;   // start of the current continuous sighting
  int last_seen_tick = 0;    // tick of the last confirmed line of sight
  int visible_ticks = 0;     // consecutive confirmed ticks
  int seen_count = 0;        // total sightings (telemetry)
  bool visible_now = false;  // confirmed line of sight in this tick
  double x = 0.0, y = 0.0, z = 0.0;   // last confirmed position (frozen on loss)
  double vx = 0.0, vy = 0.0, vz = 0.0;  // last confirmed velocity
  double confidence = 0.0;   // 1.0 fresh sighting -> 0.0 forgotten
  double health = 100.0;
  double yaw_deg = 0.0;
  bool facing_known = false;
};

// Fresh replicated yaw only. Unknown orientation must not affect priority.
inline bool AimsAtMe(double self_x,double self_z,double enemy_x,double enemy_z,
                     double enemy_yaw_deg,double tolerance_deg) {
  if(!std::isfinite(self_x)||!std::isfinite(self_z)||
     !std::isfinite(enemy_x)||!std::isfinite(enemy_z)||
     !std::isfinite(enemy_yaw_deg)) return false;
  const double dx=self_x-enemy_x,dz=self_z-enemy_z;
  if(dx*dx+dz*dz<0.01) return false;
  const double desired=std::atan2(-dx,-dz)*kRadToDeg;
  return std::fabs(std::remainder(desired-enemy_yaw_deg,360.0))<=tolerance_deg;
}
class Perception {
 public:
  Perception() { Configure(SkillFor(3), 1u); }

  void Configure(const SkillParams& skill, uint32_t seed) {
    skill_ = skill;
    seed_ = seed ? seed : 1u;
    Reset();
  }

  void Reset() {
    for (int i = 0; i < kMaxPlayers; ++i) tracks_[i] = TrackState();
    tick_ = 0;
    self_x_ = self_y_ = self_z_ = 0.0;
    view_yaw_ = view_pitch_ = 0.0;
    alert_until_tick_ = -1000000;
    alert_events_ = 0;
    gate_passes_ = 0;
    seen_events_ = 0;
  }

  // Called once per tick before any Observe().
  void BeginTick(int tick, double self_x, double self_y, double self_z, double view_yaw,
                 double view_pitch) {
    tick_ = tick;
    self_x_ = self_x;
    self_y_ = self_y;
    self_z_ = self_z;
    view_yaw_ = view_yaw;
    view_pitch_ = view_pitch;
    for (int i = 0; i < kMaxPlayers; ++i) {
      TrackState& t = tracks_[i];
      if (!t.occupied) continue;
      t.visible_now = false;
      t.visible_ticks = 0;
      const int age = tick - t.last_seen_tick;
      const int memory_ticks = MemoryTicks();
      if (age > memory_ticks) {
        t.occupied = false;  // memory expired: the bot really has forgotten
        t.confidence = 0.0;
      } else if (age > 0) {
        t.confidence = 1.0 - static_cast<double>(age) / static_cast<double>(memory_ticks);
      }
    }
  }

  // Cheap pre-filter: should the caller spend a ray on this candidate?
  // Range and field of view only; a damage alert temporarily widens the cone.
  bool NeedsLineOfSight(const SenseInput& in) const {
    if (!in.alive || in.index < 0 || in.index >= kMaxPlayers) return false;
    if (!std::isfinite(in.x) || !std::isfinite(in.y) || !std::isfinite(in.z)) return false;
    const double dx = in.x - self_x_, dy = in.y - self_y_, dz = in.z - self_z_;
    const double d2 = dx * dx + dy * dy + dz * dz;
    if (d2 > skill_.sight_range_m * skill_.sight_range_m) return false;
    if (alerted()) return true;  // "what hit me?" - look around first, then decide
    if (d2 < 1e-6) return true;
    const double dir_yaw = std::atan2(-dx, -dz) * kRadToDeg;
    const double dir_pitch = std::atan2(dy, std::sqrt(dx * dx + dz * dz)) * kRadToDeg;
    const double dyaw = std::fabs(WrapDeg(dir_yaw - view_yaw_));
    // A wider cone horizontally than vertically matches a 4:3 view frustum
    // while staying far below 360 degrees of awareness.
    const double allowed_yaw = skill_.fov_half_deg;
    const double allowed_pitch = skill_.fov_half_deg * 0.75;
    if (dyaw > allowed_yaw) return false;
    if (std::fabs(dir_pitch - view_pitch_) > allowed_pitch) return false;
    return true;
  }

  // Feed the result for one candidate. `los` is the caller's ray result; it is
  // ignored (treated as false) if the candidate failed the cheap pre-filter,
  // so a caller cannot accidentally grant wall vision.
  void Observe(const SenseInput& in, bool los) {
    if (in.index < 0 || in.index >= kMaxPlayers) return;
    if (!in.alive) {
      Forget(in.index);
      return;
    }
    const bool gated = NeedsLineOfSight(in);
    if (gated) ++gate_passes_;
    if (!gated) los = false;

    TrackState& t = tracks_[in.index];
    if (los) {
      // A gap of more than one tick means the target was lost and is being
      // re-acquired: the reaction delay starts over.
      if (!t.occupied || (tick_ - t.last_seen_tick) > 1) {
        const int seen_count = t.seen_count;
        t = TrackState();
        t.seen_count = seen_count;
        t.occupied = true;
        t.index = in.index;
        t.first_seen_tick = tick_;
      }
      t.occupied = true;
      t.index = in.index;
      t.visible_now = true;
      ++t.visible_ticks;
      ++t.seen_count;
      ++seen_events_;
      t.last_seen_tick = tick_;
      t.x = in.x;
      t.y = in.y;
      t.z = in.z;
      t.vx = in.vx;
      t.vy = in.vy;
      t.vz = in.vz;
      t.confidence = 1.0;
      t.health = std::isfinite(in.health)?in.health:100.0;
      t.yaw_deg = in.yaw_deg;
      t.facing_known = in.facing_known && std::isfinite(in.yaw_deg);
    } else if (t.occupied) {
      // Lost sight this tick: freeze the position, drop velocity so nothing
      // is extrapolated through geometry.
      t.visible_now = false;
      t.visible_ticks = 0;
      t.vx = t.vy = t.vz = 0.0;
    }
  }

  // The client observes its own health; that is the only non-visual cue we use.
  // It never reveals a direction or a position.
  void NotifyDamage(double health_before, double health_after) {
    if (!(health_after < health_before)) return;
    const double loss = health_before - health_after;
    if (loss <= 0.0) return;
    const int window = static_cast<int>(skill_.alert_window_s * kProfileTickHz + 0.5);
    alert_until_tick_ = tick_ + (window > 1 ? window : 1);
    ++alert_events_;
  }

  void Forget(int index) {
    if (index < 0 || index >= kMaxPlayers) return;
    tracks_[index] = TrackState();
  }

  /* --- queries --------------------------------------------------------- */

  bool alerted() const { return tick_ <= alert_until_tick_; }

  int MemoryTicks() const {
    const int ticks = static_cast<int>(skill_.memory_s * kProfileTickHz + 0.5);
    return ticks > 1 ? ticks : 1;
  }

  // Reaction delay, shortened while the bot is under fire: a player who is
  // being hit does not need 0.5 s to notice the attacker.
  int ReactionTicks() const {
    int ticks = static_cast<int>(skill_.reaction_s * kProfileTickHz + 0.5);
    if (alerted()) {
      const int halved = ticks / 3;
      ticks = halved > 1 ? halved : 1;
    }
    return ticks > 1 ? ticks : 1;
  }

  const TrackState* Track(int index) const {
    if (index < 0 || index >= kMaxPlayers) return nullptr;
    return tracks_[index].occupied ? &tracks_[index] : nullptr;
  }

  // Visible long enough that the bot may act on it.
  bool Selectable(int index) const {
    const TrackState* t = Track(index);
    if (t == nullptr || !t->visible_now) return false;
    return (tick_ - t->first_seen_tick) >= ReactionTicks();
  }

  bool Visible(int index) const {
    const TrackState* t = Track(index);
    return t != nullptr && t->visible_now;
  }

  // Known but not currently visible; still inside the memory window.
  bool Remembered(int index) const {
    const TrackState* t = Track(index);
    return t != nullptr && !t->visible_now;
  }

  int tick() const { return tick_; }
  // Number of candidates that passed the cheap range/FOV gate (i.e. the
  // number of rays the caller is expected to cast this run).
  int gate_passes() const { return gate_passes_; }
  int seen_events() const { return seen_events_; }
  int alert_events() const { return alert_events_; }

  static double WrapDeg(double a) {
    while (a > 180.0) a -= 360.0;
    while (a < -180.0) a += 360.0;
    return a;
  }

 private:
  SkillParams skill_{};
  uint32_t seed_ = 1u;
  TrackState tracks_[kMaxPlayers];
  int tick_ = 0;
  double self_x_ = 0.0, self_y_ = 0.0, self_z_ = 0.0;
  double view_yaw_ = 0.0, view_pitch_ = 0.0;
  int alert_until_tick_ = -1000000;
  int alert_events_ = 0;
  int gate_passes_ = 0;
  int seen_events_ = 0;
};

}  // namespace botcore

#endif  // BOTCORE_BOT_PERCEPTION_H
