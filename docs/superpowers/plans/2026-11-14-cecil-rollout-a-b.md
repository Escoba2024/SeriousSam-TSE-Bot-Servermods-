# SSAM.AI – ausführbarer Gesamtplan A → B

Stand15.11.2026,04:28UTC. Umsetzung läuft; **A offen, B nicht begonnen**.
Maßgeblich sind der vollständige Nutzerauftrag, ursprüngliche
[Milestonespezifikation](2026-11-11-milestones-a-b.md),
[Toolchainrichtlinie](../../decisions/2026-10-17-tse-ai-tools-mcp-policy.md)
und [aktueller Handoff](../../coordination/HANDOFF.md).
Die vollständige frühere Planchronologie bleibt im Gitstandd7bf1ae und Backups.

Die spätere Nutzerentscheidung hat den ersten Rolloutauftrag gesteuert:
**aktuellen Mischstand behalten; isoliert weiterentwickeln; erneut ausrollen
bei nachgewiesener Verbesserung**. Keine erneute Freigaberunde für autorisierte
normale Arbeit. Keine Produktionspromotion nur aufgrund von Buildnummer/Buildpass.

## Aktueller Zustand und Priorität

| Arbeit | Status | Nachweis bzw. nächste konkrete Aktion |
|---|---|---|
|Tatsächliche Flotte|geprüft03:56|sechs×8eigeneBots/18Targets051gleich,Dev048/RedGen2/4Public018;LittleTrouble+1ungeklärt|
|Namen/Identitäten erhalten|Bestand geprüft|458Pool/48Anzeigenamen/Profile051gleich, Instanz+ID verwenden|
|Dev-Sync|**FAIL/Ursache offen**|70neueBAD/3Kick seit23:54, eigeneBotclients0; unverändert048+PowerupDedicated|
|026passiveDiagnose|Build/Portable bestanden|15MSVC+Link/77Closure,3532normal+ASan, keinRuntime-/Skullsfixclaim|
|026Skulls600diag1|geschlossen, A4 weiter offen|Root640Dateien/4LogsRestore; vierstufigerAudit bytegleich, bewaffneter16,546sStillstand; keinePromotion|
|A1Maus/Keyboard|historischeFAILs|MousevariableAntwort,Keyboard7,5°Rückkehrfehler; Rootclosedaudit vollständig|
|A1Pitchfeedback|Native034224 FAIL vor ersterEmission|nur+12Detour/1pxFeedback/0,75°diagnostischeRückkehr,keinSchuss/A1pass|
|A3Tiernachweis|offen|020STARK13:3,Swap5:6; keinbelegtesSTARK>MITTELüberbeide|
|A4Karten|teilweiseBeobachtung|024Red/Skulls/Trouble600geschlossen, Skulls242,49sNoUseful; weitereMaps/Transitions/Resetoffen|
|A5Formalgates|nichtbegonnen|nachfunktionalgeeignetemKandidaten1/4/8Bots60/60/120min|
|BImplementierung/Dev/Flotte|nichtbegonnen|erstnachbelegtemA-Abschluss|

## Unmittelbare Ausführung

1. **026 geschlossen und vollständig ausgewertet.** Vier Readerstufen Rootreplay bytegleich,
   Finalquittung298253fd; 188Leben/111Gewinne/515ReadFAIL, 871Decisions/19UNKNOWN.
   52,303sNoUseful und16,546s exakteStillstandsphase verhindernA4-Freigabe.
   Keine pauschaleGuardlockerung; vorKorrektur Proposal→finalAction/Safety binden.
2. **Feedbackquellen073 veröffentlicht und064 vollständig gesichert.** Root24/0portableTests,
   neuePolicy/Journal/Builder integriert, direktePitchdistanz2RED→GREEN,
   Freeze a2fa6509/Controller5b348963, Peer f8c9b366PASS_SCOPE nurRootdelta/Pins.
   106/88/14Pins;6Instrumentgates+cmFalse/vierCoregleich. VollDrive-Rücklesen und
   Dateimetadatenrekonstruktion abgeschlossen034135, dannEinzelfall ohneRetry.
