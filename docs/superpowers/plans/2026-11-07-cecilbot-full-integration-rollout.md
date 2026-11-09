# CecilBot full integration and fleet rollout implementation plan

> **For agentic workers:** Use executing-plans task by task. Only the main agent integrates, builds native candidates, controls runtime or publishes.
**Goal:** All compatible Cecil subsystems implemented and qualified, then active on every verified project server.
**Architecture:** Read-only native snapshots feed a single per-bot planner/combat owner. Full directed Cecil data stays private; ordinary CPlayerAction is composed once. Preserve Human aim/hysteresis/loadout safeguards.
**Tech Stack:** Existing C++17 botcore, Retail 1.07 MSVC x86 under Wine, Python stdlib tooling, systemd.
**Spec:** Full authorized user request preserved privately at .codex/evidence/request.txt; pinned analysis 24b8c8cd46f44781c84f97fd348fb9d1df155646.

## Global constraints
- Dedicated/Engine/Entities and human clients unchanged; no custom packets, detours, authoritative entity writes or sync bypass.
- Develop/build/test on Hetzner. At most two additional agents, isolated worktrees and explicit file ownership.
- Qualify final hash: 1 bot >=3600s, 4 >=3600s, 8 >=7200s, then recovery. Behavior changes invalidate affected gates.
- All six servers included, production population remains eight each; retain names, ports, maps and rotations.
- At least 8 GiB free disk. No purchases, host reboot, unrelated merges or deletion of others' work.
- Restart, commit, push and normal integration authorized by this request; earlier analysis-only and production-hold instructions superseded for this qualified rollout.
- NAV datasets/private logs/binaries never published; retain GPL attribution, exclude CPOL patcher.

## Verified starting point — 2026-11-07 16:27 UTC
- Remote main ab0c7400353a108f8461bb82280c539fdfe81499 and analysis 24b8c8c verified by ls-remote. Drive three current documents read and captured.
- Isolated /srv/tse-cecil-full-20261107, codex/20261107-cecil-full based ed08e2c8efc9366e880da274e70acab53f8bf2a5.
- Existing source worktree contains untracked regression log/test binary: preserved untouched.
- Five production instances 25600/10/20/30/40, maps Red Station/Yodeller/Skulls/Little Trouble/Hole, all Fragmatch, eight bots. Red Station query additionally shows one player; classify against profile IDs before runtime changes.
- Development 25650 Red Station, eight bots. Six dedicated processes and twelve bot processes verified by /proc cwd, maps, cgroup.
- Production bot DLL 7fc94a39c3f5d9516f262d9e4d04a5cf38e6eb5ae3482976c32c952a99d30835; development ce559971ce4a1677c1b299a7d0c27f148fa4ecace2a55d45e006bdb1598ac6a4.
- Full private machine-readable baseline: .codex/evidence/fleet-before.json. Mapped paths observed; disk inode/hash identity still to cross-check before replacement.
- ~80.9 GiB disk free, 3.4 GiB memory available in initial snapshot. Not a load qualification.
- Current Source/NavV2 graph is symmetric, capacity 256, lacks original metadata. Do not label it full Cecil navigation.

## Review focus
1. Map changes or stale entity IDs must invalidate paths/targets before output.
2. Current/requested weapon mismatch must prohibit fire; NONE and inventory masks must never shift negatively.
3. Directed teleport/locked routes must preserve metadata and reject unsupported native transitions explicitly.
4. Occluded/wrong-floor/disappeared items must not monopolize goals; bounded sensors must retain fairness.
5. Runtime restart must preserve identities and await own slot removal; external players excluded from instrumentation.

## Responsibilities and claims
- Main: source consolidation, native BotDriver/BotSupplyNative and action composition, build/deployment/monitoring, documentation/integration.
- nav_audit: currently read-only NAV audit; implementation only after separate worktree/file claim.
- combat_audit: currently read-only combat/item/preset audit; implementation only after separate worktree/file claim.
- No other agent may modify runtime or main integration worktree.

## Task 0 — source and fleet baseline
Files: this plan; docs/reports/2026-11-07-cecil-deployment.json; private .codex/evidence.
- [x] Read request, repository policy, current Drive docs, pinned analysis documentation/verification.
- [x] Inspect current remote refs/open PRs, local worktrees, processes and fleet.
- [x] Create isolated integration worktree without disturbing existing changes.
- [x] Complete map/rotation/config/roster/source/build cross-check; preserve precise baseline.
- [x] Run existing botcore and supply regression tests; record failures before changes.
- [x] Reconcile PR54/55/57/69/91/97 and current dev snapshot; freeze actual file ownership/interfaces.

