// qa_sim.cpp - offline synthetic-combat simulator for the botcore Human-KI.
//
// STATUS: OFFLINE SIMULATION ONLY - NOT RETAIL TELEMETRY.
//  Drives the engine-free botcore decision chain (bot_human.h and friends,
//  included READ-ONLY) inside the synthetic world of qa_world.h and emits
//  NDJSON metric records. Every produced number is a property of
//  (botcore code x documented simulation assumptions), reproducible from
//  (scenario, tier, persona, seed, config). Nothing here measures the real
//  game, a real server, or a real human; see qa_world.h ASSUMPTIONS A1..A8.
//
//  The integration semantics mirrored from
//  poc/ai-integration/gamemp/BotDriver.cpp (read-only reference):
//   - fire only when the policy allows it AND the weapon switch is
//     acknowledged (current == wanted == desired);
//   - strafe suppressed unless --strafe-scale > 0 (bot_fStrafeScale default);
//   - policy clock kept alive while dead; memory cleared on death;
//   - perceived enemy state delayed by --latency ticks (assumption A7).
//
//  Build: see Makefile. Run: ./qa_sim --list | --selftest | --scenario ... |
//  --sweep ... | --duel ... | --perf.

#include <algorithm>
#include <chrono>
#include <cinttypes>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <limits>
#include <memory>
#include <string>
#include <vector>

#include "qa_world.h"

using namespace behaviorqa;
using botcore::EffectiveAggression;
using botcore::PersonalityName;
using botcore::SkillName;

/* ------------------------------------------------------------------------ */
/* Opponents                                                                 */
/* ------------------------------------------------------------------------ */

enum class DummyType {
  kStatic,    // stands still
  kZigzag,    // constant lateral speed, flips direction periodically
  kOrbit,     // circles an anchor at constant tangential speed
  kApproach,  // walks toward the bot, then holds at stop distance
  kRetreat,   // walks away from the bot
  kRangeOsc,  // distance oscillates slowly (weapon-boundary probe)
};

struct Dummy {
  DummyType type = DummyType::kStatic;
  int index = 1;          // replicated player index seen by the policy
  double x = 0.0, z = 0.0;
  double vx = 0.0, vz = 0.0;
  double hp = 100.0;
  bool alive = true;
  // script parameters
  double anchor_x = 0.0, anchor_z = 0.0;
  double speed = 0.0;        // approach/retreat/zigzag speed m/s
  double amplitude = 4.0;    // zigzag half-width / range-osc amplitude (m)
  double omega = 1.2;        // zigzag/range-osc angular rate (rad/s)
  double radius = 14.0;      // orbit radius
  double stop_distance = 6.0;
  double return_dps = 0.0;   // scripted damage back to the bot (hp/s at ref dist)
  double return_ref_dist = 0.0;  // distance at which return_dps is nominal (0=unset)
  double dir_sign = 1.0;
  HistoryRing hist;

  void PushHistory() {
    HistoryEntry e{x, kEyeHeight, z, vx, 0.0, vz, hp, alive};
    hist.Push(e);
  }
};

struct Projectile {
  bool active = false;
  int weapon = 1;
  int target_index = -1;
  int impact_tick = 0;
  double ex = 0.0, ey = 0.0, ez = 0.0;  // endpoint along the true view ray
  double fire_err_deg = 0.0;           // policy aim error at fire time
  double fire_dist = 0.0;
  double shooter_x = 0.0, shooter_z = 0.0;
};

/* ------------------------------------------------------------------------ */
/* Scenario definition                                                       */
/* ------------------------------------------------------------------------ */

struct ScenarioDef {
  const char* name;
  const char* description;
  int max_ticks;
  bool lock_movement;
  double bot_start_hp;
  double bot_yaw_deg;      // absolute; NaN => face the primary dummy
  int cover_open_from;     // ticks where the LOS gate is CLOSED: [from, to)
  int cover_open_to;       // (cover_reacquire uses cover_gap_ticks too)
  bool use_gate;
  std::vector<Rect2D> cover;
  std::vector<Dummy> dummies;
  double alert_damage_from_tick;  // scripted damage window on the bot
  double alert_damage_to_tick;
  double alert_damage_dps;
  uint32_t loadout_mask;
  bool duel;               // two HumanBotPolicy instances instead of dummies
};

static double kNaN = std::numeric_limits<double>::quiet_NaN();

static Dummy MakeDummy(int index, DummyType type, double x, double z) {
  Dummy d;
  d.type = type;
  d.index = index;
  d.x = x;
  d.z = z;
  d.anchor_x = x;
  d.anchor_z = z;
  return d;
}

// Primary dummy sits at -z (yaw 0 faces it), matching bot_aim.h convention.
static std::vector<ScenarioDef> BuildScenarios() {
  std::vector<ScenarioDef> v;

  auto base = [&](const char* name, const char* desc, int ticks) {
    ScenarioDef s;
    s.name = name;
    s.description = desc;
    s.max_ticks = ticks;
    s.lock_movement = false;
    s.bot_start_hp = 100.0;
    s.bot_yaw_deg = kNaN;  // face primary dummy
    s.cover_open_from = 0;
    s.cover_open_to = 0;
    s.use_gate = false;
    s.alert_damage_from_tick = -1;
    s.alert_damage_to_tick = -1;
    s.alert_damage_dps = 0.0;
    s.loadout_mask = 0x3FFFu;
    s.duel = false;
    return s;
  };

  {  // pure aiming gallery: body frozen, static target, full loadout
    ScenarioDef s = base("gallery_static",
                         "locked movement, static target 15 m: pure aim/hit curve", 500);
    s.lock_movement = true;
    s.dummies.push_back(MakeDummy(1, DummyType::kStatic, 0.0, -15.0));
    v.push_back(s);
  }
  {  // acquisition + kill on a standing target
    ScenarioDef s = base("reaction_static",
                         "facing a static target 15 m: reaction, TTK, weapon choice", 600);
    s.dummies.push_back(MakeDummy(1, DummyType::kStatic, 0.0, -15.0));
    v.push_back(s);
  }
  {  // target outside the FOV cone: scan-to-acquire speed
    ScenarioDef s = base("reaction_turn90",
                         "static target 15 m at 90 deg off-view: search rate to acquire", 800);
    s.bot_yaw_deg = 90.0;
    s.dummies.push_back(MakeDummy(1, DummyType::kStatic, 0.0, -15.0));
    v.push_back(s);
  }
  {  // damage from behind: alert window behaviour. The attacker sits behind the
    // bot (outside the FOV cone) and lands scripted hits; the bot's only cue is
    // its own health dropping (NotifyDamage), which opens the alert window.
    ScenarioDef s = base("damage_alert_behind",
                         "attacker 12 m behind, return fire 15 hp/s: alert-driven turn", 600);
    s.bot_yaw_deg = 180.0;  // faces +z, away from the attacker at -z (behind)
    s.alert_damage_from_tick = -1;  // disabled; the dummy's return fire is the cue
    Dummy d = MakeDummy(1, DummyType::kStatic, 0.0, -12.0);  // 12 m behind (yaw 0 to face it)
    d.return_dps = 15.0;
    s.dummies.push_back(d);
    v.push_back(s);
  }
  {  // lateral tracking
    ScenarioDef s = base("tracking_strafe",
                         "zigzag target 4.5 m/s at 12 m: tracking error, hit rate", 500);
    Dummy d = MakeDummy(1, DummyType::kZigzag, 0.0, -12.0);
    d.speed = 4.5;
    d.amplitude = 5.0;
    d.omega = 0.9;
    s.dummies.push_back(d);
    v.push_back(s);
  }
  {  // constant angular-rate tracking
    ScenarioDef s = base("tracking_orbit",
                         "orbiting target (r=14 m, 4 m/s tangential): sustained tracking", 500);
    Dummy d = MakeDummy(1, DummyType::kOrbit, 0.0, -14.0);
    d.radius = 14.0;
    d.speed = 4.0;
    s.dummies.push_back(d);
    v.push_back(s);
  }
  {  // engagement build-up over distance
    ScenarioDef s = base("approach_close",
                         "target approaches from 35 m at 5 m/s, stops at 6 m", 700);
    Dummy d = MakeDummy(1, DummyType::kApproach, 0.0, -35.0);
    d.speed = 5.0;
    d.stop_distance = 6.0;
    s.dummies.push_back(d);
    v.push_back(s);
  }
  {  // retreat decision under pressure at low health
    ScenarioDef s = base("retreat_pressure",
                         "bot at 40 HP, static target 14 m returning 15 hp/s", 600);
    s.bot_start_hp = 40.0;
    Dummy d = MakeDummy(1, DummyType::kStatic, 0.0, -14.0);
    d.return_dps = 15.0;
    s.dummies.push_back(d);
    v.push_back(s);
  }
  {  // sustained firefight: a slowly strafing target that shoots back. Used for
    // the lateral-movement A/B, where evasion benefit (survival) and accuracy
    // cost (self-motion) must both be visible.
    ScenarioDef s = base("firefight",
                         "slow-strafe target 15 m returning 12 hp/s: sustained trade", 800);
    Dummy d = MakeDummy(1, DummyType::kZigzag, 0.0, -15.0);
    d.speed = 2.5; d.amplitude = 3.0; d.omega = 0.5; d.return_dps = 12.0;
    s.dummies.push_back(d);
    v.push_back(s);
  }
  {  // LOS loss + memory + reacquisition
    ScenarioDef s = base("cover_reacquire",
                         "target visible 2 s, LOS gate closed for cover_gap ticks, then open", 800);
    s.use_gate = true;
    s.cover_open_from = 40;
    s.cover_open_to = 40 + 30;  // replaced by cover_gap_ticks at run time
    s.dummies.push_back(MakeDummy(1, DummyType::kStatic, 0.0, -15.0));
    v.push_back(s);
  }
  {  // weapon-score boundary probe: sweep 6..34 m so the band straddles the
    // close (shotgun) <-> far (sniper/minigun) weapon-score boundary and the
    // dwell/margin hysteresis is genuinely exercised against churn.
    ScenarioDef s = base("weapon_boundary",
                         "locked body, distance oscillates 6..34 m across weapon bands", 900);
    s.lock_movement = true;  // freeze the body so the range really sweeps the
                             // bands; otherwise MoveIntent stabilises distance
                             // and the weapon logic is never exercised.
    Dummy d = MakeDummy(1, DummyType::kRangeOsc, 0.0, -20.0);
    d.amplitude = 14.0;
    d.omega = 0.4;
    s.dummies.push_back(d);
    v.push_back(s);
  }
  {  // two opponents
    ScenarioDef s = base("multi_2v1",
                         "two zigzag targets at 10 m and 18 m: prioritisation", 600);
    Dummy a = MakeDummy(1, DummyType::kZigzag, -3.0, -10.0);
    a.speed = 4.0; a.amplitude = 4.0; a.omega = 0.8;
    Dummy b = MakeDummy(2, DummyType::kZigzag, 4.0, -18.0);
    b.speed = 4.0; b.amplitude = 4.0; b.omega = 0.8; b.dir_sign = -1.0;
    s.dummies.push_back(a);
    s.dummies.push_back(b);
    v.push_back(s);
  }
  {  // three opponents, mixed scripts
    ScenarioDef s = base("multi_3v1",
                         "three targets (8/14/20 m, mixed movement): focus under pressure", 700);
    Dummy a = MakeDummy(1, DummyType::kZigzag, -4.0, -8.0);
    a.speed = 4.0; a.amplitude = 3.0; a.omega = 1.0;
    Dummy b = MakeDummy(2, DummyType::kStatic, 3.0, -14.0);
    Dummy c = MakeDummy(3, DummyType::kOrbit, 0.0, -20.0);
    c.radius = 20.0; c.speed = 3.5;
    s.dummies.push_back(a);
    s.dummies.push_back(b);
    s.dummies.push_back(c);
    v.push_back(s);
  }
  {  // projectile lead competence (prediction_gain)
    ScenarioDef s = base("long_range_lead",
                         "rocket/cannon only, zigzag target at 25 m: lead quality", 700);
    s.loadout_mask = (1u << 7) | (1u << 13);  // rocket + cannon
    Dummy d = MakeDummy(1, DummyType::kZigzag, 0.0, -25.0);
    d.speed = 4.5; d.amplitude = 6.0; d.omega = 0.7;
    s.dummies.push_back(d);
    v.push_back(s);
  }
  {  // hitscan under replication latency (no lead model exists for hitscan)
    ScenarioDef s = base("hitscan_latency",
                         "tommygun only, zigzag target 12 m: latency-driven misses", 500);
    s.loadout_mask = (1u << 5);  // tommygun
    Dummy d = MakeDummy(1, DummyType::kZigzag, 0.0, -12.0);
    d.speed = 4.5; d.amplitude = 5.0; d.omega = 0.9;
    s.dummies.push_back(d);
    v.push_back(s);
  }
  {  // no opponents: search behaviour sanity
    ScenarioDef s = base("idle_scan",
                         "no opponents: scan-rate compliance, no fire, no movement", 300);
    v.push_back(s);
  }
  {  // full policy duel (both sides are HumanBotPolicy)
    ScenarioDef s = base("duel",
                         "two policy instances fight; sides via --duel-a/--duel-b", 900);
    s.duel = true;
    v.push_back(s);
  }
  return v;
}

