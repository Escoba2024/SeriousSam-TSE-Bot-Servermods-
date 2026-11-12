# A1 V5: Nebenlast beseitigt, tatsächlicher Flugabbruch eingegrenzt

## Ergebnis

Die festhängende RDC-Quelltextsuche wurde anhand von PID, Prozessstart, Elternprozess, Arbeitsverzeichnis, ausführbarer Datei und aktiver RDC-Sitzung eindeutig identifiziert und von Root gezielt beendet. Beide zugehörigen Prozesse waren anschließend abwesend. An Spiel, Renderer oder CPU-Grenze wurde nichts geändert.

Die ursprüngliche Ablehnung bei 82,2857 % Host-CPU über 1,3372 Sekunden bleibt FAIL. Ihr genauer historischer Prozessanteil ist nicht rekonstruierbar. Der aktuelle zusätzliche Verbrauch und die anschließende Entlastung sind dagegen direkt gemessen.

| Messung | Vor der Bereinigung | Nach der Bereinigung |
| --- | ---: | ---: |
| Tatsächliche Dauer | 10,000105 s | 10,000132 s |
| Host-CPU im Mittel | 57,5297 % | 37,0390 % |
| Höchstes etwa einsekündiges Intervall | 60,8142 % | 39,8438 % |
| Systemanteil | 31,6882 % | 8,6843 % |

Die frühere Suche verbrauchte 1.001 CPU-Jiffies in zehn Sekunden bei CLK_TCK 100, ungefähr einen vollständigen Kern. Die Produktionsprozesse wurden nicht beendet. Andere Last schwankte zwischen den Messungen; die Differenz ist kein exakter rückwirkender Abzug vom ursprünglichen Test.

## Einmaliger Folgeversuch

Nach der belegten Bereinigung wurde ein einzelner neuer Versuch ausdrücklich dokumentiert. Der bereits verbrauchte Lauf, sein Wrapper und seine Logs bleiben erhalten. Neue Decision-, Owner- und Logdateien verwenden denselben unveränderten V5-Controller und dasselbe gepinnte Manifest. Es gab keine automatische Wiederholung.

Das reale Fenster **153533** erreichte die Route und einen erkannten Flugübergang. Nach 16 bestätigten Eingaben scheiterte es an der unveränderten Achtsekundengrenze: **flight deadline exceeded**. Pickup, Schuss, Fremdschaden und First-State-Nachweis sind weiterhin nicht erbracht. Die Ressourcenüberwachung wies keine CPU-Probe ab; der höchste gemessene Intervallwert war 68,75 %. Die lange Startmesslücke von 24,6511 Sekunden bleibt ausgewiesen, weshalb daraus kein vollständiger Ressourcen-Dauernachweis folgt.

Der Wrapper endete mit Exit 1 nach 62,49 Sekunden. Drei Rollen und zwei Displays wurden geschlossen. Root prüfte anschließend unter der exklusiven Lab-Sperre alle vier Wurzeln auf Prozessfreiheit und bestätigte 664 Dateihashes sowie neun weiterhin fehlende Pfade. Die gesamte Wiederherstellung bestand.

## Nächste Arbeit und Abnahmegrenze

Der tatsächliche Flugverlauf wird anhand der aufgezeichneten Eingaben, erfolgreichen Lesesequenzen, Originalzustände und Nav-Geometrie untersucht. Eine bloße Verlängerung des Zeitlimits ist nicht beschlossen. Der separate Build017-Controller für die dichte Waffen-/Navigationsbeobachtung befindet sich in unabhängiger Prüfung; ein neuer Root-Lauf setzt seine abgeschlossene Prüfung voraus.

A bleibt offen: First-State-Schaden, vollständige Vergleiche des aktuellen Kandidaten, Karten-/Aktivitätsfreigaben, Langzeitprüfungen und kontrollierte Kandidatenverteilung sind nicht abgeschlossen. B bleibt unbegonnen. A2 und die verifizierte Delta020-Sicherung bleiben erhalten.

## Nachweise

Die maschinenlesbare öffentliche Quittung steht in [a1-v5-cpu-correction-flight-followup.json](milestone-a-20261112/a1-v5-cpu-correction-flight-followup.json). Private Originale: CPU-Analyse, Root-Pre-/Postflight, gesonderte Laufentscheidung und das geschlossene native Fenster 153533. Ergebnis-SHA256: 814ea8b5ff9536cc1b5c63b0b999be3d018de1eda82c853b8be2a0a3ad5c28e7.
