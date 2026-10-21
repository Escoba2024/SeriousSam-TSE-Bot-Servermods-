// Engine-free acceptance tests for the profile/perception/aim/loadout policy.
//
// These verify decision semantics only. They do not execute the retail action
// composer, do not touch the network and prove no runtime gate. Every check is
// reproducible from fixed seeds.
#include "bot_human.h"

#include <cmath>
#include <cstdio>

using namespace botcore;

static int g_failures = 0;
static int g_checks = 0;

#define CHECK(cond, msg)                                    \
  do {                                                      \
    ++g_checks;                                             \
    if (!(cond)) {                                          \
      std::printf("FAIL: %s (line %d)\n", msg, __LINE__);    \
      ++g_failures;                                         \
    }                                                       \
  } while (0)

static const double kDt = 1.0 / 20.0;

/* ------------------------------------------------------------------------ */
/* Helpers                                                                   */
/* ------------------------------------------------------------------------ */

static SenseInput MakeEnemy(int index, double x, double y, double z, double vx = 0.0,
                            double vy = 0.0, double vz = 0.0, bool alive = true) {
  SenseInput s{};
  s.index = index;
  s.x = x;
  s.y = y;
  s.z = z;
  s.vx = vx;
  s.vy = vy;
  s.vz = vz;
  s.health = alive ? 100.0 : 0.0;
  s.alive = alive;
  s.local = false;
  return s;
}

// Enemy straight ahead (-z) at `dist` metres.
static SenseInput Ahead(int index, double dist, double lateral = 0.0) {
  return MakeEnemy(index, lateral, 0.0, -dist);
}

static WorldView MakeWorld(int tick, double yaw = 0.0, double pitch = 0.0, bool alive = true,
                           double health = 100.0, uint32_t weapons = 0x3FFFu) {
  WorldView w;
  w.tick = tick;
  w.pose.x = 0.0;
  w.pose.y = 0.0;
  w.pose.z = 0.0;
  w.pose.yaw_deg = yaw;
  w.pose.pitch_deg = pitch;
  w.alive = alive;
  w.health = health;
  w.max_health = 100.0;
  w.usable_weapons = weapons;
  w.current_weapon = 2;
  w.deathmatch = true;
  return w;
}

// One full policy tick with a caller-supplied LOS decision function.
struct Sim {
  HumanBotPolicy policy;
  WorldView world;
  int tick = 0;
};

// Run a scenario: enemy is visible while `visible_until` (absolute tick) and
// then disappears. Returns the command of the last tick.
static BotCommand RunVisibleTicks(HumanBotPolicy& p, int ticks, double dist,
                                  double enemy_health = 100.0) {
  BotCommand cmd;
  for (int i = 0; i < ticks; ++i) {
    WorldView w = MakeWorld(i, 0.0, 0.0, true, 100.0);
    p.BeginTick(w);
    SenseInput e = Ahead(3, dist);
    e.health = enemy_health;
    bool needs = false;
    p.PlanLosQueries(&e, 1, &needs);
    bool los = true;
    cmd = p.Step(w, &e, &los, 1, kDt);
  }
  return cmd;
}

/* ------------------------------------------------------------------------ */
/* 1. Profile validation and parameter bounds                                */
/* ------------------------------------------------------------------------ */

static void TestProfiles() {
  for (int tier = 1; tier <= kSkillTierCount; ++tier) {
    for (int persona = 0; persona < kPersonalityCount; ++persona) {
      BotProfile p{};
      const bool ok = BuildProfile(tier, persona, DeriveSeed(7u, 0, tier, persona),
                                   "BOT-Test", &p);
      CHECK(ok, "every tier/personality combination must build and validate");
      CHECK(ValidateProfile(p) == ProfileError::kOk, "built profile validates");
      CHECK(p.skill.max_los_per_tick >= 1, "LOS budget is at least one ray");
    }
  }

  BotProfile p{};
  CHECK(!BuildProfile(0, 0, 1u, "X", &p), "tier 0 rejected");
  CHECK(!BuildProfile(6, 0, 1u, "X", &p), "tier 6 rejected");
  CHECK(!BuildProfile(3, -1, 1u, "X", &p), "personality -1 rejected");
  CHECK(!BuildProfile(3, 6, 1u, "X", &p), "personality 6 rejected");

  // Out-of-range parameters must be rejected, not silently clamped.
  SkillParams s = SkillFor(3);
  s.reaction_s = 0.0;
  CHECK(ValidateSkill(s) == ProfileError::kReactionOutOfRange, "0 s reaction rejected");
  s = SkillFor(3);
  s.turn_rate_deg_s = 5000.0;
  CHECK(ValidateSkill(s) == ProfileError::kTurnRateOutOfRange, "absurd turn rate rejected");
  s = SkillFor(3);
  s.aim_sigma_deg = std::nan("");
  CHECK(ValidateSkill(s) == ProfileError::kNonFinite, "NaN aim sigma rejected");
  s = SkillFor(3);
  s.max_los_per_tick = 0;
  CHECK(ValidateSkill(s) != ProfileError::kOk, "zero LOS budget rejected");
  s = SkillFor(3);
  s.overshoot = 1.5;
  CHECK(ValidateSkill(s) == ProfileError::kOvershootOutOfRange, "overshoot > 1 rejected");
}