/* ------------------------------------------------------------------------ */
/* Metrics                                                                   */
/* ------------------------------------------------------------------------ */

struct RunMetrics {
  // outcome
  int ticks_run = 0;
  const char* outcome = "timeout";  // kill | death | timeout
  double hp_end = 100.0;
  double dmg_dealt = 0.0;
  double dmg_taken = 0.0;
  double dmg_self_inflicted = 0.0;

  // reaction / engagement timing (s; -1 = never happened)
  double t_first_selectable = -1.0;
  double t_first_fire_policy = -1.0;
  double t_first_fire_eff = -1.0;
  double t_first_hit = -1.0;
  double t_kill = -1.0;
  double ttk_s = -1.0;

  // fire gating
  int shots_policy = 0;         // ticks with policy fire bit set
  int shots_blocked_switch = 0; // policy fire suppressed by weapon ack gate
  int shots_eff = 0;            // effective trigger ticks (integration gate)
  int trigger_pulls = 0;        // shots actually resolved (interval-limited)
  int shots_gated_aim = 0;      // aim().gated_ticks delta (visible but not settled)
  int hits = 0;
  int wasted_fire_invisible = 0; // must stay 0 (policy contract)

  // aiming
  Series aim_err_policy_at_fire;   // cmd.aim_error_deg on policy-fire ticks
  Series true_err_at_fire;         // geometric error vs TRUE target at fire
  Series true_err_visible;         // geometric error on all visible ticks
  int overshoots = 0;

  // miss attribution (heuristic, resolved trigger pulls that missed)
  int miss_range = 0;
  int miss_target_motion = 0;
  int miss_overshoot = 0;
  int miss_aim_bias = 0;

  // projectile lead
  Series lead_impact_miss_m;  // 3D miss distance at scheduled impact

  // weapons / targets
  int weapon_switches = 0;
  int weapon_switch_wasted_ticks = 0; // engagement ticks lost to switching
  int weapon_mode = 0;                // modal weapon held on engaged ticks
  int weapon_distinct = 0;            // distinct weapons held on engaged ticks
  int target_switches = 0;            // policy counter delta
  double focus_share = 0.0;           // share of resolved shots on one target
  int los_queries_max = 0;
  int ray_budget_skips = 0;
  double nearest_not_chosen_pct = 0.0; // multi-target: time a closer enemy existed

  // distance / positioning
  Series distance_engaged;
  double dist_mean = 0.0, dist_min = 0.0, dist_max = 0.0;
  double in_band_pct = 0.0;   // |d - preferred| <= 3 m on engaged ticks
  double preferred_mean = 0.0;
  double corner_pct = 0.0;    // share of ticks clamped at the arena border

  // movement
  double move_fwd_mean = 0.0;
  double strafe_cmd_uptime = 0.0;   // |strafe cmd| > 0.05 on engaged ticks
  double strafe_applied_uptime = 0.0; // actually moved laterally (strafe_scale)
  double still_pct = 0.0;
  double path_len = 0.0;
  double net_disp = 0.0;
  double approach_uptime = 0.0;     // forward > 0.1 on engaged ticks
  double retreat_uptime = 0.0;      // forward < -0.1 on engaged ticks

  // retreat decisions
  int retreat_events = 0;
  double hp_at_first_retreat = -1.0;
  double survival_s = -1.0;

  // performance (perf mode / optional)
  double policy_ns_per_tick = 0.0;

  // duel extras
  int duel_winner = 0;  // 1 = side A, 2 = side B, 0 = draw
  double duel_duration_s = 0.0;
  double duel_dmg_a = 0.0, duel_dmg_b = 0.0;  // damage dealt BY side A / B
  double duel_hp_a = 100.0, duel_hp_b = 100.0;
  int duel_switches_a = 0, duel_switches_b = 0;

  uint64_t digest = 0;
};

/* ------------------------------------------------------------------------ */
/* Fighter: one simulated body driven by HumanBotPolicy                      */
/* ------------------------------------------------------------------------ */

struct Fighter {
  HumanBotPolicy policy;
  BotProfile profile{};
  double x = 0.0, z = 0.0, yaw = 0.0, pitch = 0.0;
  double hp = 100.0;
  bool alive = true;
  int cur_weapon = 2;
  int want_weapon = 2;
  int switch_timer = 0;
  int fire_cooldown = 0;
  double last_hp = 100.0;
  HistoryRing hist;
  bool engaged_last = false;

  void PushHistory() {
    // velocity from the last two samples
    double vx = 0.0, vz = 0.0;
    HistoryEntry prev = hist.Delayed(0);
    if (hist.count() > 0) {
      vx = (x - prev.x) / kDt;
      vz = (z - prev.z) / kDt;
    }
    HistoryEntry e{x, kEyeHeight, z, vx, 0.0, vz, hp, alive};
    hist.Push(e);
  }
};

/* ------------------------------------------------------------------------ */
/* Scenario runner (bot vs scripted dummies)                                 */
/* ------------------------------------------------------------------------ */

struct RunOptions {
  SimConfig cfg;
  int tier = 3;
  int persona = 2;
  uint32_t seed = 0x20261025u;
  int latency_ticks = -1;  // <0: use cfg.latency_ticks
};

static void DummyStep(Dummy& d, int tick, double bot_x, double bot_z) {
  const double t = tick * kDt;
  const double px = d.x, pz = d.z;
  switch (d.type) {
    case DummyType::kStatic:
      break;
    case DummyType::kZigzag: {
      // lateral axis perpendicular to the anchor->origin direction
      double ax = d.anchor_x - 0.0, az = d.anchor_z - 0.0;
      double len = std::sqrt(ax * ax + az * az);
      if (len < 1e-9) { ax = 1.0; az = 0.0; } else { ax /= len; az /= len; }
      // perpendicular of (ax, az)
      const double lx = -az, lz = ax;
      const double phase = d.dir_sign * std::sin(d.omega * t);
      d.x = d.anchor_x + lx * d.amplitude * phase;
      d.z = d.anchor_z + lz * d.amplitude * phase;
      break;
    }
    case DummyType::kOrbit: {
      const double w = d.speed / d.radius;
      const double ang = w * t + (d.dir_sign > 0 ? 0.0 : 3.0);
      d.x = d.anchor_x * 0.0 + std::sin(ang) * d.radius;  // orbit around origin
      d.z = -std::cos(ang) * d.radius;
      break;
    }
    case DummyType::kApproach: {
      double dx = bot_x - d.x, dz = bot_z - d.z;
      const double len = std::sqrt(dx * dx + dz * dz);
      if (len > d.stop_distance && len > 1e-6) {
        dx /= len; dz /= len;
        const double step = std::min(d.speed * kDt, len - d.stop_distance);
        d.x += dx * step;
        d.z += dz * step;
      }
      break;
    }
    case DummyType::kRetreat: {
      double dx = d.x - bot_x, dz = d.z - bot_z;
      const double len = std::sqrt(dx * dx + dz * dz);
      if (len > 1e-6 && len < 45.0) {
        dx /= len; dz /= len;
        d.x += dx * d.speed * kDt;
        d.z += dz * d.speed * kDt;
      }
      break;
    }
    case DummyType::kRangeOsc: {
      // centre on the anchor distance, oscillate by +/- amplitude so the band
      // can be chosen to straddle a real weapon-score boundary.
      const double centre = std::fabs(d.anchor_z);
      const double dist = centre + d.amplitude * std::sin(d.omega * t);
      d.x = 0.0;
      d.z = -(dist > 2.0 ? dist : 2.0);
      break;
    }
  }
  d.vx = (d.x - px) / kDt;
  d.vz = (d.z - pz) / kDt;
}

