# Human-KI und CPU-Integration – Ausführungsplan
> Ausführung durch den Hauptagenten mit superpowers:executing-plans; keine zusätzlichen Agenten.

**Ziel:** Retail 1.07, acht aktive Bots, fünf Skillstufen/sechs Persönlichkeiten, CPU-Optimierung und öffentliche 60-Minuten-Abnahme.
**Architektur:** Eigener Kandidaten-Overlay; qualifizierte Release-Dateien bleiben unverändert. P0-Telemetrie aus main, Diagnostik/Throttling aus #42, Human-KI aus #44.
**Tech Stack:** Hetzner Ubuntu/Wine, MSVC 14.44 x86, gepinntes SE1-ModSDK.
**Spec:** docs/superpowers/specs/2026-10-21-human-cpu-master-goal.md (vollständiger Nutzerauftrag).

## Globale Grenzen
- Ausschließlich Hetzner; keine neuen Agenten, Lizenzannahmen, Kosten oder Shadow.
- Laufende Benchmarkfenster nicht durch Builds/Lasttests verfälschen.
- Original-Dedicated/Vanilla und qualifizierte 61DC-DLL erhalten.
- Kein Merge/Deployment vor Build, Runtime und bestandenem Sync.
- Keine Abschaltung der Sync-Prüfung; keine privaten Binaries/Logs in GitHub.

## Bestandsprüfung 21.10.2026 00:34 UTC
Drive-Protokoll/Handoff zuletzt 20.10.22:12 UTC, Reviewboard 16.10.; gelesen.
main 67f1977 enthält #43. #41 d64e4a8 offen; #42 f3c9384 offen; #44 7d9e695 offen.
Eigener Worktree /srv/tse-integration-20261021, Branch agent/integration/20261021-human-cpu.
Benchmark PID103292, Serienmessung mit 180s Warmup/600s Messfenster; erste zwei Fenster gespeichert.
Zwischenfenster-Build abgeschlossen: 15 Quellen, MSVC x86, DLL a54053e7a29b7b6c1de9ca724bec8bf5a6acdab50acef7b981c1575605b2dfeb.
Dieser Build ist eine Release-Quelle mit Renderänderung, keine integrierte Human-KI.
Öffentlicher Server gestoppt; qualifizierte Binaries erhalten.

## Review-Fokus
CSV-Feldverschiebung, Profil-/Entity-Neuzuordnung nach Respawn, Human-KI trotz Throttling mit 20Hz, Locks/Watchdog-Lebensdauer, Build-/DLL-/Testidentität.

## Aufgaben
1. [x] Quellen/Prozesse/PRs prüfen, eigenen Worktree und Plan anlegen.
2. [x] CSV-Fehler mit erzeugter C++-Zeile reproduzieren; Header/Feldtypen/21 Werte prüfen; minimale Korrektur; Parser-Regression.
3. [x] #42/#44 als unveränderte Vorschläge übernehmen; konfliktfreien integrierten Overlay herstellen. Legacy + Human + Telemetrie + NullRender + Diagnose gemeinsam erhalten; Default-Flags aus.
4. [x] Portable KI-/Smoke-/Parser-/Overlay-/Provenienztests. In Messfenstern keine schweren Tests.
5. [x] Serienmessungen auswerten; erst danach integrierte DLL mit MSVC bauen, Quelle/Hash/Toolchain protokollieren.
6. [ ] Eigene Runtime/Ports: 1→4→8 Bots, originale Retail-Gegenstelle, 60min aktive KI/Sync; A/B/C CPU ohne Überlappung; Ressourcen/Kapazität.
7. [ ] Nur bei allen PASS: Backup/Rollback + öffentlich 8 Bots, Browser/Join prüfen; Commit/Push/PR/Drive/Handoff aktualisieren.

## Abnahme
Konflikte gelöst; echte CSV korrekt; qualifizierte CPU-Werte; fünf Skills/sechs Personas im aktiven BotDriver; MSVC/Wine PASS; acht kämpfende Bots; Originalclient-Join; 60min Sync; öffentlich erreichbar/gelistet; Rollback; GitHub/Drive aktuell.
Jedes Gate bleibt OFFEN bis zum tatsächlichen Nachweis.

## Fortschrittsledger
- 00:34 UTC: Bestandsprüfung und isolierte Integration begonnen. Erste Messpaarung zeigt deutlich weniger CPU bei NullRender; noch kein abschließender Seriennachweis.

- 00:39 UTC: CSV-Regression RED→GREEN; 20 Parser-Tests PASS; 3 Overlay-Tests PASS; 13 Provenienz-Hashes und PR44-Patch-Verifikation PASS. #42/#44 unverändert importiert; Konflikte in separatem Kandidaten vereinigt. Vollsuite/MSVC-Build über zeitlich begrenzte Pause nach drittem abgeschlossenem Benchmarkfenster geplant.

