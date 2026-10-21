// bot_human.h - profile-driven decision policy for the vanilla bot client.
//
// This is the "one continuous vertical slice": a loaded profile reaches a real
// CPlayerAction through these three calls per tick:
//
//   policy.BeginTick(world);
//   policy.PlanLosQueries(sensed, count, needs_ray);   // cheap, budgets rays
//   ... caller casts `needs_ray[i]` rays ...
//   BotCommand cmd = policy.Step(world, sensed, los, count, dt);
//
// Everything above the engine boundary is deterministic and engine-free, so
// the whole decision chain (profile -> perception -> target -> aim -> weapon ->
// movement command) is unit-testable without Retail, SDK or Windows.
//
// SCOPE OF THIS LAYER
//  - it produces *intent* only: delta angles, forward/strafe factor, fire bit,
//    weapon number. The caller turns that into a CPlayerAction and leaves the
//    existing network/action pipeline untouched.
//  - navigation is not solved here: without a visible target the bot turns in
//    place and scans, exactly like the qualified build does today. The
//    waypoint graph and ObstacleRecovery from botcore_ai.h / bot_navigation.h
//    remain the movement-recovery layer underneath.

#ifndef BOTCORE_BOT_HUMAN_H
#define BOTCORE_BOT_HUMAN_H

#include <cmath>

#include "bot_aim.h"
#include "bot_loadout.h"
#include "bot_perception.h"
#include "bot_profile.h"

namespace botcore {

struct WorldView {
  int tick = 0;
  AimPose pose;
  bool alive = false;
  double health = 0.0;
  double max_health = 100.0;
  uint32_t usable_weapons = 0;  // after ammo filtering
  int current_weapon = 1;
  bool deathmatch = true;
};

struct BotCommand {
  int target = -1;              // -1 = nothing to fight
  bool target_visible = false;  // fresh line of sight this tick
  double yaw_delta_deg = 0.0;   // add to the accumulated heading
  double pitch_delta_deg = 0.0;
  double forward = 0.0;         // -1 back .. +1 forward
  double strafe = 0.0;          // -1 left .. +1 right
  bool fire = false;
  int weapon = 1;
  double aim_error_deg = 90.0;
  double preferred_range_m = 12.0;
  double distance_m = 0.0;
};

inline int IntMax(int a, int b) { return a > b ? a : b; }
inline double ClampUnit(double v) { return v < -1.0 ? -1.0 : (v > 1.0 ? 1.0 : v); }

class HumanBotPolicy {
 public:
  HumanBotPolicy() { Configure(nullptr); }

  void Configure(const BotProfile* profile) {
    BotProfile fallback{};
    if (profile == nullptr) {
      BuildProfile(3, 0, 0x1234567u, "BOT-Default", &fallback);
      profile = &fallback;
    }
    profile_ = *profile;
    perception_.Configure(profile_.skill, profile_.seed ^ 0x5DEECE66u);
    aim_.Configure(profile_.skill, profile_.seed ^ 0x1B54u);
    weapons_.Configure(profile_.skill);
    Reset();
  }

  void Reset() {
    perception_.Reset();
    aim_.Reset();
    weapons_.Reset();
    target_ = -1;
    target_since_tick_ = 0;
    strafe_sign_ = (profile_.seed & 1u) ? 1.0 : -1.0;
    los_queries_last_tick_ = 0;
    ray_budget_skips_ = 0;
    target_switches_ = 0;
    planned_tick_ = -1;
    was_alive_ = true;
    self_x_ = self_y_ = self_z_ = 0.0;
  }

  const BotProfile& profile() const { return profile_; }
  const Perception& perception() const { return perception_; }
  const AimController& aim() const { return aim_; }
  const WeaponSelector& weapons() const { return weapons_; }

  int target() const { return target_; }
  int los_queries_last_tick() const { return los_queries_last_tick_; }
  int ray_budget_skips() const { return ray_budget_skips_; }
  int target_switches() const { return target_switches_; }

  void BeginTick(const WorldView& w) {
    self_x_ = w.pose.x;
    self_y_ = w.pose.y;
    self_z_ = w.pose.z;
    perception_.BeginTick(w.tick, w.pose.x, w.pose.y, w.pose.z, w.pose.yaw_deg,
                          w.pose.pitch_deg);
    if (was_alive_ && !w.alive) {
      // Dying clears the working memory: a respawned player does not know where
      // the opponent who killed him went.
      perception_.Reset();
      aim_.Reset();
      target_ = -1;
    }
    was_alive_ = w.alive;
  }