static RunMetrics RunScenario(const ScenarioDef& def, const RunOptions& opt,
                              FILE* trace) {
  RunMetrics m;
  SimConfig cfg = opt.cfg;
  if (opt.latency_ticks >= 0) cfg.latency_ticks = opt.latency_ticks;
  if (def.lock_movement) cfg.lock_movement = true;
  cfg.loadout_mask = def.loadout_mask;
  const int max_ticks = def.max_ticks;

  ScenarioDef scen = def;  // local copy: cover gap tick window is config-driven
  if (scen.use_gate) {
    scen.cover_open_to = scen.cover_open_from + cfg.cover_gap_ticks;
  }

  Fighter bot;
  if (!BuildProfile(opt.tier, opt.persona,
                    DeriveSeed(opt.seed, 0, opt.tier, opt.persona), "QA-Bot",
                    &bot.profile)) {
    std::fprintf(stderr, "qa_sim: profile build failed\n");
    std::exit(2);
  }
  bot.policy.Configure(&bot.profile);
  bot.x = 0.0;
  bot.z = 0.0;
  bot.hp = scen.bot_start_hp;
  bot.last_hp = bot.hp;
  // initial facing
  if (!scen.dummies.empty()) {
    const Dummy& p = scen.dummies[0];
    const double dx = p.x - bot.x, dz = p.z - bot.z;
    bot.yaw = std::atan2(-dx, -dz) * botcore::kRadToDeg;
  }
  if (!std::isnan(scen.bot_yaw_deg)) bot.yaw = scen.bot_yaw_deg;

  for (Dummy& d : scen.dummies) d.hist.Clear();
  // prime histories so latency lookups have data from tick 0
  for (int i = 0; i < 4; ++i) {
    for (Dummy& d : scen.dummies) d.PushHistory();
    bot.PushHistory();
  }

  std::vector<Projectile> projectiles;
  int engaged_ticks = 0;
  int nearest_mismatch_ticks = 0;
  int corner_ticks = 0;
  int shots_per_dummy[16] = {0};
  int weapon_hist[15] = {0};
  int visible_ticks = 0;
  int overshoot_prev = 0;
  int switches_prev = bot.policy.target_switches();
  bool retreat_active = false;
  int first_engaged_tick = -1;
  const double start_x = bot.x, start_z = bot.z;

  for (int tick = 0; tick < max_ticks; ++tick) {
    // --- dummies move + scripted return fire -----------------------------
    for (Dummy& d : scen.dummies) {
      if (!d.alive) continue;
      DummyStep(d, tick, bot.x, bot.z);
      if (std::fabs(d.x) > cfg.arena_half) d.x = std::copysign(cfg.arena_half, d.x);
      if (std::fabs(d.z) > cfg.arena_half) d.z = std::copysign(cfg.arena_half, d.z);
    }

    // LOS gate / geometry, evaluated on TRUE positions (caller-side rays)
    auto los_open = [&](const Dummy& d) {
      if (scen.use_gate && tick >= scen.cover_open_from && tick < scen.cover_open_to)
        return false;
      return !LosBlocked(bot.x, bot.z, d.x, d.z, scen.cover);
    };

    // Scripted return damage (before the policy sees the world, like the
    // integration which calls NotifyDamage before BeginTick). A9: incoming dps
    // falls off with distance so that a retreat which opens range actually
    // reduces the damage taken - otherwise the retreat decision is untestable.
    // factor = clamp(ref/dist, 0.25, 1.0); ref = distance at first tick.
    for (Dummy& d : scen.dummies) {
      if (d.alive && d.return_dps > 0.0 && los_open(d) && bot.alive) {
        const double dx = d.x - bot.x, dz = d.z - bot.z;
        const double dist = std::sqrt(dx * dx + dz * dz);
        if (d.return_ref_dist <= 0.0) d.return_ref_dist = dist;
        double factor = d.return_ref_dist / std::max(dist, 1.0);
        factor = factor < 0.25 ? 0.25 : (factor > 1.0 ? 1.0 : factor);
        const double dealt = d.return_dps * factor * kDt;
        bot.hp -= dealt;
        m.dmg_taken += dealt;
      }
    }
    if (scen.alert_damage_from_tick >= 0 && tick >= scen.alert_damage_from_tick &&
        tick < scen.alert_damage_to_tick && bot.alive) {
      const double dealt = scen.alert_damage_dps * kDt;
      bot.hp -= dealt;
      m.dmg_taken += dealt;
    }
    if (bot.hp <= 0.0) {
      bot.hp = 0.0;
      if (bot.alive) {
        bot.alive = false;
        m.survival_s = tick * kDt;
      }
    }

    // --- policy tick (integration semantics) ------------------------------
    WorldView world;
    world.tick = tick;
    world.pose.x = bot.x;
    world.pose.y = kEyeHeight;
    world.pose.z = bot.z;
    world.pose.yaw_deg = bot.yaw;
    world.pose.pitch_deg = bot.pitch;
    world.alive = bot.alive;
    world.health = bot.hp;
    world.max_health = 100.0;
    world.usable_weapons = cfg.loadout_mask;
    world.current_weapon = bot.cur_weapon;
    world.deathmatch = true;

    if (bot.last_hp > 0.0 && bot.hp < bot.last_hp) {
      bot.policy.NotifyDamage(bot.last_hp, bot.hp);
    }
    bot.last_hp = bot.hp;

    bot.policy.BeginTick(world);

    const int n = static_cast<int>(scen.dummies.size());
    SenseInput sensed[16];
    bool needs[16];
    bool los[16];
    Dummy* by_index[16] = {nullptr};
    for (int i = 0; i < n; ++i) {
      const Dummy& d = scen.dummies[i];
      by_index[d.index] = &scen.dummies[i];
      HistoryEntry he = d.hist.Delayed(cfg.latency_ticks);
      sensed[i].index = d.index;
      sensed[i].x = he.x;
      sensed[i].y = he.y;
      sensed[i].z = he.z;
      sensed[i].vx = he.vx;
      sensed[i].vy = he.vy;
      sensed[i].vz = he.vz;
      sensed[i].health = he.health;
      sensed[i].alive = he.alive;
      sensed[i].local = false;
      los[i] = false;
    }
    bot.policy.PlanLosQueries(sensed, n, needs);
    m.los_queries_max = std::max(m.los_queries_max, bot.policy.los_queries_last_tick());
    m.ray_budget_skips += bot.policy.ray_budget_skips();
    for (int i = 0; i < n; ++i) {
      los[i] = needs[i] && scen.dummies[i].alive && los_open(scen.dummies[i]);
    }

    const BotCommand cmd = bot.policy.Step(world, sensed, los, n, kDt);

    // --- weapon switch model (A6; mirrors the integration fire gate) ------
    if (cmd.weapon != bot.want_weapon) {
      bot.want_weapon = cmd.weapon;
      bot.switch_timer = cfg.switch_ticks;
      if (bot.alive && cmd.target >= 0) ++m.weapon_switches;
    }
    if (bot.cur_weapon != bot.want_weapon) {
      if (bot.switch_timer > 0) --bot.switch_timer;
      if (bot.switch_timer <= 0) bot.cur_weapon = bot.want_weapon;
      if (bot.alive && cmd.target >= 0) ++m.weapon_switch_wasted_ticks;
    }
    const bool weapon_ready = (bot.cur_weapon == bot.want_weapon);

    // --- movement integration ---------------------------------------------
    bot.yaw += cmd.yaw_delta_deg;
    bot.pitch += cmd.pitch_delta_deg;
    bot.pitch = std::max(-89.0, std::min(89.0, bot.pitch));
    if (bot.alive && !cfg.lock_movement) {
      double fx, fz, rx, rz;
      FacingVectors(bot.yaw, &fx, &fz, &rx, &rz);
      const double dxm = (fx * cmd.forward + rx * cmd.strafe * cfg.strafe_scale) *
                         cfg.move_speed * kDt;
      const double dzm = (fz * cmd.forward + rz * cmd.strafe * cfg.strafe_scale) *
                         cfg.move_speed * kDt;
      bot.x += dxm;
      bot.z += dzm;
      m.path_len += std::sqrt(dxm * dxm + dzm * dzm);
      if (std::fabs(bot.x) >= cfg.arena_half - 1e-9 ||
          std::fabs(bot.z) >= cfg.arena_half - 1e-9) {
        ++corner_ticks;
      }
      bot.x = std::max(-cfg.arena_half, std::min(cfg.arena_half, bot.x));
      bot.z = std::max(-cfg.arena_half, std::min(cfg.arena_half, bot.z));
    }

    // --- bookkeeping: engagement -------------------------------------------
    const bool engaged = bot.alive && cmd.target >= 0;
    Dummy* tgt = (cmd.target >= 0 && cmd.target < 16) ? by_index[cmd.target] : nullptr;
    if (engaged && tgt != nullptr) {
      if (first_engaged_tick < 0) first_engaged_tick = tick;
      ++engaged_ticks;
      if (cmd.weapon >= 1 && cmd.weapon <= 14) weapon_hist[cmd.weapon]++;
      const double dx = tgt->x - bot.x, dz = tgt->z - bot.z;
      const double dist = std::sqrt(dx * dx + dz * dz);
      m.distance_engaged.Add(dist);
      if (std::fabs(dist - cmd.preferred_range_m) <= 3.0) m.in_band_pct += 1.0;
      m.preferred_mean += cmd.preferred_range_m;
      if (cmd.target_visible) ++visible_ticks;
      // geometric TRUE error against the real (undelayed) target position
      const double terr = AngularErrorDeg(bot.x, kEyeHeight, bot.z, bot.yaw,
                                          bot.pitch, tgt->x, kEyeHeight, tgt->z);
      m.true_err_visible.Add(terr);
      // multi-target: was a closer live enemy not chosen?
      if (n > 1) {
        const double ddx = tgt->x - bot.x, ddz = tgt->z - bot.z;
        const double chosen_d = std::sqrt(ddx * ddx + ddz * ddz);
        for (const Dummy& o : scen.dummies) {
          if (!o.alive || o.index == cmd.target) continue;
          const double ox = o.x - bot.x, oz = o.z - bot.z;
          if (std::sqrt(ox * ox + oz * oz) < chosen_d * 0.75) {
            ++nearest_mismatch_ticks;
            break;
          }
        }
      }
      // retreat episode detection (health-driven, per the MoveIntent formula)
      const double retreat_below =
          bot.profile.skill.retreat_health *
          (0.6 + 0.9 * bot.profile.personality.caution);
      const bool want_retreat =
          cmd.forward < -0.5 && cmd.target_visible &&
          (world.max_health > 0.0 ? world.health / world.max_health : 1.0) <
              retreat_below;
      if (want_retreat && !retreat_active) {
        ++m.retreat_events;
        if (m.hp_at_first_retreat < 0.0) m.hp_at_first_retreat = bot.hp;
      }
      retreat_active = want_retreat;
    } else {
      retreat_active = false;
    }

    // --- fire resolution ----------------------------------------------------
    if (cmd.fire) ++m.shots_policy;
    if (cmd.fire && !weapon_ready) ++m.shots_blocked_switch;
    const bool fire_eff = cmd.fire && weapon_ready && bot.alive;
    if (fire_eff) ++m.shots_eff;
    if (fire_eff && tgt != nullptr && tgt->alive) {
      const WeaponProfile& wp = WeaponAt(bot.cur_weapon);
      if (bot.fire_cooldown <= 0) {
        bot.fire_cooldown = IntervalTicks(bot.cur_weapon);
        ++m.trigger_pulls;
        shots_per_dummy[tgt->index] += 1;
        const double dx = tgt->x - bot.x, dz = tgt->z - bot.z;
        const double dist = std::sqrt(dx * dx + dz * dz);
        const double terr = AngularErrorDeg(bot.x, kEyeHeight, bot.z, bot.yaw,
                                            bot.pitch, tgt->x, kEyeHeight, tgt->z);
        m.aim_err_policy_at_fire.Add(cmd.aim_error_deg);
        m.true_err_at_fire.Add(terr);
        const double miss_m = MissDistanceM(terr, dist);
        const double hit_r = HitRadius(wp, dist, cfg.target_radius);
        const double dmg = wp.dps_rel * cfg.dps_scale * WeaponIntervalS(bot.cur_weapon);

        if (wp.proj_speed > 0.0 && dist > wp.min_m) {
          // projectile: schedule impact along the TRUE view ray
          Projectile p;
          p.active = true;
          p.weapon = bot.cur_weapon;
          p.target_index = tgt->index;
          const int flight = std::max(1, static_cast<int>(std::llround(dist / wp.proj_speed / kDt)));
          p.impact_tick = tick + flight;
          double vx3, vy3, vz3;
          {
            const double yr = bot.yaw * botcore::kDegToRad;
            const double pr = bot.pitch * botcore::kDegToRad;
            vx3 = -std::sin(yr) * std::cos(pr);
            vz3 = -std::cos(yr) * std::cos(pr);
            vy3 = std::sin(pr);
          }
          p.ex = bot.x + vx3 * dist;
          p.ey = kEyeHeight + vy3 * dist;
          p.ez = bot.z + vz3 * dist;
          p.fire_err_deg = terr;
          p.fire_dist = dist;
          p.shooter_x = bot.x;
          p.shooter_z = bot.z;
          projectiles.push_back(p);
        } else {
          // hitscan / melee (A8 cutoff)
          const bool in_range = dist <= wp.max_m * 1.5 + 0.5;
          const bool hit = in_range && miss_m <= hit_r;
          if (hit) {
            tgt->hp -= dmg;
            m.dmg_dealt += dmg;
            ++m.hits;
            if (m.t_first_hit < 0.0) m.t_first_hit = tick * kDt;
            if (tgt->hp <= 0.0 && tgt->alive) {
              tgt->alive = false;
              tgt->hp = 0.0;
            }
          } else {
            // heuristic attribution
            if (!in_range) {
              ++m.miss_range;
            } else if (terr > cmd.aim_error_deg + 1.0) {
              ++m.miss_target_motion;  // true target moved off the aim point
            } else if (bot.policy.aim().overshoot_events() > overshoot_prev &&
                       cmd.aim_error_deg > 0.5) {
              ++m.miss_overshoot;
            } else {
              ++m.miss_aim_bias;
            }
          }
        }
      }
    }
    if (bot.fire_cooldown > 0) --bot.fire_cooldown;

    // --- projectile impacts --------------------------------------------------
    for (Projectile& p : projectiles) {
      if (!p.active || p.impact_tick != tick) continue;
      p.active = false;
      Dummy* t2 = (p.target_index >= 0 && p.target_index < 16)
                      ? by_index[p.target_index]
                      : nullptr;
      const WeaponProfile& wp = WeaponAt(p.weapon);
      const double dmg = wp.dps_rel * cfg.dps_scale * WeaponIntervalS(p.weapon);
      if (t2 != nullptr && t2->alive) {
        const double dx = p.ex - t2->x, dy = p.ey - kEyeHeight, dz = p.ez - t2->z;
        const double miss3 = std::sqrt(dx * dx + dy * dy + dz * dz);
        m.lead_impact_miss_m.Add(miss3);
        const double tdist = std::sqrt((t2->x - bot.x) * (t2->x - bot.x) +
                                       (t2->z - bot.z) * (t2->z - bot.z));
        const double hit_r = HitRadius(wp, tdist, cfg.target_radius) + 0.35;
        if (miss3 <= hit_r) {
          t2->hp -= dmg;
          m.dmg_dealt += dmg;
          ++m.hits;
          if (m.t_first_hit < 0.0) m.t_first_hit = tick * kDt;
          if (t2->hp <= 0.0) t2->alive = false;
        } else {
          const double move_since = miss3;  // endpoint vs true position
          if (p.fire_err_deg * p.fire_dist * botcore::kDegToRad * 0.5 < hit_r &&
              move_since > hit_r) {
            ++m.miss_target_motion;  // aim was on the (delayed) point; target moved
          } else {
            ++m.miss_aim_bias;
          }
        }
      }
      // self blast (A4): shooter inside the blast radius at impact
      if (wp.self_blast_m > 0.0 && bot.alive) {
        const double sx = p.ex - bot.x, sz = p.ez - bot.z;
        if (std::sqrt(sx * sx + sz * sz) < wp.self_blast_m) {
          const double self_dmg = 0.30 * dmg;
          bot.hp -= self_dmg;
          m.dmg_self_inflicted += self_dmg;
          m.dmg_taken += self_dmg;
          if (bot.hp <= 0.0 && bot.alive) {
            bot.hp = 0.0;
            bot.alive = false;
            m.survival_s = tick * kDt;
          }
        }
      }
    }
    projectiles.erase(std::remove_if(projectiles.begin(), projectiles.end(),
                                     [](const Projectile& p) { return !p.active; }),
                      projectiles.end());

    // --- firsts / counters ---------------------------------------------------
    if (bot.alive && cmd.target >= 0 && m.t_first_selectable < 0.0)
      m.t_first_selectable = tick * kDt;
    if (cmd.fire && m.t_first_fire_policy < 0.0) m.t_first_fire_policy = tick * kDt;
    if (fire_eff && m.t_first_fire_eff < 0.0) m.t_first_fire_eff = tick * kDt;
    if (cmd.fire && !cmd.target_visible) ++m.wasted_fire_invisible;

    m.move_fwd_mean += engaged ? cmd.forward : 0.0;
    if (engaged) {
      if (std::fabs(cmd.strafe) > 0.05) m.strafe_cmd_uptime += 1.0;
      if (std::fabs(cmd.strafe) * cfg.strafe_scale > 0.05) m.strafe_applied_uptime += 1.0;
      if (cmd.forward > 0.1) m.approach_uptime += 1.0;
      if (cmd.forward < -0.1) m.retreat_uptime += 1.0;
      if (std::fabs(cmd.forward) < 0.05 && std::fabs(cmd.strafe) < 0.05) m.still_pct += 1.0;
    } else {
      if (bot.alive) m.still_pct += 1.0;  // searching standing still counts too
    }

    overshoot_prev = bot.policy.aim().overshoot_events();

    // history push AFTER movement (this tick's true state)
    for (Dummy& d : scen.dummies) d.PushHistory();
    bot.PushHistory();

    // --- end conditions -------------------------------------------------------
    bool all_dead = !scen.dummies.empty();
    for (const Dummy& d : scen.dummies) all_dead = all_dead && !d.alive;
    if (all_dead && !scen.dummies.empty()) {
      m.ticks_run = tick + 1;
      m.outcome = "kill";
      m.t_kill = tick * kDt;
      break;
    }
    if (!bot.alive) {
      m.ticks_run = tick + 1;
      m.outcome = "death";
      break;
    }
    m.ticks_run = tick + 1;
  }

  // --- finalize metrics -------------------------------------------------------
  m.hp_end = bot.hp;
  m.overshoots = bot.policy.aim().overshoot_events();
  m.shots_gated_aim = bot.policy.aim().gated_ticks();
  m.target_switches = bot.policy.target_switches() - switches_prev;
  if (m.t_first_selectable >= 0.0 && m.t_kill >= 0.0)
    m.ttk_s = m.t_kill - m.t_first_selectable;
  if (engaged_ticks > 0) {
    double dmin = 1e9, dmax = -1e9, dmean = 0.0;
    size_t cnt = 0;
    for (double v : m.distance_engaged.raw()) {
      dmin = std::min(dmin, v);
      dmax = std::max(dmax, v);
      dmean += v;
      ++cnt;
    }
    m.dist_mean = cnt > 0 ? dmean / static_cast<double>(cnt) : 0.0;
    m.dist_min = cnt > 0 ? dmin : 0.0;
    m.dist_max = cnt > 0 ? dmax : 0.0;
    m.in_band_pct /= engaged_ticks;
    m.preferred_mean /= engaged_ticks;
    m.nearest_not_chosen_pct =
        100.0 * static_cast<double>(nearest_mismatch_ticks) / engaged_ticks;
    m.move_fwd_mean /= engaged_ticks;
    m.strafe_cmd_uptime /= engaged_ticks;
    m.strafe_applied_uptime /= engaged_ticks;
    m.approach_uptime /= engaged_ticks;
    m.retreat_uptime /= engaged_ticks;
  }
  m.still_pct = m.ticks_run > 0
                    ? 100.0 * m.still_pct / static_cast<double>(m.ticks_run)
                    : 0.0;
  m.corner_pct = m.ticks_run > 0
                     ? 100.0 * corner_ticks / static_cast<double>(m.ticks_run)
                     : 0.0;
  {
    int total_shots = 0, best = 0;
    for (int i = 0; i < 16; ++i) {
      total_shots += shots_per_dummy[i];
      best = std::max(best, shots_per_dummy[i]);
    }
    m.focus_share = total_shots > 0
                        ? static_cast<double>(best) / static_cast<double>(total_shots)
                        : 1.0;
  }
  {
    int mode = 0, mode_ct = 0, distinct = 0;
    for (int w = 1; w <= 14; ++w) {
      if (weapon_hist[w] > 0) ++distinct;
      if (weapon_hist[w] > mode_ct) { mode_ct = weapon_hist[w]; mode = w; }
    }
    m.weapon_mode = mode;
    m.weapon_distinct = distinct;
  }
  m.net_disp = std::sqrt((bot.x - start_x) * (bot.x - start_x) +
                         (bot.z - start_z) * (bot.z - start_z));
  if (m.survival_s < 0.0) m.survival_s = bot.alive ? m.ticks_run * kDt : 0.0;
  (void)visible_ticks;
  (void)first_engaged_tick;

  // digest over the rounded metric vector (reproducibility evidence)
  Digest dg;
  dg.AddInt(m.ticks_run);
  dg.Add(m.hp_end); dg.Add(m.dmg_dealt); dg.Add(m.dmg_taken);
  dg.Add(m.t_first_fire_policy); dg.Add(m.t_first_fire_eff);
  dg.Add(m.t_first_hit); dg.Add(m.ttk_s);
  dg.AddInt(m.shots_policy); dg.AddInt(m.shots_eff); dg.AddInt(m.trigger_pulls);
  dg.AddInt(m.hits); dg.AddInt(m.weapon_switches); dg.AddInt(m.target_switches);
  dg.AddInt(m.weapon_mode); dg.AddInt(m.weapon_distinct);
  dg.Add(m.dist_mean); dg.Add(m.in_band_pct); dg.Add(m.path_len);
  dg.Add(m.true_err_visible.Mean()); dg.Add(m.aim_err_policy_at_fire.Mean());
  dg.AddInt(m.retreat_events); dg.AddInt(m.miss_aim_bias);
  dg.AddInt(m.miss_target_motion); dg.AddInt(m.miss_overshoot); dg.AddInt(m.miss_range);
  dg.AddInt(m.overshoots); dg.AddInt(m.shots_gated_aim);
  m.digest = dg.value();

  if (trace != nullptr) {
    std::fprintf(trace,
                 "# trace scenario=%s tier=%d persona=%d seed=%u ticks=%d outcome=%s\n",
                 scen.name, opt.tier, opt.persona, opt.seed, m.ticks_run, m.outcome);
  }
  return m;
}

