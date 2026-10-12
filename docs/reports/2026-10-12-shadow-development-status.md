# Shadow-Entwicklung: nachweisbarer Stand vom 12.10.2026

Die lokale Abnahme umfasst Retail-PoC, vier Bots in einem Prozess, acht Bots in zwei Prozessen sowie autonomen Deathmatch-Kampf mit reaktiver Hinderniserholung. Der aktuelle qualifizierte KI-Kandidat ist die GameMP-DLL mit SHA256 `61DC27E0E7B80BADCF9AE705C30FCA88EDD3935737715DFFFF59E90C26F1FEF9`. Dieser Bericht konsolidiert die Entwicklung vom 08.–12.10.2026 gegenüber dem zuvor veröffentlichten `main`-Commit `c636a5306c9c0e18e847c403b67cc1b0930de485`.

Die Veröffentlichung enthält Quellen, Konfigurationen, Prüfwerkzeuge und bereinigte Nachweise. Retail-Binaries, SDK-Importbibliotheken, Spieldaten, private Profile/GUIDs, Rohlogs und lokale Backups bleiben außerhalb von Git. Die private vollständige Sicherung des Shadow-Arbeitsverzeichnisses und ein geprüftes Git-Bundle wurden vor der Integration angelegt. Der Git-Commit dieser Datei ist über die Repository-Historie feststellbar; die abschließende Synchronisierung quittiert zusätzlich den Remote-Merge-Commit und die vier bestehenden Drive-Dokumente.

## Bestätigte Meilensteine

| Meilenstein | Nachweis und Geltungsbereich |
|---|---|
| Phase 1: Retail-PoC | BESTANDEN. Echte TSE-1.07-Runtime, Build/Load/CRC/Join, Vanilla-Observer, Bewegung/Rotation/Fire, Schaden/Frag, Death/Respawn, kontrollierte Reconnects/Mapwechsel und regulärer Shutdown. Separate aktive 10-/30-/60-Minuten-Läufe plus unabhängige 60-Minuten-Wiederholung. Historische Details: `CODEX_WINDOWS_POC_REPORT.md`. |
| Phase 2: vier lokale Bots | BESTANDEN. Zwei/drei/vier native lokale Spieler, unabhängige Actions und Identitäten. Auf Shadow am 08.10.2026 eine eigene Vier-Bot-Stunde: 3630.4427 s native Laufzeit, 60 vollständige aktive Minuten je Bot, 240 Fenster mit je 1200 Snapshots, 360 unabhängige Vier-Spieler-Abfragen. DLL `339058AD09DA1A9DBCA1D92145259D6871304987A0C50C39D0C71E3B4E5A81FE`. |
| Phase 3: acht Bots / 2 × 4 | LOKAL BESTANDEN. Recovery-DLL `24053920C63E02F9883056331B246BEF2D08D645FFCCE2C74ED7EDC9B35B9ACF`: 3700.637 s vollständige Acht-Spieler-Abfragen, 480 aktive Bot-Minuten. Separate Zwei-Bot-Stunde mit 3674.066 s Abfragen und 120 aktiven Minuten. Drei Karten, echte fehlgeschlagene Joins und Hard-Exit-Recovery sind in getrennten kurzen Szenarien geprüft. Details: `poc/PHASE-3-ABNAHME.md`. |
| Autonomer Kampf | BESTANDEN im lokalen DM-Pfad. Eigene modulare Ziel-/Sicht-/Aim-/Waffen-/Action-Logik; keine Änderung an synchronisierten Entities. Früher Zwei-Bot-Smoke mit sechs Observer-Kills und fünf Respawnzyklen; aktueller 61DC-Kandidat zusätzlich mit eigener Acht-Bot-KI-Stunde geprüft. |
| Reaktive Hinderniserholung | BESTANDEN. Drei kurze native Brush-Kollisionsstrahlen, begrenztes Drehen und Advance, Stuck-Erkennung, Reset bei Tod/Hold/Teleport und endliches Versuchslimit. In der aktuellen KI-Stunde besitzt jeder Bot regulär abgeschlossene Brush-Advances von mindestens 2 m. |
| Sparsames Betriebsprofil | BESTANDEN als separater Smoke mit exakt `LocalBotRelease.ini`, 176.503899 s unabhängigen Serverabfragen und CRC 6. Keine zweite KI-Stunde; kein vollständiger Wandfortschrittsnachweis pro Bot aus diesem Smoke. |
| Population Manager | TEILWEISE. C++-/PowerShell-Regeln für Zielpopulation, Human-Slot-Reserve, Start/Stop-Entscheidung und deterministische Verzögerung sind isoliert getestet. Fleet-Start/Stop, Profilprüfung und Namensklassifikation existieren. Ein dauerhaft laufender, race-freier Population-Supervisor ist noch nicht umgesetzt/abgenommen. |