  // Cheap planning: which candidates may spend a ray this tick. Existing
  // tracks get priority, so a tight budget can never drop the bot's current
  // opponent in favour of a distant stranger.
  void PlanLosQueries(const SenseInput* sensed, int count, bool* needs_ray) {
    if (needs_ray == nullptr) return;
    planned_tick_ = perception_.tick();
    for (int i = 0; i < kMaxPlayers; ++i) planned_[i] = false;
    for (int i = 0; i < count && i < kMaxPlayers; ++i) needs_ray[i] = false;
    los_queries_last_tick_ = 0;
    ray_budget_skips_ = 0;
    if (sensed == nullptr) return;

    int order[kMaxPlayers];
    int order_count = 0;
    for (int i = 0; i < count && i < kMaxPlayers; ++i) {
      if (perception_.NeedsLineOfSight(sensed[i])) order[order_count++] = i;
    }
    for (int a = 1; a < order_count; ++a) {
      const int item = order[a];
      const double key = SortKey(sensed[item]);
      int b = a - 1;
      while (b >= 0 && SortKey(sensed[order[b]]) > key) {
        order[b + 1] = order[b];
        --b;
      }
      order[b + 1] = item;
    }

    const int budget = profile_.skill.max_los_per_tick;
    for (int i = 0; i < order_count; ++i) {
      if (i < budget) {
        needs_ray[order[i]] = true;
        planned_[order[i]] = true;
        ++los_queries_last_tick_;
      } else {
        ++ray_budget_skips_;
      }
    }
  }

  BotCommand Step(const WorldView& w, const SenseInput* sensed, const bool* los, int count,
                  double dt) {
    BotCommand cmd;
    cmd.weapon = w.current_weapon > 0 ? w.current_weapon : 1;
    if (!(dt > 0.0)) dt = 1.0 / kProfileTickHz;

    if (sensed != nullptr) {
      // If PlanLosQueries ran for this tick, only the granted candidates may
      // be observed; a caller that casts fewer rays than it planned cannot
      // accidentally grant wall vision. Without a plan (direct unit-test use)
      // the per-candidate gate in Perception::Observe still applies.
      const bool have_plan = (planned_tick_ == perception_.tick());
      for (int i = 0; i < count && i < kMaxPlayers; ++i) {
        const bool hit = (los != nullptr) && los[i] && (!have_plan || planned_[i]);
        perception_.Observe(sensed[i], hit);
      }
    }

    if (!w.alive || !w.deathmatch) {
      aim_.Step(w.pose, AimPoint(), dt);
      target_ = -1;
      cmd.target = -1;
      return cmd;
    }

    const int chosen = ChooseTarget(w.tick);
    if (chosen != target_) {
      if (target_ >= 0 || chosen >= 0) ++target_switches_;
      target_ = chosen;
      target_since_tick_ = w.tick;
    }
    cmd.target = target_;

    if (target_ < 0) {
      // Nothing to fight: scan at the profile's search rate, stand still.
      aim_.Step(w.pose, AimPoint(), dt);
      cmd.yaw_delta_deg = profile_.skill.search_rate_deg_s * dt;
      cmd.fire = false;
      cmd.forward = 0.0;
      cmd.strafe = 0.0;
      cmd.weapon = weapons_.Update(BuildLoadout(w, false), w.tick);
      return cmd;
    }

    const TrackState* tr = perception_.Track(target_);
    if (tr == nullptr) {
      target_ = -1;
      cmd.target = -1;
      return cmd;
    }

    const bool visible = tr->visible_now;
    cmd.target_visible = visible;

    const double dx = tr->x - w.pose.x;
    const double dy = tr->y - w.pose.y;
    const double dz = tr->z - w.pose.z;
    const double distance = std::sqrt(dx * dx + dy * dy + dz * dz);
    cmd.distance_m = distance;

    cmd.weapon = weapons_.Update(BuildLoadout(w, true, distance), w.tick);
    if (cmd.weapon <= 0) cmd.weapon = w.current_weapon > 0 ? w.current_weapon : 1;

    AimPoint aim_point;
    aim_point.valid = true;
    aim_point.target_key = target_;
    aim_point.visible_now = visible;
    aim_point.x = tr->x;
    aim_point.y = tr->y;
    aim_point.z = tr->z;
    if (visible) {
      const WeaponProfile& wp = WeaponAt(cmd.weapon);
      if (wp.proj_speed > 0.0) {
        const double lead_time = distance / wp.proj_speed;
        const double g = profile_.skill.prediction_gain;
        aim_point.x += tr->vx * lead_time * g;
        aim_point.y += tr->vy * lead_time * g;
        aim_point.z += tr->vz * lead_time * g;
      }
    }

    const AimOutput aim = aim_.Step(w.pose, aim_point, dt);
    cmd.yaw_delta_deg = aim.yaw_delta_deg;
    cmd.pitch_delta_deg = aim.pitch_delta_deg;
    cmd.aim_error_deg = aim.residual_error_deg;
    cmd.fire = aim.fire_allowed && visible;

    MoveIntent(w, visible, distance, cmd);
    return cmd;
  }

  // Called by the integration when the bot's own health drops (see Perception).
  void NotifyDamage(double before, double after) { perception_.NotifyDamage(before, after); }

  double PreferredRange(int weapon) const {
    const WeaponProfile& wp = WeaponAt(weapon);
    double band = 0.5 * (wp.min_m + wp.max_m);
    if (band < 6.0) band = 6.0;
    if (band > 34.0) band = 34.0;
    const double blended = 0.35 * band + 0.65 * profile_.skill.preferred_range_m;
    double r = blended + profile_.personality.range_bias_m;
    if (r < 4.0) r = 4.0;
    if (r > 45.0) r = 45.0;
    return r;
  }

