# Testprotokoll – Phase 3: Multiprocess / Skalierung

**Status: VORBEREITET, NICHT ABGENOMMEN.** Voraussetzung: Phase 2 vollständig bestanden (4 lokale Bots stabil inkl. 60-Minuten-Gate). Keine Phase-3-Runtime-Evidenz vorhanden.

**Datum:** ____________  **Tester:** ____________
**Fleet-Konfiguration:** `fleet-config.sample.json` kopiert und angepasst ☐ (Pfad: ____________)
**Bot-Client-Installationen:** je Prozess eine eigene isolierte 1.07-Installation mit eigenen Profilen ☐
**Server:** unverändert ☐  **Beobachter:** unverändert ☐

> Gate der Design-Spec: 2 Bot-Client-Prozesse × bis zu 4 Spieler, danach schrittweise erhöhen; parallel echte menschliche Clients joinen/leaven lassen; CPU/RAM/Netz messen; Serverbrowser-Live-Query prüfen.

## Reihenfolge

1. 2 Prozesse × 4 Bots (8 Bots) – Pflichttests 1–8.
2. Erst nach PASS schrittweise erhöhen (3×4, dann weitere), bis Zielgröße oder Ressourcengrenze; jede Stufe separat protokollieren.
3. 60-Minuten-Soak auf der Zielstufe mit parallelem menschlichem Join/Leave.

## Pflichttests (je Stufe)

| # | Prüfung | Erwartung | Ergebnis (PASS/FAIL) | Notiz / Beweis |
|---|---|---|---|---|
| 1 | Gestaffelter Fleet-Start | `Start-BotFleet.ps1` startet alle Prozesse mit Stagger; kein Join-Burst-Fehler im Server-Log | | |
| 2 | Alle Bots verbunden | `\status\`: numplayers = Summe lokaler Bots (+ Observer); jeder CRC-Check OK | | |
| 3 | Eindeutigkeit über Prozesse | Alle Bot-Namen/GUIDs prozessübergreifend eindeutig (getrennte Installationen/Profile) | | |
| 4 | Menschlicher Join/Leave parallel | Vanilla-Client joint und leavt mehrfach ohne Fehler, während die Flotte läuft | | |
| 5 | Ressourcen | CPU/RAM je Prozess und Server über die Stufe protokolliert (Vergleichsbasis: Phase-1-Werte ~20 MB Server, ~170–180 MB Client) | | |
| 6 | Serverbrowser-Live-Query | Direkt-IP-/GameAgent-Abfrage zeigt korrekte Spielerzahl, gamever 1.07, activemod leer | | |
| 7 | Fleet-Stop | `Stop-BotFleet.ps1`: bevorzugt `graceful` (Exitcode 1 + Quit-/Cleanup-Marker); `forced` im Protokoll vermerken | | |
| 8 | Slotfreigabe nach Stop | `numplayers` fällt auf Ausgangswert; erneuter Start joint vollständig | | |

## 60-Minuten-Soak (Zielstufe)

Start: ____________  Ende: ____________  Prozesse × Bots: ____________

| Zeitpunkt | numplayers | CPU/RAM auffällig? | Sync/Kick/Crash? |
|---|---|---|---|
| 0 min | | | |
| 15 min | | | |
| 30 min | | | |
| 45 min | | | |
| 60 min | | | |

**Abbruchkriterien:** wie Spec (SYNCCHECK-Kick, Desync, Crash, GUID-Kollision, Bot nicht regulär) sowie Ressourcen-Runaway (monotoner RAM-Anstieg ohne Plateau).

**Ergebnis:** ☐ GATE BESTANDEN → Phase 4 (TESTPROTOKOLL-PHASE-4-7.md)  ☐ FAIL (Ursachenbericht)

## Harness

```powershell
.\poc\scripts\Start-BotFleet.ps1 -Config <fleet.json> -State <neue state.json>          # Start
.\poc\scripts\Test-Phase2MultiBot.ps1 -BotLog <je Prozess> -Output <JSON> -ExpectedBots 4 # je Prozess
.\poc\scripts\Stop-BotFleet.ps1 -State <state.json>                                      # Stop
```

Unit-Regressionen: `Test-FleetAndPopulation.Tests.ps1` (Konfigvalidierung, Planaufbau, Dry-Run) – vor der ersten Abnahme PASS.
