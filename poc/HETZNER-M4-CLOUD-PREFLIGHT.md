# Hetzner M4: portable Vorbereitung, Stand 17.10.2026

Cloud-Review ohne Zugriff auf Shadow/Hetzner, ohne Spielstart. Grundlage: [Cloud-Bericht](../docs/reports/2026-10-17-cloud-supervisor-review.md), Issue #6 und Drive-Hetzner-Masterplan. Bereits dokumentierte M1-/M3-Nachweise bleiben erhalten; keine Wiederimplementierung ihrer Harnesses.

## Verfügbare Quellen und belegte Lücken

Die Drive-Nachträge nennen vorbereitete private Linux-4-/8-Bot-Harnesses und bestandenen Selbsttest, aber keine im zugänglichen GitHub-Baum versionierten Skripte. Prüfung aller frisch abgerufenen Branches, einschließlich PR #8, und Drive-Projektordner/Suche fand keine entsprechenden Linux-Harness-Quelldateien. Damit sind deren Voraussetzungen, Run-IDs, Prozessidentität, Auswertungslogik und Cleanup **nicht unabhängig geprüft**. Kein behaupteter Harness-PASS.

Vorhandene versionierte Windows-Werkzeuge wurden statisch geprüft:

| Werkzeug / Eigenschaft | Vorhanden | Grenze für M4 Linux/Wine |
|---|---|---|
| `tools/run-shadow-fleet.ps1` | neue Evidence-Verzeichnisse, Backup-/Restore-Manifeste, Zustands-/Log-Prüfung | Windows-Runtimepfade, Windows-Netz-/Prozess-Cmdlets; startet eigene Spiele und ist kein Cloud-Test |
| `poc/scripts/Test-RetailFleet.ps1` | getrennte zwei Vierer-Installationen, GUID-Sidecars, Join-/CRC-/Sync-/Human-/Recovery-Fälle | lokaler Windows-Dedicated/Ports, verändert vorbereitete Testkopien, kein allgemeiner Linux-4/8-Runner |
| Steady-Query im RetailFleet | Status/Spieler, Slotverlustprüfung | fünf Sekunden Sleep plus Laufzeit, nicht unabhängiger 1-Hz-Sampler; kein zweiter Status-Fence in dieser Schleife |
| Ressourcen | kumulative CPU-Sekunden, Private/WorkingSet, Handles/Threads je Rolle | kein Linux-PSS, Host-Steal, Runqueue oder Netzwerk; Identität des Ressourcen-Samplers nur PID/Pfad, nicht Startticks |
| `Test-FleetAIEvidence.py` | CPU eines Kerns aus CPU-Zeit/Wanduhr, RAM-Peaks; Ressourcen-/Query-Dauern | akzeptiert bis 60 s Sampleabstand, feste Windows-Rollen; keine M4-1-Hz- oder Host-SLO-Auswertung |
| 20-Hz-Telemetrie | bestehende Bot-/KI-Auditoren prüfen Tickfenster | Tickanzahl allein beweist keine <0,5-%-Wandzeitdrift unter Linux/Wine |
| Cleanup | gehaltene Handles, Ownership, Restore-/Port-/Crashdiagnostik | normaler finally-Pfad; harte Controller-/Guardian-Ausfälle brauchen eigene Native-Gates |

Diese Grenzen machen die vorhandenen Windows-M1/M3-Werkzeuge nicht fehlerhaft für ihren dokumentierten Scope. Sie dürfen bloß nicht als fertiger Linux-M4-Nachweis benutzt werden. Keine spekulative zweite Linux-Harness-Implementierung: zuerst den vorhandenen privaten Harness als bereinigten Text samt Selbsttests in eigenem Branch bereitstellen, ohne Hostadressen, Profile, GUIDs, Credentials, Binärdateien oder Rohlogs. Danach Cloud-Review/Regression gegen konkrete Schnittstellen.

## Prüfliste vor dem ersten Gruppenstart

Alle Nachweise müssen echte vorhandene Artefakte referenzieren; fehlend/ungültig bedeutet BLOCKED. Keine automatischen PASS-Dateien erstellen.

1. Gewählten Git-Commit und sauberen Baum feststellen; 61DC-DLL, EXE/Engine/Entities und Startup-INI privat hashen. Getrennte Clientinstallationen, Prefixe, Logs, Ports/Serverziel und vollständige eindeutige Profile/Sidecars prüfen. Run-ID pro Lauf und Client-ID pro Prozess; private Identitäten nicht veröffentlichen.
2. Bereits bestandene M1/M3-Evidence referenzieren. Gewählte Lowrender-Variante benötigt ihren abgeschlossenen externen Stundenbericht und die zugehörige Vanilla-Gegenprüfung; Zwischenstand oder andere Renderkonfiguration ersetzt diese nicht. Aktuelle Runtime-Verfügbarkeit prüft ausschließlich der Runtime-Agent.
3. Native Wine-/x86-Runtime-Paarung, Xvfb/GLX/llvmpipe, CPU-/RAM-/Diskbudget, Uhren/monotone Zeit, Zugriff auf Prozess-Startidentität und unabhängigen externen Sampler prüfen. Fremde aktive Prozesse/Ports nicht übernehmen oder beenden.
4. Sampler und Auswerter zunächst gegen synthetische Fixtures prüfen: verlorenes Paket, fehlendes final, abgeschnittenes Feld, wechselnder Status, doppelte eigene Namen, verschwundener Slot, CPU-Zählerreset/PID-Reuse, rückläufige Zeit, Drift, Syncmarker, abgebrochener Lauf und fehlende Cleanup-Evidence müssen FAIL/BLOCKED ergeben.

