# Aktueller Handoff – 15.11.2026, 04:01 UTC

Gesamtstatus **A offen, B nicht begonnen**. Kein externer Zugriffsblocker:
reguläres lokales Terminal auf dem Host funktioniert. RDC bleibt gesperrt und
wurde nicht erneut benutzt. Aktuell kein Nativeversuch und kein Build aktiv.
Der Nutzer hat den Mischstand ausdrücklich bestätigt: **live behalten, isoliert
entwickeln, erst belegte Verbesserungen wieder ausrollen**. Seine spätere
Rückmeldung: Originalclient nicht mehr verbunden. Unbekannte Peers nicht ihm
zuordnen oder instrumentieren.

Dieses Dokument ersetzt die angewachsene Zwischenstandschronologie. Deren
vollständiger Inhalt bleibt in Git, zuletzt `d7bf1ae:docs/coordination/HANDOFF.md`,
und den verifizierten Sourcebundles erhalten. Keine alten FAILs werden umgewertet.

## Geschlossener026-Fall und nächste A1-Prüfung

026-Skulls600diag1 ist geschlossen: `nav20-026-skulls-root-skulls-20261115-030720`,
Resultat8bf66066a6736c6505d707644e0924a14562a8b0961f4f1d7723d54754b04100,
600,098758s, vier normaleCloses, keine neuen sechsFehlerklassen. Rootrestore
03:19:19:640Dateien/vierClosedlogs/PIDs/Units/Displays154155/vierLocks PASS.
Outer688Samples/CPUmax63,2653%/RAMmin2470592512B/Diskmin8774942720B,
max1,002606sLücke/keineVerletzung: nurHostbeobachtung, keineformalenGates.

Vollständiger [Funktionsaudit](../reports/2026-11-15-build026-skulls-closed-functional-audit.md)
integriert c176132 (Autorb6e50c6). Root hat alle vier Readerstufen selbst erneut
auf den geschlossenen Rohdaten ausgeführt: vier Outputs bytegleich einschließlich
Finalquittung298253fda7c3b4f29cde23b8c3840a7b8a30d5ddb046b47c3f847cc080acb9cf.
188Leben/180Tode/90Usefulleben/111Gewinne/515ReadFAIL bleiben vollständig;
871Decisions,852innenliegendeNative-Lebensbindungen/19UNKNOWN.
LängstesNoUseful52,303s; bewaffnet24,494s in1m und16,546s exaktstill.
AkzeptierterReacquirevorschlag ist kein Bewegungserfolg. Call-ID/Arbitration/
finalerSafetyguard fehlen als Kausalbindung; keineGuardaufweitung/Skullsfreigabe.

A1Feedbackcode integriert bis01ce526, Root vollständigerCode-/Testreview und
24portableTests PASS. Separates Rootfreeze a2fa65092236f1b16a8fe3f2a93199e22a530ee7c61da82cfa9599e8e7d66aa7,
Controller5b348963edd8333aa500bde864675fc167cc0d4fdae07445dae3de5c2fc0051a.
Peer f8c9b36667df6e0ffd77ff05b4ad5134418c85499051d3d9e950f5a50c8811e4
PASS_SCOPE für Rootdelta/Pins, ausdrücklich keine unabhängige eigenePolicyprüfung.
106/88/14Pins,125weitereDateienbytegleich, vierCorebytegleich,
sechsInstrumentgates+CollectorManifestFalse. EineMainfreigabe, keinFire.
Rootwrapper run-a1-pitch-feedback-original.py adc98dfe85435fd763527580ec67136ad2ecd75df44afe218b114ae777282ac9,
Outer c7d7b0bb89318dff86597f6a680bbca157ef4a7e1084461855d13a2148158791.
Einmal90s geplant, nach064vollDrive tatsächlich034224 ausgeführt: FAIL vorerster
Emission, Guard clienttargetEyesdelta0,00102027267>EPS0,001, Serverdelta
0,00095873693 darunter. Rootguardreplay6Frames;0Attempts/Emissionen/ACKs.
Result5f76c6f4; Rootrestore034328 PASS664Dateien9Abwesenheiten3Logs, Units/
PIDs/Displays/vierLocksfrei. Outer42SamplesCPU58,8689%/RAM2893430784B/
Disk8882692096B, keineBudgetverletzung, Child1→FAIL_HOST_OBSERVATION. KeinRetry.
[Bericht](../reports/2026-11-15-original-pitch-feedback-closed.md).

