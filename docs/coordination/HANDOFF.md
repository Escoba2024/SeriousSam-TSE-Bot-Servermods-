# TSE-Agenten: Start und Handoff ohne manuelle A00-Freigabe

**Stand: 19.10.2026.** Die alten `CLAIM_REQUESTED → A00-GRANTED`-Freigabestufen und vierstündigen Code-Leases sind aufgehoben. `STARTED` und `HANDOFF` sind Informationsnachweise, **keine Erlaubnisanfragen**. Kein Agent wartet für konfliktfreie Code-, Offline-Test-, Analyse- oder Dokumentationsarbeit auf A00.

## Optionaler Startstatus (ins Issue #18)

```text
STARTED
slot: Axx (nur falls sinnvoll)
ticket_or_pr: #...
goal: ...
branch: ...
worktree: ...
write_scope: ...
runtime_scope: NONE | ISOLATED_COPY | SHARED_RESOURCE (nur mit technischem exklusivem Nachweis)
check: existing_worktrees_and_writers_checked
```

Eine Nachricht ist optional; sichere Arbeit kann sofort beginnen. GitHub-Kommentare oder Slot-Labels bilden **keinen** technischen Lock.

## Nur bei echtem Konflikt

```text
CONFLICT
scope: <Datei / Worktree / PID / Installation / Port>
observed_owner_or_state: ...
safe_alternative: <eigener Worktree / separater Port / Offline-Fixture>
needs_decision: <nur falls sich Konflikt nicht sicher auflösen lässt>
```

Gemeinsame Runtime mit unbekanntem Eigentümer bleibt unangetastet; **die restliche Arbeit wird fortgesetzt**. Ein manueller A00-`GRANTED`-Kommentar löst einen fehlenden technischen Runtime-Lock ohnehin nicht.

## Handoff nach der Arbeit

```text
HANDOFF
slot: Axx
ticket_or_pr: #...
branch: ...
head_sha: ...
paths_changed: ...
tests: <Befehle/Umgebung/PASS/FAIL/SKIP>
retail_runtime: NOT_TESTED | PASS_LIMITED | FAIL | PASS_SCOPED
resource_cleanup: <nur eigene Prozesse, eigene Kopien, Ports>
known_issues: ...
pr_url: ...
status: COMPLETE | REVIEW | BLOCKED_SPECIFIC_RESOURCE
```

Keine gesonderte `RELEASE`-Genehmigung für reine Codearbeiten. Bei gemeinsam genutzten Runtime-Ressourcen nach eigenen Tests Prozessende, Portbelegung, Restore und ggf. Freigabe des **technischen** Locks prüfen. Keine fremden laufenden Sessions stoppen, keine historischen Testgates als bestanden umdeuten. Die Projektregel ersetzt weder technische Sperren noch plattformseitige Zugriffs-/MCP-Freigaben.

## 2026-11-11 — Milestone A execution, B gated

- Branch `codex/20261111-milestone-a`, worktree `/srv/tse-milestone-a-20261111`; baseline 4d04ab4. Main alone changed runtime; two independent worktrees implemented/reviewed combat and names.
- [Full eight-part progress report](../reports/2026-11-11-milestone-a-progress.md), [persistent plan](../superpowers/plans/2026-11-11-milestones-a-b.md), [manifests](../reports/milestone-a-20261111/).
- New unqualified build001 DLL `def7c044ba64a65b742c63d76c775c955b892655e626bf96a1380d778d35719a` built, NOT deployed. 183 portable Python tests passed; C++ sanitizer checks passed. 250 new names validated, NOT deployed.
- Five public servers now load typed Spawn=0 mapstart configs; all original DLLs/maps preserved. Dev A1 rolled back at **19:11:37 UTC**, exact original config pins and eight owned bots verified, following 36 SYNCBAD/3 external sync disconnects. Root cause OPEN. Dev original server powerup filter and Cecil048 clients preserved.
- Rollback stop helper first rejected an evidence directory outside its hardcoded parent. No force kill; the still-owned botB was closed with checked PID/start identity and WM_DELETE_WINDOW, then normal harness resumed under correct parent. All transient stop overrides restored. Isolated probe port25880/unit inactive; deployment locks released.
- Fresh final snapshot includes 18 native processes, eight owned bots per server; Hole now has one additional UNKNOWN, Dev zero additional. Runtime identity records refreshed after rollback. Post-rollback Dev log at 19:15 had zero SYNCBAD/disconnects; short observation only, no causal proof.
- Private receipts `/srv/tse-milestone-a-evidence-20261111/`; verified rollback `/srv/tse-cecil-full-20261107/.codex/evidence/restart-fleet-20261111-a1-sync-rollback/development/rollback.json`. Initial all-six A1 result is **superseded for Dev** by `dev-sync-rollback-result.json`.
- Backup: original source bundle and eight runtime chunks roundtrip verified on private Drive; companion carries restore index/checksums/dirty work/SDK bundles. 36,009 files restored/hashchecked separately; symlinks indexed, not materialized. No full native restore claim.
- A=INCOMPLETE; B=NOT_STARTED. Native Windows/Shadow clients offline. First next test: isolated server/client actual session-field equality for Spawn3/0, then controlled respawn damage; source session copy exists, client-local gam_ settings are not a demonstrated fix. Further A3/native map gates remain open. No new rollout until failures resolved and required evidence exists.

