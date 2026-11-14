# A1: Zeitkorrektur geprüft, unterschiedliche Drehungsverstärkung offen

**FAIL**, keine A1-Abnahme. Einzelner Original-NoFire-Lauf
`a1-release-deadline-20261114-144306`, Ergebnis-SHA256
`51e8e0e5ed32177606a71e6c1ca17e82812c5ba047581bf81525fef5652cc772`.

Alle drei tatsächlich bestätigten XTest-Eingaben wurden innerhalb der
unveränderten Fristen abgeschlossen: rechts+12 Pixel137,449 ms,
vorwärts159,541 ms und links−12 Pixel144,257 ms einschließlich Release.
Jeweils eine tatsächliche Held-Beobachtung. Keine neue Eingabe wurde ergänzt.
Der frühere Zeitfehler ist in diesem Lauf nicht aufgetreten.

Die bestehende Prüfung scheitert jetzt an
`opposite normal look does not reproduce body response: action gain`.
Die einzelne bestätigte Rechtsanfrage wird in zwei Original-GetInput-Zyklen
als jeweils+12 verarbeitet: Input37→Action38−3 Grad sowie
Input39→Action40 nochmals−3 Grad. Die entgegengesetzte Anfrage liefert
Input119→Action120+3 Grad. Damit unterscheiden sich tatsächliche ACK-Gains
−0,5 und−0,25 Grad/Pixel. Die erste Bodydrehung von etwa−6 Grad bestätigt
die doppelte Verarbeitung. Beide Rechtszyklen melden erfolgreiches Recenter;
warum erneut dieselbe Abweichung gelesen wurde, ist noch unbekannt.
Keine pauschale Hook-/Wineursache oder bloße Snapshotverwechslung behauptet.

`qualified`, `input_once_proven`, `first_processed_state_proven`,
`actual_shot_proven` und `foreign_hit_proven` bleiben false. Kein Fire,
keine Schadens-/Respawnqualifikation und keine Toleranzänderung.

Originalbytevergleich und Collectorclose sind bestätigt, der eigene Worker
wurde nach normalen Rollencloses beendet. Alle drei vollständigen Schlusslogs
sind ohne neue Sync-/Disconnect-/Crashmeldungen archiviert. Root prüfte
unabhängig664 Dateien mit Metadaten, acht Absenzen, drei Loghashes sowie
Prozess-/Displayende: `PASS_RESTORE`. Sieben Hostproben: CPUmax68,113%,
RAMmin2901565440Bytes, Diskmin8878227456Bytes; Startup-Abtastlücke26,533s,
deshalb allgemeiner Budgetclaimfalse.

Nächster A1-Schritt ist die Diagnose der bereits aufgezeichneten
Cursor-/Recenter-/Profilwerte. Kein automatischer neuer Lauf.

Parallel ist der unabhängige Root-Quellenreview des deaktivierten eigenen
Build018/Yodeller-Syncversuchs abgeschlossen:35 gezielte OfflinefällePASS.
Rootfreeze `/srv/tse-owned-sync018-yodeller-root-frozen-20261114`,
Manifest`65d146786a4b4efd9e12868a540208c406f6aaa67e2ff6a1a533ab95bb628747`,
Launcher`eccfab2da9a4f312222cce269cbbe9a97fe24d67b0ad5be1b61db523ede8aea8`;
69Runtime-/61Source-/40Pythonpins und enges Gate-/Namespace-DeltareviewPASS_SCOPE.
Dieser Versuch ist noch nicht gestartet und hat keine native Qualifikation.
