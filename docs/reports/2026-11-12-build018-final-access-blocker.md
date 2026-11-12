# Build018: Verbesserung belegt, Fortsetzung durch Remote-Quote blockiert

Stand: 12.11.2026 23:20:47 MEZ.

## Antwort auf den Versionsvergleich

Build018 ist in den sechs abgeschlossenen kurzen Vergleichen gegen die bisher öffentlich eingesetzte Bot-DLL im direkten Kampf überlegen. Pro Stufe wurden zwei Fenster von jeweils 120 Sekunden mit vertauschter Startverteilung ausgewertet.

| Stufe | Direkte Abschüsse neu gegen alt | Direkte Abschüsse alt gegen neu |
| --- | ---: | ---: |
| MITTEL | 31 | 12 |
| STARK | 31 | 13 |
| DEMON | 47 | 8 |
| Gesamt | 109 | 33 |

Das sind vollständige Zuordnungen tödlicher Fremdschadensereignisse. Die insgesamt 1490 Schadensereignisse bleiben kategorisiert. Query-Fragwerte enthalten zusätzlich Kämpfe innerhalb derselben Kohorte und werden deshalb getrennt gehalten. Die neue Version erreicht in jedem der sechs Fenster mehr direkte Abschüsse gegen die alte Version als umgekehrt.

Diese kurzen Versuche belegen weder eine verlässliche Staffelung STARK über MITTEL noch menschliche Spielstärke oder Dauerstabilität. Die vorübergehende Dev-Clientpause zur RAM-Entlastung bei den STARK-/DEMON-Fenstern und beide vorangegangenen RAM-Fehlläufe bleiben dokumentiert. Der Vergleich innerhalb jedes einzelnen Fensters hatte für beide Versionen dieselben Hostbedingungen.

Build018 ist weiterhin ein getesteter Kandidat und nicht auf Dev oder den öffentlichen Instanzen installiert. A2 ist abgeschlossen; A1, vollständige A3-/A4-Abnahme, die fortgeführten 3600/3600/7200-Sekunden-Stabilitätsgates, vollständige externe Sicherung und qualifizierter Rollout bleiben offen. B ist unbegonnen.

[Ausführliche Paarwerte](2026-11-12-build018-six-window-comparison.md) · [Abnahmedetails](2026-11-12-build018-acceptance-checkpoint.md).

## Tatsächlich abgeschlossene Sicherung

| Nachtrag | Archivgröße | Reguläre Dateien separat restauriert und nachgehasht | Wiederhergestellte Bytes |
| --- | ---: | ---: | ---: |
| Delta022 | 101451161 Bytes | 16033 | 826890437 |
| Delta023 | 35086463 Bytes | 7982 | 115121646 |

Delta023 wurde am 12.11.2026 um 23:08:30 MEZ erfolgreich beendet: tatsächlicher Exitcode 0, Laufzeit 12,210 Sekunden. Hashes, Dateimodi, Eigentümer und Nanosekunden-Zeitstempel wurden bei der getrennten Wiederherstellung geprüft. Der Dateideskriptor-/Pfadschutz und die Reserve von 8 GiB plus 16 MiB blieben erhalten. Das enge unabhängige Review bestätigte das unveränderte Archiv-/Restoreverfahren. Delta023 enthält keine zu materialisierenden Symlinks; Delta022 indexiert zwei und stellt sie nicht als Links her.

Delta022-SHA256: e88caecf53ed94ddbac6ade1b3c638a637b50459d4dc4ff699dec50513861196

Delta023-SHA256: 189f8186d0ca9180d851fb75f9e3dfe5b5e06d9994b1edecbde84b40c35724d9

Das Build018-Payload und zwölf frühere native Fenster liegen in Delta022. Delta023 ergänzt den ausdrücklich ausgewählten Fortsetzungsstand, die finalen Observer-/Controllerpakete und Reviews, die Erklärung der A4-Beobachtungslücke sowie das zusätzliche geschlossene Prescan-Fehlfenster. Alte FAILs und partielle Zwischenstände bleiben unverändert erhalten. Ein nativer Start aus der vollständigen zusammengesetzten Restorekette ist nicht nachgewiesen.

Der im Archiv festgelegte lokale Quellcommit ist 82ccda74e704fe8b4ba8e636c8b7ea6d2dd08614. Seine öffentliche Entsprechung d0b8fb6ea1d7d4fab4e751bbbf82ed90fd3d007a wurde auf dem Server tatsächlich gefetcht; beide Bäume sind 4e1d3381fbb919d41e0dafb0e2b907b514dc6f1d. Diese spätere Abschlussdokumentation ist ein eigener öffentlicher Stand. Ihr zusätzlicher Server-Fetch ist durch die nachfolgende Zugriffssperre blockiert.

## Geänderter externer Blocker

