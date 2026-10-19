# TSE-MAIN portable Sync-Qualifikation – Ausführungsplan

> Ausführung ausschließlich inline mit `superpowers:executing-plans`. Keine Subagenten. Direkter Nutzerauftrag autorisiert den isolierten Diagnose-/Dokumentationsscope; gemeinsame Runtime-/Integrationsressourcen bleiben gesperrt.

**Goal:** Portable Baseline reproduzieren, Discovery-Ursache belegen und vorhandene Sync-Diagnostik ohne spekulativen Engine-Fix qualifizieren.

**Architecture:** Bestehende enginefreie Tests und Offline-Auditoren verwenden. Fremde Zweige ausschließlich mit `git show` lesen; ausgewählte Python-Dateien für Tests nach `/tmp` exportieren. Keine Übernahme in main und keine Runtime.

**Tech Stack:** Linux x86_64, Python 3.12.3, g++ 13.3.0, GNU Make 4.3, Git 2.43.0.

**Spec:** `docs/superpowers/specs/2026-09-30-vanilla-server-bots-design.md`.

## Grenzen und Abnahme

- Retail 1.07 bleibt Maßstab; SE 1.10 ist nur Referenz. Qualifizierte 61DC-DLL schützen.
- Keine Spiele, Dienste, Dispatcher, fremden Worktrees, zentralen Koordinationsdateien oder externen Nachrichten verändern.
- Eigener Branch vor Implementierung; keine Änderungen auf main, kein Merge/Force-Push.
- Jeder produktive Fix benötigt Regression RED → minimaler Fix → GREEN. Bei falschem Runner genügt belegte Aufrufkorrektur ohne Codefix.
- Erst beobachteter SYNCBAD / Snapshot-Unterschied ist kein Nachweis des ersten divergenten Simulationsticks.
- Native Windows-/Retail-/WAN-/Stundengates separat UNGETESTET/BLOCKED belassen.

## Review-Fokus

Private-fixture-Tests dürfen nicht als portable Tests gezählt werden. Fehlende Daten und fehlende Gegenstücke dürfen kein Stabilitäts-PASS erzeugen. Zweigtests dürfen nicht als main-Tests bezeichnet werden. Frühere Leases gelten nicht automatisch weiter. Schreibbare Quellpfade bedeuten keine beschreibbare gemeinsame Git-Verwaltung.

## Historischer Ausführungsstand der beendeten Vorgängersitzung

Die folgenden Tasks 1–4 beschreiben die alte Sitzung. Deren Git-/Netzblocker sind historische Befunde; der aktive Fortsetzungsplan steht unten.

## Task 1: Inventur und Baseline

- [x] Pflichtdokumente, bestehenden Releaseplan, Git-Worktree/HEAD, Issues #18/#5/#6/#9 und relevante PR-/Branchmetadaten lesen.
- [x] Baseline: `make -C poc/botcore test` sowie `python3 -m unittest discover -s poc/scripts -p 'test_*.py' -v` selbst ausführen.
- [x] Eigenen Branch versuchen: `git switch -c agent/TSE-main/20261019-sync-qualification`.
- [ ] Eigener Branch bestätigt. **BLOCKED:** Sandbox verweigert Schreiben unter `/srv/tse/.git`; HEAD bleibt detached. Keine Implementierung begonnen.

## Task 2: Discovery systematisch abgrenzen

**Reads:** `poc/scripts/test_auto_combat_evidence.py`, `poc/scripts/Test-AutoCombatEvidence.py`, `tools/Test-Publication.ps1`, `poc/AUTO-COMBAT.md`.

- [x] Stacktrace bis ungeschütztem `unittest.main()` verfolgen; top-level `sys.argv`-Verarbeitung und private Abhängigkeiten prüfen.
- [x] Bestehende portable Runnerauswahl einzeln ausführen: `test_fleet_ai_evidence.py`, `test_obstacle_evidence.py`, `test_local_release_smoke.py` mit `python3 -B`.
- [x] Entscheidung: Runner-Abgrenzung dokumentieren, keinen unnötigen Produktionsfix schreiben. 44 portable Tests bestehen; sechs zusätzliche Combat-Evidenzprüfungen benötigen reale private Dateien und sind UNGETESTET.
- [ ] Optionales späteres Harness-Refactoring nur bei eigenem begründetem Auftrag: zunächst Subprozessregression für Import/Discovery ohne CLI-Ausführung RED; dann private Fixture-Konfiguration explizit machen, ohne native Prüfungen zu entfernen. Hier nicht erforderlich und nicht ausgeführt.

## Task 3: Sync-Zweige read-only qualifizieren

