# A3: vollständige Schadensrecords und partielle Lebensbeobachtungen trennen

> Nur Plan, keine Implementierung oder Ausführung. Spätere Umsetzung mit executing-plans/TDD im eigenen Worktree, Root allein Runtime. Der historische Analyzer und sein FAIL bleiben unverändert.

**Ziel:** Bereits vollständig aufgezeichnete 120-Sekunden-Schadensrecords streng prüfen und nutzbar dokumentieren, auch wenn eine Inventar-/Clientlog-Lebensmenge am Beobachtungsende unvollständig ist. Keine A3-Abnahme, keine erfundenen Lebensdaten und keine pauschale Wiederholung nativer Fenster wegen einer unbewiesenen Mengengleichheit.

**Ausgang:** Diagnose `4b7ebb4e8c90a288d9638ff300447236e3349718`, integriert Root `e77180f`. Swap1-Result `b0562be36a881553e25fcbd8199dd6f40ab6935722acf971f3d77a4b211191d8`: botA/local1 drei Inventarleben gegen vier Source-Spawns. Ein zusätzlicher offener Source-Lebenssuffix ist protokolliert, aber weder dessen Server-Spawnclock noch seine genaue Wallzuordnung sind aufgezeichnet. Die 207 vorhandenen Damage-Records haben konsistente Lebens-/Tick-/Sequenz-/Registrybindung; dies ersetzt noch nicht den vollständigen geschlossenen Schadens-/Serverkillvalidator. Alter Analyzer scheitert unverändert an Zeile70.

## Architektur und Wiederverwendung

Ein **neuer rein offline arbeitender Komponenten-Auditor** erzeugt einen ausdrücklich typisierten Diagnosebericht. Er wird weder in den nativen Controller noch in den bestehenden vollständigen Vergleich eingeschleust. Keine Runtime-/Observeränderung ist hierfür notwendig.

Der eingefrorene `analyze-direct020.py` ist monolithisch: sein `analyze()` kann die vollständigen Damageprüfungen nicht zurückgeben, ohne zuerst die strikte Lebensanzahlassertion auszuführen. Den Fehler zu fangen und anschließend einen Legacy-PASS-Bericht zu bauen wäre eine Umgehung. Stattdessen wird bei der späteren Umsetzung ein kleiner neuer Adapter aus **unveränderten Prüfblöcken** erstellt; der alte Analyzer bleibt bytegleich. Ein Offlinebuilder pinnt die historische Quelle, extrahiert nur eindeutig benannte Blöcke und setzt explizite Funktionsgrenzen/Returns hinzu. Keine dynamische Ausführung aus Logtext, keine beliebigen Quellfragmente oder Callerparameter. Tests müssen normalisierte AST-Gleichheit der übernommenen Prüfkörper gegen die gepinnte Quelle belegen; nur Einrückung, Funktionssignatur und Rückgabe dürfen neu sein. Falls diese Extraktion wegen versteckter Abhängigkeiten nicht genau belegbar ist, stoppt die Umsetzung vor einer Ersatzimplementierung und meldet den konkreten Blocker.

Verbindliche historische Pins unter `/srv/tse-a3-instruction-probe-root-frozen-20261114`:

| Datei | SHA256 |
|---|---|
| analyze-direct020.py | `4187020d0ceda1284bcaac3df9ccf98b251ec25863ae6947bd0aa6d96d33464a` |
| a3_compare_direct_closed.py | `9ae3a274077e85af0dfcedbf035d2a2216ac6027fc85d99d4f085cadd9a98871` |
| a3_direct_controller_policy.py | `6d2334c15fe504d8dbcb4921f5583d87ce4e05492a1e328625897a64094a0ed2` |
| stability_hard_rules.py | `9e255659101eee27b6d4dcf285129a52488db29cab021ff380c290f2d34d7472` |

Die unabhängig wiederverwendbaren Blöcke und ihre Eingaben:

1. **Geschlossener Beleg und Bedingungen** (`analyze-direct020.py:10–46` plus unveränderte Initialfinish-/Referenzprüfungen): fertiger fehlerfreier Nativebericht; vier normale Closes; tatsächliche Schlussloggrößen/-hashes und Fehlersuche; Hard2 in allen Session-/Querybelegen; tatsächliche Slots/Neunerbelegung und privat stabile Namen; reproduzierte Kohortenconfigs und tatsächlich geladene Tiers; endgültige Launch-/Cleanupidentitäten, Originalmodule und Server-PID in allen Inventarhüllen; Registry-/Pointer-/Slot-/Kohortenzuordnung; strikte Initialbeobachtungen, exakte Referenzplatzierungen und gemeinsamer erster Spawnclock. Alle vorhandenen Anforderungen bleiben bestehen. Das ist unabhängig von der Anzahl später beobachteter Leben.
2. **Vollständiger Schadensstrom** (ab `f=R['frida_damage']` bis einschließlich `assert killpairs==lethal`): exakt alle Records und Nenner, durchgehende Sequenzen, gleicher gebundener TID, kein Nested/Unknown-Victim/Fault/Drop/InFlight, keine Detachfehler; volle Windowüberdeckung und Originalbyte-Restore; korrekte Vorher-/Nachher-Spawnclock/Tick/Pointer und endliche Werte; unveränderte Zeitfenstergrenzen und Attribution. Außerhalb/überkreuzend, Corpse, Self, Unattributed und Known-Foreign bleiben getrennt; nichts wird übertragen. Unveränderte HP-/Armor-/Lethalberechnung, Damage-attribution-Gegencheck sowie exakter Serverkillpaar-Gegencheck. Diese Auswertung verwendet keine `lives`-Statistik.
3. **Host/Provenienz**: unveränderte Ressourcenverletzungsprüfung, vorhandene Kostenkennzahlen ohne kausale Overheadbehauptung; Hashes aller verarbeiteten Dateien und gleiche Kandidaten-/Original-/Config-/Initial-/Welt-/Nav-/Controller-/Worker-/Hookbedingungen. Eine vollständige Damageprüfung ersetzt keine fehlenden Restore-, Initial- oder Konfigurationsnachweise.

Der temporäre Name dieser neuen Quellgrenzen wäre `a3_closed_damage_components.py` mit kleinem `audit_a3_closed_damage_partial.py`. Keine Änderung von `analyze-direct020.py`, `a3_compare_direct_closed.py`, Controller, Hook, Intervallen, Gates oder historischen Ergebnissen.

## Partielle Inventar-/Lebensauswertung: enger eigener Vertrag

Alle Inventarhüllen und vorhandenen Rows werden weiterhin geprüft und erhalten. Keine Auswahl günstiger Samples, kein Tailabschneiden und kein Hinzufügen synthetischer Rows. Das bestehende Gruppieren tatsächlicher Beobachtungen nach Slot/Entität/Spawnclock bleibt als **Memorybeobachtung** bezeichnet; daraus entsteht kein vollständiger Source-Lebenszähler.

Die neue Teilprüfung liefert einen eigenen Abgleichbeleg, bevor sie überhaupt `PARTIAL_INVENTORY_REPORT` zulässt:

- Vollständiges Source-Ereignisprotokoll je tatsächlichem PID/local: gleiche Entität, nicht fallende Driver-Ticks mit eindeutiger Logzeilenreihenfolge, monotone Generationen sowie konsistente Spawn-/Death-/Statezähler; keine ausgelassenen oder doppelten inneren Generationen, widersprüchlichen Übergänge oder unerklärten Resets. Startgeneration darf einen beliebigen belegten Baselinewert haben. Alle vorhandenen Sourceereignisse bleiben sichtbar.
- Vorhandene Memoryleben: gleiche geprüfte Entität, positive strikt voranschreitende Spawnclocks; kein Wiedererscheinen einer älteren Lebensclock; tatsächliche Alive-/Death-/Pickupbeobachtungen und links-/rechtszensierte Eigenschaften bewahren. Native SameLife-Records bleiben an ihrem tatsächlichen Server-Spawnclock, nicht an einer nachträglich geratenen Sourcegeneration.
- Bereits gemeinsame vollständige Lebensprefixe müssen die bisherigen Entity-, Deathanzahl- und booleschen UsefulPickupprüfungen unverändert erfüllen. Der Abgleich erhält seine vollständigen Zeilen-/Clock-/Zählerzeugen. Ein bloßes `zip()` bis `min(len(...))`, gelockertes `<=` oder Ignorieren aller zusätzlichen Spawns ist verboten.
- Der **einzige eng zulässige partielle Sonderfall** ist ein einzelner zusätzlicher letzter Source-Spawn je betroffenem local, nach dem vollständigen gemeinsamen Prefix. Der letzte beobachtete Memorylebensdatensatz muss bereits seinen Tod zeigen; sämtliche abgeschlossenen Source-Lebenszyklen müssen vollständig und in derselben Reihenfolge abgebildet sein. Der zusätzliche Sourcezyklus hat keinen späteren Source-Tod und keine weitere Generation. Ein ausgelassener abgeschlossener innerer Zyklus, ein unpassender Death-/Pickupzähler, ein Entity-/Slotwechsel oder mehrere nicht zuordenbare Suffixzyklen bleibt FAIL.
- Die Umsetzung muss diese Zuordnung als eindeutigen strukturellen Abgleich mit allen Zählerzeugen zeigen. Lassen die realen Daten mehr als eine Lebenszuordnung zu oder lässt sich eine innere Lücke nicht ausschließen, lautet die Inventarkomponente `FAIL_INVENTORY_RECONCILIATION`; der Gesamtdiagnosebericht bleibt FAIL und behauptet keine erfolgreiche Teilrekonstruktion. Vollständige Damagekomponenten dürfen dabei als separat geprüfte Tatsachen erhalten bleiben.
- Das unbeobachtete Sourceleben wird als `UNKNOWN_UNOBSERVED_SOURCE_LIFE` ausgegeben: Rolle/local, Sourcegeneration/-zeile/-Driver-Tick und gegebenenfalls ausdrücklich clientseitiger Nativeclock; Server-Spawnclock, Windowmitgliedschaft, Versorgung, Überlebenszeit und outcome bleiben `null/UNKNOWN`. Es wird weder als außerhalb des Fensters noch als versorgt/fehlversorgt klassifiziert und nimmt an keinem Life-/Versorgungsnenner teil. Keine Umrechnung Clientclock→Wallclock oder neue Ticktoleranz.
- Alle negativen bekannten Inventarbelege bleiben erhalten. Insbesondere bleiben die beiden tatsächlich beobachteten abgeschlossenen local1-Leben ohne brauchbaren Waffenbesitz negativ. Unbekanntes wird nicht mit Null oder Erfolg aufgefüllt. Es werden keine vollständigen kohortenweiten Versorgungsquoten behauptet.

Der enge Suffixvertrag soll den vorhandenen Fall beschreiben, kein allgemeines Missing-Sample-Reparaturverfahren werden. Neue Fälle werden nicht automatisch in diesen Vertrag aufgenommen.

## Berichtstyp und Schutz gegen versehentliche Annahme

Neuer Bericht hat eine eigene Schema-/Typkennung, top-level `status=PARTIAL_INVENTORY_REPORT` nur bei bestandenen gemeinsamen Voraussetzungen, vollständigem Damageblock und bewiesenem engen Source-Suffixfall. Bei sonstiger Inkonsistenz FAIL mit genauer Ursache. Pflichtfelder: `qualified=false`, `a3_accepted=false`, `tier_strength_accepted=false`, `closed_compare_eligible=false`, `runtime_performed_by_this_audit=false`. Die ursprünglichen Nativebedingungen und ihr Status bleiben separat als unveränderte Provenienz sichtbar.

Getrennte Namespaces `damage_component` und `inventory_component`; keine Legacy-Top-Levelstruktur `damage`, `cohorts/lives`, `direct_condition_sha256` oder `closed_complete`, die der bestehende vollständige Vergleich als seinen eigenen zurückgegebenen Report übernehmen könnte. Der existierende `compare_reports` darf solche Komponentenberichte nicht akzeptieren; dies wird ohne Änderung seines Validators als Negativfall geprüft. Kein Eintrag in die bisherigen vollständigen Vergleichsdateien, kein Überschreiben der fehlgeschlagenen Ausgabe. Alle Quellen, Nenner, Unknowns und Abdeckungsgrenzen stehen im neuen Artefakt.

