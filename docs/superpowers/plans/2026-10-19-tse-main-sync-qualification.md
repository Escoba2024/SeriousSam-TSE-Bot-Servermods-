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


## Aktueller P0-Meilenstein: echte gepaarte Retail-Sync-Evidenz auf Shadow

**Auftrag 19.10.2026:** ausschließlich Planung/Handoff, keine native Ausführung. Start-HEAD frisch bestätigt `13ac33e2695f53794a171e2e0920a1fccd1e981b`, eigener Branch unverändert, Checkout zu Beginn sauber. Die bisherigen Nachträge sind durch den Host committed; deren Commitblocker-Audits sind historisch. Shadow online, separate Retail-Kopien/Evidenz und qualifizierte GameMP-DLL sind vom Betreiber frisch bestätigt; diese Angaben sind Hostbefunde, keine eigene Shadow-Prüfung. Verfügbarkeit ist kein Beleg vorhandener ausgerichteter Dump-Paare.

**Ziel P0-PAIR:** Ein privates, unveränderliches Evidence-Paket eines autorisierten isolierten Laufs mit mindestens einem echten Server-/Client-Paar gleicher Retail-Version, Karte/Mapepoch, Level, Sequence und Tick, dessen CRC und gedruckter Zustand offline verglichen werden können. Für eine Serie: mindestens zwei vollständig zugeordnete Paare aus derselben Mapepoch. Ein reproduzierter Unterschied ist ein wertvoller Diagnosebefund, kein Erhebungsfehler; ein übereinstimmendes Paar ist keine Stabilitätsabnahme. Erster tatsächlicher Divergenztick und Ursache bleiben separat offen.

### 1. Geprüfte Werkzeuge und Grenzen

| Quelle im eigenen Checkout bzw. gepinntes Git-Objekt | Nutzbarer Befund / Grenze |
|---|---|
| `docs/reports/2026-10-17-retail107-sync-check-investigation.md` | Original-Engine-Hash, Sync-Handler `0x601A2D10`, Zähler/Kick und Berichtsschalter belegt; Ursache offen. |
| `ccc4c46321a99d496a078aab390f4731f24a64f8:docs/reports/2026-10-17-retail107-native-syncdump.md` | Statisch: `cli_bDumpSync` bei Datenadresse `0x602CD6EC`; SessionLoop `0x601A8020` setzt den Schalter zurück und schreibt `temp\syncdump.txt`; `DumpSyncToFile_t` `0x601A7FC0`. Kein nativer Server-/Client-Dumpnachweis. `cli_bDumpSyncEachTick` nur als Symbol, Verhalten nicht qualifiziert. |
| Derselbe Commit: `tools/compare_sync_dumps.py` | Offline, genaue Level/Sequence/Decimal-Tick-Ausrichtung; CRC und Textvergleich getrennt; Exit 0 gleich, 3 verschieden, 2 ungültig/unaligned/incomplete. In diesem Branch nicht integriert; unverändert gepinnt separat bereitstellen. |
| `tools/analyze_sync_log.py` | Logzähler/Disconnects, keine CRC-Paarerhebung. Aktuelle Basis hat einfache Tickregex; dafür optional den bereits qualifizierten Parser `940a48141fd7011703510419b56aed892debce4e` separat verwenden. Keine stillschweigende Branchintegration. |
| `poc/release/gamemp/BotDriver.cpp`, `Test-Phase1Telemetry.ps1`, `Phase1Diagnostics.ini` | `[BotSnapshot]` ist lokaler Bot-Tick plus gerundete replizierte Playerwerte, kein vollständiger Engine-Syncdump und keine automatische Engine-Tick-Zuordnung. Das INI aktiviert Bewegung/periodisches Feuer; es ist keine stationäre Vanilla-Kontrolle. `-QueryServer` des Telemetrieprüfers ist fest auf `127.0.0.1:25601` gebunden. |
| `tools/Test-TSEExternalVanillaPreflight.ps1` | Read-only vier Originalhashes, Observer-Prozesspfad und frische UDP-Antwort; `canStart` aus JSON auswerten, nicht nur Shell-Exitcode. Verlangt genau einen erwarteten Bot, daher für Hinzunahme eines Vanilla-Observers zu diesem Zustand. Kein Gate für leeren Server oder Vanilla-only-Matrix. Fixture niemals Startfreigabe. |
| `Test-RetailJoin.ps1` | Kopiert die DLL in festes BotClient-Ziel und restauriert sie nicht automatisch; für diesen Auftrag nicht unverändert starten. |
| `tools/run-shadow-fleet.ps1`, `poc/LOCAL-RELEASE.md` | Backup/Restore als Referenz; Fleet-Hülle verwendet feste Root-/Port-/Mehrbotannahmen, optional Default-Build-DLL und Kill im Fehlercleanup. Kein fertiger parametrisierter Ein-Bot-Paarcollector. Nicht als direkten Startbefehl übernehmen. |
| `Stop-BotFleet.ps1`, `Restore-LocalBotRelease.ps1` | Stop prüft PID/Pfad/Startzeit, versucht CloseMainWindow und markiert Force; Restore prüft vorher sämtliche Backup-Pfade/Hashes und gestoppte Ziele. Nur mit passendem eigenen Start-/Backupmanifest benutzen; Servercleanup separat belegen. |
| Toolchain- und Lowrender-Berichte vom 17.10. | Frida-Python-Selbsttest ist kein TSE-/MCP-E2E. Reguläres Fensterschließen und anschließende Populationserholung sind belegt, aber keine serverseitige CRC-Abnahme. |