/* ------------------------------------------------------------------------ */
/* Duel runner (policy vs policy)                                            */
/* ------------------------------------------------------------------------ */

struct DuelOptions {
  SimConfig cfg;
  int tier_a = 3, persona_a = 0;
  int tier_b = 3, persona_b = 1;
  uint32_t seed = 0x20261025u;
  int rounds = 1;
};

static void FighterStepPrepare(Fighter& f, int tick, const Fighter& foe,
                               const SimConfig& cfg, WorldView* world,
                               SenseInput* sensed, bool* los) {
  world->tick = tick;
  world->pose.x = f.x;
  world->pose.y = kEyeHeight;
  world->pose.z = f.z;
  world->pose.yaw_deg = f.yaw;
  world->pose.pitch_deg = f.pitch;
  world->alive = f.alive;
  world->health = f.hp;
  world->max_health = 100.0;
  world->usable_weapons = cfg.loadout_mask;
  world->current_weapon = f.cur_weapon;
  world->deathmatch = true;

  if (f.last_hp > 0.0 && f.hp < f.last_hp) f.policy.NotifyDamage(f.last_hp, f.hp);
  f.last_hp = f.hp;
  f.policy.BeginTick(*world);

  const HistoryEntry he = foe.hist.Delayed(cfg.latency_ticks);
  sensed->index = 1;
  sensed->x = he.x;
  sensed->y = he.y;
  sensed->z = he.z;
  sensed->vx = he.vx;
  sensed->vy = he.vy;
  sensed->vz = he.vz;
  sensed->health = he.health;
  sensed->alive = he.alive;
  sensed->local = false;
  bool needs = false;
  f.policy.PlanLosQueries(sensed, 1, &needs);
  *los = needs && foe.alive;  // open arena: geometric LOS always true
}

