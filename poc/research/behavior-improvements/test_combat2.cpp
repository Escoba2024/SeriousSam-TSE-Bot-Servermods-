// test_combat2.cpp - deterministic unit tests for combat2 overlays.
#include <cmath>
#include <cstdio>
#include <set>

#include "bot_loadout.h"
#include "combat2_profile.h"
#include "combat2_tactics.h"
#include "combat2_weapon.h"

using namespace botcore;
using namespace combat2;

static int g_fail = 0, g_n = 0;
#define CHECK(cond) do { ++g_n; if (!(cond)) { std::printf("FAIL %s:%d %s\n", __FILE__, __LINE__, #cond); ++g_fail; } } while (0)

static uint32_t AllMask() { uint32_t m = 0; for (int i = 1; i <= 14; ++i) m |= (1u << (i - 1)); return m; }

int main() {
  const uint32_t all = AllMask();

  /* --- F-1 weapon niches + persona divergence --- */
  {
    std::set<int> base_tops, cand_tops;
    int differ = 0, samples = 0;
    for (double d = 2; d <= 70; d += 2) {
      base_tops.insert(BestWeapon(all, d, 0.0));
      cand_tops.insert(BestWeapon2(all, d, 2, 0.0, nullptr, 3));
      if (BestWeapon2(all, d, 0, -0.55, nullptr, 3) != BestWeapon2(all, d, 4, 0.85, nullptr, 3)) ++differ;
      ++samples;
    }
    CHECK(base_tops.size() <= 3);          // baseline defect reproduced (laser+cannon+dshot)
    CHECK(cand_tops.size() >= 6);          // niches
    CHECK(differ * 5 >= samples * 2);      // personas differ at >=40% (baseline: 0%)
    CHECK(BestWeapon2(all, 6, 0, -0.55, nullptr, 3) == 5);   // aggressor close: double shotgun
    CHECK(BestWeapon2(all, 70, 4, 0.85, nullptr, 5) == 13);  // expert marksman far: sniper
    // self-blast veto: no rocket/cannon point blank as top pick
    int close = BestWeapon2(all, 5, 2, 0.0, nullptr, 5);
    CHECK(close != 8 && close != 9 && close != 14);
    // skill gating: tier-1 marksman must not top-pick sniper at 40 m, tier-5 may at 70 m
    CHECK(BestWeapon2(all, 40, 4, 0.85, nullptr, 1) != 13);
  }

  /* --- selector hysteresis: no per-tick flicker near a boundary --- */
  {
    WeaponSelector2 ws; ws.Configure(SkillFor(3), 3, 2, 0.0, 99);
    int switches = 0, prev = -1;
    for (int t = 0; t < 400; ++t) {
      double d = 13.0 + ((t % 2) ? 1.2 : -1.2);  // oscillate across niche boundary
      int w = ws.Update(all, d, true, t);
      if (prev != -1 && w != prev) ++switches;
      prev = w;
    }
    CHECK(switches <= 6);
    CHECK(SuboptimalPickP(5) == 0.0 && SuboptimalPickP(1) > SuboptimalPickP(3));
  }

  /* --- F-2/skill curve: monotonic, beginner compressed, expert unchanged --- */
  {
    for (int t = 1; t < 5; ++t) {
      CHECK(AdjustedSkill(t).aim_sigma_deg > AdjustedSkill(t + 1).aim_sigma_deg);
      CHECK(AdjustedSkill(t).reaction_s >= AdjustedSkill(t + 1).reaction_s);
      CHECK(AdjustedSkill(t).prediction_gain < AdjustedSkill(t + 1).prediction_gain);
      CHECK(AdjustedSkill(t).fire_tol_deg >= AdjustedSkill(t + 1).fire_tol_deg);
    }
    CHECK(AdjustedSkill(1).aim_sigma_deg < SkillFor(1).aim_sigma_deg);
    CHECK(std::fabs(AdjustedSkill(5).aim_sigma_deg - SkillFor(5).aim_sigma_deg) < 1e-9);
    // persona orthogonality: identical skill for all personas of a tier
    BotProfile a{}, b{};
    CHECK(AdjustedProfile(3, 0, 7, "A", &a) && AdjustedProfile(3, 4, 7, "B", &b));
    CHECK(a.skill.aim_sigma_deg == b.skill.aim_sigma_deg &&
          a.skill.reaction_s == b.skill.reaction_s &&
          a.skill.prediction_gain == b.skill.prediction_gain);
    // adjusted profiles still pass botcore validation for the full grid
    for (int t = 1; t <= 5; ++t) for (int p = 0; p < 6; ++p) {
      BotProfile pr{}; CHECK(AdjustedProfile(t, p, 123 + t, "X", &pr));
    }
  }

  /* --- F-7 target priority --- */
  {
    CombatStyle st = StyleFor(2);
    // current target far (25 m, full hp); new visible threat at 5 m -> override
    TargetCandidate c[2] = {};
    c[0].index = 1; c[0].distance_m = 25; c[0].visible_now = true; c[0].confidence = 1;
    c[1].index = 2; c[1].distance_m = 5; c[1].visible_now = true; c[1].confidence = 1;
    CHECK(ChooseTarget2(c, 2, st, 1) == 2);
    // damager at 15 m pre-empts a farther current target
    c[1].distance_m = 15; c[1].damaged_me_recently = true;
    CHECK(ChooseTarget2(c, 2, st, 1) == 2);
    // without danger, stickiness keeps current vs slightly closer equal threat
    c[1].damaged_me_recently = false; c[1].distance_m = 22;
    CHECK(ChooseTarget2(c, 2, st, 1) == 1);
    // finish bonus: aggressor prefers 10%-hp target at equal distance (no current)
    CombatStyle agg = StyleFor(0);
    c[0].distance_m = 20; c[0].health_frac = 1.0;
    c[1].distance_m = 20; c[1].health_frac = 0.1; c[1].damaged_me_recently = false;
    CHECK(ChooseTarget2(c, 2, agg, -1) == 2);
    // invisible + forgotten candidates are never chosen
    c[1].visible_now = false; c[1].confidence = 0.2;
    CHECK(ChooseTarget2(c, 2, agg, -1) == 1);
  }

  /* --- F-3 latency lead + projectile lead --- */
  {
    double e0 = LatencyAngularErrorDeg(5.0, 18.0, 0.20, 0.0);
    double e1 = LatencyAngularErrorDeg(5.0, 18.0, 0.20, LatencyLeadFactor(AdjustedSkill(5)));
    CHECK(e0 > 3.0 && e1 < e0 * 0.2);
    double e_low = LatencyAngularErrorDeg(5.0, 18.0, 0.20, LatencyLeadFactor(AdjustedSkill(1)));
    CHECK(e_low > e1);  // weaker tier compensates less - monotonic competence
    CHECK(ProjectileLeadTime(30, 4, 20) > 30.0 / 20.0);   // opening target needs more lead
    CHECK(ProjectileLeadTime(30, -4, 20) < 30.0 / 20.0);  // closing target less
  }

  /* --- F-8 alert cone cap + reaction floor; F-6 bidirectional search --- */
  {
    for (int t = 1; t <= 5; ++t) {
      CHECK(AlertHalfAngleDeg(AdjustedSkill(t)) <= 125.0);
      CHECK(AlertReactionTicks(AdjustedSkill(t)) >= 2);
      CHECK(!AlertGatePasses(170.0, AdjustedSkill(t)));  // behind: never alert-visible
    }
    bool saw_pos = false, saw_neg = false;
    for (int tick = 0; tick < 2000; tick += 25) {
      double d = SearchYawDeltaDeg(AdjustedSkill(3), tick, 12345u, 0.05);
      if (d > 0) saw_pos = true; else if (d < 0) saw_neg = true;
    }
    CHECK(saw_pos && saw_neg);
  }

  /* --- F-5 strafe controller --- */
  {
    StrafeController sc; sc.Configure(2, 0.95, 777);
    double first = sc.Step(0, 1);
    CHECK(std::fabs(first) > 0.5);
    bool flipped = false;
    for (int t = 1; t < 200; ++t) if (sc.Step(t, 1) * first < 0) flipped = true;
    CHECK(flipped && sc.flips() >= 2);
    double before = sc.sign(); sc.NotifyDamage(300);
    CHECK(sc.sign() == -before);  // dodge flip on damage
    StrafeController duelist, marksman;
    duelist.Configure(2, 1.0, 5); marksman.Configure(4, 1.0, 5);
    for (int t = 0; t < 600; ++t) { duelist.Step(t, 1); marksman.Step(t, 1); }
    CHECK(duelist.flips() > marksman.flips());  // persona rhythm differs
    CHECK(StrafeFireTolMult(1, 1.0) > StrafeFireTolMult(5, 1.0));
    CHECK(StrafeFireTolMult(5, 1.0) == 1.0);
  }

  /* --- F-4 retreat + cover --- */
  {
    CoverPoint covers[2] = {{-19, 10, true}, {6, -14, false}};
    RetreatPlan rp = PlanRetreat(0, 0, 12, 0, covers, 2, 1.0);
    CHECK(rp.cover_index == 0);
    CHECK(rp.dir_x < 0 && rp.dir_z > 0.2);  // toward offset cover, not straight back
    RetreatPlan open = PlanRetreat(0, 0, 12, 0, nullptr, 0, 1.0);
    CHECK(open.cover_index == -1 && open.dir_x < 0 && std::fabs(open.dir_z) > 0.3);  // zig-zag
    BotProfile agg{}, sur{};
    AdjustedProfile(3, 0, 3, "A", &agg); AdjustedProfile(3, 1, 3, "S", &sur);
    // survivor retreats at a health level where aggressor still fights
    bool found = false;
    for (double h = 0.1; h < 0.9; h += 0.01)
      if (ShouldRetreat(h, sur, 1) && !ShouldRetreat(h, agg, 1)) found = true;
    CHECK(found);
    CHECK(ShouldRetreat(0.5, agg, 2) || !ShouldRetreat(0.5, agg, 1));  // outnumbered shifts threshold (monotone)
    double thr1 = 0, thr2 = 0;
    for (double h = 0.01; h < 1.0; h += 0.01) { if (!ShouldRetreat(h, agg, 1) && thr1 == 0) thr1 = h; if (!ShouldRetreat(h, agg, 2) && thr2 == 0) thr2 = h; }
    CHECK(thr2 >= thr1);
  }

  /* --- respawn plan --- */
  {
    for (int t = 1; t < 5; ++t)
      CHECK(PlanRespawn(t, 2, 9, 0).press_delay_ticks > PlanRespawn(t + 1, 2, 9, 0).press_delay_ticks);
    CHECK(PlanRespawn(5, 2, 9, 0).press_delay_ticks >= 4);          // never instant
    CHECK(PlanRespawn(3, 1, 9, 0).press_delay_ticks > PlanRespawn(3, 0, 9, 0).press_delay_ticks);
    RespawnPlan2 r1 = PlanRespawn(3, 2, 9, 1), r2 = PlanRespawn(3, 2, 9, 2);
    CHECK(r1.scan_yaw_deg != r2.scan_yaw_deg);                        // seeded variety
    CHECK(r1.weapon_ready_tick > r1.press_delay_ticks);
  }

  /* --- desired range coherence --- */
  {
    BotProfile agg{}, mk{};
    AdjustedProfile(3, 0, 3, "A", &agg); AdjustedProfile(3, 4, 3, "M", &mk);
    CHECK(DesiredRange2(5, agg) < DesiredRange2(13, mk));       // shotgun close, sniper far
    CHECK(DesiredRange2(12, agg) < DesiredRange2(12, mk));      // same weapon, persona shifts band
    BotProfile beg{}, exp{};
    AdjustedProfile(1, 2, 3, "B", &beg); AdjustedProfile(5, 2, 3, "E", &exp);
    CHECK(DesiredRange2(7, beg) < DesiredRange2(7, exp));      // beginner comfort range closer
  }

  std::printf("COMBAT2 TESTS: %d checks, %d failures -> %s\n", g_n, g_fail, g_fail ? "FAIL" : "PASS");
  return g_fail ? 1 : 0;
}
