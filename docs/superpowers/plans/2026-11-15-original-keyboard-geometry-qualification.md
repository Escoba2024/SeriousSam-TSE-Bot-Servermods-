# Original-Keyboard-Geometriequalifikation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking. Root integriert und führt Native allein aus; keine weiteren Subagenten.

**Goal:** Einen separaten deaktivierten Original-NoFire-Fall mit genau vier normalen Keyboard-Gegenimpulsen und ehrlichem Winkel-/Release-/Geometrienachweis vorbereiten.

**Architecture:** Eine neue reine Qualifikationspolicy und ein enger normaler Keyadapter verwenden vorhandene XTest-/Endpoint-/Actionstep-/Reader-/Restorehüllen. Die private Controllerkopie startet denselben eigenen Original-/Bot-/Serveraufbau, ersetzt aber ausschließlich dessen Maus-/Frida-/RECORD-Kalibrierprogramm durch vier Lookkeys plus dieselben zwei bestehenden normalen Forwardimpulse zur Yaw-Bodyausrichtung. Bestehende Mauskalibrierung, CP und vier Coredateien bleiben bytegleich; der neue Fall kann an grober Winkelauflösung scheitern und endet immer vor Aim/Route/Fire.

**Tech Stack:** Python3, bestehendes Xlib/XTest auf eigenem154, unveränderter Retail1.07-Client, bestehende passive server-/clientseitige InventoryReader.

**Spec:** Rootauftrag nach93a0b44 und `docs/decisions/2026-11-15-a1-cursor-boundary-and-keyboard-options.md`.

## Global Constraints

- Nur Offlinequellen/-tests/-pakete nach Rootplanreview; Root allein Native/Display/Input/Frida/Live. Keine Runtime in diesem Planauftrag.
- Alle bestehenden PID/Start-/Module/Inode/Namespace-/Lock-/Fokus-/Host-/Log-/Restore-/Clockguards erhalten; CPU≤75%, RAM≥1,5GiB, Disk≥8GiB.
- ACK2s, EPS0,001, frische Paarreads≤0,2s, vorhandene Stabilitätshaltezeit≥0,1s auf beiden Gameclocks, CP85s/Runner90s, max48Actions und max96nativeAttemptrecords unverändert.
- Genau6geplante Aktionen je0,1s (4Look+2Forward),12Down/Upcalls; vorhandene Actionstepgrenze0,1+0,25=0,35s einschließlich Release. Kein Retry oder weiterer Forward-/Maus-/Fireimpuls.
- Profileingriff nur `vanilla/Controls/Controls0.ctl`, nach sealed FileTransaction und vor Launch; Originalbins/Guid-/Playeridentitäten/vierCoredateien unverändert.
- Separates Result: begrenzte Keyboardqualifikation, qualified/a1_pass/mouse_gain_fixed/input_once/actual_shot_proven/foreign_hit_proven=False. Keine alten FAILs umwerten.

## Design und tatsächlich gelesene Pfade

Eigenes Plan-WT `/srv/tse-a1-keyboard-qualification-plan-20261115` ab93a0b44.
Aktueller Claim nur dieses neue Plandokument. Spätere Implementierung erst nach
Rootreview, im dafür neu benannten eigenen Worktree.

Tatsächlicher wiederzuverwendender Parent:
`/srv/tse-a1-xres-lifecycle-root-frozen-20261115`, Manifest
`e9cb52a1135ea3046570fdaaac6e2f37ac2117535b8d4c312239f39d7cbec90c`.
Gelesen: vollständige x11_endpoint.py/dual_input.py/runtime_policy.py/
a1_trace_scope.py/a1_nosmooth_intervention.py/transaction.py/a1_controls_diagnostic.py/
a1_passive_xrecord.py; vollständiger action_step und Controller-Input-/Cleanupfluss,
CPlevels/baseline_equal/ACK/geometry sowie tatsächliches archiviertes Controls0.
Nach Rootreview zusätzlich RD.run_calibration vollständig erneut gelesen:
erst Action-ACK, dann bestehendes Forward, dann tatsächliche Bodyyawgeometrie.
Ein früherer Plangentwurf verlangte Geometrie zu früh; dieser bekannte Mangel
wird vor Implementierung korrigiert, nicht durch einen Nativeversuch wiederholt.

