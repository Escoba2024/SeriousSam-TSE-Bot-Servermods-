# Source-only: eigene explizite QJS-Bedingung

Owner a4_diagnosis; neuer Branch `codex/20261115-first-state-explicit-qjs`
im vorhandenen isolierten WT. Nur neue helper/test/plan/report/claim-Dateien.
Kein Native/Frida/Build/Paket/FPS-Wechsel und keine alten Dateien ändern.

Parent unverändert: getter-receipt-disabled Manifest
cd61d6b098725d51bc78b2729eff5f1f1d5c5c3a5fa5c08f1afeb8a8c5053faf.
NativePython d2801018…/Bodyabeab90d…/compiledf5cc6498… bleiben exakt gepinnt.
Vorhandenen reinen V8-Transform wiederverwenden; Pythonänderung gegenüber dessen
Ergebnis ausschließlich literal runtime='qjs', requested_runtime'qjs', erwartete
Same-Observer-Runtime'QJS'. PID/ia32/4/echteTypprüfung und Raw vorSchema gleich.
Kalter JS-RPC ist bytegleichV8; vollständige Inversen bis zum ursprünglichen
Parent beweisen keine Änderungen an G, Hooks, Guards, Limits oder alten Gates.

TDD: tatsächliches extrahiertes load mit bestehendem V8-Transform als ältere
explizite Bedingung muss an qjs-Requestassertion scheitern; kein Import-RED.
Dann neue reine Wrapperfunktionen, FakePorts/Raw-/Fehler-/Typfälle, drei ganze
Inversen, identischesCompiledJS samt bestehender NodeVM. Kein Fallback/Retry.
Root integriert/prüft spätere Ableitung. ExplizitesQJS ist kein rückwirkender
Beweis für die Runtime alter runtime=None-Fälle und kein CPU-/A1-Fixclaim.

Status: COMPLETE_SOURCE_ONLY/HANDOFF. Echter alter V8-Behavior-RED1/1Fail
in0.011s vor Helper beobachtet. Danach nur Sourcearbeit während RootNative;
GREEN nach ausdrücklichem Closed/Resume:7/7 in0.792s, keine Korrekturrunde.
Drei ganze Inversen, gleicher G-Prefix und bytegleiches V8-ColdJS belegt.
Kein Paket/Native/FPS-/Grenzenwechsel; Rootreview/Nativequalifikation offen.
Nach finaler Receipt/Commit eigene Jobs beendet.