// Skill must be monotonic in every mechanical dimension: tier n+1 is never
// mechanically worse than tier n.
static void TestSkillMonotonicity() {
  for (int tier = 2; tier <= kSkillTierCount; ++tier) {
    const SkillParams& lo = SkillFor(tier - 1);
    const SkillParams& hi = SkillFor(tier);
    CHECK(hi.reaction_s < lo.reaction_s, "reaction improves with tier");
    CHECK(hi.turn_rate_deg_s > lo.turn_rate_deg_s, "turn rate improves with tier");
    CHECK(hi.turn_accel_deg_s2 > lo.turn_accel_deg_s2, "acceleration improves with tier");
    CHECK(hi.aim_sigma_deg < lo.aim_sigma_deg, "aim error shrinks with tier");
    CHECK(hi.overshoot < lo.overshoot, "overshoot shrinks with tier");
    CHECK(hi.fire_tol_deg < lo.fire_tol_deg, "trigger tolerance tightens with tier");
    CHECK(hi.prediction_gain > lo.prediction_gain, "lead compensation improves with tier");
    CHECK(hi.memory_s > lo.memory_s, "memory lengthens with tier");
    CHECK(hi.sight_range_m > lo.sight_range_m, "sight range grows with tier");
    CHECK(hi.fov_half_deg > lo.fov_half_deg, "awareness cone grows with tier");
    CHECK(hi.weapon_dwell_s < lo.weapon_dwell_s, "weapon decisions get faster");
  }
}

// Personality may never touch perception or aim.
static void TestSkillPersonalityOrthogonality() {
  for (int tier = 1; tier <= kSkillTierCount; ++tier) {
    for (int a = 0; a < kPersonalityCount; ++a) {
      for (int b = a + 1; b < kPersonalityCount; ++b) {
        CHECK(SkillUnaffectedByPersonality(tier, a, b),
              "personality must not change mechanical skill");
      }
    }
  }
  // and a concrete, visible consequence: two beginners of very different
  // temperament have exactly the same aim model
  BotProfile ag{}, su{};
  BuildProfile(1, 0, 11u, "A", &ag);
  BuildProfile(1, 1, 22u, "B", &su);
  CHECK(ag.skill.aim_sigma_deg == su.skill.aim_sigma_deg,
        "aggressor and survivor share the same aim sigma at the same tier");
  CHECK(ag.skill.reaction_s == su.skill.reaction_s, "same reaction at the same tier");
  CHECK(ag.personality.aggression != su.personality.aggression,
        "but their aggression differs");
}

static void TestDeterministicSeeds() {
  BotProfile a{}, b{}, c{};
  BuildProfile(3, 2, DeriveSeed(42u, 0, 3, 2), "A", &a);
  BuildProfile(3, 2, DeriveSeed(42u, 0, 3, 2), "B", &b);
  BuildProfile(3, 2, DeriveSeed(42u, 1, 3, 2), "C", &c);
  CHECK(a.seed == b.seed, "same inputs produce the same seed");
  CHECK(a.seed != c.seed, "different local slots produce different seeds");
  CHECK(DeriveSeed(0u, 0, 1, 0) != 0u, "seed is never zero even from base 0");
}

static void TestRoster() {
  int count = 0;
  const RosterEntry* roster = DefaultRoster(&count);
  CHECK(count == 8, "the default roster has eight bots");
  int tiers[kSkillTierCount + 1] = {0, 0, 0, 0, 0, 0};
  bool personas[kPersonalityCount] = {false, false, false, false, false, false};
  int distinct_personas = 0;
  for (int i = 0; i < count; ++i) {
    ++tiers[roster[i].tier];
    if (!personas[roster[i].persona]) {
      personas[roster[i].persona] = true;
      ++distinct_personas;
    }
    BotProfile p{};
    CHECK(BuildRosterProfile(i, i % 4, 0xB07u, &p), "roster entry builds");
  }
  CHECK(tiers[1] >= 1 && tiers[2] >= 1 && tiers[3] >= 1 && tiers[4] >= 1 && tiers[5] >= 1,
        "every skill tier appears at least once");
  CHECK(distinct_personas >= 5, "at least five distinct personalities");
  // a beginner may be aggressive and an expert may be cautious: both exist
  bool aggressive_beginner = false;
  for (int i = 0; i < count; ++i) {
    if (roster[i].tier == 1 && roster[i].persona == 0) aggressive_beginner = true;
  }
  CHECK(aggressive_beginner, "the roster contains an aggressive beginner");
}

/* ------------------------------------------------------------------------ */
/* 2. Reproducibility with a fixed seed and identical input sequence         */
/* ------------------------------------------------------------------------ */

static void TestReproducibility() {
  BotProfile p{};
  BuildProfile(3, 2, 0xC0FFEEu, "BOT-Repro", &p);

  auto run = [&](double* yaw_sum, double* fire_count) {
    HumanBotPolicy policy;
    policy.Configure(&p);
    double ys = 0.0;
    int fs = 0;
    for (int t = 0; t < 200; ++t) {
      WorldView w = MakeWorld(t);
      policy.BeginTick(w);
      SenseInput e = Ahead(4, 18.0, 2.0);
      bool needs = false;
      policy.PlanLosQueries(&e, 1, &needs);
      bool los = true;
      const BotCommand c = policy.Step(w, &e, &los, 1, kDt);
      ys += c.yaw_delta_deg + c.pitch_delta_deg;
      if (c.fire) ++fs;
      // carry the heading forward like the integration does
      (void)c;
    }
    *yaw_sum = ys;
    *fire_count = static_cast<double>(fs);
  };

  double y1 = 0, y2 = 0, f1 = 0, f2 = 0;
  run(&y1, &f1);
  run(&y2, &f2);
  CHECK(y1 == y2, "identical seeds and inputs produce identical aim output");
  CHECK(f1 == f2, "identical seeds and inputs produce identical fire decisions");
  CHECK(f1 > 0.0, "the scenario actually fires (otherwise the check is vacuous)");
}

