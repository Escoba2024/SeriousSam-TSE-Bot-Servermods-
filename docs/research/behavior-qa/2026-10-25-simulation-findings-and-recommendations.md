# Simulation Findings, Weaknesses & Prioritised Recommendations

Stand: 2026-10-25 · **Base SHA:** `107d28a276c4fe4428cc3c8bf5bbd876e1a85351`
Battery: 12 seeds/cell, 21 duel rounds, latency 2, `strafe_scale 0` (integration
default). Evidence: [`poc/research/behavior-qa/results/behavior_qa_report.md`](../../../poc/research/behavior-qa/results/behavior_qa_report.md)
and `results/behavior_qa_summary.json`.

> ⚠️ **Every number below is an OFFLINE SIMULATION result** — a property of
> (botcore Human-KI × assumptions A1–A9 × scenario × seed). None is retail
> telemetry, a native Retail-1.07 acceptance, or a human benchmark. Absolute
> magnitudes carry the assumptions' uncertainty; the **signal is the relative
> comparison** (tier↔tier, persona↔persona, config A↔B). Items only the real
> game can settle are tagged `NEEDS RETAIL`.

---

## 0. Test & reproduction status

| Gate | Result |
|------|--------|
| Existing botcore offline tests (built out-of-tree, read-only) | **7/7 PASS** on base SHA |
| `qa_sim --selftest` (world model + policy contracts) | **PASS** |
| `python3 -m unittest test_behavior_qa` | **21/21 OK** |
| Full QA battery invariants | **11/11 PASS** (~1.4 s) |
| Baseline regression compare (deterministic re-run) | **No regressions** |
| Native Retail-1.07 acceptance (join/sync/hit/damage/CPU) | **NOT_TESTED** (out of scope, offline only) |

The 11 invariants (I1–I11) are the behavioural contract; see the tool README.

---

## 1. What the Human-KI gets RIGHT (validated)

These are the positive results — the functions that *do* translate into
sensible, differentiated play strength.

### 1.1 Aim quality is strictly skill-monotonic (fixed geometry)
`gallery_static` (body locked, static target 15 m), 12 seeds — the pure-aim
signal, uncontaminated by movement or range choice:

| tier | true aim err (°) | overshoots | hit_rate | kill_rate | sim_dps |
|------|-----------------|-----------|----------|-----------|---------|
| 1 beginner | 7.02 | 17.1 | 0.10 | 0.42 | 4.6 |
| 2 casual   | 4.76 | 6.9  | 0.13 | 0.92 | 9.3 |
| 3 average  | 3.38 | 1.2  | 0.29 | 0.92 | 22.7 |
| 4 advanced | 2.39 | 0.1  | 0.47 | 1.00 | 37.3 |
| 5 expert   | 1.70 | 0.0  | 0.84 | 1.00 | 64.0 |

Aim error and overshoot fall monotonically; hit-rate and DPS rise. **Invariant
I4 (aim monotonic) and I5 (hit spread) hold.** The aim model (OU bias +
per-target offset + weak-brake overshoot + trigger discipline) is correctly
tiered and reproducible.

### 1.2 Skill → effective damage output is monotonic in free combat
`reaction_static` sim-DPS: **4.7 → 9.4 → 17.0 → 28.1 → 47.0** (I11 PASS). This
robust metric (unlike conditional TTK) confirms higher tiers finish fights
faster. Effective reaction `t_first_fire_eff`: **1.58 → 0.41 s** (I6 PASS).

### 1.3 Skill gradient and fairness in duels
Policy-vs-policy, 21 rounds each, 45 s cap. **Skill-gradient ladder** (tier X
vs the beginner floor, persona duelist both sides):

| ladder (A vs B) | A wins | B wins | draws |
|-----------------|--------|--------|-------|
| beginner(1) vs beginner(1) — mirror | 0 | 1 | **20** |
| casual(2) vs beginner(1)   | 8  | 0 | **13** |
| average(3) vs beginner(1)  | 20 | 0 | 1 |
| advanced(4) vs beginner(1) | 21 | 0 | 0 |
| expert(5) vs beginner(1)   | 20 | 0 | 1 |

**Cross-tier & fairness:**

| matchup | A wins | B wins | draws |
|---------|--------|--------|-------|
| expert(5) vs average(3)  | 19 | 2 | 0 |
| advanced(4) vs casual(2) | 21 | 0 | 0 |
| average(3) vs average(3) — mirror | 11 | 9 | 1 |
| aggressor(3) vs marksman(3) | 13 | 8 | 0 |

