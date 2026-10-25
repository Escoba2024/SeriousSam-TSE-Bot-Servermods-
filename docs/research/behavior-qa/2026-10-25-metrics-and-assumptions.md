# Quality Metrics, Simulation Assumptions & the Retail Boundary

Stand: 2026-10-25 · Base SHA: `107d28a276c4fe4428cc3c8bf5bbd876e1a85351`

This document defines every metric the QA harness emits, lists the simulation
assumptions those metrics depend on, and draws the line between what the
**offline simulation** may claim and what **only retail telemetry** can answer.

> **Prime directive.** A metric value is a property of
> `(botcore Human-KI code × assumptions A1–A9 × scenario × seed)`. It is
> reproducible and comparable, but it is **never** a retail measurement, a
> native acceptance, or a human benchmark. Relative deltas (tier vs tier,
> persona vs persona, config A vs B) are the signal; absolute magnitudes carry
> the assumptions' uncertainty.

---

## 1. Simulation assumption register

All assumptions live in `qa_world.h` and are echoed into every JSON record's
`config` block. Each is overridable on the CLI so its influence can be measured.

| ID | Assumption | Default | Why / caveat |
|----|-----------|---------|--------------|
| **A1** | Planar arena, eye height 1.7 m, no gravity/jumping | — | Keeps geometry 2.5-D; vertical play is out of scope |
| **A2** | Body move speed, linear in forward/strafe factor | 7.0 m/s | Retail `plr_fSpeed*` **not verified here** (`NEEDS RETAIL`); relative only |
| **A3** | Hit model: miss distance `d·tan(err)` vs radius `0.6·(0.25+0.75·AccuracyAt)` | radius 0.6 m | Uses botcore's own accuracy *hypothesis*; sets an absolute hit-rate scale that is assumption-bound |
| **A4** | Damage: `dps_rel × scale` sustained; per-shot `× interval` | scale 20 HP/s | Retail weapon damage **not extracted** (`NEEDS RETAIL`); relative DPS only |
| **A5** | Per-weapon fire intervals (sim cadence table) | see `WeaponIntervalS` | Not retail cadences; drives TTK/DPS scale |
| **A6** | Weapon switch latency, pulse → acknowledged | 6 ticks (0.3 s) | Retail switch time **not verified** (`NEEDS RETAIL`); mirrors the integration fire gate F2 |
| **A7** | Perceived enemy state delayed by `latency` ticks | 2 ticks (100 ms) | Replication+network delay **not measured** (`NEEDS RETAIL`); swept 0/2/4 |
| **A8** | Hitscan never hits beyond `1.5 × weapon max_m` | — | Damage-falloff cutoff; prevents absurd long-range pistol hits |
| **A9** | Scripted enemy return fire falls off as `clamp(ref/dist, 0.25, 1.0)` | — | Makes retreat-open-range reduce damage; **not dodgeable**, so it cannot show evasion benefit |

**Consequences you must respect when reading results:**
* Absolute hit-rates, TTK and DPS inherit A3–A5. Compare them *relatively*.
* A6/A7 are the two knobs that turn integration facts (F1/F2) and network delay
  into measurable cost; they are hypotheses, so their magnitudes are indicative.
* A9 makes `survival_s` meaningful only against return fire, and even then it
  rewards *range*, never *lateral dodging*.

---

## 2. Metric catalog

### 2.1 Timing / reaction
| Metric | Definition | Reads as |
|--------|-----------|----------|
| `t_first_selectable_s` | first tick the target is `Selectable` (reaction dwell passed) | perception latency |
| `t_first_fire_policy_s` | first tick the policy sets `fire` | decision latency |
| `t_first_fire_eff_s` | first tick fire survives the integration gate (weapon acked) | **effective** reaction |
| `t_first_hit_s` | first simulated hit | time to first effect |
| `ttk_s` | `t_kill − t_first_selectable`, **only if a kill happened** | conditional; read with `kill_rate` |
| `survival_s` | sim-time to bot death, else run duration | tankiness **only** under return fire |

### 2.2 Effectiveness (robust)
| Metric | Definition | Why it matters |
|--------|-----------|----------------|
| `kill_rate` | fraction of seeds ending in `kill` | not conditional like TTK; the honest "does it finish" signal |
| `sim_dps` | `dmg_dealt / (ticks·dt)` | always defined; the headline "does skill → damage" metric (I11) |
| `hit_rate` | `hits / trigger_pulls` | accuracy of resolved shots (A3-bound absolute) |
| `dmg_dealt` / `dmg_taken` | accumulated sim damage | trade efficiency |

### 2.3 Aiming
| Metric | Definition |
|--------|-----------|
| `true_err_visible_mean/p95` | geometric error vs the **true** target on visible ticks (°) |
| `aim_err_policy_fire_mean/p95` | policy `residual_error_deg` on fire ticks |
| `true_err_fire_mean/p95` | true error at the moment of an effective shot |
| `overshoots` | aim-controller overshoot events (error sign change at speed) |
| `shots_gated_aim` | visible ticks where the trigger was held by settle/tolerance |