## Task 1 — complete Cecil data and directed search
Files: candidate enginefree Cecil NAV headers/tests; existing strict parser/export tools reused.
- [x] Test all nine byte roundtrips, malformed schema, >256 points, slot vs ID, flags/radii/lockorigin/polygon preservation.
- [x] Implement complete persistent data and per-bot directed optimal search; TELEPORT zero cost, explicit lock snapshot, no global search state.
- [x] Compare all 193x193 Red Station pairs against independent reference including unreachable/self pairs and lock variants.
- [x] Pin map content hashes and original NAV hashes; load/publish outside timer lock.
- [ ] Native anchor/floor/LOS, point arrival/important chains, replan and normal jump/crouch/strafe/teleport transitions.

## Task 2 — weapons, items and presets
Files: existing Human/loadout/combat policy plus pure Cecil policy headers/tests; BotSupplyNative.
- [x] Pin original 30 weapon rows and four presets with source attribution, explicit versioned config.
- [x] Reproduce pickup/selection mismatch; unify capability, inventory/ammo, range/self-damage and selection (portable contracts; native weapon scenarios remain below).
- [x] Typed item snapshots: weapon, health, armor, ammo/pack, powerup; per-item LOS, availability/generation and cooldown.
- [x] Test nearest unsuitable health, distant ammo pack, overlapping conditions, floors and deleted/respawned items.
- [x] Preserve Human hysteresis/dwell/projectile lead and retreat; deterministic Cecil comparison and documented bug corrections.

## Task 3 — one native policy and action path
Files: candidate BotDriver.cpp, BotSupplyNative.h, enginefree decision state and tests.
- [ ] One state owner, bounded snapshot/ray work, per-bot RNG and lifecycle reset on death/respawn/rejoin/map.
- [x] Combine navigation/items/combat through one final composer and WeaponInput poll.
- [x] Current weapon profile fire gate, grenade hold/release, scope buttons, travel/combat and respawn.
- [ ] Validate units/tick variation, team/target CD/sightloss and safe output at stale snapshots.
- [x] Account for every one of 41 transfer areas, including necessary D adapters, E client alternatives and U evidence.

## Task 4 — build and native qualification
Files: existing build tool, native candidate manifest, isolated evidence/qualification runner.
- [ ] Verify SDK/compiler/x86/imports/CRT boundaries; build from committed exact sources, record every input hash.
- [x] Baseline-defined scenarios and thresholds BEFORE candidate measurement: movement/fire <=5s alive, unjustified idle <=10s; defined item set >=90%; first useful weapon median <=15s/P95 <=30s; current-weapon switch within CD; 100 deaths group; zero new sync/CRC/join failures; resource delta <=20% vs comparable baseline.
- [ ] Development smoke: joins/spawns/motion/pickup/switch/fight/score/death/respawn/map change, original Retail client joins and plays.
- [ ] Verify every operated map separately; no Red Station coordinates elsewhere.
- [ ] Final-hash 3600/3600/7200s gates, evaluate complete time series and recovery; no shortened substitutes.
- [ ] A/B/C source fixtures + native baseline/candidate, three comparable windows; original mod reference separately if available, document concrete limitation otherwise.

## Task 5 — fleet rollout and release
- [ ] Independent whole-change review, address blocking findings, required tests.
- [ ] Per-instance rollback manifest: binaries/configs/nav/units/profile identities, verify backups.
- [ ] One production canary then remaining servers serially; preserve identity/map/population and confirm mapped DLL/config/nav/policy and activity.
- [ ] On regression stop expansion, restore affected instance, fix/requalify then resume all.
- [ ] Entire six-instance simultaneous CPU/RAM/disk/sync/behavior check and external reachability.
- [ ] Commit/push and integrate through repository process; update Drive protocol/handoff/reviewboard + weekly report.
- [ ] Final server table, first join address, tested improvements, GitHub evidence and rollback locations.

## Current status and next action
IN_PROGRESS / CANDIDATE036 SUPPLY P95 FAILED; LIFT COMMITMENT LOSS REPRODUCED (09.11.2026). Normal036 source2f216fe5/DLLd3889413 includes the reviewed original Cecil physical-mask helper. It completes ten fresh60s supply joins with9/10 matching acquisitions, median10.475s and P9531.60s, which fails the unchanged30s threshold. No full1/4/8 duration gate starts for036. Hole600 and a separate four-bot Red600 pass limited functional observations; LittleTrouble600 also completes without recognized errors. These results do not qualify the candidate or another DLL.

Native diagnostic037b reproduces two exact supported moving-platform lock transitions. The bot is STAND on typed MovingBrush9, already committed toward hop2 but outside its original1m arrival radius; a newly observed closed hop drops commitment and reverses toward anchor180. Same-goal/life follow-up and distant/reference controls distinguish this from false NoFloor or real relocation. See lift-commitment report. Its completed600s diagnostic is not a normal-source acceptance window.

