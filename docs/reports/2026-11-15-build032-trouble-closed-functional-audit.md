# Trouble032: acht aktive Bots, neuer Erstwaffenpfad nicht ausgeübt

Der einzelne geschlossene Fall `nav20-032-trouble-root-trouble-20261115-163515` zeigt auf allen acht eigenen Bots Bewegung, tatsächliche Useful-Inventargewinne und native Useful-Fireflags mit Same-Life-Sourcecounterwachstum. **In allen vollständigen Closedlogs fehlt jedoch jeder `first_weapon`-Zielwechselmarker.** Damit ist die neue032-Präemption nativ nicht ausgeübt und keine Versorgungsverbesserung nachgewiesen. Lange Waffenlücken bleiben. Keine A4-/Stärke-/Produktionsfreigabe; A offen, B nicht begonnen.

Originalstatus unverändert `PASS_LIMITED_REACQUIRE_DIAGNOSTIC_OBSERVATION_ONLY`, Result-SHA `9bf131da4f9091abdb90a45c70100ddccf120a6039665ced497f5409e8fc175d`. Beobachtet600,052863736s, gleiche Trouble/Hard2/achtDEMON3/Original20FPS/DIAG1-Bedingung. Build032-DLL `403fa89e6be18642cc5a699ced5cca484031eb310d56b211537f077995bdf3ce`; kein eigener Runtime-/Gameplayeingriff.

## Vollständige Nenner

V3 validiert13995 Readversuche einschließlich386 aufgezeichneter Fehler. Rawgruppen4526 BotA/4543 BotB/4540 Original+Overlap, Gameplay4525/4542/4539, drei pausierte Smokes. Feste kanonische Gruppen/Readserial-/PID-/Start-/World-/Epochhüllen bleiben erhalten; Overlap ersetzt keine kanonische Evidenz.311 eigene Leben,143 Useful-Possession-Leben und194 echte Useful-Inventargewinne; drei Corpse-only-, vier mehrdeutige Healthreihenfolgen,201 links-/acht rechtszensierte Leben und303 beobachtete Todesenden. Kein Alive-after-dead oder zensierter Start wird optimistisch verlängert bzw. als neuer Pickup gewertet.

| Ownslot | Leben | Usefulbesitz | echte Gains | gebundene Useful-Fireflags | max.≤1m-Stationarität s |
|---|---:|---:|---:|---:|---:|
| A0/global0 |41|15|20|299|1,800110|
| A1/global2 |45|18|21|422|1,499634|
| A2/global3 |34|16|21|527|1,549622|
| A3/global4 |37|21|30|430|1,150070|
| B0/global5 |36|21|31|610|2,550156|
| B1/global6 |38|19|26|277|2,199463|
| B2/global7 |44|18|24|274|2,300140|
| B3/global8 |36|15|21|400|2,100128|

3239 gebundene Useful-Fireflagbeobachtungen beweisen weder3239 Schüsse noch Treffer-/Bullet-/Damage-ACKs. Alle acht haben tatsächlich veränderte native Positionen; Chords sind Endpunktabstände, keine durchgehende Route. Größte exakt unveränderte Position1,650101s, größte≤1m-Stationarität2,550156s. Kein langer allgemeiner Stillstand aus diesen Stichproben. Actor/Slotmapping A[0,2,3,4]/B[5,6,7,8]/Original[1] bleibt getrennt; der passive Originalobserver erhält keinen periodischen Respawninput und wird nicht als Bot gerechnet.

## Null neue Zielwechsel – keine erfundene Pickupkette

770 tatsächliche Goal-,764 GoalEnd-, zwei GoalBudget-, eine ReacquireSupport- und73 MotionProbezeilen bleiben erhalten. Sowohl strukturierte `CecilGoalEnd reason=first_weapon` als auch unabhängige Literalsuche in jedem der vier vollständigen Logs ergeben0. Daher gibt es0 neue Marker→Weaponattempt→nativeGain-Ketten. Ein sonstiger Weapon-Gain wird nicht ohne Marker als Beleg des neuen Pfades verwendet; fehlende Receiver-/Pickup-ACKs bleiben UNKNOWN. Eine neue generische Kausalklassifikation für hypothetische Marker wurde nicht als native geprüft ausgegeben.

4197 vollständige Pickerbatches:4197 Decision/4197 Origin/2288 Attempt/4197 Arbitration;4057 Source-Life-gebunden,140 UNKNOWN.4195 `normal_done`, zwei `no_anchor`. Attempts1759 `no_choice`,280 `committed`,236 `visibility`, acht `unreachable_path`, fünf `no_hint_or_probe`. Inf-Dijkstra und Knownbits werden entsprechend bestehendem Vertrag bewahrt; gedrosselte1Hz-Lücken und nicht ausgeführte Guards bleiben UNKNOWN. Kein fehlender/überlaufener Pflichtdatensatz wird als bestanden umetikettiert.

