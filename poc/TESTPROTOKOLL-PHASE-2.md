# Testprotokoll – Phase 2: 2 bis 4 lokale Bot-Spieler pro BotClient-Prozess

**Status: VORBEREITET, NICHT ABGENOMMEN.** Kein Pflichttest dieser Datei ist gelaufen; es existiert keine Phase-2-Runtime-Evidenz. Erst nach vollständigem PASS aller Pflichttests inklusive 60-Minuten-Gate gilt Phase 2 als bestanden und Phase 3 darf beginnen.

**Datum:** ____________  **Tester:** ____________
**Bot-Client:** GameMP.dll mit Phase-2-BotDriver ersetzt ☐ (SHA-256: ____________)
**Spielerprofile:** 2–4 eigene Profile im Bot-Client angelegt ☐ (Namen: ____________; je Profil eigene Character-GUID ☐)
**Bot-Start (2 Bots):** `SeriousSam.exe +connect <ip>:25600 +quickjoin +script Scripts\Phase2TwoBots.ini` ☐
**Beobachter:** unveränderter Vanilla-Client ☐ (Hash identisch zu Phase 0 ☐)
**Server:** unverändert, Original-Binaries ☐

> Gate der Design-Spec: mehrere lokale Spieler im selben Bot-Client, pro Spieler unabhängige Actions, GUID/Profile geprüft, Scoreboard/Playerstatus geprüft, Mapwechsel/Reconnect getestet. **4-Spieler-Prozess stabil, bevor Multiprocess (Phase 3) skaliert wird.**

## Reihenfolge

1. **Smoke-Test mit 2 Bots** (`Phase2TwoBots.ini`) – Pflichttests 1–9.
2. Erst nach PASS: **3 Bots**, dann **4 Bots** (`Phase2FourBots.ini`, `bot_ctLocalPlayers` anpassen) – Pflichttests erneut.
3. **Sync-Gate mit 4 Bots**: 10/30/60 Minuten in dieser Reihenfolge, danach unabhängige 60-Minuten-Wiederholung (frische Session), analog Phase-1-Gate E.

## Pflichttests (je Ausbaustufe 2/3/4 Bots)

| # | Prüfung | Erwartung | Ergebnis (PASS/FAIL) | Notiz / Beweis (Log) |
|---|---|---|---|---|
| 1 | Join mit n lokalen Spielern | Ein Prozess joint; Server-Log zeigt n× „Adding player …" + CRC check OK; Bot-Log: `[BotDriver] join configured for n local players` | | |
| 2 | Slot-/GUID-Eindeutigkeit | n unterschiedliche Player-Indizes und Profilnamen; `Test-Phase2MultiBot.ps1` PASS (Index-/Namensprüfung); Reconnect erkennt Characters wieder | | |
| 3 | Unabhängige Actions pro Bot | Jeder Bot eigene Positions-/Heading-Serie; kein Lockstep (`Test-Phase2MultiBot.ps1` Lockstep-Check, `bot_bVariants = 1`) | | |
| 4 | Scoreboard/Playerstatus | Vanilla-Observer sieht n Bot-Namen im Scoreboard; `\players\`-Query zählt jeden Bot genau einmal | | |
| 5 | Feuer/Schaden je Bot | Jeder Bot zeigt Feuerpulse; mindestens ein Frag-Ereignis pro getesteter Session dem richtigen Bot zugeordnet | | |
| 6 | Tod/Respawn je Bot | Jeder Bot stirbt mindestens einmal und respawnt mit fortgesetzten Actions | | |
| 7 | Mapwechsel | Nach Session-/Mapwechsel joinen alle n Bots erneut (kontrollierter Neustart zulässig wie Phase 1); CRC erneut OK | | |
| 8 | Disconnect/Reconnect + Slotfreigabe | Prozess-Stop gibt n Slots frei (`numplayers` sinkt um n); Neustart joint alle n wieder | | |
| 9 | Vanilla-Koexistenz | Unveränderter Observer bleibt parallel verbunden, keine Mod-/CRC-Meldungen | | |

## Harness

```powershell
# nach einem Lauf (Bot-Log = SeriousSam.log des Bot-Clients):
.\poc\scripts\Test-Phase2MultiBot.ps1 -BotLog <SeriousSam.log> -Output <neue JSON> -ExpectedBots 2 -QueryServer
# Telemetrie/Sync weiterhin mit Test-Phase1Telemetry.ps1 (Snapshots sind pro Spielerindex getrennt)
```

Unit-Regressionen des Harness: `Test-Phase2MultiBot.Tests.ps1` (muss vor der ersten Abnahme PASS sein).

## Sync-Gate (nur mit 4 Bots)

| Lauf | Dauer | CRC OK | Alle 4 verbunden am Ende | Aktive Minuten je Bot | Ergebnis |
|---|---:|---|---|---|---|
| 10 min | | | | | |
| 30 min | | | | | |
| 60 min | | | | | |
| 60 min Wiederholung (frische Session) | | | | | |

**Abbruchkriterien (Spec):** `MSG_SYNCCHECK`-Kick, sichtbarer Desync, Crash, Doppel-Entity/GUID-Kollision, Bot nicht als regulärer Spieler behandelt → Stufe stoppen, Ursache dokumentieren und beheben, dann neu.

**Ergebnis:** ☐ GATE BESTANDEN → Phase 3 (TESTPROTOKOLL-PHASE-3.md)  ☐ FAIL (Ursachenbericht)

## Bekannte offene Verifikationspunkte dieser Vorbereitung

- Der `CGame::JoinGame`-Anker (`BotDriver_ConfigureJoin`) ist gegen den ModSDK-Quelltext zu prüfen; `Build-RetailGameMP.ps1` bricht bei Abweichung hart ab (dann Anker anpassen und in VERIFIKATION.md dokumentieren).
- `gm_StartSplitScreenCfg`/`gm_aiStartLocalPlayers` steuern den nativen Split-Screen-Join; ob der Retail-`+quickjoin`-Pfad die Werte unverändert übernimmt, ist Runtime-Beweisziel von Pflichttest 1.
- GUID-Eindeutigkeit wird über getrennte Spielerprofile hergestellt; der Byte-Beweis (Server-Log/Netz) gehört zu Pflichttest 2.
