# Cecil-Flottenrollout und Abschluss A → B

> **For agentic workers:** Use superpowers:executing-plans. Hauptagent integriert und verändert Runtime; maximal zwei getrennte Analyseworker.

**Goal:** Zuerst den belegten Cecil-Stand auf sechs Instanzen aktivieren, danach A belegen, B auf Dev abnehmen und gestaffelt veröffentlichen.
**Architecture:** Bestehende Retail-1.07-Dedicated-Rollen erhalten; Bot-DLL plus nachgewiesenes Kampf-/Navprofil in separaten Botclients. Individuelle B-Sessions erst nach A-Abschluss.
**Tech Stack:** C++, MSVC/Wine, Python, systemd, GameSpy, Retail 1.07.
**Spec:** Nutzerauftrag 14.11.2026; privates Original `/srv/tse-milestone-a-evidence-20261111/request.md`; bestehende Pläne vom 11./13.11.

## Globale Grenzen und Abnahme

Keine Umwertung alter FAILs. Keine RDC-Ausführung ohne belegte Wiederfreigabe. Regulärer lokaler Terminalzugriff ist vorhanden (Host/UID geprüft). Mindestens 8 GiB Disk; B mindestens 25 % CPU-Reserve/1,5 GiB verfügbarer RAM. Namenpool458, GUIDs, Maps, Spielregeln und englische Hinweise erhalten. Dedicated-DLL niemals durch Bot-DLL ersetzen. Keine menschlichen Teilnehmer verdrängen. Alle Liveänderungen unter bestehenden Flotten-/Runtime-Locks, mit frischem verifiziertem Restorestand.

## Review Focus

- Höhere Buildnummer ohne Herkunft/Testbeleg: nicht auswählen.
- Neue DLL mit deaktiviertem Cecil-/Kampfprofil: tatsächliche Startwerte und Logs prüfen.
- Verwaister/ausgetauschter Prozess: PID, Starttick, Cgroup, CWD und geladenes Modul erneut binden.
- Alte Fehler mit neuen Ereignissen vermischt: Logoffsets und Prozessgenerationen getrennt halten.
- Sessionwechsel entfernt Gruppe oder verschiebt GUID: B-Einzelzyklen und unbeteiligte Spieler explizit prüfen.

## Task 1: Bestand und initialer Rollout [INITIALER ROLLOUT BELEGT; REGELKORREKTUR OFFEN]

Dateien: bestehender `restart-fleet-20261111.py`, `cecil_fleet_install.py` als geprüfte Hilfen; neue private Runtimequittungen; bereinigter Bericht unter `docs/reports/`.

- [x] Host und Git-Worktrees inventarisiert; Remote frisch gefetcht, Ausgangspunkt b797960.
- [x] Eigener Branch `codex/20261114-cecil-rollout-a-b`, fremde Worktrees erhalten.
- [x] Frische sechs Queries: je8 eigene Bots, keine zusätzlichen unbekannten Teilnehmer; Public7fc94a39, Dev ec820d04; Dedicated separat.
- [x] DLL/Manifest/Quellbaum und tatsächlich getestete Kampfkonfiguration/Navpayload gemeinsam nachhashen.
- [x] Dateimetadaten, DLLs, Profile/GUIDs, Konfiguration, Startweg, Nav und Prozess-/Modulidentität sichern und Rücklesen prüfen.
- [x] Dev25650, Red25600, Yodeller25610, Skulls25620, Trouble25630, Hole25640 nacheinander: normale eigene Botcloses, Payload installieren, bestehende Dienste starten.
- [x] Je Instanz geladene Module,8Bots, Map, Bewegung, Kampf, Tod/Respawn, Cecil und Fehlerdifferenzen im kurzen Fenster belegen. Bei schwerer Regression zurückrollen und Ursache beheben.
- [x] Gemeinsamen initialen Flottennachweis und aktualisierte Runtimeidentitäten schreiben, veröffentlichen und Remote-SHA prüfen.
- [ ] Vorgefundene Serious3→Hard2-Abweichung abschließen: Dev/RedPASS; YodellerVersorgungFAIL mit verifiziertem Restore; übrige drei nochoffen. Erst nach Ursachen-/Kandidatenprüfung fortsetzen.

## Task 2: A-Abschluss [OFFEN]