From tier 3 up the higher tier wins decisively (I9 PASS); mirror-tier is fair
with no side advantage (I10, 11-9-1); personality is observable (aggressor edges
marksman). **But note the beginner mirror ends 20/21 in draws** — see F-2.

### 1.4 Perception contracts hold
* **No blind fire** (I2): `wasted_fire_invisible == 0` in every run — the policy
  never pulls the trigger without fresh LOS.
* **LOS budget respected** (I3): planned rays ≤ tier `max_los_per_tick` always.
* **Memory & reacquisition work**: `cover_reacquire` (30-tick LOS gap) — the bot
  holds the track, wastes no shots while blind, re-engages and still kills
  (expert TTK ~4.3 s).
* **Persona orthogonality** (I7): at ≥96 seeds, pure aim error does not depend
  on persona within a tier (spread < 0.4°), confirming the bot_profile.h
  contract at the behavioural level.

### 1.5 Alert-driven turn-to-engage works (attacked from behind)
`damage_alert_behind` (attacker 180° behind, only cue is own health dropping),
12-seed aggregates:

| tier | t_selectable | t_first_fire_eff | hit_rate | dmg dealt | dmg taken | survival |
|------|-------------|------------------|----------|-----------|-----------|----------|
| 1 beginner | 0.15 s | 2.74 s | 0.02 | 13 | **100 (dies)** | 12.8 s |
| 3 average  | 0.10 s | 1.61 s | 0.16 | 84 | 86 | 9.5 s |
| 5 expert   | 0.05 s | 1.10 s | 0.69 | 106 | 35 | 3.0 s |

The alert window (⅓ reaction, see F-8) makes awareness near-instant even from
behind (0.05–0.15 s), and the higher tier completes the 180° turn and lands hits
sooner. The beginner turns but barely connects (hit_rate 0.02) and takes the
full 100 damage — a clean skill gradient under ambush. (`t_first_hit` is omitted
here: it is conditional on a hit occurring and is misleading for tiers that
rarely connect.)

### 1.6 Decision cost is negligible and skill-independent
`--perf` (8 candidates): **~0.9–1.1 µs/tick, flat across all tiers** (I8, budget
50 µs). The profile-driven layer adds no measurable per-tick cost and does not
scale with skill. (This is decision-layer cost on the build host — **not**
GameMP.dll/client CPU, which is `NEEDS RETAIL`.)

---

## 2. Weaknesses — functions that do NOT translate into play strength

Ordered by severity. Each is a concrete, code-located, simulator-evidenced
finding. Fixes touch botcore, which this work **must not modify** — so these are
recommendations for the RDC main developer, with the QA probe that validates
each fix.

### 🔴 F-1 (High) — Loadout table has a dominant weapon strategy
**Evidence** (`--weapon-curve`, range_pref 0): the **laser is the top-scoring
weapon from ~4 m to 30 m** (27 of 44 sampled distances); double-shotgun only at
2–3 m; cannon only at 32–45 m; **the sniper is never the top pick at any
distance.** The histogram is *identical* for aggressor (−0.55), duelist (0) and
marksman (+0.85) — personality `range_preference` never changes the winner.
Confirmed in-scenario: `weapon_boundary` (locked, 6–34 m sweep) yields
`weapon_distinct = 1`, `weapon_switches = 1` (initial pick only) for every tier.

**Root cause** (bot_loadout.h): laser's `dps_rel = 4.4` combined with a flat
`acc 0.85→0.70` over `0–80 m` keeps `dps_rel·AccuracyAt·RangeFit` on top
across the whole engagement envelope; the `range_preference` tilt (±0.35) is too
weak to overcome it. The switch *machinery* (dwell/margin hysteresis) is fine —
it simply has nothing to switch to.

**Impact:** intended distance-based variety (shotgun close / sniper far) is dead
content; every bot converges on one weapon regardless of tier, persona or range.
Areas affected: **#6 weapon switching, #7 combat ranges, #11 personalities,
"unsuitable weapons".**