## Aktueller KI-Stundenlauf: exakt 61DC

Ein unveränderter TSE-1.07-Dedicated-Server, zwei getrennte Vier-Spieler-BotClients und ein unveränderter Vanilla-Observer laufen auf Fortress im Deathmatch. Die unabhängigen Serverabfragen umfassen **3697.291299 s** und enthalten durchgehend alle acht erwarteten Namen. **733** Steady-Abfragen und **6** akzeptierte CRC-Prüfungen sind belegt. Die im Runner zusätzlich protokollierten 4391.806233 s enthalten nachgelagerte Auswertung und werden nicht als reine Spielzeit verwendet.

Der unabhängige KI-Auditor bestätigt **60 vollständige 20-Hz-Minuten je Bot**, **480** Fenster mit jeweils **1200** zusammengehörigen Navigation-/Combat-/Driver-/replizierten Snapshot-Datensätzen. Das sind 72.000 vollständige Entscheidungen je Bot bzw. 576.000 insgesamt. Er verwendet nur den letzten nativen Player-Source-Abschnitt des jeweiligen Prozesses; Aktivität vor dem Prozessersatz wird nicht hinzuaddiert. Innere Lücken und Duplikate werden abgelehnt; höchstens zwei unvollständige Shutdown-Ticks am Schluss sind gesondert ausgewiesen.

| Lokaler Bot | Reguläre Brush-Advances ≥ 2 m | Lebende native Fire-Eingaben |
|---|---:|---:|
| A1 | 7 | 1927 |
| A2 | 12 | 1884 |
| A3 | 3 | 1766 |
| A4 | 8 | 1670 |
| B1 | 11 | 1943 |
| B2 | 12 | 1637 |
| B3 | 4 | 1817 |
| B4 | 12 | 1811 |

Insgesamt **69** reguläre Wand-Ausweichfortschritte. Replan verlängert das 240-Tick-Budget nicht; Vorschub ist begrenzt, Advance dauert maximal 40 Ticks. Aktive Erholung unterdrückt lebendes Feuern; normale native Respawn-Eingaben bleiben möglich. **1124 Observer-Kampfkills** sind im gesamten gespeicherten Lauf einschließlich Lifecycle/Vorlauf/Teardown bezeugt. Diese Zahl ist keiner ausschließlichen Stundenmessung zugeordnet.

Der reale Lifecycle zeigt `8 → 9 → 8 → 9 → 8 → 4 → 8`: menschlicher Join/Austritt/Rejoin/Austritt und kontrollierter Ersatz eines BotClients. Eigene native PLC4-Profile und passende GUID-Sidecars verhindern Identitätskollisionen. Nach jeder Abnahme wurden die Testkopien zurückgenommen; es läuft kein dauerhaft installierter Bot-Dienst.