Dateien/Interfaces: bestehende A1-Observer/Originalinputcontroller; `poc/release/gamemp/`; Cecil-Adapter und bestehende A3/A4-Analyzer. Vor Codeänderung konkreten Fehler aus Belegen lokalisieren, Regression RED→GREEN, qualifizierten neuen Build separat behandeln.

- [ ] A1: normale Erstzustandstreffer/tödlicher Schaden Bot+Vanilla, Input/ACK-Ursache, Neustart und Mapwechsel.
- [x] A2 historisch abgeschlossen; Erhaltung beim neuen Rollout separat nachweisen.
- [ ] A3: MITTEL/STARK/DEMON, STARK>MITTEL, Waffenbeschaffung/Bewegung/Kampf anhand tatsächlicher Schaden-/Killbelege.
- [ ] A4: Build01823/24-Versorgungslücke kausal beheben; Red priorisieren, Neun-Karten-Matrix/Gefahren/Übergänge/Reset vervollständigen.
- [ ] A5: relevante1/4/8-Bot-Gates3600/3600/7200s, Ressourcen, keine neue Sync-/Crashregression; geprüfte Verbesserung Dev→Public.

## Task 3: B auf Dev [GESPERRT BIS A]

Vor Umsetzung eigenes konkretes Design anhand Originalauftrag und vorhandener Interfaces festhalten; keine verfrühte B-Implementierung.

- [ ] B1 sechs Originalzustände, persistente IDs, exklusiver Controller, idempotenter individueller Join/Leave/Rejoin; Ersatz zuerst, Mindestziel8, Menschen vor Zusatzbots.
- [ ] Aufenthalt20–90min, Pause3–20min, Zielwechsel10–30min, ein Wechsel/Server, mindestens30s Abstand;8/11/13 nur innerhalb Budget.
- [ ] Drei echte unterschiedliche Botzyklen, voller Server, Joinablehnung, Crash, Controllerneustart; unbeteiligte Bots laufen weiter.
- [ ] B2 lokaler DE/EN-Pool,5–12%, Botcooldown3–8min, höchstens3/60s, Abstand≥10s, Verzögerung1–4s, keine Textwiederholung30min, getrennte Flags.
- [ ] Ingame-Zuordnung/Encoding/Chatlimit auf Originalclient, gleichzeitige Sessions, Ressourcen und Restore prüfen.

## Task 4: B-Flotte, Sicherung und Veröffentlichung [OFFEN]

- [ ] Dev-abgenommenes B zuerst auf einem Public prüfen, weitere einzeln aktualisieren.
- [ ] Gemeinsame Tabelle: Version/Module, Mindestziel/Soll/Ist/eigene/fremde, Sessions/Chat, Fehler/Ressourcen.
- [x] Private Delta022/023 und geschlossene Nachträge024–028 im bestehenden Drive-Projekt sichern, vollständig rücklesen/hashen; Quiet-V2 und spätere Belege benötigen Delta029.
- [ ] Quellen/Configs/Navmetadaten/Tests/bereinigte Berichte committen/pushen; Remote tatsächlich lesen; vorgesehene Integration und ausführbaren Restore dokumentieren.

## Ausführungsledger

15:43 UTC: Eigener Syncversuch150433 geschlossen FAIL wegen verschwindendemFD; drei Paare je456gleich/0diff, kein voller600s-/WANnachweis. Vier normaleCloses/Root640+4RestorePASS. Dev siebenneueBAD/0Disconnect bis15:17; kontrollierter eigenerBot-onlyRollback15:22 aufCecil048, Dedicated/Identitäten unverändert;90,340s/43Queries8eigene+1NutzerOriginal/alle8Bewegung/0neueFehler. Red/YodelGen2,Skulls/Trouble/Hole018,Dev048. FD-Fix nur offline; A/Boffen. Delta022–037externPASS;038offen. Handoffhistorie bytegleich archiviert, aktuellerHandoff gekürzt.

14:54 UTC: A1-Eingabezeiten imneuenLaufalle3PASS, Gesamtergebnis51e8e0e5FAILwegenunterschiedlichemXTest→ACK-Gain: rechtsderselbeCursorversatz2×gelesen, links1×, Ereignisursacheoffen. Root664+8+3RestorePASS. Eigener018/Yodeller-Capture145119FAILbeimJSON-Tuple/Listvergleichvortcpdump/Release, Root640+4RestorePASS, kein600s-/Syncnachweis. EngerKorrekturplanf78a1fd; zweiAgentennurofflineJSON-RegressionundXRecordMethodenverfügbarkeit. Live14:54sechs×8/0Zusätzliche, Red/YodellerGen2/andere4Build018, seit13:51keineneuenServerfehler.036externfullPASS, neueBelege037offen.