### 2. Host-Preflight und Erhaltung (P0-A, vor jedem Start)

1. Host benennt privat genau die drei Testrollen Server, Client und optional Observer mit absoluten Installations-/Arbeits-/Ausgabepfaden, freien Game-/Queryports und Run-ID. Ausschließlich separate rechtmäßige Kopien; keine laufende Partie oder bestehende qualifizierte Installation umkonfigurieren. Prozess-/Portbelegung frisch lesen, Eigentum eindeutig prüfen. Fremder Prozess/Spieler oder unklarer Pfad bedeutet NO-GO; niemanden entfernen.
2. Pro Rolle SHA256 von EXE, GameMP, Engine, Entities und Map/Version erfassen. Bot-GameMP muss `61DC27E0E7B80BADCF9AE705C30FCA88EDD3935737715DFFFF59E90C26F1FEF9` sein; Server und Vanilla behalten ihre Original-GameMP. Analysierte Engine `B79BF8BB3927FE4F8F252E141D721AE5C738DF02218F0ECC12DA5C1AFBCB534F` prüfen; bei anderem Hash Adressen nicht verwenden. Keine Rebuilds/DLL-Ersetzungen. Originalhashes aus vertrauenswürdigem vorhandenem Manifest, nicht aus demselben ungeprüften Ist-Zustand ableiten.
3. Vorherzustand von Logs, Startup/PersistentSymbols/Profilen, bestehenden Temp-Dumps und Dateiinventar mit Hashes sichern. Neues privates Run-Verzeichnis, freier Speicher und Größenbudget (Vorschlag 256 MiB pro Kurzlauf; bei Erreichen sauber abbrechen) dokumentieren. Bestehende Dumps weder überschreiben noch als frische ausgeben. Restore darf erst nach Ende aller eigenen Prozesse schreiben.
4. Einstellungen für Karte, Schwierigkeit, Spielmodus, Netzwerk und Tick-/FPS-Limits über die Kontrollstufen konstant halten und protokollieren. Keine Pause/Slowmotion/Debug-Simulation zur künstlichen Ausrichtung, keine RNG-/Action-/CRC-Manipulation. `ser_iKickOnSyncBad` unverändert erfassen; insbesondere keine Abschaltung. Keine unqualifizierten ExtensiveSync-/EachTick-Schalter.
5. Zulässige beobachtende Konfiguration nur in Testkopien: `ser_bReportSyncBad=1`; `ser_bReportSyncOK=1` ausschließlich kurz und mit Logbudget, ursprüngliche Werte sichern. LATE/EARLY nur über tatsächlich bestätigte Retail-Symbole. Native Joinmarker plus unabhängige UDP-Belegung protokollieren; UTC dient Korrelation, nie als Ersatz für Engine-Tickidentität.

