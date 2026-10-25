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
//  - optional route memory retains own travel and damage warnings. Unknown
//    ground remains unknown; qualified obstacle recovery still handles walls.

#ifndef BOTCORE_BOT_HUMAN_H
#define BOTCORE_BOT_HUMAN_H

#include <cmath>

#include "bot_aim.h"
#include "bot_loadout.h"
#include "bot_perception.h"
#include "bot_profile.h"
#include "bot_route.h"

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
  double strafe_scale = 1.0; // actual adapter scaling, used only for movement safety
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
  bool escape = false;         // bounded retreat along own recent travel history
  bool travel = false;         // explicit movement/turn hold for own route memory
};

inline int IntMax(int a, int b) { return a > b ? a : b; }
inline double ClampUnit(double v) { return v < -1.0 ? -1.0 : (v > 1.0 ? 1.0 : v); }

class HumanBotPolicy {
 public:
  HumanBotPolicy() { Configure(nullptr); }

  void Configure(const BotProfile* profile, bool exploratory_search=false,
                 bool cecil_p1=false) {
    BotProfile fallback{};
    if (profile == nullptr) {
      BuildProfile(3, 0, 0x1234567u, "BOT-Default", &fallback);
      profile = &fallback;
    }
    profile_ = *profile;
    exploratory_search_ = exploratory_search;
    cecil_p1_ = cecil_p1;
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
    movement_rng_ = Lcg(profile_.seed ^ 0x79B1u);
    next_strafe_tick_ = 20 + static_cast<int>(movement_rng_.Next()%61u);
    search_rng_ = Lcg(profile_.seed ^ 0xA4D3u);
    search_turn_until_ = next_search_tick_ = 0;
    search_sign_ = 1.0;
    los_queries_last_tick_ = 0;
    ray_budget_skips_ = 0;
    target_switches_ = 0;
    planned_tick_ = -1;
    was_alive_ = true;
    dead_since_tick_ = -1;
    self_health_fraction_ = 1.0;
    for(int i=0;i<=kWeaponCount;++i) next_shot_tick_[i]=0;
    self_x_ = self_y_ = self_z_ = 0.0;
    history_count_=history_next_=0; escape_until_=0; last_health_=0;
    escape_active_=retreat_motion_allowed_=false;
    route_.Configure(profile_.seed ^ 0x3A97u);
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
    retreat_motion_allowed_=false;
    const bool saw_threat=target_>=0 && perception_.Visible(target_);
    if (exploratory_search_) route_.Observe(w.tick,w.pose.x,w.pose.y,w.pose.z,w.alive,w.health,saw_threat,w.max_health);
    if (w.alive && std::isfinite(w.health) && std::isfinite(w.pose.x) && std::isfinite(w.pose.z)) {
      if (history_count_ && DistanceTo(w.pose.x,w.pose.y,w.pose.z)>15.0) history_count_=history_next_=0;
      if (!escape_active_ && !saw_threat && was_alive_ && last_health_-w.health>=25.0 && history_count_>=2) {
        const AimPose& old=history_[history_count_==21?history_next_:0];
        const double dx=old.x-w.pose.x,dz=old.z-w.pose.z;
        if (dx*dx+dz*dz>2.25) {
          escape_x_=old.x;escape_z_=old.z;escape_until_=w.tick+100;escape_active_=true;
        }
      }
      if (w.tick%5==0) {
        history_[history_next_]=w.pose;history_next_=(history_next_+1)%21;
        if (history_count_<21)++history_count_;
      }
      last_health_=w.health;
    }
    if(was_alive_ && !w.alive) dead_since_tick_=w.tick;
    if(w.alive) dead_since_tick_=-1;
    self_health_fraction_=w.max_health>0 && std::isfinite(w.health) ?
      std::fmax(0.0,std::fmin(1.0,w.health/w.max_health)) : 1.0;
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
      escape_active_=false;history_count_=history_next_=0;last_health_=0;
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

    if (escape_active_) {
      const double dx=escape_x_-w.pose.x,dz=escape_z_-w.pose.z;
      if (w.tick>=escape_until_ || dx*dx+dz*dz<2.25) escape_active_=false;
      else {
        // Only own observations: no hidden damage-source coordinates or map
        // content reads. Face the previous path before moving; never fire here.
        const double wanted=std::atan2(-dx,-dz)*kRadToDeg;
        const double error=AimController::WrapDeg(wanted-w.pose.yaw_deg);
        cmd.escape=true;
        const double limit=profile_.skill.turn_rate_deg_s*dt;
        cmd.yaw_delta_deg=error < -limit ? -limit : (error > limit ? limit : error);
        cmd.forward=std::fabs(error)<35.0?0.9:0.0;
        retreat_motion_allowed_=cmd.forward>0;
        aim_.Step(w.pose,AimPoint(),dt);
        return cmd;
      }
    }

    const int chosen = ChooseTarget(w.tick);
    if (chosen != target_) {
      if (target_ >= 0 || chosen >= 0) ++target_switches_;
      target_ = chosen;
      target_since_tick_ = w.tick;
    }
    cmd.target = target_;

    if (target_ < 0) {
      // Bounded visual sweeps separated by straight travel in the adapter.
      // Constant yaw plus forward input traps a searching bot in small circles.
      aim_.Step(w.pose, AimPoint(), dt);
      if (w.tick >= next_search_tick_) {
        search_turn_until_ = w.tick + 10 + static_cast<int>(search_rng_.Next()%21u);
        next_search_tick_ = search_turn_until_ + 40 + static_cast<int>(search_rng_.Next()%61u);
        search_sign_ = (search_rng_.Next()&1u) ? 1.0 : -1.0;
      }
      cmd.yaw_delta_deg = w.tick < search_turn_until_
          ? search_sign_ * profile_.skill.search_rate_deg_s * dt : 0.0;
      if (!exploratory_search_) cmd.yaw_delta_deg = profile_.skill.search_rate_deg_s * dt;
      cmd.fire = false;
      cmd.forward = 0.0;
      cmd.strafe = 0.0;
      cmd.weapon = weapons_.Update(BuildLoadout(w, false), w.tick);
      if (exploratory_search_) {
        cmd.travel=true;
        // The bounded retreat has ended. An injured bot scans/defends in place
        // until observed healing or a new life; elapsed time is no safety proof.
        if (!route_.InjuryHold()) {
          const TravelIntent travel=route_.Travel(w.tick,w.pose.x,w.pose.y,w.pose.z,
                                                  w.pose.yaw_deg,profile_.skill.turn_rate_deg_s*dt);
          cmd.forward=travel.forward;cmd.yaw_delta_deg=travel.yaw_delta_deg;
        }
      }
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
        const double lead_time = InterceptTime(dx, dy, dz, tr->vx, tr->vy, tr->vz,
                                                wp.proj_speed);
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
    const WeaponProfile& firing_weapon = WeaponAt(cmd.weapon);
    const bool blast_safe = firing_weapon.self_blast_m <= 0.0 ||
                            distance > firing_weapon.self_blast_m + 1.0;
    cmd.fire = aim.fire_allowed && visible && blast_safe;
    if(cecil_p1_ && cmd.fire && cmd.weapon>=1 && cmd.weapon<=kWeaponCount) {
      const double period=firing_weapon.shot_period_s;
      if(period>0.0){
        const int delay=static_cast<int>(period*kProfileTickHz+0.5);
        if(w.tick<next_shot_tick_[cmd.weapon]) cmd.fire=false;
        else next_shot_tick_[cmd.weapon]=w.tick+(delay>0?delay:1);
      }
    }

    MoveIntent(w, visible, distance, cmd);
    const double bearing=std::atan2(-dx,-dz)*kRadToDeg;
    if (cmd.forward>0 && std::fabs(AimController::WrapDeg(bearing-w.pose.yaw_deg))>45) {
      cmd.forward=0;cmd.travel=true; // turn toward the known target before chasing
    }
    if (exploratory_search_ && (route_.InjuryHold() ||
        !route_.SafeMotion(w.pose.x,w.pose.y,w.pose.z,w.pose.yaw_deg,cmd.forward,cmd.strafe*w.strafe_scale))) {
      cmd.forward=cmd.strafe=0;cmd.travel=true;
    }
    return cmd;
  }

  // Native Fire press/release edge only after a deterministic death delay.
  // With the feature OFF retain the qualified 4-tick pulse.
  bool ShouldRespawnPulse(int tick) const {
    if(dead_since_tick_<0) return false;
    if(!cecil_p1_) return (tick&4)==0;
    const int delay=static_cast<int>(profile_.skill.respawn_delay_s*kProfileTickHz+0.5);
    const int elapsed=tick-dead_since_tick_-delay;
    return elapsed>=0 && ((elapsed&4)==0);
  }

  // Called by the integration when the bot's own health drops (see Perception).
  void NotifyDamage(double before, double after) { perception_.NotifyDamage(before, after); }
  void NotifyNavigation(bool active) { route_.NotifyRecovery(active); }

  // Adapter contract: call after EVERY movement/recovery override, with the
  // same own eye position as WorldView, resultant movement yaw and both final
  // normalized axes (strafe already scaled). On false, zero both translation
  // axes; keep perception, aim and fire. This does not assert unknown ground safe.
  bool AllowFinalMovement(double x,double y,double z,double yaw_deg,
                          double forward,double scaled_strafe) const {
    if (!exploratory_search_) return true;
    if (!route_.SafeMotion(x,y,z,yaw_deg,forward,scaled_strafe)) return false;
    return !route_.InjuryHold() || retreat_motion_allowed_ ||
           std::fabs(forward)+std::fabs(scaled_strafe)<1e-6;
  }

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

  double TargetUtility(const TrackState& t, bool sticky) const {
    double score=1.0/(DistanceTo(t.x,t.y,t.z)+1.0);
    if(cecil_p1_){
      const double hp=std::isfinite(t.health)?
        std::fmax(0.0,std::fmin(100.0,t.health)):100.0;
      const bool threat=t.visible_now && t.facing_known &&
        AimsAtMe(self_x_,self_z_,t.x,t.z,t.yaw_deg,25.0);
      score*=1.0+profile_.skill.lowhp_weight*(1.0-hp/100.0)+
        (threat?profile_.skill.threat_weight*
        (1.0+0.5*(1.0-self_health_fraction_)*profile_.personality.caution):0.0);
    }
    if(sticky) score*=1.35;
    return score;
  }

  int ChooseTarget(int tick) {
    int best = -1;
    double best_score = -1.0;
    for (int slot = 0; slot < kMaxPlayers; ++slot) {
      if (!perception_.Selectable(slot)) continue;
      const TrackState* t = perception_.Track(slot);
      if (t == nullptr) continue;
      const double score=TargetUtility(*t,slot==target_);
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
      // Threat-aware hysteresis; old distance rule preserved when disabled.
      if(cecil_p1_) {
        if(best_score>TargetUtility(*cur,true)*1.10) return best;
      } else if(DistanceTo(bt->x, bt->y, bt->z)*1.4 <
                DistanceTo(cur->x, cur->y, cur->z)) return best;
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
    if (w.tick >= next_strafe_tick_) {
      strafe_sign_ = -strafe_sign_;
      next_strafe_tick_ = w.tick + 20 + static_cast<int>(movement_rng_.Next()%61u);
    }
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
  }

  double DistanceTo(double x, double y, double z) const {
    const double dx = x - self_x_;
    const double dy = y - self_y_;
    const double dz = z - self_z_;
    return std::sqrt(dx * dx + dy * dy + dz * dz);
  }

  BotProfile profile_{};
  RouteMemory route_;
  bool exploratory_search_ = false; // native B2 exposed excessive world deaths
  bool cecil_p1_ = false;
  int dead_since_tick_ = -1;
  int next_shot_tick_[kWeaponCount+1] = {};
  double self_health_fraction_ = 1.0;
  Perception perception_;
  AimController aim_;
  WeaponSelector weapons_;
  int target_ = -1;
  int target_since_tick_ = 0;
  double strafe_sign_ = 1.0;
  Lcg movement_rng_{1u};
  int next_strafe_tick_ = 0;
  Lcg search_rng_{1u};
  int search_turn_until_ = 0, next_search_tick_ = 0;
  double search_sign_ = 1.0;
  int los_queries_last_tick_ = 0;
  int ray_budget_skips_ = 0;
  int target_switches_ = 0;
  bool planned_[kMaxPlayers] = {false};
  int planned_tick_ = -1;
  bool was_alive_ = true;
  double self_x_ = 0.0;
  double self_y_ = 0.0;
  double self_z_ = 0.0;
  AimPose history_[21];
  int history_count_=0,history_next_=0,escape_until_=0;
  double escape_x_=0,escape_z_=0,last_health_=0;
  bool escape_active_=false;
  bool retreat_motion_allowed_=false;
};

}  // namespace botcore

#endif  // BOTCORE_BOT_HUMAN_H
