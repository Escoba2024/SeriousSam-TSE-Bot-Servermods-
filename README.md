# Serious Sam TSE 1.07 – Vanilla Bot Clients

Ziel dieses Repositories ist ein Bot-System für **Serious Sam: The Second Encounter v1.07**, bei dem der Dedicated Server und menschliche Spieler unverändert bleiben. Bots joinen über separate modifizierte Bot-Client-Prozesse als reguläre Netzwerkspieler und erzeugen ihre Eingaben ausschließlich über die normale `CPlayerAction`-/`CPlayerSource::SetAction`-Pipeline.

## Verbindliche Architektur

- Primärpfad: separater Bot-Client mit GameMP-only-Anpassung.
- Dedicated Server, `EntitiesMP.dll`, Engine und Vanilla-Observer bleiben unverändert.
- CecilBotMod ist Referenz für spätere KI-/Navigationslogik, nicht der produktive Netzwerkspieler-Pfad.
- Maximal vier lokale Spieler pro normalem Client-Prozess; Multiprocess-Skalierung ist eine spätere Phase.
- Vanilla-Kompatibilität, CRC/Join und Synchronität sind harte Runtime-Gates.

Die verbindliche Designspezifikation liegt unter:
`docs/superpowers/specs/2026-09-30-vanilla-server-bots-design.md`.

## Aktueller bestätigter Runtime-Stand

Der Windows-/Retail-PoC läuft gegen echte TSE-1.07-Retail-Binaries. Bestätigt sind derzeit:

- reproduzierbarer x86-`GameMP.dll`-Build mit Engine-Allocator-Anbindung;
- echter CRC-/Joinpfad gegen unveränderten Dedicated Server;
- unveränderter Vanilla-Observer gleichzeitig verbunden;
- native Bewegung, Rotation und Fire-Actions über den normalen Action-Composer;
- realer Schaden und Frag des Bots gegen den Vanilla-Observer;
- vier Bot-Death-/Respawn-Zyklen mit fortgesetzten Actions danach;
- zwei Session-/Mapwechsel mit kontrolliertem Reconnect und erneuter CRC-/Join-Abnahme;
- regulärer Shutdown von Bot, Observer und Dedicated Server.

**Phase 1: BESTANDEN.** Gates A–E sind für den Ein-Bot-Pfad bestätigt, einschließlich aktiver 10-/30-/60-Minuten-Sync-Prüfungen und einer unabhängigen 60-Minuten-Wiederholung. Ressourcen, Restore, Crashdiagnostik und DLL-Hashes sind dokumentiert.

## Nächste Phase

Phase 2 – **2 bis 4 lokale Bots pro BotClient-Prozess**. Zuerst zwei eigene Spielerprofile und native Split-Screen-/Join-Konfiguration prüfen; danach Slot-/GUID-Eindeutigkeit, Aktionen aller Bots und Sync. Phase 2 ist noch nicht abgenommen. Kontrollierter Reconnect nach Mapwechsel ist belegt; nahtloses Autoreconnect bleibt nicht belegt.

## Vorbereitungsstand Phase 2–7 (02.10.2026) – implementiert, NICHT abgenommen

Der komplette Umsetzungs-/Testpfad für die Folgephasen ist vorbereitet; **keine** dieser Phasen hat Runtime-Evidenz, alle Gates sind offen:

- **Phase 2:** BotDriver mit `bot_ctLocalPlayers 1..4` (nativer Split-Screen-Join via `BotDriver_ConfigureJoin`), per-Bot-Varianten; `Phase2TwoBots/FourBots.ini`; Harness `Test-Phase2MultiBot.ps1` (+ Unit-Tests); `poc/TESTPROTOKOLL-PHASE-2.md`.
- **Phase 3:** Fleet-Orchestrierung `Start-/Stop-BotFleet.ps1` + `fleet-config.sample.json`; `poc/TESTPROTOKOLL-PHASE-3.md`.
- **Phase 4:** engine-freie KI in `poc/botcore/botcore_ai.h` (Zielwahl, Waffenbänder, Waypoint-Fallback, Stuck-Erkennung; standalone getestet) + `bot_iAiMode = 1`-Integration im BotDriver; `Phase4Ai.ini`.
- **Phase 5:** Population Manager (`Manage-BotPopulation.ps1`, Regeln gespiegelt und beidseitig unit-getestet in `botcore_ai.h`/`PopulationCore.ps1`): Zielpopulation, Human-Priorität, reservierte Slots.
- **Phase 6:** Presence/Chat (gejitterte Join-/Leave-Delays, niederfrequenter Chat über `CNetwork::SendChat`, Namens-/Chat-Pools); `Phase6Presence.ini`.
- **Phase 7:** Multi-Server-Farm (`Start-/Stop-ServerFarm.ps1`, `serverfarm-config.sample.json`, getrennte Ports/Bot-Gruppen/Populationen).

Abnahmeordnung unverändert streng sequenziell: Phase 2 Smoke (2 Bots) → 4 Bots + 60-Minuten-Gate → Phase 3 → … → Phase 7; Protokolle in `poc/TESTPROTOKOLL-PHASE-2.md`, `-PHASE-3.md`, `-PHASE-4-7.md`. Alle neuen BotDriver-Symbole sind per Default inaktiv; das belegte Phase-1-Verhalten bleibt unverändert.

## Einstieg für Entwickler / KI

1. `CODEX_WINDOWS_POC_REPORT.md` – aktuelle Runtime-Evidenz, Buildpfad, Hashes, Tests und offene Gates.
2. `docs/superpowers/specs/2026-09-30-vanilla-server-bots-design.md` – Architektur und Phasenmodell.
3. `poc/RUNBOOK.md` – reproduzierbarer Build-/Testablauf (inkl. Phase-2–7-Kit).
4. `poc/VERIFIKATION.md` – Quellcode- und Protokollverifikation (inkl. Phase-2/4/6-Integrationspunkte).
5. `poc/patch/gamemp/` – GameMP-seitiger BotDriver und Retail-Allocator.
6. `poc/botcore/` – engine-freie Action-/KI-/Populationslogik mit Standalone-Tests (`make test`).
7. `poc/scripts/` – Build-, Runtime-, Telemetrie-, Fleet-, Population- und Farm-Skripte.

Lokale Retail-Kopien, Buildprodukte, Screenshots/TGAs und Runtime-Evidenz unter `.codex/` gehören nicht ins Repository.

## Aktueller nächster Meilenstein

Phase 2 mit zwei lokalen Bots beginnen, anschließend auf drei/vier erweitern und separat abnehmen. Aktuelle Phase-1-Evidenz im technischen Bericht und Testprotokoll.
