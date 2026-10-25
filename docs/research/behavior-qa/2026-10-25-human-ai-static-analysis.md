# Human-KI Static Analysis — Architecture & 15 Behaviour Areas

Stand: 2026-10-25 · Base SHA: `107d28a276c4fe4428cc3c8bf5bbd876e1a85351`
Scope: **read-only analysis** of the existing Human-KI. No file outside
`poc/research/behavior-qa/**` and `docs/research/behavior-qa/**` was modified.

This document maps what the Human-KI actually is and how a loaded profile
becomes a real `CPlayerAction`, then reviews each of the 15 requested behaviour
areas against the code, and states the "bad score ≠ bad aim" root-cause
hypotheses that the simulator (document 3) then tests.

---

## 1. Component map (all engine-free, all under `poc/botcore/`)

| File | Role | Key API |
|------|------|---------|
| `bot_profile.h` | 5 skill tiers × 6 personalities as **calibration hypotheses**; strict skill/personality orthogonality | `SkillFor`, `PersonalityFor`, `BuildProfile`, `DeriveSeed`, `EffectiveAggression`, `ValidateProfile`, `SkillUnaffectedByPersonality` |
| `bot_perception.h` | FOV/range gating, per-target track memory, reaction delay, damage "alert" | `Perception::BeginTick/NeedsLineOfSight/Observe/Selectable/ReactionTicks/NotifyDamage` |
| `bot_aim.h` | rate/accel-limited turn, weak-brake overshoot, correlated OU aim bias, per-target misjudgement offset, trigger discipline | `AimController::Step` → `AimOutput{yaw/pitch_delta, residual_error, fire_allowed, overshot}` |
| `bot_loadout.h` | weapon scoring table + hysteresis (dwell/switch margin) | `ScoreWeapon`, `BestWeapon`, `WeaponSelector::Update` |
| `bot_human.h` | the vertical slice: perception → target → aim → weapon → movement intent | `HumanBotPolicy::BeginTick/PlanLosQueries/Step` → `BotCommand` |
| `botcore_ai.h` | legacy fixed-priority combat + waypoint graph + stuck detection (recovery layer) | `SelectTarget`, `SelectWeapon`, `WaypointGraph`, `StuckDetector` |

**Design intent (from the headers):** the layer produces *intent only* —
delta angles, forward/strafe factor, a fire bit and a weapon number. It is
deterministic, seeded, allocation-free and unit-testable without Retail. It
explicitly does **not** solve navigation: without a visible target the bot turns
in place and scans.

## 2. How intent reaches the engine (`poc/ai-integration/gamemp/BotDriver.cpp`)

The integration block (guarded by `bot_bHumanAI`) is the *only* place the
decision chain meets Retail. Per tick it:

1. Builds a `WorldView` from the local player's eye placement, health,
   `CombatUsableWeapons(available, ammo)` and `m_iCurrentWeapon`.
2. Calls `NotifyDamage(lastHealth, health)` on a health drop, then `BeginTick`.
3. Snapshots up to 16 replicated players into `SenseInput[]` (positions,
   `en_vCurrentTranslationAbsolute` velocities, health).
4. `PlanLosQueries(sensed, count, needsLos)` budgets rays; the caller casts them
   with `BotCombatVisible(...)`.
5. `Step(...)` returns a `BotCommand`; the driver copies `target/weapon/yaw/
   pitch/forward/fire/strafe` into its combat decision.
6. **Fire gating:** `bFire = (humanFire && testAimReady) || respawnPulse`, where
   `testAimReady = decision.fireAllowed && m_iCurrentWeapon==combatWeapon &&
   m_iWantedWeapon==combatWeapon`. So the trigger is held unless the weapon
   switch is fully acknowledged.
7. **Weapon select** via `CombatWeaponInput::Poll` (retail select-*group* pulses
   `1..8 << 14`, with a rising-edge/acknowledgement handshake).
8. **Movement:** `pa_vTranslation(3) = -moveFactor`. The lateral component
   `pa_vTranslation(1) = Clamp(humanStrafe * bot_fStrafeScale, -1, 1)` is written
   **only when `bot_fStrafeScale > 0`** — the shipped default is 0.
9. `ppls->SetAction(pa)` hands the action to the network player source.