 private:
  double SortKey(const SenseInput& s) const {
    const double tracked_bonus = (perception_.Track(s.index) != nullptr) ? -1000.0 : 0.0;
    const double dx = s.x - self_x_;
    const double dy = s.y - self_y_;
    const double dz = s.z - self_z_;
    return tracked_bonus + std::sqrt(dx * dx + dy * dy + dz * dz);
  }

  LoadoutInput BuildLoadout(const WorldView& w, bool has_target,
                            double distance = 0.0) const {
    LoadoutInput li;
    li.usable_mask = w.usable_weapons;
    li.distance_m = distance;
    li.range_preference = profile_.personality.range_preference;
    li.has_target = has_target;
    li.knife_while_travelling = false;  // VORSCHLAG: enable after a runtime check
    return li;
  }

  int ChooseTarget(int tick) {
    int best = -1;
    double best_score = -1.0;
    for (int slot = 0; slot < kMaxPlayers; ++slot) {
      if (!perception_.Selectable(slot)) continue;
      const TrackState* t = perception_.Track(slot);
      if (t == nullptr) continue;
      const double dist = DistanceTo(t->x, t->y, t->z);
      double score = 1.0 / (dist + 1.0);
      if (slot == target_) score *= 1.35;  // stickiness
      if (score > best_score) {
        best_score = score;
        best = slot;
      }
    }

    if (target_ >= 0 && perception_.Selectable(target_)) {
      const TrackState* cur = perception_.Track(target_);
      if (cur == nullptr) return best;
      // Hard lock right after a switch prevents ping-pong between two equally
      // good opponents.
      if (tick - target_since_tick_ < IntMax(1, perception_.ReactionTicks())) return target_;
      if (best < 0 || best == target_) return target_;
      const TrackState* bt = perception_.Track(best);
      if (bt == nullptr) return target_;
      // Only switch for a clearly closer opponent.
      if (DistanceTo(bt->x, bt->y, bt->z) * 1.4 < DistanceTo(cur->x, cur->y, cur->z)) {
        return best;
      }
      return target_;
    }
    if (best >= 0) return best;

    // Nothing visible: keep the last known position of the previous opponent
    // briefly. No shot is possible without fresh line of sight anyway.
    if (target_ >= 0) {
      const TrackState* t = perception_.Track(target_);
      if (t != nullptr && !t->visible_now && t->confidence > 0.5) return target_;
    }
    return -1;
  }

  void MoveIntent(const WorldView& w, bool visible, double distance, BotCommand& cmd) {
    const double health_frac = w.max_health > 0.0 ? w.health / w.max_health : 1.0;
    const double aggression = EffectiveAggression(profile_, w.tick);
    const double preferred = PreferredRange(cmd.weapon);
    cmd.preferred_range_m = preferred;

    const double retreat_below =
        profile_.skill.retreat_health * (0.6 + 0.9 * profile_.personality.caution);
    if (visible && health_frac < retreat_below) {
      cmd.forward = -0.85;
      cmd.strafe = ClampUnit(strafe_sign_ * 0.5 * profile_.personality.strafe_bias);
      return;
    }
    if (distance > preferred + 3.0) {
      cmd.forward = ClampUnit(0.55 + 0.45 * aggression);
      cmd.strafe = 0.0;
    } else if (distance < preferred - 3.0) {
      cmd.forward = -0.6;
      cmd.strafe = ClampUnit(strafe_sign_ * 0.6 * profile_.personality.strafe_bias);
    } else {
      const double t = static_cast<double>(w.tick) * (1.0 / kProfileTickHz);
      cmd.forward = 0.0;
      cmd.strafe = ClampUnit(strafe_sign_ * profile_.personality.strafe_bias *
                             (0.5 + 0.5 * std::fabs(std::sin(0.9 * t))));
    }
    // Deterministic direction changes: nobody slides sideways forever.
    const int flip_ticks = 60 + static_cast<int>(profile_.seed % 61u);
    if ((w.tick % flip_ticks) == 0) strafe_sign_ = -strafe_sign_;
  }

  double DistanceTo(double x, double y, double z) const {
    const double dx = x - self_x_;
    const double dy = y - self_y_;
    const double dz = z - self_z_;
    return std::sqrt(dx * dx + dy * dy + dz * dz);
  }

  BotProfile profile_{};
  Perception perception_;
  AimController aim_;
  WeaponSelector weapons_;
  int target_ = -1;
  int target_since_tick_ = 0;
  double strafe_sign_ = 1.0;
  int los_queries_last_tick_ = 0;
  int ray_budget_skips_ = 0;
  int target_switches_ = 0;
  bool planned_[kMaxPlayers] = {false};
  int planned_tick_ = -1;
  bool was_alive_ = true;
  double self_x_ = 0.0;
  double self_y_ = 0.0;
  double self_z_ = 0.0;
};

}  // namespace botcore

#endif  // BOTCORE_BOT_HUMAN_H
