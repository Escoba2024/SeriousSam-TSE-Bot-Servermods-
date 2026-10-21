# Runtime-Abnahme – Integrationsledger, 21.10.2026

Dieser Bericht unterscheidet Build, Timeraktivität, aktives Spiel und öffentlichen Betrieb. Ein PASS_LIMITED des Harness ist keine vollständige Abnahme.

## Kandidaten

| Build | SHA256 GameMP.dll | Quellen | Ergebnis |
|---|---|---|---|
| 01 | 84e7ce725b0c00806c2c538ac96bb9b69a78cb34021efaae25b99743e64fb771 | Git 9dcb725 | 15 MSVC-Quellen gebaut; anschließend Fehler im Engine-Anschluss entdeckt |
| 02 | 9a0a71a1d3dbf4d873a3a083287ea7d5e40cad476cb556e2d84cfc7ba492bea3 | Baum bbead369fe022798afc69d3ddca4ec6c24d93895 | Nullziel-/Gedächtnisdistanz korrigiert; echte Joins/CRC; Harness ohne Querylistener, daher Lauf ungültig |
| 03 | d4f71d7be5efafa872f8e8a9d19c69921f6b90eaf08eeffc036662a226781511 | Baum ff32d22d732e33a0a3978c18bb4f760c4d6f268f | Effektive Telemetrie korrigiert; 120s lokaler Retail-Lauf, Gameplay noch unvollständig |

Compiler: MSVC cl 19.44.35229.0, Linker 14.44.35229.0, x86 PE32, Release_TSE107 entsprechende direkte cl/link-Befehle. SDK aa7869c2c2c4db0562281814d0ac3784e6b9d6f0, Includes 94ff8cd0e63941f8601294350b616472f772ed51.

## Korrigierte Defekte

- CSV: 21 Werte mit 21 typgerechten Formatfeldern. Test erzeugt eine echte printf-Zeile und prüft Parser-Roundtrip.
- Gegner verlässt das Spiel: kein Nullzeigerzugriff; Feuer wird unterdrückt.
- Verdeckter Gegner: Engine-Anschluss verwendet die eingefrorene Gedächtnisdistanz statt aktueller unsichtbarer Position.
- Spätes CLI-Konfigurationsskript: effektive CSV-Konfiguration wird bei Änderung nachgetragen.
- Isolierter Querylistener: lokaler Master und aktivierter Heartbeat; keine Veröffentlichung des Testservers.

## Build 03, ein Bot und Original-Retail-Gegenstelle

Abgeschlossen 01:09:42 UTC. 120,001 Sekunden Messung nach separatem Warm-up. Zwei Spieler verbunden; originale Server-/Engine-/Entities-/Client-Binaries gepinnt. Bot erhält ausschließlich die Kandidaten-GameMP.dll in einer privaten Overlay-Installation.

- BotDriver: Median 20 Hz, Minimum 20 Hz, 2643 Aktionen, 20 Aktionen/s pro Bot.
- NullRender tatsächlich aktiv: 2643 übersprungene Renderaufrufe, 0 Renderdurchläufe.
- Effektive Konfiguration: bot_enabled=1, nullrender=1, nullrender_fps=20.
- Kein neues cgroup-Throttling, Host-Steal 0%, Hostauslastung 60,25%.
- Bot 7,15% eines CPU-Kerns, Originalclient 96,62%, Server 7,94%.
- RSS: Bot 187128 KiB, Originalclient 213316 KiB, Server 50728 KiB.
- Alle sechs privaten Overlay-Mounts nach Test erfolgreich ausgehängt; Originaldateien erhalten.
- **Nicht bestanden als Gameplay-Gate:** Botposition unverändert, kein protokolliertes Feuer, keine Scoreänderung. Die geerbte Human-Policy scannt ohne wahrgenommenes Ziel im Stand.

Die niedrige CPU-Zahl dieses Laufes wird ausdrücklich nicht als Einsparung aktiver kämpfender Human-Bots verwendet. Der Suchpfad muss den vorhandenen Navigationsinput erhalten und anschließend erneut in der Runtime geprüft werden.

## Laufende Qualifikation