14:42 UTC: A1-Releasefix6f6e6b3 integriert; Root20 neue/27 historische Offlinefälle PASS. Rootfreeze26655170 und A3-Rootfreeze272d04e3 separat PASS_SCOPE; A3 Root59 gezielte Offlinefälle PASS. Noch kein neuer Native-Lauf, A1 f66266f9 bleibtFAIL. Live14:38 sechs×8, Red/YodellerGen2, andere4Build018; sechs Serverpräfixe seit13:51 null neue Fehler. Delta035 externes Rücklesen läuft; A4-PCAP-Fork noch offline. Vor Native Archive/Reader beenden, frischer Preflight.

13:56UTC: NeuepräfixverifizierteFlottenprüfung zeigtYodeller27BAD/2Disconnectsfür2externePeers,einerauchbeimRedincident. Rootbot-onlyRollback13:53:59aufGen2mitverifiziertem018Restorepayload/IDs/Dedunverändert.90s43Queries0neueFehler+54positiveFrags;20sdirekteNativeprobealle8sameLifeBewegung. Andere5Instanzendelta0. JetztRed+YodellerGen2/andere4Build018,je8. Ursacheweiteroffen; Syncdiagnosepriorisiert, weiterePromotionzurückgestellt. A1historischerMappinghelperbytegleichübernommen77d54f0,Root26Python+31VMPASS,70/58/14PinsPASS; neuerRootfreeze/Nativeoffen. Resetagentstandpreserviert,Source/Testsnochunvollständig. NeueRaws034offen.

13:24 UTC: Geordnetes V3-Hard2-Redfenster geschlossen mit begrenztem Beobachtungs-PASS nach600,129s. Alle8Slots echte brauchbare Inventargewinne und gebundene Feuerflags/Quellzähler,179Serverkillereignisse, keine neuen Schlusslogfehler. Root640Dateien/Metadaten+4Schlusslogs/Prozess-/DisplayendeRestorePASS. Resultfb668f2a42e51b809ba528aa6d6a3682ab699521e99ace054cdea6e3ccb1db1e. Kein vollständiges A4, kein020live; unabhängige Review läuft. A1-Mappingfehlerquittung nur mit unveränderter harter Gleichheitsprüfung im separatenWorktree; Offlinearbeit wieder erlaubt. Delta033 für neueForks/A1-/V3-Belege offen.

2026-11-14: Historischer Deploymentblocker durch regulären bereitgestellten Terminalzugang ersetzt. Kein Umgehen eines Diagnose-/Kontingentlimits. Alte Runtime-/A-Abnahmen unverändert offen. Candidate-Audit arbeitet ausschließlich lesend; Root allein Runtimewriter. Die servereigenen Red-Station-Locks sind laufender Serverbesitz und werden nicht entfernt.

2026-11-14 Fortsetzung: Initialer6/6-DLL-Rollout91sjeInstanz bestanden; Hardkorrektur bleibt2/6wegenneuem60sYodeller-Versorgungs-FAIL. Build019ausa1e77b9gebaut(671df77a…,431104B), nach2833SDK107ASan-Prüfungen; nochkeineNativefreigabe. Original-A1-NosmoothdiagnoseFAIL vorFire, RestoreunabhängigPASS; genau ein019-A4-Fenster läuft nach frischem Preflight. Delta024upload/download/DateirestorePASS;019A4Retarget55OfflineprüfungenPASS; keine024Slotphase- oderHardfreigabevorErgebnis.

09:00UTC: erster019A4-Lauf RessourcenFAIL75,5102%, unabhängigRestore643+5 bestätigt. Getrenntes zweites Einzelfenster unter belegbar geänderter Lastbedingung (eigene breite Suite beendet), alle Kriterien unverändert, Worker nur statisch. Aktive Owner/Ended-Dateien tragen a4-build019-quiet. A1-Inputtrace und direkte Tiervergleiche werden deaktiviert vorbereitet; B bleibt gesperrt. Build019-Quellbaumce7d715d öffentlich im separaten Sourcebranch1344a948 tatsächlich zurückgeprüft.