static RunMetrics RunDuel(const DuelOptions& opt) {
  RunMetrics m;
  const SimConfig& cfg = opt.cfg;

  Fighter a, b;
  BuildProfile(opt.tier_a, opt.persona_a, DeriveSeed(opt.seed, 1, opt.tier_a, opt.persona_a),
               "QA-Duel-A", &a.profile);
  BuildProfile(opt.tier_b, opt.persona_b, DeriveSeed(opt.seed, 2, opt.tier_b, opt.persona_b),
               "QA-Duel-B", &b.profile);
  a.policy.Configure(&a.profile);
  b.policy.Configure(&b.profile);
  // start 24 m apart, facing each other
  a.x = 0.0; a.z = 12.0; a.yaw = 180.0;
  b.x = 0.0; b.z = -12.0; b.yaw = 0.0;
  a.hp = b.hp = 100.0;
  for (int i = 0; i < 4; ++i) { a.PushHistory(); b.PushHistory(); }

  struct Shot { int owner; int weapon; int impact_tick; double ex, ey, ez; };
  std::vector<Shot> shots;
  int a_fire_cooldown = 0, b_fire_cooldown = 0;
  int a_switch_timer = 0, b_switch_timer = 0;
  int a_switches = 0, b_switches = 0;

  for (int tick = 0; tick < cfg.max_ticks; ++tick) {
    WorldView wa, wb;
    SenseInput sa, sb;
    bool losa, losb;
    FighterStepPrepare(a, tick, b, cfg, &wa, &sa, &losa);
    FighterStepPrepare(b, tick, a, cfg, &wb, &sb, &losb);
    const BotCommand ca = a.policy.Step(wa, &sa, &losa, 1, kDt);
    const BotCommand cb = b.policy.Step(wb, &sb, &losb, 1, kDt);

    // per-fighter post-processing lambda
    auto integrate = [&](Fighter& f, const BotCommand& cmd, Fighter& foe,
                         int owner_id, int& cooldown, int& stimer, int& switches) {
      if (cmd.weapon != f.want_weapon) {
        f.want_weapon = cmd.weapon;
        stimer = cfg.switch_ticks;
        if (f.alive && foe.alive) ++switches;
      }
      if (f.cur_weapon != f.want_weapon) {
        if (stimer > 0) --stimer;
        if (stimer <= 0) f.cur_weapon = f.want_weapon;
      }
      const bool ready = (f.cur_weapon == f.want_weapon);
      f.yaw += cmd.yaw_delta_deg;
      f.pitch = std::max(-89.0, std::min(89.0, f.pitch + cmd.pitch_delta_deg));
      if (f.alive && !cfg.lock_movement) {
        double fx, fz, rx, rz;
        FacingVectors(f.yaw, &fx, &fz, &rx, &rz);
        f.x += (fx * cmd.forward + rx * cmd.strafe * cfg.strafe_scale) * cfg.move_speed * kDt;
        f.z += (fz * cmd.forward + rz * cmd.strafe * cfg.strafe_scale) * cfg.move_speed * kDt;
        f.x = std::max(-cfg.arena_half, std::min(cfg.arena_half, f.x));
        f.z = std::max(-cfg.arena_half, std::min(cfg.arena_half, f.z));
      }
      const bool fire_eff = cmd.fire && ready && f.alive && foe.alive;
      if (fire_eff && cooldown <= 0) {
        cooldown = IntervalTicks(f.cur_weapon);
        const WeaponProfile& wp = WeaponAt(f.cur_weapon);
        const double dx = foe.x - f.x, dz = foe.z - f.z;
        const double dist = std::sqrt(dx * dx + dz * dz);
        const double dmg = wp.dps_rel * cfg.dps_scale * WeaponIntervalS(f.cur_weapon);
        if (wp.proj_speed > 0.0 && dist > wp.min_m) {
          const int flight = std::max(1, static_cast<int>(std::llround(dist / wp.proj_speed / kDt)));
          const double yr = f.yaw * botcore::kDegToRad;
          const double pr = f.pitch * botcore::kDegToRad;
          Shot s{owner_id, f.cur_weapon, tick + flight,
                 f.x - std::sin(yr) * std::cos(pr) * dist,
                 kEyeHeight + std::sin(pr) * dist,
                 f.z - std::cos(yr) * std::cos(pr) * dist};
          shots.push_back(s);
        } else {
          const double terr = AngularErrorDeg(f.x, kEyeHeight, f.z, f.yaw, f.pitch,
                                              foe.x, kEyeHeight, foe.z);
          const double miss_m = MissDistanceM(terr, dist);
          const double hit_r = HitRadius(wp, dist, cfg.target_radius);
          if (dist <= wp.max_m * 1.5 + 0.5 && miss_m <= hit_r) {
            foe.hp -= dmg;
            if (owner_id == 1) m.duel_dmg_a += dmg; else m.duel_dmg_b += dmg;
            if (foe.hp <= 0.0 && foe.alive) {
              foe.hp = 0.0;
              foe.alive = false;
            }
          }
        }
      }
      if (cooldown > 0) --cooldown;
    };
    integrate(a, ca, b, 1, a_fire_cooldown, a_switch_timer, a_switches);
    integrate(b, cb, a, 2, b_fire_cooldown, b_switch_timer, b_switches);

    // projectile impacts
    for (Shot& s : shots) {
      if (s.impact_tick != tick) continue;
      Fighter& shooter = (s.owner == 1) ? a : b;
      Fighter& victim = (s.owner == 1) ? b : a;
      const WeaponProfile& wp = WeaponAt(s.weapon);
      const double dmg = wp.dps_rel * cfg.dps_scale * WeaponIntervalS(s.weapon);
      if (victim.alive) {
        const double dx = s.ex - victim.x, dz = s.ez - victim.z;
        const double miss3 = std::sqrt(dx * dx + (s.ey - kEyeHeight) * (s.ey - kEyeHeight) + dz * dz);
        const double vdist = std::sqrt((victim.x - shooter.x) * (victim.x - shooter.x) +
                                       (victim.z - shooter.z) * (victim.z - shooter.z));
        if (miss3 <= HitRadius(wp, vdist, cfg.target_radius) + 0.35) {
          victim.hp -= dmg;
          if (s.owner == 1) m.duel_dmg_a += dmg; else m.duel_dmg_b += dmg;
          if (victim.hp <= 0.0) { victim.hp = 0.0; victim.alive = false; }
        }
      }
      if (wp.self_blast_m > 0.0 && shooter.alive) {
        const double sx = s.ex - shooter.x, sz = s.ez - shooter.z;
        if (std::sqrt(sx * sx + sz * sz) < wp.self_blast_m) {
          shooter.hp -= 0.30 * dmg;
          if (shooter.hp <= 0.0 && shooter.alive) { shooter.hp = 0.0; shooter.alive = false; }
        }
      }
      s.impact_tick = -1;
    }
    shots.erase(std::remove_if(shots.begin(), shots.end(),
                               [](const Shot& s) { return s.impact_tick < 0; }),
                shots.end());

    a.PushHistory();
    b.PushHistory();

    if (!a.alive || !b.alive) {
      m.ticks_run = tick + 1;
      break;
    }
    m.ticks_run = tick + 1;
  }

  m.duel_winner = (a.alive && !b.alive) ? 1 : (b.alive && !a.alive) ? 2 : 0;
  m.duel_duration_s = m.ticks_run * kDt;
  m.duel_hp_a = a.hp;
  m.duel_hp_b = b.hp;
  m.duel_switches_a = a_switches;
  m.duel_switches_b = b_switches;
  m.weapon_switches = a_switches + b_switches;
  m.outcome = m.duel_winner != 0 ? "kill" : "timeout";
  Digest dg;
  dg.AddInt(m.duel_winner); dg.AddInt(m.ticks_run);
  dg.Add(m.duel_dmg_a); dg.Add(m.duel_dmg_b); dg.Add(a.hp); dg.Add(b.hp);
  dg.AddInt(a_switches); dg.AddInt(b_switches);
  dg.AddInt(a.policy.target_switches()); dg.AddInt(b.policy.target_switches());
  m.digest = dg.value();
  return m;
}

