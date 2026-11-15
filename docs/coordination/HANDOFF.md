# Aktueller Handoff – 15.11.2026, 05:29 UTC

Gesamtstatus **A offen, B nicht begonnen**. Kein externer Zugriffsblocker.
Reguläres lokales Terminal funktioniert; RDC bleibt gesperrt und unbenutzt.
**Keine Native-/Buildausführung aktiv.** Beide First-State-Methodenarme sind
beendet, inklusive Worker und aller drei regulär geschlossenen Spielrollen.

- Control `a1-first-state-method-enabled-root-control-20261115-051115`:
  **PASS_LIMITED_UNINSTRUMENTED_TWO_ORIGINALS_ONLY**, 10,000165s ohne Input,
  API oder Frida. Resultat `7c4bf5af2c885e74e478ff4cf4e475cd2cddf38f69095ad4cd80fe64b0c2859d`.
  Rootrestore 05:12:11: 664 Dateien, neun Abwesenheiten, drei Logs, PIDs/Units/
  Displays/vier Sperren geprüft. Parent1609045/Start134587274 beendet.
- Trace `a1-first-state-method-enabled-root-trace-20261115-051307`: **FAIL**
  beim Armieren vor dem Attachloop: Fridas Linux-Modulliste findet Wine-PE
  `Engine.dll` nicht. Keine beobachteten Callbacks, kein aktives Messfenster,
  null Input. Resultat `e682374f91601d831cccbf6f7fcf67aba3bfd84f12903546da9fe4f2e7551406`.
  Nachlaufvalidator ebenfalls FAIL (noch nicht initialisierte by_kind-Felder);
  keine Schemaaufweichung. Unload/Detach erfolgreich; Worker1610148 nach drei
  normalen Rollencloses beendet. Parent1609746/Start134598483 beendet.
  Rootrestore 05:14:52: 664 Dateien/neun Abwesenheiten/drei Logs und alle vier
  Sperren/PIDs/Units/Displays geprüft. Zusätzlich pure Rootprüfung05:23:14:
  alle 38 gespeicherten vollständigen Originalbereiche vor/nachher exakt zur
  unveränderten HIGHLOW-Policy, Identität gleich. Das akzeptiert nicht den Trace.
- Nächster Schritt: exakte schreibgeschützte PE-Headerprüfung an den unabhängig
  gepinnten Hostbasen statt Linux-PE-Modulliste; neue deaktivierte Paketversion,
  VM-RED/GREEN, Rootreview, Sicherung und neuer begrenzter Einzelfall.
  Alte Pakete und FAIL bleiben erhalten; keine automatische Wiederholung.

Delta068 vollständig Drive-rückgelesen und 1138 Dateimetadaten geprüft05:10:06:
17005507B, SHA `7b496b0ae1a529681257dfde0f13d7858c5555fc4391daff2451c37f9a1b6210`,
Drive `1GPjgf2bMe0EXzyL9L0rCRze9CIXcZXr-`. **Die beiden neuen Nativearme sind
noch nicht in069 gesichert.** Source077 Remote `2dac458382939fd0044e99d7ca704e7424757dbe`
ist tatsächlich gefetcht, exakt lokaler9a41a43/Tree179cbf20. Bundle9a41 benötigt
1a0ad0b aus067. Root-Handoffänderungen danach noch lokal.

027Skulls600diag1 geschlossen: `nav20-027-skulls-root-skulls-20261115-043608`,
Result55954ed68802b99c8d2d4004e0840d94931b92975ee6698685d440a9c48dcb2b,
600,052021s, vier normale Closes/keine BAD oder Disconnects. Rootrestore640Dateien/
vierLogs/PIDsUnitsDisplays/vierLocksPASS. Vier qualifizierte Reader exakt
invertiert, sechs Helfer bytegleich; Root prüfte alle Outputhashes ohne erneuten
Vollparse. 190Leben/97Usefulleben/118Gewinne/558ReadFAIL. Exactstill5,15s,
NoUseful52,087s offen; kein kausaler Vergleich oder A4-Pass. Publicbericht:
[geschlossener027-Audit](../reports/2026-11-15-build027-skulls-closed-audit.md).