Konkrete normale Buttons: TurnLeft/Right und LookUp/Down setzen bereits
ctl_bTurnLeft/Right/Up/Down auf1/0. Pfeile sind Bewegung/Strafing und ungeeignet.
Feste neue Key1-Zuordnung **J/L/I/K** für links/rechts/oben/unten; Key2 bleibtNone.
Alle vier sind in sämtlichen Key1-/Key2-Zeilen des exakt gepinnten Controls0
unbenutzt. LookUp/Down bisher Mouse4/5, TurnLeft/Right bisherNone. Die tatsächliche
RetailEntitiesMP enthält die vier user-INDEX-Deklarationen; dies allein ist noch
kein nativer Button→Winkelbeleg.

Profiltransaktion: BaselineSHA5d525c… wie Parent, zuerst unverändertes
NIP.install→NosmoothSHA76a947…; dann neuer Installer prüft diesen exakten
Zwischenstand und ersetzt ausschließlich vier Key1-Zeilen in den eindeutigen
betreffenden Buttonblöcken. Kommandos, Key2, Axis-/Sensitivity-/Globalangaben und
Zeilenenden bleiben erhalten. NeuemPreparedSHA folgt Builderpin. Nach Start
vorhandener passiver Controlsreader: tatsächlich local0/profile0/sourcePointer,
global/per-axis effectiveSmooth0, gekoppelte Entities/Originalmodule. Keine neue
Retail-Buttonlisten-ABI annehmen. Echtes Key→Winkelverhalten ist Teil des Tests.

J/L/I/K sind statisch profilkonfliktfrei; zusätzliche fest verdrahtete Spiel-
Shortcuts sind dadurch nicht vollständig bewiesen. Laufzeit verlangt Gameplay-
Fokus, kein Menu/Chat-/Pauseeffekt, vier unterschiedliche echte positive Keycodes
ohne Alias zu den vorhandenen W/A/S/D/1/2, initial und nach jedem Impuls neutrales
XQueryKeymap. Jeder Kontext-/Nebenwirkungskonflikt bleibt FAIL.

**Erste Qualifikationsgrenze:** keine Frida-/RECORD-Armoperation, keine neuen
Hooks. VierCoredateien werden unverändert kopiert, aber hier nicht gestartet.
Echte native XTest-Callreturns, natürliche Controllerrequest-Counter und
XQueryKeymap belegen Down/Up/Neutral; native server-/clientseitige Winkel belegen
die Spielwirkung. Kein zusätzlicher Wirebeleg oder reparierter Cursorcache wird
behauptet. Ein neuer passiver Keyboardjournal-Observer kann vorhandene
XtstProxy/prepare_xtest_transport und release-safe reserve_attempt/record_emission-
Körper wiederverwenden, ohne Recorder-/Frida-Worker zu starten. Metadataquery2.2
und Sync bleiben vor den ersten Inputs, Guardcounterdifferenz≤4 unverändert.

## Review Focus

1. Profilalias/duplizierter Button/Keykonflikt: vor Installation/Input FAIL.
2. Echter Downcall mit nachfolgendem Counter-/Journal-/Fokusfehler: genau ein
   erforderlicher Upversuch weiterhin ausführbar; stickyFAIL, kein nächsterDown.
3. Veralteter/fremder/anderesLeben-Paarread oder uncommanded axis/translation:
   sofortFAIL, keine günstige ACKauswahl.
4. Grobe oder nachlaufende Winkelschritte/fehlende Neutralität: FAIL unter
   unveränderten Fristen/EPS; keine Dauer-/Rate-/Rundungstoleranz anpassen.
5. Teilstart und Fehlercleanup: eigene normale Closes+Quieszenz vor vollständigem
   Dateirestore; fehlende Rollen/Restoreabsenzen nicht alsErfolg erfinden.

### Task1: Exakte Controlsvariante und normale Key-Emission

**Files:** Create `tools/a1_keyboard_input.py`, `tools/test_a1_keyboard_input.py`.
Keine bestehenden Transport-/Core-/InputScope-Globals verändern.

**Interfaces:** `prepare_controls(raw:bytes)->bytes`; `install(transaction,evidence)->dict`;
`KeyboardTransport`/`KeyboardEndpoint` als explizite engere Ableitungen;
`KeyboardJournal` für vorhandenen XtstProxy; feste `KEYS` und `ORDER`.