- Abschluss: Remote-Code `b6ae14e5497f6013bf198fad5cd105bfe658f05c`, treeidentisch zu lokal64aa881; After-Drive-Archiv und Companion zurückgeladen/SHA-geprüft. Backupindex enthält Links/Hashes. Abschließende Dev-Shellmessung3,0, 18 aktuelle Logs ohne Syncmeldungen, Locks frei. Fehlgeschlagener Test bleibt FAIL; A weiterhin offen.

### Autonomous continuation, 19:36 UTC (supersedes stopped-work wording above)

User explicitly requested autonomous completion of full A then B. Goal ACTIVE. Root continued in same main worktree; both isolated agents resumed and committed actual regressions/fixes, then independently reviewed each other's changes. Local commits84b9216 (final-residual trigger, gain10/14/20, combat vs ordinary pickup) and3dc99dc (bounded extended-item transit failure) integrated. Native build002 at `/srv/tse-milestone-a-build-002-20261111/manifest.json`: DLL `50b132c0d83d209b399c7178bcb41dc16c0ee1ffe7c28652cecbd69a07baafd5`, source3dc99dc75d3dcae22f9af18537d5df282c27f0e5, build_ok=true, qualified=false. No live DLL changes.

New original-Engine executable validates all250 added names, including actual Undecorated and LengthNaked; native GUI/query checks still pending. New own routes-free private namespace `/srv/tse-a1-isolated-20261111`, display153, port27750; unchanged Vanilla client + old048 bot + existing Dev servermod. Spawn3 control320.08s completed, no BAD/disconnect, all session156 bytes equal across three processes; normal cleanup confirmed. Spawn0 control is active under private script `/srv/tse-milestone-a-evidence-20261111/run-isolated-a1.py`, exec session75658, log `isolated-spawn0-run.log`; poll same handle or authoritative PID/result, never infer stopped from timeout.

Additional own arena runtime `/srv/tse-arena-isolated-20261111` prepared (display154, port27850), currently no processes; comparator script `run-arena-comparison.py` stages original server, four old048 bots and four build002 bots plus original Vanilla observer AFTER fresh one-bot preflight. Intended trial1/2/3=MITTEL/STARK/DEMON, launch order alternated; population9, same fixed configs/map, native score/health/respawn/telemetry measured. Start only after Spawn0 cleanup and RAM preflight. This is A3 evidence collection, no B work. Scripts intentionally remain private with licensed runtimes; sanitized results belong in reports. Original receive-damage gate at Entities RVAed380 and actual session field/health/placement/game-tick export paths independently disassembled; decision file documents limited scope and no Frida/Ghidra availability.

Remaining: normal post-respawn hits at first state; render/query new formats; native paired arena results; Hole/Skulls cycle-fix function gates, other three public map checks and required duration gates, controlled actual Dev acceptance, full staged rollout/backup. B hard-gated until A fully accepted.

### 19:45 UTC current live test handle