Next normal038 preserves only that existing original directed approach under validated current typed platform contact and <=min(2*pointRadius,2m) proximity; original arrival radius/global locks/deadlines remain unchanged. Strict current-support loss forces immediate ordinary replan, with no one-second or NULL-reference grace. Complete portable/native-contract checks and independent review, publish exact clean source and build normally. Then all new unchanged supply, five-map,3600/3600/7200-second, resource, original-Retail, weapons/special-action/health-death and recovery gates. Separate isolated fixtures can run full windows concurrently after genuine supply/Hole prerequisites; no durations or thresholds are reduced. Final six-instance rollout and900s simultaneous fleet observation, source integration and Drive/weekly/matrix remain required. Public five production and development013 binaries remain unchanged, verified again16:31 UTC.

## Frozen core interfaces and implementation claims — 16:31 UTC
- NAV agent exclusive /srv/tse-cecil-nav-20261107, branch codex/20261107-cecil-nav: candidate/cecil_nav_data.h and test_cecil_nav.cpp plus private test evidence. CecilNavGraph::Load(bytes,size,error), points retaining id/x/y/z/radius/flags/important_entity/next_slot/lock_entity/lock_origin/polygon/links. CecilNavSearch::Prepare(n) outside timer, Run(graph,start,blocked,count), NextHop(goal), Distance(goal). No allocations in Run, h=0 Dijkstra explicit teleport correction. Strict original BNMV v6, all nine datasets, defensive size limits >=335 points.
- Rules agent exclusive /srv/tse-cecil-rules-20261107, branch codex/20261107-cecil-rules: candidate/cecil_rules.h and test_cecil_rules.cpp plus private fixture evidence. CecilWeapons/CecilWeaponAt/CecilWeaponScore/CecilBestWeapon; CecilSettings/CecilPreset; typed CecilItem/CecilItemInput/CecilChooseItem; CecilFireState with current/wanted/desired gating, grenade cycle and scope. No native file edits.
- Main exclusive native adapter/driver and existing Human/loadout integration. Header-only pure cores permit x86 compilation without new dependencies.
- Native actual map content: Engine107 GetFileCRC32_t on GRO-resolved map plus private SHA256 provenance. Do not reuse mutating Nov04 FloorProbe.
- Existing botcore nine test binaries PASS, including 555 Human checks. Existing supply test PASS with pre-existing compiler maybe-uninitialized warnings in SupplyPlanner.
- Ruling: PR55/69 contracts reused conceptually, not wholesale competing planner import; their incomplete generation/ammo/health assumptions conflict with required native snapshots. Full NAV data/search needed because both existing graph variants lose direction/metadata.

## Milestone — 07.11.2026, 17:14 UTC
- Full nine-NAV lossless parser and directed h=0 search: 221682 checks; source TELEPORT edges keep zero cost. No coordinate payload published.
- Original 30 weapon rows and four presets, typed native item snapshots, Human target-CD/aim integration, one final action and weapon-selection path.
- Review-driven corrections: double Colt, stale entity/death state, final-motion floor validation, retry TTL, unreachable stays bounded to two seconds, frozen target follow, actual Swim/Dive snapshots, two-second travel knife delay, team filtering.
- 67 native-bridge fixture checks and 555 existing Human checks pass. Feedback-loop test reproduced and fixed aim-envelope fire starvation. These are offline evidence.
- Build003: fifteen translation units, PE32 x86, pinned SDK/includes, source-only reproducible overlay, no new runtime dependencies beyond existing MSVC CRT. Runtime qualification remains open.
- Normal USE/Marker alternative is being implemented because original Player::UsePressed supports it through regular action buttons. Direct SendToTarget remains excluded.
- Private transactional development installer and read-only qualification monitor prepared. Current fleet remains unchanged.
- Original Cecil B runtime is not built: original v60/v120 toolsets are absent, current v143 would require a separate Entities build/ABI qualification. Source/fixture comparison is available; no measured complete behavioral identity claimed.

## Milestone — 17:55 UTC, functional evidence and required gravity correction
- Build006 final smoke on RedStation:600.008s, eight active slots,66deaths+66respawns, no monitor errors. CPU below clean baseline; not one of the mandated long gates.
- Offline analyzer flags long quiet stationary windows (B2~36s/B3~25s). NativeHuman intended forward movement while composed axes were zero. Floor-veto hypothesis will be measured explicitly; proposed recovery accepts only another real supported floor ray within the unchanged16-ray budget.
- Skulls006 diagnosis:600.008s, all eight moved/fired, no monitor errors, but uneven/stalled navigation. CPU window includes compilation and is not a resource qualification. No inverted-gravity runtime visit established.
- OriginalGRO geometry proves Skulls WorldBase gravity-inversion sectors contain NAV294/295; arbitrary/body-frame handling is applicable, not an exclusion. Navigation agent owns cecil_frame/motion/Native bridge/test changes in its isolated worktree; main owns combat frame and Driver integration.
- Shared frame63fixturechecks passed; body-frame perception/aim plus invalid-pose neutral output implemented in8da812d. Three2000ticknormal/inverted/tilted tests each1899fireticks, existing555Human checks pass. Native integration still awaits the navigation commit/build.
- Pickup-mask evidence helper and honest offline analyzer integrated;37Python tests pass. No picked-mask or fireaction alone is treated as item acquisition or a hit.
- Deploymentmatrix now retains original inventory plus latest six-instance mapped-DLL/config observation. Development temporarily runs Skulls on25650 with006; all five production builds unchanged. Backups and map/population transaction recorded privately.
- Next: finish gravity/safe-motion bridge, native build007, verify behavior on all five maps, then final-hash1/4/8gates3600/3600/7200, recovery, fleet rollout and15min simultaneous qualification. All long gates remain open.

