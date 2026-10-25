# Identitäten/Sitzungen – Handoff und Ergebnisstand, 21.10.2026

**Fortsetzung ab 23:14 UTC:** Native Mehrbot-Bridge, individuelle Vierbot-Sessions, Crash/Ghost/Rejoin und Farb-/Namensprüfung inzwischen implementiert und begrenzt bestanden. Achtbot-/Stundenqualifikation ist nach zwei dokumentierten RAM-Guards blockiert; alle eigenen Tests beendet, Produktion unverändert. Aktueller Code `9bc8908`, 124+59 Python-Tests und C++-Regressionen bestanden. Maßgeblich: [aktueller Bericht](2026-10-21-session-execution.md) und [Messwerte](2026-10-21-session-execution-results.json).

**Historischer Stand vor dieser Fortsetzung:** Neuer Stand: `NATIVE_INPLACE_ONE_BOT_REJOIN_PASS / MULTI_BOT_SCHEDULER_NOT_IMPLEMENTED`. Der frühere Blocker `NATIVE_BLOCKED_ACTIVE_PR46_QUALIFICATION` ist seit 18:09 UTC erledigt.
Kein produktiver Einsatz, keine neue Retail-DLL, keine behauptete Verbesserung der tatsächlich spielenden KI.
Seit 17:54 UTC ist Task3a mit einem **rein portablen** Adapter ergänzt; die ältere Bilanz 72 Tests beschreibt den vorigen Stand.

