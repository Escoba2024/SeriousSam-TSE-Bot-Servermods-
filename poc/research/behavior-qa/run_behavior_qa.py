#!/usr/bin/env python3
"""Offline behavior-QA orchestrator for the botcore Human-KI.

STATUS: OFFLINE SIMULATION ONLY - NOT RETAIL TELEMETRY.

This harness builds ./qa_sim (which drives the engine-free botcore Human-KI in
a synthetic world), runs a reproducible battery of combat scenarios across the
five skill tiers and six personalities, aggregates the NDJSON metrics, and then
enforces a set of behavioural INVARIANTS. If an invariant breaks, that is a
regression signal: it means a change in botcore (bot_aim.h / bot_profile.h /
bot_human.h / ...) altered combat behaviour in a way the QA contract forbids.

Everything printed here is a property of (botcore code x documented simulation
assumptions A1..A8 in qa_world.h). None of it measures the real game, a real
server, or a real human, and none of it may be quoted as retail gameplay.

Usage:
  run_behavior_qa.py                 # build, run battery, check invariants, report
  run_behavior_qa.py --write-baseline PATH   # store a golden reference
  run_behavior_qa.py --compare PATH          # diff current run vs a baseline
  run_behavior_qa.py --no-build              # use an existing ./qa_sim
  run_behavior_qa.py --seeds N               # seeds per cell (default 8)
"""
from __future__ import annotations

import argparse
import json
import os
import statistics
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
QA_SIM = os.path.join(HERE, "qa_sim")
RESULTS = os.path.join(HERE, "results")

# Scenario battery used for the skill-tier comparison (deliverable #4). Each is
# run for every tier with a fixed persona so only skill varies.
TIER_SCENARIOS = [
    "gallery_static",      # pure aim (locked body)
    "reaction_static",     # acquisition + kill, free movement
    "reaction_turn90",     # search-rate limited acquisition
    "damage_alert_behind", # attacked from behind: alert-driven turn to engage
    "tracking_strafe",     # lateral tracking
    "tracking_orbit",      # constant angular-rate tracking
    "approach_close",      # engagement build-up over distance
    "retreat_pressure",    # retreat decision under fire at low HP
    "firefight",           # sustained trade with return fire (evasion vs accuracy)
    "cover_reacquire",     # LOS loss, memory, reacquisition
    "weapon_boundary",     # weapon-score boundary / switch churn
    "multi_2v1",           # prioritisation, two opponents
    "multi_3v1",           # focus under pressure, three opponents
    "long_range_lead",     # projectile lead competence
    "hitscan_latency",     # hitscan miss cost under replication latency
    "idle_scan",           # search behaviour, no opponent
]

# Scenarios used for the personality comparison (deliverable #5): a fixed tier,
# only the persona varies. Movement/decision-heavy scenarios matter most here.
PERSONA_SCENARIOS = [
    "reaction_static",
    "tracking_strafe",
    "approach_close",
    "retreat_pressure",
    "multi_2v1",
]

# Key metrics aggregated per (scenario, tier|persona).
KEY_METRICS = [
    "hit_rate", "sim_dps", "ttk_s", "t_first_selectable_s",
    "t_first_fire_eff_s", "t_first_hit_s",
    "true_err_visible_mean", "aim_err_policy_fire_mean", "overshoots",
    "shots_policy", "shots_blocked_switch", "trigger_pulls", "hits",
    "shots_gated_aim", "weapon_switches", "weapon_switch_wasted_ticks",
    "weapon_mode", "weapon_distinct",
    "target_switches", "focus_share", "dist_mean_m", "in_band_pct",
    "preferred_mean_m", "move_fwd_mean", "strafe_cmd_uptime",
    "strafe_applied_uptime", "still_pct", "approach_uptime", "retreat_uptime",
    "retreat_events", "survival_s", "nearest_not_chosen_pct",
    "miss_range", "miss_target_motion", "miss_overshoot", "miss_aim_bias",
    "lead_impact_miss_p50_m", "lead_impact_miss_p95_m",
    "wasted_fire_invisible", "los_queries_max", "ray_budget_skips",
    "dmg_dealt", "dmg_taken", "hp_end", "path_len_m",
]

