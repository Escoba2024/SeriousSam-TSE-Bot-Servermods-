# A1: expliziter V8-Request mit kalter Same-Observer-Quittung

Source-only; kein Paket, kein Frida-Import, Native, Build oder Liveeingriff.
Die Ursache des vorherigen Host-CPU-FAIL bleibt UNKNOWN. Die tatsächliche Runtime
jenes Retailfalls wurde nicht attestiert; `runtime=None` ist kein QJS-Nachweis.

Der neue exakte Transform bindet den vollständigen bisherigen Python-, Body- und
compiled-Quellhash. Er ergänzt in `NativePorts.load` einmal `runtime='v8'`,
einmal den kalten `runtimeidentity`-RPC direkt nach `script.load`, die bestehende
private atomare JSON-Ablage und eine exakte Schlüssel-/Wert-/Typprüfung:
V8, derselbe erwartete Server-PID, ia32, vier Byte. Eine neue frische Receiptdatei
wird durch das unveränderte `atomic_json` mit0600 erstellt. JSON-darstellbare
abweichende Antworten werden vor Ablehnung archiviert; nicht darstellbare Werte
(z.B.NaN) und Journalfehler scheitern ebenfalls vorArm. Kein Retry/Fallback.

Im JS wird ausschließlich der kalte RPC hinzugefügt. Der gesamte JS-Hash ändert
sich ausdrücklich. Vollständige Python-/Body-/compiled-Inversen und der identische
G-Prefix belegen unveränderte Originalbodies, Guards, 18Hooks, vorhandene RPCs und
Hotpath. Alte Gates bleibenfalse. Die alten Dateien und Pakete wurden nicht
verändert; der Helper erzeugt selbst kein Paket.

15 gezielte Offline-Tests PASS (0.759s). Zuvor lief dieselbe tatsächliche alte
`NativePorts.load`-Extraktion/compiled-VM:20 erwartete Verhaltenassertions FAIL,
keine Importfehler, zwei mangels Transform zunächst übersprungene Inversetests.
GREEN prüft echte AST-extrahierte load-/atomic_json-Bodies mit FakeSession,
Runtime-/PID-/Architektur-/Typ-/Schemaschäden, Create/Load/RPC-/Journalfehler,
private Receiptmode und unveränderte Cleanup-Verfügbarkeit. Die tatsächliche
compiled-VM prüft den kalten RPC ohne Attach/Memoryread, ehrliche QJS-Ausgabe bei
entsprechendem Modellwert, das weiterhin falsche Arm-Gate und neun vorhandene
I1/I2-/TTL-/Identitäts-/Header-/Body-/IAT-/Stop-Gegenfälle. Keine echte Frida-/ABI-
oder Performancequalifikation aus diesen Modellen.

Reproduktion: `nice -n 15 python3 -m unittest tools.test_first_state_v8_runtime_patch`.
Private Pins/Whole-Inversequittung und RED/GREEN-Logs:
`.codex/evidence/a1-v8-runtime-receipt/` im Autorenworktree. Private statische
Designnotiz `a1-v8-static-decision-20261115.md` bleibt erhalten.

Root muss vor einem begründeten Einzeltrace separat ableiten, reviewen, sichern
und eine neue passende inputfreie Kontrolle sowie PID-CPU-Beobachtung planen.
Alle bisherigen Queue-/TTL-/Schema-/Deadline-/Hostgrenzen bleiben gleich; der
zusätzliche kalte RPC verbraucht vorhandenes Setupbudget. Kein CPUfix-, A1-,
18ABI- oder NativeReady-Claim.