### 🔴 F-2 (High) — Low-tier "hit floor": beginners can be non-functional
**Evidence:** in free combat (`reaction_static`) tier-1 and tier-2 hit-rates are
**nearly identical (0.10 vs 0.13)** even though tier-2 aims ~32 % better
(true_err 6.98° vs 4.74°) — both sit above the ~2° angular tolerance a 0.6 m
target subtends at 15 m, so extra accuracy buys almost nothing until it crosses
the hittable threshold (tier 3+). In the duel ladder (§1.3) the **beginner
mirror ends in a timeout draw 20/21 rounds**, and **casual beats beginner in
only 8/21 (13 draws)** — decisive kills do not appear until tier 3 (20/21).
`tracking_strafe` tier-1 kill_rate is **0.08**. The floor is real: below tier 3
two bots mostly fail to finish each other inside 45 s.

**Root cause** (bot_aim.h + bot_profile.h): tier-1 `aim_sigma = 4.5°` and
`overshoot = 0.55`, plus a **per-target offset drawn once and never adapted**,
produce a persistent true error far above the hittable angle; `fire_tol = 5°`
lets the trigger fire at true errors that cannot connect, so the beginner burns
ammo without effect.

**Impact:** tier 1 risks being *non-functional* rather than *credibly weak* —
the opposite of the project goal (believable human opponents across a skill
range). Areas: **#2 aim accuracy, #5 hit probability, #10 difficulty
gradations, #12 K/D, "unsuitable skill parameters".** *Absolute hit-rate scale
is A3-bound (`NEEDS RETAIL`), but the tier-1↔tier-2 indistinguishability and
the draw-heavy mirror duel are structural, not scale artifacts.*

### 🟠 F-3 (Medium-High) — Hitscan weapons have no lead / latency compensation
**Evidence** (latency sweep, hit_rate): expert hitscan on a mover collapses as
replication delay grows —

| scenario | tier | @0 ms | @100 ms | @200 ms |
|----------|------|-------|---------|---------|
| hitscan_latency | 5 | 0.58 | 0.39 | 0.31 |
| hitscan_latency | 3 | 0.23 | 0.18 | 0.14 |
| tracking_strafe | 5 | 0.59 | 0.45 | 0.28 |

**Root cause** (bot_human.h): lead is applied **only when `wp.proj_speed > 0`**.
Hitscan weapons aim at the delayed replicated position with zero compensation,
so a target moving laterally at ~4.5 m/s is ~0.45 m off after 100 ms — outside
the hittable radius. The better the tier, the more latency robs it (the expert
has the most to lose).

**Impact:** on real servers (nonzero ping) hitscan accuracy vs movers will be
systematically worse than the aim model implies. Areas: **#4 leading, #5 hit
probability, "too slow target acquisition".** *Real delay magnitude is A7
(`NEEDS RETAIL`); the relative slope is the finding.*

### 🟠 F-4 (Medium) — Retreat does not break LOS or seek cover
**Evidence** (`retreat_pressure`, bot at 40 HP, scripted return fire): every
persona retreats, but `survival_s ≈ 4.5 s` and `kill_rate = 0` for tiers 1–3 —
the bot backs off in a straight line **while still visible**, so (under A9
range-falloff fire) it only slows the damage and still dies. No cover-seeking,
no perpendicular break.

**Root cause** (bot_human.h `MoveIntent`): retreat is `forward = −0.85` plus a
small strafe — pure back-pedalling with no navigation objective. The
waypoint/ObstacleRecovery layer is stuck-recovery only, not tactical.

**Impact:** "survivor"/cautious personalities do not actually survive better
under sustained fire. Areas: **#8 movement, #9 retreat, #11 personalities.**
*Evasion benefit vs aimed fire is `NEEDS RETAIL` (A9 fire is not dodgeable).*

### 🟠 F-5 (Medium) — Lateral evasion is dropped by default and un-compensated
**Evidence:** integration fact **F1** — `pa_vTranslation(1)` (strafe) is written
only when `bot_fStrafeScale > 0`; shipped default is 0, so the policy's in-band
lateral movement (`strafe_cmd_uptime ≈ 1.0`) never reaches the engine. The A/B
shows enabling it **costs the bot's own accuracy**: `reaction_static` tier-4
hit_rate **0.34 (off) → 0.19 (on)**, tier-5 **0.58 → 0.52**, because the aim
controller tracks from the moving pose with no self-motion feed-forward.

**Root cause:** `bot_fStrafeScale = 0` default + `AimController` has no
compensation for self-induced angular rate.

**Impact:** the human-like strafing the Human-KI computes is currently inert;
naively enabling it degrades accuracy. **This is a prime "bad score ≠ bad aim"
case: poor movement config, not poor aim.** Areas: **#8 movement, "poor
movement".** *Evasion upside is `NEEDS RETAIL`.*