Die ältere separate NullRender-A/B-Serie aus #41 wird mit drei Wiederholungen je Variante abgeschlossen. Ihre DLL ist von den integrierten Human-Kandidaten verschieden. Der Runner war ausschließlich zwischen vollständig gespeicherten Fenstern angehalten und wurde am Morgen wieder fortgesetzt; die Pause gehört zu keinem Messfenster.

Tests, neuer MSVC-Build und Runtime-Stufen werden nach Abschluss dieser Serie nacheinander ausgeführt. Vier Human-Bots und vier Legacy-Bots erhalten dieselbe DLL und Bedingungen; acht Human-Bots werden anschließend mindestens 3600 Sekunden gemessen. Keine parallelen Lasttests, keine zusätzlichen KI-Agenten.

## Noch offene Abnahme

Aktives Spiel aller Human-Bots, vergleichbare CPU-Messung der fertigen Version, 60-Minuten-Sync mit acht Bots, sichtbare Retail-Spielkontrolle, öffentliche Aktivierung/Erreichbarkeit und Masterlisteneintrag. Produktionsdateien und Rollback-DLL wurden bisher nicht ersetzt.

Masterserver-Prüfung: Die offizielle 333networks-Dokumentation nennt die JSON-Serverliste unter https://master.333networks.com/json/serioussamse. Daten einer späteren Listenprüfung sind 333networks zuzuordnen; ein lokaler Query ist kein unabhängiger WAN-Nachweis.

## Baseline abgeschlossen / weitere Laufzeitkorrekturen

Alle sechs A/B-Fenster bestanden: vier bewegte Legacy-Bots, 20Hz je Slot, 12000 Ticks je Messfenster, null SYNCBAD/Throttling. Client-CPU im Mittel 116.01% → 24.67% eines Kerns (78.74% weniger), gesamte Test-cgroup 129.88% → 43.05% (66.85% weniger). Diese Messungen gelten ausschließlich für die ältere A/B-DLL. Vollständige aggregierte Werte: 2026-10-21-qualified-cpu-ab.json.

Suchpfad-Regressionsfall und realer vollständiger Munitionsadapter RED→GREEN. Der frühere Adapter ließ Raketen/Granaten/Kanonenkugeln mit leerem Vorrat als nutzbar gelten. Neuer Engine-Adapter filtert alle endlichen Vorräte für Human- und Legacy-Pfad; geschützte Release-Header bleiben unverändert. Das echte integrierte Block-Smoke extrahiert auch diesen Adapter.

Schusspulse der lokalen Legacy-Slots sind zeitversetzt; 1Hz-Statuszeilen können sie systematisch verpassen. Ein kumulativer Zähler erfasst nun ausgegebene Kampf-Feueraktionen nach SetAction, ohne Respawn-Pulse. Die Runtime-Auswertung betrachtet nur Zählerdifferenz/Bewegung innerhalb des Messfensters. Fünf gezielte Anschluss-/Nachweistests bestanden. Neuer Build und Runtime-Nachweis stehen noch aus.

## Build04 / erstes Gameplay-Gate bestanden

MSVC-Build SHA256 7fc94a39c3f5d9516f262d9e4d04a5cf38e6eb5ae3482976c32c952a99d30835, Quellbaum 9d7512dc2db395688f7ec0ec116b998d2f4cd764, lokal ba7d0e6 / identischer veröffentlichter Quellbaum 65219c3. 59 Benchmark-/Adaptertests, 31 Parser-/Query-/Preflighttests, sieben C++-Suiten und realer Integrations-Smoke bestanden.

Ein Bot + originale Retail-Gegenstelle: 300,000s Messfenster, 6000 Tickspanne / 301 Statuszeilen, Position verändert, 92 neue Kampf-Feueraktionen, Scoreänderung. Originalclient sichtbar im gerenderten Retail-Spiel geprüft: normale Bewegung, Kill durch Rookie-Bot, Gesundheit 0, Score 1/0 vs 0/1; normale Respawn-Eingabe stellt 100 Gesundheit wieder her. Dies ist ein echter lokaler Retail-Multiplayer-Lauf unter Wine, kein unabhängiger WAN- oder menschlicher Windows-Test. Private Bildhashes und Beobachtungen stehen im Buildreport; Rohbilder/Logs bleiben auf Hetzner.

