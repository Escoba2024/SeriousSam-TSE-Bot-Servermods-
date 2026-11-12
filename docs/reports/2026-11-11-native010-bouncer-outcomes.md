# Native010: zwei echte8→12-Launches, ein Minigunerwerb,11→12 weiter fehlerhaft

Das abgeschlossene eigene Fenster `arena010hook2-checked-swap1-trial-1-232802` liefert einen funktionalen8→12-Nachweis, jedoch keine allgemeine Bouncer-/A3-Abnahme. In120,079877s wurden zwei tatsächliche234-Aufrufe der Kandidaten beobachtet; einer führt zur Minigun, der andere endet nach ursprünglichem Zieltimeout ohne Minigun. Der zuvor unvollständig erfasste11→12-Fehlanflug enthält jetzt seine wirkliche UP-Ausgabe.

[JSON-Beilage mit allen Leben,240 Diagnoseaktionen, Hook- und FlightFinish-Ereignissen](2026-11-11-native010-bouncer-outcomes.json). Alle vier Prozesse normal geschlossen, errors leer, jeweils0 SYNCBAD/Disconnect. Hook:41 Gesamtaufrufe,39 andere Pads,2 passende234-Aufrufe,0 unzugeordnete Spieler/Fehler/Verluste; vollständige120077,7ms-Listenerüberdeckung, Detach und Originalkörperrestaurierung belegt. Listenerüberdeckung bleibt vom Beweis vollständiger Spielereigniserfassung getrennt.

## Identität und Zeitbasis

Kandidat010 ist physisch botA, lokale0/1/2/3 entsprechen tatsächlichen globalen Slots0/2/3/4 und Entity-IDs565/566/567/568. Vergleichskohorte botB ist048, Slots5–8/IDs569–572. Vanilla563 ist Slot1. Die tatsächlichen Attachmeldungen wurden mit nativen Inventar-IDs verbunden, nicht mit Messgruppenlabels. Alle15/13 nativen Botleben stimmen je lokalem Spieler mit den jeweiligen CecilSpawn-Ereignissen überein.

Client-Ticks kennzeichnen Aktionen und sind **keine allgemeine Wanduhr**. Lebens-/Erwerbsalter stammen aus nativem `game_tick - spawned_tick`; Hookzeiten aus dem erfassten Hostzeitfenster. Erste Inventarproben liegen0,60–0,65s nach dem gemeinsamen Erstspawn0,9500002s: hieraus wird kein erster Simulationszustand oder exakter gleicher Startort behauptet.

## Drei konkret abgegrenzte Anflüge

| Kandidatenleben/Anflug | Beleg | Ergebnis |
|---|---|---|
|local2/g7, Entity567, früher11→12|Tick1025: tatsächliches10→11 erreicht, neuerHop12, Roh-UP1/finaleUP11 mit Support194;1026Support0/vY16,826;1031 bereits12→34 in der Luft (Log948–955)|Kein234-Aufruf dieses Anflugs. Die späteren Calls gehören ausdrücklich zum späteren Wiederanflug.|
|Dasselbe Leben567/g7, später8→12|Periodische Route6→7→8 bei1400/1420/1440, Source8/Hop12/Support193 bei1460 (Log1357–1383); echter234-Hook bei62,858545s Hostfensterzeit|Launch nach oben, aber Ziel243 endet1479mit unveränderter Deadline als timeout. Keine Minigun dieses Lebens.|
|local1/g7, Entity566,8→12|1484Roh-UP1/final0/Support54;1489erneuterRoh-UP1/final0 bei Support0;1494erneutfinal0/Support193. Echter234-Hook bei64,453545s.|Erfolgreicher Anflug und Minigun3→67 bei1587 (Log1555).|

Beide234-Aufrufe verändern die Velocity unmittelbar im Originalfunktionskörper:567 von[-17,5493;0;−0,1571] auf[53,0754;73,1982;−77,2305],566 von[−14,6194;0;−0,7991] auf[53,0762;73,1990;−77,2289]. Vorheriger Support ist jeweils193, danach null. Das ist ein tatsächlicher Launchbeleg, nicht aus einem NAV-Flag erschlossen.