## Zugriff, Arbeitsbereiche und Sperren

Root allein integriert und verändert Runtime. Zwei bestehende Worker:
`a4_diagnosis` implementiert deaktivierten FirstStateV2-Methodenadapter
(Getterfunction/admission-idle-stop/FreshExec-Transport, Registryweitergenau2);
`candidate_audit` implementiert ausschließlich eigenenCombat-Recovery-Optin
(Header/Driver/zweiTests+Docs). Beide vorhandene getrennteWorktrees, keinNative.
Getrennte Worktrees/Claims, keine Writer im Rootworktree. Vor Native alle
Workerjobs beenden und STATICONLY ausdrücklich bestätigen lassen.

- Root: `/srv/tse-cecil-rollout-a-b-20261114`, Branch
  `codex/20261114-cecil-rollout-a-b`; aktuelle HEAD jeweils frisch prüfen.
- Private Belege: `/srv/tse-cecil-rollout-evidence-20261114` (RootEV).
- Backups: `/srv/tse-cecil-rollout-backup-20261114`.
- Native Fälle: `/srv/tse-milestone-a-evidence-20261111`.
- Isolierte Fixture: `/srv/tse-arena-isolated-20261111`, vier Rollen,
  OwnNS27850/Displays154,155; fremde Public102/151 unangetastet lassen.
- Vier gemeinsame technische Sperren: Fixture`/runtime.lock`,
  `/srv/tse-msvc-wine-20261021/tse-milestone-build.lock`,
  `/srv/tse-cecil-rules-20261107/.codex/evidence/fleet-install.lock`,
  `/srv/tse-milestone-a-evidence-20261111/deployment.lock`.

Keine Compiler, Tests, Archive, Git-/Downloadjobs parallel zu Nativefenstern.
Kein Lockstehlen, keine fremden Sessions schließen, kein ungeprüftes Deploy.
Rootwrapper verwenden feste Quellen/Pins, echte Prozessgenerationen und
exklusive Ownerquittungen; neue Fälle brauchen neue Namen, keine Retrieschleife.

## Tatsächlich live

Frisch03:56:11UTC: alle18 geladenen Rollen/Datei-/Configtargets gleich dem
Mischrollback051. Jede Instanz acht eigene Bots. Zusätzlich LittleTrouble eine
ungeklärte Verbindung, andere keine. Das ist eine aktuelle Modul-/Queryprüfung,
kein neues Kampf- oder Syncqualifikationsfenster.

| Instanz | Port | Map | Bot-DLL | Sessions/Chat |
|---|---:|---|---|---|
|Dev|25650|Red Station|Cecil048 `ec820d04`|nicht implementiert|
|Red Station|25600|Red Station|Gen2 `7fc94a39`|nicht implementiert|
|Yodeller|25610|Yodeller|Build018 `6db89204`|nicht implementiert|
|Skulls|25620|We Got Skulls'n'Bones Too|Build018 `6db89204`|nicht implementiert|
|Little Trouble|25630|Little Trouble|Build018 `6db89204`|nicht implementiert|
|Hole|25640|Hole|Build018 `6db89204`|nicht implementiert|