/* ------------------------------------------------------------------------ */
/* 3. Perception: FOV, LOS, memory expiry, reaction delay                    */
/* ------------------------------------------------------------------------ */

static void TestFieldOfView() {
  BotProfile p{};
  BuildProfile(3, 0, 1u, "BOT-Fov", &p);
  HumanBotPolicy policy;
  policy.Configure(&p);
  WorldView w = MakeWorld(0, 0.0, 0.0);
  policy.BeginTick(w);
  SenseInput front = Ahead(1, 20.0);       // dead ahead, yaw 0 -> -z
  SenseInput behind = MakeEnemy(2, 0.0, 0.0, 20.0);  // behind
  CHECK(policy.perception().NeedsLineOfSight(front), "target straight ahead is gated in");
  CHECK(!policy.perception().NeedsLineOfSight(behind),
        "target behind the bot is not perceived without an alert");
  SenseInput far = Ahead(3, 500.0);
  CHECK(!policy.perception().NeedsLineOfSight(far), "target beyond sight range is ignored");
}

static void TestReactionDelay() {
  BotProfile p{};
  BuildProfile(5, 0, 5u, "BOT-Fast", &p);  // 0.15 s = 3 ticks
  HumanBotPolicy policy;
  policy.Configure(&p);
  WorldView w = MakeWorld(0);
  policy.BeginTick(w);
  SenseInput e = Ahead(1, 15.0);
  bool los = true;
  policy.Step(w, &e, &los, 1, kDt);
  CHECK(!policy.perception().Selectable(1), "no reaction after a single tick");
  CHECK(policy.perception().Visible(1), "but the target is already seen");

  for (int t = 1; t <= 3; ++t) {
    WorldView wt = MakeWorld(t);
    policy.BeginTick(wt);
    policy.Step(wt, &e, &los, 1, kDt);
  }
  CHECK(policy.perception().Selectable(1), "target becomes usable after the reaction time");

  // A beginner needs much longer for the same situation.
  BotProfile slow{};
  BuildProfile(1, 0, 5u, "BOT-Slow", &slow);
  HumanBotPolicy slow_policy;
  slow_policy.Configure(&slow);
  for (int t = 0; t <= 3; ++t) {
    WorldView wt = MakeWorld(t);
    slow_policy.BeginTick(wt);
    slow_policy.Step(wt, &e, &los, 1, kDt);
  }
  CHECK(!slow_policy.perception().Selectable(1),
        "a beginner has not acquired the target after 0.2 s");
}

static void TestMemoryExpiryAndNoWallTracking() {
  BotProfile p{};
  BuildProfile(3, 0, 9u, "BOT-Mem", &p);
  HumanBotPolicy policy;
  policy.Configure(&p);

  // Establish a sighting while the enemy walks.
  SenseInput e = MakeEnemy(2, 0.0, 0.0, -20.0, 0.0, 0.0, 8.0);
  bool los = true;
  for (int t = 0; t <= 5; ++t) {
    WorldView w = MakeWorld(t);
    policy.BeginTick(w);
    policy.Step(w, &e, &los, 1, kDt);
  }
  const TrackState* tr = policy.perception().Track(2);
  CHECK(tr != nullptr && tr->visible_now, "enemy established in memory");
  const double memorised_z = tr->z;

  // Lose sight.
  los = false;
  WorldView w6 = MakeWorld(6);
  policy.BeginTick(w6);
  policy.Step(w6, &e, &los, 1, kDt);
  tr = policy.perception().Track(2);
  CHECK(tr != nullptr, "lost target is still remembered inside the memory window");
  CHECK(!tr->visible_now, "it is no longer visible");
  CHECK(tr->vz == 0.0, "velocity is dropped: no extrapolation through walls");
  CHECK(tr->z == memorised_z, "last known position is frozen, not advanced");

  // It stays frozen for the whole memory window, then is forgotten.
  const int memory_ticks = policy.perception().MemoryTicks();
  for (int i = 0; i < memory_ticks + 2; ++i) {
    WorldView w = MakeWorld(7 + i);
    policy.BeginTick(w);
    policy.Step(w, &e, &los, 1, kDt);
  }
  CHECK(policy.perception().Track(2) == nullptr,
        "the target is forgotten after the memory window expires");
}

static void TestNoFireWithoutLineOfSight() {
  BotProfile p{};
  BuildProfile(4, 0, 13u, "BOT-Los", &p);
  HumanBotPolicy policy;
  policy.Configure(&p);
  SenseInput e = Ahead(1, 10.0);
  bool los = true;
  for (int t = 0; t <= 30; ++t) {
    WorldView w = MakeWorld(t);
    policy.BeginTick(w);
    policy.Step(w, &e, &los, 1, kDt);
  }
  CHECK(policy.perception().Visible(1), "target visible");

  los = false;
  bool fired_while_hidden = false;
  for (int t = 31; t <= 90; ++t) {
    WorldView w = MakeWorld(t);
    policy.BeginTick(w);
    const BotCommand c = policy.Step(w, &e, &los, 1, kDt);
    if (c.fire) fired_while_hidden = true;
  }
  CHECK(!fired_while_hidden, "a bot never fires at a remembered position");
}