Native Inventarproben begrenzen567s Launch zwischen Spieltick64,349327 (vY0/Support vorhanden) und64,499336 (vY71,698/Support0), bei gleichem Spawn34,199764.566 ist bei65,899422 noch unterstützt/vY0 und bei66,049431 bereits vY73,199/Support0, Spawn32,999783. Die Hostzeit der jeweiligen Inventarzeile ist Schleifenbeginn; sie darf nicht millisekundengenau als Zeitpunkt jedes späteren Einzelreads verwendet werden.

## Waffenaufnahme und FlightFinish strikt getrennt

566/g7 erhält die Minigun erstmals nativ bei70,549706, Lebensalter37,549923s, Owned67. Sein erhaltenes Ziel bleibt während dieses Fluges aktiv; ein FlightFinish für12→34 wird nicht protokolliert. Das ist kein fehlender Nachweis, der durch einen anderen FlightFinish ersetzt werden darf.

567/g7 hat nach dem Launch ursprünglichen Zieltimeout1479 und anschließend keinen aktiven Minigunpfad; die periodischen Zustände1480/1540/1560 zeigen den Flug/Fall ohne Ziel, bevor1579 ein anderes Ziel267 aufgenommen wird. Sein erster nützlicher Erwerb ist erst die Laserwaffe: Owned2051 bei nativ78,400185, Lebensalter44,200420s, CecilPickup1744. **Der FlightFinish1744–1749 gehört86→176 zu dieser späteren Laseraufnahme**, nicht zum234-Launch oder zu einer Minigun. Die ursprüngliche Deadline105,371 bleibt dabei erhalten, Ende `arrived`.

Die protokollierten FlightFinish-Paare insgesamt: local3 560–572/86→176/arrived; local2 1744–1749/86→176/arrived; local0 2362–2368/44→43/context. Dies sind drei Paare, sechs Ereignisse; keiner darf als zweiter erfolgreicher Minigunflug gezählt werden.

## Vollständiger Lebensnenner

| Kohorte | Leben | Nützliche Waffe erworben | Ohne Erwerb gestorben | Ohne Erwerb am Ende lebend | Erfolgs-only Median |
|---|---:|---:|---:|---:|---:|
|010|15|12|2|1|8,425s|
|048|13|10|2|1|3,875s|

Nützlich ist Maske0x3df8; Erwerb bedeutet erstmals lebend beobachteter Besitz, kein Treffer/Schuss. Alle Lebensenden haben direkte gleichlebige Todesproben; keine Enden nur aus Folgespawn erschlossen. Die zensierten Fälle sind010/local0 mindestens2,150s und048/local3 mindestens9,601s alt. Vanilla besitzt ein eigenes, ausgeschlossenes Leben ohne Erwerb. Vollständige Daten einschließlich getrenntem ausgewähltem nützlichem Waffenzustand mit Ammo stehen im JSON. Die Erfolgsmediane allein beweisen weder generelle Überlegenheit noch Nichtregression; dieses instrumentierte kurze Fenster ist keine finale Tiervergleichsserie.

## Enger nächster Änderungsspielraum

Für11→12 ist jetzt das gleiche konkrete Problem vollständig genug eingegrenzt: eine normale positive UP-Ausgabe noch auf unterstützter Anfahrt, anschließender gewöhnlicher Aufstieg und zu hohe12→34-Ankunft ohne234-Aufruf. Eine Erweiterung der vorhandenen UP-Unterdrückung auf ausschließlich die verifizierte gerichtete11→12-Kante ist damit testbar. Sie muss deren originale Metadaten/Links/Blockierung zusätzlich binden und die bestehenden Welt/Nav/Serial-/STAND/CROUCH-Grenzen bewahren. Radius, Flags, Sprungclock, Deadlines und Flugsteuerung sind durch diesen Befund nicht zur Änderung freigegeben. Diese Auswertung verändert weder Source noch Runtime; ein011-Fix und dessen native Abnahme bleiben eigenständige Schritte.
