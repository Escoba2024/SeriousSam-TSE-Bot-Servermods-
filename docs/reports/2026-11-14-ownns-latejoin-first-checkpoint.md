# Erster später Originalbeitritt: Startprüfung fehlgeschlagen

Root führte genau einen privaten018/Hard2/Yodeller-Fall aus. Live blieb
DevCecil048/fünfPublicGen2. Der geprüfte Rootfreeze hatte Manifest2cf9c5ca…;
Result-SHA256 `b44bab627e5cebbfa325a6fb9d6808a36f041c70d6534f7a9e0235d30b9e0a14`.
Status **FAIL vor600s**; kein vollständiges Syncfenster und keine A-/B-Abnahme.

Die vorgeschaltete Readiness war nach2,1955s tatsächlich erfüllt: alle acht
Bots bewegten sich innerhalb desselben Lebens mehr als1m; zwei Slots hatten
gebundene Native-FIREflag-/Sourcegrowthbelege, die Kohorte einen serverseitigen
Abschuss und positive eigene Queryfrags. Danach Capture bereit, privater
Acht-Botcheck erneut gültig und Original genau einmal gestartet.

Query9 und vier echte PID-/FD-/UDP-/Namespacebindungen waren vorhanden.
Die ersten Server-/Bot-A-/Bot-B-Tabellen enthielten0–8. Die erste Original-
Beobachtung dagegen enthielt in beiden tatsächlichen Reads nur0–7
(game_tick22,64994); die nächste Original-Beobachtung enthielt in beiden
Reads0–8 (23,19993). Der erste Read begann rund0,31s vor dem zweiten.
Die strenge Prüfung zweier vollständiger Neun-Slot-Beobachtungen schlug
deshalb korrekt fehl. Das beweist keine neue Syncursache oder dauerhafte
Rosterstörung. Alle Rohframes sind erhalten; sie werden nicht als gültige
vollständige Anfangsbeobachtungen umgedeutet.

Ein zusätzlicher Evidenzfehler ist eingegrenzt: der neue LocalSource-Read
und beide Slot8-Inventarreads waren im Kontrollfluss bereits durchlaufen,
ihre Rohwerte wurden vor dem späteren Framefehler aber noch nicht gespeichert.
Deshalb wird daraus ausdrücklich keine native ABIqualifikation abgeleitet.
Der enge Folgeplan verlangt sofortige private Rohquittungen vor Folgechecks
und echte Startbereitschaft innerhalb derselben absoluten30s-Aufnahmefrist.
Die vollständigen Slot-/PID-/Modul-/Entity-/Regelprüfungen bleiben bestehen;
kein zusätzlicher Originallaunch oder automatisches Retry.

Capture regulär mit Exit0 geschlossen:1157 Pakete,2336 empfangen,0Kernel-
drops,444910B, SHA256
`7a116d65953e0daee949e139127e781531d57cbfcdcbf54abac7566abb9a372b`.
Protokollstatus bleibt wegen fehlgeschlagener Schemaadmission unvollständig;
das aggregierte normal_capture_closed-Feld bleibt false, obwohl der konkrete
Stop/Exit0 belegt ist. Nachträglicher separater Audit anhand der bereits vor
Outcomes gespeicherten echten Endpointbindung: A↔B12 gleiche/0abweichende
Checks; A↔Original und B↔Original jeweils ein gleicher/0abweichende Checks,
elf fehlende Paarpartner und sechs nicht unterstützte Transportpakete.
Originalvergleiche sind **INCOMPLETE**, keine CRC-/Transportvollständigkeit.
Der erste Offlineaufruf benutzte versehentlich Path statt offenem Stream und
scheiterte vor Ausgabe; der korrekte Aufruf behielt Decoder und Rohdatei gleich.

Alle vier Testrollen normal geschlossen. Unabhängiger Rootrestore:
640Dateien/Metadaten, vier geschlossene Logs, Rollen-/Worker-/Displayende
PASS. In allen vier Schlusslogs0BAD/Disconnect. Frischer anschließender
Labpreflight: vier Roots quieszent, Displays154/155 frei, Sperren exklusiv
geprüft.35Ressourcensamples: CPUmax52,9703%,RAMmin2845278208B,
Diskmin10406174720B, längste Abtastlücke2,1464s. Kein Gameplaybudget- oder
Stabilitäts-PASS aus diesem fehlgeschlagenen Start.

Privat: RootEV/owned-latejoin018-root-restore.json und
owned-latejoin018-partial-pairs.json; vollständige Rohdaten unter
`/srv/tse-milestone-a-evidence-20261111/own-latejoin018-root-20261114-173005`.
Keine laufende Testrolle oder unbeaufsichtigte Wiederholung.