Two integration facts matter for QA and are pure code, not simulation:
* **F1 — strafe is dropped by default.** With `bot_fStrafeScale=0` the policy's
  lateral evasion never reaches the engine.
* **F2 — fire requires weapon acknowledgement.** A switch in flight suppresses
  the trigger even when aim is settled and the target is visible.

---

## 3. The 15 behaviour areas vs the code

### (1) Reaction times
`Perception::ReactionTicks()` = `reaction_s·20` (tier 1: 0.55 s → tier 5:
0.15 s), **shortened to ⅓ while `alerted()`** (after `NotifyDamage`). A target
becomes `Selectable` only after `tick − first_seen_tick ≥ ReactionTicks`. So
reaction is modelled as continuous-LOS dwell before acting. *QA angle:* measured
end-to-end as `t_first_fire_eff_s` (first LOS → first acknowledged trigger).

### (2) Aim accuracy
`AimController` drives a rate-limited, accel-limited arc toward
`desired + bias + offset`, where `bias` is an OU process (σ=`aim_sigma_deg`,
τ=`aim_corr_s`) and `offset` is a **per-target fixed misjudgement drawn once per
target** (`Gauss()·σ·0.8`). `residual_error_deg` is the *true* error vs the aim
point; `perceived_error_deg` (what gates the trigger) includes bias/offset, so
the bot can "feel" aligned while truly off. *QA angle:* `true_err_visible_mean`,
`aim_err_policy_fire_mean`, `overshoots`.

### (3) Target tracking
Tracking is the aim loop following a moving aim point. `overshoot`
(`brake = accel·(1 − 0.75·overshoot)`) makes weak profiles swing past and
recover. *QA angle:* tracking error on `tracking_strafe`/`tracking_orbit`;
overshoot event count.

### (4) Leading moving targets (Vorhalten)
`bot_human.h` applies lead **only when `wp.proj_speed > 0`**:
`aim_point += v·(dist/proj_speed)·prediction_gain`. **Hitscan weapons
(`proj_speed==0`) get no lead at all.** `prediction_gain` is tier 1: 0.05 →
tier 5: 0.90. *QA angle:* `long_range_lead` (projectile competence) and
`hitscan_latency` (the missing hitscan lead path under replication delay A7).

### (5) Hit probability
Not modelled in botcore (the engine registers hits). `bot_loadout.h` carries an
`AccuracyAt(distance)` *hypothesis* used for weapon **scoring**, not for hit
resolution. *QA angle:* the simulator supplies a documented geometric hit model
(A3) so relative hit probability is measurable; absolute values are assumption-
bound and `NEEDS RETAIL` for truth.

### (6) Weapon switching
`WeaponSelector::Update` keeps the current weapon unless a rival scores
`> switch_margin×` **and** `weapon_dwell_s` elapsed (anti ping-pong). Selection =
`ScoreWeapon = dps_rel · AccuracyAt · RangeFit · personality-tilt`. *QA angle:*
`weapon_switches`, `weapon_switch_wasted_ticks`, `weapon_distinct`, and the
`--weapon-curve` probe of `ScoreWeapon` vs distance.

### (7) Combat ranges
`HumanBotPolicy::PreferredRange` = `0.35·weaponBand + 0.65·skill.preferred_range_m
+ personality.range_bias_m`, clamped [4,45]. `skill.preferred_range_m` rises
monotonically (7→9→12→16→22 m). *QA angle:* `dist_mean_m`, `in_band_pct`.
**Watch-item:** higher tiers self-select *longer* ranges, which interacts with
the accuracy table (see findings).

### (8) Movement behaviour
`MoveIntent`: beyond `preferred+3` → advance (`0.55+0.45·aggression`); inside
`preferred−3` → back off (`−0.6`); in band → lateral strafe
(`strafe_bias·(0.5+0.5·|sin|)`), with a deterministic direction flip every
`60+(seed%61)` ticks. No jump/crouch; no navigation while searching (scan only).
*QA angle:* `approach_uptime`, `retreat_uptime`, `strafe_cmd_uptime`,
`still_pct`, `path_len_m`. **Integration fact F1:** strafe is dropped unless
`bot_fStrafeScale>0`.