| Prozess | Samples | Messspanne s | CPU % eines logischen Kerns | Peak Private MiB | Peak Working Set MiB |
|---|---:|---:|---:|---:|---:|
| BotClient A | 733 | 3697.303 | 46.371 | 82.602 | 100.156 |
| BotClient B | 733 | 3697.283 | 45.916 | 90.672 | 108.387 |
| Dedicated Server | 733 | 3697.287 | 2.474 | 21.438 | 32.914 |

Die CPU-Werte sind nicht bereits durch acht logische Host-CPUs geteilt. Diese Ressourcenmessung ist ein lokaler Stundenbeleg, keine 24/7-Abnahme und kein allgemeiner Leckfreiheitsbeweis.

## Quellstand, Build und Stabilisierung

`poc/release/gamemp/` enthält die **13 vollständigen erfassten GameMP-Anpassungen** des qualifizierten Kandidaten, einschließlich `LoadingHook.cpp`. Der vollständige Vergleich umfasst **32** Game-Quell-/Header-/Resource-/Projektdateien. Das bereinigte `2026-10-12-source-verification.json` hält deren Hashes fest. Git erhält die Rohbytes der erfassten Dateien über `.gitattributes`, damit ein Checkout diesen Vergleich nachvollziehen kann.

Buildvoraussetzungen: SE1-ModSDK `aa7869c2c2c4db0562281814d0ac3784e6b9d6f0`, sauberes Includes-Unterprojekt `94ff8cd0e63941f8601294350b616472f772ed51`, unveränderte Entities-Header, VS2022 Build Tools/v143/x86, Windows SDK 10.0.19041.0. Reproduktion: `poc/scripts/Build-LocalBotRelease.ps1`; Anleitung: `poc/LOCAL-RELEASE.md`.

Ein bereits vollständig reproduzierter Quellbuild hat DLL-SHA256 `A66476FE04926BE5CEAD1C87A55F4B550A37243CC5BF86DE228F97888C5CC19D`. Er ist trotz bytegleicher Eingabequellen **kein byteidentischer und kein separat nativ qualifizierter Ersatz**. Auch PE-Sektionen `.text`, `.rdata` und `.reloc` unterscheiden sich. Die frühere bloße Metadaten-Erklärung wurde ausdrücklich zurückgenommen. Neu gebaute DLLs benötigen ihre eigene native Abnahme.

Die Entwicklung behält die tatsächlichen früheren Sync-Fehler bei: der World-Lock allein genügte im damaligen Acht-Bot-Stundenversuch nicht. Patch `0006` schützt komplette Timer-Entity-/Ray-/Snapshot-/Action-Lebenszeiten durch die native World-/Network-Sperre; `0007` schützt den gesamten Renderdurchlauf einschließlich Thumbnail/Prescan durch die Timer-Hooks-Sperre. Reihenfolge: Hooks 1000 vor Network 2000. Native Analyse belegte gemeinsamen Ray-Sektorstapel und konkurrierende Sektorflag-Schreibzugriffe. Daraus folgt keine rückwirkende Rekonstruktion jedes früheren CRC-Fehlers.

Der sparsame Release-Startup schließt eigene lokale Mitspieler als Ziele aus, setzt LogEvery=20 und Diagnostics=0. QA-Startup und Production-Startup besitzen getrennte Prüfer. Reale Vorbereitung/Rücknahme umfasst 24 Dateizustände; der tatsächliche Retail-Versionsmarker ist `Data/Var/Sam_Version.var` mit `v1.07`. Query-Readiness verlangt vollständige eindeutige Namenslisten und konsistente Spielerzahlen, nicht nur einen Slotcount.

## Offener Bodenprüfungsversuch vom 11.–12.10.

