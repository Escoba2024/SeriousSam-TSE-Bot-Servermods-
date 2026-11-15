# Aktueller Handoff – 15.11.2026, 02:57 UTC

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

## Laufvorbereitung03:05UTC

026Skullsdiag1-Builder/Plan/Claim/Report integriert (Autorc29fa93/ce7de6f/
aa8471c/c8502bb). Root vollständigerSource-/Testreview und11gezielteTestsPASS;
Rootfreeze b82e1bd823135c9cc409a5802c2077964ebd52662c0facdef5ae2d2546870806,
Controller1e06b182ba838cbf07685bdd20d0af6b4985eb6692828381f55ce986d9d56089.
UnabhängigerRootdeltareview87415519b1995c8421176429bc487ab47f46dcf3f67b017a9136306774ebd73b
PASS_SCOPE/noC/I:einGate/zweiNamespaces exaktinvers,140/88/51Pins,
88anderePayloadfilesgleich,77neue026/0aktive024Buildtargets.
ScopeausdrücklichnurRootdelta/Pins,nichteigenePolicyunabhängiggeprüft.

Rootwrapper RootEV/run-navigation026-skulls.py SHA
b3b8ac82c30c7057ff5cd73611a3ba9ac32ec2f0ee4857b97506a8a043e49615,
Outerobserve-navigation026-skulls.py SHA
f2e46748a8bb5d49f06519dfb102a16129dff7d601814ddbef4f4e5d6892754b.
BeideASTgeprüft; Parent verlangt063fullDrive/Rootrestores/Pins/Reviews,
OwNS27850/Hard2/8DEMON/Original20FPS/diag1/600s,nurreinenSkullsfall.
NochkeinNative gestartet. WorkerA4quieszent/STATICONLY, A1isoliertoffline.
NeueQuellen072publish/fetch/Bundle und063externvollsichern, dannA1ebenfalls
STATICONLY bestätigenlassen undeinmalstarten. KeinLivewechsel/Aoffen/Boffen.

## Zugriff, Arbeitsbereiche und Sperren

Root allein integriert und verändert Runtime. Zwei bestehende Worker:
`a4_diagnosis` bereitet nur den deaktivierten026-Skullsdiagnosefall vor;
`candidate_audit` implementiert nur den getrennten A1-Pitchfeedbackfall.
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

Frisch02:48:00UTC: alle18 geladenen Rollen/Datei-/Configtargets gleich dem
Mischrollback051. Jede Instanz acht eigene Bots. Zusätzlich Yodeller eine
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

Vollhashes in RootEV/fleet-current-after-build026-private.json; tatsächliche
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

026-Skulls600diag1-Paket aktuell eigenerWorker, geplant vier enge inverse
Retargetdateien, Hardmapdiag0-Guard tatsächlichRED→nurDiag1Policy. Root muss
alle77altenBuilddeps entfernen/neue77prüfen, übrige Parentdateienbytegleich,
Status-/Finalizergrenzen reviewen, einfrieren und unabhängig prüfen lassen.
Keine Nativeausführung vor abgeschlossenem Source-/Pinaudit und Backup.
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
keinFire. Worker bereitet neue reine Policy/Tests/deaktiviertenBuilder vor;
Root erst nach Review/Freeze/Backup genau einen Fall. VierCoredateienbytegleich.

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

Letzter tatsächlich gefetchter Remote346a86f6934fe04a1bf866e8ff4a2f8eb0f1f10d,
Tree4eea6687ab2b9e8aea1c28af222a84ee83eb6790 exaktRoot75ba3bb.
NeuereCommits/aktuelleHEAD noch veröffentlichen. GitHubAPI mit expected_sha,
forcefalse; tatsächlicherFetch+Tree-/Diffvergleich, keineForcePushes.
main/PR99 unvollständig, keine abschließende Integration behauptet.

Driveprojekt14HBTUlfJvyE821KnoHJhNGZ__4Ge2-y2. Deltas022–062 vollständig
extern rückgelesen, alle Inhalte/Metadaten rekonstruiert; ursprüngliche Archive
und050/051Rollback nicht löschen. Aktueller Mischrollback051:
83540880B/SHA85249af2c74e465a74c3bdb0a8f636936a9033d6f20e48316963f8a9b4de5a06,
Drive1XX2UTI3VigXY-AdSW2Ep0HwkhJ54Kz3L,
`/srv/tse-current-mixed-fleet-backup-20261114`.

Neueste062:4782193B/SHAe04fa98fe737afbd7e5f594a56b897b8834480c8052e179fc3252e5733f2077c,
Drive1fzNIffBqn92hvsS8m81L8PhfRK2bAETP,
945Files/30425209entpackteBytes,vollständigerDrivehash+zweifachalleDatei-
SHA/UID/GID/Mode/mtime_nsPASS02:47:12,TempRestoreerstanschließendentfernt.
EnthältKeyboardRaw/Audit/025FAIL/026Kandidat und Sourcebundle75ba3bb,
benötigt067dda4 aus061; jenesBundle benötigt6f4fbbd aus060.
NativeVollrestoreStart aus diesenArchiven NICHT geprüft. Quellen-/Archiv-
Rekonstruktionskommandos und Einzelpins in Backuproot/create-/verify-delta062.py,
Manifesten/Quittungen und Gitbundles. KeineRetaildateien/Rawidentitätenpublizieren.

Nächste konkrete Reihenfolge:

1.026Skullsdiag1-Paket vollständigRootreviewen, separateRootkopie einfrieren,
   unabhängigesFreeze-/Pinreview, neueQuellen tatsächlichpublish/fetch.
2.NeueSyncdeltas/Powerupclosure/A1Spec/Skullspaket/Rootwrapper mitSourcebundle
   in063 externvollrücklesen;8GiBFloor einschließlichRestoreReserve erhalten.
3.WorkerSTATICONLY/quiescent/sämtlicheSperren frisch, genauein026Skulls600-Fall
   unterHostobserver, anschließend unabhängigerDatei-/Modul-/Prozessrestorecheck
   undvollständiger konservativerLifecycle-/Diagnoseaudit. NeueFehler stoppen.
4.A1Feedbackpaketreview/Freeze/Backup/Einzelfall und neue normale Schuss-/
   FirstStatekette; Sync-Powerupoff/onKontrolle separat vorbereiten.
5.BelegteNavigationkorrektur/übrigeKarten/A3/A5 abschließen, erst dannB;
   Live nur nach tatsächlich nachgewiesener Verbesserung stufenweise ändern.

Keine unbeaufsichtigten Prozesse behaupten: gestartete Aufgaben/Jobs und
Eigentum müssen vor Fortsetzung erneut tatsächlich geprüft werden.
