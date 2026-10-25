# ssam.ai autonomous master execution plan — 25 October 2026

Binding spec: user CODEX MASTER TASK (25 October 2026). Lead integrates; no production interruption, foreign resources untouched. This is an additional plan, not a replacement for earlier plans. User explicitly authorizes autonomous execution; routine design/plan confirmations are waived.

## Inventory and ownership
- Main freshly fetched ab0c740 (local main fdfc46e preserved). PR45 merged; PR46 d6d2911 → PR49 5b0157f → PR50 b5dafb8 stacked, draft/unmerged. PR47 b75f14d independent session branch → PR51 01d847d → PR57 / PR63; do not merge stack blindly.
- Existing dirty AI2 and master20261022 worktrees preserved. Other Codex sessions exist. Public active generation is experimental AI2 Build06 54faabf0, not README Build04; Dedicated399158, clients399232/399305, cgroup tse-integration-399143. Unknown remote slots present: no disruptive native tests or instrumentation.
- Host 2vCPU /3819MiB, ~2272MiB available; disk ~8.9GiB free. Runtime ~570MiB cgroup, no limits. Four original role hashes verified per role; bot DLL Build06 verified. All415 backup source files and415 archive contents verified; archive d7b3650d55a21fc88614d5b969e126ac1cfcc52585262a1ef139eb0be1632b7d.
- C1: isolated /srv/tse-c1-reliability-20261025, branch agent/c1/20261025-reliability-audit. Exclusive poc/research/reliability-audit-20261025/** and docs/reports/reliability-audit-20261025/**. No runtime.
- C2: isolated /srv/tse-c2-sync-20261025, branch agent/c2/20261025-native-sync-gates. Exclusive poc/research/native-sync-gates/** and docs/reports/native-sync-gates/**. No runtime.
- Lead: this worktree for integrated reports/tools. M1 owning app repository inspected; app dirty servers.json preserved; isolated /srv/ssam-monitor-fix-20261025 branch fix/20261025-runtime-monitoring. No remote configured for app; retain source patch in project for review/publication.

## Task 1: Monitoring reliability (M1, P0)
- [x] Reproduce: 19:05 UTC GameSpy10 slots; plugin0 bots/10 humans; health11:33 stale; logs/statistics ENOENT old generation path. Independent socket query on host public IP agrees (not independent WAN evidence). Infiniteammo=0 despite requested preset.
- [ ] Write RED regressions for stale/future/mismatched health, nickname spoof/unknown classification, process PID/start/CWD/cgroup, missing logs, profile/GUID and fresh local-slot telemetry provenance.
- [ ] Implement verified runtime roster and unknown default in app; bounded read-only source reads; preserve historical health as explicitly stale. Fresh query/process/telemetry evidence per request; no invented human count.
- [ ] Run app check + complete tests + MCP handshake. Stage immutable app release, backup current app registry/service/artifacts; deploy read-only adapter only if tests pass and current game generation still matches. Roll back on failure.
- [ ] Check connected MCP status/players/health/logs/statistics. Save sanitized evidence, patch, commit.
Acceptance: eight provenance-backed bots or explicit unknowns, remote slots unknown unless verified; fresh generation-bound observations, no missing-path exceptions; no game PID/hash changes.

## Task 2: Reliability audit (M3, P0/P1)
- [ ] C1 independent PR46/49/50 review; real RED→GREEN regressions and scoped patch, handoff/commit.
- [ ] Lead review/integrate research outputs only, repeat tests. Do not enable automatic public recovery; new supervisor native fault/hour gates remain required. Existing later native FAILs are not erased by old hour PASS.

## Task 3: Multiplayer sync evidence gates (M2, P0)
- [ ] C2 review PR58 and historical reports; implement strict artifact/action/state/tick capture comparison and synthetic tests; lead review/integrate.
- [ ] Native reproduction only on exclusive owned isolated resources with reserve and paired authorized clients. Public generation has remote slots; do not attach. Root cause OPEN until matching divergent state captured. No kick-disable workaround.

## Task 4: Gate downstream packages (M4–M8)
- [ ] Read PR54/55/56/57/62/63 and incoming AI2 results, map conflicts and dependencies. Offline tools can be qualified independently, production features remain gated on P0 and own Retail regression.
- [ ] Sessions eight-client/native recovery, two instances and24/7 are NOT_TESTED here. No extra client/resource cost or hardware purchase. Power-up removal/native300s chat and infinite ammo remain separately unresolved.

## Task 5: Handoff and publication
- [ ] Review complete diff, run relevant tests, integrate only own agents commits by scoped cherry-pick. Publish own branch/PR via connector if shell authentication absent; no shared branch overwrite or automatic merge on missing native gates.
- [ ] Record commits, exact test levels, runtime changes, rollback, external blockers and next commands in docs/reports/2026-10-25-master-handoff.md and decision log.

## Execution ledger
- Inventory complete; resources protected. C1/C2 active, no extra implementers.
- Ruling: user authorization supersedes routine skill confirmation steps; executable plan is supplied and work continues autonomously.
- Ruling: missing remote identity evidence produces unknown, never automatic human classification. Presence of unknown slots enforces human-protection hold for disruptive operations.

## Verified execution checkpoint
- M1 implemented/tested/deployed:20 app tests+build, real7-tool MCP handshake; logs/statistics paths repaired. Final read-only service uses immutable b7bda00 compiled release; source documentation/sandbox193e07b. Game processes/binaries unchanged.
- Independent M1 review findings all corrected RED→GREEN. Confirmed classification remains BLOCKED_SERVER_SESSION_BINDING:8 associations,10 unknown slots,0 claimed confirmed humans/bots. Health fresh LIMITED; historical collector stale/sync history unverified.
- C1 integrated64334d9; source-root runner made portable; lead rerun5RED/11GREEN and91PASS+1SKIP. C2 independent patch review no Important/Critical. Native new-source gates remain NOT_TESTED; no automatic recovery.
- C2 integrated82a994d; lead37/37 tests and PR58 original29 plus7 adversarial findings reproduced; C1 independent review no Important/Critical. Native capture producer/binding/paired divergent artifacts unavailable; root cause OPEN.
- Downstream PR dependencies/conflicts/acceptance gaps documented; no experimental gameplay merge/deployment. No native capacity gate falsely claimed from short51.224% CPU observation.
- Full handoff: docs/reports/2026-10-25-master-handoff.md. Publication/cleanup final receipt follows.
