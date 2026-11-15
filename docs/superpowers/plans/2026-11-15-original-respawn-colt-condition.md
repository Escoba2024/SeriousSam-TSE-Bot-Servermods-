# Original-Respawn/Festziel030 Implementation Plan

> Umsetzung inline mit executing-plans/TDD; keine Subagenten. Root allein
> integriert/friert/führt aus. Scope ist die benachbarte gleichnamige Spec.

**Goal:** Eine deaktivierte neue Bedingung erzeugt echte normale Respawn-/Colt-
Beispiele oder scheitert begrenzt ohne vorhandene Verträge umzudeuten.
**Architecture:** Pure Readiness-/Kettenpolicy; eigener normaler Methodenadapter
mit bestehenden Context/Worker/Cleanup-Primitiven; exakt inverser Offlinebuilder.
**Tech Stack:** Pythonstdlib, vorhandene reine Validatoren; nur Fakeports in Tests.

## Constraints und Schnittstellen

Alle Werte der Spec unverändert. Herkunftsbeleg für kopierte Endpoint-/Input-/
Windowteile; keine globale Monkeypatches. Kein Frida/X/proc-Zugriff in Tests.
Private Logs0600/O_EXCL,ausgeführte RED/GREEN erhalten. Outputs speicherarm.

Task1 policy erzeugt validierte DEAD_READY-Identität/kausale Kettenprüfung;
Task2 Method verwendet genau diese Identität, reale Endpointcalls und tatsächliche
Observer-Captures/S-F. Task3 kopiert diesen Adapter und repinnt genau die neuen
Config-/Runner-/Ownershippfade; alte Methods/Core/Observer bytegleich.

## Task1 – echte Readiness und vollständige Ketten

- [ ] Erst pure REDs:dead/MayRespawn/neutral exakt; falscherActor/Slot/Life/Clock,
  Boolwerte/Predictor/stale/Reserve fatal. Vollständige synthetische echte Rowform
  positiv; fehlenderInit/Anchor/Owner/Leave/normal+fatal/S-Cutoff negativ.
- [ ] Kleinste Policy; tatsächliche Registered-Tracevalidatoren bleiben vorgeschaltet.
- [ ] Gezieltes GREEN,Log/Quellcommit. Keine alten Raws oder Gesamtsuiten.

## Task2 – eigene normale Fire-/Readiness-Methode

- [ ] Vor Source RED mit Fakeports:echter Aufruf Down/Up/Flush/neutral; Downfehler,
  Metadatenfehler,Upfehler,Focus/PIDdrift,fehlenderACK,Deadwaittimeout,ColdTTL,
  falscherLifewechsel und ausgebliebene Damagebeispiele bleiben FAIL.
- [ ] Reuse NativeContext.read/input_frame/38Regionen und Batchworker; alte
  inputfreie Quelle bleibt bytegleich. Neue Control bleibt ohne Frida/Worker.
- [ ] Native10s/15s/2/.2/8/85/90 in Fakeclock tatsächlich ausschöpfen; Release
  unabhängig von Observer-/Journalfehlern; ein Inputprogramm/kein Retry.
- [ ] Gezieltes GREEN,Source-/Kopierherkunft/Bounds und Commit.

## Task3 – getrennte strikte Conditionkopie

- [ ] Vor Source echte Parentfixture-REDs:einzigTestTarget0,neue Ownershipkennung,
  keine Original-RVA aufBot,Deadbasisreader explizit,keinFakeInputfreeLabel;
  keine alten Gateaktivierungen,korrekteImports/JSONIPC/Quellinversen.
- [ ] NeuerBuilder mit ganzerInverse jedes geändertenParentfiles,allePinwerte,
  Snapshot-/Restoreclosure,4Core/Body/Schema/Validator bytegleich; falschePins FAIL.
- [ ] Disk8GiB+64MiB+Copy vor frischem Disabledfork; Grenzen/Gates/Rollen/Dateien
  unabhängig aus Manifestwerten prüfen,keinenControllerimport.
- [ ] Report/Receipt/saubereCommits anRoot,danach quieszent. Keine Runtime.

## Review Focus / Rulings

Root akzeptiert expliziten DEAD_READY-Basisreader statt nicht anwendbarer
Live-Muzzlegeometrie; keine Nulltransientregel. Aktuelle alteNAIConfigbindung
bleibt strikt, neue Kopie eigene exakteKennung. Alte InputfreeChecks nie grün
synthetisieren. Keine menschliche Freigaberunde nötig, Auftrag autorisiert.
Reale Vorbereitungs-Tötung ist nicht garantiert; Fristablauf ehrlich FAIL.
MayRespawn2 allein beweist keinen Respawn; Root verlangen echte Callbackkette.
Statische Unvereinbarkeiten zuerst konkret melden,kein Interface-/Guardraten.