Storage nach sechs exklusiven Root-Retire/Rekonstruktionstests05:27:38:
11.000.229.888B frei. 31.321 Dateien/2.252.459.190B tatsächlich neu rekonstruiert
und alle SHA/UID/GID/mode/mtime_ns geprüft; jeweils nur alte und danach neue
eigene Testkopie entfernt. Originalarchive/DriveReadbacks/Drive erhalten.
Vierzehn Symlinks nur indiziert. Exakte aktuelle Tempmetadaten neu erhalten,
keine historische Originalmetadatenqualifikation erfunden. [Bericht](../reports/2026-11-15-verified-storage-reserve.md).
RootEV/six-retired-restore-copies-summary.json und sechs Metadatenoverlays/
Restorehelfer, jeweils --restore-only. Vor weiteren Writes immer aktuelle Reserve.

Wineheaderfix Teil1 integriert973ac7a (Autor dbc2a00, Spezifikation ausaa48bdb
mitübernommen). Root19Tests/1,145sPASS, zwei tatsächliche Originalheader frisch
gegen Dateihash/PE geprüft, ganze Body-/JSinverse gleich. Noch kein neuer Native-
Nachweis; deaktivierter Freshfork in Arbeit. BefundRootEV/
first-state-wine-identity-root-source-review.json. AlterTraceFAIL bleibt.

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
`a4_diagnosis` entwickelt den begrenzten Wine-Modulidentitätsfix in
`/srv/tse-build026-skulls-closed-audit-20261115`; `candidate_audit` untersucht
nur Storage/alte Restore-Testkopien in `/srv/tse-a1-pitch-feedback-20261115`.
Beide getrennte Worktrees/Claims, kein Native oder Livezugriff, keine Löschrechte
im Auftrag. Vor Native müssen ihre CPU-/Dateilesearbeiten beendet und STATICONLY
bestätigt sein. Root integriert allein.

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

Frisch05:29:08UTC: alle18 geladenen Rollen/Datei-/Configtargets gleich dem
Mischrollback051. Jede Instanz acht eigene Bots. Zusätzlich Dev eine
ungeklärte Verbindung, andere keine; nicht dem abgemeldeten Nutzer zuordnen. Das ist eine aktuelle Modul-/Queryprüfung,
kein neues Kampf- oder Syncqualifikationsfenster.

| Instanz | Port | Map | Bot-DLL | Sessions/Chat |
|---|---:|---|---|---|
|Dev|25650|Red Station|Cecil048 `ec820d04`|nicht implementiert|
|Red Station|25600|Red Station|Gen2 `7fc94a39`|nicht implementiert|
|Yodeller|25610|Yodeller|Build018 `6db89204`|nicht implementiert|
|Skulls|25620|We Got Skulls'n'Bones Too|Build018 `6db89204`|nicht implementiert|
|Little Trouble|25630|Little Trouble|Build018 `6db89204`|nicht implementiert|
|Hole|25640|Hole|Build018 `6db89204`|nicht implementiert|

Vollhashes in RootEV/fleet-current-after-method-pair-private.json; tatsächliche
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

Letzter tatsächlich gefetchter Remote c57467c4acd2a9f7f971ee6c1649badf64f3a5b7,
Tree e30e0b6b374720182f5d140ec50690fce01b0be5 exakt Root e54282c.
Source074 vorbereitet+Remote tatsächlicher Fetch/Diff0. Source075 tatsächlichgefetchter Remoteff32dc1c0fbeb4cd7991cf407e39eeb271099355,
Treeeadd2e1e28f03bc65acdf563f95ebd1eec4c762b exaktRoot13896f5,Diff0.
UmfasstMethodAPI+Combatfix; neueRunnernachfolgendpublishen.
main/PR99 unvollständig, keine abschließende Integration behauptet.

Driveprojekt14HBTUlfJvyE821KnoHJhNGZ__4Ge2-y2. Deltas022–066 vollständig
extern rückgelesen, alle Inhalte/Metadaten rekonstruiert. 065:
2842626B/SHA d4bb3b7e203ff27356a3a8c45750b95e38d0c3627dc3010535226e38ee4d2f0e,
Drive1ZS2s_f6WiQtNmAL_jjyUEg88G8wG0p1J,724Files/19854093entpackteBytes,
Drivehash+zweifach alleDateimetadaten PASS04:04:21. Enthält Feedback034224
vollRaw/Rootaudit/Restore, Source-Reproducer, Sourcebundle e54282c benötigt
7a4bf42 aus064→b28e972 aus063→75ba3bb aus062→067dda4 aus061→6f4fbbd aus060.
KeinNativeVollrestoreStart aus Dateirekonstruktion ableiten.
Aktueller Mischrollback051:83540880B/
SHA85249af2c74e465a74c3bdb0a8f636936a9033d6f20e48316963f8a9b4de5a06,
Drive1XX2UTI3VigXY-AdSW2Ep0HwkhJ54Kz3L,
`/srv/tse-current-mixed-fleet-backup-20261114`.

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