Vollhashes in RootEV/fleet-current-after-feedback-private.json; tatsächliche
Dedicatedrollen separat: Public Original`1c41da35…`, Dev Powerupmod`fe4a77bd…`.
Keine pauschale Bot-DLL-Ersetzung der Dedicatedrolle. Vier Publics haben
historisch Serious3 statt gewünschtem Hard2; erhalten, bis ein geprüfter
Verbesserungsrollout dies kontrolliert korrigiert. Namen458=208+250 erhalten,
458normalisiert einzigartig/keinFlash;48eigeneAnzeigenamen/48Instanz-IDs,
Profilebytegleich051, achtGUIDs/Instanz. Nur40bareGUIDs über48Slots;
Instanz+ID gemeinsam verwenden, keine Identitäten ändern. Belege
fixed-458-name-pool-rechecked.json und fleet-current-post024-name-identity-audit-private.json.

## Kritische Syncgegenbefunde

Dev048 ist keine bewiesene Syncbehebung. Am14.11.23:27–23:47 zwölf neueBAD und
ein Kick für einen externen Peer; Nutzerzuordnung unbekannt. Neue reine
Prefixprüfung15.11.02:49:28 seit23:54:70BAD/3SyncDisconnects/29055OK,
eine externe Logverbindung; beide eigenen Botclients0BAD/Disconnect.
Gleiche Prozessgenerationen und vollständige ältere Prefixhashes geprüft,
neue feste Abschnitte privat gzip-gesichert/zurückdekomprimiert/hashgeprüft.
RootEV/dev-sync-after-025-private.json plus drei komprimierte Deltas;
[bereinigter Bericht](../reports/2026-11-15-development-sync-additional-log-evidence.md).
Ursache UNKNOWN; Kickschwelle10 unverändert, keine CRCunterdrückung.

Die bereits geschlossenen048/018/020-Redfenster mit OriginalDedicated,
Originalbeobachter20FPS und achtBots liefen jeweils600s ohne neue Syncfehler.
Nicht unnötig wiederholen. Kein aktiver WAN-Input-/Powerupvergleich.
Vorhandene Dev-Powerup-DLL frisch auf49Source+30Overlay/81Pins geprüft:
`/srv/tse-dev-powerup-build-001-20261111`, Manifestb3bbd208…,
Quelle4046a59c/Treeca088e12/DLLfe4a77bd. Filter standardmäßig aus,
`dev_bRemoveDamageAndInvisibility=1` entfernt Typ0/2 in NewGame nach
StartPeerToPeer vorSetupLocalPlayers. Quelle im separaten
`/srv/tse-dev-powerup-filter-20261111`; unverändert lassen. Ein kontrollierter
Filter-off/on-Vergleich ist noch nicht vorbereitet oder ausgeführt.

## Aktueller Kandidat und A4

**Build025 bleibt tatsächlicher Windows-FAIL** ausf905962: MSVC C2059,
leeres Windowsmakro`far` kollidierte mit Diagnoseparameter.
Makro-RED5c6b2cf/Fix06a14b3/Reportc98b2ad integriert als
cd02b33/ea93115/b38e3a0. Einzige Headerzeile Parameterfar→farValue.
Autor3532/0 normal+ASan unter aktivem Makro, Root3532/0/Bytevergleich;
keine16Parentwiederholung. RootEV/reacquire-winmacro-root-review.json.

**Build026 gebaut, nicht nativ qualifiziert**:

- Quelle05e1708abc8b886895157b57a28e35d7375c4f29,
  Tree1f96c7a6d439f9f894de0dca214d56a846ddc5c5.
- DLL2c9a238191b9642bf7f9613f01a461cf711f97fe62e581bdd7c93b5f58a9bcdd,
  443392Bytes; Manifestbe0513a059e2dcf5bda364ea70c4f2dee800fb084d2c44861912eaa22e186fd3.
- `/srv/tse-milestone-a-build-026-20261115`:15MSVC+Link0,
  Root47Sources28Overlay/77PinsPASS, nurHeader gegenüber024 verändert.