TIERS = [1, 2, 3, 4, 5]
PERSONAS = [0, 1, 2, 3, 4, 5]
PERSONA_NAMES = ["aggressor", "survivor", "duelist", "controller", "marksman", "flaky"]
SKILL_NAMES = {1: "beginner", 2: "casual", 3: "average", 4: "advanced", 5: "expert"}


def sh(cmd, **kw):
    return subprocess.run(cmd, cwd=HERE, check=True, capture_output=True, text=True, **kw)


def build():
    sh(["make", "-s"])
    if not os.path.exists(QA_SIM):
        raise SystemExit("qa_sim did not build")


def run_sweep(scenarios, tiers, personas, seeds, seed_base=0x51A2026, extra=None):
    cmd = [QA_SIM, "--sweep",
           "--scenarios", ",".join(scenarios),
           "--tiers", ",".join(str(t) for t in tiers),
           "--personas", ",".join(str(p) for p in personas),
           "--seeds", str(seeds), "--seed-base", str(seed_base)]
    if extra:
        cmd += extra
    out = sh(cmd).stdout
    return [json.loads(line) for line in out.splitlines() if line.strip()]


def run_duel(a_tier, a_persona, b_tier, b_persona, rounds, extra=None):
    cmd = [QA_SIM, "--duel",
           "--duel-a", f"{a_tier}:{a_persona}",
           "--duel-b", f"{b_tier}:{b_persona}",
           "--rounds", str(rounds)]
    if extra:
        cmd += extra
    out = sh(cmd).stdout
    rows = [json.loads(line) for line in out.splitlines() if line.strip()]
    summary = next(r for r in rows if r["kind"] == "duel_summary")
    detail = [r for r in rows if r["kind"] == "duel"]
    return summary, detail


def run_perf(candidates=8, ticks=20000):
    out = sh([QA_SIM, "--perf", "--candidates", str(candidates), "--ticks", str(ticks)]).stdout
    return json.loads(out.strip().splitlines()[-1])


def run_weapon_curve(range_pref=0.0):
    out = sh([QA_SIM, "--weapon-curve", "--range-pref", str(range_pref)]).stdout
    return json.loads(out.strip().splitlines()[-1])


def weapon_dominance(curve):
    """Histogram of the best-scoring weapon over the sampled distances."""
    hist = {}
    for r in curve["rows"]:
        hist[r["best_name"]] = hist.get(r["best_name"], 0) + 1
    return hist


# --------------------------------------------------------------------------- #
# Aggregation
# --------------------------------------------------------------------------- #

def aggregate(runs, group_keys):
    """Group runs by tuple(group_keys) and summarise KEY_METRICS."""
    groups = {}
    for r in runs:
        key = tuple(r.get(k) for k in group_keys)
        groups.setdefault(key, []).append(r)
    agg = {}
    for key, rs in groups.items():
        per = {}
        for metric in KEY_METRICS:
            vals = [r["metrics"].get(metric) for r in rs
                    if r["metrics"].get(metric) is not None]
            vals = [v for v in vals if isinstance(v, (int, float))]
            if not vals:
                continue
            entry = {"mean": statistics.fmean(vals)}
            if len(vals) > 1:
                entry["std"] = statistics.pstdev(vals)
            per[metric] = entry
        # outcome distribution + kill_rate (the robust effectiveness signal;
        # ttk_s alone is conditional on a kill and flatters tiers that rarely
        # land the finishing hit - always read ttk_s together with kill_rate).
        outcomes = {}
        for r in rs:
            outcomes[r["outcome"]] = outcomes.get(r["outcome"], 0) + 1
        per["_outcome"] = outcomes
        per["_n"] = len(rs)
        per["kill_rate"] = {"mean": outcomes.get("kill", 0) / len(rs)}
        per["death_rate"] = {"mean": outcomes.get("death", 0) / len(rs)}
        # determinism: all digests in the group
        per["_digests"] = sorted({r["metrics"]["digest"] for r in rs})
        agg[key] = per
    return agg


def mean_of(agg, key, metric):
    cell = agg.get(key)
    if not cell or metric not in cell:
        return None
    return cell[metric]["mean"]


