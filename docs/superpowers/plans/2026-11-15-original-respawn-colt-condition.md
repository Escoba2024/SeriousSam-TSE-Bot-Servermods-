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
- [x] Gezieltes GREEN,Log/Quellcommits5b13c3d/f6f4a3c.6Tests, tatsächliches
  Callbackmodell+unveränderter StrictTraceValidator. Keine alten Raws/Gesamtsuiten.

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

## Ausführungsledger

Task1 complete:6Tests0.205s. Private Logs unter
/srv/tse-original-respawn-colt-evidence-20261115. Erste Syntaxfehler in neuen
Testtexten ausdrücklich keine Verhaltens-REDs; korrigierte fehlendePolicy-REDs,
Direct/Cast-player=null-Form und echter negativer Dead-Damage-RED erhalten.
Callbackfixture zuerst zu großer Burst mit Queue64-Fehler, danach echte Drains
zwischen Schüssen statt Grenzänderung. Zweiter Fixturefehler: ursprüngliche
zweiteVanillarolle, explizit zur neuen Botrolle geändert, keine Runtimeattribution.
Eine kleine rg-Quellenlektüre des externen portablen observer_harness.js erfolgte
ohne NOATIME; dessen frühere atime war nicht gepinnt, daher kein unverändert-
Metadatenclaim für diese Hilfsquelle. Alle weiteren externen Reads NOATIME.

Task2 underway:5 gezielte Fire-/Journaltests GREEN0.009s nach tatsächlichem
fehlendemAdapter-RED. Window-/Staging-/End-to-Endbedingungen noch NICHT fertig.
Ruling: neue Kettenpolicy liefert Init-/Anchor-/FirstTick-/FirstDamage-Seq/Native-
Tick/Delta getrennt und first_valid_state_damage_proven immerFalse; keine
Erstzustandsqualifikation aus irgendwann beobachteten Schadensbeispielen.

Task2 Source checkpoint:13/13 GREEN0.214s (method-live-flag-green.log).
Echter fehlender Window-/Replica-/Namespace-RED und echter positiveHP-ohneAlive-
RED erhalten. Tatsächlicher alter Control10s-Loop mit Fake-C-Port, realer
Journal-/Flush-/Releaseausführung, 38-Context-AST byteidentisch gepinnt.
Neue Gegenfälle noDeath/missingDown/World/Shooterlife jeweils fatal; das sind
gezielte bestehende-Guard-Prüfungen, keine erfundenen neuen Verhaltens-REDs.
Ruling: Original-Replik und Server werden strikt auf Entity/Life/Health und
beobachtete FIRE-Zustände gebunden. last_buttons und buttons_now liegen an
verschiedenen Enginefeldern; Gleichheit wird als zusätzliche tatsächliche
Beobachtungsbedingung verlangt, nicht als garantierte zeitliche ABIäquivalenz.
Keine Pointergleichheit über Prozessräume. Replikationsabweichung fatal.
Task3 fehlender Builder erzeugte3 echte REDs; tatsächliche Parent-Einrückung
und vollständige Cleanupzeile mussten als Fixturefragments korrigiert werden
(Builderausführungsfehler erhalten, keine Verhaltens-RED-Umwertung).
Danach3/3 Source-/Manifesttests GREEN0.031s. Zu diesem Zeitpunkt noch kein
Paket/NativeReady.

Task2/3 complete (offline): zusätzlicher echter LateRead-RED am tatsächlichen
neuen `_sample`→ACK-Pfad; .02s frischer Read nach1.99s Guardarbeit muss dennoch
an der unveränderten2s-Gesamtfrist scheitern. Commit6adfe0f ergänzt ausschließlich
den Nachread-Fristguard. 20Policy/Method+3Buildertests GREEN .408s/.041s.
Native10s/15TTL/Workergrenzen werden durch unveränderte Parentmethodenquelle
und exakte Runnerinversen erhalten; kein neuer tatsächlicher Trace-/TTL-Test
oder nativer Retailnachweis wird aus den Fakeports abgeleitet.

Finaler D-v3 /srv/tse-a1-original-respawn-fixedtarget030-v3-disabled-20261115,
Manifest57c65e12ac413ca3231bc9141dc428e44563fe70bc1d86c1811f122ff2bf7177,
1636537Bytes,280/77/14Pinsvollständiggeprüft,7Parentdateiengeändert und130gleich.
Keine Sourcegates aktiviert. D/D-v2 unverändert superseded/NEVER_NATIVE.
Private finaleQuittung disabled-v3-final-receipt.json SHA17302d53a6276889f32166072ffe888346a43fcab2915d487a58b80f943e75ec
im obenbenannten Evidenceverzeichnis. Rootreview/Integration/Freeze/Native
bleiben allein Rootaufgabe. Keine offene Implementierungsaufgabe in diesemClaim;
FirstStateabnahme/Botopfer/Aim/Gain bleiben ausdrücklich außerhalb.