0.027Skulls geschlossen und vollständig ausgewertet:190AI-Leben/182Tode/
  97Usefulleben/118Gewinne/3892nativeFIRErequests/558ReadFAIL(500state58tick),
  125linkszensiert/8rechts/2ambiguous. Exactstill5,150s vs02616,546s;
  längsterneverUseful52,087s vs52,303s. KeinallgemeinerVerbesserungs-/Kausal-/A4pass.
  4Reader exaktinverse/sixHelpersgleich, Root alleOutputhashes/Sourceinversen
  geprüft;keinwiederholterVollreplayohnePrüfgrund. Handoffec6d9ece/Finalb2917132.
  [027Audit](../reports/2026-11-15-build027-skulls-closed-audit.md).
  067376159B/5ebb6c9d/Drive13W-zlZG2Y-ig7RQVWXfy94Z0gq4aa-Js,
  210Files1489467B vollDrive+zweifachMetadatenPASS04:35:27. Source07638d803a
  gefetcht exakt1a0ad0b/Tree956a978, Bundle1a0ad0bbenötigt13896f5 aus066.

1. **Combatfix fertig, noch kein Retailbuild/Runtimebeleg.** Root Source-/Testreview,
   3663Checks/0FAIL, Author6Logpins/5Sourcepins geprüft. Reale ersteRED3544/2,
   später Rootfund negativeMap RED4/3→GREEN4/0; finaleHeader5530062b/Driverebb2c4cc.
   Neuer ausdrücklicher produktiver Capturecall in Reacquire; alteBodyinverse
   88950482 bleibt nach gesonderter Entfernung exakt. Normalbewegung ungebremst,
   nur frische eigeneCombatownership+Stall+unveränderteSafetyguards erlaubenEscape.
   KeinBeweis für Ursache der026Episode. Rootreview in privatem
   RootEV/combat-recovery-root-source-review.json, öffentlicher Bericht
   [Combat-Recovery](../reports/2026-11-15-automatic-combat-ground-recovery.md).
   027 gebaut:Quelle13896f5/Treeeadd2e1/15MSVC+Link0,47+28+Manifest+DLL77PinsPASS.
   DLLf5bf76801cade78803c6f4bcf97837390329fc30d2a016d202a9f4b96bbfc17e,
   446464B,Manifestca235d88. KeinNativepass. [Build027](../reports/2026-11-15-build027-combat-recovery-preparation.md).
2. **MethodAPI fertig, nur offline.** Root35/0Tests und vollständigerSource-/Testreview;
   disabledManifest1e59d326/72Pins, alterRunnerFalse. Getterfunction/admission-only
   Stop/idleoutsidecallback/finishstop,18Hooks38BindingsRegistry2/alteI1I2-Drain-
   Grenzen unverändert. FreshExec/LegacyPorts+rawJournal vorParsing, Ownerreceipt
   vorIPC, reap erst nach3normalenCloses. Rootreview FirstStateMethod in RootEV.
   [Bericht](../reports/2026-11-15-first-state-v2-method-adapter.md).
