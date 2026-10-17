# Agent-Handoff-Vertrag – Serious Sam TSE 1.07

Status: Entwurf zur Review | Owner: Agent 5 (Audit und Dokumentationskontrolle) | 2026-10-17
Kanonische Projektanweisungen: [AGENTS.md](../../AGENTS.md). Dieser Prozess ergänzt, ersetzt jedoch keine vorhandenen Schutz- und Testgates.

## Ziele
Bei parallelen ChatGPT-, Codex-Cloud-, RDC-/Shadow- und Review-Agents darf kein Fortschritt verloren gehen und kein PR als bestanden gemeldet werden, nur weil Code gepusht ist. Projektkoordinator/technische Owners behalten ihre Aufgaben. Agent 5 prüft und dokumentiert unabhängig, **ändert keine technische Runtime ohne gesonderten Auftrag** und führt keine fremden PRs selbständig zusammen.

## Exklusive Arbeitsbereiche
- Pro Agent und Teilschritt: eigenes Ticket, eigener Worktree, eigener Branch und schriftlich festgehaltener Datei-/Ressourcen-Scope.
- Parallel bearbeitete Codepfade (insbesondere `poc/scripts/PopulationSupervisor.ps1`, `poc/POPULATION-SUPERVISOR.md`, `tools/Test-Publication.ps1`) vor dem Ändern explizit als konfliktgefährdet markieren.
- Cloud: portable Source-, Test- und Berichtarbeiten. Shadow/RDC: Retail-/Wine-/Vanilla-/GPU-/WAN-Tests mit privater Evidenz. REA/Ghidra/Frida nur unter den Regeln in AGENTS.md.
- Qualifizierte Retail-`GameMP.dll` nicht automatisch durch Builds ersetzen; fremde Sessions, Testports, Testkopien und Observer nicht stören.

## Pflicht-Handoff je Arbeitsabschnitt
Jeder Agent veröffentlicht in seinem Ticket oder PR die folgenden Daten:

```text
TSE-HANDOFF
Agent / Workstream:
Issue / PR:
Branch / Worktree:
Start-Ref / Parent-PR:
Geänderte Dateien:
Git local HEAD SHA:
Git upstream HEAD SHA:
Git status --short:
Push-Beleg: GLEICH / UNGLEICH / UPSTREAM_FEHLT / NICHT_GEPRUEFT
Tests (exaktes Kommando, Umgebung, Anzahl, PASS/FAIL/SKIP, Dauer):
Retail-1.07-Gates: NICHT_GETESTET / PASS_LIMITED / PASS / FAIL (mit Beleg)
Binaries/DLL SHA256 (bei nativer Arbeit):
Dokumentation (docs/reports, PR, Notion/Drive):
Private Rohlogs liegen (Ort, nur intern):
Risiken / fremde Ressourcen:
Nächster Schritt / Übernehmer:
```

**Lokale Push-Prüfung:**
1. `git status --short`
2. `git branch --show-current`
3. `git rev-parse HEAD`
4. `git rev-parse @{u}` (PowerShell: `git rev-parse '@{u}'`)
5. `git fetch --prune`, dann local HEAD erneut mit `@{u}` vergleichen und Abweichungen / uncommitted Dateien melden.

Achtung: Gleiches HEAD/Upstream plus sauberer Worktree bestätigt nur diesen lokalen Checkout. Eine neue Remote-Commit-URL allein beweist **nicht**, dass alle lokalen Änderungen dieses Agenten gepusht wurden. Ein separat laufender Agent kann zwischen Checks weiterarbeiten. Keine secrets, Profile/GUIDs, Rohlogs, fremde Spielbinaries hochladen.

## Abnahmestufen
- **CODE_PUBLISHED**: Remote-Commit/Branch oder PR belegt.
- **PORTABLE_PASS**: reproduzierbare Tests in deklarierter Umgebung bestanden; Linux ≠ Windows.
- **WINDOWS_PASS**: Windows-eigene Checks bestanden, ohne Native-Spielbeweis.
- **RETAIL_PASS_LIMITED**: genau benannte echte 1.07-Join-/Runtime-Einzelprobe.
- **RETAIL_60M_PASS**: 60-Minuten-Qualifikation mit SHA/Logs/SYNC-Prüfung und Testumfang.
- **WAN_QUERY / PUBLIC_BROWSER / 24_7**: separate Gates, jeweils unabhängig zu belegen.
- **MERGED**: PR tatsächlich in kanonisches `main` integriert und Regressionen erneut geprüft.

## Audit-Zustände
`VERIFIZIERT`, `PUSH NICHT NACHGEWIESEN`, `DOKUMENTATION FEHLT`, `INTEGRATION OFFEN`, `TEST OFFEN`, `KONFLIKTRISIKO`. Ein Status kann neben weiteren bestehen.

## Eskalation bei Konflikten
- Änderung an gleicher Datei: eigene Branches erhalten, Eigentümer/Parent-PR benennen, keine ungeprüften Cherry-Picks oder Force-Pushes.
- Technischer Live-Test läuft: keine Prozesse, DLLs, Profile, Ports oder laufende Testkopien anderer Agents verändern.
- Verdacht auf fehlenden Push: zuerst Remote-Belege prüfen, dann nur mit freigegebenem Read-only-RDC den lokalen Worktree vergleichen; ohne lokale Sicht **NICHT NACHGEWIESEN**, nicht fehlgeschlagen.
- Dokumentationskonflikt: tatsächlicher SHA/testprovenance > PR-Behauptung > Notion-/Drive-Zusammenfassung.

## Kanonische Anlaufstellen
- [Audit/Koordinations-Issue #20](https://github.com/Escoba2024/SeriousSam-TSE-Bot-Servermods-/issues/20)
- [Notion Audit-Dashboard](https://app.notion.com/p/3fc90f11bec881838e37f1286584a8ff?pvs=204)
- [TSE-Projektübersicht in Notion](https://app.notion.com/p/3fb90f11bec881a5b22df0b40e6c9ef2?pvs=204)