3. **BegrenzterOriginal-Pitchfeedbacktest geschlossen FAIL.** +12Detour, reale±1px-Korrekturen,
   bestehende0,75°Rückkehrgrenze, max48/96 und20/85/90s, 2,35sInputreserve.
   034224 Guardabbruch vorInput: clienttargetEyeoffsetdelta0,00102027>EPS0,001.
   KeineEmission/ACK, Rootrestore664Dateien9Abwesenheiten3LogsPASS. KeinRetry.
   KeinFire/Gain-/A1Pass. DirektenOriginalopferweg getrenntqualifizieren.
4. **A1 Erstzustandsschaden** nach tatsächlicherLife-/State-/Bulletordnung weiterführen;
   Originalopferwegquellseitigbestätigt, keineproximityBeweise. Jetztgetrennt
   deaktiviertenMethodenadapterqualifizieren:18Hooks/38Bindings/Registry2behalten,
   Getterfunction/admission-idle-stop/FreshExecPorts. KeineOriginalaimvoraussetzung
   aufaltenFAILumlabeln; AI-/Populations-/Waffenadaptererstdanach.
5. **A4Combat-Recoveryfix integriert692b0d0.** Root3663/0 plus vollständiger
   Source-/Testreview, negativeMapRootfund reale4/3RED→4/0GREEN. AlteGrenzen
   bleiben; separaterfrischerCombatpin/Produktivcapture explizit. NochkeineNative-
   Verbesserung. Jetzt027Build, danach disabledSkulls600Retarget/Review/Backup,
   isoliert tatsächlich testen und vollauswerten. A1MethodAPI Root35/0integriert,
   aktuellerWorker baut inputfreiesControl+TraceMethodwindow; beide10saktiv,
   keinA1Schadenspass/18ABIclaim. DetailsundAusführung im aktuellenHandoff.
   A3/A5 erst nach funktionalgeeignetemKandidaten. B weiterhin nach A.

## Verbindliche A-Abnahme

| Teil | Erforderlicher Abschlussbeleg | Offen |
|---|---|---|
|A1|effektive0laufend/Start/Mapwechsel; normale und tödlicheTreffer im ersten gültigenOriginal-Serverzustand fürBots+Original, Neustart/Mapwechsel, ACK/Bullet/Inflictor/Lifeordnung|tatsächlicheSchadenskette+Stateordnung|
|A2|458vorhandeneNamen, stabileInstanz+BotIDs getrenntvonAnzeigenamen, Kollisionsfreiheit, FarbstileohneFlashparserregression|finalerA-Stand/Sessionintegrationspäter|
|A3|MITTEL/STARK/DEMON stärkste, gleicheTaktik/definierteAim/Reaktion/Fehler; Messerstart/Waffenbeschaffung/Menschenpriorität/Bewegung; tatsächlicherTier-/Kampfvergleich|Tierseparation/humanesNiveau/verlässlicheVersorgung|
|A4|Cecilgraph/logikweiterverwenden; Red+übrigeMaps, Waffen-/Itembedarf/Erreichbarkeit/Recovery/Höhen/Jump/Bouncer/Flug/Teleport/Gefahren/Reset; neunMapsqualifizierenoderbegründetsperren|Skulls242s/Restmaps/Spezialübergänge/Reset|
|A5|ursachengerechteFixes/Regressionen; erforderliche1/4/8-Gates60/60/120min; keineSync/Crash/Restartregression; Ressourcen/Restore/Backup/Remote; Dev→gestaffeltPublic|formaleGates/finalerA-Rollout|

