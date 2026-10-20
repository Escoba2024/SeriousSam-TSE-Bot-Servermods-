# Alpha-Gaming – CecilBot-inspirierte Bot-KI: Ausführungsplan und Testnachweise

Stand: 20.10.2026. Hauptzweig: `main` bleibt unverändert.
Entwicklungsbranch: `agent/bot-ai-cecil-20261020` (Draft-PR #39).
Hetzner-Quellkopie: `/srv/tse-bot-ai-20261020` (ursprünglicher lokaler Commit `aa19d2c`).
CecilBotMod-Referenz: `953b477`, GPL-2.0.

## Implementiert

- [x] Bestehenden BotDriver, CPlayerAction, BotCore und parallele Liveprozesse geprüft; laufenden öffentlichen Hetzner-Server nicht verändert.
- [x] CecilBotMod-Kampflogik, Zielwahl, Ausweichverhalten, Waffenstrategie und Navmesh-Format als Referenz untersucht.
- [x] Unabhängig implementierte clientseitige Kampftaktik: stabile Gegnerauswahl, Gegnergesundheit, Waffenreichweite, Richtungswechsel/Strafing, defensiver Rückzug, drei Bewegungs-Schwierigkeitsstufen.
- [x] Opt-in-GameMP-Integration als Patch auf isolierte Quellkopie: `bot_bTacticalAI` ist standardmäßig AUS.
- [x] CecilBotMod BNMV-v6-Navmesh-Konverter mit neun Karten; gerichtete Kanten, Kapazität 512 Knoten und 16 ausgehende Kanten.
- [x] Herkunft und GPL-2.0-Attribution dokumentiert.

## Abgeschlossene Tests

- [x] Linux: alle acht portablen C++-Testprogramme bestanden.
- [x] Python: fünf Konverter-/Fehlerfalltests bestanden.
- [x] Strenge Kompilierung `-Wall -Wextra -Werror -pedantic` der neuen KI-Tests bestanden.
- [x] AddressSanitizer und UndefinedBehaviorSanitizer für taktischen C++-Test bestanden.
- [x] Alle neun konvertierten Karten als Textgraph importierbar; gerichtete Verbindungen validiert.
- [x] Originale Release-`BotDriver.cpp`-Datei auf Hetzner SHA256 unverändert (`b5d3290391b2504cce96529155b4072361fed0319a80ad1695707e36a9165c64`).
- [x] Windows/Shadow: vollständiger isolierter Win32-`Release_TSE107`-Build mit VS2022 BuildTools und gepinntem SE1-ModSDK erfolgreich.
  - Baseline-Rebuild SHA256: `D63769D99FDDCE1D8A3A730D384D8F0A070E5101D88DEF6AB29AE7E68B5022F6`.
  - **Neuer taktischer Kandidat** SHA256: `C65CB29BB17D9BE85CBC597D95C55E7ABE2A9D67C159ADE2735C096FDC6396D1`.
  - Native Build- und Compilerprotokolle lokal unter `C:\Users\Shadow\Documents\SeriousSam-TSE-TacticalBuild-20261020\isolated-build-20261020`; keine DLL veröffentlicht.
- [x] **Isolierter nativer Retail-1.07-/Shadow-Smoke, 75 s, 2 × 4 Bots**, Testprofil mit `bot_bTacticalAI=1`, `bot_iTacticalDifficulty=1`.
  - Harness-Meldungen: `Retail 2x4 fleet PASS`; `SHADOW FLEET PASS` (exit 0, gemessene Prozesslaufzeit des Wrappers 117,27 s inkl. Setup/Restore).
  - Serverlog: acht Join-Einträge, drei `CRC check OK`-Einträge, keine erkannten SYNCBAD-/`Too many bad syncs`-Marker.
  - Zwei BotClient-Logs: 657 `[BotTactical]`-Statuszeilen insgesamt, 77 Statuszeilen mit `strafe != 0`, 993 `[BotCombat]`-Zeilen, 20 dokumentierte Feuer-Snapshots, kein SYNCBAD-/Disconnect-Marker im untersuchten Logauszug.
  - Backup-/Restorebericht: `passed=true`, `nativeAccepted=true`, 817 mit `restored=true` markierte Einträge, null Restore- oder Cleanupfehler, null nachlaufende eigene Spielprozesse/Ports.
  - Evidenz privat im Shadow-Testverzeichnis `evidence-smoke-20261020`, inklusive `preservation.json`, `retail/diagnostics.json`, Client-/Serverlogs.
  - **Bedeutung:** kurzer nativer Gameplay-/Join-/Verhaltens-Smoketest erfolgreich, KEIN 60-min-Syncnachweis und keine Produktionsfreigabe.

## Weiter offen – Release-Schranken

- [ ] Längere deterministische 60-min-Laufzeitabnahme auf Retail/Wine mit CRC-/Sync-/CPU-/RAM- und externer Vanilla-Spielerprüfung; Tests gegen unveränderte Kontroll-DLL.
- [ ] Intensive Praxisprüfung von lateraler Bewegung (Vorzeichen, Boden-/Abgrundsicherung), Ausweichmanövern, Zielwechseln, Gegner-Sichtbarkeit und Schwierigkeit.
- [ ] Integration der Navmesh-Routen in den BotDriver **erst** mit Kartennamen-/Hashprüfung, beweglichen Türen, Sprüngen/Ducken, Gefälle und Absturzschutz; bisher nur Parser und Kartenimport, KEINE aktive Navmesh-Steuerung.
- [ ] Gegenstands-/Munitionssuche, Predictive Aim und weitere CecilBot-inspirierte Entscheidungen separat entwickeln und abnehmen.
- [ ] Kontrollierte Veröffentlichung nur nach vollständigen Gates, Backup und Rollback-Nachweis. Öffentlicher Hetzner-Server blieb unverändert.

## Wiederaufnahme

Erster Einstieg: `poc/experiments/tactical-ai/README.md`, `poc/botcore/bot_tactics.h`, Integrationstestprotokoll hier und Draft-PR #39.
Ein erfolgreicher Build oder 75-Sekunden-Smoke allein rechtfertigt keinen automatischen Rollout.