79 Reacquirezeilen:70 `context_only`, fünf `support_motion_guard`, drei `accepted_proposal`, ein `hints_exhausted`.Alle79 Source-Life-gebunden,76 zusätzlich mit vollständig innerhalb des Lebens liegendem nativen Print-/WPO-Zeitintervall. Zwei Hopcheckpoints, keine GroundReplan-/ImportantOriginRecovery-/Flightbegin-/Flightend-Zeile im gelesenen Bereich. Akzeptierter Vorschlag bleibt von Bewegung, ursprünglicher Radiusankunft und Pickup getrennt. Keine Spezialübergangs-/Lava-/Teleporter-/Jumppadfreigabe aus Höhe oder Endpunktnähe.

## Lange Waffenlücken und konkret beobachtetes Eligibility-Veto

Useful bleibt Mask0x3df8; Knife/Colt/DoubleColt zählen nicht als Useful. Längste fünf Aliveintervalle ohne Useful44,239227/36,741058/35,691284/33,391846/23,244324s.

A0/global0/g39, Spawn498,401824951: erster Alive498,401824951, letzter542,641052246, erster Dead542,841003418.333 Aliveproben:148 Knife,22 Colt,160 DoubleColt sowie drei `current=8` ohne entsprechenden Usefulbesitz. Ein Currentwert allein ersetzt keinen Owned-/Ammo-/Lifezeugen. Acht Colt-/19DoubleColt-Lastbuttons-Firebits und43 von46 Sourcezuständen mit nichtnulliger Bewegung, Positionschords405,429m; größte≤1m-Stationarität0,849792s, Readgap0,299927s. Keine durchgehend belegte reine Fernkampfphase oder Stehenbleiben.

Diese44s-Life hält überwiegend bereits mapped Weapon220/219:220 tick10141→10283 unavailable,21910283→10386 unavailable; kurz Armor67310406→10429 unavailable;22010489→10889 **Timeout**,21910889→10987 unavailable; Armor67310987→Tod11027. Der220-Versuch hat Sourcebeginn524,450012 und feste Deadline544,450012, kein Scan verlängert ihn.42 Pickerbatches,34×Supply genommen,36 behalten ein bestehendes Ziel; sechs öffnen normale Auswahl. Attemptsfünf no_choice/ein committed/zwei visibility/ein unreachable_path.

Bei den beobachteten Armor-Heldscans ist das bestehende Searchcooldown konkret noch offen: tick10426 `source_now=521.2999877929688 < search_after=525.2999877929688`; tick11007 `550.3500366210938 < 554.3500366210938`. Das ist ein tatsächliches032-Eligibility-Veto, keine Erklärung der gesamten44s und kein Beleg eines alternativen freien Waffenpools. Die langen mapped Weaponversuche sind ohnehin absichtlich nicht durch die Sideitem-Präemption ersetzbar.

A3/global4/g46, Spawn500,001434326: Alive bis536,742492676, Dead536,992431641,36,741058s.133 Colt/85Knife/59DoubleColt;21Colt-/sechsDoubleColt-Lastbuttons-Firebits.31 von35 Supplyarbitrationen genommen, Positionschords371,601m,≤1m-Stationarität0,649841s. Weapon220→219 unavailable, danach nichturgentes Health302 tick10489→10569 unavailable (Sourcehealth55), kurz DoubleColtitem13155, danach220 bisTod. Die drei beobachteten Health-Heldscans `525.450012/526.450012/527.450012` liegen sämtlich vorSearchAfter529,450012. Keine globale Combat-veto- oder CD-Defekthypothese daraus.

A0/global0/g31, Spawn352,837371826: beobachteter Alive352,887359619 bis388,578643799, Dead388,728607178;35,691284s, linkszensiert.128Colt/140Knife, Chords399,532m,≤1m-Stationarität0,499878s. Mehrere220/219-Versuche enden unavailable, kurze Armor673/289-Versuche dazwischen, später220 bisTod. Der beobachtete gehaltene Armor673-Scan `369.6499938964844 < 373.6499938964844` scheitert ebenfalls am vorhandenen5s-CD. Native und Sourceuhren werden nicht über tick/20 gleichgesetzt; diese Vergleiche verwenden ausschließlich die bereits gemeinsam geloggten Sourcezeiten.

Der engste verbleibende Source-/SDK-Prüffokus ist somit ein **lange unverändert gehaltener mapped Weapon220-Versuch** mit tatsächlicher Bewegung, unterbrochenem nahen Kampf, festem20s-Timeout und wiederholter Unavailability anderer Weaponziele. Ob der Bot die tatsächliche Ankunft/Connector-/Pfadphase verfehlt oder ein anderer Teilnehmer das Item vorher nimmt, ist nicht bewiesen. Kein pauschales CD-/Radius-/Deadline-Relaxieren oder neuer Sideitem-Diagnose-Retry folgt aus diesem Fall. Weitere Gameplayänderung bleibt separater Rootentscheid nach diesem Audit.

## Vergleich ausschließlich vorhandener031-Aggregate

| Beobachtung |031|032|
|---|---:|---:|
| ganze eigene Leben |292|311|
| Useful-Possession-Leben |154|143|
| tatsächliche Useful-Gains |205|194|
| gebundene Useful-Fireflags |2846|3239|
| längste NoUseful s |38,449664|44,239227|
| größte≤1m-Stationarität s |2,449402|2,550156|

