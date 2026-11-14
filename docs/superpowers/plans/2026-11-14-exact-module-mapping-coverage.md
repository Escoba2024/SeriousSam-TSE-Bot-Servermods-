# Exakte Modulbereichsdeckung statt VMA-Zeilenpartition

> Ausführung mit executing-plans. Root allein Runtime/Integration; zwei getrennte Review-/Implementierungsworktrees. Während nativer Fenster ausschließlich statische Vorbereitung.

**Ziel:** Den konkret gemessenen Fehlalarm durch reine VMA-Aufteilung beheben und weiterhin jede Änderung der abgebildeten Adressen, Rechte, Dateioffsets, Dateiidentität und Dateisignatur erkennen. Keine Frida-Ausnahme, kein Rebaseline nach Attach, keine Toleranzänderung der Gameplay-/ACK-/Schadensprüfungen.

**Befund:** Privater A1-Versuch133108 bleibt FAIL; Ergebnis `d2755f6d65122a3f27dfee577c9539cb7a4224cb1ed6e46eb99209668ac5d239`. Genau eine RX-Region teilt sich in drei lückenlose RX-Regionen mit identischem affinem Dateioffset, Device, Inode und Pfad; alle19übrigen Zeilen unverändert. Der alte Rohzeilenvergleich erkennt Partitionierung, obwohl die gesamte gemessene Bytebereichszuordnung gleich ist. Vollständige Prozessmaps sind archiviert, Cleanup/Restore unabhängig bestanden.

## Aufgaben und Abnahme

- [x] Tatsächlichen Fehler aus denselben vorhandenen Reads privat archivieren; alter FAIL bleibt FAIL.
- [x] Rootdesign auf den belegten Darstellungsfehler begrenzen; kein pauschaler Attach-Freibrief.
- [ ] Kandidat: separat versionierte reine Mappingfunktion entwerfen. Jede Zeile streng parsen, positive sortierte nicht überlappende Intervalle verlangen. Nur unmittelbar benachbarte Intervalle mit identischen Rechten/Device/Inode/Pfad und exakt fortlaufendem Dateioffset zusammenfassen. Normalisierte vollständige Soll-/Istlisten exakt vergleichen. Lücken bleiben erhalten und ungleich; keine Seiten weglassen.
- [ ] RED→GREEN nach Ende des aktiven nativen Fensters: tatsächliche archivierte20/22-Gleichdeckung, identische Listen, andere zulässige Partitionen; fehlender/zusätzlicher Bereich, Überlappung, Umordnung, geänderter Basis/Offset/Rechte/Device/Inode/Pfad sowie ungültige Zeile müssen scheitern. Dateisignatur-/PID-Fehler unverändert testen. Readanzahl bleibt dieselbe.
- [ ] Enger neuer deaktivierter A1-Fork vom unveränderten Rootfreeze `bd83f6e3ad7320e7eed5b9059ec1d107dc295dd60168803eb2cef78f607750ae`: ausschließlich Mappinggleichheit nach exakter Deckung; bestehende private Fehlerquittung für echte Ungleichheit erhalten. Hooks/Input/ABI/ACK/EPS/TTL/Close-/Hostgates unverändert. Kein neuer Herkunfts- oder Dateihashbasisstand.
- [ ] Unabhängiges Code-/Paketreview, gezielte Rootprüfungen, neue Rootcopy mit eigenen Pfaden/Gates, frischer Preflight; genau ein passiver NoFire-Originalversuch. Keine automatische Wiederholung.
- [ ] Native Ergebnis/Originalbytevergleich/Unload/Detach/Workerende/normale Rollencloses/vollständige Schlusslogs und unabhängigen Datei-/Metadatenrestore prüfen. Ein bestandener Mappingvergleich qualifiziert allein keine Gameplaykalibrierung oder A1-Schaden.
- [ ] Falls A3 denselben Fehler besitzt, nach diesem Ergebnis getrennt auf seinen tatsächlichen Backendpfad übertragen und erneut eng prüfen. Keine ungetestete Flottenänderung.

**Reviewfokus:** Nur Zeilengrenzen dürfen sich unterscheiden, die Funktion von virtueller Adresse auf Dateioffset/Rechte/Dateiidentität bleibt exakt gleich. Keine Whitelist, kein Snapshot nach Hook, keine bloße Gesamtgrößengleichheit, keine ignorierten anonymen Ersatzseiten. Alle alten Ergebnisse unverändert lassen. Native Starts ausschließlich Root nach Ende sämtlicher paralleler CPU-Arbeit.
