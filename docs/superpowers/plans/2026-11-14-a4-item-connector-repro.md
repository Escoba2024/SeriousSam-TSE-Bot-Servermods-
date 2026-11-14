# A4 Itemconnector: SDK107-Reproduktion

> Required execution: superpowers:executing-plans, systematic-debugging und TDD.
> Keine Delegation. Root allein integriert und verändert native/live Runtime.

**Goal:** Einen über mehrere echte BotSupplyTick-Aufrufe unterbrochenen
Itemconnector beim Verlassen der2mNav-Zielsphäre nachweisen oder widerlegen.
**Architecture:** Vorhandenen portablen SDK107-Bridgeharness unverändert als
Ausführungsweg benutzen. Nur eine neue gezielte Testfixture ergänzen; der echte
BotSupplyNative.h-/CecilNavigatorcode bleibt unverändert. Nativebelege liefern
die Hypothese, keine automatische kausale Laufzeitqualifikation.
**Tech Stack:** Python, g++ C++14, echte Produktionskörper mit vorhandenen
deterministischen Entity-/Raystubs, SDK107 Player.es-/Brush-/Raykonstanten.
**Spec:** Rootauftrag auf3c0a0c2; geschlossener20FPS020Arm
nav20-020-root-redstation-20261114-191457 und private Peerdiagnose.

## Grenzen und Reviewfokus

- Kein DLL-Build, Spiel, Wine, Frida, Capture, Display, Livechange oder Fix.
- BotSupplyNative.h und bestehende Produktionsdateien bleiben bytegleich.
- Nur eigener WT/Claim, neue Plan-/Reportdatei und gezielte Harnessfixture.
- NativeunavailableReason ist bei Diagnostics0 unbekannt; keine Behauptung,
  dass der Connectorbefund allein die45.739s ohne Useful erklärt.
- Health ist nicht durch den020Weaponterminalwatchdog abgedeckt.
- Nur echte Productionupdates zählen; keine Algorithmusnachbildung und kein
  fiktiver Pickup. Positionen sind kontrollierte Testeingaben, keine Simulation.
- Health/Weapon, Coldstart/Special, fehlende Rays, Death/World/Reset bleiben
  getrennte Grenzen; keine neue Movementfreigabe oder gelockerte Gates.
- Root STATICONLY stoppt alle eigenen Tests/Compiler/Reader/Gitvorgänge.

## Aufgabe1: Baseline und Hypothese

- [x] Bestehenden Harness/Produktionskörper, Navigationarrivalsphäre und
  geschlossene relevante Slot-/Goal-/Zeit-/Positionbelege lesen/pinnen.
- [x] Bestehenden SDK107-Bridgeharness laufen lassen; Baselinecounts und
  SHA256 von SDK/Produktionskörper privat belegen.
- [x] Eine schrittweise Testfixture im bestehenden Harness ergänzen:
  Livehealthziel5–6m vom Navpunkt, Player zunächst innerhalb2m, danach weiter
  zum Item außerhalb2m; echte BotSupplyTick-Ausgaben in jedem Schritt prüfen.
- [x] RED muss eine tatsächlich wieder zum Navpunkt gerichtete Bewegung
  aus aktuellem Produktionscode zeigen, nicht fehlende Symbole/Fixturefehler.
- [x] Vergleichsfälle für bestehende naheItem-/Kaltstart-/Spezial-/Resetgrenzen
  aus Parent benennen; keine Erwartung zum Grünfärben ändern.

## Aufgabe2: Diagnosehandoff, kein Produktionsfix

- [x] Bereinigter Bericht mit exakten Commands, RED-Ausgaben, Quellzeilen,
  getesteten Vorbedingungen, Unterschied Fixture/Native und engem Fixentwurf.
- [x] Private Hash-/Testquittung; keine Rohspieleridentitäten/retailbytes im Git.
- [x] Tests/Fixtures/Plan/Bericht committen; Root erhält SHA/Status/Jobabschluss.
- [ ] Erst Root entscheidet anhand RED über einen späteren Produktionsfix.

## Aktueller Abschluss

Baseline2920/0PASS; neuerTest2942/6erwarteteFAIL (beideHealthrichtungen),
keinProduktionsfix. PrivateQuittung und bereinigterBericht erstellt.
Rootentscheidung zum vorgeschlagenen Phasenzustand bleibt offen.
