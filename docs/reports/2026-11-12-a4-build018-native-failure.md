# Build018: Red-Resetprüfung nicht bestanden, Flotte restauriert

Stand: 12.11.2026 21:47:01 MEZ.

## Tatsächlicher Ausgang

Das einzelne fest begrenzte Build018-Fenster 202210 endet mit FAIL. Nach 424,969771 beobachteten Sekunden sind beide Red-Station-Wechsel und drei Spielphasen erfasst. 23 von 24 Slotphasen erfüllen die unveränderten fünf Aktivitätsfelder. In Phase1 fehlen für botB:1 die beobachtete nützliche Waffenaufnahme und native nützliche Fernfeuer-Samples. Die vorhandene Fire-Action-Zeile allein ersetzt diese beiden Felder nicht.

Die originale Vanilla-Beobachtung wurde pro Mapepoche normal neu gestartet. Daraus folgt kein automatischer Vanilla-Wiederbeitritt. Es gibt keine Freigabe der Red-Whitelist, keine A4-Gesamtabnahme und keinen Rollout.

Kandidat: SHA256 6db89204e33dc7d76ecdfed68055d2b75bde4950475793a57101fd0cefcb8e4a. Originalresultat: SHA256 40ec26b7c4987a05931f4ca09f90df25f19157b61a64874f04951e0feb584f45.

## Inventarbeobachtungen und offene Korrelation

Die vorhandene Inventarauswertung ist für alle 133 darin beobachteten Leben unabhängig reproduziert: 110 beobachtete HP-Tode, 23 rechtszensierte Leben, 54 Leben mit nützlichem Besitz und 50 mit tatsächlichem Vorher/Nachher-Aufnahmebeleg. Die vier übrigen Besitzfälle werden nicht als beobachtete Aufnahme umgedeutet. 1601 Samples erfüllen die bestehende Kombination alive/current-useful/has-ammo/fire-requested; sie sind keine Schuss- oder Trefferzahl.

Der auffällige Slot hat acht inventarbeobachtete Leben und sieben HP-Tode. Kein Leben zeigt nützlichen Besitz; das längste reicht bis zum letzten lebenden Alter von 46,399574 Sekunden. Der phasenweise Clientlog enthält acht Goal-End-Ereignisse mit unavailable und fünf mit death. Ohne vollständige kausale Zuordnung wird daraus keine pauschale Konkurrenz- oder Navigationsursache abgeleitet.

178 Datenintegritätsprüfungen und 57 Quellnachhashes bestehen. Der anschließende unveränderte strenge Lebens-/Clientlogabgleich stoppt jedoch in Phase1 botA:2: sechs inventarbeobachtete Leben stehen sieben CecilSpawn-Markern gegenüber. Alle sieben Marker und sämtliche Inventarproben bleiben erhalten. Die komplette Eins-zu-eins-Lebenskorrelation ist deshalb offen; die Bezeichnung 133 ist ausdrücklich der Inventarbeobachtungsnenner. Der Fehler der Analyse wird nicht durch Weglassen des zusätzlichen Markers oder Hochsetzen einer Uhrtoleranz verdeckt. Die alten Build017-Auswertungen bleiben unverändert; ein Vergleich unterschiedlicher Builds wird nicht als bloße Zeitverlängerung desselben Builds bezeichnet.

## Ressourcen und tatsächliche Wiederherstellung

Die Hostmessungen bleiben innerhalb der unveränderten Grenzen: maximal 56,470588 Prozent gemessene CPU-Intervallauslastung und mindestens 1916665856 Byte MemAvailable. Die maximale Gameplay-Abtastlücke beträgt 2,357524 Sekunden; die deutlich längere Startlücke bleibt separat dokumentiert. Diese Messung erfüllt kein Dauerlastgate.

Root bestätigt vier normal geschlossene Labrollen, akzeptierte geschlossene Logs, beide entfernten Displays und unabhängig 643 restaurierte Dateihashes sowie fünf Absenzen. Keine Native- oder Buildausführung dieses Fensters bleibt aktiv.

Der Dev-Wächter hat am 12.11.2026 um 21:31:53 MEZ die beiden ursprünglichen Botdienste nach 1692,647926 Sekunden Pause erfolgreich wiederhergestellt. Pinned DLLs, Eingaben, Spielerdateien/Namen/GUIDs und die Dev-Serveridentität sind geprüft; Restorefehler null, keine neue Release-DLL installiert.

Die vollständige frische Flottenprüfung um 21:32:51 MEZ bestätigt sechs Instanzen mit je acht eigenen Bots, UNKNOWN überall null und effektiven Spawnwert0. Die aktuellen kumulativen Logzähler sind öffentlich0BAD/0Disconnects und Dev37BAD/3Disconnects, unverändert zu den vorigen Belegen. Das ist eine Bestandsprüfung, keine neue Langzeit- oder individuelle Aktivitätsabnahme.

## Fortsetzung und reale Grenzen

A1 bleibt vor dem eigentlichen Erstzustands-Schadensnachweis offen. Die sechs A3-Vergleiche zeigen einen Vorsprung gegenüber der Alt-DLL; STARK > MITTEL ist noch nicht nachgewiesen. A4 benötigt die vollständige Lebenskorrelation und eine belegte Ursache/Abnahme der Versorgungslücke. Die Originalgates 3600/3600/7200 Sekunden, vollständige Kartenqualifikation, separate Wiederherstellung und Dev-zuerst-Rollout bleiben bestehen.

Die lokale Arbeitsumgebung ist ausgefallen. Der tatsächliche Uploadversuch einer lokalen Testquittung wurde mit no primary turn environment is available abgewiesen. RDC bleibt erreichbar; eine neue Drive-Sicherung wird daraus nicht behauptet. Delta021 ist der letzte vollständig auf Drive zurückgeprüfte private Stand. Delta022 wird als eigener Archiv-/Restore-/Transfer-Schritt geführt.

[Maschinenlesbarer Nachweis](milestone-a-20261112/a4-build018-native-failure.json). [Sechs A3-Vergleiche](2026-11-12-build018-six-window-comparison.md).