### 🟡 F-6 (Low-Medium) — Search is unidirectional and never turns toward bearing
**Evidence** (`reaction_turn90`, target 90° off-FOV, no alert): `t_first_selectable`
is **2.9 s (expert) to 6.0 s (beginner)** — the bot scans at `search_rate` in a
single fixed direction, so a target just outside the cone on the near side is
reached only after sweeping the long way round (up to ~270°).

**Root cause** (bot_human.h): no-target scan is `yaw += search_rate·dt`, always
the same sign; there is no "turn toward last known / most recent sound" logic
(the client legitimately lacks attacker bearing, but lost-target memory bearing
is available and unused for search).

**Impact:** slow, predictable acquisition when not under fire. Areas: **#1
reaction, #3 tracking, #8 movement.**

### 🟡 F-7 (Low-Medium) — Mid-tier target prioritisation ignores the nearest threat
**Evidence** (`multi_3v1`, `nearest_not_chosen_pct`): tier-2 **11.7 %**, tier-3
**18.1 %** of engaged ticks have a ≥25 % closer live enemy that is *not* the
chosen target, vs tier-4 5.4 % and tier-5 0.2 %. Mid-tier `focus_share` is only
~0.59 (fire is spread), and mid-tier kill_rate in 3v1 is ~0.08.

**Root cause** (bot_human.h `ChooseTarget`): `1.35×` stickiness + `1.4×`-closer
switch rule + post-switch hard-lock of `ReactionTicks`. Mid tiers have long
reaction → long hard-lock → sluggish re-prioritisation; stickiness keeps a
stale, farther target.

**Impact:** mid-tier bots are overwhelmed in multi-opponent fights partly by
prioritisation, not only by aim. Areas: **#14 multiple opponents, "missing
prioritisation", "too frequent/infrequent target switches".**

### 🟢 F-8 (Low) — Alert grants near-360° awareness
**Evidence:** in `damage_alert_behind` the attacker 180° behind becomes
`Selectable` in **0.05–0.15 s** — `NeedsLineOfSight()` returns true for all
in-range candidates while `alerted()`, bypassing the FOV cone, so the LOS ray
"sees" the attacker without the body turning.

**Root cause** (bot_perception.h): the damage alert intentionally drops the FOV
gate ("what hit me? — look around first"). It is generous vs a human glance.

**Impact:** realism question, not a performance bug — being shot from behind
gives near-omniscient acquisition. Consider requiring the turn before the track
is *selectable*. Area: **#1 reaction, #11 believability.**

### 🟢 F-9 (Low) — Range inflation compresses mid-tier scoring
**Evidence:** `skill.preferred_range_m` rises 7→22 m, so experts self-position
farther (`reaction_static` dist_mean 15 m → 19.6 m). Because `AccuracyAt` falls
with distance, free-combat hit-rate is compressed at the top (expert still wins,
but the gallery→reaction hit-rate drop is largest for high tiers). This is why
**free-movement hit-rate is not cleanly monotonic** even though aim is.

**Root cause:** monotonic `preferred_range_m` × accuracy falloff.

**Impact:** a methodological caution (range confounds hit-rate) and a possible
balance lever if experts fighting at 20 m+ is undesired. Areas: **#7 ranges,
"poor positioning".**

---

## 3. Prioritised recommendations for the RDC main developer

Priority = severity × how directly it blocks "believable human opponents".
None require this QA work to modify botcore; each lists the **QA probe that
proves the fix** (re-run `run_behavior_qa.py --compare baseline/…`).

