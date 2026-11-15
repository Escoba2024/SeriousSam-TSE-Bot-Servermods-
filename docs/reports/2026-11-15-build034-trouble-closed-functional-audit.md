# Build034 Little Trouble: closed300-second observation audit

The new attempt-bound circulation safeguard was exercised once: a `revisited_edges` abort ended a held Weapon goal, followed by an ordinary Armor goal and then a Weapon5 goal. A same-life Weapon5 inventory gain was observed later, but its sampling interval overlaps the Weapon5 `unavailable` witness. This establishes the exercised abort and later observations, **not a causal pickup ACK or a Native improvement claim**. A separate43.652664-second life still had no useful weapon. No gameplay change or A4 acceptance follows from this audit.

The original case remains `PASS_LIMITED_REACQUIRE_DIAGNOSTIC_OBSERVATION_ONLY`:300.021755 seconds, four normal closes, four closed logs without BAD/disconnect, independently restored by Root. No Raw or old031/032 replay, build, Runtime, Frida or live action was performed here.

## Complete bounded denominators

Unchanged ordered V3/life checks validated7077 read attempts, retaining190 failed attempts;3 paused smoke samples and all three provenance groups remain distinct. There are149 observed lives, including3 corpse-only lives,87 left-censored and8 right-censored lives,141 observed deaths,73 useful-possession lives and101 strict same-life useful inventory gains. No slot is absent. These are memory observations, not continuous simulation snapshots.

| Own slot | Observed lives | Useful-possession lives | Useful gains | Fire-flag observations with same-life Source growth | Maximum1m stationary span(s) |
|---|---:|---:|---:|---:|---:|
|0|17|11|14|175|1.150070|
|2|22|11|13|176|2.100128|
|3|16|6|8|114|2.650162|
|4|19|10|15|201|1.149982|
|5|16|8|11|175|1.049744|
|6|23|7|12|170|1.949970|
|7|20|9|15|147|2.099968|
|8|16|11|13|256|1.500006|

All eight have observed position changes, inventory gains and Native fire flags with qualified same-life Source counter growth. A flag is not a weapon-function/shot/damage ACK. Endpoint chords and stationary spans do not establish collision-free routes. The single server log has121 player-kill-template records (81 lead,37 blast,3 telefrag) and25 self-blast records; peer copies are not summed. The inherited exact query-name join did not bind those console names, so per-slot/per-life killer attribution is UNKNOWN. Query frags are not substituted for kills. No flight-finish row occurred;42 Reacquire rows include34 context-only,6 support-motion-guard and2 accepted proposals. Four HopCheckpoint rows are not successful route/teleport/jumppad proofs; GroundReplan and ImportantOriginRecovery are unexercised in these retained events.

## Complete new custody denominator

Both process serial sequences are contiguous:328 and342 rows,670 total. There are179 ARM,179 DISARM,179 END and133 pre-admission UNADMITTED rows. No CAP, FORMAT, malformed row, serial gap, duplicated domain phase or open admitted tail was found.643 rows bind to a Source/Native life;27 remain explicitly UNKNOWN rather than gaining Native evidence. Client world pointers and Source clocks remain separate from server Native values.

DISARM reasons are76 `goal_clear`,51 `eligibility_false`,51 `owner_lost` and1 `history_full`; all179 END rows use `goal_clear`. Combined raw reason totals are255 `goal_clear`,184 `eligibility_false`,179 `first_entry`,51 `owner_lost`,1 `history_full`. The133 pre-admission rows are included in eligibility_false; not every eligibility veto was a new admitted history. Thus the new diagnostic budget remained below the1024/process cap, but it does not make throttled or absent engine observations complete.

The single exercised abort has one exact admitted domain and an unextended printed goal deadline. It occurs after10 Source seconds without the required directed-edge progress; the whole attempt runs about14.9 Source seconds, before its fixed goal deadline. After the abort: Armor goal→unavailable→Weapon5 goal→unavailable→later Weapon3 goal, then death. Native owned-mask3→19 (Weapon5 bit16) appears in an adjacent-observation interval containing the Weapon5-end WPO witness. The broad WPO interval around the initial abort prevents a precise Native abort timestamp or a causal attribution to the old Weapon9 target. The private receipt retains Source lines, Native read serials, actual masks and conservative clock intervals.

## Longest remaining no-Useful life and ownership

The longest observed no-Useful life lasts43.652664 seconds, ends in observed death and is left-censored. Native HP ranges25–100; owned masks3/7 and current weapons1/2/3 represent Knife/Colt/DoubleColt, with no useful weapon. It traverses322.44m of sampled position chords; its longest1m-stationary span is0.500031 seconds. Continuous or ranged Colt firing is not established.

Its source sequence includes Weapon3→unavailable, mapped Weapon9→unavailable, mapped Weapon8→unavailable, Health→unavailable, another mapped Weapon9 held until death. Forty sampled picker batches contain26 held-goal gate-zero cases and14 open normal-picker cases;15 sampled attempts are12 no-choice,2 committed and1 visibility rejection. Thirty-one arbitration receipts took the proposal. This distinguishes a held supply target from simple lack of motion, without inventing a globally nearest available weapon pool or a pickup cause.

