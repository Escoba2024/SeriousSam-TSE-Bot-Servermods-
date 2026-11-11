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
