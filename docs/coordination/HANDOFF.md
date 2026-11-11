# TSE-Agenten: Start und Handoff ohne manuelle A00-Freigabe

**Stand: 19.10.2026.** Die alten `CLAIM_REQUESTED → A00-GRANTED`-Freigabestufen und vierstündigen Code-Leases sind aufgehoben. `STARTED` und `HANDOFF` sind Informationsnachweise, **keine Erlaubnisanfragen**. Kein Agent wartet für konfliktfreie Code-, Offline-Test-, Analyse- oder Dokumentationsarbeit auf A00.

## Optionaler Startstatus (ins Issue #18)

```text
STARTED
slot: Axx (nur falls sinnvoll)
ticket_or_pr: #...
goal: ...
branch: ...
worktree: ...
write_scope: ...
runtime_scope: NONE | ISOLATED_COPY | SHARED_RESOURCE (nur mit technischem exklusivem Nachweis)
check: existing_worktrees_and_writers_checked
```

Eine Nachricht ist optional; sichere Arbeit kann sofort beginnen. GitHub-Kommentare oder Slot-Labels bilden **keinen** technischen Lock.

## Nur bei echtem Konflikt

```text
CONFLICT
scope: <Datei / Worktree / PID / Installation / Port>
observed_owner_or_state: ...
safe_alternative: <eigener Worktree / separater Port / Offline-Fixture>
needs_decision: <nur falls sich Konflikt nicht sicher auflösen lässt>
```

Gemeinsame Runtime mit unbekanntem Eigentümer bleibt unangetastet; **die restliche Arbeit wird fortgesetzt**. Ein manueller A00-`GRANTED`-Kommentar löst einen fehlenden technischen Runtime-Lock ohnehin nicht.

## Handoff nach der Arbeit

```text
HANDOFF
slot: Axx
ticket_or_pr: #...
branch: ...
head_sha: ...
paths_changed: ...
tests: <Befehle/Umgebung/PASS/FAIL/SKIP>
retail_runtime: NOT_TESTED | PASS_LIMITED | FAIL | PASS_SCOPED
resource_cleanup: <nur eigene Prozesse, eigene Kopien, Ports>
known_issues: ...
pr_url: ...
status: COMPLETE | REVIEW | BLOCKED_SPECIFIC_RESOURCE
```

Keine gesonderte `RELEASE`-Genehmigung für reine Codearbeiten. Bei gemeinsam genutzten Runtime-Ressourcen nach eigenen Tests Prozessende, Portbelegung, Restore und ggf. Freigabe des **technischen** Locks prüfen. Keine fremden laufenden Sessions stoppen, keine historischen Testgates als bestanden umdeuten. Die Projektregel ersetzt weder technische Sperren noch plattformseitige Zugriffs-/MCP-Freigaben.

## 2026-11-11 — Milestone A execution, B gated

- Branch `codex/20261111-milestone-a`, worktree `/srv/tse-milestone-a-20261111`; baseline 4d04ab4. Main alone changed runtime; two independent worktrees implemented/reviewed combat and names.
- [Full eight-part progress report](../reports/2026-11-11-milestone-a-progress.md), [persistent plan](../superpowers/plans/2026-11-11-milestones-a-b.md), [manifests](../reports/milestone-a-20261111/).
- New unqualified build001 DLL `def7c044ba64a65b742c63d76c775c955b892655e626bf96a1380d778d35719a` built, NOT deployed. 183 portable Python tests passed; C++ sanitizer checks passed. 250 new names validated, NOT deployed.
- Five public servers now load typed Spawn=0 mapstart configs; all original DLLs/maps preserved. Dev A1 rolled back at **19:11:37 UTC**, exact original config pins and eight owned bots verified, following 36 SYNCBAD/3 external sync disconnects. Root cause OPEN. Dev original server powerup filter and Cecil048 clients preserved.
- Rollback stop helper first rejected an evidence directory outside its hardcoded parent. No force kill; the still-owned botB was closed with checked PID/start identity and WM_DELETE_WINDOW, then normal harness resumed under correct parent. All transient stop overrides restored. Isolated probe port25880/unit inactive; deployment locks released.
- Fresh final snapshot includes 18 native processes, eight owned bots per server; Hole now has one additional UNKNOWN, Dev zero additional. Runtime identity records refreshed after rollback. Post-rollback Dev log at 19:15 had zero SYNCBAD/disconnects; short observation only, no causal proof.
- Private receipts `/srv/tse-milestone-a-evidence-20261111/`; verified rollback `/srv/tse-cecil-full-20261107/.codex/evidence/restart-fleet-20261111-a1-sync-rollback/development/rollback.json`. Initial all-six A1 result is **superseded for Dev** by `dev-sync-rollback-result.json`.
- Backup: original source bundle and eight runtime chunks roundtrip verified on private Drive; companion carries restore index/checksums/dirty work/SDK bundles. 36,009 files restored/hashchecked separately; symlinks indexed, not materialized. No full native restore claim.
- A=INCOMPLETE; B=NOT_STARTED. Native Windows/Shadow clients offline. First next test: isolated server/client actual session-field equality for Spawn3/0, then controlled respawn damage; source session copy exists, client-local gam_ settings are not a demonstrated fix. Further A3/native map gates remain open. No new rollout until failures resolved and required evidence exists.

