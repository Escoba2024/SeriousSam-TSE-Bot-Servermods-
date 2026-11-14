# Own-XRECORD: Cold5/Warm1 tatsächlich beobachtet

Am 14.11.2026 um 21:45 UTC führte Root genau einen begrenzten Methodenlauf
auf eigenem Xvfb :167 aus. Kein TSE-Prozess wurde gestartet.

| Messung | Kalt | Warm |
|---|---|---|
| Requestzähler | 14 → 19 | 21 → 22 |
| Eingabe | einmal RelativeMotion +12 | einmal RelativeMotion +12 |
| Tatsächliche Position | 400 → 412 | 412 → 424 |

Die fünf kalten Requests sind QueryExtension XInputExtension, XTEST,
Generic Event Extension, GEQueryVersion und XTEST RelativeMotion. Im warmen
Intervall erscheint ausschließlich RelativeMotion. Die eigenen QueryPointer-
Antworten sowie Device- und Delivered-Motion stimmen überein. Der Auditor
bindet die Requests an die eigene Verbindung und die Query-/Emissionsintervalle.

Status: `PASS_METHOD_COLD_WARM_LIBRARY_REQUESTS_ONLY`. Raw 6170 Bytes,
SHA256 `9a2fd52bcc5a18928098cfaf8f59e095d8a9b0a1eca94e53d693eff072a012ef`.
Result SHA256 `45adbbad603ab49fde34e3b20f51c8b38ba62a0cb403937a27d15458ccd7a7d2`.
Keine unbekannten, fehlerhaften oder verlorenen Records; kein TTL-/Overflow-
Ereignis. Alle drei eigenen Kinder regulär beendet, Exit 0, kein Force;
XRECORD-Kontext, Daten und Verbindungen freigegeben. Root prüfte unabhängig
PID-Generationen, verschwundenes Display und freigegebene Sperren.
Laufzeit 0,3693 s; Parent-CPU 0,0353 s, Child-CPU 0,2316 s.

Das erklärt die Bibliotheksinitialisierung reproduzierbar, ersetzt aber keine
nachträgliche Wireaufzeichnung des früheren Originalclient-Fehlschlags 26→31.
Beide früheren A1-Fehlschläge bleiben fehlgeschlagen. Keine Retail-/XI2-/A1-
Abnahme und kein Schadensnachweis. Nächster Schritt: Metadatenvorbereitung
auf derselben Verbindung vor Recorder-arm, ohne zusätzliche Mauseingabe,
ohne Lockerung von Requestguard, ACK, EPS oder Messfristen; danach Rootreview
und genau eine eigenständige Originalclient-Diagnose.

Private Belege: RootEV/own-xrecord-cold-warm-root-20261114 und
RootEV/cold-warm-method-root-independent-end.json. Vorbereitungsquellen und
Rückrollstand bereits in Delta051 vollständig extern rückgelesen; das spätere
Methodenresultat benötigt Delta052. Live bleibt unverändert.
