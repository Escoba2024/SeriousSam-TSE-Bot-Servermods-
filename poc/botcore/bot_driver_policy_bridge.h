// bot_driver_policy_bridge.h - engine-free adapter between BotDriverPolicy
// and the native Retail 1.07 BotDriver.cpp action pipeline.
//
// PURPOSE
//  - Translate the engine-free DriverCommand produced by BotDriverPolicy into
//    the normalized action values that BotDriver.cpp writes into CPlayerAction.
//  - Keep all Retail-specific conventions in one place so that
//    bot_driver_policy.h itself stays engine-free and unit-testable.
//  - Provide helper builders for DriverWorld and SenseInput from the plain
//    numeric snapshots already available in BotDriver.cpp (positions, health,
//    velocities, yaw/pitch). No Engine/Entity types are used here.
//
// NATIVE CONVENTIONS (from poc/ai-integration/gamemp/BotDriver.cpp)
//  - pa_vTranslation(3) = -forward, i.e. full forward motion is negative z.
//  - pa_vTranslation(1) = strafe (positive = right, negative = left).
//  - pa_vTranslation(2) = vertical (jump), driven separately by recovery.
//  - pa_aRotation(1/2) are absolute accumulated angles; the caller subtracts
//    m_aLocalRotation to obtain the delta for this tick.
//  - pa_ulButtons bit 0 = fire; weapon select is (weapon_index << 14).
//
// CecilBotMod concepts used as inspiration (not code):
//  - explicit waypoint graph per map;
//  - item desirability based on need and distance;
//  - retreat when health is low.

#ifndef BOTCORE_BOT_DRIVER_POLICY_BRIDGE_H
#define BOTCORE_BOT_DRIVER_POLICY_BRIDGE_H

#include "bot_driver_policy.h"

namespace botcore {

/* ------------------------------------------------------------------------ */
/* Normalized action ready for CPlayerAction                               */
/* ------------------------------------------------------------------------ */

struct DriverAction {
  double forward = 0.0;   // 0..1, mapped to -z by the native composer
  double strafe = 0.0;    // -1..1, +1 = right
  double up = 0.0;        // jump impulse, 0 or 1 normally
  double yaw_delta_deg = 0.0;    // absolute accumulated heading delta
  double pitch_delta_deg = 0.0;  // absolute accumulated pitch delta
  bool fire = false;
  int weapon = 1;         // desired weapon index (1..14)
  bool active = false;    // true if any command is non-zero
};

/* ------------------------------------------------------------------------ */
/* Builders: numeric snapshots -> engine-free policy inputs                */
/* ------------------------------------------------------------------------ */

inline SenseInput BuildSenseInput(int index,
                                  double x, double y, double z,
                                  double vx, double vy, double vz,
                                  double health,
                                  bool local) {
  SenseInput s{};
  s.index = index;
  s.x = x; s.y = y; s.z = z;
  s.vx = vx; s.vy = vy; s.vz = vz;
  s.health = health;
  s.alive = health > 0.0;
  s.local = local;
  return s;
}

inline NavWorld BuildNavWorld(double x, double y, double z,
                              double yaw_deg, double pitch_deg,
                              double health, double max_health,
                              bool alive,
                              bool has_target = false,
                              double target_distance_m = 0.0) {
  NavWorld w;
  w.x = x; w.y = y; w.z = z;
  w.yaw_deg = yaw_deg;
  (void)pitch_deg;  // stored for API symmetry; navigation uses yaw only
  w.health = health;
  w.max_health = max_health;
  w.alive = alive;
  w.has_target = has_target;
  w.target_distance_m = target_distance_m;
  return w;
}

inline FloorProbes BuildFloorProbes(double front_m, double left_m, double right_m,
                                    double step_m = 1.2) {
  FloorProbes p;
  p.front_m = front_m;
  p.left_m = left_m;
  p.right_m = right_m;
  p.step_m = step_m;
  return p;
}

/* ------------------------------------------------------------------------ */
/* Policy command -> normalized DriverAction                               */
/* ------------------------------------------------------------------------ */

inline DriverAction ApplyCommandToAction(const DriverCommand& cmd) {
  DriverAction a;
  a.forward = cmd.forward;
  a.strafe = cmd.strafe;
  a.yaw_delta_deg = cmd.yaw_delta_deg;
  a.pitch_delta_deg = cmd.pitch_delta_deg;
  a.fire = cmd.fire;
  a.weapon = cmd.weapon > 0 ? cmd.weapon : 1;
  a.active = cmd.active;
  return a;
}

// Full one-shot: world snapshot -> DriverAction. This is the function the
// native BotDriver.cpp would call inside its per-tick loop when bot_bHumanAI
// and a navigation graph are configured.
inline DriverAction BotDriverPolicyTick(BotDriverPolicy& policy,
                                        const DriverWorld& world,
                                        int tick,
                                        double dt) {
  return ApplyCommandToAction(policy.Update(world, tick, dt));
}

// Native weapon-select button value: (weapon_index << 14). Mirrors the
// PLACT_SELECT_WEAPON_SHIFT convention used in botcore_ai.h and the
// integration patch.
inline uint32_t DriverWeaponSelectButtons(int weapon_index) {
  return WeaponSelectButtons(weapon_index);
}

}  // namespace botcore

#endif  // BOTCORE_BOT_DRIVER_POLICY_BRIDGE_H