Ein-Bot-CPU: Bot 9,980%, Server 8,423%, Originalrenderer 95,420% eines Kerns; Host 61,752% ausgelastet. Noch keine Vergleichsmessung der fertigen Vier-/Acht-Bot-Version.

## Vier-Bot-Human-/Legacy-Gates bestanden; Acht-Bot-Stunde läuft

Dieselbe neue DLL und 600s-Fenster mit 180s Warm-up: Human 21,305% Client-CPU / 10,255% Server, Legacy 22,658% / 10,785% eines Kerns. Beide Varianten: vier bewegte Bots, je 12000 Tickspanne, neue Kampf-Feueraktionen, Scoreänderung, keine protokollierten Sync-Fehler und kein neues Throttling. Ein Fenster je Variante; daraus wird keine kausale Ersparnis durch die Human-Policy abgeleitet. Vollständige Werte: integrated-runtime-results.json.

Acht Human-Bots + Original-Retail-Gegenstelle sind seit 10:05 UTC verbunden; Messfenster begann nach dem Warm-up um 10:09 UTC und ist noch NICHT als Stunden-PASS gewertet. Alle fünf Skillstufen/sechs Personas sind im nativen BotDriver protokolliert und alle acht Slots bewegen sich/feuern. Drei echte Client-CRC-Akzeptanzen, bisher keine SYNCBAD/Disconnects.

Die GameSpy-Regelfelder dürfen nicht naiv als Standard-Booleans interpretiert werden: Im gepinnten SDK schreibt GetGameSpyStatusInfo mehrere Regeln mit TRUE→0. Die Serverkonfiguration der älteren A/B-Serie und des aktuellen Laufs enthält gam_bInfiniteAmmo=1; die aktuelle Rohquery liefert entsprechend infiniteammo=0. Gleiche tatsächliche Spielregeln wurden zusätzlich anhand der persistenten Konfiguration geprüft.

Nach der Stunde folgt für Phase H noch ein separates CPU-Fenster mit der unveränderten früher qualifizierten 61DC-DLL. Der erfolgreiche ältere Renderer-A/B-Kandidat 4f7414... wird dadurch nicht fälschlich mit dem früheren Release gleichgesetzt. Ein Reader für dessen unveränderte Statuslogs muss ohne neue CSV-/Feuerzähler 20Hz/Bewegung belegen; keine erfundenen Schusszahlen für den alten Binärstand.

## Abschließende private Gates / öffentlicher Preflight

Acht-Bot-Stunde PASS_60MIN_WINE nach 3600,000s, alle acht Bots in allen zwölf Fünfminutenintervallen aktiv bewegt und mit echten Combat-Fire-Aktionen, drei CRC-Akzeptanzen, null SYNCBAD/Disconnects/Throttling. Alle acht Mounts entfernt.

Unveränderte 61DC-Referenz über 600s: Client 103,593%, Server 9,768%; alle vier bewegt mit 20Hz und Scoreänderung. Null Throttling/Sync-Fehler, vier Mounts entfernt. Frühere Timestamp-Verzeichniskollision vor jedem Spielstart durch eindeutige mkdtemp-Pfade behoben und RED→GREEN geprüft.

Öffentliche Population akzeptiert menschliche Beitritte, verlangt aber alle acht Botnamen (RED→GREEN). Frisch: 40 root Python-Tests, 59 Benchmark-/Adaptertests, sieben C++-Suiten einschließlich 555 Human-Checks und realer Integrations-Smoke bestanden. Vorbereitungsprobe auf öffentlichen Ports bestanden, sechs Mounts entfernt. 415 alte DLL-/Konfigurations-/Profil-/Log-/Launcher-Dateien gesichert und aus Archiv bytegenau restauriert. Noch kein öffentlicher Lauf-PASS.

Öffentlicher Erststart bewusst vor Abnahme abgebrochen: acht Bots/Query gesund, aber geerbtes net_strMasterServerOverride=127.0.0.1 übersteuerte das öffentliche Ziel. Keine fremden Spieler; eigener SIGINT durchlief normales Cleanup und alle sechs Unmounts. Beide Mastervariablen werden nun explizit gesetzt (RED→GREEN); frische 41 root- und 59 Benchmarktests bestanden. Vollständiger öffentlicher Smoke wird neu gestartet.
