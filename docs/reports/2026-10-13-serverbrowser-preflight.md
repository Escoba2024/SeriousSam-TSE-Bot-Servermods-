# Serverbrowser-Abnahme vorbereitet; sparsames Acht-Bot-Profil lokal bestätigt – 13.10.2026

Die Fortsetzung verwendet den synchronisierten Quellstand `3e0c8415bef056ce0b349603872180ba9e7c6b5f`, dieselbe nativ qualifizierte 61DC-DLL und exakt `LocalBotRelease.ini`. Es gibt keine neue Bot-Funktion, DLL-Änderung oder Ground-Integration. Der begrenzte lokale Betriebsnachweis besteht. **Öffentliche Serverbrowser-/333networks-Abnahme bleibt offen.**

## Neuer lokaler Nachweis

| Prüfung | Ergebnis |
|---|---|
| Geplante Steady-Testdauer | 600 s; gemessene Runner-Steady-Zeit 601,9843383 s |
| Unabhängige vollständige Serverabfragen | 595,771161 s; 119 Steady-Proben, jeweils alle acht eindeutigen erwarteten Namen |
| Runtime | Retail TSE 1.07, leerer Mod; unveränderter Dedicated Server und Vanilla-Observer |
| CRC | 3 akzeptierte Verbindungen: zwei Vier-Spieler-BotClients und Observer |
| Native Profile | Acht eindeutige native Profile mit passenden Sidecars; Identitäten bleiben privat |
| Sparsame Entscheidungen/Actions | A1–A4 jeweils 604 vollständige 1-Hz-Proben; B1–B3 jeweils 603; B4 602; keine inneren Periodenlücken oder unvollständigen Schlussproben |
| Bewegung/Kampf | Mehr als zehn verschiedene native Positionen sowie lebende Combat-Readiness für jeden Bot; 118 unabhängige Observer-Kampfkills im gesamten gespeicherten Lauf |
| Cleanup/Rücknahme | 815 ursprüngliche Runtime-Dateizustände bytegleich restauriert; 30 Originalbinaries unverändert; null eigene Spieleprozesse/Testports; keine Crash-/Cleanupmarker |

Die eigenständige Auswertung verwendet die vorhandenen Funktionen `audit_runtime` aus `Test-FleetAIEvidence.py` und `audit_sparse_stream` aus `Test-LocalReleaseSmoke.py`. Die acht Logstreams müssen mit den acht nativen Runtime-Identitäten übereinstimmen. Jede erfasste periodische Probe wird auf gültige Bewegung, Combat-/Action-Semantik, Zielzuordnung und begrenzte Hinderniserholung geprüft.

Dies ist ein **Steady-Probe ohne neuen Lifecycle-Test**. Der vollständige Lifecycle-Smoke vom früheren lokalen Release bleibt ein eigener Beleg. 1-Hz-Proben ersetzen keinen lückenlosen 20-Hz-KI-Nachweis; aus diesem Lauf folgen weder eine neue KI-Stunde noch ein neuer regulärer Shutdown- oder Brush-Abschlussnachweis für jeden Bot. Der Prüfablauf verwendet kontrollierten Teardown. Die unabhängige Query-Spanne liegt knapp unter zehn vollständigen Minuten und wird mit ihrem tatsächlichen Wert dokumentiert.

- Kandidaten-DLL SHA256: `61DC27E0E7B80BADCF9AE705C30FCA88EDD3935737715DFFFF59E90C26F1FEF9`.
- Exakter sparsamer Startup SHA256: `2B063633CE598B787BAFDA426C30DD39125A9EA7DF1D94A37B880FA64EEC42F6`.
- Private Rohbelege: `.codex/serverbrowser-20261013/native-eight-public-600/`.
- Bereinigte Zahlen und Grenzen: [Abnahmezusammenfassung](2026-10-13-serverbrowser-preflight.json).

## Externe Masterserver-Beobachtung