- Passive Reacquirediagnose, kein zusätzlicher Cast/Lookup/RNG oder
  ursprünglicher Guard-/Aktionswechsel. Originalbodyinverse88950482…,
  Formatgrenze2029B+NUL<2048. Ein angenommener Vorschlag ist kein Pickup.
- [Buildbericht](../reports/2026-11-15-build026-diagnostic-build.md).

024DLL192169fe…/438272B, Quelle100bda43…, drei einzelne600s-Fenster mit
Hard2/8DEMON/Original20FPS/diag0 geschlossen, allevier normalenCloses,
Root640Dateien+4Logs/Units/PIDs/Display/SperrenRestorePASS, keine neuen
sechs Fehlerklassen. Keine vollständige A4-/Dauerqualifikation:

| Map | Kills | Leben/Useful/gewinne | längster beobachteter Abschnitt ohneUseful |
|---|---:|---|---:|
|Red|172|186/90/121|50,14s,links zensiert|
|Skulls|170|192/95/113|242,49s,links+rechts zensiert|
|Trouble|236|279/137/184|33,39s,nicht links zensiert|

Skulls konkreter Funktionsgegenbefund: Slot0/Spawn358.13607788,
beobachtet358.18606567..600.67687988, keineZusatzwaffe/keinFire/HP85.
Actual ItemTransitEnd seit379.75→389.75/no_hop_progress, danach221Snapshots
ohneGoal/Anchor/Navsource/Hop; regionaleSchleife, nicht242sStillstand.
Rückkehr-/Support-/LOS-/Budgetursache UNKNOWN, deshalb026diag1.
[geschlossener Audit](../reports/2026-11-15-build024-skulls-closed-functional-audit.md).
Red9GroundReplans und Trouble1 belegen die neue StaleAnchor-Verzweigung nicht:
unmittelbarer alterAnchor UNKNOWN, frischerHint schon vorher gesehen.

024Hole/Yodeller600s sind separat vorbereitet, noch nicht ausgeführt;
026belegt diese Karten nicht automatisch. NeunKartenmatrix:
DesertTempleWorld fehlt/gesperrt; LostTomb/Fortress/Compound vorhanden,
noch nicht funktional qualifiziert. Keine Kooparbeit/Cecilparitätsbehauptung.

## A1/A3/A5 und B

A1 [First-State-Vertrag](../reports/2026-11-12-a1-original-first-state-contract.md)
bleibt bindend: erste tatsächlich verarbeitbare Original-Lebenszustände,
normale Bullet-/Damagekette/HP/Armor/Tod, Bots+Original/Neustart/Kartenwechsel.
Config0 allein kein Schadensbeleg. I1Stateordnung/I2Bulletbindung/I3Validator/
I4boundedController und uninstrumentierte Kontrolle offen.

Mouse222350/005628 und Keyboard022737 FAILs bleiben. Keyboardresultatf8c13257,
12Calls/Attempts/Keymaps,6Releases/EinzelACKs,45Paare46Reads39Policyframes,
Pitch0→30→7,5 statt Rückkehr≤0,75. Rootvollreplay bytegleich5078d455…;
664Dateien9Abwesenheiten3Logs/PIDsUnitsDisplaysSperrenRestorePASS.
Kein genauer Callbackcount/Ursache/Gainfix/Schussbeleg.
[Audit](../reports/2026-11-15-original-keyboard-closed-audit.md).

Neue [Pitchfeedback-Spezifikation](../superpowers/specs/2026-11-15-a1-closed-loop-original-input.md)
7514449→Rootd7bf1ae genehmigt innerhalb bestehenden Auftrags:
+12Detour,dann tatsächliche1px-ACK-Korrekturen, unveränderte0,75°-Rückkehr;
max48Aktionen/96Attempts/.35sHold/2sACK/20saktivePhase/85sGesamt/90sRunner,
EPS.001, 2,35sReserve vorInput. KeinCP-Gain-/Toleranzrefactor/Memorywrite,
keinFire. Policy/Journal/Builder fertig und Rootreviewed24/0; Rootfreeze und
begrenzterWrapper fertig, 064Backup/Native noch ausstehend. VierCoredateienbytegleich.
Rootbefund direktePitchdistanz statt zyklischemCP.same durch zwei echteREDs
behoben; kopierterCP-ACK-AST unverändert. KeineGain-/Schuss-/A1-Abnahme.