/* ------------------------------------------------------------------------ */
/* JSON output                                                               */
/* ------------------------------------------------------------------------ */

static void PrintConfigJson(const SimConfig& c) {
  std::printf("\"config\":{"
              "\"latency_ticks\":%d,\"strafe_scale\":%.2f,\"move_speed\":%.2f,"
              "\"switch_ticks\":%d,\"dps_scale\":%.1f,\"target_radius\":%.2f,"
              "\"arena_half\":%.1f,\"lock_movement\":%s,\"loadout_mask\":%u,"
              "\"cover_gap_ticks\":%d}",
              c.latency_ticks, c.strafe_scale, c.move_speed, c.switch_ticks,
              c.dps_scale, c.target_radius, c.arena_half,
              c.lock_movement ? "true" : "false", c.loadout_mask, c.cover_gap_ticks);
}

static void EmitRunJson(const ScenarioDef& def, const RunOptions& opt,
                        const SimConfig& eff_cfg, const RunMetrics& m) {
  Series ae = const_cast<RunMetrics&>(m).aim_err_policy_at_fire;
  Series te = const_cast<RunMetrics&>(m).true_err_at_fire;
  Series tv = const_cast<RunMetrics&>(m).true_err_visible;
  Series lm = const_cast<RunMetrics&>(m).lead_impact_miss_m;
  const double hit_rate = m.trigger_pulls > 0
                              ? static_cast<double>(m.hits) / m.trigger_pulls
                              : 0.0;
  std::printf("{\"kind\":\"run\",\"scenario\":\"%s\",\"tier\":%d,\"persona\":%d,"
              "\"seed\":%u,\"skill_name\":\"%s\",\"persona_name\":\"%s\",",
              def.name, opt.tier, opt.persona, opt.seed, SkillName(opt.tier),
              PersonalityName(opt.persona));
  PrintConfigJson(eff_cfg);
  std::printf(",\"outcome\":\"%s\",\"ticks\":%d,\"metrics\":{"
              "\"hp_end\":%.2f,\"dmg_dealt\":%.1f,\"dmg_taken\":%.1f,\"dmg_self\":%.1f,"
              "\"t_first_selectable_s\":%.3f,\"t_first_fire_policy_s\":%.3f,"
              "\"t_first_fire_eff_s\":%.3f,\"t_first_hit_s\":%.3f,\"t_kill_s\":%.3f,"
              "\"ttk_s\":%.3f,"
              "\"shots_policy\":%d,\"shots_blocked_switch\":%d,\"shots_eff\":%d,"
              "\"trigger_pulls\":%d,\"shots_gated_aim\":%d,\"hits\":%d,"
              "\"hit_rate\":%.4f,\"wasted_fire_invisible\":%d,"
              "\"aim_err_policy_fire_mean\":%.3f,\"aim_err_policy_fire_p95\":%.3f,"
              "\"true_err_fire_mean\":%.3f,\"true_err_fire_p95\":%.3f,"
              "\"true_err_visible_mean\":%.3f,\"true_err_visible_p95\":%.3f,"
              "\"overshoots\":%d,"
              "\"miss_range\":%d,\"miss_target_motion\":%d,\"miss_overshoot\":%d,"
              "\"miss_aim_bias\":%d,"
              "\"lead_impact_miss_p50_m\":%.3f,\"lead_impact_miss_p95_m\":%.3f,"
              "\"lead_samples\":%d,"
              "\"weapon_switches\":%d,\"weapon_switch_wasted_ticks\":%d,"
              "\"weapon_mode\":%d,\"weapon_distinct\":%d,"
              "\"target_switches\":%d,\"focus_share\":%.3f,"
              "\"los_queries_max\":%d,\"ray_budget_skips\":%d,"
              "\"nearest_not_chosen_pct\":%.2f,"
              "\"dist_mean_m\":%.2f,\"dist_min_m\":%.2f,\"dist_max_m\":%.2f,"
              "\"in_band_pct\":%.3f,\"preferred_mean_m\":%.2f,\"corner_pct\":%.2f,"
              "\"move_fwd_mean\":%.3f,\"strafe_cmd_uptime\":%.3f,"
              "\"strafe_applied_uptime\":%.3f,\"still_pct\":%.2f,"
              "\"approach_uptime\":%.3f,\"retreat_uptime\":%.3f,"
              "\"path_len_m\":%.2f,\"net_disp_m\":%.2f,"
              "\"retreat_events\":%d,\"hp_at_first_retreat\":%.2f,"
              "\"survival_s\":%.2f,\"sim_dps\":%.2f,"
              "\"digest\":\"%016" PRIx64 "\"}}\n",
              m.outcome, m.ticks_run,
              m.hp_end, m.dmg_dealt, m.dmg_taken, m.dmg_self_inflicted,
              m.t_first_selectable, m.t_first_fire_policy, m.t_first_fire_eff,
              m.t_first_hit, m.t_kill, m.ttk_s,
              m.shots_policy, m.shots_blocked_switch, m.shots_eff, m.trigger_pulls,
              m.shots_gated_aim, m.hits, hit_rate, m.wasted_fire_invisible,
              ae.Mean(), ae.Percentile(0.95), te.Mean(), te.Percentile(0.95),
              tv.Mean(), tv.Percentile(0.95), m.overshoots,
              m.miss_range, m.miss_target_motion, m.miss_overshoot, m.miss_aim_bias,
              lm.Percentile(0.5), lm.Percentile(0.95), static_cast<int>(lm.n()),
              m.weapon_switches, m.weapon_switch_wasted_ticks, m.weapon_mode,
              m.weapon_distinct, m.target_switches,
              m.focus_share, m.los_queries_max, m.ray_budget_skips,
              m.nearest_not_chosen_pct,
              m.dist_mean, m.dist_min, m.dist_max, m.in_band_pct, m.preferred_mean,
              m.corner_pct, m.move_fwd_mean, m.strafe_cmd_uptime,
              m.strafe_applied_uptime, m.still_pct, m.approach_uptime,
              m.retreat_uptime, m.path_len, m.net_disp,
              m.retreat_events, m.hp_at_first_retreat, m.survival_s,
              m.ticks_run > 0 ? m.dmg_dealt / (m.ticks_run * kDt) : 0.0,
              m.digest);
  (void)eff_cfg;
}

static void EmitDuelJson(const DuelOptions& opt, const SimConfig& eff_cfg,
                         int round, const RunMetrics& m) {
  std::printf("{\"kind\":\"duel\",\"round\":%d,"
              "\"a\":{\"tier\":%d,\"persona\":%d,\"skill\":\"%s\",\"persona_name\":\"%s\"},"
              "\"b\":{\"tier\":%d,\"persona\":%d,\"skill\":\"%s\",\"persona_name\":\"%s\"},",
              round, opt.tier_a, opt.persona_a, SkillName(opt.tier_a),
              PersonalityName(opt.persona_a), opt.tier_b, opt.persona_b,
              SkillName(opt.tier_b), PersonalityName(opt.persona_b));
  PrintConfigJson(eff_cfg);
  std::printf(",\"seed\":%u,\"winner\":%d,\"outcome\":\"%s\",\"duration_s\":%.2f,"
              "\"ticks\":%d,\"hp_a\":%.1f,\"hp_b\":%.1f,\"dmg_by_a\":%.1f,"
              "\"dmg_by_b\":%.1f,\"switches_a\":%d,\"switches_b\":%d,"
              "\"digest\":\"%016" PRIx64 "\"}\n",
              opt.seed, m.duel_winner, m.outcome, m.duel_duration_s, m.ticks_run,
              m.duel_hp_a, m.duel_hp_b, m.duel_dmg_a, m.duel_dmg_b,
              m.duel_switches_a, m.duel_switches_b, m.digest);
}

/* ------------------------------------------------------------------------ */
/* Self-test                                                                 */
/* ------------------------------------------------------------------------ */

static int g_self_fail = 0;
#define QA_CHECK(cond, msg)                                              \
  do {                                                                   \
    if (!(cond)) {                                                       \
      std::printf("SELFTEST FAIL: %s (line %d)\n", msg, __LINE__);       \
      ++g_self_fail;                                                     \
    }                                                                    \
  } while (0)

static const ScenarioDef* FindScenario(const std::vector<ScenarioDef>& v,
                                       const char* name) {
  for (const ScenarioDef& s : v)
    if (std::strcmp(s.name, name) == 0) return &s;
  return nullptr;
}