### 3. Kleine geordnete Kontrollmatrix (P0-B)

Alle Zeiten sind vorgeschlagene Erhebungsbudgets nach belegtem Join, keine bereits bestandenen Tests. Jede Zelle erhält eigene Run-ID, Logs und Restore-Nachweis. Erst weitergehen, wenn Erhaltung/Logging der vorigen Zelle funktioniert. Keine automatische Skalierung; Mapwechsel und Reconnects vorerst ausschließen.

| Stufe | Teilnehmer und tatsächliche Eingaben | Budget | Ergebnisfrage |
|---|---|---:|---|
| V0 | Originalserver + ein Vanilla-Client, stationär | 120 s ohne Dump-Trigger | Funktionieren Join, Syncberichte und sicherer Stop als uninstrumentierte Kontrolle? |
| V1 | Gleiche Rollen/Settings wie V0, stationär | 120 s, höchstens 3 paarige One-shot-Versuche, mindestens 10 s auseinander | Schreibt jede Seite einen frischen vollständigen nativen Dump; entsteht ein exakt ausgerichtetes Paar? |
| B0 | Originalserver + genau ein Bot im separaten 61DC-Client, AutoCombat/Navigation/Bewegung/Feuer deaktiviert über nachgewiesene vorhandene Settings | 120 s ohne Dumps, dann separater 120-s-Capturelauf | Gelingt dieselbe Erfassung im BotClient? Wirksame stationäre Eingaben nachweisen; unbekannte Settings => Zelle noch nicht ausführbar. |
| B1 | Gleiche Rollen wie B0, nur nachgewiesene normale Bewegung/Rotation aktiv, kein Combat/keine Hinderniserholung | 300 s Kontrolle, separat höchstens 300 s Capture | Ändert normale Action-Erzeugung den ersten beobachteten Sync-/Dumpbefund? |
| B2a (bedingt) | B1-Bot + stationärer Vanilla-Observer; sonst identische Einstellungen | 120 s Kontrolle, separat 120 s Capture | Zunächst ausschließlich zusätzliche Population variieren. |
| B2b (bedingt) | B2a mit normalem periodischem Feuer, AutoCombat weiterhin aus | 300 s Kontrolle, separat höchstens 300 s Capture | Feuer separat von Zielwahl prüfen; Schäden/Kills nur tatsächlich beobachtet ausweisen. |
| B2c (bedingt) | B2b mit AutoCombat an, Hinderniserholung weiterhin aus | 300 s Kontrolle, separat höchstens 300 s Capture | Erst jetzt AutoCombat als nächsten Faktor prüfen; echte Ziel-/Fire-/Schadenbelege, kein vorgetäuschtes Gameplay. |

Quellseitig konkrete Profile aus `BotDriver.cpp` (Shellregistrierung Zeilen 164–175, Actionpfad ab 278): B0 setzt `bot_bEnabled=1`, `bot_bAutoCombat=0`, `bot_bObstacleAvoidance=0`, `bot_iTestTarget=-1`, `bot_fMoveFactor=0`, `bot_fYawSpeed=0`, `bot_fFirePeriod=0`, `bot_iFireTicks=0`. B1/B2a ändern nur MoveFactor auf 1 und YawSpeed auf 45 als dokumentiertes Bewegungsprofil. B2b setzt FirePeriod auf 1 und FireTicks auf 3; B2c schaltet allein AutoCombat auf 1. `bot_bCombatSkipLocals=1` bleibt konstant. Diagnosekonfiguration `bot_bDiagnostics=1`, `bot_iLogEvery=1` für diese kurzen Messzellen bereits in der jeweils zugehörigen uninstrumentierten Kontrolle gleich halten; Logkosten separat messen. Werte nur in privaten Testprofilen, nicht im qualifizierten Betriebsprofil ändern. Diese Profile sind aus dem Quellstand abgeleitet, **keine nativ freigegebenen INIs**: Host muss Symbole/Werte des geladenen 61DC-Kandidaten und effektive Actions bestätigen. Auch bei Nullbewegung können Spawnphysik/andere Spieler Zustände ändern; stationär bedeutet hier keine angeforderte Bewegung/Feuer, nicht eingefrorene Simulation. B2-Observer erst nach erneutem Live-Ein-Bot-Preflight mit `canStart=true`; währenddessen genau erwartete Population überwachen. Vanilla-only V0/V1 benötigen ihren eigenen rollen-/populationsgerechten Host-Preflight.

