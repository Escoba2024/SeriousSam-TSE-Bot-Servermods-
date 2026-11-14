# A4 gesperrter Ausgangsanker: SDK107-Reproplan

> executing-plans/systematic-debugging/TDD; reine Reproduktion vor Fixentscheidung.

**Goal:** Den nach not_usable gesperrten und außerhalbRadius stehenden
Ausgangsanker mit echten Produktionskörpern im SDK107-Harness reproduzieren.
**Architecture:** Tatsächlicher BotSupplyTick erreicht Important138, ruft
BotCecilImportant→FinishImportant(not_usable); anschließende gewöhnliche
Armor260/Nav182-Steuerung läuft über echte Locks/Navigator. Originaler direkter
Link138→182 und Metadaten bleiben erhalten. Keine Algorithmusnachbildung.
**Tech Stack:** bestehende SDK107-Brücke, portables C++14; keine DLL/Runtime.
**Spec:** Rootauftrag nach geschlossenem022-Healthreview36137adb.

## Grenzen

- EigenerWT abf9fc13a; nur neueFixture im vorhandenen SDK107-Test und eigener
  Plan/Claim/Bericht. BotSupplyNative/cecil_motion/BotDriver read-only.
- Root allein Runtime/Integration; keine neuen Agenten, keine nativen Prozesse.
- Bestehende Arrival/LOS/Floor/blocked-Regeln nicht verändern/lockern.
- Tatsächlicher022-Beleg: tick968 not_usable138, avoid10Policysekunden,
  Source138 draußen4.87m>r2, späterOrdinary182/Armor260,hop−1/neutral.
- Repro zuerst RED mit Kontrollen: ursprünglicher Radius erlaubt blockierten
  Ursprungs-Austritt; Ablauf der10s stellt Route wieder her; echter blockierter
  Zielknoten/physische Safety bleiben Veto. Kein Healthregressionsclaim.

## Schritte

- [x] Echte sequenzielle Fixture in test_cecil_native_bridge.py ergänzen;
  193Slots, relevante Originalpunkte138/182, direkter Link138→182, Itemtypen.
- [x] Bestehenden tatsächlichen SDK107-Gesamtharness ausführen und RED exakt
  zählen; Produktionspins unverändert nachweisen.
- [x] Bereinigten Ursachen-/Grenzenbericht und private Log-/Hashquittung
  committen. Keine Produktionsimplementierung vor Rootreview des RED.

Ergebnis3115/2erwarteteRED, alleKontrollenGREEN; Rootreview desRED/
Produktionsfix bleibt ausstehend. Produktion unverändert.