Spawn0 session75658 completed320.009s, no errors, all roles gracefully closed. Trial1 session53501 completed240.086s with9own slots,0BAD/0disconnect, exact originalserver and mixed old/new DLL pins, normal cleanup. Score old+7/newMITTEL+25; no human inference and no independent hit attribution. Trial2=STARK with reversed client launch order is now live: exec session64566, own `ssam-arena-isolated-20261111-*` units, log `/srv/tse-milestone-a-evidence-20261111/arena-trial2-run.log`, result under newest `arena-trial-2-*`. Poll same handle/PID. After clean result, trial3 command `python3 /srv/tse-milestone-a-evidence-20261111/run-arena-comparison.py 3 240`; no retries over existing evidence. Testpopulation and resource bounds are isolated from production; copies under `/srv/tse-arena-isolated-20261111` are exclusively owned test resources. Native logs remain private. Build002/source backed up separately next; GitHub code throughc85927d published asf5d8cf030adb6034b388d0240fc773d290ca62ba (same tree).


### 19:59 UTC — A2 native evidence and Build003 continuation

- Two Build002 windows completed240s each,9own slots,0SYNCBAD/Disconnect. Trial1MITTEL+25 vsold+7; weapon acquisition regressed in some lives. **Build002 NOT accepted**. Build002trial3 intentionally not run once concrete shared regression known; fresh finalcandidate still requires>=3native comparisons.
- Actual rootcause found/tested: existing mapped weapon route was incorrectly invalidated by `enemy_distance<8`, resetting a route during temporary closecombat. Local77d8339 integrates retention-only fix40491d3; admission>=8, combatownership, typedneed/deadlines remain. Independent review found no material issue. New sanitized trial1 full-life report630f815 preserves failures/censored lives and distinguishes real weaponanimation/state from fireintent/hits.
- Build003 manifest at `/srv/tse-milestone-a-build-003-20261111/manifest.json`: source77d8339, DLL `0ae31bb552ea4d97bd6c6f9d74ea90c84dd4b80b06f84e2c965d24936e5ee9c4`, unqualified. Main ran1378SDK107bridgechecks ASan/UBSan and183tools tests successfully. No live DLL promotion.
- New current native handle **33276**, root script `run-arena003-comparison.py 1 240`, log `arena003-trial1-run.log`, units `ssam-arena003-isolated-20261111-*`, root `/srv/tse-arena-isolated-20261111`, display154/port27850 in private namespace. Latest window under `arena003-trial-1-*`. Poll actual handle/PID/result. Only after clean result decide whether native acquisition improved; do not substitute higher score for Supply gate. If valid, run tier2/3 with the same003 script, altered joinorder remains built in.
- A2: `names-render-195207` completed180.108s,85/85queries validate exactlyfive representative own aliases (plain,color,bold,italic,combined), original unchanged Retailclient screenshot visually inspected and formats correct. GUIDs preserved. All250 additionally passed originalnative decoder. NoSYNCBAD/disconnect. Tool session returned143 after finishedreceipt; four own units independently confirmedinactive/MainPID0/Resultsuccess, all recordedgame roles normallyclosed. Scope is Wine/localindependentGameSpy, not physicalWindowsGPU/WANbrowser/all250GUI cases. Image/rawprofiles stay private; sanitized `names-native-render-query.json` records limitations.
- Early actual originalserverSpawn0 hit: unique matching server cannonkill confirms oldbotDev3 killed bynewDev7 within0.20–0.30s afterspawn. This proves belowold3s protection but not exactfirsttick or repeatednewbot/Vanilla gate.
- Build002/source/closedcontrols/trial1 backup: privateDrivefile1GoR32sMm91ryFm718RT7PDK8MUElLLST,6,852,961bytes,SHA256d7c8ad227798ad44cb48ba1c87693dae8a81ade30610c2bad91e55bbedf9fbe8; roundtripverified,242regularfilesisolatedrestored,2SDKsymlinksindexednotmaterialized. Build003/nativeprogress backup follows.
- Goal remains fullA thenB, ACTIVE. Public5oldDLL+Spawn0, DevoldDLL+Spawn3 unchanged. No B implementation. Remaining exactdamage/restart/mapchange, final3comparisons+acquisition, five-mapfunctional/hourgates, Devcontrolledgateandstagedfleetrollout/backups all remain required.

### 20:13 UTC — actual next step (supersedes previous live handles)

