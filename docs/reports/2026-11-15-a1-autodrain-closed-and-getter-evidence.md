# A1: neuer autonomer Drain geschlossen, erste Getterabweichung weiterhin FAIL

Der neue gepaarte inputfreie Lauf verwendet den prospektiv gesicherten Rootfreeze
`f7de423422c967fbfda01225e5c292a86796e30dca7ec98d7411340a2526f5a0`.
Der Control vom 15.11., 08:55:39 UTC lief 10,000170 Sekunden begrenzt erfolgreich;
keine Eingaben, kein Worker/Frida, drei normale Prozessabschlüsse und Abschlusslogs.
Result-SHA256 `4a24f1962a953c5a42010f687d3440b62eb103d3a8860d4e21fd831135cc64e2`.

Der Trace 08:59:39 bleibt **FAIL**, Result-SHA256
`e7c50e390aea56e60533196b22e8973212c9b1f7f1075c75e22987d317bb9a13`.
Bereits die erste Drainserie meldet `bound getter changed` beim ersten
ApplyAction-LEAVE, vor dem Beobachtungsfenster. Zwei Events, zwei Faults,
ein vollständiger Aufruf, keine Drops/Abbrüche, ein Getteraufruf. Alle beteiligten
Callbacks und die TLS-Bindung liefen im Hauptthread. Die ersten tatsächlich
abweichenden Bytes fehlen im damaligen Fehlerdetail: **Ursache unbekannt**.
Damit ist ein periodischer alter Eingabepfad keine notwendige Voraussetzung
für diesen neuen Fehler; daraus folgt noch keine Retail-/Frida-Ursache.

Alle 38 Originalregionen waren nach Unload/Detach wieder identisch; drei Rollen
normal beendet, Abschlusslogs vorhanden. Root prüfte um 09:00:41 UTC unabhängig
664 Dateien einschließlich SHA256, Rechten, beiden Snapshot-Zeitstempeln,
neun Abwesenheiten sowie eigene Rollen, Units, Displays und vier Sperren.
Das ist Wiederherstellung, keine A1-Abnahme.

## Eng begrenzte Cleanupkorrektur

Nach einem authentischen Fault-/TTL-/Queue-Stop verlangte der alte Drainworker
irrtümlich weiterhin `host requested`. Dadurch blieb der finale Capture-Nenner
offen und es entstanden zusätzliche Folgefehler. Root `25e3847` akzeptiert den
exakt zum gemeldeten Stop passenden ACK, erhält den sticky FAIL und versucht
abschließende Rohdatensicherung/F-Zähler. Ein geänderter Stopgrund oder laufende
Callbacks werden weiterhin abgewiesen. Root: 61 Tests bestanden in 4,314 Sekunden;
kein unveränderter Native-Retry, alte Resultate bleiben fehlgeschlagen.

## Gegenproben und nächster konkreter Beleg

Drei eigene Linux-ELF32-Frida-Proben prüften Entry/Leave, x87 sowie zuletzt die
22-Byte-Instruktionsform mit Callback vor FLD bei +15. Je drei Fälle mit 400
nativen Rückgabewertprüfungen endeten regulär. Während des Selfdetach waren
Hookbytes sichtbar; beim ersten äußeren Apply-/Tick-LEAVE waren Originalbytes
wiederhergestellt. **Keine Probe reproduzierte den Retail/Wine-Fehler.**
Der +15-Fall verwendet eigenes Fake-TLS statt des Retail-FS-Zugriffs;
keine ABI-, Vanilla-, Windows- oder Getterursachenabnahme daraus ableiten.
Quittung: `e652e3d00b557ad7b9453eb87e1eb52f2498117acd2109fd7ce7d9d35dea5120`.

Root `202dea5` integriert deshalb ausschließlich einen Fehlerbeleg aus dem
bestehenden einzelnen 22-Byte-Read, ohne Guardlockerung. Root acht Tests
bestanden in 1,023 Sekunden; [Details](2026-11-15-a1-getter-first-mismatch-receipt.md).
Ein neuer prospektiv geprüfter Fork und frischer Control sind vor einem einzigen
begrenzten Trace erforderlich; keine alten Controls übertragen.

## Korrektur eines Root-Metadatenfehlers

Nach dem Control scheiterte der erste unabhängige Checker an einem Python-
Pfadausdruck vor den Dateiprüfungen. Ein danach gestarteter Trace-Preflight
brach korrekt wegen des fehlenden Restorebelegs ab, hatte jedoch durch einen
normalen Hashread die Zugriffszeit genau einer Originaldatei verändert.
Inventar: alle 664 Hashes/Rechte/mtimes unverändert, genau eine atime abweichend.
Nach erneuter exklusiver Sperrung und Quieszenz spielte Root ausschließlich
diese gesicherte atime zurück. Korrekturquittung:
`65d7ed3d2d56bec580e6bd1e8de3a5ceff5e5ac2eec75fb383986ab310dbe9c3`.
Control-Restore gilt ab diesem ausdrücklich dokumentierten Korrekturpunkt,
nicht als ununterbrochener automatischer Metadatenerhalt. Nachfolgende
Root-Hashreads verwenden O_NOATIME ohne Fallback. Der Trace benötigte keine
solche Nachkorrektur. Originalresultate und fehlgeschlagene Checker sind erhalten.

A offen; keine First-State-/Schadens-, vollständige 18-ABI- oder Dauerabnahme.
Live-Flotte unverändert, B nicht begonnen.