A3 gemeinsameTaktik/tatsächlicheMITTEL<STARK<DEMON/humanesNiveau offen.
020STARKvsMITTEL13:3, Rollentausch5:6; Legacy-SwapanalyzerFAIL3Inventarleben
vs4SourceSpawns bleibt. Komponentenaudit31FällePASS keinStärkenbeleg.
Vergleichbare Red048/018/020600s:84/168/159Kills, keine direkten Kandidatenduelle
und unterschiedliche Lebensdauern; kein pauschaler Gesamtsieger.

A5 formale1/4/8-Botgates60/60/120min noch nicht begonnen; erst nach funktional
geeignetem Kandidaten, keine zusätzliche gleiche Langzeitschleife ohneGrund.
Root-Hostobserver87bced91/helperf786416a/budget9a8132af:1s-Messung,CPU≤75%,
RAM≥1,5GiB,Disk≥8GiB; intervalavg inklFremdlast,keinpauschalerKapazitätspass.

B erst nach vollständigem A. Noch keine Sessions/Chatimplementierung.
Zustände offline/joining/active/leaving/cooldown/failed, stabileInstanz+BotIDs,
exklusiverController/idempotent/backoffjitter, mindestens8nachKapazität,
ErsatzvorLeave/Menschenpriorität. Aufenthalt20–90min/Pause3–20min,
Zielwechsel10–30min/max1gleichzeitig≥30sAbstand. Chat5–12%,CD3–8min,
max3/60s≥10sAbstand/1–4sDelay/keinidentischerText30min,DE/EN;
RUerstEncodingtest. WeitereAbnahme im ursprünglichen A/B-Plan.

## Veröffentlichung, Backups und nächster Schritt

Letzter tatsächlich gefetchter Remoteaed02cd6926d3e88e2b6b24a194ffb39ca42a719,
Treee06e97231deee95e0a10d184931b145f80c9368d exaktRoot7a4bf42.
NeuereCommits/aktuelleHEAD noch veröffentlichen. GitHubAPI mit expected_sha,
forcefalse; tatsächlicherFetch+Tree-/Diffvergleich, keineForcePushes.
main/PR99 unvollständig, keine abschließende Integration behauptet.

Driveprojekt14HBTUlfJvyE821KnoHJhNGZ__4Ge2-y2. Deltas022–064 vollständig
extern rückgelesen, alle Inhalte/Metadaten rekonstruiert; ursprüngliche Archive
und050/051Rollback nicht löschen. Aktueller Mischrollback051:
83540880B/SHA85249af2c74e465a74c3bdb0a8f636936a9033d6f20e48316963f8a9b4de5a06,
Drive1XX2UTI3VigXY-AdSW2Ep0HwkhJ54Kz3L,
`/srv/tse-current-mixed-fleet-backup-20261114`.

Neueste063:12093715B/SHAaf1803a745acc71c8ffe758afa57685069ed4bb1740da2fe3695ec22387f2f6a,
Drive1J5j9k012p2_O3IuzmaPK37YxcrTLAILK,332Files/16737176entpackteBytes,
vollerDrivehash+zweifachalleDatei-SHA/UID/GID/Mode/mtime_ns PASS03:07:16.
Enthält026Vorbereitung/DevSyncdeltas/Powerupclosure/Sourcebundleb28e972,
benötigt75ba3bb aus062; dieses067dda4 aus061; jenes6f4fbbd aus060.
NativeVollrestoreStart NICHT geprüft. 064 e93e5ddf/24063346B/1022Dateien90395513B vollständigDrive+zweifach
MetadatenPASS034135, Drive1WzItQF8GqgIce3s2ihkfhLiS-yo10Yy_.
Enthält geschlossenen026Fall/Audit undFeedbackvorbereitung, Bundle7a4bf42
benötigtb28e972 aus063. NeuesterFeedback-FAILrawlauf nochzusichern.