Both11280and33276areTERMINAL. Names rendered180s andBuild003trial1completed240.021s, allnormalgameprocessclosuresindependentlyverified. No own labserver/display remains running. Latestpublicinventory18nativeprocesses, all6ports8ownbots,noadditionalplayersatchecktime. Currentfleetlogsresampledseparately; historicalDevFAILremainsprivatepreserved. Build003trial1scoreold+7/newMITTEL+30,0BAD0disconnect; **notaccepted** because some first useful ranged acquisitions remain slow. ExcludeDoubleColts/chainsaw: usefulmask0x3df8. Retainedloss/failedlivesmustremaininanalysis.

Nav agent now implements bounded default-off read-only diagnostics (usingbot_bDiagnostics) in own namesworktree: actualBotCecilReadItem rejectionreason/per-playerindex/pickedmask/flags/render/pickuponce/sessionweaponsstay; candidatepath/score/firstspecialedge and groundedterminalcontext. Smallconst Parent(slot) accessor approved; no routecost/search/RNG/ray/state changes permitted. Mainawaitscommit then independentreview/build004. Code003unchangedinlivefleet. Hypothesesnotfixes: split-client visualhide vs per-playerpickedmask; nativeLasergoalscancelledsimultaneouslyafterteammatepickupunderweaponsstay=1. No savedalternativeselectiontelemetryexists, therefore no guessedfirstweaponroutepatch yet. Minigunspecialroute42flags movedairborneacross169m; noteligibleforgroundwatchdogandnotprovedstationaryloop.

Next safe action: inspect collaborationnav_audit status/workingdiff, takecommitteddiagnosticfeature, reviewandrunexistingSDK/sanitizerparitychecks, buildnewunqualifiedcandidate, runownprivateon/offcomparisoncapturing actualdecisionsanditemreadreasons, then implementonlyprovenrootcause. Finalcandidateneedsfresh3matchedtests, exactstartcondition/swapverification (joinorderaloneisnotfixed-positionproof), firstweapon/respawngates,5mapsfunctional/formalstability,thenDev/stagedfleetbackups. FullBstillhardgated.

Latestpublishedsource5eaef8df42d7504a7fc01657bdf457678d18d406,treeidenticaltoc64c288; localafter-native-reportcommitwillbenewer. Build003privateDrive1wgbVRXSqDe9dVlzLf3Kgn57iTq47Y_1L,9,131,523bytes,SHA2561990e2400ff14e6421d36ae25b928af40eb5aa1bbdfa2a7930f5beb4a035aadb,roundtripverified,362regulararchivemembersfullyread (new003archivefile-restorewritegatepending; beforebundle36,009filesand002delta242filesalreadyseparatelyrestored). GoalACTIVE; significantcode/runtime/evidenceprogress,notblockedandnotcomplete.


### Milestone-A continuation 2026-11-11 20:22 UTC

Current branch `codex/20261111-milestone-a`, implementation7e96f03; diagnostic-only Build004 DLL43908fa08d7cb40c058fd03d455797feae8b40c9be4cf94667aa9ee179b14310, not qualified. Private owncopy harness `run-arena004-diagnostics.py` runs120s off then120s on in isolated27850 namespace; no production candidate deployment. Root owns all runtime actions.

Hole precautionary config rollback completed after9BAD/max8/noDisconnect in external peer; exact original script and eight ownbots restored; live session3.0. Dev remains3.0 after previous rollback; publicotherfour config0. All originalDLLs preserved, identity manifests freshly updated. Evidence sanitized `docs/reports/milestone-a-20261111/hole-precautionary-rollback.json`; private `/srv/tse-milestone-a-evidence-20261111/hole-sync-rollback-result.json`. No causal attribution; A/B remain unaccepted/unbegun.


### Milestone-A continuation 21:09 UTC

Source fix3fec334 integratesd1fb865 (bounded committed-flight finish after item loss). Main replay1513SDK107ASan/UBSanbridgechecks, independentreviewincludingactualSafeMotionreturn2. Build005 succeeded, qualifiedfalse, DLL35c950832d8ce4c48e0363ab33ba1a517d4a87e95bb320ca5aa686c59f2bfc35. No productiondeployment.

Active ownnative test: `/srv/tse-milestone-a-evidence-20261111/run-arena005-checked-barrier.py 1 240 1 0`, exec41963; privateconsole `arena005-tier1-swap0-controller.log`, namespacegame27850/display154. Uses early normal Pause, originalserver/Vanilla, old048vsnew005, waits9unspawnedentities/all156SPbytes, captures controller source, then240s. Finalstatusonlyafterpurecleanupgate. Next: inspect actualCecilFlightFinish lifecycle + ALLspawnlifeinventory denominators/censoredfailure; exchangedphysicalDLLleg withsameTier beforeother2tiers. NoPASSuntilactualmatchedstarts/fullwindow/normalclose. Threecomparisons, A1exactfirststate/human/restart/mapchange, mapfunctional/hourgates, Devandfleetstagedrolloutremainopen. Bnotbegun.