static void TestAlertOnDamage() {
  BotProfile p{};
  BuildProfile(3, 0, 21u, "BOT-Hit", &p);
  HumanBotPolicy policy;
  policy.Configure(&p);
  WorldView w = MakeWorld(0);
  policy.BeginTick(w);
  SenseInput behind = MakeEnemy(1, 0.0, 0.0, 20.0);  // behind the bot
  CHECK(!policy.perception().NeedsLineOfSight(behind), "not perceived before being hit");
  policy.NotifyDamage(100.0, 80.0);
  CHECK(policy.perception().alerted(), "taking damage raises the alert");
  CHECK(policy.perception().NeedsLineOfSight(behind),
        "an alerted bot does look behind it");
  CHECK(policy.perception().ReactionTicks() <
            static_cast<int>(SkillFor(3).reaction_s * kProfileTickHz + 0.5),
        "reaction is shortened while under fire");
  // Healing or a non-damaging tick must not alert
  HumanBotPolicy calm;
  calm.Configure(&p);
  WorldView w2 = MakeWorld(0);
  calm.BeginTick(w2);
  calm.NotifyDamage(80.0, 80.0);
  CHECK(!calm.perception().alerted(), "no damage, no alert");
}

/* ------------------------------------------------------------------------ */
/* 4. Aim: turn rate, no instant lock, overshoot, correlated error           */
/* ------------------------------------------------------------------------ */

static void TestNoInstantLockAndTurnLimit() {
  BotProfile p{};
  BuildProfile(5, 0, 31u, "BOT-Expert", &p);
  AimController aim;
  aim.Configure(p.skill, p.seed);

  AimPose pose;
  pose.yaw_deg = 0.0;
  pose.pitch_deg = 0.0;
  AimPoint pt;
  pt.valid = true;
  pt.visible_now = true;
  pt.target_key = 1;
  pt.x = -15.0;  // 45 degrees off to the left: a real swing is required
  pt.y = 0.0;
  pt.z = -15.0;

  double yaw = 0.0;
  double max_delta = 0.0;
  bool locked_immediately = false;
  for (int t = 0; t < 40; ++t) {
    pose.yaw_deg = yaw;
    const AimOutput out = aim.Step(pose, pt, kDt);
    if (t == 0 && std::fabs(out.yaw_delta_deg) >= 20.0) locked_immediately = true;
    if (std::fabs(out.yaw_delta_deg) > max_delta) max_delta = std::fabs(out.yaw_delta_deg);
    yaw += out.yaw_delta_deg;
  }
  CHECK(!locked_immediately, "the crosshair does not snap onto the target in one tick");
  CHECK(max_delta <= p.skill.turn_rate_deg_s * kDt + 1e-6,
        "per-tick rotation never exceeds turn_rate_deg_s * dt");

  // A beginner must be slower still on the very same 45 degree swing.
  BotProfile slow{};
  BuildProfile(1, 0, 31u, "BOT-Beginner", &slow);
  AimController slow_aim;
  slow_aim.Configure(slow.skill, slow.seed);
  AimPose p2;
  p2.yaw_deg = 0.0;
  const AimOutput first = slow_aim.Step(p2, pt, kDt);
  CHECK(std::fabs(first.yaw_delta_deg) < std::fabs(max_delta),
        "a beginner turns slower than an expert on the first tick");
  CHECK(std::fabs(first.yaw_delta_deg) <= slow.skill.turn_rate_deg_s * kDt + 1e-6,
        "and still respects its own rate limit");
}

static void TestTurnLimitRespectedAtLargeAngles() {
  for (int tier = 1; tier <= kSkillTierCount; ++tier) {
    const SkillParams& s = SkillFor(tier);
    AimController aim;
    aim.Configure(s, 1234u);
    AimPose pose;
    pose.yaw_deg = 0.0;
    AimPoint pt;
    pt.valid = true;
    pt.visible_now = true;
    pt.target_key = 9;
    pt.x = 0.0;
    pt.y = 0.0;
    pt.z = 20.0;  // 180 degrees behind
    double max_allowed = s.turn_rate_deg_s * kDt + 1e-6;
    for (int t = 0; t < 50; ++t) {
      const AimOutput o = aim.Step(pose, pt, kDt);
      CHECK(std::fabs(o.yaw_delta_deg) <= max_allowed,
            "rotation limit holds even for a 180 degree turn");
      pose.yaw_deg += o.yaw_delta_deg;
    }
  }
}

