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
