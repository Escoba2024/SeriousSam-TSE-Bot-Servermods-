# A4: deaktiviertes Build016-Paket für frühe Phaseninventare

## Ergebnis und Abgrenzung

Der separate A4-Beobachtungspfad ist offline fertig geprüft. Die vollständige Regression besteht mit **130/130 Tests**; die Laufzeit betrug 0,731 Sekunden. Das private Paket bleibt mit `RUNTIME_REVIEWED=False` deaktiviert. Diese Übergabe enthält keine Aussage, dass Build016 bereits die native A4-Abnahme bestanden hat. Der bisherige Versuch `a4-reset015-lowrender-readable-20261112-092421` bleibt unverändert FAIL.

Die vorgelagerte C++-Korrektur der eigenen kumulativen Sollwinkel liegt im Worker-Commit `bea377448cd03465b651d2c11059e4e0fda5c790` und wurde von Root als `58e8559903d999772218a6b5fd1d042b1759b547` integriert. Root hat daraus Build016 erstellt. Die Korrektur und ihre Aussagegrenzen sind in `2026-11-12-a4-rotation-epoch-and-observation.md` und `milestone-a-20261111/a4-rotation-epoch-source.json` beschrieben.

## Warum die Beobachtung geändert wurde

Die bisherige Steuerung schloss den alten Reader am normalen Rundenende und eröffnete den neuen erst nach dem vollständigen Rejoin des Original-Observers. Im vorhandenen Versuch begann das native Inventar deshalb erst bei Spielsekunde 19,94998 beziehungsweise 15,10004 der Reloadphasen. Vollständige Phasenlogs enthalten bereits davor echte Waffenaufnahmen und Feuerinputs. Linkszensierter Erstbesitz darf daraus dennoch nicht als beobachteter nativer Inventarzuwachs gewertet werden.

Die neue Steuerung verwendet denselben Original-InventoryReader bereits nach bestätigter frischer Acht-Bot-Phase und vor dem Observer-Start. Während der bestehenden Warteoperationen und der Waiting-Schleife erfasst sie höchstens alle 0,1 Sekunden zwei tatsächliche Vierergruppen. Der Reader bleibt bis zur regulären Neun-Spieler-Phase offen; die spätere Registry muss die früh beobachteten acht Entity-ID/Pointer/World-Tupel bestätigen.

Jede frühe Probe ist an neue CecilLoad-/Level-Bytegrenzen, die tatsächliche Beginfolge 1/2/3, das effektive Zeitlimit 1/1/0, aktuelle Local/Global/Entity-Zuordnung, gepinnte PID-/Start-Tupel und den aktuellen nativen Zeitbereich gebunden. Eine wiederverwendete Entity-ID oder Adresse reicht als Phasennachweis nicht. Der explizite Epochenschlüssel enthält Phase, frische Logoffsets und Serveridentität.

Rohframes werden vor Zuordnungs- oder Fristfehlern separat gespeichert. Die Quittung hält tatsächliche Leseabschlusszeiten und Ablehnungsgründe fest. Ein verspäteter erster Read stoppt bereits den zweiten Read und erhält keine Aktivitätsgutschrift. Die zusätzlichen Kontrollen verwenden den vorhandenen reinen PID-/Startvergleich `B.same`; sämtliche bestehenden vollständigen Unit-/PID-/Modul-/Namespace-Guards bleiben erhalten.

## Unveränderte Abnahme

Die Aktivitätsauswertung bleibt bytegleich. Jeder der acht Bots benötigt in jeder Phase weiterhin Ready, Bewegung, eine Feueraktionszeile, einen echten beobachteten brauchbaren Inventarzuwachs und eine native Fernwaffenfeuerprobe. Ein erster Besitzstand zählt nicht als Pickup. Kumulative Schusszähler oder native Feuerflags erzeugen keine nachträgliche Feueraktionszeile.

Unverändert gelten 300 Sekunden Gesamtkappe, 50 Sekunden Übergang, 19 Sekunden Observer-Schließgrenze, die normale 20-Sekunden-Rundenpause und mindestens 60 Sekunden Wand-/Spielzeit in der letzten aktiven Phase. CPU75, MemAvailable1,5GiB, freier Speicher8GiB, exklusiver Runtime-Lock, normales Schließen, genaue Wiederherstellung und die Prüfung final geschlossener Logs bleiben bestehen.