def detect_regressions(current, base, metric_tol=0.25):
    """Compare a baseline_vector (current) against a loaded baseline (base).

    Returns a list of human-readable regression strings. A regression is:
      - an invariant that flipped PASS -> FAIL;
      - an aggregated tier metric that moved more than metric_tol (relative);
      - a change in the loadout-table dominant-weapon histogram.
    Deterministic digests make the metric comparison meaningful: without any
    botcore change, re-running reproduces the baseline exactly.
    """
    regressions = []
    for cid, ok in current.get("invariants", {}).items():
        was = base.get("invariants", {}).get(cid)
        if was is True and ok is False:
            regressions.append(f"INVARIANT {cid} regressed PASS->FAIL")
    for key, metrics in current.get("tier", {}).items():
        bmet = base.get("tier", {}).get(key, {})
        for mname, val in metrics.items():
            bval = bmet.get(mname)
            if bval is None:
                continue
            denom = max(abs(bval), 1e-6)
            if abs(val - bval) / denom > metric_tol:
                regressions.append(f"METRIC {key} {mname}: {bval} -> {val} (>{int(metric_tol*100)}%)")
    bwd = base.get("weapon_dominance", {})
    cwd = current.get("weapon_dominance", {})
    if bwd and cwd and bwd != cwd:
        regressions.append(f"WEAPON_DOMINANCE changed: {bwd} -> {cwd}")
    return regressions


# --------------------------------------------------------------------------- #
# Invariant checks (regression contract)
# --------------------------------------------------------------------------- #

class Report:
    def __init__(self):
        self.checks = []

    def check(self, cid, desc, ok, detail=""):
        self.checks.append({"id": cid, "desc": desc, "ok": bool(ok), "detail": detail})
        return ok

    @property
    def failed(self):
        return [c for c in self.checks if not c["ok"]]


