# Behavior-QA — Human-KI Combat Behaviour Quality Assurance

**Independent offline QA system for the Alpha-Gaming Human-KI.**
Stand: 2026-10-25 · Base SHA: `107d28a276c4fe4428cc3c8bf5bbd876e1a85351`

This directory documents an **offline quality-assurance system** that measures
whether the existing botcore Human-KI functions actually translate into
sensible, differentiated, human-credible combat behaviour — and where they do
not. It is the analysis counterpart to the runnable tool in
[`poc/research/behavior-qa/`](../../../poc/research/behavior-qa/).

> **Hard boundary — simulation vs retail.** Every quantitative result here is
> produced by a deterministic simulator that drives the engine-free botcore
> decision code inside a synthetic world under documented assumptions
> (A1–A9). **None of it is retail gameplay telemetry, a native Retail-1.07
> acceptance, or a measured human benchmark.** No invented human comparison
> values and no claimed in-game results appear in this work. Where a question
> can only be answered by the real game (network sync, true hit registration,
> real weapon damage, evasion benefit), it is explicitly marked
> `NEEDS RETAIL` and left open.

## Documents

1. **[Human-KI static analysis](2026-10-25-human-ai-static-analysis.md)** —
   what the Human-KI is, how it reaches a real `CPlayerAction` through
   `BotDriver.cpp`, and a code-referenced review of all 15 requested behaviour
   areas plus the "bad score ≠ bad aim" root-cause hypotheses.

2. **[Metrics & assumptions](2026-10-25-metrics-and-assumptions.md)** —
   the quality-metric definitions, the simulation assumption register (A1–A9),
   the reproducibility/digest model, and the simulation↔retail boundary.

3. **[Simulation findings & recommendations](2026-10-25-simulation-findings-and-recommendations.md)** —
   the measured results (5 skill tiers, 6 personalities), the concrete
   weaknesses found, prioritised improvement recommendations, and integration
   guidance for the RDC main developer. Includes base SHA, test results and
   open blockers.

## The tool (in `poc/research/behavior-qa/`)

* `qa_sim` — C++17 simulator: 17 scenarios + policy-vs-policy duels + perf +
  weapon-score-curve probe; emits NDJSON; `--selftest` for internal contracts.
* `run_behavior_qa.py` — orchestrator: runs the battery, aggregates, enforces
  **11 behavioural invariants**, writes the report + summary JSON, and does
  baseline/regression compare.
* `test_behavior_qa.py` — offline `unittest` suite (pure-logic + binary
  integration; binary tests auto-skip if unbuilt).
* `results/behavior_qa_report.md` — the generated evidence report (committed).
* `baseline/qa_baseline.json` — golden reference for regression detection.

## Headline results (offline simulation, 12 seeds / 21 duel rounds)

* **The Human-KI works and is skill-monotonic where it should be.** Pure aim
  error falls monotonically tier 1→5 (7.02° → 1.70°); effective sim-DPS on a
  static engagement rises monotonically (4.7 → 47.0); expert beats beginner in
  20/21 duels. All 11 invariants PASS.
* **But several functions do not translate into play strength** — the exact
  concern raised. The strongest structural findings:
  * **A dominant weapon strategy**: the loadout score table makes the *laser*
    the top pick from ~4–30 m for every personality; the shotgun/sniper
    specialisation is effectively dead content (weapon variety collapses).
  * **A low-tier hit floor**: beginner aim-σ is large enough that, at common
    ranges, beginners can barely hit — the beginner-mirror duel ends in a
    timeout draw 20/21 rounds, and decisive kills do not appear until tier 3.
    Tier 1 may be non-functional rather than credibly weak.
  * **Hitscan has no lead path**: replication latency (A7) nearly halves expert
    hitscan accuracy on movers (0.58 → 0.31 from 0→200 ms), because only
    projectile weapons get `prediction_gain` lead.
  * **Lateral evasion is dropped by default**: `bot_fStrafeScale=0` in the
    integration means the policy's strafe never reaches the engine; enabling it
    costs accuracy (the aim model has no self-motion feed-forward).
  * **Retreat does not break LOS**: `MoveIntent` backs off in a straight line
    while still visible, so under sustained fire it delays but does not prevent
    death; there is no cover-seeking.

Full detail, numbers and the prioritised fix list are in document (3).

## Reproduce

```bash
cd poc/research/behavior-qa
make && ./qa_sim --selftest                       # QA SELFTEST PASS
python3 run_behavior_qa.py --seeds 12 --rounds 21  # 11/11 invariants + report
python3 -m unittest test_behavior_qa -v            # 21 offline tests OK
```
