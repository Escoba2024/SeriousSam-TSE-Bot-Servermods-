# A4 Healthconnector-Kontinuität

> Ausführung durch a4_diagnosis mit executing-plans/TDD/systematic-debugging.
> Rootauftrag: nach echtem RED6b38b8 fortsetzen, keine weitere Nutzerrunde.

**Goal:** Ausschließlich gewöhnliche Healthconnector nach tatsächlicher
Navankunft über nachfolgende Ticks bis zum bestehenden Ende fortsetzen.
**Architecture:** Kleiner ausschließlich lokaler Phasenzustand in
SSupplyState, an vollständigen Versuch und echten Navigatorresetstand gebunden.
Bestehenden Itemread-/Typedneed-/LOS-/Geometrie-/Ray-/Safetyweg wiederverwenden.
Ein rein beobachtender Navigator-Resetserial bindet auch direkte/interne Resets.
**Tech Stack:** C++14, tatsächliche Produktionskörper im vorhandenen SDK107-
Bridgeharness, portable g++- und ASan/UBSan-Verifikation.
**Spec:** Rootfortsetzungsauftrag und
docs/reports/2026-11-14-a4-item-connector-sdk107-repro.md.

## Verbindliche Grenzen

- Keine DLL-, Wine-/Spiel-/Frida-/Display-/Liveausführung oder Delegation.
- Root allein Integration/Native; STATICONLY stoppt sämtliche eigenen Jobs.
- Vorhandenes RED2942/6 und private Quittung bleiben erhalten.
- Nur Health, Stand/Crouch, gewöhnlicher offener Terminal ohne Flags,
  Important/Lock/Nextchain/Follow/Flight/Liquid oder anderen Bewegungseigentümer.
- Phase nur nach echter move.arrived-Ankunft UND aktuellem erfolgreichen
  bestehenden Connectorcast; kein Coldshortcut, keine synthetische Ankunft.
- Fullbinding World/Map/Player/Generation/Item/Navziel/Goalstart/rawDeadline/
  effektiveDeadline/Gravity/Resetserial; Contextwechsel/Reset/Relocation/
  Timeback/Death/Goalende löschen die Phase. Aktuelle Navmetadaten erneut prüfen.
- Gewöhnliche12sDeadline,30sBackoff,8m/3mConnectorgrenzen und letzte2Reserve-
  Rays bleiben exakt. Budget<=2 neutral ohne Cast/Reject/Timerverlängerung.
- Kontinuierter Connector außerhalbNavradius löscht currentNavPoint-Stempel:
  kein neuer Floorbypass; vorhandene physische Safety bleibt maßgeblich.
- Weaponverhalten/-Watchdog bleibt unverändert. Quellenbegrenzung und
  tatsächliche Healthreceipts/Weapon-unavailable-Ursache bleiben nativ offen.

## Reviewfokus

1. Warme Phase darf aus Keeper-/Cold-/Hopzustand allein nicht entstehen.
2. Wieder verwendete IDs, World-/Map-/Life-/Goal-/Clock-/Gravity-/Resetwechsel
   dürfen kein altes Ziel fortsetzen; bei Rückkehr des Kontextes kein Wiederaufleben.
3. Rays/LOS/Höhe/Distanz und Timer dürfen außerhalbNavsphäre nicht umgehen werden.
4. Navstuck/-relocation/Special/Follow/Important/Use/Liquid und fremde
   Movementownership dürfen keine Healthfortsetzung erhalten.
5. Telemetrie unterscheidet frische Connectorproposal von Navtravel und
   tatsächlichem Pickup/Ankunft; opt-inFloor und Wall bleiben echte Vetoes.

## Task1: Vorher echte adversariale Tests

Datei: poc/candidates/redstation-supply-20261107/test_cecil_native_bridge.py.

- [x] Neue echte BotSupplyTick-Fixture vorbereitet aus erfolgreichem tatsächlichen
  arrived-Connector; danach warme Fortsetzung außerhalbRadius verlangen.
- [x] Context-/Reset-/Cold-/Special-/Budget-/Geometrie-/Deadline-/Typedneed-
  Gegenfälle vor Produktionsänderung hinzufügen und SDK107-RED aufzeichnen.
- [x] Physische fehlendeFloor-/Wall-Vetoes und ehrliche frischeProposaltests
  vor Produktionscode formulieren, keine Algorithmusnachbildung.

## Task2: Kleiner Produktionspatch

Dateien: BotSupplyNative.h, cecil_motion.h (nur Beobachtungsserial),
BotDriver.cpp (nur periodisches Proposal-Telemetriefeld).

- [x] Healthphase + Clearfunktion hinzufügen; ClearGoal/Reset erben Clear.
- [x] Resetserial ausschließlich bei tatsächlichem Navigator.Reset erhöhen;
  keinerlei Pfadentscheidung ändern, keine zusätzlichen Allokationen.
- [x] Reine Eligibility-/Bindinghelper und bestehende Connectorbewegung nutzen;
  nach frisch geprüftem arrived armieren, warm nur validiert fortsetzen.
- [x] Jeder nicht zulässige frühzeitige Ausgang/Movementowner löscht Phase.
  Budgetneutralität lässt nur den gebundenen Versuch bis fester Deadline stehen.
- [x] currentNavTravel/Point bei Fortsetzung ehrlich löschen, Proposal separat
  melden und vorhandene finales Safety unverändert durchlaufen lassen.

## Task3: Verifikation und Handoff

- [x] SDK107-Bridge einschließlich vollständiger Parentchecks GREEN.
- [x] ASan/UBSan derselben vollständigen Suite GREEN; relevante portable
  Motion-/Supply-/Observertests nur gezielt, keine breite Tools-Discovery.
- [x] Bereinigter Bericht + private Commands/Outputs/Sourcehashes und Grenzen.
- [x] Eigene Source-/Testscommits, sauberer WT; Root übernimmt unabhängigen
  Review/Integration. Kein DLL-/Runtime-/A4-GREEN aus portablem GREEN ableiten.

## Restliche Abnahme

- [ ] Unabhängiger Rootreview/Integration.
- [ ] Neuer DLL-Build und tatsächliche native Devprüfung; kein Rollout aus portablem GREEN.

Finaler Sourcecommit b8854df01479a3aa0cd0673de86bc5d170561e1e; SDK107 normal und ASan/UBSan
je3104/0, zwölf C++- und vier Python-Parentprüfungen Exit0. Bericht
`docs/reports/2026-11-14-a4-health-connector-continuity.md`; private Quittung
`.codex/evidence/health-connector-fix/final-receipt.json`.
