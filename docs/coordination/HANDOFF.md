# Agenten-Handoff und Claim-Protokoll

Alle Vorlagen als **Issue-Kommentar** im zentralen Koordinationsissue posten; Geheimnisse, personenbezogene Spielernamen, Rohlogs und Retail-Dateien nicht veröffentlichen. Die Claims werden durch A00 **manuell** geprüft; ein Kommentar erteilt keine Freigabe.

## Arbeitsanforderung

```text
CLAIM
slot: A01-A09
ticket: #<Issue oder PR>
purpose: <ein eindeutiges Ergebnis>
branch: agent/Axx/<ticket>-<name> (oder existierender Branch)
worktree: <vollständiger eigener Pfad>
write_paths: <exakte Dateien oder enges Muster>
runtime_resources: NONE | SHADOW_RETAIL | SHADOW_GAME_FILES | HETZNER_RUNTIME | GHIDRA_TSE_PROJECT
planned_tests: <portable / Windows / Retail / WAN, nur beabsichtigt>
lease_until: <ISO-8601 mit Zeitzone, maximal +4 Stunden>
known_dependencies: <PRs/Dateien/Prozesse>
status: CLAIM_REQUESTED
```

## Autorisierung nur durch A00

```text
GRANTED
slot: Axx
ticket: #...
branch: ...
write_paths: ...
runtime_resources: ...
lease_until: ...
conditions: <z.B. nur read-only während laufender Tests>
```

Ohne passendes `GRANTED`, bei abgelaufener Lease, Unsicherheit über Prozesse oder fremden Änderungen => `BLOCKED`, **keine Schreibaktion**. A00 kann `REJECTED` mit engerem Scope zurückgeben. A00 soll nie zwei überschneidende Schreib-/Runtime-Leases parallel erteilen.

## Konflikt/Blocker

```text
BLOCKED
slot: Axx
ticket: #...
conflict: <Pfad / PID / Git-Branch / Runtime / PR>
observed_state: <read-only Feststellung>
action_taken: NONE
needed_from_A00: <Entscheidung>
```

## Übergabe/Abschluss

```text
HANDOFF
slot: Axx
ticket: #...
branch: ...
head_sha: <40-stelliger Commit-SHA>
paths_changed: ...
tests: <exakte Befehle, PASS/FAIL/SKIP mit Plattform>
retail_runtime: NOT_TESTED | PASS_LIMITED | FAIL | PASS_SCOPED
safety: <DLL SHA, Backup, keine fremden PIDs gestoppt>
dependencies: ...
known_issues: ...
pr_url: ...
status: REVIEW
```

```text
RELEASE
slot: Axx
ticket: #...
write_paths: ...
runtime_resources: ...
cleanup_verified: <eigene Prozesse / Profile / aktive Spieler>
status: RELEASED
```

**Kritisch:** `RELEASE` erst nach Prüfung lokaler Prozesse, laufender Proben und Git-Status. A00 markiert eine Leasesperre erst nach Prüfung als frei. Kein Anspruch auf automatische Live-Überwachung aus diesen Vorlagen.