Die vollständigen Damagepartitionen und Matrizen dürfen für die zwei schon geschlossenen Swapbedingungen nebeneinander dokumentiert werden, sofern jede identische Bedingung und jeder zugehörige Validator wirklich geprüft ist. Das ist eine begrenzte Schadensbeobachtung ohne Stärkefreigabe, ohne vollständige Waffenversorgungsbilanz und ohne menschliches Niveau-/Stabilitätsurteil. Ausführbare Vergleiche bleiben vom bestehenden vollständigen Vergleich getrennt.

## Umsetzungsaufgaben und Abnahme nach Rootreview

- [x] Abhängigkeiten des alten monolithischen Analyzers statisch prüfen; getrennte Damageprüfung benötigt keine Lebensanzahl.
- [x] Altes FAIL, konkrete Unknown-Grenze und nicht austauschbaren Berichtstyp festlegen.
- [ ] Rootreview dieses Plans; keine Implementierung davor.
- [ ] Neuer isolierter Worktree/Claim. RED: aktuelles Swap1-Archiv kann noch keinen neuen typisierten Komponentenbericht erzeugen; alter Analyzerfehler bleibt erwarteter historischer Befund, kein Test-PASS-Ersatz.
- [ ] Gepinnte unveränderte Prüfblöcke ableiten, statische AST-/Provenienzgleichheit belegen; explizite Eingaben statt versteckter Globals. Bei nicht belegbarer Blockgleichheit stoppen.
- [ ] Minimalen partiellen Abgleich und getrenntes Berichtsschema implementieren. RED→GREEN mit echten kleinen anonymisierten Lebens-/Source-Fixtures für exakten Suffixfall; Gegenfälle für innere fehlende Leben, Sourcegenerationloch, zusätzliche Deaths/Spawns, wechselnde Entität/Slots/PID, fehlende Initial-/Config-/Restorebelege, Zeitfenster-/Damage-/Lethal-/Serverkillabweichungen bleiben FAIL. Der Unknownspawn darf niemals in einen Versorgungsnenner gelangen.
- [ ] Relevante vorhandene strikte Damage-/Kohorten-/Controllerprüfungen sowie neue Fälle gezielt ausführen. Negative Übergabe eines Komponentenberichts an den vorhandenen Vollvergleich muss scheitern. Keine Runtime/Frida/neue Nativefenster.
- [ ] Vorhandene geschlossene Swap0-/Swap1-Archive nur offline neu auditieren, Hashes/Deltas/Nenner/Unknowns dokumentieren und unabhängig reviewen. Ergebnis aus jeder Komponente exakt berichten; alte FAILs nicht überschreiben.
- [ ] Commit/Push durch Root und bereinigter Handoff. Erst dann beurteilt Root, welcher tatsächlich fehlende A3-Beleg eine prospektive Ergänzung erfordert.

## Falls der enge vorhandene Lebensabgleich nicht beweisbar ist

Kein Rückschluss aus einem erfolgreich geprüften Damageblock auf eine vollständige Lebensstatistik. Ein konkret begrenzter prospektiver Plan müsste dann pro tatsächlich vorhandener Sample-/Source-Epoche gemeinsame Grenzquittungen und letzte Messversuche aufzeichnen, ohne die Gameplaydauer oder bestehenden Abnahmekriterien zu lockern. Zusätzliche Reads/Hooks/Instrumentierung dürften erst nach eigenem Kosten-/ABI-/Cleanupreview erfolgen. Er wäre auf die fehlende Lebensgrenze zu beschränken; bereits vollständig belegte Native-Damagerecords verlieren dadurch nicht ihren Datenwert. Eine automatische Wiederholung aller abgeschlossenen nativen Fenster ist kein Bestandteil dieses Plans.

**Aktueller Handoff:** Nur diese Plan-/Berichtdatei; keine Quelländerung, kein Testlauf, keine native Aktion und keine weitere Agentendelegation. Root-Handoff und bestehende Belege bleiben unverändert.
