# Build018 auf allen sechs Servern – Ausführungsplan

> **Für ausführende Agenten:** superpowers:executing-plans verwenden. Root führt Deployment und Integration selbst aus; höchstens zwei Worker übernehmen unabhängige Leseprüfungen.

**Ziel:** Den vorhandenen Build018 mit seinem tatsächlich wirksamen neuen Kampfprofil zuerst auf Dev und danach auf den fünf öffentlichen Instanzen aktivieren, jeweils mit frischem Rückstand und kurzer Betriebsprüfung.

**Architektur:** Pro Instanz werden die beiden eigenen Botclients regulär beendet, das identisch geprüfte Kandidatenpayload und die passende getestete Konfiguration eingesetzt und die bestehenden Dienste nacheinander gestartet. Dedicated-Rollen bleiben separat gebunden; private Diagnosecontroller sind kein Flottenpayload.

**Technik:** Retail TSE1.07, Wine, GameMP.dll, bestehende systemd-Dienste, GameSpy-Abfragen, Cecil-/Kampfprofile.

**Auftrag:** Ausdrückliche Nutzeranweisung vom13.11.2026, alles auf die Server auszurollen. Diese aktuelle Anweisung autorisiert die Promotion trotz der zuvor benannten offenen Abnahmen. [Vorheriger Befund](../../reports/2026-11-12-build018-final-access-blocker.md) bleibt als historische Evidenz erhalten.

## Rahmen und Entscheidungen

- Keine weitere Nutzerbestätigung für den hier beschriebenen Rollout nötig.
- Ältere Anweisungen, erst nach der gesamten Releaseabnahme auszurollen, sind durch die heutige konkrete Rolloutanweisung als Ausführungsstop überholt. Offene Tests und alte FAILs werden dadurch nicht bestanden.
- Bestehende Arbeiten, Instanzidentitäten, Namen, GUIDs und Serverkonfiguration erhalten. Aktuelle Quelldateien und Konfigurationen vor jeder Änderung binden.
- Root ist alleiniger Runtimewriter. Die freigegebenen Zugriffsgrenzen gelten weiterhin; keine Umgehung über Diagnose-, Test- oder Offlineagentfunktionen.
- Mindestens8GiB freie Plattenreserve erhalten. Ressourcen vor/nach der Instanz prüfen; frühere Lab-Startgrenzen nicht ohne Prüfung ihrer tatsächlichen Geltung als neue Rolloutbedingung übernehmen.
- Keine zusätzlichen Stundenprüfungen als neue Voraussetzung dieser ausdrücklich gewünschten Promotion. Kurze tatsächliche Betriebsprüfung und gegebenenfalls Rücknahme bleiben erforderlich.
- Unimplementierte B-Funktionen und private Frida-/First-State-Controller sind kein ausrollbares Produktpayload.

## Kandidat und Reihenfolge

Build018:428544Bytes, SHA2566db89204e33dc7d76ecdfed68055d2b75bde4950475793a57101fd0cefcb8e4a. Buildmanifest-SHA256f4212443317b58b04808bd42d084e6a3286e458af2c0dbcfb276aa3bca931c2e. Quellcommit1802fb3f0720b53feb032abfe2c2a83407bfea6e, Baumdf9f4336153662e3398a28793e72c53e0c2161a3. Diese Pins stammen aus dem tatsächlich dokumentierten Build; sie sind heute noch nicht erneut am Host geprüft.

| Reihenfolge | Instanz | Port | Botclients / eigene Bots |
| --- | --- | ---: | ---: |
| 1 | Dev / Red Station | 25650 | 2 / 8 |
| 2 | Red Station | 25600 | 2 / 8 |
| 3 | Yodeller | 25610 | 2 / 8 |
| 4 | Skulls | 25620 | 2 / 8 |
| 5 | Little Trouble | 25630 | 2 / 8 |
| 6 | Hole | 25640 | 2 / 8 |

Historische Rückstände: öffentliche Botclients SHA2567fc94a39c3f5d9516f262d9e4d04a5cf38e6eb5ae3482976c32c952a99d30835; Dev-Botclients ec820d0461313c41fec2b477f57109310d3c71a77b4423955ac69f3807566530. Ein historischer Hash ersetzt keine heute vorhandene, frisch gesicherte Rückrolldatei. Die Dedicated-DLLs sind eigene Rollen und werden nicht pauschal durch die Bot-DLL ersetzt.

## Prüfungsfokus

1. Neue DLL, aber alter/inaktiver Kampfpfad: tatsächliche018-Konfiguration und wirksamen Pfad bestätigen.
2. Veraltete Prozess-/Unit-/Profilzuordnung: vor jedem Stop frisch binden.
3. Fehlender Rejoin oder neuer schwerwiegender Sync-/Crashfehler: Instanz rücknehmen, weitere Promotion pausieren.
4. Verlorene Namen/GUIDs oder falsche Instanzzuordnung: aktuelle Profile sichern und nach dem Start abgleichen.
5. Versehentliche Dedicated-/Map-/Navänderung: getrennte Rollen, tatsächliche Dateien und Weltbindung prüfen.

## Aufgabe1: Bestands- und Zugriffsprüfung

