# Cecil P1 native receipt comparability — 26 October 2026

## Decision
Historical Build04/Build06 four-bot PASS_LIMITED_SESSION_LIFECYCLE and Cecil P1 four-bot FAIL (SYNCBAD) are **NOT a controlled Cecil feature-flag A/B**. Do not attribute the native CRC divergence to Cecil P1 without new controlled experiments.

## Existing read-only native receipts
| Control | Control outcome | Candidate outcome | Gate | Confounders |
|---|---|---|---|---|
| Build04, four bots | 328.90s, PASS_LIMITED_SESSION_LIFECYCLE | Cecil P1, four bots, 97.93s, FAIL/SYNCBAD | CONFOUNDED, exit 3 | different DLL SHA256; different session qualification harness source hash; colors enabled in control but disabled in P1; control Cecil flag absent (NOT known false) |
| Build06, four bots | 326.51s, PASS_LIMITED_SESSION_LIFECYCLE | Cecil P1, four bots, 97.93s, FAIL/SYNCBAD | CONFOUNDED, exit 3 | same four differences |
| Cecil P1, one bot | 131.87s, PASS_LIMITED_SESSION_LIFECYCLE | Cecil P1, four bots, 97.93s, FAIL/SYNCBAD | CONFOUNDED, exit 3 | one-versus-four players; feature flag true in both; qualification harness source hash differs |

All are metadata observations of retained locally generated native test artifacts, not an independent current native A/B run. In particular, 4-bot failure does not establish first divergent engine tick, field, or root cause. Source provenance equality was enforced only for the named five harness files; this is necessary but not sufficient to rule out unknown external confounders. No raw log contents or private identifiers were copied into this report.

## Implemented gate
- \`tools/native_ab_comparability.py\` compares explicit control/candidate directory metadata (\`result.json\` and \`source-sha256.json\`); it does **not** access game processes, logs, ports or binaries.
- Fails closed when binaries, harnesses, game settings, native scope or 4-bot population differ, or explicit flag off/on cannot be proven. Exit 0 means controlled **receipt preflight only**, not native sync or release PASS; exit 3 means confounded; exit 2 invalid input.
- Reads optional outcome duration/status only as observations. Emits no GUIDs, IPs, raw log excerpts, client identities or paths.
- TDD verified a missing-module RED, a separate private-status leakage RED, and GREEN with 13 focused tests; repository \`tools\` suite: 56 tests PASS. A test suite result is NOT Retail gameplay acceptance.

## Controlled next native A/B
1. Acquire exclusive isolated test ownership, backed by verified public-process pins, backup hashes, 8 GiB free-disk reserve, CPU/RAM safety, and separate network namespace, Wine prefixes, native ports and test cgroup. Do not evict or instrument any public human player.
2. Start four owned bots + original Retail counterpart using **the same pinned Cecil P1 DLL, unchanged qualification script hashes and baseline settings**, explicitly \`cecil_p1=false\`. Run a bounded native control and save the observed receipt.
3. Repeat with the **same DLL and same environment** but \`cecil_p1=true\` as the only intentional change; preserve unchanged sync kick threshold and reproduce/measure the earliest bad sequence. Run longer only if resource and health gates permit.
4. Run this comparator first; treat a clean toggle verdict as a comparability preflight, *not* a root-cause verdict. Native paired authorized action/state/CRC captures and original-client activity are required for causality and Stable Candidate 1.
5. If the reference/flag-off run also fails, stop attributing the issue to Cecil feature logic and investigate native harness/runtime sources. If only P1-on fails, isolate target selection, fire cadence, respawn with one switch at a time and exact pinned DLL builds.

**BLOCKER:** A controlled four-bot same-DLL off/on run, full paired native CRC/engine-action producer and final source hour test have not been performed. Current two-vCPU production host is shared with an eight-bot public experimental generation. There was no safe isolated resource reservation in this read-only task. No production deployment, process signal, new native runtime, Git main merge, 24/7 claim or game/config change performed.

## Handoff
Worktree: \`/srv/tse-native-ab-comparability-20261026\`; branch: \`agent/chat/20261026-native-ab-comparability\`. Based on public \`main\` \`ab0c740\`. Scope is only the new comparator, its tests, this decision report and a focused plan/spec. Integration master at \`/srv/tse-master-20261026\` remains owned by the other active agent. Review in a separate PR; no blind merge.