**NICHT ABGENOMMEN.** Die optionale Ground-Lookahead-Arbeit bleibt außerhalb des qualifizierten Quellreleases im lokalen, gesicherten `poc/ground/`. Die erste 600-s-Aufzeichnung wurde durch Rechner-/Sitzungsunterbrechung beendet. Zwei spätere Vollvarianten scheiterten nach BotClient-Ersatz an nativen Sync-Fehlern und Verlust von vier Slots. Der zuletzt geprüfte Versuch hat DLL-SHA256 `53982F05A1EEE73E52AF48C77301C67399D9EA38F5F5D23B8C549ADE2D0372C6` und besitzt keinen erfolgreichen Ground-Abnahme-Audit.

Ground-deaktivierte und reine Ray-Diagnostik-Läufe bestanden jeweils kurze Lifecycle-Prüfungen. Das grenzt Hypothesen ein, beweist aber keine alleinige Ursache. Isolierte Ground-Unit-Tests und Code-Review ersetzen diese fehlende native Abnahme nicht. Es wird keine sichere Abgrundvermeidung behauptet und kein experimenteller Ground-Build als Release ausgeliefert. Weiterentwicklung ist während dieses Synchronisierungsauftrags angehalten.

## Grenzen und nächste Prioritäten

1. Öffentliche Serverbrowser-/333networks-Sichtbarkeit und Internet-/NAT-/Firewall-Betrieb separat prüfen. Lokale echte UDP-Status-/Player-Abfragen sind bestanden; öffentliche Listung folgt daraus nicht.
2. Population-Regeln zu einem robusten Supervisor mit verlässlicher eigener Bot-Erkennung, reservierten Human-Slots und race-freier Steuerung integrieren. Namenspräfix allein ist keine fälschungssichere Human/Bot-Erkennung.
3. Navigation nach einem eigenen Entwicklungsauftrag fortsetzen: globale Wege, Item-/Health-Routen, Boden-/Abgrundsicherheit. Den Ground-Sync-Fehler zuerst nachvollziehen; die aktuelle lokale Hinderniserholung bleibt der qualifizierte Ausgangspunkt.
4. Eigene Gates für weitere Waffenfamilien, Coop und eine aktuelle KI-Mehrkartenstunde. Alte Recovery-Mehrkartenläufe werden nicht auf eine neue KI-DLL übertragen.
5. 12/16 Bots, mehr als zwei Prozesse, mehrere Server, automatischen Dedicated-Neustart und dauerhafte Recovery getrennt abnehmen.
6. 2-/6-/24-Stunden-Soaks, Logrotation, Speicher-/Handle-/Ressourcenentwicklung und 24/7-Betrieb prüfen. Eine lokale Stunde ist keine Produktionsfreigabe.

## Handoff ohne Chatgedächtnis

Zuerst diesen Bericht, `README.md`, `poc/LOCAL-RELEASE.md` und `poc/PHASE-3-ABNAHME.md` lesen. `poc/release/gamemp/` ist der aktuelle qualifizierte Quellstand; `poc/patch/gamemp/` und Patches `0001` bis `0007` dokumentieren die älteren Entwicklungsstufen. `poc/botcore/` enthält die enginefreien Regeln und Tests; `poc/scripts/` die Fleet-, Installations-, Restore-, Build- und Audit-Werkzeuge. Die vorhandenen Sicherungshüllen und älteren unabhängigen Auditoren sind unter `tools/` öffentlich erfasst. Die Testmatrix und Befehle stehen in `docs/reports/2026-10-12-publication-validation.md`.

Die lokalen Primärbelege liegen unter `.codex/evidence/shadow-20261008/`, `shadow-20261010/completion/`, `shadow-20261010/local-release/` und `shadow-20261011/ground-lookahead/`. Sie bleiben privat; veröffentlichte bereinigte Zusammenfassungen behaupten keine öffentliche Rohlog-Abnahme. Herkunft und Prüfscope sind im Acceptance-Summary dokumentiert. Fehlversuche und unterbrochene Stunden wurden erhalten und niemals addiert. Lizenzen/Attribution: `poc/release/LICENSE` und `THIRD-PARTY-NOTICES.md`.
