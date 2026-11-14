# Instruktionsprobe-Vertrag vor weiterer A1/A3-Nativeprüfung

Ausgangspunkt: Root c98e164. Gesamtauftrag und A-/B-Gates bleiben unverändert.

## Befund und Grenze

A1 115139 geschlossen FAIL (b7efb2074b44598d1f9153184f0e9fc65fab9d14952187db5b23f35c9f39ba50): 20 GetInput, null CreateAction, keine Gameplayinputs. Expliziter Host-Originalbytevergleich, Unload/Detach und unabhängiger 664-Dateien-/8-Absenzen-/3-Log-Restore bestanden. Native Ursache noch nicht bewiesen.

Vier Midpoints verwenden Frida-Objektform mit onEnter. Frida17.26.2 wählt damit JSCallListener mit C-on_leave; die Instruktionsprobe benötigt Funktionsform/JSProbeListener ohne Returntrap. Bei zwei GetInput-Midpoints liegt gesichertes EDI oben auf dem Stack; beim dritten liegen Aufrufargumente dort. A3-GetCurrentTick+15 ebenfalls prüfen. Keine Behauptung eines Frida-Fehlers oder tatsächlichen Retailbranchverlaufs.

## Enger Arbeitsumfang

1. Agent candidate_audit: eigener Worktree, fehlende Regression zuerst RED, dann ausschließlich vier A1-Midpointformen und den bestätigten A3-Midpoint zu Funktionsprobes ändern. Echte Funktionseintritte mit onEnter/onLeave bleiben unverändert. Keine zusätzlichen Sites, Spielinputs, Fristen, Raten, Gains, ACK-/EPS- oder Abnahmeänderungen.
2. Eigene Win32-IA32-Testquelle und begrenzter Testcontroller: native EDI-Sentinel/Stackargumente vor/nach eigenem Midpoint; getrennte Baseline, historische Objektform als erwartbar fehlschlagende Kontrolle, Funktionsform. Eigener Prozess, gepinnte Frida-Version, kein TSE. Nur Root baut/startet; Agent liefert Quellen/Offlinefälle/disabled Vorbereitung.
3. Root prüft fremde Prozesse, Locks und Platz; baut mit vorhandener Toolchain. Abnahme: Funktionsform erhält Sentinel und Argumentergebnis; historische Form zeigt spezifische Verletzung oder bleibt ausdrücklich unbewiesen. Vollständige Originalbytes/Quieszenz/Detach/Prozessende belegen. Nicht auf TSE übertragen, solange Methode nicht bestanden.
4. Neue deaktivierte A1-/A3-Pakete mit vollständigen Hashpins bauen; gezielte Regressionen und unabhängiger Review. Root allein friert Runtimekopien ein und startet danach je begründetes isoliertes Nativefenster. Frühere FAILs bleiben FAIL.

## Parallelität und Sperren

Root allein Runtime/Build/Integration. a4_diagnosis darf fertigen Canonical-Observer unabhängig statisch reviewen lassen bzw. neuen Probeumfang reviewen. Maximal zwei Agenten, getrennte Worktrees, keine Native-/Attach-/Compilerarbeit durch Agenten. Keine Root-Archivierung/Publikation/Tests parallel zu späteren TSE-Nativefenstern.

## Status

- [x] Konkreter API-/Stackbefund aus gepinntem Frida-Quellcode und Retaildisassembly.
- [ ] Enge RED/GREEN-Regression und Quellenkorrektur.
- [ ] Eigener Win32-Methodenbeleg, Cleanup und Rootprüfung.
- [ ] Neue deaktivierte Pakete und Review.
- [ ] Prospektive Retailbelege; A1-Schaden/A3-Tierstärke weiterhin separat offen.