static int RunSelfTest() {
  std::printf("# behavior-qa selftest (offline simulation; not retail)\n");
  const std::vector<ScenarioDef> scenarios = BuildScenarios();

  // geometry
  {
    const Rect2D r{-2.0, -6.0, 2.0, -5.0};
    QA_CHECK(SegmentHitsRect(0, 0, 0, -10, r), "segment through rect hits");
    QA_CHECK(!SegmentHitsRect(0, 0, 10, -10, r), "segment past rect misses");
    QA_CHECK(!SegmentHitsRect(5, 0, 5, -10, r), "parallel segment misses");
  }
  // angular error: dead-on view => ~0 deg; 90 deg off => ~90
  {
    const double e0 = AngularErrorDeg(0, kEyeHeight, 0, 0.0, 0.0, 0.0, kEyeHeight, -10.0);
    QA_CHECK(e0 < 0.01, "dead-on angular error ~0");
    const double e90 = AngularErrorDeg(0, kEyeHeight, 0, 90.0, 0.0, 0.0, kEyeHeight, -10.0);
    QA_CHECK(std::fabs(e90 - 90.0) < 0.5, "90 deg off-view error ~90");
  }
  // facing vectors match the aim convention
  {
    double fx, fz, rx, rz;
    FacingVectors(0.0, &fx, &fz, &rx, &rz);
    QA_CHECK(std::fabs(fz + 1.0) < 1e-9 && std::fabs(fx) < 1e-9, "yaw 0 faces -z");
    QA_CHECK(std::fabs(rx - 1.0) < 1e-9, "yaw 0 right is +x");
  }
  // determinism: same inputs twice => same digest
  {
    const ScenarioDef* s = FindScenario(scenarios, "tracking_strafe");
    QA_CHECK(s != nullptr, "tracking_strafe exists");
    RunOptions o;
    o.tier = 3; o.persona = 2; o.seed = 42u;
    const RunMetrics m1 = RunScenario(*s, o, nullptr);
    const RunMetrics m2 = RunScenario(*s, o, nullptr);
    QA_CHECK(m1.digest == m2.digest, "identical seed => identical digest");
    RunOptions o2 = o;
    o2.seed = 43u;
    const RunMetrics m3 = RunScenario(*s, o2, nullptr);
    QA_CHECK(m3.digest != m1.digest, "different seed => different digest");
  }
  // policy contract: never fire without fresh LOS; ray budget respected
  {
    const ScenarioDef* s = FindScenario(scenarios, "cover_reacquire");
    QA_CHECK(s != nullptr, "cover_reacquire exists");
    for (int tier = 1; tier <= 5; ++tier) {
      RunOptions o;
      o.tier = tier; o.persona = tier % 6; o.seed = 7u + tier;
      o.cfg.cover_gap_ticks = 40;
      const RunMetrics m = RunScenario(*s, o, nullptr);
      QA_CHECK(m.wasted_fire_invisible == 0, "no fire without LOS (any tier)");
      QA_CHECK(m.los_queries_max <= botcore::SkillFor(tier).max_los_per_tick,
               "LOS budget respected");
    }
  }
  // gallery: locked movement must not move the body
  {
    const ScenarioDef* s = FindScenario(scenarios, "gallery_static");
    RunOptions o; o.tier = 5; o.persona = 0; o.seed = 11u;
    const RunMetrics m = RunScenario(*s, o, nullptr);
    QA_CHECK(m.net_disp < 1e-9, "gallery mode freezes the body");
    QA_CHECK(m.hits > 0, "expert gallery lands hits");
    QA_CHECK(m.t_first_fire_policy > 0.0, "fire is reaction-gated, not instant");
  }
  // Skill sanity inside the sim, using the FIXED-GEOMETRY gallery so the aim
  // signal is not confounded by the tiers' differing preferred_range_m (see the
  // QA report: free-movement hit rate is deliberately NOT monotonic in tier).
  {
    const ScenarioDef* gal = FindScenario(scenarios, "gallery_static");
    QA_CHECK(gal != nullptr, "gallery_static exists");
    // Aggregate several seeds: mean TRUE aim error must fall with rising tier.
    double err[6] = {0.0};
    double hr[6] = {0.0};
    const int kSeeds = 8;
    for (int t = 1; t <= 5; ++t) {
      for (int r = 0; r < kSeeds; ++r) {
        RunOptions o; o.tier = t; o.persona = 2; o.seed = 100u + r;
        const RunMetrics mm = RunScenario(*gal, o, nullptr);
        Series tv = const_cast<RunMetrics&>(mm).true_err_visible;
        err[t] += tv.Mean() / kSeeds;
        hr[t] += (mm.trigger_pulls > 0
                      ? static_cast<double>(mm.hits) / mm.trigger_pulls
                      : 0.0) / kSeeds;
      }
    }
    QA_CHECK(err[5] < err[4] && err[4] < err[3] && err[3] < err[2] && err[2] < err[1],
             "gallery: true aim error strictly decreases with tier");
    QA_CHECK(hr[5] > hr[1] + 0.2, "gallery: expert hit rate far above beginner");
    QA_CHECK(hr[5] > hr[3], "gallery: expert hit rate above average");
  }
  // Free-movement engagement: the expert must actually finish a static target
  // and pull the trigger sooner than the beginner (reaction, not TTK order).
  {
    const ScenarioDef* s = FindScenario(scenarios, "reaction_static");
    RunOptions o1; o1.tier = 1; o1.persona = 2; o1.seed = 5u;
    RunOptions o5 = o1; o5.tier = 5;
    const RunMetrics m1 = RunScenario(*s, o1, nullptr);
    const RunMetrics m5 = RunScenario(*s, o5, nullptr);
    QA_CHECK(m5.t_first_fire_eff >= 0.0 && m1.t_first_fire_eff >= 0.0,
             "both tiers eventually fire");
    QA_CHECK(m5.t_first_fire_eff < m1.t_first_fire_eff,
             "expert fires earlier than beginner");
    QA_CHECK(m5.ttk_s >= 0.0, "expert finishes the static target");
  }
  // duel sanity: expert beats beginner in the majority of rounds
  {
    int expert_wins = 0;
    const int rounds = 9;
    for (int r = 0; r < rounds; ++r) {
      DuelOptions d;
      d.tier_a = 5; d.persona_a = 2;
      d.tier_b = 1; d.persona_b = 2;
      d.seed = 1000u + r;
      d.rounds = 1;
      d.cfg.max_ticks = 900;
      const RunMetrics m = RunDuel(d);
      if (m.duel_winner == 1) ++expert_wins;
    }
    QA_CHECK(expert_wins >= rounds * 2 / 3, "expert wins most duels vs beginner");
  }
  // strafe suppression mirrors the integration default
  {
    const ScenarioDef* s = FindScenario(scenarios, "tracking_strafe");
    RunOptions o; o.tier = 3; o.persona = 2; o.seed = 9u;
    o.cfg.strafe_scale = 0.0;
    const RunMetrics off = RunScenario(*s, o, nullptr);
    o.cfg.strafe_scale = 1.0;
    const RunMetrics on = RunScenario(*s, o, nullptr);
    QA_CHECK(off.strafe_applied_uptime == 0.0, "strafe_scale 0 => no lateral motion");
    QA_CHECK(on.strafe_applied_uptime > 0.0, "strafe_scale 1 => lateral motion");
    QA_CHECK(off.strafe_cmd_uptime > 0.0, "policy still commands strafe when suppressed");
  }
  std::printf(g_self_fail == 0 ? "QA SELFTEST PASS\n" : "QA SELFTEST FAIL\n");
  return g_self_fail == 0 ? 0 : 1;
}

/* ------------------------------------------------------------------------ */
/* Perf mode                                                                 */
/* ------------------------------------------------------------------------ */

static int RunPerf(int candidates, int ticks) {
  std::printf("{\"kind\":\"perf\",\"candidates\":%d,\"ticks\":%d,\"rows\":[", candidates,
              ticks);
  bool first = true;
  for (int tier = 1; tier <= 5; ++tier) {
    BotProfile p;
    BuildProfile(tier, tier % 6, DeriveSeed(99u, 0, tier, 0), "QA-Perf", &p);
    HumanBotPolicy policy;
    policy.Configure(&p);
    std::vector<SenseInput> sensed(candidates);
    std::unique_ptr<bool[]> los(new bool[candidates]());
    std::unique_ptr<bool[]> needs(new bool[candidates]());
    for (int i = 0; i < candidates; ++i) {
      sensed[i].index = i;
      sensed[i].x = (i % 3 - 1) * 6.0;
      sensed[i].y = kEyeHeight;
      sensed[i].z = -(5.0 + i * 2.0);
      sensed[i].vx = 2.0;
      sensed[i].health = 100.0;
      sensed[i].alive = true;
    }
    double yaw = 0.0;
    const auto t0 = std::chrono::steady_clock::now();
    for (int t = 0; t < ticks; ++t) {
      WorldView w;
      w.tick = t;
      w.pose.yaw_deg = yaw;
      w.alive = true;
      w.health = 90.0;
      w.max_health = 100.0;
      w.usable_weapons = 0x3FFFu;
      w.current_weapon = 2;
      policy.BeginTick(w);
      policy.PlanLosQueries(sensed.data(), candidates, needs.get());
      for (int i = 0; i < candidates; ++i) los[i] = needs[i];
      const BotCommand c = policy.Step(w, sensed.data(), los.get(), candidates, kDt);
      yaw += c.yaw_delta_deg;
    }
    const auto t1 = std::chrono::steady_clock::now();
    const double ns =
        std::chrono::duration_cast<std::chrono::nanoseconds>(t1 - t0).count();
    if (!first) std::printf(",");
    first = false;
    std::printf("{\"tier\":%d,\"ns_per_tick\":%.1f}", tier,
                ns / static_cast<double>(ticks));
  }
  std::printf("]}\n");
  return 0;
}

/* ------------------------------------------------------------------------ */
/* Weapon-score curve probe (exposes dominant-strategy in the loadout table) */
/* ------------------------------------------------------------------------ */