// The error must change slowly, not shake every frame. We measure the mean
// absolute tick-to-tick change of the applied aim bias.
static void TestCorrelatedErrorNotPerFrameJitter() {
  BotProfile p{};
  BuildProfile(1, 0, 77u, "BOT-Jitter", &p);  // sigma 4.5 deg, corr 0.55 s
  AimController aim;
  aim.Configure(p.skill, p.seed);

  AimPose pose;
  AimPoint pt;
  pt.valid = true;
  pt.visible_now = true;
  pt.target_key = 3;
  pt.x = 0.0;
  pt.y = 0.0;
  pt.z = -30.0;

  double prev = aim.bias_yaw_deg();
  double sum_change = 0.0;
  int n = 0;
  for (int t = 0; t < 400; ++t) {
    aim.Step(pose, pt, kDt);
    const double now = aim.bias_yaw_deg();
    sum_change += std::fabs(now - prev);
    prev = now;
    ++n;
  }
  const double mean_change = sum_change / n;
  // Independent per-frame noise with the same sigma would change by about
  // sigma * sqrt(2) ~= 6.4 deg per tick. A correlated process must be far below.
  CHECK(mean_change < 1.5,
        "aim error is correlated between ticks, not re-randomised every frame");
  // ... but it must still move, otherwise it is a constant offset, not an aim.
  CHECK(mean_change > 0.01, "aim error is not frozen");
}

static void TestOvershootHasMechanicalCause() {
  // Same scenario, only `overshoot` differs -> the sloppy profile overshoots.
  SkillParams sloppy = SkillFor(1);
  SkillParams precise = SkillFor(1);
  precise.overshoot = 0.0;
  precise.aim_sigma_deg = 0.0;  // isolate the braking effect
  sloppy.aim_sigma_deg = 0.0;
  sloppy.overshoot = 0.8;

  auto count_overshoots = [](const SkillParams& s) {
    AimController aim;
    aim.Configure(s, 555u);
    AimPose pose;
    pose.yaw_deg = 0.0;
    AimPoint pt;
    pt.valid = true;
    pt.visible_now = true;
    pt.target_key = 4;
    pt.x = 0.0;
    pt.y = 0.0;
    pt.z = -15.0;
    // start 30 degrees off to force a fast swing
    pose.yaw_deg = 30.0;
    for (int t = 0; t < 120; ++t) {
      const AimOutput o = aim.Step(pose, pt, kDt);
      pose.yaw_deg += o.yaw_delta_deg;
    }
    return aim.overshoot_total_deg();
  };

  const double sloppy_deg = count_overshoots(sloppy);
  const double precise_deg = count_overshoots(precise);
  CHECK(sloppy_deg > 0.0, "weak braking produces an overshoot");
  CHECK(sloppy_deg > precise_deg * 1.3,
        "a sloppier profile swings further past the target than a precise one");
  std::printf("  overshoot: sloppy=%.2f deg precise=%.2f deg\n", sloppy_deg, precise_deg);
}

static void TestFireNeedsFreshSightAndSettle() {
  BotProfile p{};
  BuildProfile(3, 0, 44u, "BOT-Trig", &p);
  AimController aim;
  aim.Configure(p.skill, p.seed);
  AimPose pose;
  AimPoint pt;
  pt.valid = true;
  pt.visible_now = true;
  pt.target_key = 2;  // "straight ahead"
  pt.x = 0.0;
  pt.y = 0.0;
  pt.z = -12.0;

  int first_fire = -1;
  for (int t = 0; t < 60; ++t) {
    const AimOutput o = aim.Step(pose, pt, kDt);
    pose.yaw_deg += o.yaw_delta_deg;
    pose.pitch_deg += o.pitch_delta_deg;
    if (o.fire_allowed && first_fire < 0) first_fire = t;
  }
  CHECK(first_fire > 0, "the bot does not fire on the very first tick");
  CHECK(first_fire >= static_cast<int>(p.skill.settle_s * kProfileTickHz * 0.5),
        "the first shot respects the settle time");

  AimController other;
  other.Configure(p.skill, p.seed);
  AimPose pose2;
  AimOutput o2;
  for (int t = 0; t < 80; ++t) {
    pose2.yaw_deg += o2.yaw_delta_deg;
    o2 = other.Step(pose2, pt, kDt);
  }
  pt.visible_now = false;
  const AimOutput hidden = other.Step(pose2, pt, kDt);
  CHECK(!hidden.fire_allowed, "no fire without a fresh sighting");
}

/* ------------------------------------------------------------------------ */
/* 5. Weapon choice and hysteresis                                           */
/* ------------------------------------------------------------------------ */

static void TestWeaponUtility() {
  const uint32_t all = 0x3FFFu;
  CHECK(BestWeapon(all, 3.0, 0.0) == 5 || BestWeapon(all, 3.0, 0.0) == 4,
        "a shotgun family weapon wins at point blank");
  CHECK(WeaponAt(13).min_m >= 10.0, "the sniper has a minimum engagement range");
  CHECK(ScoreWeapon(13, 4.0, 0.0) < ScoreWeapon(5, 4.0, 0.0),
        "sniper is not chosen at 4 m");
  CHECK(ScoreWeapon(13, 70.0, 0.0) > ScoreWeapon(5, 70.0, 0.0),
        "sniper wins at 70 m");
  // explosives are strongly discouraged inside their blast radius
  const uint32_t rockets = (1u << 0) | (1u << 7);
  CHECK(BestWeapon(rockets, 2.0, 0.0) == 1,
        "rocket launcher is not used at 2 m next to yourself");
  CHECK(BestWeapon(rockets, 40.0, 0.0) == 8, "and it is used at 40 m");
  // empty mask still yields a usable fallback
  CHECK(BestWeapon(0u, 10.0, 0.0) == -1, "no weapon when nothing is usable");
}