Die Daten stammen aus der [333networks-JSON-API](https://333networks.com/json). Die Serverliste für `serioussamse` war vom Shadow-PC erreichbar und enthielt 70 Einträge. Vor dem Test und während des Tests wurde kein passender eigener Endpunkt gefunden; die Detailabfragen antworteten `not_in_db`.

Die Beobachtung am 13.10.2026 umfasst eine Listenabfrage um 19:50:01 UTC und die spätere Endpunktabfrage um 19:53:06 UTC, jeweils während die lokale Query acht Bots zeigte. Wiederholte identische API-Abfragen wurden durch mindestens 460 s getrennt. Die API dokumentiert einen 7,5-Minuten-Aktualisierungszyklus; gespeicherte Master-Daten sind daher keine zeitgleiche Echtzeitmessung der Botpopulation.

**Nicht bestanden bzw. noch nicht durchgeführt:** öffentliche eigene Listung, direkte externe UDP-Query, eigener Eintrag im nativen Vanilla-Serverbrowser und ein echter Vanilla-Join von außerhalb des Shadow-Netzes. Die Abwesenheit innerhalb dieses begrenzten Fensters beweist keine alleinige Ursache oder dauerhafte Unmöglichkeit der Registrierung.

## Netzwerk- und Routingbefund

Die isolierte Dedicated-Server-Kopie besitzt aktivierte öffentliche Windows-Firewall-Allow-Regeln. Der laufende Prozess bindet UDP `0.0.0.0:25600` für das Spiel und UDP `0.0.0.0:25601` für die Query. Das bestätigt lokale Bindung und vorhandene Regeln, nicht die externe Erreichbarkeit.

`master.333networks.com` und `gs.ostap.eu` werden aufgelöst, jedoch auf unterschiedliche Adressen. Der gespeicherte Serverwert `net_strMasterServer` nennt `gs.ostap.eu`; zusätzlich steht ein `net_strMasterServerOverride` auf 333networks. Die tatsächlich verwendete native Heartbeat-Zieladresse wurde nicht durch einen Packet-Capture bestätigt. Die Original-Engine enthält weiterhin ältere GameSpy-Domaintexte; deren DNS-Namen werden hier nicht aufgelöst. Aus statischen Strings und gespeicherten Einstellungen allein folgt keine bewiesene aktive Routing-Ursache.

Die [333networks-Anleitung für Serious-Sam-Server](https://333networks.com/instructions/serioussam/s) beschreibt Steam-Versionen als automatisch angebunden. Für dieses konkrete unveränderte Binär-/Konfigurationspaar bleibt die aktive Anbindung trotzdem zu verifizieren.

UPnP stellt auf diesem Host keine auslesbare Mapping-Collection bereit; der private Standardgateway war über die begrenzte HTTP-Abfrage nicht administrierbar. Es wurde keine Weiterleitung verändert. Der Benutzer bestätigte, dass noch keine Portweiterleitungen eingerichtet sind.

Der ursprüngliche Auftrag benennt **Shadow Neo Lite als Entwicklungs-/Testsystem**; die Netzwerkkarte ist virtuell und der Gateway privat. Shadow ist ein Cloud-PC, wie auch die [Anbieter-FAQ](https://shadow.tech/gb/faq/) beschreibt. Eine Freigabe am Heimrouter würde nicht den im Shadow-Rechenzentrum laufenden Server veröffentlichen. Auch ein Mobilfunk-Hotspot für den Streaming-Zugang stellt keine öffentlichen UDP-Ports im Cloud-Netz bereit. Aus diesen Befunden wird keine pauschale, offiziell bestätigte Shadow-Port-Sperre abgeleitet. Die tatsächliche öffentliche UDP-Erreichbarkeit ist ungeklärt.

Ein privater, nur syntaktisch geprüfter Probe-Wrapper für eine temporäre `net_strMasterServer`-Variation wurde vorbereitet, aber **nicht ausgeführt**. Er gehört nicht zum Release und liefert keinen Erfolgsnachweis.

## Nächster öffentlicher Abnahmeschritt

1. Einen tatsächlich erreichbaren öffentlichen UDP-Endpunkt für den unveränderten Dedicated Server bereitstellen. Spiel- und Query-Port müssen getrennt korrekt geroutet sein. Ein öffentlicher Dedicated-Host mit normal ausgehend verbundenen Shadow-BotClients erhält die bestehende Architektur.
2. Effektive native Masterserver-Adresse/Heartbeat und Registrierung prüfen. Keine Änderung an Engine, Entities oder Original-Server-EXE aus diesem Befund ableiten.
3. Frische externe Master-Daten, direkte UDP-Status-/Player-Abfrage und die acht nativen Identitäten vergleichen. Cache-Alter, vollständige Namen, echte Slotzahl, Version und Mod prüfen.
4. Den eigenen Eintrag im normalen Vanilla-Browser sowie einen echten externen Vanilla-Join abnehmen.
5. Erst danach Gate 9 als öffentlich bestanden kennzeichnen. Größere Skalierung, Population-Supervisor und 24/7 bleiben ihre eigenen Gates.

Die öffentlichen Berichte enthalten keine konkreten Host-IP-Adressen, privaten Profil-GUIDs oder Runtime-Rohlogs. Firewall, Hosts-Datei, Router, GameMP-Kandidat und Originalbinaries bleiben unverändert. Der ältere Quellcode-Bericht `poc/VERIFIKATION.md` kennzeichnet seine 333networks-Aussage jetzt korrekt als Erwartung plus lokale Query, mit weiterhin offenem öffentlichen Gate.