### 2.4 Fire gating & miss attribution (heuristic)
| Metric | Definition |
|--------|-----------|
| `shots_policy` / `shots_eff` | policy fire ticks vs those passing the integration gate |
| `shots_blocked_switch` | policy fire suppressed **only** by weapon-ack (F2 cost) |
| `trigger_pulls` | shots actually resolved after the fire-interval limit |
| `wasted_fire_invisible` | fire while target not visible — **must be 0** (I2) |
| `miss_range` / `miss_target_motion` / `miss_overshoot` / `miss_aim_bias` | dominant-cause split of resolved misses |

`miss_target_motion` = true target moved off the (delayed/lead) aim point
(captures latency + lead failure); `miss_aim_bias` = the aim point itself was
off (σ/offset/overshoot). Attribution is a labelled heuristic, not ground truth.

### 2.5 Weapons
| Metric | Definition |
|--------|-----------|
| `weapon_switches` | post-initial weapon changes on engaged ticks |
| `weapon_switch_wasted_ticks` | engaged ticks lost mid-switch |
| `weapon_mode` / `weapon_distinct` | modal weapon held / number of distinct weapons held |
| `--weapon-curve` | direct `ScoreWeapon(distance)` read-out: best weapon + runner-up margin per metre |

### 2.6 Targets / perception
| Metric | Definition |
|--------|-----------|
| `target_switches` | policy counter delta (opponent changes) |
| `focus_share` | share of resolved shots on the single most-shot opponent |
| `nearest_not_chosen_pct` | engaged ticks where a ≥25 % closer live enemy was ignored |
| `los_queries_max` / `ray_budget_skips` | rays planned (must be ≤ tier budget, I3) / candidates dropped by budget |

### 2.7 Movement / positioning
| Metric | Definition |
|--------|-----------|
| `dist_mean/min/max_m`, `in_band_pct` | engagement distance and time within ±3 m of `preferred_range_m` |
| `preferred_mean_m` | the policy's own preferred range (rises with tier) |
| `move_fwd_mean`, `approach_uptime`, `retreat_uptime` | forward intent statistics |
| `strafe_cmd_uptime` / `strafe_applied_uptime` | lateral **intent** vs lateral **motion actually applied** (`strafe_scale`) |
| `still_pct`, `path_len_m`, `net_disp_m`, `corner_pct` | movement volume and arena-border pinning |
| `retreat_events`, `hp_at_first_retreat` | health-driven retreat episodes (per the `MoveIntent` threshold formula) |

### 2.8 Duels, performance, determinism
| Metric | Definition |
|--------|-----------|
| `winner`, `wins_a/b`, `draws` | policy-vs-policy outcome (sim K/D proxy) |
| `ns_per_tick` | decision-layer cost per tier (perf guard I8; **not client CPU**) |
| `digest` | FNV-mix over the rounded metric vector — the reproducibility token (I1) |

---

## 3. Reproducibility model

Every run is a pure function of `(scenario, tier, persona, seed, config)`. The
`digest` (2.8) summarises the metric vector; `run_behavior_qa.py --compare`
re-runs and diffs against `baseline/qa_baseline.json`:

* **Invariant flip** PASS→FAIL → regression.
* **Aggregated tier metric** moved > 25 % → regression.
* **Loadout dominant-weapon histogram** changed → regression (a rebalance is a
  deliberate behaviour change and should be re-baselined consciously).

Determinism (I1) is asserted in both the C++ `--selftest` and the Python suite.
Because the code is seeded and allocation-deterministic, an *unmodified* botcore
reproduces the baseline exactly; any delta points at a real change.

---

## 4. Simulation ↔ retail boundary

| Answerable OFFLINE (this harness) | `NEEDS RETAIL` telemetry |
|-----------------------------------|--------------------------|
| Is aim skill-monotonic under fixed geometry? | True hit registration / hitbox sizes |
| Does reaction/dwell order tiers correctly? | Real weapon damage & cadence (replaces A4/A5) |
| Does the weapon table have a dominant strategy? | Real `plr_fSpeed*` (replaces A2) |
| Does the policy ever fire without LOS? (contract) | Real weapon-switch latency (replaces A6) |
| Does latency cost hitscan accuracy on movers? (relative) | Actual replication/network delay (replaces A7) |
| Is the decision step within a per-tick CPU budget? (relative) | Real client CPU / GameMP.dll cost, sync stability |
| Do personas stay orthogonal in pure mechanics? | True K/D and frags-per-minute on a live server |
| Does retreat extend survival vs range-falloff fire? | **Evasion benefit of strafing** (A9 can't dodge) |

The existing runtime evidence pipeline (`BotTelemetry.h`, `[BotHuman]` log
lines in `BotDriver.cpp`) is where the retail column gets filled: it already logs
`target/vis/fire/weapon/dist/pref/move/strafe/err/rays/skipped/switches/
overshoots` per tick. **Recommendation R8** in document 3 maps each offline
metric onto those fields so retail logs can confirm or refute the simulation.