Die lokale Ausführungsumgebung wurde nach ihrem Ausfall tatsächlich wieder verfügbar. Der Upload des unveränderten Delta022-Restoremanifests in den bestehenden privaten Drive-Ordner gelang. Der tatsächliche Rückdownload am 12.11.2026 um 23:16:55 MEZ ergab exakt 50063 Bytes und SHA256 d69a4ec7a72da2b2df7f193d84cf7236ef668c07e0aa015afb65830ab6119cfe.

Danach meldeten beide getrennten Worker schon beim ersten neuen RDC-Lesezugriff, dass das monatliche Desktop-Commander-Kontingent ausgeschöpft sei und Toolaufrufe pausiert seien. Die Rückmeldung untersagt erneute Versuche oder Neuverbindung. Danach gab es keinen weiteren RDC-Aufruf und keinen Wechsel auf einen anderen Remote-Ausführungspfad zur Umgehung.

Die Archive022/023 sind nicht lokal verfügbar und konnten vor dieser Sperre nicht auf Drive übertragen werden. Das hochgeladene Manifest ist keine Kopie der Archive. Delta021 bleibt der letzte vollständige, tatsächlich extern hochgeladene und per Rückdownload geprüfte Archivstand.

Die gesondert angestoßenen neuen A1-/A4-Ursachenaufgaben konnten ihre aktuellen Remote-Rohbelege nicht lesen und ihre geplanten Remoteordner nicht anlegen. Ihre lokalen Übergaben sind abgeschlossen. Eine begrenzte Sichtung vorhandener historischer Delta019-Quellen bestätigt lediglich ältere Controls-Initialisierung und Glättungskonfiguration; sie belegt weder die aktuelle Original-1.07-Verarbeitung noch die Ursache der wechselnden Eingabeverstärkung. Es gibt keine neue Ursachebehauptung oder spekulative Produktivkorrektur.

## Geschlossener Betriebsstand

Alle dokumentierten Root-Spiel- und Buildfenster sowie der Sicherungsprozess sind beendet. Die normalen Prozessschlüsse, akzeptierten Schlusslogs und Dateirestores der Versuche sind dokumentiert. Beide Worker sind nach ihren Handoffs ruhig. Es läuft keine automatische Wiederholung oder unbeaufsichtigte Fortsetzung.

Die letzte tatsächliche Flottenprüfung vom 12.11.2026 um 22:43:05 MEZ bestätigte sechs Instanzen mit jeweils acht eigenen Bots, UNKNOWN0, effektiven Spawnwert0 und die bisherigen DLLs. Öffentliche aktuelle Logzähler waren jeweils 0 BAD/0 Disconnect; die bekannte Devhistorie 37/3. Dies ist der datierte letzte Beleg und keine neue Prüfung nach der Zugriffssperre.

## Exakte Fortsetzung

1. Erst nach legitimer Wiederverfügbarkeit des Remote-Zugriffs den aktuellen Server-, Prozess-, Lock-, Git- und Archivzustand feststellen. Die Kontingentsperre nicht durch Wiederverbindungen oder andere Remote-Ausführungspfade umgehen.
2. Die unveränderlichen Archive022/023 mit den oben genannten Größen und Hashes aus der bestehenden Sicherung übernehmen, privat auf Drive hochladen und tatsächliche Rückdownloads prüfen. Das originale Delta022-Manifest und die Archiv-Indizes bestimmen die konkrete Vorgängerkette; keine fortlaufende Nummerierung erfinden.
3. Die spätere öffentliche Abschlussdokumentation mit der bestehenden lokalen Git-Historie abgleichen. Der zuletzt tatsächlich serverseitig gefetchte Stand bleibt d0b8fb6; der saubere Archivquellstand bleibt 82ccda7. Vorhandene Arbeit und lokale Historie erhalten.
4. A1 anhand der aktuellen geschlossenen Rohzeitlinien klären: Enthält die als Kalibrierung beziehungsweise ACK akzeptierte Winkelantwort bereits die vollständige Eingabeverarbeitung des Einzelimpulses? Prescan-aus hat den Faktorunterschied nicht behoben. Keine Toleranz-/Timeoutlockerung.
5. Die tatsächliche A4-Versorgungslücke von Phase1 botB:1 anhand der vorhandenen acht beobachteten Leben untersuchen. Die separat erklärte frühe Log-/Inventarabdeckung von botA:2 beseitigt diesen anderen Fehler nicht.
6. Erst die unveränderten fachlichen und dauerhaften Abnahmekriterien erfüllen, danach qualifizierter Dev-zuerst-Rollout. B bleibt bis zum vollständigen A-Abschluss unbegonnen.

Bereits verbrauchte Freeze-/Native-/Sicherungswrapper dürfen nicht erneut gestartet werden. Ein vor der Umgebungsrückkehr vorbereiteter Abschlusshelper wurde nicht ausgeführt und enthält inzwischen veraltete Transportannahmen; er darf nicht unverändert als neuer Erfolgsbeleg verwendet werden.

[Maschinenlesbarer Abschlussstand](milestone-a-20261112/build018-blocked-handoff.json) · [Aktueller Status](2026-11-12-codex-continuation-status.md).
