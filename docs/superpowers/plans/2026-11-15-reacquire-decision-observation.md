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

## Writerfortschritt 15.11.

- Task1 tatsächlich RED: zuerst3445/4, anschließend3464/23; nur die neuen
  Diagnoseerwartungen fehlten, die ursprünglichen3440Checks bestanden.
- Task2 umgesetzt: fester Datensatz, explizite normale Returns, optionaler
  bestehender LOSdetailpfad,1Hz ohne ClearGoal-Burst, UNKNOWN bei fehlendem
  Cast-/Nativezeitbeleg. Keine Änderung anderer Quelldateien.
- Rootreview-Korrektur: fünf Supportlocal-REDs3532/5; vorhandene Locals mit
  Knownbits an ihren tatsächlich erreichten Stellen ergänzt.3532/1 enthielt
  allein eine Stringerwartung `0` gegen tatsächliches `-0`; numerischer exakter
  Nullvergleich ohne EPS und protokollierte synthetische Vollzeile lösen diese
  Testdarstellungsannahme, kein Produktionsguard wurde verändert.
- Final normal und ASan/UBSan je3532/0 gegen Source-/Testcommitdd42a7b;
 16 bekannte Parentprogramme seriellnice15 abgeschlossen. Die abschließenden
 Läufe enthalten die präzisen Hint-Probe-Statuskombinationen; die konservative
 Formatobergrenze wurde ebenfalls tatsächlich geprüft.
- Byteinverse des gesamten Original-Reacquirebodys samt Heightguardmutation
  bestanden. Tatsächliche extreme Vollzeile1540Bytes; konservative Hülle mit
  sogar64BitUnsigned-/vollenInt-/32ByteEnumzulagen2029Bytes+NUL<2048.

Ruling: Height wird nur aus dem tatsächlich vorhandenen Local nach klarem LOS
kopiert; unversuchte/blockierte Hint-Height bleibt mit Knownbit UNKNOWN. Dafür
keine zusätzliche Geometrieberechnung oder Änderung des Selector-Ausdrucks.
Kosten: die Diagnose kann Height eines vorher ausgeschiedenen Hints nicht
nachträglich erklären; das darf nicht als bewiesenes Höhenveto gelesen werden.

Ruling: Rückkehr einer RayLength-Prüfung und deren vorhandenes Lengthlocal
werden gemeinsam passiv erfasst. Die Referenz auf Length wird erst im Setter
nach der ursprünglichen einzelnen Funktionsauswertung gelesen; Ergebnisbool
und ursprünglicher Guard werden unverändert zurückgegeben. Keine zweite Probe.

Abschlussbericht:
`docs/reports/2026-11-15-reacquire-decision-observation-implementation.md`.
PrivateQuittungSHA256c72ace674454fe43411d3957ed89e9b3346b9103376f872715a5d0634cd916f6.
Alle eigenen Jobs regulär beendet, keine weitere Hintergrundarbeit.
Noch keine native Beobachtung dieses Datensatzes, kein Skullsfix-/A4-PASS.
