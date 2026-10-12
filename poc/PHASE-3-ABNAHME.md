# Lokale Netzwerkabnahme – 10.10.2026

Die lokale Basis mit zwei getrennten BotClient-Prozessen und insgesamt acht
echten Netzwerkspielern ist abgenommen. Zusätzlich ist der separate
Zwei-Bot-Stundennachweis bestanden. Beide frischen Läufe verwenden dieselbe
finale Recovery-DLL; abgebrochene Vorgängerversuche zählen nicht zur Laufzeit.

## Architektur und Build

Nur die separaten BotClients verwenden die modifizierte `GameMP.dll`.
Dedicated Server, Engine, EntitiesMP, menschlicher Client und Vanilla-Observer
bleiben unverändert. Pro Prozess höchstens vier lokale Spieler, eigene
Profile/GUIDs und normale `CPlayerAction`-/`CPlayerSource::SetAction`-Eingaben.

Finaler Build: `.codex/shadow-20261010-reconnect-final`.
DLL: `Sources/Bin/vs2022.Release_TSE107/GameMP.dll`.
SHA256: `24053920C63E02F9883056331B246BEF2D08D645FFCCE2C74ED7EDC9B35B9ACF`.
Der zusätzliche Recovery-Patch ist `patch/0003-gamemp-reconnect-transaction.patch`
und setzt den vorhandenen Patch `0002-gamemp-bot-reconnect.patch` voraus.
Der getestete x86-Build nutzt v143; die Spiel-DLL wurde für diesen Abschluss
nicht nochmals geändert. Git-HEAD bleibt `c636a53`; keine Veröffentlichung.

## Native Stundenbelege

| Gate | Native Gesamtlaufzeit | Vollständige Spielerabfragen | Aktive Bot-Minutenfenster | Snapshots pro geprüftem Fenster |
|---|---:|---:|---:|---:|
| Acht Bots, zwei Prozesse mit je vier Spielern | 5458,960 s | 3700,637 s / 728 Abfragen | 480 | 1200 |
| Zwei Bots, ein Prozess mit zwei Spielern | 3700,359 s | 3674,066 s / 365 Abfragen | 120 | 1200 |

Jedes Minutenfenster verlangt monotone native Ticks, mindestens zehn verschiedene
Positionen und Yaw-Werte sowie angewendetes Feuer an/aus. Beide Läufe zeigen
Version 1.07, leeren Mod, vollständige Namenlisten und eindeutige Profile/GUIDs.
CRC akzeptiert: sechs Verbindungen im Acht-Bot-Szenario, zwei im Zweibot-Szenario.

Der Acht-Bot-Lifecycle zeigt reale Slots `8 → 9 → 8 → 9 → 8 → 4 → 8`:
zwei Beitritte eines normalen menschlichen Clients mit regulären Abgängen,
danach kontrollierter Neustart von B. A bleibt dabei derselbe Prozess;
der neue B übernimmt seine eigenen vier Profile. Nach dem Rejoin bleiben die
beiden finalen Botprozesse über den vollständigen Messzeitraum erhalten.

Die Acht-Bot-Gesamtlaufzeit enthält die langsame PowerShell-Nachauswertung,
während die Clients weiterliefen. Als früher unabhängiger Aktivitätsbeleg
werden alle acht replizierten Spieler in gemeinsamen A-Tickfenstern
`2372..74371` ausgewertet: native Minuten 2 bis 61 nach dem B-Rejoin.
Grundlage ist das vor der langen Auswertung erfasste Log-Prefix. Es wurde
11,942 Sekunden nach der finalen Spielerabfrage gelesen; ein unvollständiges
Zeichen am Capture-Rand ist ausgeschlossen und kein Snapshot wird repariert.
Spätere Logdaten dürfen dieses frühe Fenster nicht ergänzen.
Einzelne Snapshots haben keine UTC-Zeitstempel; eine punktgenaue gemeinsame
UTC-Action-/Query-Stunde ist damit nicht behauptet.

Zusätzlich sind die eigenen finalen Botlogs, lokale Spielerzuordnungen und
reguläre Cleanupmarker geprüft. Beide finalen Acht-Bot-Clients enden regulär
mit Retail-Exitcode 1. Der Zweibot-Runner verwendet einen harten Teardown und
belegt damit Stabilität, keinen regulären Shutdown. Für Server und Observer
wird aus diesen Stundenläufen ebenfalls kein regulärer Shutdown abgeleitet.