09:03UTC: Quiet019A4 erneutFAIL23/24, andererSlotPhase2botB:0 ohnebeobachtetenUsefulPickup; initial linkszensierterBesitz istkeinbeobachteterÜbergang. VollständigerCleanup/RootrestorePASS, keine019Liveübernahme. NeuekonkreteUrsachenanalyse; unveränderteGates.

09:25UTC: Terminaleligibilityfix f9f5531 unabhängig ohneKritisch/Wichtigreviewt, integriert e5f7a65502fbea683014ef8fcc95ecdd2a927b6a. RootSDK107ASan2920/0; neuerBuild020094ec8ed…/431104B, Manifest3099a0be…. DeaktivierterA4Retarget65Runtime/75Quellpins,47bestehendeTestsPASS; ersterfalscherCWD-Aufruf separatFAILerhalten. NativeGateundPromotionbleibenoffen.

09:37UTC: 020A4geschlossenFAIL23/24nurState-Feuerbit;11nativeServerFIRE-Proben/Sourcecounter desselbenSlots belegenSnapshotlücke, alle24UsefulPickup. NeuerterminalerWatchdog nativnichtausgeübt. RootRestore/PreflightPASS, keine020Liveübernahme. NativeFeuerObserver-V2 undA1NoFireCollector/Controller werdengetrenntdeaktiviertgeprüft; nächsteRuntimefrischbinden.

09:53UTC: ArchivanalyseV2 unabhängig13TestsPASS,24/24strengeSameLife-FIRE-/Counterbelege und echteUsefulPickup-Übergänge; alter020Status bleibtFAIL. ProspektiverController separat inArbeit. A1Collector braucht vorAttach äußeren FridaWorker-Supervisor und Method-/Kontrollprüfung. Delta026Dateirestore und vollständigerDrive-RückdownloadPASS. AktuelleFlotte09:51:48weiter6×8Build018/Spawn0, Botlogs0neueFehler; Hardnur2/6. KeineNative-/Build-/Liveausführung aktiv.

10:05UTC: Einneuer prospektiver020A4-V2-Lauf aktiv, Rootowner a4-fire020-v2; unverändert24Slotphasen/480s/Serious3 und physischeGates. Root69Checks/67Runtime-/75BuildpinsPASS, frischerPreflightPASS, beideWorker ausschließlichstatisch. ErstnachvollständigemErgebnis/Cleanup/unabhängigemRestore weiter. Hard2-Formaladapter nurdeaktiviertmit31Offlinechecks vorbereitet, keinLanglauf. FridaPython eigenerELF64Methodsmoke99CallbacksPASS, keineRetail-/A1-Freigabe. Remote33e9671/Tree44320f13 gleichlokal713bce9tatsächlichgefetcht.

10:10UTC: V2frühFAILCPU80,095923%>75%; keinevollständigePhase/V2Freigabe. RootpublikationmitParallelreadernüberlappte; keinealleinigePIDkausalitätgemessen. Restore643+5+4LogsunabhängigPASS, frischerPreflightfrei/LocksPASS. KeineNativeaktiv; neueA1Control-/Workerstartfälle jetztgezieltofflinetestbar. VorweitererNativeauchRootpublikation/Sicherungenbeenden; unveränderteGates, keineautomatischeWiederholung.

10:20UTC: A1Controller+Controlmodusfinalunabhängigreviewt, Root63OfflinechecksPASS; Rootfreeze2e3bf79b…/Library8b350891…ebenfallsunabhängig68/13/46PinsPASS. Delta027lokalerDateirestore+vollständigerDrive-RückdownloadPASS. NochkeineA1Native, geplanteReihenfolgeuninstControl→vollständigerRestore→passiveTrace; beideNoFire, keinA1SchadensPASS. VorStartPublikation/Sicherungenbeenden, Workerreinstatic.

10:27UTC: BeideA1FenstergeschlossenFAIL. UninstPitchgains−.5/−.25nach6Inputs; Instr21GetInput/0Action/0FaultsvorGameplay, OriginalbyteRestore/WorkerendePASS. Rootje664+9+3Logs/MetadatenPASS, frischerPreflightfrei. KonkreteAction-/Fokusursachejetztofflineprüfen, keineToleranzlockerung. RootHard2-Formaladapter unabhängigPASS_SCOPE, weiterdeaktiviert. A3konkreterController/AnalyzermitgezieltenOfflinefälleninArbeit. NeueRawsDelta028offen.

