# Bot-Respawn — gezielter Quellcode-Fix und Handoff (31.10.2026)

## Scope und Ausgangsstand

- Auftrag: Letzte Arbeit an „Repariere Bot-Respawn“ fortsetzen, Bot-Clients für Serious Sam TSE Classic 1.07 / ssam.ai, Red Station.
- Ausgangsbasis: veröffentlichter GitHub-Draft PR #91, Branch `agent/publication/20261031-m2m3-redstation`, SHA `dc64cc6c814f62088d0cd413173affa360c21022`. Dieser Branch enthält **nicht** alle lokalen Änderungen des späteren Kimi/OpenCode-Laufs.
- Neuer isolierter Branch: `agent/chat/20261031-respawn-missing-entity`.
- Letzter dokumentierter OpenCode-Task `1d3a50085397c8d9da6d57db` endete am 31.10.2026 mit Exit 1, „Go usage limit exceeded“. Separate lokale Worktrees `ssam-m2m3-native-20261031` und `ssam-m2m3-native-build-20261031` bleiben unverändert.
- Die lokale Version von `poc/ai-integration/gamemp/BotDriver.cpp` hatte beim letzten Read SHA-256 `b4294bf7fe8dc1babac4fa68c92cdd2bf58752abdf2aa01332235fb6900178fa` und 940 Zeilen; ihre Respawn-Logik enthält bereits `BotDriverNeedsRespawn` und V2-Policy. Sie wurde **nicht überschrieben oder integriert**.

## Statischer Befund / Hypothese

Die veröffentlichte `BotDriver.cpp` überspringt bei `localInput == NULL` die gesamte Action-Erzeugung. Nach dem Tod/Wechsel zur Zuschauer-Entity kann damit auch bei bestehendem `CPlayerSource` keine Fire-Press/Release-Flanke gesendet werden. Zusätzlich war der periodische Feuer-Takt als Voraussetzung für den Legacy-Respawn aktiv. Der exakte Fehlerzustand des produktiven Servers wurde nicht mit einem synchronen nativen Trace reproduziert; daher ist dies ein begründeter Quellcode-Fix, **noch keine bestätigte Runtime-Ursache**.

## Änderungen

1. `BotDriver.cpp`: Für einen bereits zuvor verbundenen Source ohne lokale Entity nur im automatischen Frag-/Scorematch eine begrenzte `CPlayerAction` mit alternierenden Fire-Press/Release-Flanken senden. Initialen Join, manuelle Steuerung und andere Modi ausnehmen. Die Original-Server-Binaries unverändert lassen.
2. `BotDriver.cpp`: `player==NULL`, `health<=0` oder fehlende Waffen-Entity als Respawn-Kandidat erkennen; Respawn-Puls auch bei ausgeschaltetem Kampf-Feuerintervall unabhängig erzeugen.
3. `poc/botcore/botcore.h`: deterministische `BotDriverRespawnPulse()` und `BotDriverMissingEntityRespawnEligible()` als enginefreie Helfer.
4. `poc/botcore/test_botcore.cpp`: Tests für initialen Join, manuell, Nicht-Deathmatch, etablierte Quelle und 40-Tick-Flanken.
5. Strenge Trennung: keine Änderung an Vanilla Dedicated Server, Original-Retail-Client, produktiver DLL, anderen Agent-Worktrees oder `main`.

## Bisherige Prüfungen

- GitHub Compare gegen PR #91-Basis: ausschließlich drei C++-Dateien geändert, anfangs +61/-4 Zeilen, keine anderen Projektpfade.
- Neuer 40-Tick-Helfertest ist als C++-Quellcode angelegt (erwartet 20 Fire-Ticks, 6 Press-Flanken und 5 Release-Flanken), aber **ein tatsächlich ausgeführter Compiler-/Testlauf dieses neuen Branches ist nicht nachgewiesen**. Die Erwartung am Tick-40-Rand wurde durch Codeprüfung korrigiert.
- Bestands-Botcore-Qualitätsgate auf Ubuntu via ssam.ai System Control: **PASS** für bestehende Botcore/Human-AI-Suiten (u.a. 555 Checks), jedoch **nicht** auf diesem neuen GitHub-Branch.
- GitHub Commit-CI: keine Status-Checks zurückgegeben.
- Native MSVC-x86-`GameMP.dll`-Build, Game-/Wine-Integration, echte Red-Station-Death/Respawn/Return-to-Combat-Sequenz, Bot-SYNC/CRC, Originalclient-Join: **NICHT AUSGEFÜHRT**.
- RDC-Verbindung online, aber Monatslimit blockiert Befehle; ssam.ai Test MCP meldet `native_tests_allowed=false`. Ein GitHub-Clone in der isolierten Codeprüfung schlug ohne DNS/Netzwerk fehl.

## Erforderliche Abnahme vor Integration oder Rollout

1. GitHub-Branch gegen **neueren lokalen Kimi-Build-Worktree** reviewen/rebasen/cherry-picken; V2-Respawn-Heuristik nicht duplizieren. Zuerst saubere lokale Worktrees sichern.
2. Das geänderte `BotDriver.cpp` mit der tatsächlichen privaten 1.07-MSVC-x86-Buildkette kompilieren, DLL SHA und 42/42 Inputs dokumentieren.
3. Offline-Tests auf **diesem** Code/Commit durchführen (`make test` plus geeignete native Tests); keinen PASS aus dem alten Quellstand übernehmen.
4. Privates isoliertes Original-Retail-1.07-Red-Station-Death→Respawn→Kampf-Szenario für alle relevanten Bot-Client-Konfigurationen ausführen; prüfen, dass Fire beim Nicht-Deathmatch und initialen Join nicht unerlaubt emittiert wird.
5. Originalclient und Sync/CRC prüfen, Recovery, CPU/RAM/Plattenreserve und exklusive Lease sauber dokumentieren. Die M1-Acht-Bot/120-Minuten-Abnahme bleibt ausgesetzt.
6. Review + Rollback/Backup, vor jedem öffentlichen DLL-Ersatz ausdrückliche Freigabe. **Kein Merge, kein Live-Deployment** allein auf Basis dieses Kandidaten.

**Status: QUELLCODE-KANDIDAT / STATIC_REVIEW_PENDING / NATIVE_QA_BLOCKED / NOT_RELEASED.**
