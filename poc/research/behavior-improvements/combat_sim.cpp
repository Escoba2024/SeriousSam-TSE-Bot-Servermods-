// combat_sim.cpp - deterministic offline duel simulator (research).
// Drives the REAL botcore HumanBotPolicy (read-only include) in a synthetic
// 20 Hz arena. Baseline = qualified botcore profile + shipped integration
// defaults (bot_fStrafeScale=0 => strafe suppressed, per PR #62 F-5).
// Candidate = adjusted profile + combat2 overlays (weapon selector 2, strafe
// controller, LOS-breaking retreat, hitscan latency lead at the sense seam).
//
// SIMULATION != RETAIL. Weapon damage/fire-interval table below is ONE shared
// world model for both policies (fair A/B); it is a calibration hypothesis,
// not extracted Retail data. All results: NOT_TESTED_RETAIL.
#include <array>
#include <chrono>
#include <cmath>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <vector>

#include "bot_human.h"
#include "combat2_profile.h"
#include "combat2_tactics.h"
#include "combat2_weapon.h"

using namespace botcore;

namespace {

constexpr double kDt = 0.05;
constexpr double kEyeY = 1.6;
constexpr double kMaxSpeed = 7.0;

struct SimWeapon { double dmg; double interval_s; double tol_mult; double max_range; double proj_speed; double splash_tol; };
const SimWeapon& SW(int i) {
  static const SimWeapon kW[14] = {
      {20, .50, 3.0, 2.6, 0, 0},   {10, .35, 1.0, 200, 0, 0},  {10, .22, .95, 200, 0, 0},
      {56, .90, 1.0, 200, 0, 0},   {96, 1.10, 1.0, 200, 0, 0}, {9, .10, 1.0, 200, 0, 0},
      {9, .07, 1.0, 200, 0, 0},    {75, .80, 1.0, 200, 20, 1.9}, {60, .90, 1.0, 200, 12, 1.6},
      {15, .20, 3.0, 2.6, 0, 0},   {6, .08, 1.6, 13, 15, 0},   {11, .12, 1.0, 200, 0, 0},
      {90, 1.40, .85, 300, 0, 0},  {100, 1.60, 1.0, 200, 25, 1.4}};
  if (i < 1) i = 1;
  if (i > 14) i = 14;
  return kW[i - 1];
}
bool IsShotgun(int i) { return i == 4 || i == 5; }

struct Fighter {
  double x = 0, z = 0, yaw = 0, pitch = 0, hp = 100;
  double vx = 0, vz = 0;
  bool alive = true;
  HumanBotPolicy policy;
  combat2::WeaponSelector2 ws2;
  combat2::StrafeController strafe2;
  int tier = 3, persona = 0, weapon = 6; bool candidate = false;
  double fire_cooldown = 0;
  // metrics
  long shots = 0, hits = 0, fire_ticks = 0, strafe_ticks = 0, retreat_ticks = 0;
  double dmg_dealt = 0, aim_err_sum = 0; long aim_err_n = 0;
  int first_fire_tick = -1, weapon_switches = 0; int prev_weapon = -1;
  long weapon_ticks[15] = {0};
  double range_sum = 0; long range_n = 0;
  double prev_hp = 100;
};

struct DuelResult {
  int winner = -1;  // 0,1 or -1 timeout draw
  double duration_s = 0;
  Fighter* f[2];
};

uint32_t AllWeaponsMask() { uint32_t m = 0; for (int i = 1; i <= 14; ++i) m |= (1u << (i - 1)); return m; }

void SetupFighter(Fighter& F, int tier, int persona, uint32_t seed, bool candidate) {
  BotProfile p{};
  if (candidate) combat2::AdjustedProfile(tier, persona, seed, "BOT-Cand", &p);
  else BuildProfile(tier, persona, seed, "BOT-Base", &p);
  F.policy.Configure(&p);
  F.tier = tier; F.persona = persona; F.candidate = candidate;
  F.ws2.Configure(p.skill, tier, persona, p.personality.range_preference, seed ^ 0xABCDu);
  F.strafe2.Configure(persona, p.personality.strafe_bias, seed ^ 0x77u);
}

// cover boxes (x1,z1,x2,z2) only used in cover scenario
bool LosBlocked(double ax, double az, double bx, double bz,
                const std::vector<std::array<double, 4>>& boxes) {
  for (auto& b : boxes) {
    // segment vs AABB (slab test)
    double t0 = 0, t1 = 1;
    const double dx = bx - ax, dz = bz - az;
    const double lo[2] = {std::fmin(b[0], b[2]), std::fmin(b[1], b[3])};
    const double hi[2] = {std::fmax(b[0], b[2]), std::fmax(b[1], b[3])};
    const double o[2] = {ax, az}, d[2] = {dx, dz};
    bool ok = true;
    for (int a = 0; a < 2; ++a) {
      if (std::fabs(d[a]) < 1e-9) { if (o[a] < lo[a] || o[a] > hi[a]) { ok = false; break; } }
      else {
        double ta = (lo[a] - o[a]) / d[a], tb = (hi[a] - o[a]) / d[a];
        if (ta > tb) std::swap(ta, tb);
        t0 = std::fmax(t0, ta); t1 = std::fmin(t1, tb);
        if (t0 > t1) { ok = false; break; }
      }
    }
    if (ok && t0 < 0.999) return true;
  }
  return false;
}

DuelResult RunDuel(int tA, int pA, int tB, int pB, bool candA, bool candB, uint32_t seed,
                   double start_dist, double latency_s, double max_s,
                   const std::vector<std::array<double, 4>>& boxes = {},
                   const std::vector<combat2::CoverPoint>& covers = {}) {
  Fighter* A = new Fighter(); Fighter* B = new Fighter();
  SetupFighter(*A, tA, pA, seed ^ 0x1111u, candA);
  SetupFighter(*B, tB, pB, seed ^ 0x2222u, candB);
  A->x = -start_dist / 2; A->z = 0; B->x = start_dist / 2; B->z = 0;
  // facing: yaw with forward=(-sin,-cos): to face +x need -sin=1 => yaw=-90
  A->yaw = -90; B->yaw = 90;
  Fighter* F[2] = {A, B};
  const int lat_ticks = (int)(latency_s / kDt + 0.5);
  // delayed observation ring: store true states per tick
  struct Snap { double x, z, vx, vz, hp; };
  std::vector<Snap> hist[2];
  const int max_ticks = (int)(max_s / kDt);
  DuelResult R; R.f[0] = A; R.f[1] = B;

  for (int tick = 0; tick < max_ticks; ++tick) {
    for (int i = 0; i < 2; ++i) hist[i].push_back({F[i]->x, F[i]->z, F[i]->vx, F[i]->vz, F[i]->hp});
    BotCommand cmds[2];
    for (int i = 0; i < 2; ++i) {
      Fighter& me = *F[i]; Fighter& op = *F[1 - i];
      WorldView w; w.tick = tick; w.alive = me.alive; w.health = me.hp; w.max_health = 100;
      w.usable_weapons = AllWeaponsMask(); w.current_weapon = me.weapon;
      w.pose.x = me.x; w.pose.y = kEyeY; w.pose.z = me.z; w.pose.yaw_deg = me.yaw; w.pose.pitch_deg = me.pitch;
      const int hi2 = tick - lat_ticks >= 0 ? tick - lat_ticks : 0;
      Snap s = hist[1 - i][hi2];
      SenseInput in{}; in.index = 1 - i; in.alive = op.alive;
      in.x = s.x; in.y = kEyeY; in.z = s.z; in.vx = s.vx; in.vy = 0; in.vz = s.vz; in.health = s.hp;
      if (me.candidate && lat_ticks > 0) {
        // Hitscan latency lead at the sense seam (approximation of the
        // aim_point seam): predict the sensed position forward by
        // latency * prediction_gain. Baseline sees the stale position.
        const double g = combat2::LatencyLeadFactor(me.policy.profile().skill);
        in.x += s.vx * latency_s * g; in.z += s.vz * latency_s * g;
      }
      if (me.hp < me.prev_hp) { me.policy.NotifyDamage(me.prev_hp, me.hp); if (me.candidate) me.strafe2.NotifyDamage(tick); }
      me.prev_hp = me.hp;
      me.policy.BeginTick(w);
      bool need[1] = {false};
      me.policy.PlanLosQueries(&in, 1, need);
      bool los[1] = {need[0] && !LosBlocked(me.x, me.z, op.x, op.z, boxes)};
      BotCommand cmd = me.policy.Step(w, &in, los, 1, kDt);

      const double dx = op.x - me.x, dz = op.z - me.z;
      const double dist = std::sqrt(dx * dx + dz * dz);
      if (me.candidate) {
        // weapon override
        const bool has_t = cmd.target >= 0;
        cmd.weapon = me.ws2.Update(w.usable_weapons, dist, has_t, tick);
        if (has_t) {
          const BotProfile& prof = me.policy.profile();
          const double hpf = me.hp / 100.0;
          if (cmd.target_visible && combat2::ShouldRetreat(hpf, prof, 1)) {
            combat2::RetreatPlan rp = combat2::PlanRetreat(
                me.x, me.z, op.x, op.z, covers.data(), (int)covers.size(), me.strafe2.sign());
            // convert world dir to forward/strafe in view space
            const double yr = me.yaw * kDegToRad;
            const double fx = -std::sin(yr), fz = -std::cos(yr);
            const double rx = std::cos(yr), rz = -std::sin(yr);
            cmd.forward = combat2::Clamp(rp.dir_x * fx + rp.dir_z * fz, -1, 1);
            cmd.strafe = combat2::Clamp(rp.dir_x * rx + rp.dir_z * rz, -1, 1);
            ++me.retreat_ticks;
          } else {
            const double pref = combat2::DesiredRange2(cmd.weapon, prof);
            const double tol = combat2::StyleFor(me.persona).band_tolerance_m;
            const int mode = dist > pref + tol ? 0 : (dist < pref - tol ? 2 : 1);
            if (mode == 0) cmd.forward = combat2::Clamp(0.55 + 0.45 * botcore::EffectiveAggression(prof, tick), -1, 1);
            else if (mode == 2) cmd.forward = -0.6;
            else cmd.forward = 0.0;
            cmd.strafe = me.strafe2.Step(tick, mode);
          }
        }
      } else {
        cmd.strafe = 0.0;  // shipped default bot_fStrafeScale=0 (patch 0008)
        if (cmd.forward < -0.5 && cmd.target >= 0) ++me.retreat_ticks;
      }
      cmds[i] = cmd;
      me.weapon = cmd.weapon > 0 ? cmd.weapon : me.weapon;
      if (me.prev_weapon != -1 && me.weapon != me.prev_weapon) ++me.weapon_switches;
      me.prev_weapon = me.weapon;
      if (me.weapon >= 1 && me.weapon <= 14) ++me.weapon_ticks[me.weapon];
      if (cmd.target >= 0) { me.range_sum += dist; ++me.range_n; }
    }
    // apply movement + combat
    for (int i = 0; i < 2; ++i) {
      Fighter& me = *F[i]; Fighter& op = *F[1 - i];
      BotCommand& cmd = cmds[i];
      if (!me.alive) continue;
      me.yaw += cmd.yaw_delta_deg; me.pitch += cmd.pitch_delta_deg;
      const double yr = me.yaw * kDegToRad;
      const double fx = -std::sin(yr), fz = -std::cos(yr);
      const double rx = std::cos(yr), rz = -std::sin(yr);
      double mx = fx * cmd.forward + rx * cmd.strafe;
      double mz = fz * cmd.forward + rz * cmd.strafe;
      const double ml = std::sqrt(mx * mx + mz * mz);
      if (ml > 1.0) { mx /= ml; mz /= ml; }
      me.vx = mx * kMaxSpeed; me.vz = mz * kMaxSpeed;
      me.x += me.vx * kDt; me.z += me.vz * kDt;
      me.x = combat2::Clamp(me.x, -70, 70); me.z = combat2::Clamp(me.z, -70, 70);
      if (std::fabs(cmd.strafe) > 0.25 && cmd.target >= 0) ++me.strafe_ticks;
      me.fire_cooldown -= kDt;
      if (cmd.fire && cmd.target_visible) {
        ++me.fire_ticks;
        if (me.first_fire_tick < 0) me.first_fire_tick = tick;
        const SimWeapon& sw = SW(me.weapon);
        if (me.fire_cooldown <= 0) {
          me.fire_cooldown = sw.interval_s;
          ++me.shots;
          // true angular error of crosshair vs opponent NOW
          const double dx = op.x - me.x, dz = op.z - me.z;
          const double dist = std::sqrt(dx * dx + dz * dz);
          const double want_yaw = std::atan2(-dx, -dz) * kRadToDeg;
          double ey = AimController::WrapDeg(want_yaw - me.yaw);
          double err = std::fabs(ey);
          me.aim_err_sum += err; ++me.aim_err_n;
          if (dist <= sw.max_range) {
            const double tol_direct = std::atan2(0.45, dist > 0.5 ? dist : 0.5) * kRadToDeg * sw.tol_mult;
            double tol = tol_direct;
            double dmg = 0;
            if (IsShotgun(me.weapon)) {
              const double frac = combat2::Clamp(1.6 * tol / (err + 0.15 * tol), 0.0, 1.0);
              const double range_frac = combat2::Clamp(1.3 - dist / 22.0, 0.05, 1.0);
              dmg = sw.dmg * frac * range_frac;
              if (frac > 0.25) ++me.hits;
            } else if (err <= tol_direct) {
              dmg = sw.dmg; ++me.hits;
              if (sw.splash_tol > 0 && dist < 7.0) me.hp -= sw.dmg * 0.35;  // self blast
            } else if (sw.splash_tol > 0 && err <= tol_direct * sw.splash_tol) {
              dmg = sw.dmg * 0.35;  // splash partial, not a direct-hit count
            }
            if (dmg > 0) { op.hp -= dmg; me.dmg_dealt += dmg; }
          }
        }
      }
    }
    for (int i = 0; i < 2; ++i) if (F[i]->hp <= 0 && F[i]->alive) F[i]->alive = false;
    if (!A->alive || !B->alive) {
      R.winner = A->alive ? 0 : (B->alive ? 1 : -1);
      R.duration_s = (tick + 1) * kDt;
      return R;
    }
  }
  R.winner = -1; R.duration_s = max_s;
  return R;
}

__attribute__((unused)) void PrintFighterJson(const char* key, Fighter& F) {
  std::printf("\"%s\":{\"shots\":%ld,\"hits\":%ld,\"hitrate\":%.4f,\"dmg\":%.1f,\"fire_ticks\":%ld,"
              "\"first_fire_s\":%.2f,\"strafe_ticks\":%ld,\"retreat_ticks\":%ld,\"wswitches\":%d,"
              "\"mean_range\":%.2f,\"mean_aim_err_deg\":%.3f,\"weapons\":{",
              key, F.shots, F.hits, F.shots ? (double)F.hits / F.shots : 0.0, F.dmg_dealt,
              F.fire_ticks, F.first_fire_tick >= 0 ? F.first_fire_tick * kDt : -1.0,
              F.strafe_ticks, F.retreat_ticks, F.weapon_switches,
              F.range_n ? F.range_sum / F.range_n : 0.0,
              F.aim_err_n ? F.aim_err_sum / F.aim_err_n : 0.0);
  bool first = true;
  for (int i = 1; i <= 14; ++i) if (F.weapon_ticks[i] > 0) {
    std::printf("%s\"%s\":%ld", first ? "" : ",", WeaponName(i), F.weapon_ticks[i]); first = false;
  }
  std::printf("}}");
}

int Battery(const char* policy_name, bool candidate, int seeds) {
  std::printf("{\"policy\":\"%s\",\"seeds_per_cell\":%d,\"duels\":[\n", policy_name, seeds);
  bool first = true;
  auto cell = [&](const char* kind, int tA, int pA, int tB, int pB, double dist, double lat, bool cross = false) {
    int wA = 0, wB = 0, draws = 0; double dur = 0, hrA = 0, hrB = 0, ffA = 0;
    long strafeA = 0, wtA[15] = {0}, wtB[15] = {0}; double aeA = 0; int aen = 0;
    double rangeA = 0; int rn = 0;
    for (int s = 0; s < seeds; ++s) {
      DuelResult R = RunDuel(tA, pA, tB, pB, candidate, cross ? false : candidate, 0xC0FFEEu + (uint32_t)s * 977u, dist, lat, 45.0);
      if (R.winner == 0) ++wA; else if (R.winner == 1) ++wB; else ++draws;
      dur += R.duration_s;
      hrA += R.f[0]->shots ? (double)R.f[0]->hits / R.f[0]->shots : 0;
      hrB += R.f[1]->shots ? (double)R.f[1]->hits / R.f[1]->shots : 0;
      ffA += R.f[0]->first_fire_tick >= 0 ? R.f[0]->first_fire_tick * kDt : 45.0;
      strafeA += R.f[0]->strafe_ticks;
      if (R.f[0]->range_n) { rangeA += R.f[0]->range_sum / R.f[0]->range_n; ++rn; }
      if (R.f[0]->aim_err_n) { aeA += R.f[0]->aim_err_sum / R.f[0]->aim_err_n; ++aen; }
      for (int i = 1; i <= 14; ++i) { wtA[i] += R.f[0]->weapon_ticks[i]; wtB[i] += R.f[1]->weapon_ticks[i]; }
      delete R.f[0]; delete R.f[1];
    }
    std::printf("%s{\"kind\":\"%s\",\"tA\":%d,\"pA\":%d,\"tB\":%d,\"pB\":%d,\"dist\":%.0f,\"lat_ms\":%.0f,"
                "\"winA\":%d,\"winB\":%d,\"draws\":%d,\"mean_duration_s\":%.2f,\"hitrateA\":%.4f,\"hitrateB\":%.4f,"
                "\"first_fireA_s\":%.2f,\"strafe_ticksA\":%ld,\"mean_rangeA\":%.2f,\"aim_errA_deg\":%.3f,\"weaponsA\":{",
                first ? "" : ",\n", kind, tA, pA, tB, pB, dist, lat * 1000, wA, wB, draws,
                dur / seeds, hrA / seeds, hrB / seeds, ffA / seeds, strafeA / seeds,
                rn ? rangeA / rn : 0.0, aen ? aeA / aen : 0.0);
    first = false;
    bool fw = true;
    for (int i = 1; i <= 14; ++i) if (wtA[i] > 0) { std::printf("%s\"%s\":%ld", fw ? "" : ",", WeaponName(i), wtA[i]); fw = false; }
    std::printf("},\"weaponsB\":{");
    fw = true;
    for (int i = 1; i <= 14; ++i) if (wtB[i] > 0) { std::printf("%s\"%s\":%ld", fw ? "" : ",", WeaponName(i), wtB[i]); fw = false; }
    std::printf("}}");
  };
  for (int t = 1; t <= 5; ++t) cell("mirror", t, 2, t, 2, 18, 0.0);            // duelist mirrors
  for (int t = 1; t <= 4; ++t) cell("ladder", t + 1, 2, t, 2, 18, 0.0);        // adjacent tiers
  cell("ladder", 5, 2, 1, 2, 18, 0.0);
  for (int p = 0; p < 6; ++p) cell("persona", 3, p, 3, 2, 18, 0.0);            // persona vs duelist ref
  cell("latency", 5, 2, 3, 2, 18, 0.0);
  cell("latency", 5, 2, 3, 2, 18, 0.10);
  cell("latency", 5, 2, 3, 2, 18, 0.20);
  cell("range", 3, 0, 3, 4, 45, 0.0);                                          // aggressor vs marksman, far
  cell("range", 3, 0, 3, 4, 8, 0.0);                                           // ... close
  if (candidate) {  // head-to-head: candidate (A) vs baseline (B)
    for (int t = 1; t <= 5; ++t) cell("cross", t, 2, t, 2, 18, 0.0, true);
    cell("cross", 3, 0, 3, 0, 10, 0.0, true);
    cell("cross", 3, 4, 3, 4, 40, 0.0, true);
  }
  std::printf("\n]}\n");
  return 0;
}

// F-3 probe: hitscan shooter vs scripted lateral mover (18 m, sinusoidal,
// ~5 m/s peak lateral). Duel bots mostly move along the sightline, so the
// latency effect needs this dedicated probe (same logic as PR #62).
int MoverTest() {
  std::printf("policy,tier,lat_ms,shots,hits,hitrate\n");
  for (int cand = 0; cand < 2; ++cand) {
    for (int tier : {3, 5}) {
      for (double lat : {0.0, 0.10, 0.20}) {
        Fighter F; SetupFighter(F, tier, 2, 4242, cand == 1);
        F.x = 0; F.z = 0; F.yaw = -90;
        const int lat_ticks = (int)(lat / kDt + 0.5);
        struct S2 { double x, z, vx, vz; };
        std::vector<S2> hist;
        const uint32_t mask = (1u << 11) | (1u << 5);  // laser + tommygun only
        for (int tick = 0; tick < 600; ++tick) {
          const double t = tick * kDt;
          const double tx = 18.0, tz = 9.0 * std::sin(0.55 * t);
          const double tvz = 9.0 * 0.55 * std::cos(0.55 * t);
          hist.push_back({tx, tz, 0.0, tvz});
          S2 s = hist[tick - lat_ticks >= 0 ? tick - lat_ticks : 0];
          WorldView w; w.tick = tick; w.alive = true; w.health = 100; w.usable_weapons = mask;
          w.current_weapon = F.weapon; w.pose.x = F.x; w.pose.y = kEyeY; w.pose.z = F.z;
          w.pose.yaw_deg = F.yaw; w.pose.pitch_deg = 0;
          SenseInput in{}; in.index = 1; in.alive = true; in.x = s.x; in.y = kEyeY; in.z = s.z;
          in.vx = s.vx; in.vy = 0; in.vz = s.vz; in.health = 100;
          if (cand && lat_ticks > 0) {
            const double g = combat2::LatencyLeadFactor(F.policy.profile().skill);
            in.x += s.vx * lat * g; in.z += s.vz * lat * g;
          }
          F.policy.BeginTick(w);
          bool need[1] = {false}; F.policy.PlanLosQueries(&in, 1, need);
          bool los[1] = {need[0]};
          BotCommand cmd = F.policy.Step(w, &in, los, 1, kDt);
          if (cand) cmd.weapon = F.ws2.Update(mask, 18.0, cmd.target >= 0, tick);
          F.weapon = cmd.weapon > 0 ? cmd.weapon : F.weapon;
          F.yaw += cmd.yaw_delta_deg;
          F.fire_cooldown -= kDt;
          if (cmd.fire && cmd.target_visible && F.fire_cooldown <= 0) {
            const SimWeapon& sw = SW(F.weapon);
            F.fire_cooldown = sw.interval_s; ++F.shots;
            const double want = std::atan2(-(tx - F.x), -(tz - F.z)) * kRadToDeg;
            const double err = std::fabs(AimController::WrapDeg(want - F.yaw));
            const double tol = std::atan2(0.45, 18.0) * kRadToDeg * sw.tol_mult;
            if (err <= tol) ++F.hits;
          }
        }
        std::printf("%s,%d,%.0f,%ld,%ld,%.4f\n", cand ? "candidate" : "baseline", tier,
                    lat * 1000, F.shots, F.hits, F.shots ? (double)F.hits / F.shots : 0.0);
      }
    }
  }
  return 0;
}

int CoverTest() {
  // One low-HP bot retreats from a static threat, cover box nearby.
  // Measure ticks until LOS breaks (baseline backpedal vs candidate plan),
  // executed through the duel sim with boxes + cover points.
  // Cover is offset laterally: straight back-pedal (baseline) stays exposed,
  // only a cover-directed retreat breaks the sightline.
  std::vector<std::array<double, 4>> boxes = {{{-16, 7, -11, 13}}};
  std::vector<combat2::CoverPoint> covers = {{{-19, 10, true}, {6, -14, false}}};
  for (int cand = 0; cand < 2; ++cand) {
    double break_s = -1;
    // custom mini-run: reuse duel but measure via duration of visibility is not
    // exposed; instead directly simulate retreat kinematics with each plan.
    double x = 0, z = 0; const double tx = 12, tz = 0;
    combat2::StrafeController sc; sc.Configure(1, 0.7, 42);
    for (int tick = 0; tick < 400; ++tick) {
      double dx, dz;
      if (cand) {
        auto rp = combat2::PlanRetreat(x, z, tx, tz, covers.data(), 1, sc.sign());
        dx = rp.dir_x; dz = rp.dir_z;
      } else { dx = -1; dz = 0; /* baseline: straight back along view */ }
      x += dx * kMaxSpeed * kDt; z += dz * kMaxSpeed * kDt;
      if (LosBlocked(x, z, tx, tz, boxes)) { break_s = (tick + 1) * kDt; break; }
    }
    std::printf("%s los_break_s=%.2f final=(%.1f,%.1f)\n", cand ? "candidate" : "baseline ", break_s, x, z);
  }
  return 0;
}

int Bench(bool candidate) {
  Fighter F; SetupFighter(F, 3, 2, 12345, candidate);
  WorldView w; w.alive = true; w.health = 100; w.usable_weapons = AllWeaponsMask(); w.current_weapon = 6;
  SenseInput in{}; in.index = 1; in.alive = true; in.x = 15; in.y = kEyeY; in.z = 0; in.health = 100;
  bool need[1], los[1] = {true};
  const int N = 200000;
  auto t0 = std::chrono::steady_clock::now();
  double sink = 0;
  for (int i = 0; i < N; ++i) {
    w.tick = i; w.pose.yaw_deg = -90 + (i % 7);
    F.policy.BeginTick(w);
    F.policy.PlanLosQueries(&in, 1, need);
    BotCommand c = F.policy.Step(w, &in, los, 1, kDt);
    if (candidate) {
      c.weapon = F.ws2.Update(w.usable_weapons, 15.0, true, i);
      c.strafe = F.strafe2.Step(i, 1);
    }
    sink += c.yaw_delta_deg + c.weapon;
  }
  auto t1 = std::chrono::steady_clock::now();
  double us = std::chrono::duration<double, std::micro>(t1 - t0).count() / N;
  std::printf("%s policy+overlay: %.3f us/tick (sink=%.1f) -> %.4f%% of one core @20Hz/bot\n",
              candidate ? "candidate" : "baseline ", us, sink, us * 20 / 10000.0);
  return 0;
}

}  // namespace

