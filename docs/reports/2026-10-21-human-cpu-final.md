# Alpha-Gaming: Human-KI und CPU-Integration – Abnahmebericht

## 1. Gesamtstatus

Retail-Abnahme unter Wine bestanden; öffentliche Inbetriebnahme und abschließende Integration noch in Arbeit. Keine pauschale Windows-, WAN-Spieler-PC- oder 24/7-Abnahme.

## 2. Integrierte Änderungen

CSV mit 21 typgerechten Feldern, aktuelle effektive Konfiguration, NullRender bei unveränderter nativer 20-Hz-Aktionspipeline, Human-Policy im BotDriver, sichere Wahrnehmung gespeicherter Ziele, fortgesetzte Bewegung ohne Ziel und vollständiger Munitionsadapter. Kumulative Combat-Fire-Zähler verhindern eine falsche Aktivitätsbewertung durch seltene Stichproben. Die alternativen Vorschläge aus #42/#44 sind getrennt erhalten; keine doppelte Patchnummer wird blind gestapelt.

## 3. DLL und SHA256

Build04: `7fc94a39c3f5d9516f262d9e4d04a5cf38e6eb5ae3482976c32c952a99d30835`.
MSVC cl 19.44.35229.0 / Win32 unter vorhandenem Wine. 15 Übersetzungen und Link erfolgreich. Quellcommit `65219c355c08c6859150a9aa9d596f476da5247c`, Quellbaum `9d7512dc2db395688f7ec0ec116b998d2f4cd764`. Spätere Commits ändern Harness und Dokumentation, nicht die gebauten GameMP-Quellen. Geschützte ursprüngliche DLL `61dc27e0e7b80badcf9ae705c30fca88edd3935737715dffff59e90c26f1fef9` bleibt unverändert.

## 4. GitHub

