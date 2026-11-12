# A4 phase activity and rotation continuity implementation plan

> **For agentic workers:** Use superpowers:executing-plans task by task. Preserve all failed native evidence; Root owns independent review, integration, builds and native execution.

**Goal:** Explain the per-phase pickup/fire gaps and correct a proven cause without weakening eight-bot activity or reset acceptance.

**Architecture:** First separate incomplete observation from absent behavior using full phase logs, captured native inventory and the exact Build015 source. If rotation state crosses a map/life boundary incorrectly, reproduce that production boundary offline before a minimal normal-action correction. Prepare a separate disabled observation package only after the source finding; a new longer protocol, if justified, must have a new identity and fixed bounds.

**Tech stack:** Python read-only evidence analysis, existing C++ Driver/native-shaped regressions, private Python controller.

**Spec:** Root's bounded A4 follow-up and pitch-priority delegation on 2026-11-12; persistent claim `/srv/tse-milestone-a-continuation-evidence-20261112/a4-phase-activity-claim.json`.

## Global constraints

- Own worktree `/srv/tse-milestone-a-a4-phase-activity-completion-20261112`, branch `codex/20261112-a4-phase-activity`, base `0e7deda04b06571a83da1342b7f13d10347eda74`.
- No old package edits, live fixture writes, native starts, DLL builds, process controls or broad resource tests. Names/A3 windows belong to Root.
- The original 300-second protocol and trial `a4-reset015-lowrender-readable-20261112-092421` remain unchanged/FAIL.
- Preserve required useful pickup and native ranged-fire evidence for each of eight bots in every phase, plus all existing mapping, world, identity, resource, 50-second transition and 19-second close guards.
- Do not equate body pitch with view pitch, action emission with native firing, left-censored possession with observed pickup, or 1.10 source with verified Retail behavior.
- A new private package remains GateFalse; Root alone reviews/freezes/runs it.

## Review focus

- Reused local source/entity identifiers across a normal map reload must not carry stale orientation decisions into a fresh native player.
- Respawn and map reload have different native input baselines; do not zero cumulative native fields or bypass normal action composition.
- One-Hz fire status can miss real emitted actions; cumulative counts remain separate from native ranged-fire acceptance.
- Early inventory must bind to fresh load offsets, actual map execution, native player identity tuples and the newly observed local-to-global mapping.
- Bouncer route evidence, absent actual Teleport entities, item pickup and reset evidence require a scoped RedStation decision, not blanket qualification.

## Tasks

- [x] Verify isolated worktree/claim and read project instructions/tool policy.
- [x] Produce compact phase/local-bot evidence table: log coverage, pickup transitions, cumulative fire deltas, inventory start, native ranged-fire observations and pitch continuity.
- [x] Trace actual Build015 Driver and original input/map/life reset behavior; confirm or reject a causal rotation-state defect with explicit limits.
- [x] Before implementation, send Root the finding and precise plan. Write a meaningful RED regression at the actual production boundary, then implement the minimal correction and prove GREEN. If no defect is established, leave C++ unchanged.
- [ ] Prepare a new disabled private observation package if required: early passive samples during observer restart, strict fresh-phase/entity binding, complete failure receipts and unchanged activity requirements. Any longer protocol requires a separately named fixed design justified by measured coverage.
- [x] Review existing RedStation Bouncer/items/reset evidence; state the exact remaining map-whitelist risk instead of treating all qualification as permanently false.
- [ ] Verify bounded tests, preservation/pins and normalized deltas; write sanitized report, commit own changes and hand off disabled package plus Root run plan.

## Ledger

- Root created the isolated worktree with a direct permitted Git operation after RDC rejected two Python read-only commands. Only explicit file reads/searches/writes are used in this worker until an allowed test path is established; rejected commands are not reissued through another route.
- Native trial confirms ordered begin scripts 1/2/3 and time limits 1/1/0; reset sequence observed, all roles normally closed, retained logs accepted, exact restoration. Activity failure remains authoritative.
- Phase 1 native inventory starts at game tick 19.949981689453125; phase 2 at 15.1000394821167. Controller creates its new InventoryReader only after observer rejoin/readiness. B1/B2 (phase 1) and A0/A2 (phase 2) already possess useful weapons at their first inventory sample.
- Full phase-2 A0 log has 75 sampled fire=0 rows, but cumulative emitted fire actions rise 172 to 182. Phase-2 A2 acquires Shotgun at action tick 3656, emits Shotgun firing inputs before inventory starts, and cumulative fire count rises 140 to 178. These are evidence blind spots, not permission to substitute action counters for native-fire evidence.
- Separate pitch hypothesis has priority: phase-2 A0 starts with view pitch 90, input/composed/last pitch 173.4698792 and keeps that view through its first observed life. The root Driver and Build015 overlay are text-identical. The initial source inspection found new-player-source reset clears requested angles while entity-change reset and BotResetNavigation did not; this was a hypothesis until the later native-baseline inspection and RED test below.

- Confirmed production-boundary defect: old requested pitch survives persistent PlayerSource/new entity; ordinary respawn retains cumulative native basis and must not be zeroed. Root approved the narrow baseline-adoption change after actual-path RED: 18 checks, 8 behavioral failures, compilation successful.
- Own source now adopts finite native LastRotation into own desired angles at Attach/map serial/original input identity boundary, under the existing world lock. Original/predicted identity and world must agree. No native angle writes, gain/FOV changes or per-tick rebasing. Optional boundary-only diagnostic records the prior values.
- Root independently verified unchanged original 18 checks GREEN, expanded actual-path ASan/UBSan 47 checks/0 failures (0.84s), and existing actual Driver action ASan/UBSan guards exit0 (1.05s). Source/SDK pins and receipts are in docs/reports/milestone-a-20261111/a4-rotation-epoch-source.json.
- Full phase-1 logs also establish real gaps: A2 never records a useful ranged pickup (only 3->7 twice), while B0 obtains Shotgun late and does not increase its fire counter thereafter. Early inventory alone therefore cannot close the whole activity gate.
- RedStation has no actual Teleport/PlayerActionMarker entity in the pinned world. Existing Bouncer/item and ordered reload evidence is concrete; remaining candidate qualification concerns phase-wide eight-bot activity and native effect of the corrected rotation baseline. No blanket transfer to other maps/liquids.
- Source report and five-file source commit are ready for Root commit/integration. Next, separately prepare epoch-bound inventory during observer rejoin, preserving the 300/50/19-second bounds and all pickup/fire requirements; do not edit old frozen controllers or failed trials.
