# SSAM.AI – ausführbarer Gesamtplan A → B

Stand 15.11.2026, 16:25 UTC. Umsetzung läuft; **A offen, B nicht begonnen**.
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

Stand 15.11.2026, 16:25 UTC. Exakte private Pfade/Hashes und frühere Fehler stehen im Handoff; ältere Planstände bleiben in Git erhalten.

| Arbeit | Status | Beleg und nächster Schritt |
|---|---|---|
| Live-Flotte | zuletzt 15:59 erneut geprüft | Dev048, Public Red Gen2, vier Public018; je acht eigene Bots, keine zusätzlichen Teilnehmer; 18 geladene Rollen/Startkonfigurationen wie Rollback051. Bis belegter Verbesserung erhalten. |
| Namen/Identitäten | Bestand erhalten | 458 Namen; 48 kollisionsfreie sichtbare Botnamen, stabile Profile/IDs wie Rollback051. |
| Dev-Sync | frühere Ursache offen | 14:50–15:59 weitere 9.987 OK/0BAD/0Disconnect; ältere 23BAD/2Disconnect und 70BAD/3Disconnect bleiben FAIL. |
| A1 Eingabekalibrierung | offen | Maus-/Tastatur-/Pitchbefunde fehlgeschlagen; keine Toleranzänderung. |
| A1 neue Messmethode | begrenzt bestanden | Kontroll-/Traceprobe geschlossen und voll ausgewertet: 414 tatsächlich beendete exkludierte Weltcasts, 207 GameTickpaare bis F, 38 Originalbereiche restauriert; Init/Colt/Schaden jeweils 0. Kein A1-Pass. |
| A1 normaler Originalrespawn | Source/TDD in eigenem Worktree | Echter regulärer Tod vor Arm/MayRespawn2; danach ein normaler Fire-Release und tatsächliche Init-/erste-Tick-/Normal-/Fatal-Schadenskette. Neue Bedingung, alte Inputfree-/Coltverträge unverändert. |
| A3 Schwierigkeitsstufen | offen | STARK>MITTEL und menschliches Spielniveau noch nicht belegt; Waffenversorgung unzureichend. |
| A4 Reset031 | geschlossen, begrenzt bestanden | 24/24 aktive Slotphasen; Vollauswertung 145 Leben, weiterhin 49,4s Waffenlücke. Reset030 bleibt 22/24 FAIL. |
| A4 Hole031 | geschlossen, vollständig ausgewertet | 206 Leben/204 zusätzliche Waffen-Gewinne/172 erkannte Spieler-Killzeilen; 79,43s und 57,85s ohne brauchbare Zusatzwaffe verhindern Freigabe. |
| A4 Trouble031 | geschlossen, vollständig ausgewertet | 600,074s/292 Leben/205 Gains/259 Spielerkillmeldungen; 38,45s Versorgungslücke. Root-Restore und Auditdateihashes geprüft; kein A4-Pass. |
| A4 Karten/Spezialübergänge | gezielter Fix032 gebaut, nativ ungeprüft | Atomischer Erstwaffenwechsel SDK4175/0;032/81Pins geprüft, neuer Trouble600-Fork in Vorbereitung. Übrige Karten/Übergänge offen; Desert Temple gesperrt, Welt fehlt. |
| A5 formale Stabilität | nicht begonnen | Funktional geeigneter Kandidat erforderlich; 1/4/8 Bots für 60/60/120 Minuten. |
| Sicherung/Veröffentlichung | Source105 / Delta098 vollständig geprüft | Remote-Fetch/Baum/Diff0; privater Vollrücklauf und zwei vollständige Perfile-Metadatenrestores. Trouble-Rohdaten voll gesichert; neuer Recoverybackup separat geprüft. |
| B Sessions/Chat | nicht begonnen | Erst nach nachgewiesenem Abschluss von A. |

## Unmittelbare Ausführung und Claims

1. **Trouble031 abgeschlossen:** Rootjob36038 beendet0/abgeholt; unabhängiger Rootrestore15:49:50 PASS. A4-Vollaudit022dee4 integriert, Root3TestsPASS und kanonische Dateihashes geprüft. A4-Agent im eigenen WT `/srv/tse-reset031-diag1-prepare-20261115` reproduziert nun die gesperrte Erstwaffensuche bei gehaltenem nicht dringendem Nebenitem und entwickelt nur nach echtem SDK-RED das atomische Wechseln zum vollständig validierten Ersatz. Keine neuen passiven Nativewiederholungen ohne konkrete neue Hypothese. Danach engste ursächliche Gameplaykorrektur mit messbarem Beschaffungs-/Bewegungsnachweis.
2. **A1 gezielter normaler Respawn:** Candidate im eigenen WT `/srv/tse-build030-skulls-closed-audit-20261115` dokumentiert neue Bedingung/Plan und implementiert mit echten RED→GREEN-Tests. Rootentscheidung: expliziter DEAD_READY-Basisreader ohne optionale lebende Muzzlegeometrie zulässig; alte Coltreader-/Inputfreeguards unverändert. PID/World/Actor/Slot/MayRespawn2/Buttons/HP durch frische Doppelreads binden. Keine HP-/Positions-/Winkelwrites, kein Treffer aus Input ableiten. Vorbereitung nur regulär durch bestehenden Festziel030-Coltpfad, sonst begrenzter FAIL. Nach Arm genau ein normaler Fire-Down/Up; tatsächliche Hold-/Releasezeiten und serverseitige ACK/Init/erste-Tick-/Owner-/Schadenskette messen. Grenzen 10s/15sTTL/Queue64/Native16384/85s/90s/eight/.2 unverändert.
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

Source104: remote `56209ff331deb82f7a722a34470c881c0bee1378`, lokal
`cd70501026e42a33f0e6d25106d2ccd9e2198b3f`, Baum
`0031d66207c664d58bd5177a8035e11b1cbb16fb`; tatsächlich gefetcht und Diff0 am
15.11.15:35:43. Delta097: 9.128.045B, SHA256
`ff19e2ef0538e190b9b444c34c7bc8c9322577a975ccdcd5ddb8ccda9fdf516f`,
Drive `1T_p93-BlSn62AD_Ms3d8HlHSb4ztA6si`; Vollrücklauf+zwei vollständige
Datei-/Metadatenrekonstruktionen 1.613 Dateien/65.273.762B PASS15:38.
Historische Sync-Recovery eigenständig archiviert und vollständig extern geprüft;
Originalarchive und Mischrollback051 bleiben erforderlich. Keine Rohidentitäten,
Zugangsdaten oder Retaildateien öffentlich veröffentlichen.

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