- [ ] RED: exakter4Key1-Diff bei bestehendemNosmoothhash; Doppelblock, geänderter
  Press/Release, J/L/I/K-Kollision, Symlink/Metadaten-/unsealed-Fehler verweigern.
- [ ] RED: normale4Keycodes unterscheiden sich/aliasfrei; echteFake-C Down/Up-
  Argumente einmalig; XSync und Keymapreadback; Taste nachUp nochgedrückt→FAIL.
  Downausgeführt→Metadatenreject→finallyUp muss genaueinmal nativ erfolgen.
- [ ] Kleinste Implementation: keine neue XOpenDisplayverbindung, Parenthandle;
  nur vier Lookkeys plus das bestehende Forward/W emittierbar, letzteres nur an
  den zwei fest vorgesehenen Scopepositionen; `.look`/Fire/sonstigeBewegung verweigern.
  Bestehendes event(False) ist unabhängig von Pressdeadline/stickyObserverfehler;
  Focusverlust keinRefocus imCleanup, Displaywechsel verhindertRetarget.
- [ ] GREEN: nur `python3 -B -m unittest test_a1_keyboard_input -v`; realeRED/GREEN-
  Logs0600/O_EXCL und Hashes sichern, Quellcommit.

### Task2: Reiner Sechsaktions-/Winkel-/Geometriequalifikator

**Files:** Create `tools/a1_keyboard_geometry.py`, `tools/test_a1_keyboard_geometry.py`.

**Interfaces:** `KeyboardScope.admit(role,control,seconds)` nur vanilla und feste
Reihenfolge `(yaw_left,forward,yaw_right,forward,pitch_up,pitch_down)` je0,1;
`run(read_frame,step,clock,sleep,receipt,*,started)` verwendet vorhandene
CP.geometry/levels/baseline_equal/check_window ohne deren Quelländerung.

- [ ] RED: exakt6Aktionen/12DownUpcalls; Fire/Mouse/Folge7 und Forward an jeder
  anderen Position verboten.
  Zweite Richtung erst nach vorherigem normalemRelease/Neutral/ACK. Fehler
  verhindert weitereImpulse, Rohreads undVersuche bleiben erhalten.
- [ ] RED: frische echte server+clientFrames mit denselben PID/Start/Slots/
  World/Entity/Life; richtigeVorzeichen links/up positiv, rechts/down negativ
  anhand tatsächlicher Winkelkonvention validieren; andereAchse und Translation
  bleiben während Look-/PitchACK EPSgleich. Beabsichtigte Forwardtranslation
  bekommt ausschließlich die nachfolgend genannten vorhandenen RD-Gates.
  Fehlende/alte/abweichendeACKlevels oder fehlenderAdvance→FAIL.
- [ ] Kleinste ACKimplementation aus vorhandenemCP-Prinzip: request_finished+2s,
  ≤42Beobachtungen, vorhandene0,1Gamezeit-Stabilität auf beiden Peers, alle drei
  nativen kumulativen Achsenlevels stimmenEPSgleich; expliziter nichtnulliger
  richtiger Winkelzuwachs. Pitch verlangt wieCP tatsächliche server/client-
  Viewpointgeometrie; Yaw zunächst nur den frischen kumulativen Action-ACK.
  Keine Pixelgainrange oder Grad-pro-Pixel-Vergleiche auf Keys umdeuten.
- [ ] Yaw danach exakt nach geprüftemRD: vorForward erneuter echterRead mit
  allen3Levels=bestätigtemACK; finalerPrepressguard hält Levels/Bodyyaw und beide
  relative_view_yaw_deg gegenüber der ACKbaseline EPSgleich. Ein0,1sForward,
  echterRelease, dann RD.settled-Regeln unverändert: ≤2s/42Reads,50msPoll;
  neuerPair.monotonic_started≥Release; Servertranslation-Abstand zumNullvektor≤0,2,
  echterSupportpointer, relativeViewYaw beiderPeers EPS0, alleLevels bleiben beim
  erwartetenACK, Signatur ausServerBodyyaw+3Levels stabil≥0,1Gamezeit aufbeiden.
  Rawendpoint vorVergleich persistieren. GleicheLife/World; tatsächliches
  wrap(BodyyawNachher−BodyyawVorLook) muss dem bestätigten Actiondelta EPSgleich
  sein. Keine zusätzliche Positions-/Geschwindigkeits-/Distanzmarge erfinden.
  Normale Forwardbewegung ist zulässig; nachSettling gilt die echte neue
  Position alsBaseline, CP.geometry/server-clientÜbereinstimmung weiterhin
  unverändert. Keine synthetische Reposition oder erhoffte Key-Sondersemantik.