### (9) Retreat decisions
`retreat_below = skill.retreat_health·(0.6 + 0.9·personality.caution)`; when
visible and `health_frac < retreat_below`, `forward = −0.85` plus a small strafe.
`retreat_health` tier 1: 0.55 → tier 5: 0.28; `caution` e.g. survivor 0.90 vs
aggressor 0.15. *QA angle:* `retreat_events`, `hp_at_first_retreat`,
`survival_s` in `retreat_pressure`/`firefight`. **Watch-item:** retreat moves the
body but does not break LOS or seek cover.

### (10) Difficulty gradations
5 tiers, every `SkillParams` column monotonic by construction; personalities
applied afterwards and (by `SkillUnaffectedByPersonality`) cannot touch skill.
*QA angle:* the 11 invariants, esp. I4 (aim monotonic), I5 (hit spread),
I6 (reaction order), I11 (DPS monotonic), I9 (duel gradient).

### (11) Bot personalities
6 personas affecting only *desire* (`aggression`, `range_bias_m`, `strafe_bias`,
`caution`, `range_preference`, and `kFlaky`'s `mood_period_s`/`mood_swing`
via `EffectiveAggression`). *QA angle:* persona sweep + I7 orthogonality
(persona must not shift pure aim error).

### (12) Kill/Death ratios
No native K/D in the decision layer. *QA angle:* policy-vs-policy **duels**
produce win/loss/draw under the sim damage model; labelled simulation, `NEEDS
RETAIL` for true K/D.

### (13) Frags per minute
Same as (12): not a decision-layer quantity. *QA angle:* duel duration and
`sim_dps` are proxies; **must not be quoted as retail frags/min.**

### (14) Multiple opponents
`ChooseTarget`: score `1/(dist+1)` with a `1.35×` stickiness for the current
target, a post-switch hard-lock for `ReactionTicks`, and a switch only when a
rival is `1.4×` closer. `PlanLosQueries` prioritises existing tracks so a tight
ray budget never drops the current opponent. *QA angle:* `multi_2v1`/`multi_3v1`
`focus_share`, `target_switches`, `nearest_not_chosen_pct`.

### (15) Differences between bots
`DeriveSeed(base, slot, tier, persona)` guarantees distinct random streams;
`DefaultRoster` spreads 8 bots across tiers/personas. *QA angle:* per-seed
variance and between-group separation (tier/persona effect sizes) in the report.

---

## 4. "Bad score ≠ bad aim" — root-cause hypotheses (tested in document 3)

The task warns that a poor score must not be read as poor aim. Concrete
candidate causes, each mapped to a code location and a simulator probe:

| Hypothesised cause | Code locus | Simulator probe |
|--------------------|-----------|-----------------|
| **Missing fire release** (trigger held by weapon ack) | F2: `testAimReady && current==wanted` | `shots_blocked_switch`, `weapon_switch_wasted_ticks` |
| **Unsuitable / dominant weapon** | `ScoreWeapon` table | `--weapon-curve`, `weapon_mode/distinct` |
| **Poor movement (no evasion applied)** | F1: `bot_fStrafeScale=0` | strafe A/B (`strafe_cmd` vs `strafe_applied`) |
| **Slow target acquisition** | `ReactionTicks`, `search_rate_deg_s`, FOV | `reaction_static`, `reaction_turn90`, `damage_alert_behind` |
| **Missing opponent prioritisation** | `ChooseTarget` distance+stickiness | `multi_*` `nearest_not_chosen_pct`, `focus_share` |
| **Too-frequent target switches** | `1.35×` stickiness, `1.4×` switch rule, hard-lock | `target_switches` |
| **Poor positioning** | `PreferredRange` (rises with tier) | `dist_mean_m`, `in_band_pct` |
| **Unsuitable skill parameters** | `SkillFor` σ / range / reaction columns | tier sweeps; hit-floor & range-inflation findings |
| **Hitscan has no lead** | `proj_speed==0` branch | `hitscan_latency` latency sweep |
| **Retreat doesn't break LOS** | `MoveIntent` straight back-off | `retreat_pressure`/`firefight` `survival_s` |

Each row is answered with numbers — and each number is explicitly a
**simulation** result, with the retail-only truth flagged `NEEDS RETAIL`.