- 00:50 UTC: Vollsuite PASS: sieben C++-Suiten (555 Human-KI-Checks), realer integrierter KI-Block-Smoke, 52 Benchmark-/Overlay-Tests, 20 Parser-Tests, 6 Query-Tests; zusätzlicher Runtime-Preflight 5 Tests PASS. MSVC kompiliert alle 15 Quellen und linkt integrierte PE32-DLL SHA256 84e7ce725b0c00806c2c538ac96bb9b69a78cb34021efaae25b99743e64fb771. Noch keine Runtime-Freigabe.
- Speichergrenze erkannt: 1,9GiB frei. Overlayfs-Isolation mit eigenem synthetischem Schreibtest bestätigt; kompletter Acht-Bot-/Vanilla-Datei-Preflight ohne Spieleprozess bestanden, alle acht eigenen Mounts wieder ausgehängt. Ursprünglicher Vanilla-GMS-Provider war TCP/IP Server; privater Client-Overlay setzt ihn reproduzierbar auf TCP/IP Client (neue Regression RED→GREEN).
- Nächstes Gate: nach viertem vollständig gespeichertem Benchmarkfenster isolierter Ein-Bot-/Originalclient-Lauf (120s), danach Benchmark fortsetzen. Controller /srv/tse-integration-one-gate-20261021.py und Status-JSON; keine andere Messung überlappend.

- 01:01 UTC: echter Target-Application-Regressionsfall kompiliert aus dem Driver: RED mit null target dereference. Minimale Korrektur nutzt Human-Policy-Gedächtnisdistanz statt verdeckter Liveposition; fehlendes Entity deaktiviert Fire. GREEN bei verschwundenem und verdecktem Ziel; volle KI-/Smoke-/Benchmark-Suite erneut bestanden. Neuer MSVC-Kandidat erforderlich; erster 84e7-Build bleibt historisch/unqualifiziert erhalten.

- 01:05 UTC: korrigierter Target-Build 9a0a71a1d3dbf4d873a3a083287ea7d5e40cad476cb556e2d84cfc7ba492bea3 verbindet Bot und originalen Retail-Client (beide CRC OK), aktive Human-KI/20Hz nachgewiesen. Erstprobe NICHT qualifiziert: Harness hatte Heartbeat=0 und damit keinen GameSpy-Querylistener; Timeout trotz zwei echter Joins. Außerdem war CSV-#config vor dem späteren CLI-Skript geschrieben (falsches bot_enabled=0). Alle eigenen Prozesse/Mounts bereinigt; rohe Belege bleiben privat.
- 01:06 UTC: Header-Lifecycle-Regression RED→GREEN: GameMainLoop aktualisiert effektive Konfiguration nur bei Änderungen. 54 Benchmark-/Overlay-/Anschluss-Tests PASS, geschützte 13 Release-Hashes PASS. Isolierter Testserver aktiviert Querylistener mit ausschließlich lokalem Master 127.0.0.1. Dritter Build/Ein-Bot-Wiederholung folgt im selben abgeschlossenen CPU-Messfenster-Zwischenraum. Eigenen Controller 109275 vorübergehend angehalten; Benchmark 103292 ebenfalls T; Fortsetzung nach Probe zwingend.

- 08:59 UTC: Ein-Bot-Probe Build03 ausgewertet: echte Original-Retail-Gegenstelle, CRC, effektive Konfiguration, 20Hz/2643 Aktionen und NullRender nachgewiesen, alle Mounts sauber ausgehängt. Kein Bewegung-/Feuernachweis; daher Gameplay-Gate weiterhin OFFEN. Benchmark PID103292 nach Identitäts-/Lastprüfung fortgesetzt, letzte zwei Fenster laufen. PR45 mit effektivem Telemetrie-Fix auf cb7fa64 aktualisiert. Serialcontroller /srv/tse-integration-serial-20261021.py wartet auf vollständige Baseline, führt erst danach Suchpfad-RED/GREEN, Regressionen, Build04 und gestufte Laufzeittests aus.

- 09:30 UTC: CPU-Baseline mit sechs Fenstern abgeschlossen. Dritter Build d4f71d7 bestand 120s Join/CRC/20Hz/NullRender mit Original-Retail-Client, aber ohne Bewegung/Feuer. Suchpfad-Regressionsfall RED→GREEN: Driver erhält bestehenden Reiseinput/Hinderniserholung, ohne Gegnerpositionen zu nutzen; Policy bleibt unverändert. Neue DLL und erneute Runtime-Gates erforderlich.

- 09:45 UTC: CPU-A/B vollständig qualifiziert (sechs Fenster, 78,74% weniger Client-CPU / 66,85% weniger gesamte Test-cgroup). Quellstand des vorhandenen Runners gehört zu PR41-HEAD; SHA256 und Commit im CPU-Report. Suchpfad, vollständiger Munitionsadapter und phasenfester Kampf-Feuerzähler mit RED→GREEN bestätigt. 59 Benchmark-/Anschlusstests, 31 Parser-/Query-/Preflighttests sowie sieben C++-Suiten und realer Block-Smoke PASS. Build04 mit allen 15 MSVC-Quellen: 7fc94a39c3f5d9516f262d9e4d04a5cf38e6eb5ae3482976c32c952a99d30835, Quellbaum 9d7512dc2db395688f7ec0ec116b998d2f4cd764, veröffentlicht 65219c3. Ein Bot + Original-Retail 300s PASS: 6000 Tickspanne, Bewegung, 92 Kampf-Feueraktionen, Kill/Scoreänderung; Retail-Bildkontrolle zeigt Tod und normalen Respawn. Vier-Bot-Messung läuft, Legacy-Vergleich und Acht-Bot-Stunde folgen seriell über resume2-Controller. Beide öffentlichen Bot-DLLs weiterhin exakt 61dc27e0...; Originalserver unverändert, keine Sync-Kick-Überschreibung in Testskripten.