**Reads:** PR #16 `940a48141fd7011703510419b56aed892debce4e`, PR #21 `ccc4c46321a99d496a078aab390f4731f24a64f8` und deren drei jeweilige Diffdateien.

- [x] Diffs und Tests gegen main lesen; keine Cherry-picks, Rebase oder Branchwechsel.
- [x] Unveränderte Auditoren und Tests nach `/tmp` exportieren; dort 7 Logparser- und 18 Dump-Vergleichstests ausführen.
- [x] Kleinstes nächstes Paket abgrenzen: **paired Retail evidence qualification**, derzeit BLOCKED. Vorhandener Comparator deckt Ausrichtung und ersten beobachteten Unterschied bereits ab. Keine belegte zusätzliche Implementierungslücke ausgewählt.
- [ ] Rechtmäßig vorhandene private Server-/Client-Snapshotpaare mit gleicher Version/Karte/Level/Sequence/Tick und belegter Capture-Abdeckung verfügbar machen. Keine neuen Runtime-Starts in diesem Auftrag.
- [ ] Erst vorhandene Paare offline auswerten; bei Lücken INCOMPLETE_ALIGNMENT/EVIDENCE_GAP erhalten. Ein erster tatsächlicher Divergenztick benötigt zusätzlich belegte durchgehende Tick-Abdeckung und relevante CRC-Eingaben.

## Task 4: Abschluss und Fortsetzung

- [x] Frischer vollständiger C++-Rebuild, portable Python-Auswahl, negative Discovery-Reproduktion und Provenienzprüfung; genaue Ergebnisse im Ledger.
- [x] Dokumentation und separater Selbstreview; keine unabhängige Review behaupten.
- [ ] Eigene Dokumente auf eigenem Branch committen und nur diesen pushen. **BLOCKED:** gemeinsame Git-Metadaten außerhalb Schreibsandbox; zusätzlich CLI-DNS für github.com fehlgeschlagen.

Fortsetzung: In einer regulär beschreibbaren Git-Worktree-Verwaltung denselben HEAD und Dokumentationsdiff prüfen, den neuen eigenen Branch anlegen, dokumentierte portable Auswahl erneut ausführen, ausschließlich diese beiden Dokumente committen. Keine zusätzliche A00-/Agentenbeauftragung. Nachfolgende Runtime-/Integrationsarbeit erfordert weiterhin deren eigene gültige Freigabe und Datenbasis.

## Aktive Fortsetzung – eigenständiger Checkout 19.10.2026

**Identität:** `/srv/tse-main-agent-20261019`, Branch `agent/TSE-main/20261019-sync-qualification`, Basis `eeb40426f77d223d9f0f07489598ed2cdeac8ec7`. Lokale Git-Verwaltung: `/srv/tse-main-agent-20261019/.git` (kein verknüpfter Worktree). Der Betreiber hat diesen Checkout bereitgestellt; kein Branchwechsel und keine Worktree-Anlage erforderlich.

**Scope:** ausschließlich diese Plandatei und `docs/superpowers/ledger/2026-10-19-tse-main-sync-progress.md` schreiben und committen. Ausgaben/Exporte unter `/tmp`; keine Produktivfixes ohne neu reproduzierten Defekt. Kein Netzwerkversuch, Push, Merge, Dispatcher, Subagent, Runtime oder zentrale Koordinationsänderung. Der direkte Fortsetzungsauftrag ersetzt im eigenen isolierten Dokumentationsscope eine neue Koordinationsbeauftragung.

**Ablauf und erwartete Belege:**

- [x] AGENTS.md, Toolpolicy, README, Retail-Sync-Bericht, übernommene Dokumente und tatsächliche Git-Identität prüfen.
- [x] `make -C poc/botcore -B test`: sechs C++-Testprogramme, Exit 0.
- [x] Drei explizite portable Python-Module: 25 + 9 + 10 Tests, jeweils Exit 0. Discovery ist kein Freigabegate; private Combat-Daten werden nicht ersetzt.
- [x] `python3 -B tools/Verify-SourceProvenance.py`: 13 Quellen, Exit 0.
- [x] Zwei gepinnte Zweigstände unverändert mit `git show` nach `/tmp` exportieren und dort 18/7 synthetische Tests ausführen, jeweils Exit 0; keine aktuelle main-Abnahme daraus ableiten.
- [x] Lokalen Evidenzumfang begrenzt prüfen; fehlende echte Snapshotpaare als `BLOCKED_EVIDENCE` erhalten.
- [x] Plan/Ledger mit tatsächlichen Versionen, Befehlen, Ergebnissen und Grenzen abschließen; separater Selbstreview ohne unabhängige Reviewbehauptung.
- [ ] Nur beide Dateien stagen; Schutzprüfung, `git diff --check`, `git diff --cached --check` und Status prüfen; lokal auf dem eigenen Branch committen und Commit-SHA im dauerhaften Ledger nachtragen.