Both Weapon9 histories ARM and then DISARM with `owner_lost`, remain disarmed and end on goal clear. Existing Source binds this marker to `BotCecilSafeMotion(!useReacquire)`; Driver passes `supplyActive!=FALSE`. Around the first marker, the preceding Driver receipt is supply-owned and the following receipt has `supplyActive=false`, combatHold/visible-target and combat recovery true. The second shows the same lane transition. Both retain Actor/generation/life binding, but neither exact marker tick was Driver-sampled: these are1Hz brackets, **not same-call ownership proof**. Source current weapon remains DoubleColt, and Source HP is70 then25 in the following rows. No blanket combat/supply priority change is justified by this evidence.

All51 owner_lost markers were selected from the same retained RAM logs and joined to2536 existing strictly typed DriverFinal rows.48 have a preceding supply-owned receipt,39 a following combat-owned receipt,11 a following supply-owned receipt, and one lacks a following same-actor receipt. Three have a matching printed Source-time Driver witness. These aggregate brackets cannot turn the other48 unsampled transitions into exact causes. The primary physical reason for failure to acquire the held Weapon9 remains UNKNOWN; no new diagnostic Native retry or Gameplay fix is proposed here.

## Reproduction and provenance

Source uses the existing corrected Hole031 reader through a complete reversible case transform; its original algorithms and disk guard remain intact. Prospective admission:64MiB/stream,16MiB/log,32MiB all logs,128MiB total; main Raw sizes61767866B. Core actual input63365385B includes metadata and Source. Final output4811141B is below8MiB; every write retains the absolute8GiB floor plus64MiB reserve, exclusive0600 creation and fsync. No Raw duplication or old-case replay occurred.

Run in ONE Python process from the isolated source tree with `PYTHONPATH=tools`:

```python
import audit_trouble034_closed as a
import trouble034_ram_conclusions as f
a.main()                 # exactly one Native Raw acquisition
f.complete(a.C)           # retained RAM and small outputs only
```

The target output directory must be fresh. Raw archives may require Root's exact lossless rehydration first; this reader has no invented fallback. Do not rerun merely to obtain another result.

New pointer/duplicate/width behavior checks first failed3/3 against the actual old lexer. Root caught stale Host/Restore literals before Raw; the actual034 binding test failed then passed. A missing `json` dependency and an interactive `__file__` invocation failure also occurred before acquisition, were preserved and corrected; they are not Raw passes or Native failures. Final19 pure tests pass0.097s. The finalizer subsequently executed all51 ownership selections using the existing strict Driver parser without an old-case replay. These are portable parser/selection checks, not Runtime qualification.

Executed coordinator SHA `ad942928daaca4226bda5b08b01d52825dccaae9a395712ff772856d01300e77`; strict history parser `2628778ff7c1d696b3767ab2ba192dd9314f00a13bf85c4d0e69a4d5ba3cea15`; separate RAM finalizer `d9d99b6b20acc0d61cb9c538d6bb444a1c4282c5b40a802c4a788160203888b4`. The original whole-reader inverse restores `475ddc0a9ea17020873e6733964b3d93abdb8c3a8005e6871fe338db466e0f0e`.

Private canonical handoff: `/srv/tse-trouble034-closed-audit-evidence-20261115/complete034-handoff.json`, SHA `7f941ff31ec8ca24b2a3b5494774e66aef7a6a8f38422cf19f41af366db983db`; core-stage receipt SHA `1f05e5821090b3d0ebc42931c7d81d8a338b3a6ab887fdf8249cdf14c346072c`; focused full custody SHA `ca909ba0c18473e0cb9d42f07d41827e6fb23d9a3fce3e14c2308aeda217b87f`. Earlier receipts remain explicitly identified checkpoints. Private test/run proof manifest SHA `fa289674a7894e708175f054a379a44e47bf1d89f2f4255ac0c5fdb0f8433ad4` is under the isolated worktree's `.codex/evidence/trouble034-closed-audit-proof/`.

The300s window differs from older600s conditions; no duration-normalized performance,031/032 causal improvement, map ranking, A4 qualification or promotion is claimed. All reader handles are closed and the RAM interpreter exited0. Root alone reviews, integrates and decides subsequent Runtime work.

## Review correction: printed9-significant-digit Source-time bins

Root review found that the RAM finalizer used the textual Decimal exponent to infer print precision. For a trimmed `%.9g` string such as `159`, that incorrectly gives a half-second bin. Five tests against the actual `owner_context` call path reproduced the error before correction: integer, exponent spelling, zero, negative value and decade boundary. The replacement uses9 significant digits (`adjusted()-8`), exact zero, and the narrower predecessor bin at a power-of-ten boundary. No Source/Native clocks are fused; matching a print bin is still not an exact same-call/ordinal proof.

No Raw replay or full51-marker recomputation was performed. The old bins were supersets, so the new pure recheck reads only the previously pinned small `functional-focus-ram.json` and checks its three old candidates. All three remain: actual Source values40.0,57.0 and60.0 match bins of half-width0.00000005, replacing the old0.5. This preserves the reported count while correcting the verifier; the two longest-life markers still lack a matching Driver row. All original outputs and the earlier handoff remain unchanged historical checkpoints.

Correction Source SHA `4c31b7f4b154af34a67c789b7f12e4124da8cd26586a0283f07817e1b676739e`;24 focused tests PASS0.101s after5/5 expected behavior failures. New private `printed-source-time-correction.json` is1723B, SHA `26f91071b0853beb1b6d593dba646556ca36d261d8ae813e6ee2d581a17799ff`. Reproduce this addendum by passing the original focus JSON to `trouble034_ram_conclusions.recheck_prior_candidates(value)`; its three-candidate denominator is checked against the old receipt. Do not invoke the Native reader for this correction.