### 4. Nativer One-shot-Capturevertrag (P0-C)

1. Auf eigenem Testprozess jeweils einmal den vorhandenen Retail-Shellweg zum Setzen von `cli_bDumpSync=1` hostseitig prüfen. Es ist kein allgemeiner Remote-Shell-/PowerShell-Befehl bekannt; Host muss lokalen nativen Konsolenzugriff und PID/Fensterzuordnung bestätigen. Der Serverpfad ist separat zu qualifizieren; ein clientseitig registriertes Symbol beweist keine wirksame Ausgabe auf einem Dedicated Server. Wenn eine Seite keinen Dump liefert: CAPTURE_CAPABILITY_BLOCKED, keine erfundenen Ersatzsnapshots.
2. Vor jedem Versuch alte Datei samt Hash archivieren; frischen Triggerzeitpunkt, Rolle, PID/Startzeit und Konsolenbestätigung protokollieren. Tatsächlichen Zielpfad in genau der eigenen Installation bestimmen (Arbeitsverzeichnis/Bin vs. Spielroot nicht raten). Dump-Erfolgsmeldung, neue Dateiänderung und neue Engine-Metadaten prüfen. One-shot-Ausgabe kann vorigen Dump überschreiben: jeden vollständigen Dump vor dem nächsten Trigger unverändert rollengetrennt archivieren.
3. Datei erst nach Ende des Schreibens übernehmen: vorzugsweise nach kontrolliertem Prozessende oder mit belegbar geschlossenem Writer; zwei unveränderte Größen-/Hashproben plus vollständige Pflichtmetadaten sind nur ein Fallback-Indiz. Trunkierte/wechselnde Datei als unvollständig markieren, nie reparieren. SHA256 über Rohbytes, Bytezahl, Encoding und Archivzeit im Sidecar vermerken. Originale behalten; keine Metadaten nachträglich in Dumptext einsetzen.
4. Server und Client zeitnah auslösen, aber **keine Gleichzeitigkeit und keine Tickgleichheit unterstellen**. Paarung nur nach originalem Level/Sequence/Decimal-Tick und externer gleicher Run-/Mapepoch. Mapwechsel => neues Segment; wiederholte Identität innerhalb eines Segments ungültig. Fehlende Gegenstücke erhalten, nicht durch Dateiumbenennung oder nächstliegenden Tick passend machen.
5. Private Archivstruktur je Run: `server/` und `client/` ausschließlich vollständige ausgewählte `.txt`-Dumps; `manifest.json`, `events.jsonl`, Logs, Hashmanifest und unvollständige Rohdateien außerhalb dieser Comparatorordner. Sidecars enthalten: Run-ID, Rolle/PID/Startzeit, Binary-/Map-/Confighashes, Version, Mapepoch, Trigger-/Capturezeiten, Dump-Hash/-Größe, Level/Sequence/Tick/CRC, Capturemethode, Fehler-/Drop-/Truncationzähler und tatsächlich erfasste Zeitspanne. Actionlokalticks nur mit separat bewiesener Zuordnung.
6. Native Fortschrittsdaten, Lograte, CPU und verfügbare Tick-/Frame-Latenzen bei Kontrolle und Capture erfassen. Vorläufiges Messbudget: keine neuen Stalls/Timeouts und höchstens 10 % Verschlechterung vergleichbarer Durchsatz-/Latenzmetriken gegenüber wiederholter Kontrolle. Ist die Metrik nicht messbar oder Baseline zu variabel, Overhead als UNKNOWN behandeln und Kontrollwiederholung verlangen; kein Performance-PASS aus CPU allein. Dump-I/O verursacht Messkosten und wird mitgeführt.