KeineCecilparität/Koopportierung oder vollständigeKartenabnahme ausNavLoad allein.
DesertTempleWorldfehltgesperrt; LostTomb/Fortress/Compoundvorhandenungeprüft.
024Hole/Yodeller600deaktiviert/frozenbereit, nochkeinNativebeleg. 026überträgt
keine024Abnahmeautomatisch. JedeBuild-/Bedingungsgruppe getrenntauswerten.

## B – erst nach A

B1: echte individuelleClients/Sessions, sechsZustände
`offline/joining/active/leaving/cooldown/failed`, stabilepersistenteInstanz+BotIDs,
exklusiverController/idempotent/BackoffJitter. Aufenthalt20–90min,
Pause3–20min,Zielbesetzungalle10–30min,maxeinWechseljeServer/≥30sAbstand.
Mindestziel8mitErsatzvorLeave, Menschenvorrang/Slots ehrlichausweisen,
8/11/13nurbeigemessenemBudget. EchteJoin/Leave/Rejoin/Abfragen/Logs und
mindestensdreiZyklen plusvollerServer/Joinabweisung/Clientcrash/Controllerneustart,
andereBotslaufend. Testintervalle strengvonProduktiontrennen.

B2: eigenerlokalerDE/EN-Pool fürJoin/Kill/Tod/Anerkennung/Leave,
RUerstEncodingprüfung. Ereignis5–12%,Botcooldown3–8min,max3Nachrichten/60s,
≥10sAbstand,1–4sReaktionsdelay,keinidentischerText30min,
keineRekursion/Spam. RichtigerBot/tatsächlichimOriginalspielsichtbar,
Chatlimits/Zeichencodierungprüfen. SessionsundChatgetrenntschaltbar;
Community-MOTD/5minHinweiseEnglisch.

DevabnahmebeiderFunktionen zusammen: IDs/Namen/Logs/Abfragenkorrekt,
CPUreserve≥25%,RAM≥1,5GiB,Disk≥8GiB untergemessenerBetriebslast,
keineNeueSync-/Crash-/Restartregression, rollbackgesichert/wiederherstellbar.
PublicbleibtwährendB-EntwicklunggeprüfterA-Stand. NachAbnahme zuerstPublic1,
tatsächlichprüfen, dannübrigeeinzeln; abschließendergemeinsamerFlottenbeleg
mitMindestziel/Zielzahl/eigenenBots/MenschenungeklärtenTeilnehmern,keinpauschal48.

## Sicherung, Veröffentlichung und Abschluss

Aktuell Source074 Remote c57467c4acd2a9f7f971ee6c1649badf64f3a5b7,
Treee30e0b6b374720182f5d140ec50690fce01b0be5 exaktRoote54282c, Fetch/Diff0;
neuereMethod-/CombatcommitsnochSource075publizieren. Delta022–065 vollDrive/
Dateimetadatengeprüft,065d4bb3b7e/2842626B/724Files19854093B,
Drive1ZS2s_f6WiQtNmAL_jjyUEg88G8wG0p1J. 051istMischrollback.
NeueKompression024Skulls/022023Red vollständigDateimetadaten-testrestored,
066externeSicherung noch ausstehend, Originalarchive060/050/053bleiben.

NeueBelege/Quellen/Config/Navmetadatenbereinigtcommitten/publizieren,
Remote tatsächlichabholen/diffen, ZielbranchintegrationnachReviewregeln.
PrivateRestorearchive insbestehendeDriveprojekt, vollrücklesen/Hash/
Metadatenrekonstruktion; keinRetail/Token/Rohspieleridentity insöffentlicheGit.
KeinevollständigeNativeRestoreStartqualifikationausDateirekonstruktionableiten.
Handoff bei jedemmaterialenStandaktualisieren, konkreteJobs/Sperren/SHAs/
offeneTests/NächsteKommandos festhalten. Keine unbeaufsichtigteWeiterarbeit
behaupten. GesamtabschlussnurbeiA+B+sechsInstanzen+Stabilität+Backup/Remote/
Rollbackbelegen; bei konkretemexternemBlocker ehrlichblockiert/teilweise.