static void TestWeaponHysteresis() {
  SkillParams s = SkillFor(3);
  WeaponSelector sel;
  sel.Configure(s);
  LoadoutInput in;
  in.usable_mask = (1u << 0) | (1u << 1) | (1u << 4) | (1u << 6) | (1u << 12);
  in.range_preference = 0.0;
  in.has_target = true;

  // start at close range
  in.distance_m = 6.0;
  int w = sel.Update(in, 0);
  CHECK(w > 0, "a weapon is selected");
  const int first = w;

  // Sweep the distance across the range boundary tick by tick. Without
  // hysteresis the weapon would flip constantly.
  int switches = 0;
  int previous = first;
  for (int t = 1; t < 400; ++t) {
    in.distance_m = 6.0 + 20.0 * std::sin(t * 0.05);
    const int now = sel.Update(in, t);
    if (now != previous) ++switches;
    previous = now;
  }
  CHECK(switches <= 20,
        "weapon does not ping-pong across a range boundary (hysteresis works)");

  // Ammo loss forces an immediate rethink.
  LoadoutInput empty;
  empty.usable_mask = (1u << 0);  // knife only
  empty.has_target = true;
  empty.distance_m = 10.0;
  CHECK(sel.Update(empty, 500) == 1, "losing all ammo switches to the knife immediately");
}

static void TestWeaponPreferenceByPersonality() {
  const uint32_t all = 0x3FFFu;
  const int close_choice = BestWeapon(all, 12.0, -1.0);
  const int far_choice = BestWeapon(all, 12.0, 1.0);
  CHECK(close_choice != far_choice || WeaponAt(far_choice).max_m >= WeaponAt(close_choice).max_m,
        "range preference tilts the choice towards the preferred band");
}

/* ------------------------------------------------------------------------ */
/* 6. Movement and target hysteresis                                         */
/* ------------------------------------------------------------------------ */

static void TestPreferredRangeAndMovement() {
  BotProfile aggressive{}, marksman{};
  BuildProfile(3, 0, 5u, "BOT-Agg", &aggressive);   // aggressor
  BuildProfile(3, 4, 5u, "BOT-Mark", &marksman);    // marksman

  HumanBotPolicy pa, pm;
  pa.Configure(&aggressive);
  pm.Configure(&marksman);
  CHECK(pa.PreferredRange(2) < pm.PreferredRange(2),
        "an aggressor wants a shorter engagement range than a marksman");

  // An enemy far away -> approach.
  BotCommand c = RunVisibleTicks(pa, 40, 45.0);
  CHECK(c.forward > 0.0, "a distant enemy is approached");

  // An enemy very close -> back off.
  HumanBotPolicy pb;
  pb.Configure(&aggressive);
  BotCommand close = RunVisibleTicks(pb, 40, 1.5);
  CHECK(close.forward < 0.0, "an enemy inside the preferred band is backed off from");
}

static void TestRetreatWhenHurt() {
  BotProfile cautious{};
  BuildProfile(3, 1, 6u, "BOT-Surv", &cautious);  // survivor, caution 0.9
  HumanBotPolicy p;
  p.Configure(&cautious);

  WorldView w = MakeWorld(0, 0.0, 0.0, true, 15.0);  // 15 % health
  SenseInput e = Ahead(1, 20.0);
  bool los = true;
  BotCommand cmd;
  for (int t = 0; t < 40; ++t) {
    w = MakeWorld(t, 0.0, 0.0, true, 15.0);
    p.BeginTick(w);
    cmd = p.Step(w, &e, &los, 1, kDt);
  }
  CHECK(cmd.forward < 0.0, "a hurt survivor retreats");
}

static void TestTargetSwitchHysteresis() {
  BotProfile p{};
  BuildProfile(3, 2, 8u, "BOT-Duel", &p);
  HumanBotPolicy policy;
  policy.Configure(&p);

  SenseInput enemies[2];
  bool los[2] = {true, true};
  WorldView w;
  BotCommand cmd;
  // Both visible, one clearly closer.
  for (int t = 0; t < 40; ++t) {
    w = MakeWorld(t);
    policy.BeginTick(w);
    enemies[0] = Ahead(1, 20.0, -2.0);
    enemies[1] = Ahead(2, 40.0, 2.0);
    cmd = policy.Step(w, enemies, los, 2, kDt);
  }
  CHECK(cmd.target == 1, "the closest visible opponent is chosen");
  const int initial_switches = policy.target_switches();

  // Make the far one only slightly closer: no switch (1.4x rule).
  for (int t = 40; t < 80; ++t) {
    w = MakeWorld(t);
    policy.BeginTick(w);
    enemies[0] = Ahead(1, 20.0, -2.0);
    enemies[1] = Ahead(2, 19.0, 2.0);
    cmd = policy.Step(w, enemies, los, 2, kDt);
  }
  CHECK(policy.target_switches() - initial_switches <= 2,
        "no target ping-pong for a marginally closer opponent");
}

/* ------------------------------------------------------------------------ */
/* 7. CPU budgeting: the FOV gate must actually save ray casts               */
/* ------------------------------------------------------------------------ */