**Ausrichtungsgrenze:** Nach höchstens drei One-shot-Paarversuchen ohne exakte Identität ist P0-C als UNALIGNED zu beenden, nicht beliebig länger zu probieren. Kein EachTick-Flag auf Verdacht. Dann P0-D vorbereiten, nicht eigenmächtig instrumentieren.

### 5. Bedingte passive Diagnose (P0-D, separates Host-Gate)

Nur wenn One-shot-Capture scheitert oder ein reproduzierter Fehler weitere Feldbelege benötigt: erst vorhandene private Original-Engine statisch gegen Hash und konkrete Feld-/Calling-Convention-/Lifetimes validieren. Historischer Handler `0x601A2D10`, ImageBase `0x600C0000`, RVA `0xE2D10` ist ein Suchanker, **kein fertiger Hook**. Message-Case/CSyncCheck-Layout nicht aus Engine 1.10 übernehmen. Client-Checksum-Aufruf und serverseitig verglichene lokale/empfangene Werte samt deren tatsächlicher Tick-/Sequencezuordnung müssen separat belegt werden.

Frida-MCP zunächst natürlicher Hooktreffer, Attach/Unload/Detach an eigenem Wegwerfprozess; der alte explizite NativeFunction-Selbstaufruf genügt nicht. Danach nur eigentumsgeprüfte isolierte TSE-Testprozesse, geladene Modulhashes/Base und x86 prüfen. Minimal vorallokierter begrenzter Ringpuffer, nur validierte primitive Werte kopieren; keine fremden Zeiger dereferenzieren ohne Layout-/Lifetimebeleg, keine Gamefunktionen aufrufen, keine Dumps/Formatierung blockierend im Tick-Hook, keine eigenen Schreibzugriffe auf Spiel-/Action-/CRC-Zustand und kein Funktions-Replace. Frida-Interceptor kann zur Installation selbst Laufzeitcode verändern; deshalb ist auch ein nur lesender Hook instrumentiert und separat zu genehmigen/zu vermessen. Overflow/verlornene Records mit Zählern sichtbar machen. Das Instrument selbst verändert Timing; Kontrolle ohne Instrumentierung vor/nach identischer Zelle und gemessene Kosten sind Pflicht. Daten nur aus tatsächlichen CRC-Erzeugungs-/Vergleichspunkten mit originaler Identität korrelieren. Ein Roh-CRC-Hook allein liefert noch keine vollständigen Zustandsdumps und keine Ursache.

Implementierung und native Ausführung dieses Collectors sind **nicht Bestandteil dieses Planungsauftrags**. Wenn sie erforderlich werden, lautet der reale nächste Blocker CAPTURE_ALIGNMENT_METHOD_UNQUALIFIED; kein pauschales „Shadow fehlt“.

### 6. Offline-Auswertung, Stop und Entscheidung (P0-E)

Host stellt die beiden geprüften Auditorstände separat bereit, ohne Merge/Cherry-pick. Beispielaufrufe ausschließlich auf existierenden privaten Dateien, Parameterpfade aus dem Hostmanifest:

```text
python -B <gepruefter-parser> <server-log> <client-log>
python -B <gepruefter-comparator> --server <server-dump> --client <client-dump>
python -B <gepruefter-comparator> --server-dir <server-segment> --client-dir <client-segment>
```

Comparatorlimits: 1–128 `.txt`-Dateien je Ordner, höchstens 8 MiB je Datei/32 MiB je Serie, keine Symlinks, keine Sidecars im Ordner; größere Runs in nachvollziehbare Segmente teilen, ohne Lücken zu verbergen. JSON/Exitcode speichern; Exit 3 ist gemessener Unterschied, Exit 2 EVIDENCE_GAP/UNALIGNED/INVALID, Exit 0 ausschließlich MATCHED_OBSERVATIONS. Parserausgaben enthalten Clientidentitäten/Pfade und bleiben wie Rohlogs privat. Nur freigegebene bereinigte Aggregate ins Git.