10:56 UTC: Quiet-V2 geschlossen mit 24/24 begrenzten Slotphasen und unabhängigem Restore-PASS; keine vollständige A4-/020-Freigabe. Delta028 extern vollständig geprüft. Neuer Red-SYNC-Befund hat Vorrang: im stabilen privaten Serverpräfix 10:54:01 UTC 15 BAD/ein Disconnect für eine öffentliche IPv4, acht eigene Botlogs/Slots unauffällig, ein zusätzlicher Teilnehmer. Zuordnung läuft nur lesend, keine fremde Instrumentierung/Entfernung. Neue Nativefenster zurückgestellt. A1-Timerguards und A3-Hardvergleich deaktiviert zur unabhängigen Prüfung; Root-Kartenadapter geplant.

11:05 UTC: Zuordnung zusätzlicher externer Peer unabhängig bestätigt. Betrieblicher Bot-only-Rückroll Red abgeschlossen: aktuelle018-Sicherung rekonstruiert/hashgeprüft, reguläre eigene Closes, vorherige7fc94a39-Module geladen, acht Bots, Identitätsdateien und Dedicated unverändert.116,91s kurze Nachprüfung mit Zusatzteilnehmer und0neuenBAD/Disconnects, Ursache weiteroffen. Fünf weitere Instanzen018, keine weitere Promotion bis Syncklärung. A1-Guards efcb7eb integriert/39OfflinefällePASS; separater Freeze9fd173db zur Prüfung. A3 blockiert durch zwei wichtige Frida-Lifecycle-Befunde, Fix deaktiviert in Arbeit; HardMapadapter ohneFrida getrennt in Arbeit. Kein B-Beginn.

11:24 UTC: A1-Guarddiagnose110842 FAIL vor Input an neuer EDI-Gleichheitsannahme; Entry/Returnphase noch ununterscheidbar. Root664Dateien/8Absenzen/3Logs+MetadatenrestorePASS, Worker/Rollen beendet. Neuer enger beobachtender Guard-/Cleanupquittungsfix in Arbeit. Erster Hardmap111731 FAIL vor Botjoin wegen erster Hardquery, rohe Antwort nicht erhalten. Root640-DateirestorePASS, nur gestarteter Server regulär zu; Schlusslogarchiv fehlte wegen geerbter Vierrollenpflicht. Enger Startuptransport-/Rohquery-/Teilstartarchivfix mit84 OfflinefällenPASS separat vorbereitet, finale Vierrollen-/Gameplay-/Hardgates unverändert. Keine native Kartenabnahme, keine zusätzliche Livepromotion; Public Red nach Rückroll bis11:22 keine neuen Syncereignisse. Delta030 für neue geschlossene Belege offen.

11:58 UTC: A1 115139 geschlossen FAIL20Input/0Action, expliziterHostOriginalvergleich+Workerende+Root664/8/3RestorePASS. Konkreter Midpoint-Objektlistenervertrag falsch, enge Funktionsprobefix-/eigeneWin32Methodenprüfung vor weiterer FridaNative; Plan2026-11-14-instruction-probe-contract. A3boundedQuellen integriertc98e164, Nativeoffen. CanonicalObserverdeaktiviert63Offlinefällebereit, historischerHard600FAILunverändert. Delta030externfullPASS, neuer031offen. KeineNativeaktiv.

12:21UTC: CanonicalHard120936geschlossenFAILnach600,098s wegenWithinGroup-Gesamtrowkonflikt; alle4normalzu/Root640+4RestorePASS,CPUmax59,184%,Gameplaygap1,177s. NeuegezielteKonfliktdiagnose stattRetry/Gateloosening. FünfMidpointfix gezieltRED/GREENagentbereit, eigeneWin32Methodenquellen inArbeit. Remote6e1a20e/treecbbeddf1gleich1987e12;031offen,A/Boffen.

13:02UTC: EigeneWin32Baseline/FunktionsprobevollständigPASS_METHOD_ONLY, historischeObjektformnativekorrupt+CleanupTimeoutFAILerhalten. Prefixquieszententfernt/10GBfrei;032externfullPASS. V3Root56f4c319unabhängig64/52PinsPASS_SCOPE,85RootchecksPASS. NeueA1/A3Forks2483e3c/40OfflinechecksPASS;A1Root7521e53cFreereviewoffen,genaueinNoFireTracevorV3600geplant. KeineNativeaktiv,A/Boffen.