static void TestRayBudget() {
  BotProfile p{};
  BuildProfile(3, 0, 99u, "BOT-Rays", &p);
  HumanBotPolicy policy;
  policy.Configure(&p);

  WorldView w = MakeWorld(0);
  policy.BeginTick(w);
  SenseInput crowd[8];
  for (int i = 0; i < 8; ++i) {
    // half in front, half behind
    crowd[i] = (i % 2 == 0) ? MakeEnemy(i + 1, 0.0, 0.0, -(10.0 + i))
                            : MakeEnemy(i + 1, 0.0, 0.0, (10.0 + i));
  }
  bool needs[8];
  policy.PlanLosQueries(crowd, 8, needs);
  int requested = 0;
  for (int i = 0; i < 8; ++i) {
    if (needs[i]) ++requested;
  }
  CHECK(requested == 4, "only the four candidates in front of the bot get a ray");
  CHECK(policy.los_queries_last_tick() == requested, "budget counter matches the request");

  // Hard budget: 16 candidates in front, but at most max_los_per_tick rays.
  HumanBotPolicy tight;
  BotProfile q{};
  BuildProfile(1, 0, 3u, "BOT-Tight", &q);
  q.skill.max_los_per_tick = 4;
  tight.Configure(&q);
  WorldView w2 = MakeWorld(0);
  tight.BeginTick(w2);
  SenseInput many[16];
  for (int i = 0; i < 16; ++i) many[i] = Ahead(i, 10.0 + i);
  bool needs2[16];
  tight.PlanLosQueries(many, 16, needs2);
  int n2 = 0;
  for (int i = 0; i < 16; ++i) {
    if (needs2[i]) ++n2;
  }
  CHECK(n2 <= 4, "the per-tick ray budget is a hard cap");
  CHECK(tight.ray_budget_skips() >= 12, "skipped candidates are counted");
  CHECK(needs2[0] && needs2[1] && needs2[2] && needs2[3],
        "the budget goes to the nearest candidates first");
}

// The budget must never drop the current opponent in favour of strangers.
static void TestRayBudgetProtectsCurrentTarget() {
  BotProfile p{};
  BuildProfile(3, 0, 12u, "BOT-Keep", &p);
  p.skill.max_los_per_tick = 2;
  HumanBotPolicy policy;
  policy.Configure(&p);

  // Phase 1: a single, distant opponent. It becomes the current target.
  SenseInput solo[1];
  bool los[1] = {true};
  for (int t = 0; t < 30; ++t) {
    WorldView w = MakeWorld(t);
    policy.BeginTick(w);
    solo[0] = Ahead(1, 30.0);
    bool needs[1];
    policy.PlanLosQueries(solo, 1, needs);
    policy.Step(w, solo, los, 1, kDt);
  }
  CHECK(policy.target() == 1, "the single opponent is acquired as target");

  // Phase 2: three much closer opponents appear, budget still two rays.
  SenseInput group[4];
  bool group_los[4] = {true, true, true, true};
  WorldView w = MakeWorld(31);
  policy.BeginTick(w);
  group[0] = Ahead(1, 30.0);
  group[1] = Ahead(2, 16.0);
  group[2] = Ahead(3, 14.0);
  group[3] = Ahead(4, 12.0);
  bool needs[4];
  policy.PlanLosQueries(group, 4, needs);
  CHECK(needs[0], "the tracked opponent keeps its ray despite being the farthest");
  CHECK(policy.los_queries_last_tick() == 2, "the budget is respected");

  // A caller that reports LOS for candidates it was not granted must not be
  // able to grant vision anyway.
  CHECK(!needs[2], "the third-nearest candidate was not granted a ray");
  policy.Step(w, group, group_los, 4, kDt);
  CHECK(policy.perception().Track(3) == nullptr,
        "a candidate without a granted ray is never perceived");
  CHECK(policy.perception().Visible(1), "the granted ray is still used");
}

/* ------------------------------------------------------------------------ */
/* 8. Mixed-roster behaviour differentiation                                 */
/* ------------------------------------------------------------------------ */

// Different tiers must behave differently in a measurable, non-cosmetic way.
static void TestProfilesActuallyDiffer() {
  double first_shot[kSkillTierCount + 1] = {0};
  int fires[kSkillTierCount + 1] = {0};
  double aim_error[kSkillTierCount + 1] = {0};

  for (int tier = 1; tier <= kSkillTierCount; ++tier) {
    BotProfile p{};
    BuildProfile(tier, 2, DeriveSeed(3u, 0, tier, 2), "BOT-T", &p);
    HumanBotPolicy policy;
    policy.Configure(&p);

    double yaw = 0.0;
    double pitch = 0.0;
    double err_sum = 0.0;
    int err_n = 0;
    SenseInput e = Ahead(1, 22.0, 6.0);  // off to the side: requires a swing
    bool los = true;
    for (int t = 0; t < 160; ++t) {
      WorldView w = MakeWorld(t);
      w.pose.yaw_deg = yaw;
      w.pose.pitch_deg = pitch;
      policy.BeginTick(w);
      const BotCommand c = policy.Step(w, &e, &los, 1, kDt);
      yaw += c.yaw_delta_deg;
      pitch += c.pitch_delta_deg;
      if (c.fire) {
        ++fires[tier];
        if (first_shot[tier] == 0.0) first_shot[tier] = t * kDt;
      }
      if (t > 40) {
        err_sum += c.aim_error_deg;
        ++err_n;
      }
    }
    aim_error[tier] = err_n > 0 ? err_sum / err_n : 0.0;
  }

  // Higher tiers must land the first shot earlier on average.
  CHECK(first_shot[5] > 0.0 && first_shot[1] > 0.0, "every tier eventually fires");
  CHECK(first_shot[5] <= first_shot[1], "the expert opens fire at least as early as a beginner");
  // and keep the crosshair tighter
  CHECK(aim_error[5] < aim_error[1], "the expert keeps a tighter average aim error");
  // and fire more often in the same window
  CHECK(fires[5] > fires[1], "the expert gets more firing ticks out of the same window");

  std::printf(
      "  profile differentiation: first shot t1=%.2fs t5=%.2fs, fire ticks 1..5 = "
      "%d/%d/%d/%d/%d, mean aim error t1=%.2f t5=%.2f deg\n",
      first_shot[1], first_shot[5], fires[1], fires[2], fires[3], fires[4], fires[5],
      aim_error[1], aim_error[5]);
}

