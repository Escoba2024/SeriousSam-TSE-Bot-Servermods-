#!/usr/bin/env python3
"""HUMAN AI 2.0 Combat-QA orchestrator (research, offline only).

Runs combat_sim battery (baseline vs candidate vs cross), the F-3 mover
probe, the F-4 cover probe and CPU bench; checks behavioural invariants;
writes results/combat_qa_summary.json + results/combat_qa_report.md.

All results are OFFLINE SIMULATION under a documented synthetic world model.
Retail status: NOT_TESTED_RETAIL.
"""
import argparse, json, subprocess, sys, os

HERE = os.path.dirname(os.path.abspath(__file__))

def run(*args):
    return subprocess.run([os.path.join(HERE, "combat_sim"), *args],
                          capture_output=True, text=True, check=True).stdout

def cell(pol, kind, tA=None, pA=None, dist=None):
    out = []
    for c in pol["duels"]:
        if c["kind"] != kind: continue
        if tA is not None and c["tA"] != tA: continue
        if pA is not None and c["pA"] != pA: continue
        if dist is not None and c["dist"] != dist: continue
        out.append(c)
    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, default=16)
    args = ap.parse_args()
    data = json.loads(run("--battery", str(args.seeds)))
    base, cand = data[0], data[1]
    mover = {}
    for line in run("--mover").strip().splitlines()[1:]:
        p, t, lat, sh, hi, hr = line.split(",")
        mover[(p, int(t), int(float(lat)))] = float(hr)
    cover = run("--cover").strip().splitlines()
    bench = run("--bench").strip().splitlines()
    curve = run("--weapon-curve")

    inv = []  # (id, pass, detail)
    def check(cid, ok, detail): inv.append({"id": cid, "pass": bool(ok), "detail": detail})

    bm = {c["tA"]: c for c in cell(base, "mirror")}
    cm = {c["tA"]: c for c in cell(cand, "mirror")}
    check("I1-beginner-floor",
          cm[1]["draws"] <= bm[1]["draws"] and cm[1]["hitrateA"] >= bm[1]["hitrateA"],
          f"t1 mirror draws base={bm[1]['draws']} cand={cm[1]['draws']}, hitrate {bm[1]['hitrateA']:.3f}->{cm[1]['hitrateA']:.3f} (F-2)")
    # Mirror hitrate alone is NOT monotonic by construction: weaker tiers fight
    # closer (DesiredRange2), which enlarges the angular target. The capability
    # metric that must be monotonic is angular aim error (+ end-point hitrate gap).
    mono = all(cm[t]["aim_errA_deg"] <= cm[t-1]["aim_errA_deg"] + 0.15 for t in range(2, 6))
    mono = mono and cm[5]["aim_errA_deg"] < 0.6 * cm[1]["aim_errA_deg"] and cm[5]["hitrateA"] > cm[1]["hitrateA"] + 0.15
    check("I2-skill-monotonicity", mono,
          "candidate mirror aim-err deg t1..t5: " + ", ".join(f"{cm[t]['aim_errA_deg']:.2f}" for t in range(1, 6)) +
          "; hitrates: " + ", ".join(f"{cm[t]['hitrateA']:.3f}" for t in range(1, 6)))
    lad = cell(cand, "ladder")
    check("I3-ladder", all(c["winA"] > c["winB"] for c in lad),
          "; ".join(f"t{c['tA']}>t{c['tB']}: {c['winA']}-{c['winB']}" for c in lad))
    cross = cell(cand, "cross")
    cwins = sum(1 for c in cross if c["winA"] > c["winB"])
    check("I4-cross-policy", cwins >= 6,
          f"candidate beats baseline in {cwins}/{len(cross)} same-tier cells: " +
          "; ".join(f"t{c['tA']}p{c['pA']}@{c['dist']:.0f}m {c['winA']}-{c['winB']} D{c['draws']}" for c in cross))
    def laser_share(c):
        w = c["weaponsA"]; tot = sum(w.values()) or 1
        return w.get("laser", 0) / tot, len(w)
    bl = [laser_share(bm[t])[0] for t in range(1, 6)]
    cl = [laser_share(cm[t]) for t in range(1, 6)]
    check("I5-weapon-diversity", max(s for s, _ in cl) < 0.35 and min(n for _, n in cl) >= 3,
          f"laser share mirrors base={['%.2f'%x for x in bl]} cand={['%.2f'%s for s,_ in cl]}; distinct weapons cand={[n for _,n in cl]} (F-1)")
    check("I6-latency-lead",
          mover[("candidate", 5, 200)] >= 0.85 * mover[("candidate", 5, 0)] and
          mover[("baseline", 5, 200)] < 0.75 * mover[("baseline", 5, 0)],
          f"mover t5 hitrate 0->200ms base {mover[('baseline',5,0)]:.3f}->{mover[('baseline',5,200)]:.3f}, cand {mover[('candidate',5,0)]:.3f}->{mover[('candidate',5,200)]:.3f} (F-3)")
    check("I7-strafe-active",
          all(cm[t]["strafe_ticksA"] > 0 for t in range(1, 6)) and all(bm[t]["strafe_ticksA"] == 0 for t in range(1, 6)),
          f"strafe ticks/duel cand={ [cm[t]['strafe_ticksA'] for t in range(1,6)] } base=0 (shipped bot_fStrafeScale=0, F-5)")
    cov_ok = "los_break_s=-1" in cover[0] and "los_break_s=" in cover[1] and "los_break_s=-1" not in cover[1]
    check("I8-cover-retreat", cov_ok, f"cover probe: {cover[0]} | {cover[1]} (F-4)")
    per = {c["pA"]: c for c in cell(cand, "persona")}
    bper = {c["pA"]: c for c in cell(base, "persona")}
    tops = {p: max(c["weaponsA"], key=c["weaponsA"].get) for p, c in per.items()}
    rng_spread = max(c["mean_rangeA"] for c in per.values()) - min(c["mean_rangeA"] for c in per.values())
    def hist_l1(ca, cb):
        ka, kb = ca["weaponsA"], cb["weaponsA"]
        ta, tb = sum(ka.values()) or 1, sum(kb.values()) or 1
        return sum(abs(ka.get(k, 0) / ta - kb.get(k, 0) / tb) for k in set(ka) | set(kb)) / 2
    l1_c = hist_l1(per[0], per[4])   # aggressor vs marksman
    l1_b = hist_l1(bper[0], bper[4])
    check("I9-persona-difference", l1_c >= 0.25 and l1_c > 3 * l1_b and rng_spread >= 3.0,
          f"weapon-histogram L1 aggressor-vs-marksman cand={l1_c:.2f} base={l1_b:.2f}; mean-range spread={rng_spread:.1f} m; tops={tops}")
    ff_mono = all(cm[t]["first_fireA_s"] <= cm[t-1]["first_fireA_s"] + 0.35 for t in range(2, 6))
    check("I10-reaction-ordering", ff_mono and cm[5]["first_fireA_s"] < cm[1]["first_fireA_s"],
          "candidate first-fire s t1..t5: " + ", ".join(f"{cm[t]['first_fireA_s']:.2f}" for t in range(1, 6)))
    # survival/TTK: candidate mirrors last longer (evasion), expert kills faster than beginner mirrors
    check("I11-ttk-ordering", cm[5]["mean_duration_s"] < cm[1]["mean_duration_s"],
          f"candidate mirror duration t1={cm[1]['mean_duration_s']:.1f}s t5={cm[5]['mean_duration_s']:.1f}s")

    npass = sum(1 for i in inv if i["pass"])
    summary = {"seeds_per_cell": args.seeds, "retail_status": "NOT_TESTED_RETAIL",
               "invariants": inv, "invariants_pass": f"{npass}/{len(inv)}",
               "mover_hitrates": {f"{k[0]}_t{k[1]}_{k[2]}ms": v for k, v in sorted(mover.items())},
               "cover_probe": cover, "bench": bench, "battery": data}
    os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
    with open(os.path.join(HERE, "results", "combat_qa_summary.json"), "w") as f:
        json.dump(summary, f, indent=1)
    with open(os.path.join(HERE, "results", "weapon_curve.txt"), "w") as f:
        f.write(curve)
    lines = ["# Combat-QA report (offline simulation - NOT_TESTED_RETAIL)", "",
             f"Seeds/cell: {args.seeds} (seed base 0xC0FFEE + 977*i). Invariants: **{npass}/{len(inv)} PASS**.", ""]
    for i in inv:
        lines.append(f"- {'PASS' if i['pass'] else '**FAIL**'} `{i['id']}` - {i['detail']}")
    lines += ["", "## CPU bench", "```"] + bench + ["```", "", "## Cover probe", "```"] + cover + ["```"]
    with open(os.path.join(HERE, "results", "combat_qa_report.md"), "w") as f:
        f.write("\n".join(lines) + "\n")
    for i in inv:
        print(("PASS " if i["pass"] else "FAIL ") + i["id"] + " - " + i["detail"])
    print(f"INVARIANTS {npass}/{len(inv)} PASS  (results in results/)")
    return 0 if npass == len(inv) else 1

if __name__ == "__main__":
    sys.exit(main())
