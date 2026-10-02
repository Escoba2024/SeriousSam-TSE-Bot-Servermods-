// Standalone reference checks for cadence and geometry; these do not execute
// the retail ctl_ComposeActionPacket or verify its native control-state effects.
//  1. heading delta per tick is exactly yaw_speed * TickQuantum (no jumps,
//     no wraps -> CPlayerEntity::ApplyAction deltas stay small and correct)
//  2. translation is negative z (forward) and equals -speed * factor
//  3. fire duty cycle matches the configured period / pulse length
//  4. simulated ApplyAction rotation sums up to the expected heading change
#include "botcore.h"

#include <cmath>
#include <cstdio>
#include <cstdlib>

using namespace botcore;

static int g_failures = 0;

#define CHECK(cond, msg)                                              \
  do {                                                                \
    if (!(cond)) {                                                    \
      std::printf("FAIL: %s (line %d)\n", msg, __LINE__);             \
      ++g_failures;                                                   \
    }                                                                 \
  } while (0)

int main() {
  CHECK(BotBrain::kSpeedForward == 10.0, "native TSE default forward speed is 10");
  CHECK(TestJump(400) && TestJump(403) && !TestJump(404) && !TestJump(479),
        "fixed-target test jump lasts four ticks every four seconds");
  const AimAngles forward = AimAt(0, 0, -10);
  CHECK(std::fabs(forward.yaw_deg) < 1e-9 && std::fabs(forward.pitch_deg) < 1e-9,
        "test aim forward is negative z");
  CHECK(std::fabs(AimAt(-10, 0, 0).yaw_deg - 90) < 1e-9, "test aim left");
  CHECK(std::fabs(AimAt(10, 0, 0).yaw_deg + 90) < 1e-9, "test aim right");
  CHECK(std::fabs(AimAt(0, 10, -10).pitch_deg - 45) < 1e-9, "test aim elevated target");
  CHECK(std::fabs(TestTurnDelta(179, -179, 2.25) - 2) < 1e-9,
        "test aim takes short path across wrapped entity heading");
  CHECK(std::fabs(TestTurnDelta(0, 90, 2.25) - 2.25) < 1e-9,
        "test aim respects tick turn limit");
  const Params p{45.0, 1.0, 1.0, 3};  // 45 deg/s, full speed, 1 s period, 3 ticks fire
  BotBrain bot(p);

  const int kTicks = 20 * 60;  // one minute of game time
  double prev_heading = 0.0;
  int fire_ticks = 0;
  double applied_rotation_sum = 0.0;  // simulated Player.es ApplyAction deltas
  double last_pa_heading = 0.0;

  std::printf("tick | heading_deg | transl_z | fire | applied_delta\n");
  std::printf("---------------------------------------------------\n");

  for (int i = 0; i < kTicks; ++i) {
    Action a = bot.Step();

    // 1) heading continuity
    const double delta = a.heading_deg - prev_heading;
    CHECK(std::fabs(delta - p.yaw_speed_deg * kTickQuantum) < 1e-9,
          "heading delta must be yaw_speed * TickQuantum every tick");
    prev_heading = a.heading_deg;

    // 2) translation convention
    CHECK(a.translation_z < 0.0, "forward must be negative z");
    CHECK(std::fabs(a.translation_z + BotBrain::kSpeedForward) < 1e-9,
          "full forward must be -plr_fSpeedForward");

    // 3) fire duty cycle
    if (a.buttons & kPlactFire) ++fire_ticks;
    CHECK((a.buttons & ~kPlactFire) == 0, "only PLACT_FIRE may be set in the PoC");

    // 4) simulate the consumer side (Player.es ApplyAction):
    //    delta = pa - last_pa; then the entity rotates by delta/tick per tick
    if (i > 0) {
      const double applied = a.heading_deg - last_pa_heading;
      applied_rotation_sum += applied;
    }
    last_pa_heading = a.heading_deg;

    if (i < 10 || (i % 40) == 0) {
      std::printf("%4d | %10.2f | %8.1f | %4d |\n", i + 1, a.heading_deg,
                  a.translation_z, (a.buttons & kPlactFire) ? 1 : 0);
    }
  }

  // after 60 s at 45 deg/s the bot must have turned 2700 degrees
  CHECK(std::fabs(prev_heading - 2700.0) < 1e-6, "total heading after 60 s");
  // fire duty cycle: 3 of 20 ticks
  const double duty = static_cast<double>(fire_ticks) / kTicks;
  CHECK(std::fabs(duty - 3.0 / 20.0) < 1e-9, "fire duty cycle = fire_ticks/period");
  // applied rotation (deltas) must equal total heading change minus the
  // first action (which establishes the baseline at the consumer)
  CHECK(std::fabs(applied_rotation_sum - (2700.0 - 45.0 * kTickQuantum)) < 1e-6,
        "sum of ApplyAction deltas equals heading change");

  std::printf("---------------------------------------------------\n");
  std::printf("ticks=%d  heading=%.2f deg  fire_ticks=%d (duty %.1f%%)\n",
              kTicks, prev_heading, fire_ticks, duty * 100.0);
  std::printf(g_failures == 0 ? "ALL CHECKS PASSED\n" : "%d CHECKS FAILED\n", g_failures);
  return g_failures == 0 ? 0 : 1;
}
