# Alpha-Gaming: Human-KI und CPU-Integration – Abnahmebericht

## 1. Gesamtstatus

Retail-Abnahme unter Wine und öffentliche Inbetriebnahme bestanden. Acht Human-Bots bleiben auf 91.99.75.33:25600 aktiv; Original-Internetbrowser, Beitritt daraus, aktives Originalspiel und unabhängige WAN-UDP-Queries belegt. Keine pauschale Windows-Spieler-PC- oder 24/7-Abnahme.

## 2. Integrierte Änderungen

CSV mit 21 typgerechten Feldern, aktuelle effektive Konfiguration, NullRender bei unveränderter nativer 20-Hz-Aktionspipeline, Human-Policy im BotDriver, sichere Wahrnehmung gespeicherter Ziele, fortgesetzte Bewegung ohne Ziel und vollständiger Munitionsadapter. Kumulative Combat-Fire-Zähler verhindern eine falsche Aktivitätsbewertung durch seltene Stichproben. Die alternativen Vorschläge aus #42/#44 sind getrennt erhalten; keine doppelte Patchnummer wird blind gestapelt.

## 3. DLL und SHA256

Build04: `7fc94a39c3f5d9516f262d9e4d04a5cf38e6eb5ae3482976c32c952a99d30835`.
MSVC cl 19.44.35229.0 / Win32 unter vorhandenem Wine. 15 Übersetzungen und Link erfolgreich. Quellcommit `65219c355c08c6859150a9aa9d596f476da5247c`, Quellbaum `9d7512dc2db395688f7ec0ec116b998d2f4cd764`. Spätere Commits ändern Harness und Dokumentation, nicht die gebauten GameMP-Quellen. Geschützte ursprüngliche DLL `61dc27e0e7b80badcf9ae705c30fca88edd3935737715dffff59e90c26f1fef9` bleibt unverändert.

## 4. GitHub