Abbruch bei SYNCBAD, unerwartetem Disconnect/Crash, fremdem Spieler, Hashabweichung, Datenverlust oder Ressourcenbudget: keine Folgevariation starten. Bei erstem SYNCBAD nur bereits eingerichteten passiven Capturepuffer sichern, keine neue invasive Aktion; Fehlerzähler/Kick normal wirken lassen. Ein SYNCBAD wird als Fehlerbefund erhalten, kein „stabiler Lauf“ daraus. Stop eigene Clients zuerst über eigentumsgeprüftes CloseMainWindow mit 15-s-Timeout; Force nur danach markiert, kein regulärer Shutdown-PASS. Eigener Dedicated separat mit geprüftem regulärem Beenden behandeln; keine globalen Prozesskills. Prozessende und tatsächliche Serverpopulation/Slotabbau belegen. Nach Log-/Dump-Archivierung nur eigene gesicherte Dateizustände restaurieren und sämtliche Binary-/Config-/Backuphashes nachprüfen; Rücknahmefehler blockieren weitere Zellen.

**Abnahme P0-PAIR:** Hostpaket hat überprüfbare Provenienz/Erhaltung, natürliche native Dump-Erzeugung auf beiden Seiten, vollständige Originaldateien, exakte Paaridentität und gespeicherte Offlineauswertung. CHECKSUM_DIFFERENCE_OBSERVED ist erlaubt und getrennt von CAPTURE_QUALIFIED; NO_DIFFERENCE_OBSERVED gilt ausschließlich für erfasste Paare. Beide Seiten können denselben Tick auslassen: `complete_pairing=true` ist kein Nachweis lückenloser Simulation. Erster tatsächlicher Divergenztick benötigt zusätzlich kontinuierliche überprüfte Tickabdeckung und relevante CRC-Eingaben; hier weiterhin FIRST_DIVERGENT_GAME_TICK_NOT_DETERMINED.

### Ausführbarer nächster Host-Schritt und aktuelle Blocker

1. Host füllt Rollen-/Hash-/Pfad-/Port-/Restoremanifest auf den bestätigten separaten Shadow-Kopien aus und prüft P0-A live. Vorher vorhandene Evidenz gezielt anhand dieses Manifests auf echte Paare prüfen; brauchbare Paare zuerst offline auswerten.
2. Ohne vorhandene Paare V0 ausführen, dann V1: Fähigkeit eines frischen One-shot-Dumps pro Seite nachweisen, maximal drei Paarversuche archivieren und offline nach Metadaten paaren.
3. Bei CAPTURE_QUALIFIED B0/B1 nur mit validierten Profilen durchführen. Bei fehlender Dedicated-Ausgabe oder UNALIGNED den konkreten Capability-/Alignmentbefund liefern; erst danach separates P0-D-Gate.

**Reale offene Abhängigkeiten:** Vorhandensein ausgerichteter Paare noch nicht belegt; nativer One-shot auf Dedicated und Client sowie sichere Shellauslösung/Archivierung noch nicht qualifiziert; keine qualifizierte tickgenaue Erfassungsmethode, falls One-shots nicht passen. Shadow-Erreichbarkeit und Existenz der 61DC-DLL sind nach Betreiberprüfung keine aktuellen Blocker. Keine neue Runtime-Freigabe aus diesem Dokument ableiten. P0-portable bleibt QUALIFIED; Retail-Sync-/WAN-/Wine-/24h-Gates bleiben NICHT abgenommen.


## P0-PAIR-OFFLINE-VALIDATOR – Implementierungsauftrag 19.10.2026

Basis frisch geprüft: `4b8ec040d351178be33acae985a3a12f5115837b`, eigener Branch, sauber. Lokales Tracking zeigt ahead 3; Betreiber meldet Push erfolgt, kein Remotezugriff zur erneuten Prüfung. Shadow-RDC laut neuem Betreiberauftrag OFFLINE; keine Runtime. Aktualisierte Betreiberpolicy ersetzt alte manuelle CLAIM/GRANTED-Gates für konfliktfreie Offlinearbeit.

