# Population-Supervisor – Prozessgruppen, 14.10.2026

## Ziel und bestehende Autorisierung
Fortsetzung des bestehenden autonomen Entwicklungsauftrags. Einen lokal prüfbaren Supervisor auf vorhandenen Fleet-Werkzeugen aufbauen, ohne GameMP/Engine/Entities/Server zu verändern. Er steuert ganze vorbereitete BotClient-Gruppen, nicht einzelne native Spieler.

## Entscheidung
Die gesamte tatsächliche Serverbelegung ist maßgeblich. Cap = min(TargetPopulation, MaxPlayers − ReservedHumanSlots). Namen/Präfixe dienen nicht zur Human-Erkennung. Unbekannte Spieler zählen vollständig gegen Cap. Identitätsgeprüfte eigene Prozesse sind die einzigen Stop-Ziele. Ungefüllte Restplätze kleiner als die kleinste inaktive Gruppe bleiben frei. Beispiel Target8: acht Bots + Human =9 → eine Vier-Bot-Gruppe stoppen → fünf Spieler; nach Human-Abgang vier Spieler → Vier-Bot-Gruppe wieder starten → acht.

## Beobachtung und Sicherheit
Drei UDP-Antworten: status → players → status. Version1.07, serioussamse, leerer Mod, MaxPlayers1..16, vollständige Player-Indizes und Final-Marker; Count/Max/Map/Version/Mod müssen beide Statusantworten konsistent machen. Gleiche Namen verschiedener Player-Indizes sind erlaubt. Fehler/Teilantwort/Wechsel setzt Start-Stabilisierung zurück und startet nichts.
Starts benötigen zwei konsistente freie Beobachtungen sowie zehn Sekunden Wiederstartverzögerung nach Stop/Fehlstart. Stops bei belegungsbedingtem Überhang erfolgen sofort, nur eine Aktion pro Poll. Pro Gruppe vorbereitete native Profile/GUID-Sidecars und1..4Spieler; vorhandene Start-/Stop-Skripte übernehmen Prozessbuchhaltung/Rollback/PID-Pinning.
Ein Start bleibt pending: nächster Start erst nach verifiziertem laufenden Prozess, frischem eigenen Joinlog und vollständigen erwarteten Namen. Deadline45s; bei Überschreitung eigenen Prozess stoppen und Cooldown. Konfigurationsfehler, Dateischreibfehler und Prozessfehler führen zum Exit mit finally-Cleanup aller selbst gestarteten Gruppen. Neue State-Verzeichnisse; exklusives Dateilock für jede Clientinstallation verhindert parallele Controller verschiedener State-Verzeichnisse. Kein Übernehmen bereits laufender fremder Clients. Logdateien vor Start sichern und für frischen Joinnachweis archivieren; keine Dateien/Profiles/DLLs neben Logs verändern.
ObserveOnly arbeitet ohne Starts/Stops und verwendet optional einen bestehenden Fleet-State ausschließlich lesend. Abbruch über stop.request im eigenen State-Verzeichnis, begrenzte Iterationen oder Ctrl+C;finally beendet nur eigene Gruppen. Keine Dienstinstallation.

## Abnahme und Grenzen
Reine Modelltests: unbekannte/spoofähnliche Namen, Dubletten, unvollständige/wechselnde Antworten, Reserve, Überhang, Gruppengröße/Cooldown. Controllerprüfungen: echte Kindprozesse mit injiziertem Transport/Launch; Fehlstart, Join-Timeout, fehlender PID/Startzeit-Mismatch, zweiter Lock und Cleanup. Kurze native Probe mit derselben61DC-DLL ist eigener Gate; bis dahin keine neue native/24h-/race-freie/Einzelslot-Abnahme behaupten. Reserve mildert, garantiert keine unbegrenzten gleichzeitigen Human-Joins. Öffentliche Serverbrowser-Abnahme bleibt offen.