- Abschluss: Remote-Code `b6ae14e5497f6013bf198fad5cd105bfe658f05c`, treeidentisch zu lokal64aa881; After-Drive-Archiv und Companion zurückgeladen/SHA-geprüft. Backupindex enthält Links/Hashes. Abschließende Dev-Shellmessung3,0, 18 aktuelle Logs ohne Syncmeldungen, Locks frei. Fehlgeschlagener Test bleibt FAIL; A weiterhin offen.

### Autonomous continuation, 19:36 UTC (supersedes stopped-work wording above)

User explicitly requested autonomous completion of full A then B. Goal ACTIVE. Root continued in same main worktree; both isolated agents resumed and committed actual regressions/fixes, then independently reviewed each other's changes. Local commits84b9216 (final-residual trigger, gain10/14/20, combat vs ordinary pickup) and3dc99dc (bounded extended-item transit failure) integrated. Native build002 at `/srv/tse-milestone-a-build-002-20261111/manifest.json`: DLL `50b132c0d83d209b399c7178bcb41dc16c0ee1ffe7c28652cecbd69a07baafd5`, source3dc99dc75d3dcae22f9af18537d5df282c27f0e5, build_ok=true, qualified=false. No live DLL changes.

New original-Engine executable validates all250 added names, including actual Undecorated and LengthNaked; native GUI/query checks still pending. New own routes-free private namespace `/srv/tse-a1-isolated-20261111`, display153, port27750; unchanged Vanilla client + old048 bot + existing Dev servermod. Spawn3 control320.08s completed, no BAD/disconnect, all session156 bytes equal across three processes; normal cleanup confirmed. Spawn0 control is active under private script `/srv/tse-milestone-a-evidence-20261111/run-isolated-a1.py`, exec session75658, log `isolated-spawn0-run.log`; poll same handle or authoritative PID/result, never infer stopped from timeout.

Additional own arena runtime `/srv/tse-arena-isolated-20261111` prepared (display154, port27850), currently no processes; comparator script `run-arena-comparison.py` stages original server, four old048 bots and four build002 bots plus original Vanilla observer AFTER fresh one-bot preflight. Intended trial1/2/3=MITTEL/STARK/DEMON, launch order alternated; population9, same fixed configs/map, native score/health/respawn/telemetry measured. Start only after Spawn0 cleanup and RAM preflight. This is A3 evidence collection, no B work. Scripts intentionally remain private with licensed runtimes; sanitized results belong in reports. Original receive-damage gate at Entities RVAed380 and actual session field/health/placement/game-tick export paths independently disassembled; decision file documents limited scope and no Frida/Ghidra availability.

Remaining: normal post-respawn hits at first state; render/query new formats; native paired arena results; Hole/Skulls cycle-fix function gates, other three public map checks and required duration gates, controlled actual Dev acceptance, full staged rollout/backup. B hard-gated until A fully accepted.
