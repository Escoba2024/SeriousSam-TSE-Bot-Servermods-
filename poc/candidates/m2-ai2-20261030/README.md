# M2 Human AI 2.0 — unqualified source candidate

Reuses the exact C1 PR57/PR66 composition. No second policy, target selector or
respawn clock. Five mechanical tiers and six existing personalities are retained:
Aggressor, Survivor, Duelist, Controller, Marksman, Flaky.

```
python3 poc/candidates/m2-ai2-20261030/verify.py
python3 poc/candidates/m2-ai2-20261030/verify.py --sanitize
python3 poc/candidates/m2-ai2-20261030/apply.py --gamemp NEW_OUTPUT
```

The output is a flat source overlay for `tools/build_integrated_gamemp.py`.
Existing paths are rejected. SOURCE_MANIFEST.json preserves upstream provenance,
patch hashes and actual output hashes. Source/build success does not qualify a DLL.

Changes relative to the reviewed C1 composition:

- Death/absence/exclusion and changed replicated player pointer invalidate a slot's
  memory and aim. Retained pointer values are compared only, never dereferenced.
  Living occluded players keep their frozen last-seen position until memory expires.
- Native shot cadence commits only after final accepted combat `SetAction`, with
  tick/weapon-matched acknowledgement. Portable users retain immediate commitment
  unless explicitly configured otherwise. Emitted fire input is not a shot/hit counter.
- No combat fire with an empty usable mask. Knife/chainsaw require <=2m and
  healthy bots close to 1.5m; hurt bots retain retreat priority. Reach values are
  conservative policy assumptions pending native qualification.
- Recovery suppresses combat strafe, owns yaw/translation and vetoes fire. Human
  stationary intent replaces the old unconditional 8m recovery hold.
- Reverse/lateral commands get at most two existing wall rays at the two possible
  movement headings; <1.2m or nonfinite clearance vetoes both axes. This is bounded
  local wall avoidance, not ground lookahead, swept collision or an M3 path planner.
- New optional `bot_iSkillTier` (1..5) and `bot_iPersonality` (0..5) independently
  configure profiles before attach while preserving identity. Defaults -1 and
  invalid values retain the roster. Existing weapon2/lead2/strafe2/P1 opt-ins stay OFF.

Set existing experimental symbols before attach in isolated tests. Meaningful
observation-age tuning requires measured position age; unknown remains zero.
Finite-ammo fallback is separate from infinite-ammo preset behavior. Damage
awareness currently observes health drops, not armor-only hits.

Evidence and remaining native gates are in docs/reports/2026-10-30-m2-ai2.md
and docs/coordination/M2-CONTINUATION.md. M1 stays IN_PROGRESS / NOT_ACCEPTED;
no eight-bot test, public activation, qualified-DLL replacement or main merge.