## Veröffentlichung
[Draft-PR #47](https://github.com/Escoba2024/SeriousSam-TSE-Bot-Servermods-/pull/47), offen und nicht merge-/aktivierungsbereit.
HTTPS-Push auf Hetzner hat keine Git-Anmeldung. Der verbundene GitHub-Connector veröffentlichte stattdessen den byteidentischen Implementierungsbaum `b1bcf596beeacdceecbe8f109c64efb011a881d3` als `a94f36aea4560095da097c912103cb14582823a5`.
Alle neun Blob-Hashes und der vollständige Tree wurden mit dem lokal geprüften `f9d8a40519f9419efe173a1216de4cbf9bdb0ed7` abgeglichen.
Lokale Belegcommits bleiben unter `agent/identities/20261021-sessions-local-proof` erhalten. Der eigene Worktree folgt dem veröffentlichten PR-Branch; spätere Dokumentationscommits ändern keinen getesteten Code.
Keine Änderung von Zugangsdaten, Credential-Helpern oder fremder Git-Konfiguration.

## Eigene Arbeit
- Hetzner: `/srv/tse-identities-20261021`, Branch `agent/identities/20261021-sessions`.
- Basis: `fdfc46eae8ba5557af427c1b36fc91b0d95aec37` (gemergter PR #45).
- Portabler Implementierungscommit: `8467149777c86303aebe67c75f65d9f766bdae89`.
- Plan: [Ausführungsplan](../superpowers/plans/2026-10-21-identities-sessions.md).
- [Entwurf](../superpowers/specs/2026-10-21-identities-sessions-design.md), [API/Runbook/Aktivierung/Rollback](2026-10-21-identities-sessions-runbook.md).
- Kein fremder Worktree übernommen. Keine Änderung an `tools/operations/`, qualifizierten Quellen/DLLs, Runtime-Skripten, Prozessen, Ports, DNS oder Services.
- Lokales fortsetzbares Ledger: `.codex/PROJECT_STATE.md`, bereits durch vorhandene Ignore-Regel ausgeschlossen.

## Implementierter und geprüfter Teil
24 konfigurierbare fiktive Identitäten im Beispiel; bereinigte, eindeutig sichtbare Namen.
SQLite speichert GUIDs, Gameplay-Seeds, feste vorhandene Rosterprofile, Serverzuordnung, Status, Session-Epoch und Ereignisse.
OFFLINE/WAITING/JOINING/PLAYING/LEAVING/COOLDOWN; gewichtete Sessionbänder, gestaffelte Joinabstände,
echte Pausen, Menschenreserve, globale Begrenzung auf je einen laufenden Join/Leave und persistenter Admin-Halt.
Farben nur Metadaten; Ausgabe bewusst gesperrt, bis echte Retail-Nachweise vorliegen.
Das Modul erzeugt Absichten, führt sie nicht aus. Die Reservierung ist transaktional;
eine spätere genau-einmalige Prozessausführung benötigt den noch fehlenden Eigentums-/Recovery-Adapter.

## Reproduzierbare Nachweise – ausschließlich auf Hetzner
```bash
cd /srv/tse-identities-20261021
python3 -m unittest discover -s tools -p 'test_*.py'
python3 -m unittest discover -s tools -p test_bot_sessions.py -v
git diff --check
```
- Ausgangssuite: 43 Tests, OK, 2.004 s.
- Eigene vollständige Python-Suite: **72 Tests, OK**, 3.227 s im letzten Lauf; davon **29 neu**.
- Unabhängiger Reviewer führte die 29 neuen Prüfungen separat aus: 29 PASS / 0 FAIL / 0 SKIP / OK.
  Kein belegter blockierender Fehler im portablen Kern; nur als deaktivierter Draft-Teilstand reviewfähig.
- Echte gleichzeitige SQLite-Controller geprüft, nicht nur sequenzielle Wiederholung.
- Neues Beispiel wurde mit `:memory:` tatsächlich importiert/ausgeführt: deaktiviert keine Absicht;
  aktiviert offline genau eine Join-Absicht, **null gestartete Spiele**.
- 200 virtuelle Sitzungen mit normalen Zeitbändern, Seed 20261021, Ein-Identitäts-Fixture:
  19 kurz / 163 mittel / 18 lang; Minimum 306 s, Maximum 10508 s; Pause jeweils 900 s.
  Dies sind **virtuelle Zeitwerte**, keine real abgewarteten Sessions, kein Lastbenchmark und keine Langzeitabnahme.
- RED-Belege: zunächst fehlendes Modul; zusätzliche echte Assertion-Fehler bei unbekannter menschlicher Formatierung,
  nichtganzzahligen Epochs und ungültiger Konfiguration; anschließend GREEN.
- Private Ausgaben: `.codex/evidence/{baseline-python,python-suite,sessions-*,normal-policy-simulation.json}`.
  Keine Rohlogs, Profile/GUID-Datenbanken, Retail-Binaries oder Screenshots in Git.
- C++/MSVC-/CPU-/Retail-/Gameplay-Prüfungen dieses Kandidaten nicht durchgeführt. Keine C++-Quelle verändert.

## Live-Bestand und belegter externer Blocker
Bestandsprüfung über GitHub-Connector und RDC auf Hetzner, etwa 17:07–17:24 UTC:
- PR #45 gemergt; PR #46 offen/Draft, bei Erstprüfung `d6d29115e807826f8d4ca802359b535b31362fcd`.
  Dessen Plan ist `docs/superpowers/plans/2026-10-21-alpha-gaming-next-phase-reliability.md`.
- Fremde laufende Qualifikation: `/srv/tse-reliability-evidence-20261021/native-qualification.json`
  meldet `RUNNING / MEASURING_3600`; PID 135203 `qualify-ops.py`,
  Supervisor PID 135705, eigene fremde Testports 26820/26821,
  Runtime `/srv/tse-ops-runtime-20261021/eight/eight-164719-1o1hrlr9`.
  PID-/Phasenwerte sind Momentaufnahmen, vor Fortsetzung erneut prüfen.
- Öffentliche Instanz auf 25600/25601 hat weiterhin acht Bots; frische Query/Telemetrie und Prozessnachweise
  aus `/srv/tse-public-health-20261021/health.json`. Eigene Bot-SYNCBAD 0.
  Bestehender historischer Alert `EXTERNAL_CLIENT_SYNC` mit 21 externen SYNCBAD wird nicht als neuer eigener Fehler ausgegeben.
- Neuer letzter Snapshot 17:24:31 UTC: neun Spieler = acht eigene Bots + ein Mensch,
  frische Query/Telemetrie, zusätzliche Warnung HUMAN_HOLD und safe_recovery=false.
  Name/Identität dieses Menschen werden nicht veröffentlicht. Kein Eingriff.
- Beide öffentlichen Bot-DLLs frisch gehasht:
  `7fc94a39c3f5d9516f262d9e4d04a5cf38e6eb5ae3482976c32c952a99d30835`.
- 2 vCPU / 3819 MiB RAM; ca. 16 GiB Platte frei.
  Aus bisheriger Acht-Bot-Baseline folgt keine Reserve für zusätzlich 2x8 mit neuen Einzelverbindungsprozessen.
- App-Thread-/Prozessinventar gelesen; keine laufenden Agenten gestoppt oder angeschrieben.
  Ein separater Reviewer prüfte ausschließlich unseren eigenen Teilstand ohne Runtime-Eingriff.

Zusätzliche Retail-Prozesse, Builds oder Lastbenchmarks während des fremden Stundenfensters würden dessen
CPU-/RAM-/Stabilitätsbelege beeinflussen. Der Benutzerauftrag untersagt genau diese Kollision.
Deshalb kein neues Runtime-Experiment. Es gibt **keine** Freigabe zur vorzeitigen Beendigung der fremden Messung.

## Offene Umsetzung und kleinster nächster Schritt
1. Nach tatsächlichem Ende der fremden PR-46-Qualifikation deren Ergebnis/Prozesse/Ports/Ressourcen frisch lesen.
   Nicht nur auf vergangene Uhrzeit oder verschwundenen Controller vertrauen.
2. Runtime-Vertrag mit dann aktuellem PR-46-Sollzustand festlegen. Der Supervisor darf geplante Offline-/Cooldown-Slots
   nicht als fehlgeschlagene Pflicht-Bots auffüllen. Aktuell darf dieser Planer deshalb nicht parallel aktiviert werden.
3. Einen eigenen Einzelverbindungsprozess in einer separaten Overlay-/Wine-/PID-/cgroup-/Port-Umgebung starten,
   ohne öffentliche Flotte zu stoppen. Regulären Join/Quit und stabile GUID-Rückkehr zuerst belegen.
   Retail-Header bietet AddPlayer_t, aber keinen belegten Einzelabmeldepfad der vier lokalen Slots.
   Einzelprozess je Identität ist eine ungemessene Option, keine erteilte 8/16-Prozess-Kapazitätsfreigabe.
4. Native Farbcodesyntax und tatsächliche Name-Grenzen in HUD, Meldungen und Query ermitteln;
   erst danach den Ausgabe-Gate ändern.
5. Fehlende Gameplay-Anforderungen (Ressourceninteressen, passende Orientierungs-/Entscheidungspausen) gezielt
   in die vorhandene Human-KI integrieren und separat qualifizieren.
6. 1/4/8, dann zwei isolierte Instanzen mit je acht; mindestens 3600 s gemeinsamer neuer Stabilitätslauf.
   CPU/RAM/20Hz/SYNCBAD/Disconnect/Restart messen, normale Echtzeitsitzungen und beschleunigte Tests trennen.
   Profile unter vergleichbaren Bedingungen beobachten; Unit-Tests sind kein Gameplay-Urteil.

**Produktionsstatus:** acht vorhandene qualifizierte Build04-Bots bleiben aktiv.
Dieser PR liefert keine produktive Aktivierung und keine isoliert vollständig qualifizierte Gesamtänderung.

## Fortsetzung im Chat über Hetzner RDC, 2026-10-21 17:54 UTC
Task 3a (portabler Adapter) programmiert in eigenem Branch/Worktree.
Dateien: `tools/bot_session_runtime.py` und `tools/test_bot_session_runtime.py`.
Neu: PLC4-Profilbyte-Patch ohne Team-/Appearance-Veränderung, fester UUIDv5-Sidecar, BotDriver-Seed/Profil-INI-Overrides nur für späteren Einzelspieler-Test, `flock` über realpath, transaktional genau einmal reservierbarer Launch-Epoch in SQLite, reine fail-closed Prozess-/Query-/Ghost-Reconciliation.
Die neuen 17 Tests prüfen unter anderem die unveränderte originale Retail-Vorlage **nur lesend**, Hardlink-/Symlink-Grenzen, Kernel-Lock-Recovery, Claim-Persistenz über Neuöffnung, falsche Epoch/Identität und Ghost-/Human-/Unknown-Holds.
Test-Ergebnis: volle Python-Tools-Suite **89 Tests OK (3.634 s)**, zusätzlich `git diff --check` PASS; privates Log `.codex/evidence/adapter-python-suite.log`.
Grenze: `reconcile` liefert ausschließlich eine Entscheidung; **keine** native PID-Discovery, Launch-/Quit-Automation oder PR46-Supervisor-Integration. `claim_launch` muss vor jedem künftigen Prozessstart unter ControllerLock atomar verbraucht werden. Unerwarteter Abbruch nach Claim verlangt Recovery/Quarantäne statt eines automatischen Zweitstarts.
Farbcodes bleiben bis zu originaler HUD-/Scoreboard-/Query-/Name-Limit-Abnahme gesperrt. Individuelle echte Retail-Verbindung, Quit/Rückkehr, neue Human-KI-Verbesserungen und 2×8-Tests sind **nicht** abgeschlossen.
Produktive Acht-Bot-Instanz, Spielbinaries, Profile, Ports, Dienste, fremder PR46-Supervisor/Qualifier und Backups unverändert.
Nächster Schritt nach tatsächlichem Ende der fremden nativen PR46-Stundenmessung: neuen Eigentums-/Ressourcencheck, isolierter einzelner Botprozess und nachweisliche Join-/Leave-/Profil-ID-/GUID-Abnahme, ohne die öffentliche Flotte zu unterbrechen.

### Follow-up 18:00 UTC
GitHub #47 auf erstem Adaptercommit `507217ccfd82407ffcb5e3ded473d51309e16d64` aktualisiert und lokale Branch-Referenz nach Prüfung des identischen Trees sauber mit `origin` synchronisiert; lokaler Beweiscommit `9e960aa` bleibt unter `agent/identities/20261021-adapter-local-proof` erhalten.
Zwei ergänzende Tests belegen reale zweite Prozesssperre und rein simulierten lückenlosen Planner-/Adapter-/SQLite-Claim-Lebenszyklus. Volle Python-Suite: **91/91 PASS (3.985 s)**, davon **19 Runtime-Adapter-Tests**.
Native PR46-Qualifikation 18:00:22 UTC weiterhin `MEASURING_3600` (3044 s); weitere Retail-Prozesse deshalb weiterhin gesperrt.

### Vorbereitung eines wirklich isolierten Retail-Single-Smokes, 18:07 UTC
Der bestehende Harness `tools/qualify_integrated_wine.py` besitzt einen zusätzlichen strikt privaten `--identity-record`-Pfad für `stage one`, dessen Build04-Overlay vor jedem PLC4-/Sidecar-Write als Mount geprüft wird. Alte Stufen ohne Flag haben ihren bisherigen Codepfad. Die echte Quelle und Public-Build04 sind nicht angefasst.
Statische Probe ohne Wine und mit ausschließlich simulierter Mountprüfung bestanden; volle Tools-Python-Suite **92/92 PASS (3.740 s)**. Noch keine zweite Live-Instanz, kein echter individueller Beitritt, kein bestätigter Farbcode. Vor Native-Start PR46-Abschluss, Prozesse/Mounts/Ports/CPU/Disk/Human-Hold frisch prüfen.

## Native Fortsetzung 18:29 UTC – bestätigter privater Einzel-Bot-Lebenszyklus
Der zuvor belegte PR46-Hour-Blocker ist weggefallen: `PASS_ISOLATED_LIFECYCLE_AND_60MIN` (3600.004 s, null neue Throttles, 8 Public + 8 Privat gleichzeitig, alle fremden Testmounts aufgeräumt). Öffentliche acht Build04-Bots durch eigene Tests unverändert auf 25600/25601.

Eigene isolierte Original-Retail-1.07-Läufe auf 26980/26981, Xvfb :119: Preflight Plain, dann 120s + 70s Plain mit byte-identischem GUID-Profil, Preflight Color + 45s isolierter Colorprobe, danach **echter Same-Server WM_DELETE_WINDOW-Abgang und Rückkehr** sowie 45s Stabilität. Vier native Läufe: alle PASS_LIMITED, alle `ACTIVE_OK`, 0 neue CPU-Throttles, sämtliche sechs Mounts pro Lauf sauber ausgehängt. Rejoin-Probe: 3 Query-Abwesenheiten, Server und Vanilla beobachten durchgehend, alte/neue Bot-PIDs verschieden, GUID- und Profilhash stabil. Beweisdaten ohne Rohlogs/Player-GUIDs: `docs/reports/2026-10-21-identities-native-smokes.json`; vollständige private Nachweise nur auf Hetzner unter `/srv/tse-identity-native-runtime-20261021`.

**Farbstatus:** Die private PLC4-Formatierung `^c80D8FFMika^r` wurde vom Original-Retail-1.07-Server als Spieler akzeptiert und GameSpy gab `Mika` aus. Echter HUD-/Scoreboard-Farbeindruck konnte nicht belegt werden (privater Xvfb-Screenshot zeigte Splash). Keine Produktionsfarbe freigeben.

**Grenze des Fortschritts:** Die native Probe ist **manuell isoliert**, nicht mit SQLite-JOINING/LEAVING-Policy und nicht mit PR46-Produktionssupervisor als einheitlichem Desired State verdrahtet. Acht unabhängige Einzelprozesse, normale 20–90-Minuten-Sitzungen und Human-Konflikte nativ noch nicht qualifiziert. Die bisherigen 8+8 vom PR46-Stundentest sind zwei Clients je 4 Bots, **nicht** 8 einzelne Sessions je Instanz. Nutzerziel NICHT vollständig.

**Eingriffsschutz:** Original-Referenz-DLL auf dem Template SHA256 `61dc27e0e7b80badcf9ae705c30fca88edd3935737715dffff59e90c26f1fef9` unverändert, Test-DLL SHA256 `7fc94a39c3f5d9516f262d9e4d04a5cf38e6eb5ae3482976c32c952a99d30835`; Public-Prozesse/PIDs und Ports unverändert, Besitzer-SYNCBAD 0. Kein externes Backend geändert.

Nächster eigentumsbewusster Schritt: native PLC4-Profile und Start-/Stopprozesse pro SQLite-Identität verwalten, unter ControllerLock transaktionalen Launch-Claim verbrauchen; Join/Leave-Ack nur nach überprüfter Prozessidentität und vollständiger GameSpy-Query, eigens isoliert 1→4→8 messen; PR46-Supervisor-Sollzustand erst nach kollisionsfreier Integration ändern; Farb-Gate gesperrt lassen.
