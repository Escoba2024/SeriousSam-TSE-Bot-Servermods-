// bot_driver_policy.h - engine-free coordinator that combines HumanBotPolicy
// (combat) with NavigationPlanner (movement without target / retreat / items).
//
// DESIGN PRINCIPLES
//  - Combat owns targeting, aiming and firing. Navigation never selects a
//    target or pulls the trigger.
//  - Navigation owns movement when combat has no visible target, when the
//    bot is explicitly retreating, or when a high-value item should be fetched.
//  - Both subsystems are optional: HumanBotPolicy works unchanged when no
//    navigation graph is supplied, and NavigationPlanner stays idle when no
//    graph is configured.
//  - All inputs are supplied by the caller; no engine calls, no allocation,
//    deterministic.

#ifndef BOTCORE_BOT_DRIVER_POLICY_H
#define BOTCORE_BOT_DRIVER_POLICY_H

#include "bot_human.h"
#include "bot_navigation_v2.h"

namespace botcore {

struct DriverWorld {
  NavWorld nav;                 // bot's own state / health / target flag
  const SenseInput* players;    // replicated players (for combat perception)
  int player_count;             // number of entries in players[]
  const ItemInfo* items;        // known pickups (may be nullptr)
  int item_count;               // number of entries in items[]
  FloorProbes probes;           // floor distances for pit avoidance
  bool retreat_requested;       // true if health / situation demands retreat
};

struct DriverCommand {
  // Unified command that BotDriver.cpp can translate into CPlayerAction.
  int target = -1;               // combat target, -1 if none
  bool target_visible = false;
  bool fire = false;
  int weapon = 1;
  double yaw_delta_deg = 0.0;
  double pitch_delta_deg = 0.0;
  double forward = 0.0;
  double strafe = 0.0;
  bool active = false;           // true if any command is non-zero

  // Source of the movement decision, for telemetry.
  enum class Source { kCombat = 0, kNavigation = 1, kIdle = 2 } source =
      Source::kIdle;
};

class BotDriverPolicy {
 public:
  BotDriverPolicy() = default;

  void Configure(const BotProfile* profile, const WaypointGraph* graph) {
    human_.Configure(profile);
    nav_.Configure(profile, graph);
  }

  void Reset() {
    human_.Reset();
    nav_.Reset();
  }

  // One complete engine-free tick.
  DriverCommand Update(const DriverWorld& w, int tick, double dt) {
    DriverCommand out;

    // --- 1. Combat policy always runs for perception/aim/fire decisions.
    WorldView world;
    world.tick = tick;
    world.pose.x = w.nav.x;
    world.pose.y = w.nav.y;
    world.pose.z = w.nav.z;
    world.pose.yaw_deg = w.nav.yaw_deg;
    world.pose.pitch_deg = 0.0;  // pitch is supplied separately if needed
    world.alive = w.nav.alive;
    world.health = w.nav.health;
    world.max_health = w.nav.max_health;
    world.usable_weapons = 0x3FFFu;  // placeholder: caller can override
    world.current_weapon = 2;
    world.deathmatch = true;

    human_.BeginTick(world);
    bool needs[kMaxPlayers] = {false};
    human_.PlanLosQueries(w.players, w.player_count, needs);
    bool los[kMaxPlayers] = {false};
    for (int i = 0; i < w.player_count && i < kMaxPlayers; ++i) {
      // In a real integration the caller performs the ray cast. Here we model
      // line-of-sight as granted for all candidates that passed the cheap gate,
      // so the coordinator can be unit-tested without a collision model.
      los[i] = needs[i];
    }
    BotCommand combat = human_.Step(world, w.players, los, w.player_count, dt);

    // --- 2. Navigation policy runs when combat has no visible target or when
    //        retreat/item-fetch is requested.
    NavCommand nav;
    bool use_nav = false;
    if (w.nav.alive) {
      const bool no_target = (combat.target < 0);
      const bool fetch_item = (w.items != nullptr && w.item_count > 0 &&
                               human_.profile().personality.aggression < 0.45 &&
                               (w.nav.health / w.nav.max_health) < 0.65);
      if (w.retreat_requested || (no_target && !w.nav.has_target) || fetch_item) {
        nav = nav_.Update(w.nav, w.items, w.item_count, w.probes, w.retreat_requested);
        use_nav = nav.active;
      }
    }

    // --- 3. Compose output. Combat wins fire/weapon; navigation wins movement
    //        when active, otherwise combat's strafing is preserved.
    out.target = combat.target;
    out.target_visible = combat.target_visible;
    out.fire = combat.fire;
    out.weapon = combat.weapon;
    out.yaw_delta_deg = combat.yaw_delta_deg + (use_nav ? nav.yaw_delta_deg : 0.0);
    out.pitch_delta_deg = combat.pitch_delta_deg;

    if (use_nav) {
      out.forward = nav.forward;
      out.strafe = nav.strafe;
      out.source = DriverCommand::Source::kNavigation;
    } else {
      out.forward = combat.forward;
      out.strafe = combat.strafe;
      out.source = (combat.target >= 0) ? DriverCommand::Source::kCombat
                                         : DriverCommand::Source::kIdle;
    }

    out.active = (out.fire || std::fabs(out.forward) > 1e-6 ||
                  std::fabs(out.strafe) > 1e-6 ||
                  std::fabs(out.yaw_delta_deg) > 1e-6 ||
                  std::fabs(out.pitch_delta_deg) > 1e-6);

    // Bound accumulated yaw delta to avoid the engine wrap trap.
    while (out.yaw_delta_deg > 180.0) out.yaw_delta_deg -= 360.0;
    while (out.yaw_delta_deg < -180.0) out.yaw_delta_deg += 360.0;

    return out;
  }

  const HumanBotPolicy& human() const { return human_; }
  const NavigationPlanner& nav() const { return nav_; }

 private:
  HumanBotPolicy human_;
  NavigationPlanner nav_;
};

}  // namespace botcore

#endif  // BOTCORE_BOT_DRIVER_POLICY_H
