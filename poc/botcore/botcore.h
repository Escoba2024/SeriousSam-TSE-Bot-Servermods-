// botcore.h - standalone, engine-free mirror of the BotDriver tick logic
// ("Pfad D" PoC for Serious Sam: TSE). Used to verify the action-generation
// semantics in isolation (see test_botcore.cpp).
//
// Conventions replicated from the vanilla engine sources:
//  - tick rate: CTimer::TickQuantum = 1/20 s (Engine/Base/Timer.cpp:54)
//  - full forward speed: pa_vTranslation(3) = -plr_fSpeedForward (z < 0!)
//    (GameMP/Game.cpp CControls::CreateAction + EntitiesMP/Player.es
//     ctl_ComposeActionPacket)
//  - pa_aRotation is an ABSOLUTE accumulated angle; consumers compute deltas
//    against the previous action (Player.es CPlayerEntity::ApplyAction)
//  - fire button: bit 0 of pa_ulButtons (PLACT_FIRE, Player.es:259)

#ifndef BOTCORE_H
#define BOTCORE_H

#include <cstdint>
#include <cmath>

namespace botcore {

struct AimAngles { double yaw_deg, pitch_deg; };

inline bool TestJump(int tick) { return tick % 80 < 4; }

// Phase-1 fixed-target test geometry; no navigation or target selection.
inline AimAngles AimAt(double x, double y, double z) {
  const double degrees = 180.0 / std::acos(-1.0);
  return {std::atan2(-x, -z) * degrees,
          std::atan2(y, std::sqrt(x*x + z*z)) * degrees};
}

inline double TestTurnDelta(double current, double target, double limit) {
  const double delta = std::remainder(target - current, 360.0);
  return delta < -limit ? -limit : (delta > limit ? limit : delta);
}

constexpr double kTickQuantum = 1.0 / 20.0;  // 20 Hz
constexpr uint32_t kPlactFire = 1u << 0;     // PLACT_FIRE

struct Params {
  double yaw_speed_deg;   // heading change per second (0 = straight)
  double move_factor;     // 0..1 fraction of plr_fSpeedForward
  double fire_period_s;   // fire pulse period in seconds (<=0 = never)
  int    fire_ticks;      // fire pulse length in ticks
};

struct Action {
  double translation_z;   // velocity along view z (negative = forward)
  double heading_deg;     // absolute accumulated heading (never wrapped)
  uint32_t buttons;       // PLACT_* flags
};

class BotBrain {
 public:
  // bot_index mirrors iLP in BotDriver.cpp (local player index 0..3) and is
  // only used to phase-shift the fire cadence per bot.
  explicit BotBrain(const Params& p, int bot_index = 0)
      : p_(p), idx_(bot_index) {}

  // Advance one tick and produce the action for it.
  Action Step() {
    ++tick_;
    // 1) accumulate heading (absolute, never wrapped - deltas matter)
    heading_deg_ += p_.yaw_speed_deg * kTickQuantum;

    // 2) periodic fire pulse (deterministic, phase-shifted per bot) -
    //    same formula as BotDriver.cpp: (tick + iLP*period/4) % period
    bool fire = false;
    const int period = (p_.fire_period_s >= kTickQuantum)
                           ? static_cast<int>(p_.fire_period_s / kTickQuantum + 0.5)
                           : 0;
    if (period > 0 && p_.fire_ticks > 0) {
      const int fire_len = p_.fire_ticks < period ? p_.fire_ticks : period;
      const int phase_tick = (tick_ + idx_ * period / 4) % period;
      fire = phase_tick < fire_len;
    }

    // 3) compose the action
    Action a;
    a.translation_z = -kSpeedForward * ClampFactor(p_.move_factor);
    a.heading_deg = heading_deg_;
    a.buttons = fire ? kPlactFire : 0;
    return a;
  }

  int tick() const { return tick_; }
  double heading_deg() const { return heading_deg_; }

  // Reference value from vanilla TSE (plr_fSpeedForward default; the engine
  // clamps pa_vTranslation(3) to [-plr_fSpeedForward, +plr_fSpeedBackward]).
  static constexpr double kSpeedForward = 10.0;

 private:
  static double ClampFactor(double f) { return f < 0.0 ? 0.0 : (f > 1.0 ? 1.0 : f); }
  Params p_;
  int idx_ = 0;
  int tick_ = 0;
  double heading_deg_ = 0.0;
};

}  // namespace botcore

#endif  // BOTCORE_H