3. **InputfreiesMethodwindow fertig/inRoot integriert.** Root21/0 undvoller
   Source-/Testreview. EchteR1-Verifierlücke durch5REDs Body/Policy/NestedHash/
   Path/Helpergeschlossen; erwartetevolleHashwertejetztgeprüft. Finaldisabled
   51e1bc45/151Pins72Methoden. AlterCheckpointf2cae1f7 bleibtunverändert.
   ErstesRootfreeze26d62d26 hatbewusstnochdeaktivierteMethodpfade, niegestartet.
   TatsächlichesneuesEnabledRootfreeze b86615c13475f9e7dd430c4f1154b025f83fef8061865d1f7c9990de7f1c9336,
   Runner6a33221a/Nested0c4ab262, RootEV/first-state-window-enabled-root-source-review-freeze.json.
   ExaktMainGate+zweiNamespaces+Transport-/compiledJSGate+NestedmanifestAdmission;
   sonst90Filesbytegleich, Sourcebody/Policy/18Hooks38Regions11Bindings/alleGrenzen
   gleich. Bindungsmetadata/ACK bleibenfalse, alte6Input-/BaseCLI-/FirstStategatesfalse.
   Peer3f787786 ScopeRootdelta/PinsPASS151+72, keinePolicyUnabhängigkeitbehauptet.
   Rootwrappercontrol6d8a3a64/traceb9756aa1, Outer8431bdf2/4fa18d2e.
   Fest1Control+1Trace je10saktiv,85/90sAdmissionkeinHardwatchdog; Traceabhängigvon
   bestandenemControl+Rootrestore. KeinFire/Maus/AI, TLS+echtesTickpaar+voll38Restore
   gibtmaxnurObservedCallbacksstatus, keineA1/18ABIqualifikation.
4. VorControlNative:068sichern+vollDriveprüfen/Source077publizieren, beideWorker
   quiescent/fresh4Locks/PID-/Unit-/Display-/Diskvorprüfung. RootaloneNative;
   normaler3Rollenclose+unabhängigerRestore nachjedemArm. KeinAutomatikretry.
5. A1 echteOriginalopfer-Schadenskette, A3Tiernachweis, A4Restmaps/Spezialübergänge,
   A5formaleGates erst nach funktionalem Kandidaten. B erst nach A. LiveMischstand
   behalten; kein Promotion allein ausBuild/Portablepass.

Neue verlustfreie Kompression nach065:024Skulls9Dateien121495597→8411831B,
RootEV/compressed-closed024-skulls-index.json und restore-compressed024-skulls.py;
Originale060Drive. 022+023Red18Dateien242582133→17268030B, Index
compressed-closed022-023-red-index.json, Restorehelfer
restore-compressed022-023-red.py --build 022|023; Originale050/053Drive.
Vor Entfernung jedesOriginals vollständigesTestrestoreSHA/UID/GID/Mode/mtime_ns
geprüft; Archive vorKompression gegen frühereManifeste undDrivebelege verifiziert.
Neue Gzip/index/Helper vollständig066Drivegesichert. 06627382263B/
SHA72049d8accca6105d417350a757dea4f5bb1554809117bb2bebf0ff9b5290836,
Drive1mnNPd_Y2zsB5PAYLrqzGbWN5qdq_U9Fq/239Files32631557B,
vollerDrivehash+zweifach alleDateimetadatenPASS04:31:15. Bundle13896f5
benötigte54282c aus065. Aktuell~8,98GBfrei;8GiBFloor bleibt.

Keine unbeaufsichtigten Prozesse behaupten: gestartete Aufgaben/Jobs und
Eigentum müssen vor Fortsetzung erneut tatsächlich geprüft werden.

Speicher05:03:14Files geschlossene027Raw+Audit193483370→14576757B verlustfrei,
jedesFilevollTestrestoreSHA/UID/GID/Mode/mtime_ns vorOriginalentfernung.
IndexRootEV/compressed-closed027-and-author-audit-index.json, Restorehelfer
restore-compressed027-and-author-audit.py --scope native|audit|all. ErsterVersuch
stopptevorMutationwegen64MiBReserve; Reserve/Floornichtgesenkt. Erst16bereitsvoll
Drive-/Archiv-/MetadatenverifizierteDoppeldateien(15alteGitHubAPI-Payloads+ein
Root023Duplikat)lokalretired15440600B, keineArchive/Runtimefilesentfernt.
Indexretired-verified-transport-and-duplicate-replay-index.json, ausführbar
restore-retired-verified-copies.py --restore-name NAME; tatsächlichesTempTestrestore
aller16Files samtNSMetadaten bestanden, anschließendnurverifizierteTempfilesentfernt.
EininitialerPAXfloat-nsCheckstopptevorEntfernung; maßgeblichesexaktesNSstehtim
archiviertenManifestundwurdemitgeprüft. 068enthältneueGzip/Indizes/Helper.
8GiBFloor/64MiBReserve bleiben, aktuell~8,84GBfrei. KeineNativegeradeaktiv.