## Forwardfix nach echtem geschlossenen Control-FAIL17:03

Root bestätigte explizite Vanilla-Basisflags `colt_preparation=False` UND
`mouse_input_profile=False`; optionaler perFrame-Mausprofilzusatz ist für den
reinen Fire-Respawnfall nicht erforderlich. Alter Reader unverändert.
Der bisherige True/False-Mix war ein eigener Interfacefehler, keine
Readiness-Transientursache. Tatsächlich ausgeführter Constructorprefix und
Snapshotguard reproduzieren denselben EvidenceError (v4-real-reader-contract-red.log).
Engster Literalfix plus explizite neue Metadaten;6gezielteTests GREEN .081s.
Basisframes ohne Animatorread füttern unveränderte NativeContext-Doppelreads;
unveränderte Controls.sample-Guard-/Doppelreadkette bleibt aktiv und wurde mit
einem tatsächlichen fatalen Smooth-Gegenfall geprüft. Keineproc-/Runtimecalls.

Frischer D-v4 Manifest360afce14b4a1193c28ff8cd33d9fbe34b2da167c30affff52640a8040af99f6,
1644803Bytes;280/77/14Pins+4Inversen frischPASS. Alle älteren D und tatsächlicher
F-v1-FAIL unverändert erhalten. PrivateQuittung disabled-v4-final-receipt.json
SHAfda261c7047a6881ed078f769a30833ce24bca42a1410f177c14a4ebecdf4fc4.
MIP-Startupintervention/Originalmarker, NIPcontrols und alte20Method-/Policy-
Tests unverändert; Letztere nicht erneut ausgeführt. KeineNativefreigabe.

## Forwardfix D-v5: frische Ownershipbelege je Rollenread

Claim bleibt eigener RP-Methodenadapter, exakter Runnertransform und zugehörige
Tests/Metadaten. Allgemeine NAI-Capture-/Validator-/private_json-Quelle unverändert.
Realer F2-Control-FAIL FileExistsError beim zweiten Capture bleibt erhalten.

1. Tatsächliche native_roles-Closure samt Capture/private_json mit zwei Reads
   ausführen: erwarteter RED ist Kollision am bisherigen O_EXCL-Pfad.
2. Eigenen expliziten RP-Adapter ergänzen: initialer Methodframe UND Folgeproben
   in EINEM Serialbudget1..1024; frische0700-Verzeichnisse; O_EXCL0600 beibehalten.
   Maximal3MiB Receiptpayload gesamt = zweimal bestehendes1536KiB-Einzelmaximum;
   vor jedem Read vollständiges Einzelmaximum reservieren, danach tatsächliche
   Größe anrechnen. Deshalb kann das Bytebudget konservativ vor1024 abbrechen.
   Keine Ownership-/Hash-/Logprüfung überspringen oder cachen.
3. Bestehende absolute parent_started+85-Frist vor/nach Callback; keine neue
   Frist, Writes zählen real mit. Capturefehler bleibt primär; Custody-/Zeitfehler
   separat sticky und weiterhin FAIL. Gegenfälle für Budget, Frist, O_EXCL,
   fehlenden/fehlerhaften Beleg sowie unverändert fatale Ownershipmutation.
4. Gezielt GREEN und ganze4Runner/NAI/Config-Inversen; frischer D-v5 mit
   vollständigen Pins, alte D/F unverändert. Root allein Freeze/Native.

D-v5-Implementierung abgeschlossen: realer Doppelcapture-RED und sechs
Bounds-REDs beobachtet;34 fokussierte Tests GREEN0,664s. Initialframe plus zwei
_sample-Reads mit tatsächlicher NativeContext.input_frame-AST und puren
Byteports geprüft, keineRuntime/ABIqualifikation. Zusätzliche Logs/Dateien
ändern keine Nativeinputs oder Guards. Ganze4Inversen weiter geprüft.
Quelle/Belege siehe neuen Fresh-Ownership-Report; Abschluss mit frischemD-v5
und vollständigem Pinreceipt erfolgt nach separatem Sourcecommit.

D-v5 final1662009B, Manifest6ca287db33640b859b2854df19dfd1acd78b6b4f91ab2fc3879b1d8d2a33a9a7.
280/77/14Pinwerte und ganze4Inversen verifiziert; Receipt
disabled-v5-final-receipt.json SHA
bbed8048c5fb0fbd4a07efa47dcdf3c1923e1332aa8d11a182c2d6a24f3648f1.
Root hat34Tests eigenständig reproduziert; keine Native durch Autor. Keine
weitere Implementierungsaufgabe offen; Rootfreeze/Retest bleibt Rootaufgabe.
