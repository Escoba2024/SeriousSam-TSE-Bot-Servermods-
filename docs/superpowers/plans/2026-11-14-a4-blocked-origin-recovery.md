# A4 FinishImportant-Ausgang: begrenzter Recoveryfix

> executing-plans/TDD; Root autorisierte Umsetzung nach echtem40477b5-RED.

**Goal:** Ausschließlich den selbst temporär vermiedenen not_usable-Ursprung
wieder innerhalb seiner originalen Ankunftsgeometrie erreichen.
**Architecture:** Lokale provenancegebundene Ergänzung der vorhandenen
FinishImportant-Avoidregel. Blockmaske und Navigator bleiben unverändert;
nur sein belegter neutraler Ursprungspfad kann nach frischem bestehendem
LOS-Cast langsame Rückannäherung vorschlagen. Echter Radius/ursprünglicher
Navigator erlauben danach wie bisher den Exit. Keine allgemeine neue Navigation.
**Tech Stack:** C++14 SDK107-Brücke, tatsächliche Produktionskörper, ASan/UBSan.
**Spec:** Rootfortsetzung nach3115/2RED und geschlossenem022-Bericht36137adb.

## Grenzen / Reviewfokus

- Nur not_usable-FinishImportant ohne Next/Special/Lock, kein pauschales
  blockedSourceignore, keine Änderung von Blockmasken, Türen, Kanten/Radien.
- World/Map/Player/Generation/Gravity/ursprüngliche Navmetadaten einschließlich
  ImportantEntity, IDs/Links, exakte vorhandeneAvoidNode/10s-Deadline binden.
- Gewöhnliches anderes Ziel, seine Item-/Start-/Deadlinebindung und tatsächliche
  Navigatorresetgeneration ab erster Recovery berücksichtigen. Fullreset/Death/
  Contextwechsel/Timeback/andererAvoidgrund/physischeSourcelocks widerrufen.
- Frischer bestehender LOS-Cast, begrenzt auf8m/3m Höhe, nur Bodenstand/Crouch,
  keinUse/Follow/Flight/Liquid/Special-/Importantziel; Budget<=2 neutral.
- Nur langsame vorhandene Reacquire-Projektion; keine synthetische Ankunft,
  kein Ankerwechsel, keine Nav-/Floorstempel; reguläreSafeMotion prüft weiter.
- Ursprüngliche Item-/Goal-/10sAvoidfristen niemals verlängern.
- Keine DLL/Live/Native/Delegation. Root allein Integration und Runtime.

## Aufgaben

- [x] Vor Produktion echte Adversarialfixtures im vorhandenen SDK107-Harness:
  Cast/Budget, Metadaten/ImportantEntity/physischeLocks, World/Map/Gen/Reset,
  fremdeAvoidgründe, Zielkontext/Deadline, Special/Use/Liquid und finaleSafety.
- [x] RED gegen unveränderte Produktion sichern; 3115/2Repro bleibt erhalten.
- [x] Minimaler provenancegebundener Helper ausschließlich im Supplyheader,
  bestehendeFinishImportantcallers binden, klareRecoverytelemetrie ergänzen.
- [x] Vollständige SDK107-Brücke normal und ASan/UBSan, gezielte Parent-/Header-
  Regressionen, echte Commands/Pins/RED→GREEN/Quittung/Report und Commits.
- [ ] Root unabhängiger Review; keine native Abnahme aus portablem GREEN.

Abschluss des portablen Implementierungsschritts: Produktion `eecac110`,
SDK107 normal/ASan+UBSan je3223/0, zwölf C++- und vier Python-Parentprüfungen
Exit0. Einzelheiten und private Quittung im Recoverybericht. Rootreview und
native Wirksamkeit bleiben offen; kein DLL-/Runtime-/Livevorgang.