### Meilenstein 07.11.2026, 19:45 UTC
- Native Combat-Asymmetrie auf serverseitigen Versandrückstand bei effektivem4000-B/s-Clientbudget eingegrenzt; Original-1.07-Adressen und passive Traces belegen Pfad. Keine Aim-Codeänderung.
- Gleiche010-DLL mit explizitemLAN-Startup100000/6000 bei B:60-s-Aktionsfeedback0,05s statt2,15s;300-s-Combatkontrolle alle8 bewegt/feuernd/Scorezuwachs,41 Todesfälle/Respawns,0 Logfehler. A-Konfigurationsübernahme und beidseitige effektive Sessionwerte bestätigt;5Produktionsserver unverändert.
- Isolierte native Stopfixture besteht Wrapper/WM_DELETE sowie ausstehendes Auto-Restart ohne Game, einschließlich Cleanup/Flottenschutz. Vorherige Permission-,BadWindow- und Drain-Versuche bleiben als Fehler mit eigenem Cleanupnachweis erhalten.
- Nächste Schritte: beide Clientwerte nativ prüfen, alle5Mapfunktionen/Supply/Original-Retailgameplay, dann formale3600/3600/7200-s-Gates und Recovery. Noch kein formales Langzeitgate begonnen.


### Fortsetzung 09.11.2026 — Reviewkorrekturen und neuer Kandidat

- Flotte erneut vollständig inventarisiert: fünf Produktionsinstanzen unverändert, Entwicklung seit 07.11. auf Yodeller/Build010. Beide Clientlogs ohne erkannte Sync-/Fatal-/InvalidAction-Fehler; 55 serverseitige SYNCBAD betreffen externe/unklassifizierte Verbindungen, keine bekannte lokale BotClientadresse. Keine rückwirkende Langzeitfreigabe.
- Abgeschlossene Yodeller-600-s-Beobachtung: 129 Todesfälle, alle acht mit positivem Scorezuwachs. Neue Little-Trouble-600-s-Beobachtung: 135 Todesfälle, alle acht mit Bewegung/Feuer/Pickups und Scorezuwachs, keine neuen Monitorfehler, maximal 1,02 s unbegründeter Stillstand. Beide bleiben Build010-Kurztests.
- Unabhängiges Review reproduzierte Itemstarvation nach 128 ungeeigneten Snapshots und fortwirkende vorige Move/Fire-Aktion bei drei InvalidAction-Abbrüchen. Regressionstests jeweils RED→GREEN; geeignete Items werden vor Aufnahme gefiltert und Snapshotfenster rotiert, ungültige Aktionen werden durch endliche Ausgabe ohne Bewegung/Buttons ersetzt. Native Bridge157 mit ASan/UBSan bestanden, acht C++-Suiten sowie echte Driver-/Item-Verträge und30Waffen-/vierPreset-Exportvergleiche bestanden.
- Monitor/Auswertung schließen jetzt fehlende Anfangs-/End-/Binnenabdeckung >5s, zusätzliche Spieler, falsche Retailidentität/Port und Mapwechsel aus; CRLF-Endfelder bereinigt.107 portable Tooltests bestanden. Keine Änderung der eingefrorenen Spiel-/Stabilitätsgrenzen.
- Git-Push per lokalem HTTPS nicht authentifiziert; vorhandener GitHub-Connector veröffentlicht exakt denselben geprüften Tree737b87266daee2d79524b944b8ab916f429b0875 per Fast-Forward/Lease als2934b9e9010beda432a14e5c4acab8281a8d530b auf dem bestehenden PR99-Branch. Lokale ursprüngliche Commits bleiben erhalten. Neuer nativer Build012 aus genau diesem veröffentlichten Stand: DLL e0d70efb9a234121ffd97ea98d5a7d9956062c080a852be6cf7fd2dc31abc0d2. Vorläufiger011 wurde nie installiert; keine Übertragung von010-Abnahmen.
- Nutzer kann keinen Windows-Rechner online bringen; unveränderter Original-Retailtest wird auf Hetzner/Wine vorbereitet. Windows-spezifische Gegenprobe bleibt separat NOT_TESTED. Alle vier Originalkomponenten der eigenen isolierten Kopie SHA-geprüft; noch kein Join.
- Nächste Schritte:012 nur Entwicklung installieren, native Funktions-/Karten-/Original-Retailkontrolle, anschließend unverändert3600/3600/7200s+Recovery; Produktion erst nach erfüllten Gates.