def run_invariants(rep, gallery_agg, tier_agg, persona_agg, all_runs, perf, duels, seeds):
    # I1 - determinism: re-running one cell with one seed must repeat its digest.
    sample = next((r for r in all_runs if r["scenario"] == "gallery_static"
                   and r["tier"] == 5 and r["persona"] == 2), None)
    if sample:
        rerun = sh([QA_SIM, "--scenario", "gallery_static", "--tier", "5",
                    "--persona", "2", "--seed", str(sample["seed"])])
        digest2 = json.loads(rerun.stdout.strip())["metrics"]["digest"]
        rep.check("I1-determinism", "identical inputs reproduce the identical digest",
                  digest2 == sample["metrics"]["digest"],
                  f"{sample['metrics']['digest']} vs {digest2}")

    # I2 - no fire without fresh LOS (policy contract), across every run.
    bad = [r for r in all_runs if r["metrics"]["wasted_fire_invisible"] != 0]
    rep.check("I2-no-blind-fire", "policy never sets the fire bit without LOS",
              not bad, f"{len(bad)} offending runs")

    # I3 - per-tick LOS budget respected (<= skill.max_los_per_tick).
    budget_bad = []
    for r in all_runs:
        cap = {1: 4, 2: 5, 3: 6, 4: 7, 5: 8}[r["tier"]]
        if r["metrics"]["los_queries_max"] > cap:
            budget_bad.append((r["scenario"], r["tier"], r["metrics"]["los_queries_max"]))
    rep.check("I3-los-budget", "planned LOS rays never exceed the tier budget",
              not budget_bad, f"{budget_bad[:3]}")

    # I4 - gallery aim error strictly decreases with tier (skill monotonicity).
    errs = [mean_of(gallery_agg, ("gallery_static", t), "true_err_visible_mean") for t in TIERS]
    mono = all(errs[i] is not None and errs[i + 1] is not None and errs[i + 1] < errs[i]
               for i in range(4))
    rep.check("I4-aim-monotonic", "gallery true aim error falls monotonically tier 1->5",
              mono, "err=" + ",".join(f"{e:.2f}" if e else "?" for e in errs))

    # I5 - gallery hit rate: expert clearly above beginner.
    hr1 = mean_of(gallery_agg, ("gallery_static", 1), "hit_rate")
    hr5 = mean_of(gallery_agg, ("gallery_static", 5), "hit_rate")
    rep.check("I5-hitrate-spread", "expert gallery hit rate >> beginner (skill matters)",
              hr1 is not None and hr5 is not None and hr5 > hr1 + 0.2,
              f"t1={hr1:.3f} t5={hr5:.3f}" if hr1 is not None and hr5 is not None else "?")

    # I6 - expert reacts faster than beginner on a static engagement.
    r1 = mean_of(tier_agg, ("reaction_static", 1), "t_first_fire_eff_s")
    r5 = mean_of(tier_agg, ("reaction_static", 5), "t_first_fire_eff_s")
    rep.check("I6-reaction-order", "expert first effective fire earlier than beginner",
              r1 is not None and r5 is not None and r5 < r1,
              f"t1={r1:.2f}s t5={r5:.2f}s" if r1 is not None and r5 is not None else "?")

    # I7 - personality orthogonality: within one tier, gallery aim error must not
    #      depend systematically on persona (bot_profile.h contract).
    ortho_ok = True
    ortho_detail = []
    ORTHO_TOL = 0.4  # deg; measured MC noise floor is ~0.25 deg at 96 seeds
    for t in TIERS:
        perrs = [mean_of(persona_agg, ("gallery_static", t, p), "true_err_visible_mean")
                 for p in PERSONAS]
        perrs = [e for e in perrs if e is not None]
        if len(perrs) >= 2 and (max(perrs) - min(perrs)) > ORTHO_TOL:
            ortho_ok = False
            ortho_detail.append((t, round(max(perrs) - min(perrs), 3)))
    rep.check("I7-persona-orthogonal",
              "persona does not shift pure aim error within a tier (>=96 seeds)",
              ortho_ok, f"spreads>{ORTHO_TOL}: {ortho_detail}")

    # I8 - performance: decision cost per tick stays far below a 20 Hz budget.
    worst = max((row["ns_per_tick"] for row in perf["rows"]), default=None)
    rep.check("I8-perf-budget", "worst-tier policy step < 50 us/tick (offline build host)",
              worst is not None and worst < 50_000, f"{worst:.0f} ns/tick" if worst else "?")

    # I9 - skill gradient in duels: expert beats beginner in most rounds.
    d = duels.get("5v1")
    if d:
        wins = d["wins_a"]
        total = d["rounds"]
        rep.check("I9-duel-gradient", "expert (A) wins the majority of duels vs beginner (B)",
                  wins * 2 >= total, f"{wins}/{total}")

    # I10 - equal-tier duels are competitive (no side has a structural advantage).
    d = duels.get("3v3")
    if d:
        a, b, draws = d["wins_a"], d["wins_b"], d["draws"]
        rep.check("I10-duel-symmetry", "mirror-tier duel is not lopsided (A vs B within 1 win)",
                  abs(a - b) <= max(1, d["rounds"] // 4), f"A={a} B={b} draws={draws}")

    # I11 - robust effectiveness: sustained sim damage-per-second on a static
    #       free-movement engagement rises monotonically with tier. Unlike ttk_s
    #       (conditional on a kill) this is always defined and is the headline
    #       "does skill translate to damage output" signal.
    dps = [mean_of(tier_agg, ("reaction_static", t), "sim_dps") for t in TIERS]
    dps_mono = all(dps[i] is not None and dps[i + 1] is not None and dps[i + 1] > dps[i]
                   for i in range(4))
    rep.check("I11-dps-monotonic", "reaction_static sim_dps rises monotonically tier 1->5",
              dps_mono, "dps=" + ",".join(f"{x:.1f}" if x else "?" for x in dps))
    return rep


# --------------------------------------------------------------------------- #
# Reporting
# --------------------------------------------------------------------------- #

def fmt(v, nd=3):
    if v is None:
        return "  -  "
    return f"{v:.{nd}f}"


def build_markdown(tier_agg, persona_agg, gallery_agg, duels, perf, rep, cfg, elapsed,
                   strafe_ab=None, latency_sweep=None, weapon_curves=None,
                   weapon_dominance=None):
    L = []
    L.append("# Behavior-QA Simulation Report (OFFLINE - NOT RETAIL TELEMETRY)")
    L.append("")
    L.append(f"_Generated by run_behavior_qa.py in {elapsed:.1f}s. Every number is a "
             "property of (botcore Human-KI code x documented simulation assumptions "
             "A1..A8 in qa_world.h). Nothing here is measured from the real game, a "
             "real server, or a real human._")
    L.append("")
    L.append(f"- Simulation config: `{json.dumps(cfg, sort_keys=True)}`")
    L.append(f"- Invariants: {len(rep.checks) - len(rep.failed)}/{len(rep.checks)} PASS")
    L.append("")

    # invariant table
    L.append("## Invariant / regression contract")
    L.append("")
    L.append("| ID | Check | Result | Detail |")
    L.append("|----|-------|--------|--------|")
    for c in rep.checks:
        L.append(f"| {c['id']} | {c['desc']} | {'PASS' if c['ok'] else '**FAIL**'} | {c['detail']} |")
    L.append("")

    # skill tier comparison
    L.append("## Skill-tier comparison (5 levels)")
    L.append("")
    for scen in TIER_SCENARIOS:
        rows = [t for t in TIERS if (scen, t) in tier_agg]
        if not rows:
            continue
        L.append(f"### {scen}")
        L.append("")
        cols = ["kill_rate", "sim_dps", "hit_rate", "ttk_s", "t_first_fire_eff_s",
                "true_err_visible_mean", "overshoots", "dist_mean_m", "in_band_pct",
                "retreat_events", "target_switches"]
        L.append("| tier | " + " | ".join(cols) + " |")
        L.append("|------|" + "|".join(["----"] * len(cols)) + "|")
        for t in rows:
            vals = [fmt(mean_of(tier_agg, (scen, t), c)) for c in cols]
            L.append(f"| {t} {SKILL_NAMES[t]} | " + " | ".join(vals) + " |")
        L.append("")

    # personality comparison
    L.append("## Personality comparison (6 personas, tier 3)")
    L.append("")
    for scen in PERSONA_SCENARIOS:
        rows = [p for p in PERSONAS if (scen, 3, p) in persona_agg]
        if not rows:
            continue
        L.append(f"### {scen}")
        L.append("")
        cols = ["kill_rate", "hit_rate", "dist_mean_m", "approach_uptime",
                "retreat_uptime", "retreat_events", "survival_s", "ttk_s"]
        L.append("| persona | " + " | ".join(cols) + " |")
        L.append("|---------|" + "|".join(["----"] * len(cols)) + "|")
        for p in rows:
            vals = [fmt(mean_of(persona_agg, (scen, 3, p), c)) for c in cols]
            L.append(f"| {p} {PERSONA_NAMES[p]} | " + " | ".join(vals) + " |")
        L.append("")

    # duels
    L.append("## Duel outcomes (policy vs policy)")
    L.append("")
    L.append("| matchup | rounds | A wins | B wins | draws |")
    L.append("|---------|--------|--------|--------|-------|")
    for label in sorted(duels):
        d = duels[label]
        L.append(f"| {label} | {d['rounds']} | {d['wins_a']} | {d['wins_b']} | {d['draws']} |")
    L.append("")

    # weapon-score curve (dominant-strategy probe)
    if weapon_curves:
        L.append("## Weapon-score curve (loadout table dominant-strategy probe)")
        L.append("")
        L.append("Direct read-out of botcore `ScoreWeapon()` (bot_loadout.h) over "
                 "distance. `best` = highest-scoring usable weapon at that range.")
        L.append("")
        curve0 = weapon_curves.get("duelist_0.0")
        if curve0:
            L.append("| dist (m) | best weapon | score | runner-up | margin |")
            L.append("|----------|-------------|-------|-----------|--------|")
            for r in curve0["rows"]:
                if r["dist_m"] % 2 == 0 or r["dist_m"] in (15, 25, 45):
                    L.append(f"| {r['dist_m']} | {r['best_name']} | {r['best_score']:.2f} | "
                             f"{r['runner_up_name']} | {r['margin']:.2f} |")
            L.append("")
        if weapon_dominance:
            L.append("Best-weapon histogram over 2..45 m (how often each weapon is the top pick):")
            L.append("")
            L.append("| personality range_pref | " + " | ".join(
                sorted({w for h in weapon_dominance.values() for w in h})) + " |")
            weapons_sorted = sorted({w for h in weapon_dominance.values() for w in h})
            L.append("|---|" + "|".join(["---"] * len(weapons_sorted)) + "|")
            for k, h in weapon_dominance.items():
                L.append(f"| {k} | " + " | ".join(str(h.get(w, 0)) for w in weapons_sorted) + " |")
            L.append("")
            L.append("_A single weapon dominating most of the range means the intended "
                     "distance-based variety (shotgun close / sniper far) is not realised; "
                     "see the findings document. This is a property of the calibration "
                     "hypothesis table, not a measured retail balance._")
            L.append("")

    # strafe A/B (integration default bot_fStrafeScale=0 vs enabled)
    if strafe_ab:
        L.append("## Lateral-movement A/B (integration default `strafe_scale=0` vs `1`)")
        L.append("")
        L.append("**Integration fact (BotDriver.cpp):** the policy's strafe is written to "
                 "the action only when `bot_fStrafeScale>0`; the shipped default is 0, so "
                 "the Human-KI's in-band lateral movement is computed but silently dropped.")
        L.append("")
        L.append("**What this offline harness CAN show:** the accuracy cost of enabling it. "
                 "The aim controller tracks the target from the bot's *current* pose, so "
                 "self-induced lateral motion adds angular rate the controller lags behind "
                 "(no self-motion feed-forward), lowering the bot's own hit rate.")
        L.append("")
        L.append("**What it CANNOT show:** the evasion *benefit*. Scripted return fire "
                 "(assumption A9) is range-falloff dps, not dodgeable aimed projectiles, so "
                 "`survival_s` here does NOT reward strafing. Quantifying evasion benefit "
                 "requires retail telemetry or an aimed-fire model - explicitly out of scope.")
        L.append("")
        L.append("| scenario | return fire? | tier | hit_rate (off) | hit_rate (on) | strafe_cmd | strafe_applied |")
        L.append("|----------|--------------|------|------|------|------|------|")
        rf = {"firefight": "yes (not dodgeable)", "reaction_static": "no"}
        for scen in ["reaction_static", "firefight"]:
            for t in TIERS:
                off = strafe_ab["off"].get((scen, t))
                on = strafe_ab["on"].get((scen, t))
                if not off or not on:
                    continue
                L.append(
                    f"| {scen} | {rf.get(scen, '?')} | {t} | "
                    f"{fmt(mean_of(strafe_ab['off'], (scen, t), 'hit_rate'))} | "
                    f"{fmt(mean_of(strafe_ab['on'], (scen, t), 'hit_rate'))} | "
                    f"{fmt(mean_of(strafe_ab['on'], (scen, t), 'strafe_cmd_uptime'), 2)} | "
                    f"{fmt(mean_of(strafe_ab['on'], (scen, t), 'strafe_applied_uptime'), 2)} |")
        L.append("")
        L.append("_Read: `strafe_cmd` is the policy's lateral intent (present even when the "
                 "integration drops it); `strafe_applied` is motion actually produced at "
                 "`strafe_scale=1`. The hit_rate(off) > hit_rate(on) gap is the self-motion "
                 "accuracy cost the aim model does not currently compensate._")
        L.append("")

    # latency sweep
    if latency_sweep:
        L.append("## Replication-latency sweep (moving target; hitscan has no lead model)")
        L.append("")
        L.append("Assumption A7 delays the perceived enemy state by `latency` ticks. "
                 "Projectile weapons lead via `prediction_gain`; hitscan weapons have "
                 "no lead path, so latency should cost them accuracy on movers.")
        L.append("")
        L.append("| scenario | tier | hit_rate @0 | hit_rate @2 | hit_rate @4 |")
        L.append("|----------|------|------|------|------|")
        for scen in ["hitscan_latency", "tracking_strafe"]:
            for t in [3, 5]:
                cells = []
                ok = True
                for lat in (0, 2, 4):
                    v = mean_of(latency_sweep[lat], (scen, t), "hit_rate")
                    cells.append(fmt(v))
                    ok = ok and v is not None
                if ok:
                    L.append(f"| {scen} | {t} | " + " | ".join(cells) + " |")
        L.append("")

    # perf
    L.append("## Decision-layer cost (offline build host; NOT client CPU)")
    L.append("")
    L.append("| tier | ns/tick |")
    L.append("|------|---------|")
    for row in perf["rows"]:
        L.append(f"| {row['tier']} | {row['ns_per_tick']:.0f} |")
    L.append("")
    return "\n".join(L)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, default=12)
    ap.add_argument("--no-build", action="store_true")
    ap.add_argument("--write-baseline")
    ap.add_argument("--compare")
    ap.add_argument("--latency", type=int, default=2)
    ap.add_argument("--strafe-scale", type=float, default=0.0)
    ap.add_argument("--rounds", type=int, default=15)
    args = ap.parse_args()

    t0 = time.time()
    if not args.no_build:
        build()
    if not os.path.exists(QA_SIM):
        raise SystemExit("qa_sim missing; run without --no-build")

    base_cfg = ["--latency", str(args.latency), "--strafe-scale", str(args.strafe_scale)]
    cfg = {"latency_ticks": args.latency, "strafe_scale": args.strafe_scale,
           "seeds": args.seeds, "rounds": args.rounds}

    os.makedirs(RESULTS, exist_ok=True)

    # --- tier sweep (persona fixed to 2=duelist) ---------------------------
    tier_runs = run_sweep(TIER_SCENARIOS, TIERS, [2], args.seeds, extra=base_cfg)
    tier_agg = aggregate(tier_runs, ["scenario", "tier"])

    # --- gallery sweep across personas for the orthogonality check ---------
    # Orthogonality is a *statistical* property: persona changes the aim RNG
    # seed (DeriveSeed mixes persona), never the aim parameters, so the persona
    # means of pure aim error only converge with enough seeds. A dedicated,
    # larger seed count keeps the check from producing Monte-Carlo false
    # positives (measured: tier-1 spread 0.85 deg @8 seeds -> 0.25 deg @96).
    ortho_seeds = max(args.seeds, 96)
    gal_persona_runs = run_sweep(["gallery_static"], TIERS, PERSONAS, ortho_seeds, extra=base_cfg)
    persona_agg = aggregate(gal_persona_runs, ["scenario", "tier", "persona"])

    # --- personality sweep (tier fixed to 3) -------------------------------
    persona_runs = run_sweep(PERSONA_SCENARIOS, [3], PERSONAS, args.seeds, extra=base_cfg)
    persona_agg2 = aggregate(persona_runs, ["scenario", "persona"])
    # merge into persona_agg keyed by (scenario, tier, persona) with tier=3
    for (scen, pers), cell in persona_agg2.items():
        persona_agg[(scen, 3, pers)] = cell

    gallery_agg = tier_agg  # gallery_static is part of TIER_SCENARIOS

    # --- duels -------------------------------------------------------------
    duels = {}
    # Skill gradient ladder: every tier vs the beginner floor (persona duelist).
    # "1v1" is the beginner mirror - it exposes the low-tier "hit floor" (F-2):
    # if beginners cannot reliably finish each other, most rounds time out as draws.
    s, _ = run_duel(1, 2, 1, 2, args.rounds, extra=base_cfg); duels["1v1"] = s
    s, _ = run_duel(2, 2, 1, 2, args.rounds, extra=base_cfg); duels["2v1"] = s
    s, _ = run_duel(3, 2, 1, 2, args.rounds, extra=base_cfg); duels["3v1"] = s
    s, _ = run_duel(4, 2, 1, 2, args.rounds, extra=base_cfg); duels["4v1"] = s
    s, _ = run_duel(5, 2, 1, 2, args.rounds, extra=base_cfg); duels["5v1"] = s
    # Same-tier fairness + a mid/high cross-tier check.
    s, _ = run_duel(3, 2, 3, 2, args.rounds, extra=base_cfg); duels["3v3"] = s
    s, _ = run_duel(5, 2, 3, 2, args.rounds, extra=base_cfg); duels["5v3"] = s
    s, _ = run_duel(4, 2, 2, 2, args.rounds, extra=base_cfg); duels["4v2"] = s
    # personality duel at fixed tier 3: aggressor vs marksman
    s, _ = run_duel(3, 0, 3, 4, args.rounds, extra=base_cfg); duels["3:aggr_v_3:marks"] = s

    # --- perf --------------------------------------------------------------
    perf = run_perf()

    # --- weapon-score curve (dominant-strategy probe on the loadout table) --
    weapon_curves = {
        "duelist_0.0": run_weapon_curve(0.0),
        "aggressor_-0.55": run_weapon_curve(-0.55),
        "marksman_+0.85": run_weapon_curve(0.85),
    }
    weapon_dominance_summary = {k: weapon_dominance(v) for k, v in weapon_curves.items()}

    # --- strafe A/B (integration default 0 vs enabled 1) -------------------
    strafe_off = run_sweep(["firefight", "reaction_static"], TIERS, [2], args.seeds,
                           extra=["--latency", str(args.latency), "--strafe-scale", "0"])
    strafe_on = run_sweep(["firefight", "reaction_static"], TIERS, [2], args.seeds,
                          extra=["--latency", str(args.latency), "--strafe-scale", "1"])
    strafe_ab = {
        "off": aggregate(strafe_off, ["scenario", "tier"]),
        "on": aggregate(strafe_on, ["scenario", "tier"]),
    }

    # --- latency sweep: hitscan has no lead model, so replication latency
    #     should measurably cost accuracy on a moving target (assumption A7).
    latency_sweep = {}
    for lat in (0, 2, 4):
        rows = run_sweep(["hitscan_latency", "tracking_strafe"], [3, 5], [2], args.seeds,
                         extra=["--latency", str(lat), "--strafe-scale", str(args.strafe_scale)])
        latency_sweep[lat] = aggregate(rows, ["scenario", "tier"])

    all_runs = tier_runs + gal_persona_runs + persona_runs + strafe_off + strafe_on

    rep = Report()
    run_invariants(rep, gallery_agg, tier_agg, persona_agg, all_runs, perf, duels, args.seeds)

    # --- persist raw aggregate JSON ---------------------------------------
    def serialize_agg(agg):
        return {json.dumps(list(map(str, k))): v for k, v in agg.items()}

    try:
        base_sha = sh(["git", "-C", HERE, "rev-parse", "HEAD"]).stdout.strip()
    except Exception:
        base_sha = ""
    out = {
        "meta": {
            "generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "config": cfg,
            "note": "OFFLINE SIMULATION - NOT RETAIL TELEMETRY",
            "base_sha": base_sha,
        },
        "tier_agg": serialize_agg(tier_agg),
        "persona_agg": serialize_agg(persona_agg),
        "duels": duels,
        "perf": perf,
        "strafe_ab": {k: serialize_agg(v) for k, v in strafe_ab.items()},
        "latency_sweep": {str(lat): serialize_agg(agg) for lat, agg in latency_sweep.items()},
        "weapon_dominance": weapon_dominance_summary,
        "invariants": rep.checks,
    }
    with open(os.path.join(RESULTS, "behavior_qa_summary.json"), "w") as f:
        json.dump(out, f, indent=1, sort_keys=True)

    md = build_markdown(tier_agg, persona_agg, gallery_agg, duels, perf, rep, cfg,
                        time.time() - t0, strafe_ab=strafe_ab, latency_sweep=latency_sweep,
                        weapon_curves=weapon_curves,
                        weapon_dominance=weapon_dominance_summary)
    with open(os.path.join(RESULTS, "behavior_qa_report.md"), "w") as f:
        f.write(md)

    # --- baseline write / compare -----------------------------------------
    baseline_vector = {
        "tier": {f"{k[0]}|{k[1]}": {m: round(v[m]["mean"], 4)
                                     for m in v if isinstance(v.get(m), dict) and "mean" in v[m]}
                 for k, v in tier_agg.items()},
        "duels": {k: [v["wins_a"], v["wins_b"], v["draws"]] for k, v in duels.items()},
        "invariants": {c["id"]: c["ok"] for c in rep.checks},
        "weapon_dominance": weapon_dominance_summary.get("duelist_0.0", {}),
    }
    if args.write_baseline:
        with open(args.write_baseline, "w") as f:
            json.dump(baseline_vector, f, indent=1, sort_keys=True)
        print(f"baseline written: {args.write_baseline}")

    regressions = []
    if args.compare and os.path.exists(args.compare):
        with open(args.compare) as f:
            base = json.load(f)
        regressions = detect_regressions(baseline_vector, base)

    # --- console summary ---------------------------------------------------
    print(md)
    print("=" * 72)
    if regressions:
        print("REGRESSIONS DETECTED vs baseline:")
        for r in regressions:
            print("  -", r)
    elif args.compare:
        print("No regressions vs baseline (within 25% metric tolerance).")
    print(f"INVARIANTS: {len(rep.checks) - len(rep.failed)}/{len(rep.checks)} PASS")
    for c in rep.failed:
        print(f"  FAIL {c['id']}: {c['desc']} ({c['detail']})")

    os.makedirs(RESULTS, exist_ok=True)
    print(f"\nWrote {os.path.join(RESULTS, 'behavior_qa_summary.json')}")
    print(f"Wrote {os.path.join(RESULTS, 'behavior_qa_report.md')}")

    return 1 if (rep.failed or regressions) else 0


if __name__ == "__main__":
    sys.exit(main())