Beide sind separate stochastische Einzelbedingungen mit unterschiedlichen Leben. Mehr Fireflags sind kein Stärkenachweis; weniger Gains/längere Maxlücke kein kausaler Regressionsbeweis. **Eine belegte Verbesserung wird nicht behauptet**, gerade weil der neue Pfad0-mal ausgeübt wurde. Nur031 `summary.json` und dessen bereits bestehender Canonicalreceipt wurden gelesen, kein031-Rawreplay.

Originalserver-Consolevorlagen liefern275 Playerkillmeldungen (201Lead/71Fremdblast/dreiTelefrag),44 getrennte Selfblastmeldungen. Peerlogs werden nicht addiert. Exakte Namensbindung zu Queryslots scheitert; Slots/Lives/nativeZeit/Schadenkette bleiben UNKNOWN. Keine erfundene Normalisierung, kein Queryfrag-Damageersatz, kein Telefrag=Navteleport oder Selfblast=geplanterJump.

Alle vier Closedlogs frisch NOATIME gehasht:0SYNCBAD/0Too-many-bad-syncs/0geprüfte Crashmarker. Rootrestore16:46:48 bestätigt640Dateien/0Absenzen/beideSnapshotNS/viernormaleCloses/PIDsUnitsDisplay/vierLocks. Separater äußerer Hostmonitor691 Samples: CPUmax61,323155%, RAMminimum2451267584B, Disk8673673216B, größteLücke1,005713s,0Errors,KindExit0/reaped. Innerer581-Samplemonitor hat46,794089s-Startlücke. Unveränderte75%/1,5GiB/8GiB-Schranken, keine allgemeine Budget-/Dauerstabilitätsabnahme.

## Ein Rawpass, reproduzierbare Outputs

Neuer Caseadapter `tools/audit_trouble032_closed.py` SHA `f816be76cdf947e9a805cbb1b8d9283603060b26da1feaefeec5332cb524a533`, unveränderter Commonbody475ddc0a; neun exakte Case-/Pfad-/Map-/Statusliterale und vollständige Inverse. Tatsächlich importierte fünf V3-/Canonical-/Firehelper vollständig bytegleich zu archivierten Pins geprüft. Echtes falsches Parentcase-RED, drei neue Puretests PASS0,048s. Keine Änderung an Reader-/Life-/Decimal-/Sourcejoin-/Sampler-/Gameplayguards.

```sh
PYTHONDONTWRITEBYTECODE=1 nice -n 15 python3 -m unittest discover -s tools -p test_trouble032_closed_reader.py -v
PYTHONDONTWRITEBYTECODE=1 nice -n 15 python3 -i tools/audit_trouble032_closed.py
```

Audit verlangt frisches privates OUT und den exakten geschlossenen Case; nach Rootstoragekomprimierung vorher ausdrücklich dessen gepinnten Rehydratehelper verwenden, kein stiller gzipfallback. Vorscan nurstat:121767226B schwere Inputs. Jeder schwere Stream genau einmal gelesen, danach ausschließlich gehaltenes RAM. Finale Readerinputs123680131B; einschließlich kleiner031-Vergleichsmetadata124002004B<128MiB, proStream<64MiB. Ein zu enger vorgelagerter262KiB-Result-Metadatenread wurde korrekt vorParse abgewiesen; actualCommonreader blieb bei seiner bestehenden2MiB-Metadatengrenze.

Die erste Summaryausgabe wurde korrekt bei written0 durch8GiB+64MiB-Reserve abgewiesen. Nach Rootreservefreigabe wurde nur das eigene noch leere OUT entfernt und aus gehaltenem RAM fortgesetzt; keine schwere Datei erneut geöffnet. Absolute8GiB wurden dadurch nicht als unterschritten behauptet. Private Outputs `/srv/tse-trouble032-closed-audit-evidence-20261115`,4272425B<5MiB, jeweilsfrischeReserve/exclusive0600.

Canonicalreceipt `complete-final-receipt.json` SHA `3764e8de472245e2012524178ee43470b175a9f884382eaf88616a40cf9b8c5b`; Caseinverse `reader-adaptation.json` SHA `69ba37fb9430ac19d8e2cefc9947d412912de7272ee9efeb5d33d548efcb019c`. ZusätzlicherRAM-/031Aggregatebeleg `first-weapon-and-gap-final.json` SHA `4b6a98830fdeb23dd489d503e1f7bf70ceed22040d2d2a675265353a1672d09f`,28388B. Sein privater deterministischer Folgeschritt `.codex/evidence/trouble032-closed/final-ram.py` SHA `f2497deea4b69ecbe90dd34fcb28817dae1821141bccaabbf35e62d4f67df6d6` wird nach dem Hauptreader im selben gehaltenen `STATE` ausgeführt. Frühere Receipt-/Sourceaddendumdateien bleiben ausdrücklich Checkpoints. Keine Rohidentitäten/Retailbytes veröffentlicht. Reader59759 regulärExit0, alleRawhandles/Jobs beendet; keine weitere Analyse oder Änderung während Root's folgendem Nativefenster.