Speicher: nur geschlossene eigene Belege verlustfrei gzip-komprimiert, jedeDatei
vorOriginalentfernung vollständig auf SHA/UID/GID/Mode/mtime_ns rekonstruiert.
024Red/Trouble18Dateien250224378→18064685B (Originale zusätzlich058/061Drive),
026+Rootreplay13Dateien187370676→14331994B (inzwischen064vollDrive).
RootEV/compressed-closed024-red-trouble-index.json und
compressed-closed026-and-root-replay-index.json pinnen sämtlicheOriginalmetadaten.
AusführbareRestorehelfer restore-compressed024-red-trouble.py --map redstation|trouble
und restore-compressed026-and-root-replay.py --scope native|replay|all.
8GiBFloor und64MiBReserve nicht gesenkt; ein erster024Kompressionslauf stoppte
korrekt vor zu großerTempdatei und wurde kleinsteDateien zuerst fortgesetzt.
Alter045Retireversuch stoppte vorMutation, weil048/018/020 bereits komprimiert
waren; vorhandenenRestorehelfer wiederverwenden, keineDoppelkompression.

Nächste konkrete Reihenfolge:

1.Feedback-FAILraw/Rootguardreplay/Restorebericht undSource-Reproducerfortlaufend
  publizieren+sichern. Source073/064bereitsvollbelegt, neuereCommitsnochlokal.
2.A1 engerMethodenadapterinArbeit: alter18Call/38Binding-I1I2-/Drainvertrag
  Registrygenau2/unveränderteLimits. EchterGetterFunctioncallback, admission-only
  stop+outside-callbackIdle/finishstop, admittedLeavesunteraltenTTL. Separate
  status-RPCs, Drainpayloadunverändert. LegacyPortsadaptermitFreshExec3Rollen
  server/vanilla/botA, 2MiBpayload+16KiBfesteIPChülle, keineTruncierung; alter
  Runnerdeaktiviert/unverändert. KeineAI-/Populations- oderWaffenvertragserweiterung.
3.A4 Source-Reproducerintegriert8554080/16a3095/9b94a45: einnormalerBridge-Lauf
  3541Checks/0FAIL,9neueAssertions. 70gleichePoseProposals: visibleCombat0Owner/
  0Stall/0Escape, novis70Owner/30Stall/12Escape; nurfalschesStandOn70/30/0.
  KeineEpisodekausalität. FolgenderOptin-RecoveryfixjetztimWorker: getrennte
  combatRecoveryRequested nurautomatic/humanMode/visible/nonneutral/up0/noSupply,
  gleichefrischeObservation/Support/Map/Life/Contactpins, keineNavhint-/Flightgrant.
  EchteRED3544Checks/2FAILvorCode,0.5Normale/2s/.25m/.25gap/.3/.6/unveränderte
  Budgets. KeineNormallockerung; neuerMetadatencaptureexplizitproduktivesDelta,
  nichtinderpassivenDiag-Inverseverstecken. Header/Driver+Bridge+ActionNativeTest.
4.Disk≥8GiB/64MiBReserve, keineaktiveRuntime. RootmussÄnderungenreviewen,
  getrenntePakete/eigeneFreeze-/Pinnachweise/Backup, erstbeiechterEignung
  neuenKandidatenbauen+isoliertNativeprüfen. A3/A5/Karten/Bweiteroffen.

Keine unbeaufsichtigten Prozesse behaupten: gestartete Aufgaben/Jobs und
Eigentum müssen vor Fortsetzung erneut tatsächlich geprüft werden.