Konsolidierung in [PR #45](https://github.com/Escoba2024/SeriousSam-TSE-Bot-Servermods-/pull/45). #43 bereits in main. #41 wurde unabhängig und hashgepinnt ausgeführt; dessen älterer Prozess-Cleanup wird nicht ungeprüft als Produktionswerkzeug übernommen. #42/#44 bleiben als ursprüngliche Vorschläge nachvollziehbar. Merge noch ausstehend.

## 5. KI-Eigenschaften

Fünf Skillstufen und sechs Persönlichkeiten in der echten Human-Policy. Acht verschiedene Rosterprofile im Lauf bestätigt. Wahrnehmung, Reaktionszeit, Zielgedächtnis und Waffenentscheidung funktionieren; native Waffenanforderung und tatsächliche Waffe konvergierten für IDs 1,2,3,5,7,8,9,12 mit echten Fire-Aktionen. Original-GUI belegte Botmodell, Bewegung, Schaden, Kill/Score und Respawn. Skill-/Persona-Spezifik wird durch 555 deterministische Checks gestützt; einzelne Scorelisten sind keine kontrollierte statistische Rangfolgenstudie.

## 6. CPU vorher/nachher

Alle Prozesswerte in Prozent eines CPU-Kerns, Host mit zwei vCPU. Vier Bots, Yodeller, Fragmatch, 20Hz, 180s Warm-up und 600s Messung. Aktuelle Legacy-Policy: 22,658%; aktuelle Human-Policy: 21,305%; Server 10,785% bzw. 10,255%. Je nur ein Fenster: keine kausale CPU-Ersparnis durch Human-KI behauptet.

Separater älterer NullRender-A/B-Kandidat: drei Paare à 600s, Clientmittel 116,013% → 24,667% (−78,74%), gesamte Test-cgroup −66,85%. Dieser DLL-Hash unterscheidet sich von Build04 und dem geschützten 61DC-Referenzartefakt. Unveränderte 61DC-Referenz: 103,593% Client /9,768% Server. Alle vier bewegt, 20Hz, Scoreänderung, keine Sync-Fehler/Throttling. A/B/C je ein Fenster: 103,593% /22,658% /21,305%; beobachtete Gesamtreduktion C gegen A 79,43%. Keine erfundenen Combat-Zähler für die alte DLL.

Acht-Bot-Stunde einschließlich softwaregerendertem Originalclient: Botprozesse 20,548% +20,505%, Server 14,686%, Originalclient 88,162%; Host 83,193%, Steal und neues Throttling null. Der Originalrenderer ist eigener Testaufwand und kein Bestandteil der dauerhaften Botflotte.

## 7. RAM je Bot

Stundenlauf: BotA 189496 KiB, BotB 188440 KiB; zusammen etwa 369,1 MiB beziehungsweise 46,1 MiB/Bot als geteiltes Prozess-RSS. Kein inkrementell gemessener Pro-Bot-Speicher: Ressourcen werden pro Viererprozess geteilt. Server etwa 50,4 MiB; Originalclient etwa 208,1 MiB separat.

## 8. Gemessene maximale Botanzahl

Acht aktive Bots qualifiziert. Betriebliche Empfehlung derzeit acht; keine höhere Anzahl als gemessen ausgeben. 16 Bots wären mindestens vier Botprozesse und benötigen wegen des 16-Spielerlimits sowie Platz für Menschen mehrere Server. 32/64 sind reine Planungsfälle, keine Kapazitätsfreigabe. Keine Infrastruktur bestellt.

## 9. Multiplayer

Originale Retail-EXE/Engine/Entities/Vanilla-GameMP per Hash gepinnt. Ein Bot plus Originalclient 300s; vier Human- und vier Legacy-Bots je 600s. Native Aktionen, Scoreänderungen und Originalbeitritt belegt. Kein hochgesetzter oder deaktivierter ursprünglicher Sync-Kickgrenzwert 10.

## 10. Stabilität

3600,000s mit acht Human-Bots und einem Originalclient; alle acht in allen zwölf Fünfminutenintervallen bewegt und echte Combat-Fire-Aktionen. Median 20Hz, keine Render-Draws bei Bots, keine Telemetrie-Stalls, drei erfolgreiche CRC-Checks, null SYNCBAD/Disconnects, reguläres eigenes Cleanup und acht erfolgreiche Unmounts. Rohbelege bleiben privat auf Hetzner; bereinigte Werte in `2026-10-21-integrated-runtime-results.json`.

## 11. Produktivstatus

Noch in Arbeit. Geplant ist ein eigener persistenter Overlay-Lauf mit acht Bots auf 91.99.75.33:25600, ohne Überschreiben der bisherigen Installation. Öffentliche Query, frische Masterlistung, Originalbeitritt und kontrollierter Produktions-Smoke werden separat nachgewiesen. Vorab: öffentliche Ports frei, reale Overlay-Vorbereitung bestanden, alle sechs Mounts entfernt; 415 Dateien mit DLL/Konfiguration/Profilen/Logs/Launchern gesichert und nach Extraktion bytegenau geprüft. Unveränderte große Spieldateien bleiben im erhaltenen Lower-Verzeichnis.

## 12. Einschränkungen

Keine unabhängige neue Windows-/GPU-Spieler-PC-Probe, keine 24/7-Abnahme, keine Mehrkartenfreigabe für diese DLL, keine globale Item-/Navmesh-Navigation. StrafeScale bleibt 0. Automatischer Neustart nach Host-Reboot und dynamische Botpopulation sind nicht als implementiert behauptet. Wine benötigt beim Start weiterhin Xvfb/GL, obwohl NullRender laufende Renderarbeit ausspart. Netzwerk und Physik bleiben die Originalengine.

## Abschließende Pflichtkriterien

Wird nach dem öffentlichen Smoke mit konkreten Nachweisen abgeschlossen. Öffentliche Erreichbarkeit, Serverlistung, Rückrollprobe, finale GitHub- und Dokumentationsaktualisierung bleiben bis dahin offen.
