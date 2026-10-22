# PR #47 – autonome Fortsetzung der individuellen Sitzungen

Arbeitsbeginn: 21.10.2026, ca. 23:14 UTC. **Gesamtqualifizierung offen.**
Dieser Bericht wird mit den tatsächlichen Native-Ergebnissen fortgeschrieben.

## Rekonstruktion

Host `ubuntu-4gb-nbg1-2`, Ubuntu 24.04.4, 2 vCPU, 3819 MiB RAM.
Bestehender Worktree/Branch bei `2914e1c` sauber übernommen; GitHub-HEAD gleich.
PR #46 und #47 offen/Draft. Der zweite Codex-Prozess ist ein App-Server-Proxy,
kein zweiter Implementierer. Keine neue Entwicklungssitzung oder zweite
Runtime-Steuerung gestartet. Der einzige zusätzliche Reviewer liest ausschließlich
Code. Die existierenden fremden Änderungen im Reliability-Worktree bleiben erhalten.

Die öffentliche Dedicated-PID 124818 und Bot-PIDs 124882/124950 bleiben aktiv.
Frischer öffentlicher Status: acht Bots, eigene Syncfehler 0. Der Monitor meldet
separat historische Syncfehler externer Clients; das wird nicht als eigener
Scheduler-Fehler umgedeutet. Rückfallarchiv und qualifizierte Binaries erhalten.
Zu Beginn etwa 15 GiB freie Platte und 2352 MiB verfügbarer RAM, ohne Swap.

## Implementierung und portable Prüfung

- `fbdb461`: ausführende Planner-Bridge und ausschließlich privater Native-Runner.
- Dauerhafte Start-/Leave-Claims, vollständige Query-Validierung, GUID-Prüfung,
  Prozessbindung und geplante individuelle Abgänge; keine feste Slot-Recovery.
- Neue zentrale `min_bots`-Option; native Farben standardmäßig aus, nach begrenztem Retail-Nachweis zuschaltbar.
- Kernel-Freigabe bei Controller-Ende, kein zeitbasiertes Lock-Stehlen;
  Parent-Death-Abbruch und erneutes Öffnen der SQLite-Verbindung während realer Sessions.
- 94 Bestandstests frisch bestanden; nach Erweiterungen zuletzt **124 Python-Tests
  bestanden**, einschließlich echter Prozessbindung/Elternende und simulierter
  Mehrbot-Lebenszyklen. Portable Simulation ist keine Native-Abnahme.
- Testkommandos: `python3 -m unittest discover -s tools -p 'test_*.py'`
  und `git diff --check`.

## Bisherige native Ergebnisse

Private Belege: `/srv/tse-session-qualification-*`, zusätzlich
`.codex/evidence/` im eigenen Worktree. Rohdaten nicht veröffentlichen.

| Lauf | Ergebnis | Geltungsbereich |
|---|---|---|
| `one-20261021` | Setup abgelehnt | Falsche sysfs-basierte Namespace-Prüfung, noch keine Spielprozesse |
| `one-retry-20261021` | FAIL/sauber beendet | Unpassender Xvfb-Modus, eigene Originalclient-Anzeige schlug fehl; 6/6 Unmounts |
| `disabled-test` | Fehler des neuen Sicherheitstests | Fehlendes Enabled-Gate erzeugte private Overlays; belegte Testanzeige verhinderte Spielstart; 8/8 Unmounts. Test auf reine Vorprüfung umgestellt, Gate und globale Sperre ergänzt |
| `one-r3-20261021` | PASS_LIMITED | 180,962 s, zwei automatische Joins und reguläre Leaves mit gleicher Identität, Peak 1, Originalclient parallel, 6/6 Unmounts |
| `one-stable-20261021` | PASS_LIMITED | 180 s Messfenster, 2 Joins/2 reguläre Leaves, 2× ACTIVE_OK mit 20 Hz, echte DB-Neuöffnung bei laufenden Clients; 558,688 MiB private cgroup-Spitze, 45,589 % eines Kerns einschließlich Aufbau/Drain; 6/6 Unmounts. Nachträgliche Prüfung aller vier vollständigen aktuellen/archivierten Generationen: 0 Sync-/Fatalfehler |
| `one-color-20261021` | INTERRUPTED/FAIL | Äußerer Controller endete mit Signal 143; genaue Signalquelle nicht belegt. Innerer Parent-Death-Pfad schloss eigene Clients und hängte 6/6 Overlays aus. Kein Farb-Sicht-PASS |

Die erste private Aufnahme zeigte das Originalspiel, aber noch keinen Bot im
Scoreboard; eine weitere Aufnahme zeigte einen Splash. Kein Farberfolg daraus
abgeleitet. Der überarbeitete Originalclient-Fenster-/FPS-Pfad benötigt eine
eigene neue Native-Prüfung. Die Konsolen-FPS-Vorgabe allein belegt keine wirksame
Bildratenbegrenzung.

## Unabhängiger Code-Review

Read-only Review von `2914e1c..fbdb461` einschließlich Observer-Ergänzung:
keine Critical-Findings, zwei Important-Findings. Beide reproduziert und in
`ee9713d` mit neuen Regressionen behoben: Aufräumfehler pro Ressource isolieren,
weitere eigene Prozesse trotzdem abbauen und Fehlerstatus erhalten; Sync-/Fatal-
Prüfung über aktuelle und archivierte Generationen sowie den gesamten Drain.
114 Tests danach PASS. Der Reviewer hat keine Runtime-Abnahme durchgeführt.