## Earlier qualification snapshot — 9 November 2026 15:06 UTC

Build024 ten-spawn supply cohort failed8/10; no final duration or production rollout accepted. Candidate030 includes reviewed one-time relocation budget, physically measured missing-reference support, native FLOAT leveling composition correction and actual final movement ownership. Merged320 sanitized bridge checks and Driver guards pass. Diagnostic029 completed600.008s/full coverage/no errors/max unexplained stillness2.030s; it is not qualification. All final-hash supply/map/1h/1h/2h/resource/Retail/weapons/special-waypoint/recovery/fleet gates remain open. Five production baseline DLLs and development013 remain unchanged. No Windows host is required for continuing available original-Retail/Wine work; no native Windows or independent WAN result is claimed.

## Fortsetzung09.11.2026,17:45 UTC — Skulls blockiert Normal038

- Normal038 aus veröffentlichtem e2804ac2d0cabdc082a3bb881ef0557cd0f66bfc/DLL eacc13bd22221f758c151875857fab48012eb2637ffa89abb24346b2af52ec1b gebaut.518 SDK107-Bridgeprüfungen unter ASan/UBSan und aktuelle neun Original-NAV-Rundläufe mit221.682 Prüfungen bestehen.
- Neue vollständige v11-Versorgung mit zehn getrennten initialen Leben:9/10 korroborierte erste Waffenziele,Median3,625s/P9510,20s. Zu breite automatische offene-Ziel-Meldung bezieht sich ausschließlich auf Rang13; getrennte unabhängige Scope-Bewertung, automatische NONPASS-Ausgaben und frühere v10-Zensierung bleiben erhalten. Einzelgate bestanden; keine globale Freigabe.
- Hole/Trouble/Yodeller je600s mit acht Bots sowie zusätzlicher Vierbotlauf600s ohne neue Monitorfehler.118 tatsächliche gesundheitskorrelierte Respawnfolgen unabhängig und durch erneute Ausführung bestätigt.
- Skulls600s scheitert an271,19s/15,12s/12,12s unbegründetem Stillstand. Offgraph-Reacquisition bewertet freie Strahlen als Bewegung, ohne dauerhaft fehlenden tatsächlichen Positionsfortschritt zu behandeln. Ein weiterer Fall hat keinen Knoten innerhalb der ursprünglichen32m. Alle privaten Prozesse normal geschlossen. Red und formale3600/3600/7200s nicht gestartet; sechs öffentliche Instanzen unverändert.
- Eng begrenzte Original-NoPosChange-Korrektur isoliert entwickelt: bestätigter aktueller Ground-Kontext, tatsächlich angenommener Offgraph-Supply-Owner, Positionswatchdog über Ziel-/Cooldownwechsel, bestehende geprüfte begrenzte Escape-Richtungen einschließlich explizitem Backstep bei neutralem Request. Lifecycle-/Owner-/Medium-/Zeitresets,16-Raybudget,0,3-Bewegungsnorm und Pflichtbodenprüfung bleiben erhalten. Keine garantierte freie Escape-Richtung unterstellt.
- Danach unabhängiger Review, Veröffentlichung des exakten neuen Quellstands, normaler Retail-Build und frische betroffene Versorgung-/Karten-/Waffen-/Sonderaktions-/Retail-/Langzeit-/Ressourcen-/Recovery-Gates. Nur ein echter finaler Qualifikationsnachweis erlaubt den bereits autorisierten gestaffelten Rollout aller sechs Instanzen mit gemeinsamer15-Minuten-Flottenprüfung.

## Fortsetzung09.11.2026,18:29 UTC — Normal039 erneut ohne Freigabe

Normal039 aus c11bc16d6892068f65bf3946fd60b31ff9d554b5/DLL42d2a536263d599edf47c3387b4056eb5e099ee836ab2337fb7dab6f7fbc267f normal gebaut,556 zusammengeführte SDK-ASan/UBSan-Bridgeprüfungen bestanden. Der600-s-Skulls-Lauf scheitert mit maximal552,588s unbegründetem Stillstand. Zehn neue vollständige Versorgungsepochen v12 scheitern mit7/10 Erwerbsnachweisen undP9533,05s. Kein gelockerter Grenzwert, kein Stundenfenster oder Rollout. Alle normalen039-Spielprozesse geschlossen, getrennte passive039diag-Kopie normal beendet; ihre Ergebnisse qualifizieren039 nicht. Die fehlende Ground-Watchdog-Voraussetzung und physische Unterstützung werden weiter gezielt diagnostiziert. Kein externer Windows-Blocker für vorhandene originale Retail/Wine-Prüfungen. [Vollständiger aktueller Ergebnisbericht](../../reports/cecil-full-20261107/2026-11-09-candidate039-native-results.md).