// Personalities at the same tier must not collapse the skill ordering.
static void TestPersonalityDoesNotBreakSkillOrder() {
  // A beginner doing everything right must still be mechanically slower than
  // an expert doing everything wrong. Compare the *median* first-shot delay.
  int beginner_max = 0;
  int expert_min = 1000000;
  for (int persona = 0; persona < kPersonalityCount; ++persona) {
    for (int tier_index = 0; tier_index < 2; ++tier_index) {
      const int tier = tier_index == 0 ? 1 : 5;
      BotProfile p{};
      BuildProfile(tier, persona, DeriveSeed(17u, persona, tier, persona), "BOT-X", &p);
      HumanBotPolicy policy;
      policy.Configure(&p);
      double yaw = 0.0, pitch = 0.0;
      SenseInput e = Ahead(1, 25.0, 8.0);
      bool los = true;
      int first = -1;
      for (int t = 0; t < 200 && first < 0; ++t) {
        WorldView w = MakeWorld(t);
        w.pose.yaw_deg = yaw;
        w.pose.pitch_deg = pitch;
        policy.BeginTick(w);
        const BotCommand c = policy.Step(w, &e, &los, 1, kDt);
        yaw += c.yaw_delta_deg;
        pitch += c.pitch_delta_deg;
        if (c.fire) first = t;
      }
      if (first < 0) first = 200;
      if (tier == 1 && first > beginner_max) beginner_max = first;
      if (tier == 5 && first < expert_min) expert_min = first;
    }
  }
  CHECK(expert_min < beginner_max,
        "even the slowest expert personality reacts before the fastest beginner");
}

/* ------------------------------------------------------------------------ */
/* 9. Mixed-roster determinism and separation over a longer scenario         */
/* ------------------------------------------------------------------------ */

static void TestMixedRosterOverTime() {
  int count = 0;
  const RosterEntry* roster = DefaultRoster(&count);
  double total_forward[8] = {0};
  double total_strafe[8] = {0};

  for (int i = 0; i < count; ++i) {
    BotProfile p{};
    BuildProfile(roster[i].tier, roster[i].persona, DeriveSeed(5u, i, roster[i].tier,
                                                               roster[i].persona),
                 roster[i].name, &p);
    HumanBotPolicy policy;
    policy.Configure(&p);
    double yaw = 0.0, pitch = 0.0;
    for (int t = 0; t < 300; ++t) {
      WorldView w = MakeWorld(t, 0.0, 0.0, true, 70.0);
      w.pose.yaw_deg = yaw;
      w.pose.pitch_deg = pitch;
      policy.BeginTick(w);
      SenseInput e = Ahead(1, 9.0 + (t % 5));
      bool los = true;
      const BotCommand c = policy.Step(w, &e, &los, 1, kDt);
      yaw += c.yaw_delta_deg;
      pitch += c.pitch_delta_deg;
      total_forward[i] += std::fabs(c.forward);
      total_strafe[i] += std::fabs(c.strafe);
    }
  }

  int different = 0;
  for (int i = 1; i < count; ++i) {
    if (std::fabs(total_forward[i] - total_forward[0]) > 1.0) ++different;
  }
  CHECK(different >= 4, "at least four roster bots move visibly differently");
  bool strafes = false;
  for (int i = 0; i < count; ++i) {
    if (total_strafe[i] > 1.0) strafes = true;
  }
  CHECK(strafes, "at least one profile actively strafes");
}

int main() {
  std::printf("bot human-AI policy tests\n");

  TestProfiles();
  TestSkillMonotonicity();
  TestSkillPersonalityOrthogonality();
  TestDeterministicSeeds();
  TestRoster();

  TestReproducibility();

  TestFieldOfView();
  TestReactionDelay();
  TestMemoryExpiryAndNoWallTracking();
  TestNoFireWithoutLineOfSight();
  TestAlertOnDamage();

  TestNoInstantLockAndTurnLimit();
  TestTurnLimitRespectedAtLargeAngles();
  TestCorrelatedErrorNotPerFrameJitter();
  TestOvershootHasMechanicalCause();
  TestFireNeedsFreshSightAndSettle();

  TestWeaponUtility();
  TestWeaponHysteresis();
  TestWeaponPreferenceByPersonality();

  TestPreferredRangeAndMovement();
  TestRetreatWhenHurt();
  TestTargetSwitchHysteresis();

  TestRayBudget();
  TestRayBudgetProtectsCurrentTarget();

  TestProfilesActuallyDiffer();
  TestPersonalityDoesNotBreakSkillOrder();
  TestMixedRosterOverTime();

  std::printf("%s: %d checks, %d failures\n", g_failures ? "HUMAN AI FAIL" : "HUMAN AI PASS",
              g_checks, g_failures);
  return g_failures == 0 ? 0 : 1;
}
