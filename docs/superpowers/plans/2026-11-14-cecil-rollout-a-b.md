# SSAM.AI – ausführbarer Gesamtplan A → B

Stand 15.11.2026, 17:23 UTC. Umsetzung läuft; **A offen, B nicht begonnen**.
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

Stand 15.11.2026, 17:23 UTC. Exakte private Pfade/Hashes und frühere Fehler stehen im Handoff; ältere Planstände bleiben in Git erhalten.

| Arbeit | Status | Beleg und nächster Schritt |
|---|---|---|
| Live-Flotte | zuletzt 17:20 erneut geprüft | Dev048, Public Red Gen2, vier Public018; je acht eigene Bots, Dev ein ungeklärter zusätzlicher Teilnehmer; 18 geladene Rollen/Startkonfigurationen wie Rollback051. Bis belegter Verbesserung erhalten. |
| Namen/Identitäten | Bestand erhalten | 458 Namen; 48 kollisionsfreie sichtbare Botnamen, stabile Profile/IDs wie Rollback051. |
| Dev-Sync | frühere Ursache offen | 15:59–17:21 neue16.191OK/10BAD/1Disconnect; ältere23BAD/2Disconnect und70BAD/3Disconnect bleiben FAIL. |
| A1 Eingabekalibrierung | offen | Maus-/Tastatur-/Pitchbefunde fehlgeschlagen; keine Toleranzänderung. |
| A1 neue Messmethode | begrenzt bestanden | Kontroll-/Traceprobe geschlossen und voll ausgewertet: 414 tatsächlich beendete exkludierte Weltcasts, 207 GameTickpaare bis F, 38 Originalbereiche restauriert; Init/Colt/Schaden jeweils 0. Kein A1-Pass. |
| A1 normaler Originalrespawn | F1ControlFAILvorInput; Readerkonfiguration korrigiert/6neueRoottests/F2Rootfreeze geprüft, noch nicht nativ | Echter regulärer Tod vor Arm/MayRespawn2; danach ein normaler Fire-Release und tatsächliche Init-/erste-Tick-/Normal-/Fatal-Schadenskette. Neue Bedingung, alte Inputfree-/Coltverträge unverändert. |
| A3 Schwierigkeitsstufen | offen | STARK>MITTEL und menschliches Spielniveau noch nicht belegt; Waffenversorgung unzureichend. |
| A4 Reset031 | geschlossen, begrenzt bestanden | 24/24 aktive Slotphasen; Vollauswertung 145 Leben, weiterhin 49,4s Waffenlücke. Reset030 bleibt 22/24 FAIL. |
| A4 Hole031 | geschlossen, vollständig ausgewertet | 206 Leben/204 zusätzliche Waffen-Gewinne/172 erkannte Spieler-Killzeilen; 79,43s und 57,85s ohne brauchbare Zusatzwaffe verhindern Freigabe. |
| A4 Trouble031 | geschlossen, vollständig ausgewertet | 600,074s/292 Leben/205 Gains/259 Spielerkillmeldungen; 38,45s Versorgungslücke. Root-Restore und Auditdateihashes geprüft; kein A4-Pass. |
| A4 Build032 Trouble | geschlossen, vollständig ausgewertet | 600,053s/0BAD/0Disconnect in vier Logs, Rootrestore640Dateien PASS; 311Leben/194Gains/0neue first_weapon-Marker/44,24s NoUseful; keine Verbesserung belegt. Atomischer Erstwaffenwechsel SDK4175/0. Übrige Karten/Übergänge offen; Desert Temple gesperrt, Welt fehlt. |
| A5 formale Stabilität | nicht begonnen | Funktional geeigneter Kandidat erforderlich; 1/4/8 Bots für 60/60/120 Minuten. |
| Sicherung/Veröffentlichung | Source108 / Delta100 vollständig geprüft | Remote-Fetch/Baum/Diff0; privater Vollrücklauf und zwei vollständige Perfile-Metadatenrestores. 032Build/Freeze gesichert; neue032Rohdaten erst mit nächstem Backup101. |
| B Sessions/Chat | nicht begonnen | Erst nach nachgewiesenem Abschluss von A. |

## Unmittelbare Ausführung und Claims