- [x] Aktuellen Fortsetzungsbranch prüfen: vor dieser Dokumentationsänderung f0078ffe13f64518875084673d8ed4d1cbc1597f.
- [x] Build-/Rolloutumfang anhand vorhandener Belege unabhängig prüfen: zwölf Botclientziele, sechs Instanzen, passende Profilmigration erforderlich.
- [x] Vorhandenen ssam.ai-Zugang frisch prüfen: Hostcheck13.11.2026 10:30:14UTC erfolgreich, ssam-system-control.service aktiv.
- [x] Tatsächliche Grenzen feststellen: Lesen der bestehenden privaten Backupquittung endet mit Permission denied; allgemeine systemctl-Diagnose nicht zugelassen; keine passende Deploy-/SSH-/Binärdateikopierfunktion im zugänglichen Toolbestand.
- [ ] Nach legitimer Wiederverfügbarkeit eines geeigneten Zugangs aktuelle sechs Instanzrollen, Dienste, Prozesse, Configs, Navbindungen, Spieler und Locks lesen.
- [ ] Kandidaten-DLL und Manifest tatsächlich am Host nachhashen; aktive018-Profile an die bewiesenen Kandidaten-/Startprofile binden.

**Ist:** BLOCKED_EXECUTION_CAPABILITY. RDC wegen der bestehenden Monatskontingentsperre nicht erneut aufgerufen. Keine Serverdatei verändert, keine Dienste gestartet oder beendet. Der erreichbare Hoststatus ist kein aktueller Sechs-Server-Spieltest.

## Aufgabe2: Dev aktivieren

- [ ] Aktuellen Dev-Rückstand aus DLLs, betroffenen Config-/Profil-/Navdateien, Metadaten und Runtimeidentitäten separat sichern und prüfen.
- [ ] Die beiden eigenen Dev-Botclients über ihren tatsächlichen normalen Dienstweg schließen.
- [ ] Exakt geprüfte018-DLL und passende getestete aktive Kampfeinstellungen einsetzen; Spawn0, Namenpool458, GUIDs und gewünschte Spielregeln erhalten.
- [ ] Dienste nacheinander starten und beide tatsächlich geladenen Module gegen018 prüfen.
- [ ] Kurzes frisches Betriebsfenster auswerten: Query, richtige Map, acht eigene Bots, Bewegung/Kampf/Tod/Respawn, wirksamer Kampfpfad, Navbindung, neue Fehlerdifferenzen und Ressourcen.
- [ ] Bei falschem Payload, fehlendem Rejoin oder neuem schwerwiegendem Betriebsfehler den frischen Dev-Rückstand regulär wiederherstellen.

**Abnahme dieser Aufgabe:**018 läuft tatsächlich auf beiden Dev-Clients und die konkreten Betriebsbelege sind festgehalten. Das ist keine vollständige Release- oder First-State-Abnahme.

## Aufgabe3: Fünf öffentliche Instanzen

- [ ] Aufgabe2 als denselben instanzbezogenen Ablauf für Red Station, Yodeller, Skulls, Little Trouble und Hole in dieser Reihenfolge ausführen.
- [ ] Nach jedem erfolgreichen kurzen Betriebscheck selbstständig mit der nächsten Instanz fortfahren.
- [ ] Bei schwerwiegendem neuen Fehler die betroffene Instanz zurücknehmen; keine unkontrollierte Fortsetzung auf den restlichen Instanzen.

**Abnahme dieser Aufgabe:**Zehn weitere eigene Botclients laden das identische018-Payload mit der richtigen wirksamen Konfiguration. Historische Fehlerzähler getrennt von neuen Ereignissen behandeln.

## Aufgabe4: Rolloutabschluss

- [ ] Gemeinsamen frischen Snapshot der sechs Instanzen und48 eigenen Bots erstellen; zusätzliche Teilnehmer gesondert ausweisen.
- [ ] Tatsächliche Module, Profile, Config-/Navbindungen, GUIDs und aktualisierte Runtimeidentitäten sichern.
- [ ] Neue Deploymentbelege und Rückstände persistent sichern; große Archive022/023 weiterhin separat extern übertragen und tatsächlich zurückprüfen, sobald ihr Zugriff wieder möglich ist.
- [ ] Ergebnis als ausgeführten Nutzerrollout mit konkreten Betriebschecks berichten. Offene Releaseabnahmen und unimplementiertes B weiter korrekt ausweisen.

## Aktueller Ledger — 13.11.2026 11:39:12 MEZ

**Ruling:**Die heutige konkrete Nutzerfreigabe ersetzt die alte Stopregel „erst vollständige Releaseabnahme“. Dadurch werden keine fehlgeschlagenen Tests umgewertet. Die bekannte Versorgungslücke und die offenen Dauer-/Erstzustandsbelege bleiben dokumentiert.

**Ruling:**Kein bloßer DLL-Tausch ohne wirksame018-Kampfeinstellungen; sonst wäre die beabsichtigte Verbesserung nicht nachgewiesen aktiv.

**Ruling:**Keine Änderung an Diagnose- oder Testwerkzeugen, um ihre Ausführungsgrenzen zu umgehen. Die tatsächlich fehlende Deploymentcapability ist ein externer Blocker, keine fehlende Nutzererlaubnis.

**Fortschritt:**Aufgabe1 nur bis zur Zugriffsprüfung erledigt; Aufgaben2–4 nicht begonnen. Kein Deploymentprozess aktiv. Der unabhängige Reviewer ist idle. Die nächste Handlung ist die tatsächliche Bestands-/Payloadprüfung über einen legitim wieder verfügbaren Zugang, keine erneute Freigabeabfrage.
