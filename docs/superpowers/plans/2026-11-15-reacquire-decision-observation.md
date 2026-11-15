# Passiver Reacquire-Entscheidungsbeleg – TDD-Umsetzungsplan

> Umsetzung erst nach Rootdesignreview, dann mit superpowers:executing-plans
> und superpowers:test-driven-development; keine Delegation.

**Goal:** Im bereits bestehenden Reacquireaufruf tatsächliche Entscheidungen
belegen, ohne irgendeine Gameplayentscheidung oder Probe zu verändern.
**Architecture:** Fester lokaler Datensatz, bekannte Returnstellen und vorhandene
optionale Castdetails; neuer Diagnosezeitstempel, ein begrenzter Logemit.
**Tech Stack:** bestehender echter SDK107-C++-Bridgeharness/Python-Treiber,
seriellesnice15-Portablecompiler/ASan erst nach Rootfreigabe; kein Retailbuild.
**Spec:** `../specs/2026-11-15-reacquire-decision-observation.md`.

## Dateiscope

- Später ändern: `poc/candidates/redstation-supply-20261107/BotSupplyNative.h`,
  nur Diagnosefeld/-stück und passive Reacquireaufrufstellen/optionale LOSdetails.
- Später ändern: dort `test_cecil_native_bridge.py`, echte Bodies und vorhandene
  World-/Ray-/Networkstubs; keine Algorithmusnachbauten.
- Kein BotDriver-/PhysicalCast-/Memorydecoder-/Nav-/Runtimecontrollerrefactor.

## Reviewfokus

UNKNOWN darf nicht blocked werden; budgetbedingtes Nichtprüfen bleibt sichtbar.
Keine neue Actorsuche/Casts/RNG, keine stillen metadata-invalid-Returns.
Hint-/Scan-/Retrydaten müssen vor zerstörenden Clears aufgenommen werden.
NativeGameTime ist ein tatsächlicher zusätzlicher Getterread nur bei Ausgabe.
Lograte und fixed-size-Ausgabe dürfen weder Speicherwachstum noch Burst erlauben.

### Task1: adversariale REDs vor jedem Produktionsedit

- [ ] Im echten vorhandenen Harness neuen Logtag erfassen; Networkstub zählt
  tatsächliche GetGameTime-Aufrufe, Ray-/Worldlookup-/Normalize-/Allocationszähler
  bleiben unabhängig. Keine Xlib-/TSE-/Netz-/Runtimeausführung.
- [ ] Zuerst fehlenderLogtag/fehlenderGrund als echte RED protokollieren, nicht
  bloß ein fehlendes Symbol kompilieren lassen. Ursprüngliche3440Checks behalten.
- [ ] Reale Reacquirefälle paarweise diagnostics0/1: supportBudget3 ohneRay;
  NULLrefMotionguard; collapsed/invalidSupportsegment; ungültigesCastresultat;
  fehlenderHit/passable/fehlendePlane/Distance außerhalbOriginalintervall;
  Normalguard; Shapeinvalid; Metadata-invalid-weiterlauf; ContextOnly.
- [ ] Kandidatenmatrix: echte lokaleGeometrieabwesenheit/farHint; alletried oder
  backoff/blocked; ein bis drei Slots; erstblocked dannbudget2/unattempted;
  alleblocked; clearaberplanar<.25; clearaccepted; liquide/air/Rückticks.
  Gültiger FALSEblocked, invalidProbeFALSEUNKNOWN und leeresSegment ohneCast
  müssen unterschiedliche Datensätze ergeben.
- [ ] Retention6s/Reject6s und triedbitmap über mehrere Updates,ClearGoal,Reset,
  Map/Generation,Gravity/Position undBudgetdefer prüfen: keine Diagänderung am
  ursprünglichen Hint-/Deadline-/Bitmapverhalten.

### Task2: kleinstes passives GREEN

- [ ] Diagnosefeld/-struktur/-Emitter und explizite Abschlussstellen implementieren;
  alle Originalguards/Reihenfolgen und bereits ausgewerteten Locals beibehalten.
  Neue Logfelder hinter due-Flag; keine Gate-/Motion-/Suchverzweigung aus Logs.
- [ ] Bestehende optionale Castdetails ausschließlich beim bereits fälligen
  Diagnoseaufruf verbinden; bei diagnostics0 exakt bisherige Defaultargumente.
  Keine zweite Längen-/Support-/LOSprüfung mit Gameplaywirkung.
- [ ] Ratechecks: wiederholteAufrufe0..0.95→eineZeile,1.0→zweite; Goal-/Hint-/
  Deathwechsel darf keine Zusatzzeile öffnen; Rücklauf/NaN unterdrücken, Reset
  beginnt ausdrücklich neuenStatezyklus. DreiHintgrenze/2048Byteformatgrenze
  einschließlich extremen Zahlen/UNKNOWN testen. FehlenderNetwork/ungültige
  Nativezeit bleibt Unknown und beeinflusst keine Aktion.
- [ ] SDK-NoDiagpaar identische Bewegungs-/Aktionsausgaben, alle operationalen
  Statefelder/Bitmaps/RNG/Hint-/Retry-/Goal-/Navsource-/ResetSerial und Queryzahlen.
  Vektor-Inhalte/read-only-Searchberichte vergleichen, kein C++Paddingmemcmp.
  Nur neues passives Diagnosefeld wird explizit aus Zustandsvergleich getrennt.
- [ ] Zusätzlicher reversibler Quellvergleich: nach Entfernen ausschließlich
  benannter Diagnoseeinschübe/optionalerArgumente muss ursprünglicher Reacquirebody
  bytegleich sein. Mutation eines Guards(z.B.Height8→9) muss diesen Test rot machen.

### Task3: Verifikation und Handoff nach Rootfreigabe

- [ ] Fokussierten echtenSDK107-Harness einmal normal seriellnice15 ausführen;
  nur bei neuen Fehlbefunden begründet wiederholen, keine breiten Loops.
- [ ] Relevante vollständige vorhandeneHeader-/SDK107-Regressionsliste des024-
  Parents und einmal ASan/UBSan; tatsächliche Kommandos/Exits/Counts protokollieren.
- [ ] Bericht/RED→GREEN/Quelle/Tests/Hashes committen, alle Jobs beenden. Root
  integriert/reviewt/baut separat. Kein Nativeerfolg/ursächlicherSkullsfixclaim.

Aktueller Abschluss dieses Auftrags: ausschließlich Design und Plan geschrieben;
alle obigen Implementierungs-/Testschritte sind noch offen.
