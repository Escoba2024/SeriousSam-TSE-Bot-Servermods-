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
- [x] Prepare a new disabled private observation package if required: early passive samples during observer restart, strict fresh-phase/entity binding, complete failure receipts and unchanged activity requirements. Any longer protocol requires a separately named fixed design justified by measured coverage.
- [x] Review existing RedStation Bouncer/items/reset evidence; state the exact remaining map-whitelist risk instead of treating all qualification as permanently false.
- [x] Verify bounded tests, preservation/pins and normalized deltas; source correction committed, sanitized reports complete and disabled package plus Root run plan handed off. The final two documentation files are ready for Root's separate commit.

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

## Offline implementation handoff complete

- Source commit `bea377448cd03465b651d2c11059e4e0fda5c790` was integrated by Root as `58e8559903d999772218a6b5fd1d042b1759b547`. Root built Build016; manifest SHA `4cd6b5a8d853afe2dbe492fb12fff0aed22a06c77b5de7fc4e732795d2676603`, DLL SHA `e5a80634b5247c900ae25b5b18869c433c30dcfb49b890338fb231da63b04825`.
- Separate private package `/srv/tse-a4-phase-inventory-completion-20261112` opens the same Original reader before observer launch and captures phase-bound eight-bot frames inside existing bounded waits. Actual entity/log/process/world/time binding and later nine-player confirmation are required. Raw failure receipts precede rejection. Existing pickup/fire gates and 300/50/19-second bounds are unchanged.
- Root verified three actual-path RED failures, 7+10 targeted GREEN tests and finally the complete 130/130 suite in 0.731s. The only intermediate full-suite failure was the obsolete while-local Reader AST assertion; its exact helper-call/constructor adaptation and every remaining assertion are documented and normalized.
- Of 82 old pinned sources, 79 remain byte-identical; eleven lifecycle/evidence functions and the entire old operation-guard prefix are AST-identical. All 59 previous runtime dependencies were rechecked. The final new package has 111 source pins and 64 runtime pins.
- After A1 normally closed/restored, Root's final refresher succeeded. GateFalse manifest SHA `40abb08ff7fab1f71b0bf9359161c7d258fb26fdfffb3b1c3baf2925f3ded093`; controller SHA `bbe3a481bb3ac94e13e4e7a262db03d42fe8be48d4319213dc4ca986b8d9c789`; helper SHA `2ea407070b15ed8ed94a765c7bccfb6510805d0b89676ba774a4452eb4e15b73`; delta SHA `0bd4095caa9825253434a75bb39fa9419b8762dfa58f2ee77cbbee428f2c6a88`. The private package is now immutable for this worker.
- Final companion report: `docs/reports/2026-11-12-a4-early-phase-inventory.md`. Root owns the separate documentation commit, independent runtime freeze and one newly named native A4 attempt under the existing exclusive lock. No old failed result was reclassified, no live configuration was changed by this worker, and native A4 qualification remains open.