## Fortsetzung09.11.2026,20:02UTC — Normal040 Supply begrenzt PASS, Skulls FAIL

Aktueller040-Stand ergänzt die historischen Statusabschnitte oben: Quelle `0c48a4f9f92d993ea1c5a5a9fed82d5acea08db1`, Tree `7cb63a29e1a072511c101f68c2362a7f92f71724`, DLL `4925d3f38c43795730d5d73d9cffd73681f92200820d51e0fe994cd6651f84c5`;15 MSVC-Einheiten+Link und633 SDK-ASan/UBSan-Bridgeprüfungen bestanden, Main-/unabhängig reviewed. Die neue vollständige v13-Versorgung besteht ihr unverändertes Teilgate:10/10 feste erste Waffenziele über alle33 erhaltenen Starts, zehn feste initiale Leben, Median9,775s/P9518,00s,592 gültige Ein-Bot-Abfragen und zwei unabhängige Reviews. Privater begrenzter Verdict-SHA256 `436442c66ca8c8ef91ad699e59b3f3ef2a6a8008453fbba797b47ad1f50ab560`; kein globales QUALIFIED. Native Itemzuordnung beruht auf Typ/Entity/passendem neuen Besitzbit/gleichem Endtick und lokalem Kontext, nicht allein auf `goal_picked`. Keine neue geometrische Erfolgstoleranz.

040-Skulls600,006024632s ist vollständig mit52 Todesfällen, Scorezuwachs aller acht und ohne neue Monitorfehler, aber wegen sechs langen Stillständen bis228,921s fehlgeschlagen. Alle drei normalen Prozesse normal geschlossen; andere040-Karten und formale3600/3600/7200s nicht gestartet. WM_CLOSE mit Bot-Exitstatus1 bleibt als solcher dokumentiert, nicht zu Exit0 oder Syncfatal umgedeutet. Fehlender persistierter Server-Kernelstarttick und fehlende Einzelantworten des erfolgreichen Population0-Drains bleiben explizite Beleggrenzen.

Die getrennte private040diag-Folgemessung ist nach600,002959462s/536 Abfragen mit normalem Cleanup abgeschlossen. Ohne zusätzliche Diagnose-Rays/Engine-/World-Abfragen belegt sie18 exakte Treffer auf das bereits native Standpolygon trotz zusätzlicher Neigungsablehnung bei einem A3-Stillstand. Keine Qualifikationszeit, keine Erklärung aller anderen Stillstände und noch kein nativer Wirknachweis einer Korrektur. Die41er-Transfermatrix bleibt ausdrücklich039-Snapshot. Frühere039-FAILs und alle Grenzwerte bleiben erhalten. Nächste Arbeit: eng begrenzte Verhaltenskorrekturen, unabhängiger Review und neue exakte Laufzeitnachweise. Finale Feature-/Karten-/Waffen-/Sonderaktions-/Retail-/Stunden-/CPU-/RSS-/Recovery-Gates sowie alle sechs Instanzen+900s bleiben offen, öffentliche Instanzen unverändert. [Vollständiger040-Bericht](../../reports/cecil-full-20261107/2026-11-09-candidate040-native-results.md).


## Fortsetzung09.11.2026,20:32UTC — Normal041 Supply PASS begrenzt, Skulls FAIL

Normal041 aus74b5e16/Tree5cfe4e0/DLL9ffb5008 ist normal gebaut und mit743 zusammengeführten SDK-ASan/UBSan-Prüfungen und zwei unabhängigen Reviews geprüft. Die enge aktuelle Standpolygon-Ausnahme, geometrisch begründete ferne Originalhinweise und zwei begrenzte NoPosChange-Diagonalen bleiben neue native Verhaltensänderungen. Supplyv14 besteht als frische vollständige Kohorte10/10, Median3,65s/P959,85s/597 Queries/26 erhaltene Starts; späterer nicht zur Kohorte gehörender offener Cannon bleibt rechtszensiert. Server-Kernelstart/elf normale Abschlüsse/zehn Population0-Antworten sind persistiert.

Skulls600,009s scheitert spät mit16,145s unbegründetem Stillstand bei einem unbekannten NULL-Support; alle acht haben Scorezuwachs,64 gesundheitskorrelierte Respawns und null neue Monitorfehler, danach normaler Cleanup. Keine Stundenfenster, weiteren041-Karten oder öffentliche Ausweitung. Eine getrennte rein passive041diag-Messung liest native Standebenen samt Abstand und vorhandene Strahlergebnisse, ohne zusätzliche Queries oder Aktionsänderung; noch keine neue Kontaktursache bewiesen. Original-Retail/Wine120,198s belegt begrenzten Join/Combat/normalen Abschluss, Bewegungseffekt wird gezielt separat überprüft. [Vollständiger041-Bericht](../../reports/cecil-full-20261107/2026-11-09-candidate041-native-results.md). Native Gesamtfreigabe, alle übrigen Gates und autorisierter All6-Rollout+900s bleiben offen; kein externer Windows-Blocker, kein gelockerter Grenzwert.