Zurückgestellter kleiner Punkt: leere private cgroups bleiben nach Tests bestehen.
Sie enthalten nach sauberem Teardown keine Prozesse. Produktionsintegration und
Wiederaufnahme nach vollständigem Controllerverlust sind eigenständige offene
Gates; erneutes Öffnen der DB im laufenden Controller ersetzt diese nicht.
Bestehende Human-KI/DLL bewusst erhalten; keine neue Gameplay-Funktion behauptet.

## Fortgeschriebene Ergebnisse

- `four-r3-20261021`: **PASS_LIMITED_SESSION_LIFECYCLE**, 360 s Messung /
  389,459 s einschließlich Drain, Peak vier eigene Einzelprozesse plus
  unveränderter Originalclient. Acht Joins, sieben reguläre Leaves, ein
  gezielter eigener Crash, korrekter Cooldown und Rejoin. Zwei DB-Neuöffnungen.
  Jede Identität hat zwei ACTIVE_OK-Intervalle mit 20-Hz-Median; vollständige
  zehn Generationenlogs ohne Sync-/Fatalfehler. Alle vier Profile und GUID-
  Sidecars stimmen nach Rückkehr bytegenau mit der deterministischen Vorlage
  überein. Ein Ghost-Zeitraum ist keine aktive Spielzeit.
- Private cgroup: Peak 1157,992 MiB, 72,495 % eines CPU-Kerns einschließlich
  Aufbau/Drain, null neue Throttles. Gesamter Host: mittlere Auslastung 65,602 %,
  P95 84,397 %, geringster verfügbarer RAM 1178,957 MiB. Das ist eine begrenzte
  Funktionsprüfung und keine Produktions-Kapazitätsfreigabe. 12/12 Unmounts,
  äußerer Guard FINISHED, unveränderte Public-PIDs.
- `color-boundary-20261021`: **PASS_LIMITED**, 90 s Messung / 97,178 s mit Drain,
  vollständiger orangefarbener Name `ColorBoundaryName12345` im Original-HUD
  und im GameSpy-Status. Profilfeld exakt 32 Bytes einschließlich `^cFF7A4D`
  und `^r`. Vier unterschiedliche Poolfarben im Vierbot-Scoreboard geprüft.
  Keine sichtbaren Rohcodes. Sechs erfolgreiche Unmounts.
- Aktuell 124 Root-Python-Tests und 59 weitere Benchmark-Werkzeugtests bestanden.
  `make -C poc/botcore test smoke
  BOTDRIVER=../candidates/integrated-human-cpu-20261021/BotDriver.cpp` bestanden,
  darin 555 Human-KI-Checks und echter Integration-Block. Ein vorhandener
  unbenutzter Clamp-Helfer erzeugt eine Compiler-Warnung, keine Testfehler.
- Vorläufer-Vierbot-Läufe wurden korrekt nicht als bestanden gezählt: zunächst
  zu strenge Query-Slotprüfung; danach reproduzierbare lückenhafte Retail-
  Slotnummern nach eigenem Crash. Parser und persistente Crash-Provenienz
  durch neue Regressionen korrigiert und in obigem Lauf erneut nativ geprüft.

## Reproduktion und weitere Gates

Aus `poc/scripts/BotSessions.example.json` eine **private Kopie** erzeugen:
genau einen Server-ID-Eintrag, `enabled=true`, gewünschte Anzahl 1/4/8 in
`max_bots` und genau so viele eindeutige Pool-Einträge. Kurze Sitzungs-/Pausenzeiten
erfordern `accelerated=true`; normale Zeitbänder bleiben separat zu prüfen.
Alle Identitäten müssen ihren Pool-ID/Seed/Profileintrag bei DB-Neustarts behalten.

```sh
python3 tools/qualify_bot_sessions.py \
  --config /privater/pfad/sessions.json \
  --runtime /srv/tse-session-qualification-eindeutiger-lauf \
  --duration 3600
```

Ohne `--execute`: `DRY_RUN_NO_RUNTIME`, keine Spiele oder Laufzeitdateien.
`--execute` startet nach den Guards eine frische private Qualifikation;
existierende Laufverzeichnisse werden niemals überschrieben. `--color-probe`
ist ausschließlich ein nativer Testschalter und aktiviert keine Produktionsfarben.
Private Ergebnisdateien: `result.json`, `host-guard.json`, `samples.jsonl`,
`source-sha256.json`, SQLite und unveränderte archivierte Einzelgenerationen.
Ein PASS benötigt zusätzlich erfolgreiche Aufräumergebnisse.

Offen: acht Einzelprozesse mit >=60 Minuten und normalen Zeitbändern,
aktive menschliche Originalclients,
Ressourcenabnahme und abgestimmte Produktionsintegration. Kein Merge/Rollout
aus dem bisher begrenzten Ergebnis ableiten.

## Kapazitätszwischenstand

`eight-20261021`: **BLOCKED_CAPACITY / kein Stunden-PASS**. Bei fünf verbundenen
Bots wurde Client sechs vor seinem Start verweigert: verfügbarer RAM 970,465 MiB
statt erforderlicher 1068 MiB. Private cgroup-Spitze 1322,781 MiB. Cleanup: 20/20
Unmounts, keine Cleanup-Fehler, Public unverändert. Die eigenen Schutzschwellen
bleiben erhalten. Anschließend begrenzter opt-in Grafikversuch im eigenen
Native-Runner: `one-lowmem-20261021` über 90 s PASS_LIMITED, 546,148 MiB Peak,
null neue Throttles und sechs Unmounts. Eine Vierbot- und erneute Achtbotprüfung
folgen seriell; eine ausreichende Kapazitätsverbesserung ist noch nicht belegt.