Konsolidierung in [PR #45](https://github.com/Escoba2024/SeriousSam-TSE-Bot-Servermods-/pull/45). #43 bereits in main. #41 wurde unabhängig und hashgepinnt ausgeführt; dessen älterer Prozess-Cleanup wird nicht ungeprüft als Produktionswerkzeug übernommen. #42/#44 bleiben als ursprüngliche Vorschläge nachvollziehbar. Abschließender Quell-/Nachweisstand wird über #45 integriert; tatsächlicher Merge-Commit und Zeitpunkt sind im verlinkten GitHub-PR maßgeblich dokumentiert. Keine entfernten CI-Checks konfiguriert; qualifizierte lokale Tests und reale Hetzner-Läufe sind separat belegt.

## 5. KI-Eigenschaften

Fünf Skillstufen und sechs Persönlichkeiten in der echten Human-Policy. Acht verschiedene Rosterprofile im Lauf bestätigt. Wahrnehmung, Reaktionszeit, Zielgedächtnis und Waffenentscheidung funktionieren; native Waffenanforderung und tatsächliche Waffe konvergierten für IDs 1,2,3,5,7,8,9,12 mit echten Fire-Aktionen. Original-GUI belegte Botmodell, Bewegung, Schaden, Kill/Score und Respawn. Skill-/Persona-Spezifik wird durch 555 deterministische Checks gestützt; einzelne Scorelisten sind keine kontrollierte statistische Rangfolgenstudie.

## 6. CPU vorher/nachher

Alle Prozesswerte in Prozent eines CPU-Kerns, Host mit zwei vCPU. Vier Bots, Yodeller, Fragmatch, 20 Hz, 180 s Warm-up und 600 s Messung. Aktuelle Legacy-Policy: 22,658%; aktuelle Human-Policy: 21,305%; Server 10,785% bzw. 10,255%. Je nur ein Fenster: keine kausale CPU-Ersparnis durch Human-KI behauptet.

Separater älterer NullRender-A/B-Kandidat: drei Paare à 600 s, Clientmittel 116,013% → 24,667% (−78,74%), gesamte Test-cgroup −66,85%. Dieser DLL-Hash unterscheidet sich von Build04 und dem geschützten 61DC-Referenzartefakt. Unveränderte 61DC-Referenz: 103,593% Client /9,768% Server. Alle vier bewegt, 20 Hz, Scoreänderung, keine Sync-Fehler/Throttling. A/B/C je ein Fenster: 103,593% /22,658% /21,305%; beobachtete Gesamtreduktion C gegen A 79,43%. Keine erfundenen Combat-Zähler für die alte DLL.

Acht-Bot-Stunde einschließlich softwaregerendertem Originalclient: Botprozesse 20,548% +20,505%, Server 14,686%, Originalclient 88,162%; Host 83,193%, Steal und neues Throttling null. Der Originalrenderer ist eigener Testaufwand und kein Bestandteil der dauerhaften Botflotte.

## 7. RAM je Bot

Stundenlauf: BotA 189496 KiB, BotB 188440 KiB; zusammen etwa 369,1 MiB beziehungsweise 46,1 MiB/Bot als geteiltes Prozess-RSS. Kein inkrementell gemessener Pro-Bot-Speicher: Ressourcen werden pro Viererprozess geteilt. Server etwa 50,4 MiB; Originalclient etwa 208,1 MiB separat.

## 8. Gemessene maximale Botanzahl

Acht aktive Bots qualifiziert. Betriebliche Empfehlung derzeit acht; keine höhere Anzahl als gemessen ausgeben. 16 Bots wären mindestens vier Botprozesse und benötigen wegen des 16-Spielerlimits sowie Platz für Menschen mehrere Server. 32/64 sind reine Planungsfälle, keine Kapazitätsfreigabe. Keine Infrastruktur bestellt.

## 9. Multiplayer

Originale Retail-EXE/Engine/Entities/Vanilla-GameMP per Hash gepinnt. Ein Bot plus Originalclient 300 s; vier Human- und vier Legacy-Bots je 600 s. Native Aktionen, Scoreänderungen und Originalbeitritt belegt. Kein hochgesetzter oder deaktivierter ursprünglicher Sync-Kickgrenzwert 10.

## 10. Stabilität

3600,000 s mit acht Human-Bots und einem Originalclient; alle acht in allen zwölf Fünfminutenintervallen bewegt und echte Combat-Fire-Aktionen. Median 20 Hz, keine Render-Draws bei Bots, keine Telemetrie-Stalls, drei erfolgreiche CRC-Checks, null SYNCBAD/Disconnects, reguläres eigenes Cleanup und acht erfolgreiche Unmounts. Rohbelege bleiben privat auf Hetzner; bereinigte Werte in `2026-10-21-integrated-runtime-results.json`.

## 11. Produktivstatus

Aktiv: acht Bots auf 91.99.75.33:25600, Query 25601, private persistente Overlays ohne Überschreiben der bisherigen Installation. Zusätzlicher öffentlicher Smoke 600,000 s bestanden: alle acht bewegen sich/kämpfen, Median 20 Hz, keine Render-Draws/Stalls/Sync-Fehler/Throttling. Server 13,750%, BotA 23,820%, BotB 22,835% eines Kerns; gesamte Test-cgroup 69,031%, gesamter Zwei-vCPU-Host 35,333%, Steal 0. RSS: Server 51368 KiB, BotA 188436 KiB, BotB 188820 KiB.

Originaler In-Game-Internetbrowser zeigte Alpha-Gaming/Yodeller/8 von 16/Version 1.07, tatsächliche externe TCP-Masterantwort und anschließender Beitritt direkt aus der Liste bestätigt. Originalclient war normaler Spieler: neun Serverteilnehmer, Botmodell/Killmeldungen, Gesundheit 60→0→100, Tod und normaler Respawn sowie W/S/D und normale Feuereingabe. Anschließend nur eigener Observer per WM_CLOSE beendet, beide Observer-Mounts entfernt und öffentliche Acht-Bot-Population erneut bestätigt. Serverlog nach dieser Kontrolle: drei CRC-OK, 6430 SYNCOK, 0 SYNCBAD; keine fehlerbedingten Disconnects.

Unabhängige WAN-Erreichbarkeit: vier unterschiedliche externe IPv4-Rechner sendeten echte Statusqueries an eth0/25601 und erhielten vier vollständige Antworten mit Version 1.07, allen acht Bots plus Originalclient, korrekt neun Spielern und final-Marker (881/885/881/886 Bytes). Die unbekannten Peeradressen und Rohpakete werden nicht veröffentlicht. Dies ist zusätzlicher WAN-UDP-Nachweis; der Spielclient selbst befand sich auf Hetzner. Vorab: öffentliche Ports frei, reale Overlay-Vorbereitung bestanden, alle sechs Mounts entfernt; 415 Dateien mit DLL/Konfiguration/Profilen/Logs/Launchern gesichert und nach Extraktion bytegenau geprüft. Unveränderte große Spieldateien bleiben im erhaltenen Lower-Verzeichnis.

## 12. Einschränkungen

Keine unabhängige neue Windows-/GPU-Spieler-PC-Probe, keine 24/7-Abnahme, keine Mehrkartenfreigabe für diese DLL, keine globale Item-/Navmesh-Navigation. StrafeScale bleibt 0. Automatischer Neustart nach Host-Reboot und dynamische Botpopulation sind nicht als implementiert behauptet. Wine benötigt beim Start weiterhin Xvfb/GL, obwohl NullRender laufende Renderarbeit ausspart. Netzwerk und Physik bleiben die Originalengine.

## Abschließende Pflichtkriterien

| Pflichtkriterium | Status | Konkreter Nachweis |
|---|---|---|
| PR-Konflikte beseitigt | ERLEDIGT | Separater integrierter Kandidat; Alternativen erhalten; main enthält #43 |
| CSV-Telemetriefehler behoben | ERLEDIGT | Echter printf-/Parser-Roundtrip, 21 typgerechte Felder |
| CPU-Messungen qualifiziert | ERLEDIGT | Drei ältere Render-A/B-Paare plus getrennte aktuelle A/B/C-Fenster |
| CPU-Optimierungen integriert | ERLEDIGT | NullRender tatsächlich aktiv, Draws=0, 20 Hz native Actions |
| Fünf KI-Fähigkeitsstufen | ERLEDIGT | 555 Checks und native Profilzuordnung |
| Sechs Persönlichkeiten | ERLEDIGT | Policy-Spezifikation, Checks, vollständiges natives Roster |
| KI im BotDriver aktiv | ERLEDIGT | Human-Tick-/Waffen-/Aktionstelemetrie im Retail-Lauf |
| GameMP mit MSVC gebaut | ERLEDIGT | 15 Quellen und Link; gepinnte Build04-DLL |
| GameMP unter Wine funktionsfähig | ERLEDIGT | Gestufte reale Retail-Läufe |
| Acht Bots verbunden | ERLEDIGT | Vollständige Queries/CRC/acht native Slots |
| Acht Bots bewegen sich/kämpfen | ERLEDIGT | Alle acht in jedem von zwölf Fünfminutenabschnitten |
| CPU/RAM dokumentiert | ERLEDIGT | Mess-JSON und getrennte Kapazitätshochrechnung |
| Originalclient beigetreten | ERLEDIGT | 300 s- und 3600 s-Originalgegenstelle, Gameplay-GUI |
| Multiplayer-Sync geprüft | ERLEDIGT | Original CRC und erfolgreiche SYNCOK, null SYNCBAD/Disconnects |
| 60-Minuten-Stabilität | ERLEDIGT | 3600,000 s unter Wine; keine Windows-/24/7-Ausdehnung |
| Öffentlicher Server erreichbar | ERLEDIGT | Vier echte unabhängige eth0-WAN-Queries und vier vollständige Antworten |
| In Serverliste sichtbar | ERLEDIGT | Frische externe Master-TCP-Liste, Originalbrowser Alpha-Gaming 8/16 und Beitritt daraus |
| Rollback sichergestellt | ERLEDIGT | Alte DLL unverändert; 415 Dateien bytegenau restauriert; normale eigene Abbruch-/Unmount-Probe |
| GitHub aktualisiert | ERLEDIGT | Konsolidierter Source-/Nachweisstand in #45; tatsächlicher Mergestatus im PR |
| Dokumentation aktualisiert | ERLEDIGT | Dieser 12-Punkte-Bericht, Mess-JSON, Betrieb, Kapazität, Entscheidungen und Plan; Drive als abschließend verifizierter Spiegel |

Alle 20 Kriterien sind durch die angegebenen Nachweise im Hetzner-/Retail-Wine-Umfang erfüllt. Rohlogs und Screenshots bleiben privat. Der separate HTTP-JSON-Endpunkt meldete weiterhin leere Ergebnisse/not_in_db trotz erfolgreicher echter Master-TCP-Liste, Originalbrowser und unabhängiger WAN-Antworten. Daraus wird kein HTTP-API-PASS behauptet; maßgeblich sind die direkten funktionierenden Spiel-/Netzwerkbelege.