## Ressourcen und Wiederherstellung

Host: acht logische CPUs; `ded_bRestartWhenEmpty=0` aus der effektiven
Testkonfiguration gesichert. CPU-Angaben sind Prozess-CPU-Zeit geteilt durch
Messdauer und acht logische CPUs, keine gesamte Hostauslastung.

| Lauf | Prozess | Mittlere CPU / Hostkapazität | Maximales privates RAM |
|---|---|---:|---:|
| Acht Bots | BotClient A | 3,83 % | 90,95 MiB |
| Acht Bots | BotClient B | 3,82 % | 90,97 MiB |
| Acht Bots | Dedicated Server | 0,54 % | 21,71 MiB |
| Zwei Bots | BotClient | 1,36 % | 85,91 MiB |
| Zwei Bots | Vanilla-Observer | 0,94 % | 85,90 MiB |
| Zwei Bots | Dedicated Server | 0,15 % | 20,98 MiB |

Der PowerShell-Telemetrieprüfer ist nicht in den BotClient-RAM-Werten enthalten;
GPU-Auslastung wurde nicht gemessen.

Abschließend sind 30 Ausgangsbinaries hashgleich und alle 815 globalen
Manifesteinträge der fünf isolierten Kopien gegen Ausgangshash beziehungsweise
ursprüngliche Abwesenheit geprüft. Der Zweibot-Runner restaurierte zusätzlich
489 erfasste Einträge. Keine isolierten Spielprozesse, Testports, Crashreports
oder passenden Crash-Events; Application-Eventlog gelesen. Die drei schon
vorher geänderten Quelldateien zeigen einen unveränderten Git-Diff.
Diese Git-Prüfung belegt keine identischen Rohbytes der Arbeitsdateien.

## Reproduktion und lokale Evidenz

Die vollständigen Befehle stehen im Runbook. Frische Evidence-Verzeichnisse
verwenden und die fünf Testkopien ausschließlich nacheinander belegen.
Die beiden Abschlussläufe verwenden `-Seconds 3700 -SyncMinutes 60` und
explizit die oben genannte finale DLL. Acht Bots zusätzlich mit `-Lifecycle`,
zwei Bots über `run-shadow-validation.ps1 -Mode Soak -Counts 2`.

Lokales Evidence-Verzeichnis: `.codex/evidence/shadow-20261010/completion/`.
Der vollständige Bericht steht in `report.md`; entscheidende Dateien:

- `eight-bot-60m/retail/result.json`, `eight-bot-60m/acceptance-audit.json`, `eight-bot-60m/hour-acceptance-audit.json`;
- `two-bot-60m/native-2-Soak/result.json`, `two-bot-60m/diagnostics.json`, `two-bot-60m/hour-acceptance-audit.json`;
- native Logs, Profile/GUID-Inventur, Spielerabfragen und Ressourcen in beiden Unterverzeichnissen;
- `final-preservation-audit.json`, Auditor-Regressionen und `review.md`.

`.codex/` enthält lokale Rohbelege und Retail-Dateien und gehört nicht in ein
öffentliches Repository. Diese Dokumentation und die Quellpatches sind davon
getrennt. Kein Commit, Push oder Google-Drive-Sync wurde ausgeführt.

## Grenzen und nächster Meilenstein

Der Stundenlauf fand auf Fortress statt. Drei Karten, native fehlgeschlagene
Joins mit Recovery in denselben Botprozessen und Hard-Exit-Recovery sind
separate bereits bestandene kurze Szenarien unter
`.codex/evidence/shadow-20261010/reconnect-fault/`; keine Mehrkartenstunde.
Die historische Vier-Bot-Stunde bleibt dem Build `339058AD…` zugeordnet.

Als nächste Entwicklungsphase folgen Bot-KI und Navigation auf Basis des
vorhandenen `botcore_ai.h`. Externer Serverbrowser/Internetbetrieb, echter
Serverprozess-Neustart, nahtloser Vanilla-Observer-Rejoin, permanenter Supervisor,
12/16 Bots und physische GUI-Abbruchbedienung bleiben getrennte offene Gates.
Die lokale Netzwerkabnahme belegt keinen abgeschlossenen KI- oder 24/7-Betrieb.
