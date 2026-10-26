# Navigation/item completion implementation plan

Goal: repair QA03 multi-floor anchoring, QA04 Retail item/ammo semantics, and QA07 unprobed wall shortcuts in pinned offline candidate.
Architecture: retain pinned PR54/55/69 trees and contextual patches; controller remains default-off, offline-only, caller-owned combat. No BotDriver or native runtime edits.
Tech stack: C++14/17/20, Python3 standard library, existing g++ and make; serial nice19 tests.
Spec: Parent task and PR72 QA03/04/07; AGENTS.md and tool policy apply.
Authorized execution: autonomous inline; no approval or deployment step.

Review focus: stacked floors; overmax health/armor; shared ammo and infinite mode; unprobed/unreachable items; stale graph and ownership.

- [x] Task 1: Inventory imported uncommitted source with hashes, read native handoffs and QA evidence, prepare pinned real headers, run baseline.
- [x] Task 2: Add focused failing tests for floor selection and unknown route costs, patch generated upstream, run regressions and original suites.
- [x] Task 3: Add failing tests for legal overmax, ammo pools/weapon requirements/infinite ammo; patch item data/rules from original sources, run all candidate suites.
- [x] Task 4: Verify compatibility and sanitizer tests serially; review scope and document exact driver seam plus native blockers; commit own files only.
