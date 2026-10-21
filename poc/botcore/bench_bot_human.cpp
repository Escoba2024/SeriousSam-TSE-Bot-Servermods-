// Decision-layer micro-benchmark for the profile-driven policy.
//
// SCOPE: this measures ONLY the engine-free decision code (perception,
// target selection, aim integration, weapon scoring) on this machine. It is
// NOT a measurement of GameMP.dll, of a bot client process, or of the Hetzner
// runtime, and it deliberately excludes ray casting, entity lookups, action
// composition and networking. Do not quote it as client CPU.
#include <chrono>
#include <cmath>
#include <cstdio>

#include "bot_human.h"

using namespace botcore;

int main() {
  const int kTicks = 200000;
  int count = 0;
  DefaultRoster(&count);
  int failures = 0;

  for (int r = 0; r < count; ++r) {
    BotProfile profile;
    BuildRosterProfile(r, 0, 20261020u, &profile);
    HumanBotPolicy policy;
    policy.Configure(&profile);

    // Eight candidates: four in front, four behind -> exercises both the
    // gate and the budget.
    SenseInput sensed[8];
    bool los[8];
    for (int i = 0; i < 8; ++i) {
      sensed[i].index = i;
      sensed[i].x = 0.0;
      sensed[i].y = 0.0;
      sensed[i].z = (i % 2 == 0) ? -(8.0 + i) : (8.0 + i);
      sensed[i].vx = (i % 2 == 0) ? 3.0 : -3.0;
      sensed[i].vy = 0.0;
      sensed[i].vz = 0.0;
      sensed[i].health = 100.0;
      sensed[i].alive = true;
      sensed[i].local = false;
      los[i] = false;
    }

    double yaw = 0.0;
    long long rays = 0;
    const auto t0 = std::chrono::steady_clock::now();
    for (int t = 0; t < kTicks; ++t) {
      WorldView w;
      w.tick = t;
      w.pose.yaw_deg = yaw;
      w.pose.pitch_deg = 0.0;
      w.alive = true;
      w.health = 80.0;
      w.max_health = 100.0;
      w.usable_weapons = 0x3FFFu;
      w.current_weapon = 2;
      w.deathmatch = true;

      policy.BeginTick(w);
      bool needs[8];
      policy.PlanLosQueries(sensed, 8, needs);
      for (int i = 0; i < 8; ++i) {
        if (needs[i]) {
          ++rays;
          los[i] = true;  // pretend the ray was cast and hit
        } else {
          los[i] = false;
        }
      }
      const BotCommand c = policy.Step(w, sensed, los, 8, 0.05);
      yaw += c.yaw_delta_deg;
    }
    const auto t1 = std::chrono::steady_clock::now();
    const double us =
        std::chrono::duration_cast<std::chrono::nanoseconds>(t1 - t0).count() / 1000.0 /
        kTicks;
    std::printf("%-20s tier=%d persona=%-10s %8.2f us/tick  %.1f rays/tick\n",
                profile.name, profile.tier, PersonalityName(profile.persona), us,
                static_cast<double>(rays) / kTicks);
    if (!(us >= 0.0) || us > 200.0) {
      std::printf("FAIL: implausible per-tick cost\n");
      ++failures;
    }
  }
  std::printf("%s\n", failures ? "BENCH FAIL" : "BENCH PASS");
  return failures ? 1 : 0;
}
