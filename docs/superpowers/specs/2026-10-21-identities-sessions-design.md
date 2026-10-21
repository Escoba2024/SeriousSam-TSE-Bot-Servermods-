# Dauerhafte Botidentitäten und Sitzungen – Entwurf
Datum: 2026-10-21. Status: ENTWURF / NICHT PRODUKTIV QUALIFIZIERT.

## Auftrag und Grenzen
Fiktive dauerhafte Identitäten, wenige lesbare Farben, feste Human-KI-Profile und unabhängige Sitzungen. Nur Hetzner; öffentliche acht Bots, Originale und fremde Qualifikation erhalten. Kein Merge und keine produktive Aktivierung. Die direkte Benutzeranweisung autorisiert autonome Umsetzung ohne routinemäßige Entwurfsfreigaben.

## Bestätigte Ausgangslage
main fdfc46e enthält PR #45. Build04 SHA256 7fc94a39c3f5d9516f262d9e4d04a5cf38e6eb5ae3482976c32c952a99d30835. PR #46 (Draft, d6d2911 bei Prüfung) besitzt tools/operations/fleet_supervisor.py und fleet_health.py; dessen native Qualifikation läuft auf 26820/26821. Öffentliche 8/16 auf 25600/25601 mit frischer Telemetrie, eigene Syncfehler 0; historischer EXTERNAL_CLIENT_SYNC-Alert separat. Host 2 vCPU / 3819 MiB, ca. 16 GiB freie Platte.

## Architekturentscheidung
Vorhandene fünf Skillstufen/sechs Personas, Wahrnehmung, Aim, Waffenwahl und CPU-Optimierungen erhalten. Keine parallele KI. Neuer portabler Python-Kern unter tools/bot_sessions.py mit SQLite-Transaktionen: gemeinsamer Pool, beständige GUID/Seeds, je Identität genau ein Zustandsdatensatz, serverübergreifend atomare Entscheidung. Alle Instanzen müssen dieselbe lokale Datenbank verwenden. Separate deterministische Zufallsströme aus Seed, Identität, Zweck und persistiertem Zähler. Keine Engine-Zufallsquellen.

OFFLINE -> WAITING -> JOINING -> PLAYING -> LEAVING -> COOLDOWN. Erfasste Ereignisse trennen planned, crash, disconnected, admin und human_capacity. Neustart übernimmt persistierte Zustände; JOINING/LEAVING erzeugen keinen zweiten Auftrag. Ein Runtime-Adapter muss diese Zustände vor neuem Spielstart mit tatsächlichen eigenen Prozessen/Verbindungen abgleichen. Geplante Abmeldung darf niemals im alten Supervisor als vermisster Pflichtslot erscheinen.

Pool-Konfiguration enthält interne ID, bereinigten sichtbaren Nickname, optionale RGB-Farbe, bestehenden Rosterindex (0..7), Gewicht für Stammspieler. Eine lokal gespeicherte GUID und gameplay_seed bleiben erhalten. Keine Namensübernahme aus Live-Queries; diese dienen ausschließlich Kollisionsprüfung. Sichtbare Namen sind im ganzen Pool case-insensitiv eindeutig. Farbsyntax und Retail-Grenzen bleiben NATIVE GATES: konservative eigene Caps sind keine Behauptung über Retail-Maximalwerte.

Sitzungen: konfigurierbare gewichtete Zeitbänder, standardmäßig 80% 20–90 min, 10% kürzer, 10% länger. Mindestpause 15 min. Globale Join-/Leave-Raten und pro Server höchstens ein laufender Join/Leave. Menschenplätze sind echte Reserve. Unsichere/veraltete Abfragen blockieren neue Beitritte. Admin-Off hält den Server offline bis explizitem Enable.

## Runtime-Optionen und Abwägung
1. Einzelne Verbindung je eigenem Prozess: verwendet vorhandenen regulären Quit-/Join-Pfad, aber 8/16 Prozesse statt 2/4 erfordern neue CPU/RAM-Messung.
2. Mehrere Slots pro Prozess: sparsamer; echter Retail-Einzelabmeldepfad nicht belegt (Network.h: AddPlayer_t, kein RemovePlayer). Nicht durch direkte Speicheränderung oder fremde ABI ersetzen.
3. Gleichzeitiger Prozessgruppenwechsel erfüllt unabhängige Sitzungen nicht und wird verworfen.
Der portable Kern schreibt nur Intent-Datensätze. Keine Runtime-Anbindung als fertig ausgeben, bevor die Variante nativ qualifiziert ist. Keine konkurrierende Änderung am aktiven PR-46-Supervisor.

## Abnahme
Unit-Tests: Sanitizing, sichtbare Kollisionen, stabile GUID/Seeds, DB-Neustart, SQLite-Doppelcontroller, reproduzierbare Intervalle, Zustände, Pause, Join-/Leave-Limits, Menschenreserve, Admin-Halt, geplantes Ende vs. Crash.
Native Gates: Farbnamen in HUD/Meldung/Query, echte individuelle Join/Quit/Rückkehr, Crash getrennt; 8 dann 2x8, >=3600 s gemeinsame Stabilität, normale und beschleunigte Zeiten getrennt, Baseline CPU/RAM/20Hz/SYNCBAD/Disconnect/Restart, vergleichbare Gameplay-Metriken und vollständiger Restore.
Keine KI-Verbesserung aus Unit-Tests ableiten. Item-Navigation und Orientierungs-/Entscheidungspausen erfordern zusätzliche gezielte Integration und native Abnahme.

## Blocker / nächster kleinster Schritt
Fremde laufende PR-46-Qualifikation (PID 135203, Supervisor 135705; Momentaufnahme) misst 3600 s. Keine neuen Retail-Experimente, Builds oder Lastbenchmarks daneben. Nach deren Abschluss frischen Prozess-/Port-/Ressourcencheck und Supervisor-Schnittstelle festhalten; dann eigenen Einzelverbindungs-Smoke mit PID/start/CWD/cgroup-Gate auf eigenen Ports durchführen. Nicht fremde Prozesse stoppen.