| # | Prio | Recommendation | Validate with |
|---|------|----------------|---------------|
| **R1** | P0 | **Rebalance the loadout score table** so each weapon owns a band: reduce laser `dps_rel` or steepen its accuracy falloff; raise shotgun close-weight and sniper mid/far accuracy; increase the `range_preference` tilt so marksman/aggressor actually differ. | `--weapon-curve` until ≥4 distinct best-weapons across 2–45 m and the persona histograms diverge; WEAPON_DOMINANCE regression will flag the change (re-baseline consciously). |
| **R2** | P0 | **Fix the low-tier hit floor.** Prefer (b)+(c): add slow *aim-offset adaptation* (bleed the per-target offset toward zero while a target is continuously tracked, so a beginner improves within an engagement) **and** tie `fire_tol` to the hittable angle at range instead of a flat 5°. Optionally trim tier-1/2 `aim_sigma`. | gallery hit_rate tier-1 rises off the floor; **beginner-mirror duel draws drop** from 20/21; tier-1 vs tier-2 become distinguishable in `reaction_static`. |
| **R3** | P1 | **Add latency lead for hitscan.** Apply a velocity·latency aim-point offset for `proj_speed==0` weapons too (feed an estimated replication delay). | `hitscan_latency` slope flattens across latency 0/2/4 (expert hit_rate no longer halves). |
| **R4** | P1 | **Decide strafe policy and compensate aim.** If evasion is wanted, set `bot_fStrafeScale>0` **and** add self-motion feed-forward to `AimController`; otherwise document that lateral movement is intentionally inert. | strafe A/B: self-motion accuracy cost shrinks; `NEEDS RETAIL` for the evasion benefit. |
| **R5** | P1 | **Make retreat break contact.** Give retreat an objective (perpendicular break + cover via the existing waypoint/ObstacleRecovery layer), not straight back-pedal. | `retreat_pressure`/`firefight` survival_s and kill_rate improve for cautious personas; `NEEDS RETAIL` vs aimed fire. |
| **R6** | P1 | **Wire offline metrics to retail telemetry.** Extend the `[BotHuman]` log (already has `err/dist/pref/move/strafe/switches/overshoots/rays/skipped`) with first-hit/kill markers, hit/shot counters and weapon_mode, so retail logs can *replace* assumptions A2–A7 with measured values and confirm/refute each finding. | retail log fields map 1:1 to the metric catalog (doc 2, §4). |
| **R7** | P2 | **Threat-aware prioritisation.** Bias `ChooseTarget` by recently-damaged + visible + nearest; shorten the post-switch hard-lock for higher tiers or scale it inversely with reaction. | `multi_3v1` `nearest_not_chosen_pct` falls for mid tiers; `focus_share` rises; mid-tier 3v1 kill_rate improves. |
| **R8** | P2 | **Bidirectional / memory-guided search.** Scan toward the last known target bearing, or alternate direction, instead of a single fixed sign. | `reaction_turn90` `t_first_selectable` drops and stops depending on which side the target is on. |
| **R9** | P2 | **Review alert FOV generosity.** Optionally require the body to turn before an alerted rear track becomes *selectable*. | `damage_alert_behind` `t_first_selectable` rises toward the turn time (more human), without losing the ambush skill gradient. |
| **R10** | P3 | **Reconsider range inflation** if experts fighting at 20 m+ is undesired: cap or non-monotonic `preferred_range_m`. | `reaction_static` dist_mean and gallery↔reaction hit-rate gap narrow for high tiers. |

---

## 4. How to use this system for ongoing QA (integration workflow)

1. **Before editing botcore Human-KI**, run
   `python3 run_behavior_qa.py --compare baseline/qa_baseline.json` — it should
   report *no regressions* (deterministic).
2. **Edit in a separate worktree/branch** (never in this QA scope), then re-run
   the same command. Invariant flips and >25 % metric deltas pinpoint exactly
   which behaviour moved (aim, reaction, weapon choice, prioritisation, …).
3. **Isolate the change** with the right probe: `gallery_static` (aim only,
   body locked) · `--weapon-curve` (loadout table) · latency sweep (A7/lead) ·
   strafe A/B (integration F1) · duels (net play strength).
4. **Re-baseline consciously** (`--write-baseline`) once a change is accepted,
   and record the new base SHA. The WEAPON_DOMINANCE and invariant checks are
   designed to make deliberate rebalances visible rather than silent.

---

## 5. Open blockers / not-tested (honest boundary)

* **No native Retail-1.07 acceptance performed.** This is offline simulation
  only; join/sync/hit-registration/true-damage/client-CPU are **NOT_TESTED**.
* Assumptions **A2 (move speed), A4/A5 (damage/cadence), A6 (switch latency),
  A7 (replication delay)** are hypotheses; their absolute values are `NEEDS
  RETAIL`. Relative comparisons are robust to them; absolute hit-rates/TTK/DPS
  are not.
* **Evasion benefit of strafing and cover** cannot be shown offline (A9 return
  fire is not dodgeable). Only the accuracy *cost* of self-motion is measured.
* No changes to `main`; no productive server touched; no protected binaries,
  private logs or credentials published. This work is delivered as a standalone
  PR from the session branch and is **not auto-merged**.