## Messvertrag für 1×4, danach 2×4

Je Stufe zehn Minuten Warmup, 30 Minuten Messung und 60 Minuten Soak, gleiche Karte/INI wie die bekannte Baseline. Acht Bot-Slots plus ein unveränderter Vanilla-Observer für die Acht-Bot-Stufe; Beobachter/zusätzliche Menschen explizit getrennt in Sollbelegung erfassen. Human-Join/Leave, Mapwechsel, Reconnect und gewollten Client-Crash als gekennzeichnete Lifecycle-Fenster auswerten, nicht als ununterbrochenen Steady-Lauf ausgeben.

| Beweis | Aufzuzeichnen / auszuwerten |
|---|---|
| Unabhängige UDP-Sicht | separater externer 1-Hz-Sampler; Status/Spieler/Status, vollständige Felder/final, 1.07/leerer Mod, Counts/Max/Map und alle erwarteten Identitäten; Beginn/Ende jeder Query und Fehler/Timeouts; tatsächlich erreichte Rate und maximale Lücke berichten |
| Prozessidentität | Run-ID + Client-ID + OS-PID + unveränderliche Startzeit + EXE/Prefix-/Planbindung; Ressourcen niemals über PID-Reuse zusammensetzen |
| CPU | Delta Prozess-CPU-Sekunden / monotone Wandsekunden ×100 = Prozent eines Kerns; Hostanteil separat normalisieren; kumulative CPU nicht mit Prozent verwechseln |
| RAM / Host | RSS und PSS je Prozess, Host-RAM/Swap, CPU-Steal, Runqueue, Netzwerk; Peaks und Verteilungen je Messphase |
| 20-Hz-Timing | Delta Simulatorticks / (20×monotone Wandsekunden) −1, je Client und Phase; vollständige Tick-/Wall-Zuordnung, Rücksprünge, Lücken und Timerdrift erfassen; Render-FPS separat |
| Sync / Slots | frische pro Lauf gebundene Client-/Dedicated-/Vanilla-Logs, CRC/Join und BotDriver je lokalem Slot; Disconnected/bad-sync/SYNCBAD/CRC-/Crashmarker und erwartete externe Slots prüfen; lebender Prozess ist kein Joinbeweis |
| Abschluss | Ergebnis erst nach beendetem Messfenster und geprüftem Cleanup; fehlendes Summary oder abgebrochener Sampler bedeutet keine Stundenabnahme |

Masterplan-SLOs sind vorgeschlagene Abnahmeziele: Host-CPU dauerhaft ≤70 %, RAM ≤80 %, keine Sync-Kicks, absolute Zeitdrift <0,5 % je 30 Minuten. Bei >2 % Drift oder verlorenen erwarteten Steady-Slots STOP. Die Umsetzung muss Samplelücken/Unsicherheit als eigene Fehler ausweisen; kein geglätteter Mittelwert darf einen Stop-Fall verdecken. Keine Behauptung einer schon implementierten SLO-Prüfung in den vorhandenen Windows-Auditoren.

## Stop und Cleanup

Vor Start Grenzen und maximale Laufzeit festlegen. Nur eigene gehaltene Prozessidentitäten stoppen; kein globales wineserver/Prozessnamen-/PID-/Baum-Kill. Bei Fehler Logs/Result privat sichern, Identitäten und eigene Ports prüfen, temporäre Konfiguration/Netzregeln zurücknehmen und Originalhashes vergleichen. Blockierte Restore-Pfade bleiben blockiert, solange dort ein unbekannter Prozess aktiv ist. Harte Abbrüche müssen gesondert zeigen, wer noch Ownership hält und wie der Runtime-Agent anschließend sicher bereinigt.

Nächste M4-Vorleistung des Runtime-Agenten: bereinigte vorhandene Linux-Harness-Quellen + echte Prerequisite-Referenzen + Selftest-Kommandos/Schema bereitstellen. Erst nach Prüfung dieses konkreten Standes und abgeschlossenen Lowrender-Gates den begrenzten 4-Bot-Lauf starten; 8 Bots folgen erst nach dessen PASS. Cloud startet keinen dieser Läufe.