int main(int argc, char** argv) {
  std::string mode = argc > 1 ? argv[1] : "--battery";
  int seeds = argc > 2 ? std::atoi(argv[2]) : 8;
  if (mode == "--battery") { std::printf("[\n"); Battery("baseline", false, seeds); std::printf(",\n"); Battery("candidate", true, seeds); std::printf("]\n"); return 0; }
  if (mode == "--cover") return CoverTest();
  if (mode == "--mover") return MoverTest();
  if (mode == "--bench") { Bench(false); Bench(true); return 0; }
  if (mode == "--weapon-curve") {
    uint32_t all = AllWeaponsMask();
    std::printf("dist | baseline rp -0.55/0/+0.85 | candidate aggressor/duelist/marksman\n");
    for (double d = 2; d <= 70; d += 2) {
      std::printf("%4.0f | %-14s %-14s %-14s | %-14s %-14s %-14s\n", d,
                  WeaponName(BestWeapon(all, d, -0.55)), WeaponName(BestWeapon(all, d, 0.0)),
                  WeaponName(BestWeapon(all, d, 0.85)),
                  WeaponName(combat2::BestWeapon2(all, d, 0, -0.55)),
                  WeaponName(combat2::BestWeapon2(all, d, 2, 0.0)),
                  WeaponName(combat2::BestWeapon2(all, d, 4, 0.85)));
    }
    return 0;
  }
  std::fprintf(stderr, "usage: --battery [seeds] | --cover | --bench | --weapon-curve\n");
  return 2;
}