1. **Trouble032 geschlossen:** Root43288 beendet0/abgeholt; unabhängiger Rootrestore16:46:48 PASS640Dateien/beideSnapshotNS/vierLogs/PIDsUnitsDisplay/vierLocks. Audit0459c58 integriert/3RootTests/kanonischeHashes geprüft. BeideAgenten jetzt quieszent. Der lange mappedWeapon220-Rundlauf ist perSDK4193/1RED reproduziert; enger Attempt-NoProgressschutz im getrenntenWriterWT in Arbeit, noch kein Rootbuild/native Beleg. Vorhandene031Aggregate dienen dem Vergleich; kein alterRawreplay. Keine weiteren Gameplayänderungen oder Nativewiederholung vor Auswertung.
2. **A1 gezielter normaler Respawn:** Candidate im eigenen WT `/srv/tse-build030-skulls-closed-audit-20261115` hat den konkreten Nachread-ACK-Fristguard per RED→GREEN abgeschlossen, Source932a119/63dfe2c integriert/23Roottests. D-v1/D-v2 bleiben NEVER_NATIVE; D-v3/F eingefroren und Rootdelta separat geprüft. F1scheitertevorInputamechtenReadervertrag; Source27ab3f5korrigiertnurbeideOptionalflagsFalse,6neueTestsPASS. NächsterSchrittistnachSource110/Delta102diefrischeF2KontrolleundnurbeiPASSbedingterTrace. Rootentscheidung: expliziter DEAD_READY-Basisreader ohne optionale lebende Muzzlegeometrie zulässig; alte Coltreader-/Inputfreeguards unverändert. PID/World/Actor/Slot/MayRespawn2/Buttons/HP durch frische Doppelreads binden. Keine HP-/Positions-/Winkelwrites, kein Treffer aus Input ableiten. Vorbereitung nur regulär durch bestehenden Festziel030-Coltpfad, sonst begrenzter FAIL. Nach Arm genau ein normaler Fire-Down/Up; tatsächliche Hold-/Releasezeiten und serverseitige ACK/Init/erste-Tick-/Owner-/Schadenskette messen. Grenzen 10s/15sTTL/Queue64/Native16384/85s/90s/eight/.2 unverändert.
3. **Root integriert und prüft:** Claims getrennt; ausschließlich Root baut, ändert Runtime und Live. Nach Source-/Pinreview und Sicherung genau passende neue uninstrumentierte Kontrolle und nur bei erfolgreichem Close/Restore passender Trace. Fehlende Ereignisse bleiben INCOMPLETE; kein blinder AI-only-Retry.
4. **Ressourcen:** mindestens8GiB Disk erhalten, zusätzlich64MiB Schreibreserve vor vorbereitenden Schreibaktionen. Closedbelege nur nach vollständigem externem Backup und geprüfter ausführbarer Byte-/Metadatenrekonstruktion komprimieren/retiren; bestehende Originalarchive/Rollback051/qualifizierte Runtimes bleiben erhalten. Während Native keine Tests/Builds/Reader/Archive/Downloadsparallel.
5. **A abschließen:** A1 beide Opferrollen/Neustart/Mapwechsel; A3 direkte Tiervergleiche; A4 funktionale Kartenmatrix/Spezialübergänge und konkrete Waffenlücken beheben. Erst geeigneten Kandidaten in formale A5-Gates nehmen, danach Dev→Public seriell. Anschließend B ohne erneute Aufforderung beginnen. Ein Build, Audit oder Commit beendet den Gesamtauftrag nicht.

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

Source108: remote `ca2fc93a23df88c4c9ad80dc2763d2c5e37e91a2`, lokal
`7a576d31dbaac34710376a5609376e9704849874`, Baum
`f3bc0dabfb636459d31386da6a6f99a206ac1912`; tatsächlich gefetcht und Diff0 am
15.11.16:32:27. Delta100: 2.239.537B, SHA256
`37bfdc47695c224251a1777df269ce99ffd1add502fa7535f234d17a2dd46c20`,
Drive `1U2EMTQNUBujCkDffxNCQYUivBx6v4T0D`; Vollrücklauf+zwei vollständige
Datei-/Metadatenrekonstruktionen 576 Dateien/8.806.707B PASS16:33:55.
Historische Sync-/Trouble031-/22Mapstream-Recoveries eigenständig archiviert und
vollständig extern geprüft; Originalarchive und Mischrollback051 bleiben erforderlich.
Keine Rohidentitäten, Zugangsdaten oder Retaildateien öffentlich veröffentlichen.

Neue Quellen/Configs/Navmetadaten/Tests/bereinigte Berichte committen und pushen,
Remote tatsächlich rückprüfen. Private vollständige Belege und Restorearchive im
vorhandenen Drive-Projekt sichern, vollständig rücklesen und rekonstruieren.
Bei Kontextwechsel exakte aktive Jobs/Locks/SHAs/Fehler/nächste Befehle im Handoff
festhalten. Keine unbeaufsichtigte Weiterarbeit behaupten.

Gesamtabschluss erst bei A-Nachweisen, B-Abnahme auf Dev und anschließendem
Flottenrollout, realem Kampf/Navigation/Respawn, Sessions/Chat und geprüften
Ressourcen/Backups/Remote/Rollback. Bei konkretem externem Hindernis blockiert oder
teilweise abgeschlossen melden. Derzeit **A offen/B nicht begonnen, kein externer
Blocker**; selbstständig weiterarbeiten.
