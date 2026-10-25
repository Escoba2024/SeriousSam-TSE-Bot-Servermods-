# Behavior-QA — Offline Human-KI Combat Test System

**Status: OFFLINE SIMULATION TOOL. Not a retail test, not a native acceptance.**

An independent quality-assurance harness that drives the existing engine-free
botcore **Human-KI** (`../../botcore/bot_human.h` and companions) inside a
synthetic combat world, so combat behaviour becomes **measurable, comparable
and regression-tested** without the game, a server, Windows or Wine.

It answers the project question: *"The bots already have many Human-KI
functions — do they actually translate into sensible play strength?"* It does
so by producing numbers, not prose, and by separating **what the simulation can
prove** from **what only retail telemetry can prove**.

> 🔒 **Scope:** this harness lives entirely under `poc/research/behavior-qa/`
> and `docs/research/behavior-qa/`. It includes the botcore headers
> **read-only** and never modifies `BotDriver.cpp`, `bot_human.h`,
> `bot_profile.h`, `bot_aim.h`, `bot_loadout.h` or `bot_perception.h`.

---

## What it is / what it is NOT

| It IS | It is NOT |
|-------|-----------|
| A deterministic simulator of the botcore decision chain | A measurement of the real game or a real server |
| A source of *relative* signals (tier vs tier, persona vs persona, config A vs B) | A source of absolute "human" hit-rates or K/D |
| A regression gate (invariants + baseline digest compare) | A native Retail-1.07 acceptance |
| Reproducible from `(scenario, tier, persona, seed, config)` | Evidence of runtime/sync/network behaviour |

Every produced number is a property of **(botcore code × documented simulation
assumptions A1–A9)**. The assumptions are listed in `qa_world.h` and in
[`docs/research/behavior-qa/2026-10-25-metrics-and-assumptions.md`](../../../docs/research/behavior-qa/2026-10-25-metrics-and-assumptions.md).
No invented human comparison values and no claimed gameplay results appear
anywhere in this tool or its output.

---

## Layout

```
poc/research/behavior-qa/
├── qa_world.h            # synthetic world model + assumptions A1..A9 (read-only botcore include)
├── qa_sim.cpp            # simulator: scenarios, duels, metrics, NDJSON, selftest, perf, weapon-curve
├── Makefile              # builds ./qa_sim against ../../botcore (read-only)
├── run_behavior_qa.py    # orchestrator: battery → aggregate → invariants → report → baseline/compare
├── test_behavior_qa.py   # offline unittest suite (pure-logic tests + binary integration tests)
├── baseline/qa_baseline.json   # golden reference for regression compare
└── results/              # generated evidence (report.md + summary.json) — committed
```

## Build & run

```bash
cd poc/research/behavior-qa
make                 # builds ./qa_sim (g++ -std=c++17 -O2), read-only botcore include
./qa_sim --selftest  # internal correctness + policy-contract checks  → "QA SELFTEST PASS"

# full QA battery: 5-tier + 6-persona comparison, duels, latency & strafe A/B,
# weapon-score curve, 11 invariants, writes results/ report + summary JSON
python3 run_behavior_qa.py --seeds 12 --rounds 21

# regression gate: store a golden baseline, then compare future runs against it
python3 run_behavior_qa.py --write-baseline baseline/qa_baseline.json
python3 run_behavior_qa.py --compare        baseline/qa_baseline.json   # exit 1 on regression

# offline test suite (safe anywhere; binary tests auto-skip if ./qa_sim absent)
python3 -m unittest test_behavior_qa -v
```

The whole battery runs in ~1–2 s on a laptop; it is pure CPU decision code.

## Single-scenario / ad-hoc probes

```bash
./qa_sim --list                                   # enumerate scenarios (NDJSON)
./qa_sim --scenario reaction_static --tier 5 --persona 2 --seed 5
./qa_sim --sweep --scenarios gallery_static --tiers 1,2,3,4,5 --personas 2 --seeds 16
./qa_sim --duel --duel-a 5:2 --duel-b 1:2 --rounds 21
./qa_sim --weapon-curve --range-pref 0            # loadout dominant-strategy probe
./qa_sim --perf --candidates 8 --ticks 20000      # decision-layer ns/tick (NOT client CPU)
```

CLI knobs that change the *simulation assumptions* (all reported in the JSON):
`--latency` (A7 replication delay, ticks), `--strafe-scale` (mirrors
`bot_fStrafeScale`, default 0 = integration default), `--move-speed` (A2),
`--switch-ticks` (A6), `--dps-scale` (A4), `--target-radius` (A3),
`--cover-gap` (LOS-loss length).

## Scenarios

`gallery_static` (locked body, pure aim) · `reaction_static` · `reaction_turn90`
(search-rate limited) · `damage_alert_behind` (attacker outside FOV) ·
`tracking_strafe` · `tracking_orbit` · `approach_close` · `retreat_pressure`
(low HP + return fire) · `firefight` (sustained trade) · `cover_reacquire`
(LOS loss + memory) · `weapon_boundary` (locked, 6–34 m sweep) · `multi_2v1` ·
`multi_3v1` · `long_range_lead` (projectile lead) · `hitscan_latency` ·
`idle_scan` (no opponent control) · `duel` (policy vs policy).

## The 11 invariants (regression contract)

| ID | Contract |
|----|----------|
| I1 | identical inputs reproduce the identical metric digest (determinism) |
| I2 | policy never sets the fire bit without fresh LOS (no blind fire) |
| I3 | planned LOS rays never exceed the tier's `max_los_per_tick` budget |
| I4 | gallery true aim error falls monotonically tier 1→5 |
| I5 | expert gallery hit rate ≫ beginner (skill is observable) |
| I6 | expert's first effective fire is earlier than beginner's (reaction) |
| I7 | persona does not shift *pure* aim error within a tier (orthogonality, ≥96 seeds) |
| I8 | worst-tier decision step < 50 µs/tick on the build host (perf guard) |
| I9 | expert wins the majority of duels vs beginner (skill gradient) |
| I10 | mirror-tier duel is not lopsided (no structural side advantage) |
| I11 | `reaction_static` sim-DPS rises monotonically tier 1→5 (robust effectiveness) |

A future edit to any botcore Human-KI file that changes combat behaviour will
trip one or more invariants and/or the baseline compare — that is the
regression signal this tool exists to produce.

## Interpreting results honestly

* **`ttk_s` is conditional on a kill.** Low tiers often never finish a target,
  so averaging TTK only over the lucky seeds flatters them. Always read `ttk_s`
  together with `kill_rate` and `sim_dps` (always defined).
* **`survival_s` in a no-return-fire scenario is just run duration** (≈ inverse
  of kill speed), not tankiness. Only interpret it in `retreat_pressure`,
  `firefight`, `damage_alert_behind` and duels.
* **Absolute hit-rates depend on assumption A3** (0.6 m target × botcore
  `AccuracyAt`). The *signal* is relative (tier/persona/config deltas), not the
  absolute percentage.
* **Evasion benefit of strafing is not measurable offline** — scripted return
  fire (A9) is not dodgeable. The strafe A/B shows only the self-motion
  accuracy *cost*; the benefit needs retail telemetry.

See `docs/research/behavior-qa/` for the full analysis, findings and the
prioritised recommendations for the RDC main developer.
