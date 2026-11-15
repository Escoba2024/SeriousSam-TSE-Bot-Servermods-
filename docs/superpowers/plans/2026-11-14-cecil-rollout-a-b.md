# SSAM.AI – ausführbarer Gesamtplan A → B

Stand15.11.2026,03:03UTC. Umsetzung läuft; **A offen, B nicht begonnen**.
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
|Tatsächliche Flotte|geprüft02:48|sechs×8eigeneBots/18Targets051gleich,Dev048/RedGen2/4Public018;Yodeller+1ungeklärt|
|Namen/Identitäten erhalten|Bestand geprüft|458Pool/48Anzeigenamen/Profile051gleich, Instanz+ID verwenden|
|Dev-Sync|**FAIL/Ursache offen**|70neueBAD/3Kick seit23:54, eigeneBotclients0; unverändert048+PowerupDedicated|
|026passiveDiagnose|Build/Portable bestanden|15MSVC+Link/77Closure,3532normal+ASan, keinRuntime-/Skullsfixclaim|
|026Skulls600diag1|vorbereitet/rootreviewed|4inverseDateien/77unverändert,77Alt→77Neu,11Roottests; Rootfreezeb82e1bd8/Peer87415519PASS_SCOPE,Backup/Native alsNächstes|
|A1Maus/Keyboard|historischeFAILs|MousevariableAntwort,Keyboard7,5°Rückkehrfehler; Rootclosedaudit vollständig|
|A1Pitchfeedback|isolierteImplementierung|nur+12Detour/1pxFeedback/0,75°diagnostischeRückkehr,keinSchuss/A1pass|
|A3Tiernachweis|offen|020STARK13:3,Swap5:6; keinbelegtesSTARK>MITTELüberbeide|
|A4Karten|teilweiseBeobachtung|024Red/Skulls/Trouble600geschlossen, Skulls242,49sNoUseful; weitereMaps/Transitions/Resetoffen|
|A5Formalgates|nichtbegonnen|nachfunktionalgeeignetemKandidaten1/4/8Bots60/60/120min|
|BImplementierung/Dev/Flotte|nichtbegonnen|erstnachbelegtemA-Abschluss|

## Unmittelbare Ausführung

1. **026Skullsdiagnose abschließen.** DeaktiviertesPaket
   `/srv/tse-nav20-026-skulls600-diag1-disabled-20261115` cdb5b958,
   Rootkopie `/srv/tse-nav20-026-skulls600-diag1-root-frozen-20261115`
   b82e1bd8/Controller1e06b182. VollständigerRootreview+11Tests bereitsPASS.
   Unabhängiger Peer prüft nur Root-Gate-/Namespace-/Pindelta; keine eigene
   Policyprüfung als unabhängig ausgeben. Neue Quellen publish/fetch,
   Paket/Wrapper/Syncdeltas/A1Spec in063 externvollrücklesen.
2. **Genau ein026Skulls600s/diag1-Fenster.** AlleWorkerSTATICONLY und CPUjobs
   beendet; Build/Fleet/Deploymentlocks plus Fixturelock exklusiv, keine
   fremden Ressourcen. Hard2/8DEMON/Original20FPS/OriginalDedicated.
   RootEV/observe-navigation026-skulls.py startet ausschließlich den gepinnten
   Rootparent. KeinRetry/keineRolloutsequenz. CPU≤75%,RAM≥1,5GiB,Disk≥8GiB.
3. **Geschlossenen Fall tatsächlich prüfen.** Vier normaleCloses, komplette
   Inhalts-/Besitzer-/Modus-/Profile-/GUID-Restoration, gestarteteGenerationen/
   Units/Displayende, geladeneDLL/Config/Map/Nav, Schlusslogdifferenzen.
   AlleReadattempts/Leben/Zensierungen behalten. NeueReacquirezeilen an
   tatsächlicheEntity-/World-/Life-/Nativezeit binden; unaufgezeichnete oder
   throttledFelder UNKNOWN. Proposal≠Bewegung/Ankunft/Pickup.
4. **Konkrete Ursache reproduzieren und korrigieren.** ErstbelegterSDK107RED,
   kleinerFix, relevanteRegressionen/ASan, neuerseparaterRetailkandidat,
   tatsächlichnativegleicheBedingungen. Keine Guard-/Toleranzlockerung nurfürPASS.
5. **A1Pitchfeedback getrennt prüfen.** [Spec](../specs/2026-11-15-a1-closed-loop-original-input.md).
   ReineTests/disabledBuilder/Rootreview/Freeze/Backup/einOriginalfall;
   max48Aktionen96Attempts/.35sHold/2sACK/20saktiv/85sGesamt/90sRunner,
   EPS.001 und2,35sReserve vorInput. AlteCP/Gain-/KeyboardFAILsunverändert.
   Danach normale Original-Schuss-/Bullet-/FirstStatekette weiterentwickeln.
6. **Dev-Sync getrennt eingrenzen.** Vorhandene048/018/020Originalserver-
   Kontrollen600s bereits0neueSync; nichtunbegründetwiederholen. Filter-off/on-
   Kontrolle mit bestehender PowerupDedicatedfe4a77 ist noch vorzubereiten;
   identischeeigeneOriginal-/Bot-/Join-/Inputbedingungen, keineFremdspielerhooks.
   Schwellwert10/CRC unverändert, keineUrsachenbehauptungausbloßemBAD.

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

AktuellSource071Remote346a86f6/Tree4eea6687 exaktRoot75ba3bb,
neuereCommitsnochpublish/fetch. Delta022–062 vollDrive-/Dateimetadatengeprüft,
aktuell062e04fa98f/4782193B/945Files30425209B,
Drive1fzNIffBqn92hvsS8m81L8PhfRK2bAETP. 051istMischrollback;
ursprünglicheArchive/qualifizierteRetaildateien/Identitätenerhalten.
Sourcebundles benötigenBasis061067dda4 und0606f4fbbd.

NeueBelege/Quellen/Config/Navmetadatenbereinigtcommitten/publizieren,
Remote tatsächlichabholen/diffen, ZielbranchintegrationnachReviewregeln.
PrivateRestorearchive insbestehendeDriveprojekt, vollrücklesen/Hash/
Metadatenrekonstruktion; keinRetail/Token/Rohspieleridentity insöffentlicheGit.
KeinevollständigeNativeRestoreStartqualifikationausDateirekonstruktionableiten.
Handoff bei jedemmaterialenStandaktualisieren, konkreteJobs/Sperren/SHAs/
offeneTests/NächsteKommandos festhalten. Keine unbeaufsichtigteWeiterarbeit
behaupten. GesamtabschlussnurbeiA+B+sechsInstanzen+Stabilität+Backup/Remote/
Rollbackbelegen; bei konkretemexternemBlocker ehrlichblockiert/teilweise.