Scope: neu `tools/p0_pair_evidence.py`, `tools/test_p0_pair_evidence.py`, `tools/p0_pair_evidence.md`; nur bestehende eigene Plan-/Ledgerdateien zusätzlich ändern. Comparator unverändert. Ein Hauptagent, inline mit Superpowers writing-plans/executing-plans/TDD/systematic-debugging/verification-before-completion; keine zusätzliche Designfreigabe bei ausdrücklich beauftragter eigenständiger Umsetzung.

Kleinster Schema-v1-Vertrag: strikt typisierte JSON-Objekte, Duplicate-/Unknown-Key-Abweisung, eine Run-/Mapepoch/Retail-Version, genau zwei Rollen. Separater vertrauenswürdiger Modul-Pinsatz mit unabhängig übergebenem SHA256-Anker; bekannte Engine-/Vanilla- bzw. 61DC-GameMP-Pins zusätzlich fest prüfen. Exe/Entities-Pins stammen aus vertrauenswürdigem Hostmanifest, nicht aus erfundenen Originalhashes. Snapshotreferenzen ausschließlich relativ unter explizitem privaten Evidenzroot, keine Symlinks/Traversal/Spezialdateien; begrenzte unveränderliche Rohbytes hashen und strikt dekodieren. Rohtext muss eindeutige Level/Sequence/Decimal-Tick/CRC enthalten, mit Manifest übereinstimmen und rollenweise exakt paaren. Fehlende/duplizierte/ungültige/unvollständige Daten => Exit 2; validierte Metadaten => Exit 0, ausdrücklich keine native Sync-/Tick-/Ursachenfreigabe. Vollständigkeit ist bei unbekanntem Retail-Footer nur begrenzt prüfbar; keine erfundene native Endemarkierung, Host-Vollständigkeitserklärung und messbare Grenzen dokumentieren.

- [x] Neue synthetische stdlib-unittests mit privaten Platzhaltern und temporären Dateien schreiben; gezieltes RED ohne Implementierung belegen.
- [x] Minimalen sicheren Reader, JSON-/Pin-/Rohdump-/Paarungsvalidator und redigierte CLI implementieren; GREEN prüfen.
- [x] Schema, Vertrauensgrenze, Trunkierungs-/Samplinggrenzen und plattformabhängige sichere Dateizugriffe dokumentieren; Tests um reale Reviewlücken ergänzen.
- [x] Gezielte neue Tests plus bestehende portable Regressionsauswahl/Provenienz und C++-Gate einmal zur Abschlussfreigabe, keine private Discovery. Scope-/Datenschutz-/Diffcheck, Ledger mit Exitcodes, kein Push/Merge. Bekannte Git-Sandboxsperre nicht wiederholt testen; Host erhält Änderungen uncommitted.


Ergebnis: stdlib-only Validator, 30 synthetische Tests und vollständiger Schema-v1-Vertrag implementiert. Unabhängiger Pinsatz mit SHA256-Trustanker; sichere descriptor-relative POSIX-Dateizugriffe, keine Symlinks/Hardlinks/Traversal/Spezialdateien; Rohbyte-Integrität, streng deklarierte Encodings, eindeutige Rohheader, exakte Decimal-Paarung, Null-Drop-/Finalisierungsdeklaration, Größenlimits und redigierte Reports. Status ausschließlich VALIDATED_CAPTURE_METADATA bzw. INVALID_EVIDENCE_MANIFEST; native Sync/Authentizität/Tickkontinuität nicht geprüft. Windows-sicherer Reader noch nicht implementiert; auf nicht unterstützten Hosts fail closed. Endemarker unbekannt: neu gehashte/deklarierte zeilengenaue Teilkopie nicht erkennbar, deshalb keine native Vollständigkeitsabnahme.

Gezieltes RED (fehlender Erfolgsfall) Exit 1, GREEN 30/30 Exit 0. Abschlussregression einmal: 44 portable Python-Tests, 13 Provenienzprüfungen und sechs enginefreie C++-Programme Exit 0. Keine private Discovery, kein neuer Zweigexporttest. Nur fünf eigene Scope-Dateien; Quell-/Comparator-/Runtimebestände unverändert. Details/Exitcodes im Ledger. Host kann die Änderungen unabhängig prüfen und committen; keine Git-Schreib-/Pushversuche aus dieser Sitzung.