20:51UTC: 041b-Retailbewegung durch benachbarte lebende First-Person-Bilder und Rohlogs unabhängig bestätigt,120,185s/107 korrekte Queries/Originalhashes unverändert/alle4Prozesse normal geschlossen. Native NULL-Kontaktdiagnose reproduziert nun tatsächlichen Referenz-/Standpolygonwechsel und separates Erschöpfen aller5Ausweichrichtungen. Optionaler1800s-Diagnoseversuch nach546,003s administrativ normal geschlossen; unvollständig/keinZeitgate-PASS. Nächster Schritt: ausschließlich messende native StepDn-Bodenabfrage im isolierten Diagnosebuild, dann kleinste ursächlich belegte Korrektur und neue vollständige Kandidatenqualifikation. Alle sechs Liveinstanzen unverändert; kein vorzeitiger Rollout.


## Fortsetzung09.11.2026,21:43UTC — Normal042 Supply PASS begrenzt, Skulls FAIL

Normal042 ist exakt veröffentlicht und normal gebaut:7a0a5c89cf069bde47fa82dcabf0bfc5232bb874/Treeff11d698de322a56166edd6660bed98ac45862bb/DLL6eb4eb8043f45ce7b2f721886452bc6cf1f26aa6c24e3c760c6ac29ba89adf37.770 zusammengeführte SDK-ASan/UBSan-Prüfungen und unabhängige Quellreviews bestätigen den achtteiligen, bei weiter fehlendem Positionsfortschritt wiederholbaren Weltrichtungs-Sweep. Probegeometrie,16-Raybudget,0,3-Bewegungsbetrag, Holds/Cooldowns und Gatekriterien unverändert. Neue Versorgungv15 nach vollständigem Main-/unabhängigem Rohreview10/10 feste erste Ziele, Median3,95s/P9510,15s/589 Queries/zehn feste Initialleben; späterer Grenade-Timeout auf Rang12 zählt als solcher, alle26 Starts erhalten. Elf normale Abschlüsse und zehn tatsächliche Leerslotantworten nachgewiesen.

Skulls600,005982s scheitert an36,321s und10,083s unbegründetem Stillstand trotz Scorezuwachs aller acht/keiner neuen Monitorfehler/voller Abdeckung. Neuer längster Kontext ist ein akzeptierter originaler UNREACHABLE-Anchor ohne Ausgangskanten, ohne Ziel und ohne Anchor<0-gebundenen Watchdog; getrennte NULL-Seitenwandlage weiterhin offen. Alle drei Prozesse normal geschlossen. Keine weiteren042-Karten, Stundenfenster oder öffentliche Ausweitung. Die separate zusätzliche StepDn1,5m-Diagnose liefert23 gepaarte Nichttreffer und endet nach705,390s administrativ/unvollständig mit normalem Cleanup; keine Qualifikationszeit oder neue Bodenautorisierung. Nächster Schritt ist eine gezielt belegte Navigations-/NoPosChange-Korrektur mit Originalvergleich, RED-Test und unabhängiger Prüfung, danach vollständige neue Kandidatenqualifikation. [Vollständiger042-Bericht](../../reports/cecil-full-20261107/2026-11-09-candidate042-native-results.md). Alle sechs öffentlichen Instanzen und alle eingefrorenen Grenzwerte bleiben unverändert; vollständiger All6-Rollout+900s bleibt autorisiert und offen.


## Fortsetzung 09.11.2026, 22:14 UTC — Normal043 besteht Messgrenzen, gezielte Luftsteuerung folgt

Normal043 aus `4fd46626` ist mit der vollständig im [043-Bericht](../../reports/cecil-full-20261107/2026-11-09-candidate043-native-results.md) gebundenen DLL normal gebaut. 802 finale SDK-ASan/UBSan-Prüfungen, neun C++-Suiten, Driver-/Item-/Originaltabellenprüfungen und unabhängige vollständige Quellreviews bestehen. Echte Positionsbeobachtung umfasst nun angenommene Anker ohne gültiges Ziel; Standardpolicy0-Wandbewegung und wirklicher Supportnachweis bleiben strikt getrennt. Keine NAV-Änderung, Bodenfiktion, neue API oder Fristerneuerung.