**Abnahme:** P0-portable Baseline nur bei allen genannten frischen Gates `QUALIFIED`. Wirkliche Retail-Sync-/WAN-/Wine-/24h-Gates bleiben offen. Nächste isolierte Prüfstufe: vorhandene echte Server-/Client-Snapshotpaare privat offline nach Version, Map, Level, Sequence, Tick und Capture-Abdeckung qualifizieren; bei fehlenden Paaren keine Ursachenbehauptung. Eine spätere Datenerhebung benötigt einen separaten autorisierten Runtime-Auftrag. Push kann anschließend ein vertrauenswürdiger Host-Controller unabhängig und kontrolliert ausführen.


**Frisches Ergebnis:** sechs C++-Programme + 44 portable Python-Tests + 13 Provenienzprüfungen bestehen, alle Exit 0. Separat bestehen 18/7 synthetische Tests der gepinnten Remote-Zweigobjekte; keine Übernahme in den Checkout. **P0-portable Baseline QUALIFIED** für Basis `eeb40426` in diesem Checkout. Kein zusätzlicher Produktivdefekt nachgewiesen, keine Produktivänderung. Echte Sync-Ursache weiterhin **BLOCKED_EVIDENCE**; neue Retail-Sync-/WAN-/Wine-/24h-Gates **NICHT abgenommen**. Details und Commitbezug im Ledger.


**Tatsächlicher Commitblocker dieser Fortsetzung:** `git add -- docs/superpowers/plans/2026-10-19-tse-main-sync-qualification.md docs/superpowers/ledger/2026-10-19-tse-main-sync-progress.md` endet mit Exit **128**: `fatal: Unable to create '/srv/tse-main-agent-20261019/.git/index.lock': Read-only file system`. Eigener Branch und lokales `.git` sind vorhanden; beschreibbare Git-Metadaten sind entgegen der Betreiberannahme innerhalb dieser Sandbox **nicht** gegeben. Der alte detached-/Branchanlageblocker ist historisch, der aktuelle Index-Schreibblocker bleibt offen. Kein Commit-SHA, kein Push. Kein weiterer Schreibversuch, keine Eskalation oder Git-Umgehung.

Host-Handoff: Nach unabhängiger Prüfung im vertrauenswürdigen Host-Kontext ausschließlich die zwei angegebenen Markdowndateien stagen, `git diff --cached --check`/Scope/Branch prüfen, lokal committen und die entstandene SHA im Ledger nachtragen. Anschließend kontrollierter Push des eigenen Branches möglich. Diese Sitzung kann keinen Commitabschluss behaupten.


**Abschluss des aktuellen Blockeraudits:** Derselbe read-only `.git`-Mount über drei aufeinanderfolgende aktuelle Zielturns bestätigt. Goals-Status `blocked`, nicht `complete`; Commit-Task bleibt unerledigt. Fortsetzung erfordert externe Mountkorrektur oder Host-Übernahme. Keine wiederholten Schreibversuche und keine Umgehung.


## Wiederaufnahme nach externer Host-Übernahme

Lokal verifiziert: Plancommit `41394216c307d775c36d055a412d8f0989bb607f`, Ledgercommit/HEAD `d9fcd0954f8b6a1420f251e5379b02af7d287838`, eigener Branch unverändert. Gegen Basis `eeb40426` ausschließlich die zwei Scope-Dateien geändert, Diffprüfung Exit 0, Checkout bei Wiederaufnahme sauber. Frühere Commitblockerabschnitte bleiben historisch erhalten; der Host hat die ursprünglichen Dokumente inzwischen versioniert.

- [x] Ursprüngliche zwei Dokumente lokal auf eigenem Branch committed; tatsächliche SHAs frisch geprüft und im Ledger nachgetragen.
- [ ] Abschließenden SHA-/Statusnachtrag in Plan/Ledger versionieren: weiterhin nur durch Host-Übernahme möglich, da `.git` in dieser Sandbox unverändert read-only gemountet ist.

Keine weitere Testwiederholung erforderlich: erhaltenes Manifest und Exporthashes geprüft, seit der Qualifikation nur Dokumentationsänderungen. Portable QUALIFIED; echte Retail-Sync-/WAN-/Wine-/24h-Gates und BLOCKED_EVIDENCE bleiben unverändert. Kein Push behauptet.