Diese Messkorrektur erklärt nicht alle bisherigen Aktivitätslücken: Phase-1-A2 protokollierte keine brauchbare Fernwaffenaufnahme; Phase-1-B0 erhielt spät eine Shotgun und erhöhte danach seinen Feuerzähler nicht mehr. Das neue Paket darf solche Befunde weiterhin ablehnen.

## Nachweise

| Prüfung | Ergebnis |
| --- | --- |
| Drei tatsächliche alte Warte-/Startpfade vor der Änderung | 3 echte Assertion-Fehler, keine Importfehler |
| Neuer tatsächlicher Sampler-/Wartepfad einschließlich Fehlerquittungen | 7/7 bestanden |
| Phasenbindung, ID-/World-/Zeitfehler, Zensierung und unveränderte Policy | 10/10 bestanden, zusätzliche Negativvarianten |
| Erste vollständige Suite | 129/130; einzige Abweichung war die alte Reader-Ortsassertion im Test |
| Endgültige vollständige Suite | 130/130 bestanden, 0,731s, Exit0 |
| Alte Parentquellen | 79 von82 bytegleich |
| Alte Runtimeabhängigkeiten | alle59 erneut geprüft |
| Neues Paket | 111 gepinnte Dateien, 64 gepinnte Runtimeabhängigkeiten |

Die dritte geänderte Parentdatei ist ausschließlich `test_mapreset.py`: Der Test erwartet den Reader nicht mehr direkt im While-Block, sondern prüft den dortigen Helper-Aufruf und die echte `inventory=InventoryReader(...)`-Zuweisung im Helper. Alle anderen Assertions sind exakt erhalten. Elf vorhandene Lifecycle-/Evidenzfunktionen und der komplette bisherige Präfix von `operation_guard` sind im AST unverändert. Der Adapter unterscheidet sich nur im exakten Kandidat-SHA.

## Endgültige Pins

Privates deaktiviertes Paket: `/srv/tse-a4-phase-inventory-completion-20261112`.

| Gegenstand | SHA-256 |
| --- | --- |
| Finales GateFalse-Manifest | 40abb08ff7fab1f71b0bf9359161c7d258fb26fdfffb3b1c3baf2925f3ded093 |
| Controller | bbe3a481bb3ac94e13e4e7a262db03d42fe8be48d4319213dc4ca986b8d9c789 |
| PhaseInventory-Helper | 2ea407070b15ed8ed94a765c7bccfb6510805d0b89676ba774a4452eb4e15b73 |
| Normalisierter Delta-Receipt | 0bd4095caa9825253434a75bb39fa9419b8762dfa58f2ee77cbbee428f2c6a88 |
| Build016-Manifest | 4cd6b5a8d853afe2dbe492fb12fff0aed22a06c77b5de7fc4e732795d2676603 |
| Build016-DLL | e5a80634b5247c900ae25b5b18869c433c30dcfb49b890338fb231da63b04825 |
| Gepinnte Parentbasis | f69bb4a0122f184e4aa2b3416e79349eb85731f3d9bd06de118845d05c19600d |

Der letzte Manifestabgleich erfolgte erst nach normalem Close/Restore des parallel von Root geführten A1-Versuches, damit absichtliche temporäre Fixtureänderungen nicht als Pinabweichung bewertet werden. Produktionscode und Tests blieben während der abschließenden Dokumentationsquittungen unverändert.

Vollständige private Unterlagen: `EARLY-INVENTORY-REVIEW.md`, `early-inventory-offline-receipt.json`, `early-inventory-delta.json`, `early-inventory-controller.diff`, `source-manifest.json`. Die Ergebnisse und Pins wurden von Root mit direkten erlaubten Offline-Aufrufen erhoben; der Worker änderte keine gefrorene Parentbasis, keinen alten Versuch und keine Livekonfiguration.

## Nächster Root-Schritt

Root prüft das finale Manifest, friert seine eigene Runtime-Kopie ein und führt den separat benannten `a4-reset016-early-inventory-...`-Versuch nacheinander unter dem bestehenden Lock aus. Zuerst sind die neuen `BotRotationBaseline`-Zeilen je neuer Map-/Entity-Grenze sowie die frühe, korrekt gebundene Inventardeckung zu prüfen. Ein normaler Respawn darf seine kumulative native Basis behalten. Es folgt die unveränderte Aktivitätsabnahme aller acht Bots je Phase einschließlich normalem Close und genauer Wiederherstellung. Fehlende Teilnachweise bleiben FAIL; ein neuer nativer Erfolg wird erst anhand dieses neuen Laufes behauptet.