- [ ] Nach jedemAchsenpaar vorhandene0,75°Rückkehrgrenze, unveränderteGeometrie-
  Gültigkeit und server/clientÜbereinstimmung; beobachtete Schritte/Readgaps und
  Restfehler ausgeben. Keine behauptete minimaleSchrittweite aus lückenhaften
  Samples. Grobraster darf als FAIL enden. NochkeineTarget-Aimschleife.
- [ ] GREEN: gezielte pure ACK-/Life-/LateStep-/CoarseRaster-/Scopefälle;
  protokollieren und eigenen Quellcommit erstellen.

### Task3: Deaktivierte Controllerableitung, Restore und Paketpins

**Files:** Create `tools/prepare_a1_keyboard_qualification.py`,
`tools/test_prepare_a1_keyboard_qualification.py`, eigener Abschlussbericht.
Nur neue private Controllerkopie, kein alterParent überschreiben.

**Interfaces:** `prepare(destination)->dict` prüft alle tatsächlichen Parentpins;
erstellt GateFalse+ManifestFalse, eigene Service-/Evidenzpräfixe, differenzierten
Controllerdiff und genaue Source-/Runtime-/Original-/Corepins.

- [ ] RED: Paket bleibt deaktiviert; alle Original-/Corebytes/Hostgrenzen und
  vollständige Launch-/Close-/Read-/Restorekörper erhalten. action_step unverändert
  als vorhandener0,35s/finallyReleasepfad; Keyneutrals zusätzlich im neuenEndpoint.
- [ ] Controllerkopie ersetzt nur Endpointkonstruktion/Profileinstall und die
  Vorbereitung: eigenerSechsaktionsscope+Journal+Qualifier statt collector/passive-
  Arm/CP.run_preparation. Kein alter method.execute, Frida, RECORD oder MouseGain-
  Code wird ausgeführt. BestehendeCleanupzweige mitNone bleiben nachweisbar leer.
  CP85s/Runner90s und gebundeneReader bleiben erhalten, Programm endet nach vier
  Look- und zwei bereits bestehenden Forwardimpulsen vorAim/Fire. Vollständiger
  begrenzter Input/Attemptjournal auch beiFAIL.
- [ ] RED: CPU-/Timing-/Fokus-/Downpartial-/Journal-/ACKfehler lassen Keyup und
  normale eigeneRolecloses zu; erst nachQuieszenz Restore aller gesicherten
  Dateien+Modi/UID/GID/Absenzen, unabhängigeSource-/Config-/Namenpins. KeineForce-
  Spielrollen; keineSnapshot-/Preflightumgehung.
- [ ] GREEN: nur neuezielgerichteteTests plus konkret relevante vorhandene
  Actionstep-/Release-/Transactionregressionen; kein breitesDiscovery. Builder
  ausführen ausschließlich offline, tatsächlichePins und disabledHandoff sichern.
- [ ] Bericht/saubereCommits anRoot: konkreteCodeänderungen, Logs/Hashes,
  nochfehlendeNativequalifikation und genauein möglicherRootfall. Rootreview,
  exklusiveLocks, Backup undfrischerOriginal-/Labpreflight vorRuntime.

## Akzeptanz und nächster Schritt

Nur nach allenvier Look- und beiden fest gebundenen Forwardimpulsen, vollständigen12DownUp-
Quittungen/Keymapneutral, nativenGeometrie-ACKs und normalemCleanup darf der neue
Fall `PASS_LIMITED_ORIGINAL_KEYBOARD_GEOMETRY_ONLY` melden. Kein mausbezogener
Gain-/input_once-/Aim-/Schadens-/Respawnschutz-/A1-PASS. EinFAIL beendet genau
diesenFall, bewahrt dieDaten und führt nichtautomatisch zumRetry.

Dieser Plan wurde nur lesend vorbereitet; keine Tests oder Implementierung.
Root prüft den konkreten Scope vorCode. Keine erneuteNutzerfreigaberunde für
bereits beauftragteRoutineentwicklung ableiten.