// Prints, per distance, the best weapon and the runner-up gap for a given
// personality range_preference. This is a direct read-out of botcore's
// ScoreWeapon() hypothesis table (bot_loadout.h) - it makes the "one weapon
// dominates every band" finding reproducible without running a scenario.
static int RunWeaponCurve(double range_pref) {
  std::printf("{\"kind\":\"weapon_curve\",\"range_preference\":%.2f,\"rows\":[", range_pref);
  bool first = true;
  for (int d = 2; d <= 45; d += 1) {
    const double dist = static_cast<double>(d);
    // rank all weapons by ScoreWeapon at this distance
    int best = -1, second = -1;
    double bs = -1.0, ss = -1.0;
    for (int w = 1; w <= 14; ++w) {
      const double s = botcore::ScoreWeapon(w, dist, range_pref);
      if (s > bs) { ss = bs; second = best; bs = s; best = w; }
      else if (s > ss) { ss = s; second = w; }
    }
    if (!first) std::printf(",");
    first = false;
    std::printf("{\"dist_m\":%d,\"best\":%d,\"best_name\":\"%s\",\"best_score\":%.3f,"
                "\"runner_up\":%d,\"runner_up_name\":\"%s\",\"margin\":%.3f}",
                d, best, WeaponName(best), bs, second, WeaponName(second), bs - ss);
  }
  std::printf("]}\n");
  return 0;
}

/* ------------------------------------------------------------------------ */
/* CLI                                                                       */
/* ------------------------------------------------------------------------ */

static void Usage() {
  std::printf(
      "qa_sim - offline Human-KI combat QA (SIMULATION ONLY, not retail)\n"
      "usage:\n"
      "  qa_sim --list\n"
      "  qa_sim --selftest\n"
      "  qa_sim --scenario NAME [--tier T] [--persona P] [--seed S]\n"
      "         [--latency L] [--strafe-scale F] [--cover-gap N] [--switch-ticks N]\n"
      "         [--move-speed F] [--dps-scale F] [--target-radius F]\n"
      "  qa_sim --sweep --scenarios A,B,... --tiers 1,2,.. --personas 0,1,.. \n"
      "         [--seeds N] [--seed-base S] [--latency L] [--strafe-scale F] ...\n"
      "  qa_sim --duel --duel-a TIER:PERSONA --duel-b TIER:PERSONA [--rounds N]\n"
      "         [--seed-base S] [--strafe-scale F] [--latency L]\n"
      "  qa_sim --perf [--candidates N] [--ticks N]\n");
}

static bool ParseIntList(const char* s, std::vector<int>* out) {
  out->clear();
  const char* p = s;
  while (*p) {
    char* end = nullptr;
    const long v = std::strtol(p, &end, 10);
    if (end == p) return false;
    out->push_back(static_cast<int>(v));
    p = end;
    while (*p == ',' || *p == ' ') ++p;
  }
  return !out->empty();
}

static bool ParseScenarioList(const char* s, std::vector<std::string>* out) {
  out->clear();
  std::string cur;
  for (const char* p = s;; ++p) {
    if (*p == ',' || *p == '\0') {
      if (!cur.empty()) out->push_back(cur);
      cur.clear();
      if (*p == '\0') break;
    } else {
      cur.push_back(*p);
    }
  }
  return !out->empty();
}

int main(int argc, char** argv) {
  std::vector<ScenarioDef> scenarios = BuildScenarios();
  SimConfig cfg;
  int tier = 3, persona = 2;
  uint32_t seed = 0x20261025u;
  const char* scenario_name = nullptr;
  bool do_list = false, do_selftest = false, do_sweep = false, do_duel = false,
       do_perf = false, do_weapon_curve = false;
  double weapon_curve_pref = 0.0;
  std::string sweep_scenarios, tiers_s, personas_s;
  int seeds = 5;
  uint32_t seed_base = 0x51A2026u;
  int duel_a_t = 3, duel_a_p = 0, duel_b_t = 3, duel_b_p = 1, duel_rounds = 9;
  int perf_candidates = 8, perf_ticks = 20000;

  for (int i = 1; i < argc; ++i) {
    const std::string a = argv[i];
    auto next = [&](const char* what) -> const char* {
      if (i + 1 >= argc) {
        std::fprintf(stderr, "qa_sim: missing value for %s\n", what);
        std::exit(2);
      }
      return argv[++i];
    };
    if (a == "--list") do_list = true;
    else if (a == "--selftest") do_selftest = true;
    else if (a == "--scenario") scenario_name = next("--scenario");
    else if (a == "--sweep") do_sweep = true;
    else if (a == "--duel") do_duel = true;
    else if (a == "--perf") do_perf = true;
    else if (a == "--weapon-curve") do_weapon_curve = true;
    else if (a == "--range-pref") weapon_curve_pref = std::atof(next("--range-pref"));
    else if (a == "--scenarios") sweep_scenarios = next("--scenarios");
    else if (a == "--tiers") tiers_s = next("--tiers");
    else if (a == "--personas") personas_s = next("--personas");
    else if (a == "--tier") tier = std::atoi(next("--tier"));
    else if (a == "--persona") persona = std::atoi(next("--persona"));
    else if (a == "--seed") seed = static_cast<uint32_t>(std::strtoul(next("--seed"), nullptr, 10));
    else if (a == "--seeds") seeds = std::atoi(next("--seeds"));
    else if (a == "--seed-base") seed_base = static_cast<uint32_t>(std::strtoul(next("--seed-base"), nullptr, 10));
    else if (a == "--latency") cfg.latency_ticks = std::atoi(next("--latency"));
    else if (a == "--strafe-scale") cfg.strafe_scale = std::atof(next("--strafe-scale"));
    else if (a == "--move-speed") cfg.move_speed = std::atof(next("--move-speed"));
    else if (a == "--switch-ticks") cfg.switch_ticks = std::atoi(next("--switch-ticks"));
    else if (a == "--dps-scale") cfg.dps_scale = std::atof(next("--dps-scale"));
    else if (a == "--target-radius") cfg.target_radius = std::atof(next("--target-radius"));
    else if (a == "--cover-gap") cfg.cover_gap_ticks = std::atoi(next("--cover-gap"));
    else if (a == "--max-ticks") cfg.max_ticks = std::atoi(next("--max-ticks"));
    else if (a == "--duel-a") {
      if (std::sscanf(next("--duel-a"), "%d:%d", &duel_a_t, &duel_a_p) != 2) {
        std::fprintf(stderr, "qa_sim: --duel-a expects TIER:PERSONA\n"); return 2;
      }
    } else if (a == "--duel-b") {
      if (std::sscanf(next("--duel-b"), "%d:%d", &duel_b_t, &duel_b_p) != 2) {
        std::fprintf(stderr, "qa_sim: --duel-b expects TIER:PERSONA\n"); return 2;
      }
    } else if (a == "--rounds") duel_rounds = std::atoi(next("--rounds"));
    else if (a == "--candidates") perf_candidates = std::atoi(next("--candidates"));
    else if (a == "--ticks") perf_ticks = std::atoi(next("--ticks"));
    else if (a == "--help" || a == "-h") { Usage(); return 0; }
    else {
      std::fprintf(stderr, "qa_sim: unknown argument %s\n", a.c_str());
      Usage();
      return 2;
    }
  }

  if (do_list) {
    std::printf("{\"kind\":\"scenarios\",\"items\":[");
    for (size_t i = 0; i < scenarios.size(); ++i) {
      std::printf("%s{\"name\":\"%s\",\"description\":\"%s\",\"max_ticks\":%d}",
                  i ? "," : "", scenarios[i].name, scenarios[i].description,
                  scenarios[i].max_ticks);
    }
    std::printf("]}\n");
    return 0;
  }
  if (do_selftest) return RunSelfTest();
  if (do_perf) return RunPerf(perf_candidates, perf_ticks);
  if (do_weapon_curve) return RunWeaponCurve(weapon_curve_pref);

  if (do_duel) {
    DuelOptions d;
    d.cfg = cfg;
    d.cfg.max_ticks = cfg.max_ticks > 0 ? cfg.max_ticks : 900;
    d.tier_a = duel_a_t; d.persona_a = duel_a_p;
    d.tier_b = duel_b_t; d.persona_b = duel_b_p;
    long long wins_a = 0, wins_b = 0, draws = 0;
    for (int r = 0; r < duel_rounds; ++r) {
      d.seed = seed_base + static_cast<uint32_t>(r);
      const RunMetrics m = RunDuel(d);
      EmitDuelJson(d, d.cfg, r, m);
      if (m.duel_winner == 1) ++wins_a;
      else if (m.duel_winner == 2) ++wins_b;
      else ++draws;
    }
    std::printf("{\"kind\":\"duel_summary\",\"a\":{\"tier\":%d,\"persona\":%d},"
                "\"b\":{\"tier\":%d,\"persona\":%d},\"rounds\":%d,"
                "\"wins_a\":%lld,\"wins_b\":%lld,\"draws\":%lld,"
                "\"dmg_a\":0,\"dmg_b\":0}\n",
                duel_a_t, duel_a_p, duel_b_t, duel_b_p, duel_rounds, wins_a,
                wins_b, draws);
    return 0;
  }

  if (do_sweep) {
    std::vector<std::string> names;
    std::vector<int> tiers, personas;
    if (!ParseScenarioList(sweep_scenarios.c_str(), &names) ||
        !ParseIntList(tiers_s.empty() ? "3" : tiers_s.c_str(), &tiers) ||
        !ParseIntList(personas_s.empty() ? "2" : personas_s.c_str(), &personas)) {
      std::fprintf(stderr, "qa_sim: bad sweep lists\n");
      return 2;
    }
    for (const std::string& name : names) {
      const ScenarioDef* s = FindScenario(scenarios, name.c_str());
      if (s == nullptr) {
        std::fprintf(stderr, "qa_sim: unknown scenario %s\n", name.c_str());
        return 2;
      }
      for (int t : tiers) {
        for (int p : personas) {
          for (int r = 0; r < seeds; ++r) {
            RunOptions o;
            o.cfg = cfg;
            o.tier = t;
            o.persona = p;
            o.seed = seed_base ^ (static_cast<uint32_t>(t) * 0x9E37u) ^
                     (static_cast<uint32_t>(p) * 0x85EBu) ^
                     (static_cast<uint32_t>(r) * 0xC2B2u);
            const RunMetrics m = RunScenario(*s, o, nullptr);
            EmitRunJson(*s, o, o.cfg, m);
          }
        }
      }
    }
    return 0;
  }

  if (scenario_name != nullptr) {
    const ScenarioDef* s = FindScenario(scenarios, scenario_name);
    if (s == nullptr) {
      std::fprintf(stderr, "qa_sim: unknown scenario %s\n", scenario_name);
      return 2;
    }
    RunOptions o;
    o.cfg = cfg;
    o.tier = tier;
    o.persona = persona;
    o.seed = seed;
    const RunMetrics m = RunScenario(*s, o, nullptr);
    EmitRunJson(*s, o, o.cfg, m);
    return 0;
  }

  Usage();
  return 2;
}