Skulls600,006398s/596 Abfragen erfüllt die quantitativen Grenzen mit voller Abdeckung, Scorezuwachs aller acht,70 gesundheitskorrelierten Respawns, keinen neuen erkannten Monitorfehlern und maximal6,055s unbegründetem Stillstand. Supplyv16 ist nach vollständigem Main-/unabhängigem Rohreview begrenzt bestanden:10/10 feste Ziele, Median7,20s/P9520,50s, zehn feste Initialleben und589 Abfragen. Alle25 Starts bleiben sichtbar; späterer Rang25 Flamer bleibt rechtszensiert. Alle eigenen Testprozesse schließen normal.

Die getrennte20s-Flugphase mit neutraler Supply-Aktion und später durch Combat mitbestimmter NAV-Rückkehr bleibt funktional offen. Reale Höhenbewegung wird nicht zum Stillstands-FAIL umgedeutet. Nächste enge Korrektur: aktueller unanchored FALL-Kontext mit wirklichem Originalhint, LOS und begrenzter physischer Wandsteuerung. Proposal- und Action-Regressionstests müssen vor der Implementierung tatsächlich fehlschlagen; native Befreiung braucht einen eigenen Nachweis.

Der zusätzliche Main-Prüffehler und die ausdrücklich erst nach Start erfolgte vollständige Dateibindungsprüfung bleiben erhalten. Ein neuer289-Pin-POST_RUN-Snapshot entsteht nach normalem Testende ausschließlich für künftiges Staging. Weitere043-Karten,3600/3600/7200s, Retail43, Ressourcen, Rotation, Recovery und öffentlicher Rollout wurden nicht gestartet. Der All6-Auftrag samt900s bleibt aktiv, ohne Gesamtfreigabe oder übertragene Zeit einer früheren DLL.


## Fortsetzung09.11.2026,22:55UTC — Normal044 funktionale Routenschleife offen

Normal044 Quelle3c09c21c56c18a846873bcb4c5766d9399ba8b87/Tree9734ea4e089b5460ddfb0ebd64c366292185b083/DLLeb9201ebf36c8ae3374c9d095aaaf135801cebce0584b7d73ac68ad20f161509:15 MSVC-Einheiten/Link,855 SDK-ASan/UBSan und frische221682 Neun-NAV-Prüfungen bestehen. Neue native Skulls600,008936s/595 und Hole600,009415s/595 halten numerische Grenzen ein, maxquiet4,040818/3,016412s, keine erkannten neuen Monitorfehler, alle acht mit positiven Scoreänderungen. HoleDev7netto−1 bleibt explizit.133 unterschiedliche gesundheitskorrelierte Respawnpaare innerhalb der beiden tatsächlichen Monitorfenster; ein weiterer Hole-Spawn nur Nachlauf, kein zusätzlicher Fensterkredit.

Skulls zeigt mehrere beobachtete autonome Luft→NAV-Ketten desselben Lebens, aber einen separaten tatsächlichen Boden-Wegpunktzyklus ohne Hopannäherung über203s im Monitorfenster(207s einschließlich4snormalemNachlauf). Weltpositionsänderungen setzen den bisherigen Watchdog zurück, die gebundene Kante wird dauerhaft behalten; Original-Cecil prüft alle5s den nächsten Anker. Kein umetikettierter numerischer StillstandsFAIL und keine Gesamtfreigabe. Neuer eng begrenzter Besthop-Checkpoint auf tatsächlich akzeptiertem statischem Boden wird mit echten RED-Fällen entwickelt; Flug/Lift/Locks/Originalradien/feste Ziele bleiben geschützt. Keine formalen Stunden oder öffentlichen Installationen für044.

Prospektive Supplyv17 bestätigt9/10 feste erste Ziele, zehn feste Initialleben, Median6,725/P9512,9s/605 korrekte Ein-Bot-Abfragen. Echter Rang3-Cannon-Timeout bleibt Fehler; alle30Starts28korroboriert+1Timeout+1rechtszensierter Nichtkohortenfall erhalten, elf normale Abschlüsse/zehn echte Leerslots/17Pins. Original-Retail/Wine120,184946s/107Abfragen/fünf reguläre Eingaben und direkt betrachtete benachbarte Bewegungsscreenshots begrenzt bestanden, vier Originalhashes/alle vier normalen Abschlüsse. Spätere Cannon-Tode getrennt; kein Windows-/GPU-/WAN-PASS.

[044-Ergebnisse](../../reports/cecil-full-20261107/2026-11-09-candidate044-native-results.md) und [Build044](../../reports/cecil-full-20261107/build044.json) halten die Grenzen fest. Alle künftigen geänderten DLLs benötigen neue Gates; keine044Zeit/Respawn-/Retailgutschrift wird übertragen. All6-Auftrag mit vollständiger fünf-Karten-/Waffen-/Sonderaktions-/3600/3600/7200s-/Ressourcen-/Rotations-/Recovery-/900s-Flottenprüfung und regulärer Integration bleibt aktiv. Alle sechs bisherigen öffentlichen DLLs unverändert, Transfermatrix039-Snapshot bis tatsächlicher Neubindung.