Remote7842506df859b370bcbcb98e11d7938b069b6d81 hasexacttreeaf5a46c581e65d5c422a96ed5556b26278df4da8 oflocal2d388d1, verifiedfetch/tree. New3fecfix+currentreportsneednextpublication. Fullprivatearena fixturebackedup3parts(total276969100bytes),SHA3e39ff6c4aa8b185a093c910c0b2b9ecff54735e61fa94d41e77141270027c50. All3roundtripverifiedandcombinedhash;6542regularfiles(2.888GB)separatelyrestored,1680uniqueobjects;symlinksindexed/notmaterialized,noNativeLaunch. GROdependenciesall8hash-matchseparatelyverifiedbaselineRestore. Companionandpartlinks inbackup-index. OriginalproductionDLLsunchanged; Hole/DevSpawn3, other4publicSpawn0, last20:39fleetall6×8ownbots/currentlogs0BAD/noDisconnect. ShadowRDCstilloffline69h, otherWindows40h; localWineworkcontinues.


### 21:27 UTC — maßgeblicher aktueller Stand

Beide005-Gegenproben sind beendet:240s, alle vier Rollen normal geschlossen,0BAD/0Disconnect. Tatsächliche Erststarts8/8 identisch in Position und Inventar, PRNG2306364401; absolute Spawnuhren0.95/0.90, je Fenster Spread0. Score neuerMITTEL32:9 und22:6. Allgemeine Waffenbeschaffung weiterhin FAIL(max63/50.6s, volle Nenner einschließlich Tod/zensierter Fälle). Zweites Fenster zeigt nach FlightFinish3772→3774(context84→86) erneuten Sprungpad-Anflug; Contextgrund nur nach genauer Prüfung eingrenzen. Keine A-Freigabe.

Neue Quelle ece185a erhält exakt die drei Änderungen der fremden Notice-Game.cpp; d0b2f05 ergänzt passive Auswertung desselben bestehenden Connector-Casts, keine neuen Rays/Lookups/Entscheidungen.1520SDK107Sanitizer-Bridgechecks und192Tools bestanden. Build006 DLL9690b088719ccd21e7a54e06063331a1391d4bfc904dc93fb20fadfe7dfeec7d, unqualified. 006 diagnostics0 ist nach60.0076s vollständig beendet,0BAD/0Disconnect, alle Rollen normal geschlossen. Aktueller privater Controller `run-arena006-checked-barrier.py 1 240 1 0`, Session45653, `arena006-diag1-controller.log`. Prüfen, bevor weitere Runtime starten. Root allein Runtime-Writer.

Die alte Aussage „Produktions-DLLs unverändert, Hole/Dev3“ ist überholt: separate Notice-Aufgabe rollte21:02–21:12 neue BotA-DLLs aus. Aktuelle21:24-Flotte6×8eigeneBots, UNKNOWN0,18Logs0BAD0Disconnect, überall tatsächlicher Sessionwert0.0. PublicBotA407fc5d6, PublicBotB7fc94a39, DevBotA58017fbe, DevBotBec820d04; Dedicated unverändert1c/fe. Herkunft der erneuten Spawn0-Setzung nach eigenen Rücksetzungen unbekannt; Notice-Vorherbackups hatten schon0. Fremde Notice-Quelle und Konfigurationsschalter erhalten, bestehende Transaktion nicht überschreiben. A-Kandidat noch nirgends produktiv.

Mainagent fortsetzt volleA→B. Navagent prüft beide005Fenster und konkrete zweite Contextbedingung in eigenem Worktree; Combatagent entwickelt hash-/identitätsgebundene passive Allspieler-Waffenbeobachtung für tatsächlichen Legacy7fc-Vergleich. Keine Vermutung aus1.10-Offsets. Neue Fortschrittsveröffentlichung/Drive-Delta mit beiden005Fenstern, normalem Start-Harness, Build005/006 und fremder Notice-Quellensicherung folgt.
