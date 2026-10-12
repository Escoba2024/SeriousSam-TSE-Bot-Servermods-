> Historisches Implementierungsprotokoll vom 10.–11.10.2026. Der separate Auftrag vom 12.10. autorisiert die überprüfte GitHub-/Drive-Synchronisierung. Aktueller Stand: `../../reports/2026-10-12-shadow-development-status.md`.

# Local bot release implementation plan

**Goal:** Deliver a usable local release of the existing combat/obstacle DLL with native eight-player qualification, reproducible source package and start/stop instructions.

**Architecture:** Preserve candidate 1A38F0A41583A11A0790CE91EEA2A86162B2B3B8E575204AB1360854BA6AF1E7 unchanged. A separate release build adds the native world/network mutex around timer AI entity/ray accesses after a reproduced eight-bot synchronization failure. Reuse the native fleet runner and preservation wrapper with an optional startup source. Validate real native actions independently; publish no retail assets and perform no external deployment.

**Execution:** Inline under the user's autonomous completion instruction. Preserve the current checkout and all earlier SDK builds; no reset, clean, commit or push.

## Acceptance

- Stock 1.07 dedicated server/observer/human binaries; eight distinct native PLC4+sidecar GUIDs in two separate four-player clients.
- A short native fleet run before the hour; then one uninterrupted 3700-second steady run and 60 complete 1200-tick windows per bot, after any controlled client replacement.
- AutoCombat and obstacle recovery enabled in every bot client; valid paired Nav/Combat/Driver data, real brush-triggered recovery and living combat. Legitimate no-target pauses are not forced periodic fire; report per-minute movement/fire and require native decisions/action continuity.
- Human join/leave/rejoin, actual eight-player names/query duration and CRC, no unexpected synchronization/runtime errors; owned-process cleanup and global original-file preservation.
- Source-only release ZIP, reproducible build/verification commands, production startup with sibling exclusion, validated fleet configuration and explicit installation/rollback instructions.
- Global routes, items, cliff safety, coop, internet hosting and 24/7 are not silently added to this release.

## Tasks

- [x] Extend native fleet startup input with early file validation; RED/GREEN invalid startup tests and existing Fleet regressions.
- [x] Create independent streaming fleet-AI audit and fixtures for missing ticks/actions, wrong identities/candidate, false obstacle success and insufficient hour/query span. Run native short fleet qualification, then hour.
- [x] Assemble source-only local release, validate archive/build sources, document final exact-DLL results and limitations, run final preservation and review.

## Ledger

2026-10-10: Baseline inspected; accepted obstacle DLL and earlier original-file hashes present. 216 GB disk free. Ruling: the old periodic-fire minute gate is retained for legacy mode; AI mode uses its own raw 20-Hz/decision audit because firing while no visible target would violate combat behavior. No hour success is inferred from prior DLLs.

2026-10-10: Native eight-short and eight-combat-only both failed with Too many bad syncs; all originals restored and owned processes/ports zero after each. Read-only review of Engine107 native disassembly confirms CCastRay's unsynchronized global sector scratch array and MainLoop's ga_csNetwork lock; timer AI previously did not hold that lock beyond GetLocalPlayerEntity. RED is the two actual native failures. Smallest hypothesis test is one RAII lock spanning timer entity accesses, ray construction/Cast/destruction, snapshot and action composition. Accepted SDK/DLL remains untouched. The apparent render ray references were inspected: they belong to PostMoving; no renderer lock added without evidence.

2026-10-11: The single-lock build709E passed195s but failed its hour attempt atA tick1846. Native renderer RVAED4D0 concurrently reads/writes the same full bsc_ulFlags word, potentially restoring a stale RAYTESTED0x40 despite casting no rays. Patch0007 adds a timer-hooks guard across GameRedrawView including recursive thumbnail/prescan scopes, preserving hooks1000 -> network2000. New isolated DLL61DC27E0E7B80BADCF9AE705C30FCA88EDD3935737715DFFFF59E90C26F1FEF9 needs fresh native qualification. Failed hour stopped explicitly; originals restored, zero processes/ports/crash events. Its inner diagnostics records existing stop-evidence protection after manual stop; failure remains unaccepted. A new steady-query assertion will fail immediately on lost slots rather than wait out a failed hour.


## Lokales Acht-Bot-KI-Release – 11.10.2026

**BESTANDEN:** Der aktuelle GameMP-Kandidat `61DC27E0E7B80BADCF9AE705C30FCA88EDD3935737715DFFFF59E90C26F1FEF9` ist lokal mit zwei getrennten Vier-Spieler-BotClients auf einem unveränderten TSE-1.07-Dedicated-Server geprüft. Die unabhängigen Serverabfragen umfassen 3697.291299s mit allen acht erwarteten Namen; 6 CRC-Annahmen. Der eigenständige KI-Auditor bestätigt 60 vollständige 20-Hz-Minuten pro Bot, insgesamt480 Fenster, native replizierte Bewegung, gültige begrenzte Eingaben und regulär abgeschlossene Brush-Advances von mindestens2m für jeden Bot. Der gesamte Observer-Lauf enthält 1124 bezeugte Kampfkills; diese Zahl ist nicht allein dem ausgewerteten Stundenfenster zugeordnet.

Menschlicher Join/Austritt/Rejoin und kontrollierter Ersatz eines BotClients wurden nativ geprüft. Das exakte sparsame Betriebsprofil `LocalBotRelease.ini` besteht einen zusätzlichen Lifecycle-Smoke mit 176.503899s unabhängigen Serverabfragen; dieser Smoke ersetzt keine zweite20-Hz-Stunde. Reale Vorbereitung und Rücknahme bestehen ebenfalls. Anschließend sind30 Original-Binärdateien,815 globale Dateizustände, die drei vorbestehenden geänderten Quellen und ältere abgenommene DLLs unverändert; null eigene Testprozesse oder Testports bleiben aktiv.

13 erfasste GameMP-Anpassungen und alle32 kompilierten Game-Quelldateien stimmen mit dem vollständigen frischen Quellbuild überein. Der neu gebaute DLL-Hash unterscheidet sich; ausschließlich der oben genannte Kandidat besitzt diese native Stundenabnahme. Anleitung: `poc/LOCAL-RELEASE.md`. Vollständige Belege: `.codex/evidence/shadow-20261010/local-release/report.md`. Ziel des getrennt verifizierten Quellarchivs: `.codex/evidence/shadow-20261010/local-release/SeriousSam-TSE-LocalBotRelease-20261011-source.zip`.

Die alten Sync-Fehler und die strengere KI-Ablehnung des kurzen61DC-Laufs bleiben erhalten. Abgenommen ist dieser lokale Fortress-Deathmatch-Meilenstein. Globale Wege, Item-Routen, Boden-/Abgrundsicherheit, weitere native Waffenfamilien, Coop, Internetbetrieb, zusätzliche Prozessskalierung, eine aktuelleKI-Mehrkartenstunde und24/7-Supervision bleiben eigene Folgeschritte. Kein Commit, Push, externe Veröffentlichung oder Google-Drive-Sync wurde ausgeführt.
