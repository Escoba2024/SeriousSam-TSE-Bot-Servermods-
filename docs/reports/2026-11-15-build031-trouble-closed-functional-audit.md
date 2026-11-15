# Trouble031: acht aktive Bots, lange Erstwaffenlücken bleiben

Der einzelne geschlossene Fall `nav20-031-trouble-root-trouble-20261115-153818` zeigt auf allen acht eigenen Bots native Positionsänderungen, tatsächliche Useful-Inventargewinne und native Useful-Fernfeuerflags mit gebundenem Sourcecounterwachstum. Die beobachteten Waffenlücken reichen trotzdem bis38,449664 Sekunden. Dies ist ein begrenzter Kartenfunktionsbeleg; weder vollständige A4-Abnahme noch Versorgungsgarantie, Gameplayfix oder Produktionspromotion folgt daraus. A bleibt offen, B nicht begonnen.

Der technische Originalstatus bleibt `PASS_LIMITED_REACQUIRE_DIAGNOSTIC_OBSERVATION_ONLY`, Result-SHA `fba9d4a9c276e7dd3612c36ecbd81941ab67cf284a920810a5d3942bce4d7b1f`. Tatsächlich beobachtet600,074105s. Build031-DLL `5c5c21d651f5513bcba4c1c3cc8ddc6495fbfbe7cdbbee506c70853bd15bbb0b`; unveränderte Hard2/8DEMON3/Original20FPS/DIAG1-Bedingung. Kein neuer Lauf oder Runtimeeingriff durch diesen Audit.

## Ganze Lebens- und Slotnenner

V3 validiert13992 Readversuche einschließlich372 aufgezeichneter Fehler. Rawgruppen4534 BotA/4545 BotB/4541 Original+Overlap; Gameplay4533/4544/4540, drei pausierte Smokes. Feste kanonische Gruppen, PID/Start/World/Epoch/Readserialhüllen und genaue Source-/Life-/Decimalregeln bleiben unverändert. Overlapdaten sind kein Ersatz für fehlende kanonische Evidenz. Alle292 eigenen nativen Leben bleiben erhalten:154 Useful-Possession-Leben,205 echte Useful-Inventargewinne, drei Corpse-only-Leben, vier mehrdeutige Healthreihenfolgen,178 links- und sieben rechtszensierte Leben sowie285 beobachtete Todesenden. Zensierte Anfangsbestände zählen nicht als neue Pickups; Alive-after-dead verlängert kein Leben optimistisch.

| Ownslot | Leben | Usefulbesitz | echte Gains | gebundene Useful-Fireflags | max.≤1m-Stationarität s |
|---|---:|---:|---:|---:|---:|
| A0/global0 |33|23|31|500|1,549622|
| A1/global2 |38|23|28|325|0,850003|
| A2/global3 |41|16|22|214|2,099487|
| A3/global4 |36|22|30|384|1,950119|
| B0/global5 |31|11|13|429|2,449402|
| B1/global6 |36|17|22|332|1,350082|
| B2/global7 |38|19|26|323|1,899536|
| B3/global8 |39|23|33|339|2,200134|

2846 gebundene Fireflagbeobachtungen sind weder2846 Schüsse noch Weaponfunktions-/Schaden-ACKs. Positionschords sind Summen beobachteter Endpunktabstände, kein lückenloser Weg. Die größte exakt unveränderte Position innerhalb eines Lebens beträgt1,199707s. Höhenbereiche reichen je Slot ungefähr vom Boden bis8,08–12,01m; ohne kausalen Trigger-/Physicszeugen ist das kein Nachweis einer geplanten Höhenroute oder eines erfolgreichen Jumppads.

## Lange Waffenlücken: Bewegung und tatsächliche Prioritätsentscheidungen

Useful bedeutet unverändert Mask0x3df8, also keine Knife-/Colt-/DoubleColt-Aufwertung. Die längsten fünf beobachteten Aliveintervalle ohne Usefulbesitz betragen38,449664/32,492065/29,292847/27,143372/26,043640s; alle bleiben im vollständigen Nenner.

A1/global2, Sourcegeneration6, nativer Spawn2,399998903: Alive2,399998903 bis40,849662781, erster Dead40,999660492.300 lebende Inventorybeobachtungen:174 Colt,109 DoubleColt,17 Knife;177×Owned3 und123×Owned7. Beobachtete Positionschords308,413m, größte≤1m-Stationarität0,850003s, größter Readabstand0,250001s. Native Lastbuttons-Firebit38×bei Colt und13×bei DoubleColt; Sourcefire/Visibility ebenfalls vorhanden. Das belegt einzelne Pistolen-Feuerflags und Bewegung, keinen ununterbrochenen Fernkampf und keine Trefferkette.

Die tatsächlich Source-/WPO-/Life-gebundene Zielkette lautet:

- tick221 Weapon220/WeaponID9, mapped, Nav27; Endtick364 `unavailable`;
- tick364 Health274/Nav88; Endtick504 `unavailable`;
- tick504 Armor671/Nav81; Endtick534 `unavailable`;
- tick582 erneut mapped Weapon220/Nav27; Endtick853 `unavailable`.

Alle vier Readgründe sind konkret `render_type`/Render5. Für beide Weaponenden sind tatsächliche Weaponmetadaten gültig: OwnPickedMask0, picked_for_player0, pickup_once0, dropped0, respawn1, raw_weapon_type7, weapons_stay0. Das ist die bereits bekannte globale Respawnsemantik, kein neuer Ursachenfund und kein Nachweis des Aufnehmers. Bei Armor671 steigt nativer Armorbestand später auf25; die exakte Aufnahme dieses einen Items ist ohne Receiver-/Pickupzeugen nicht bewiesen.

37 vollständige1Hz-Pickerbatches gehören zu diesem Leben:27 behalten ein bestehendes Goal, zehn öffnen die normale Auswahl; neun Attempts `no_choice`, einer `committed`.25 Supplyarbitrationen werden genommen, zwölf nicht: sieben haben `known=3,truth=1,proposal=12` (aktive Bewegung/Movementownership fehlt, zugehörige Enemyentfernungen jeweils<8); fünf `known=1023,truth=271,proposal=7` (sichtbarer Gegner, nichturgentes Health-/Armorziel). Diese Stichproben zählen weder die dazwischenliegenden Ticks noch beweisen sie eine dauernde Blockierung. Die beiden Weapon220-Versuche behalten dieselbe Goalidentität und feste Deadline über mehrere Scans; ein unbegrenztes Rebudget-/Goalchurnproblem ist hier nicht belegt. Einige anschließende mapped Scans melden ausdrücklich eligible0; daraus wird keine verfügbare alternative Waffe erfunden.

B0/global5, Generation25, Spawn373,682281494: Alive373,732269287 bis406,224334717,32,492065s ohne Useful.245 lebende Beobachtungen nurOwned3:138 Colt,107 Knife, elf Colt-Lastbuttons-Firebits. Positionschords308,566m,≤1m-Stationarität0,549866s.32 Pickerbatches,31×Supply genommen; mehrere Armor671/673- und Weapon219/220-Ziele enden `unavailable`, letzter Weapon220-Versuch endet mit Tod. Hier erklärt eine pauschale Combat-veto-Hypothese die Lücke gerade nicht. Der dritte Fokus A2/global3 bleibt29,292847s ohne Useful mit Bewegung; vollständige Lebensdaten sind archiviert.

Die engste nächste überprüfbare Gameplayhypothese betrifft deshalb **Zielpriorität bei einem gehaltenen nichturgenten Nebenitem**, nicht allgemeine Reacquireradien: In `BotCecilChooseGoal` sperrt `!goalEntity` den Normalrescan; danach sperrt der erste `goalEntity!=0`-Guard auch `BotCecilChooseMappedWeapon`. Während Health274/Armor671 gehalten werden, wird ein möglicher mapped Erstwaffenpool tatsächlich nicht geprüft. Der vorhandene Code schützt dringende Heilung und nahe Kämpfe, doch ein gewöhnliches Nebenitem kann die Erstwaffensuche vollständig verdrängen. Ob im jeweiligen nativen Intervall eine freie erreichbare Alternative existierte, ist UNKNOWN, weil diese Entscheidung nicht ausgeführt wurde. Nächster enger SDK-Source-RED: echte ChooseGoal-Bodies mit gehaltenem **nichturgentem** Health/Armor, ohne brauchbare Usefulwaffe und einer frisch vollständig validierbaren mapped Weaponalternative. Erst bei echtem RED atomisches Handshake prüfen: altes Ziel erst nach vollständiger Ersatzvalidierung wechseln; dringende Heilung, Flight, nahen Kampf, Itembedarf, Cast-/Raybudget, Locks, Floor, Radien und feste Deadlines unverändert halten. Das ist ein überprüfbarer Fixclaim, keine bereits bewiesene native Fehlerursache oder Implementierung.

## Custody, Recovery, Todes- und Observergrenzen

4172 Decision-/4172 Origin-/2371 Attempt-/4172 Arbitrationzeilen ergeben4172 vollständige Batches:4034 Source-Life-gebunden,138 UNKNOWN;4170 `normal_done`, zwei `no_anchor`. Attempts1816 `no_choice`,277 `committed`,263 `visibility`,14 `unreachable_path`, einer `no_hint_or_probe`. Bekannte Inf-Dijkstraergebnisse bleiben textuell erhalten; nicht ausgewertete Knownbits und1Hz-Lücken bleiben UNKNOWN, kein Overflow-/Missingrow-Pass durch Weglassen.

85 Reacquirezeilen:73 `context_only`, neun `support_motion_guard`, je ein `accepted_proposal`, `hints_exhausted` und `support_geometry_rejected`.84 Source-Life-gebunden,80 zusätzlich mit ganz innerhalb des Lebens liegendem nativen Print-/WPO-Zeitintervall; fünf Hopcheckpoints. Keine GroundReplan-, ImportantOriginRecovery- oder Flightbegin/-end-Zeile im gelesenen Sourcebereich. Der eine akzeptierte Reacquirevorschlag betrifft B0/g13 bei nativer Zeit209,108154297, Air1/ground0, Hint16, ursprüngliche Position y12,0122. Er beweist weder kontrollierten Navflug noch tatsächliche Ankunft oder Pickup. Support-Knownbits werden nicht nachträglich vervollständigt. Insgesamt746 tatsächliche Goals,743 Goalends, fünf Goalbudget-, sieben ReacquireSupport- und64 MotionProbezeilen bleiben gebunden bzw. UNKNOWN erhalten.

Originalserver-Consolevorlagen liefern259 tatsächliche Playerkillmeldungen (171 Lead,85 Fremdblast, drei Telefrag) und41 getrennte Selfblastmeldungen. Peerlogkopien werden nicht addiert. Exakte Namensbindung zu Queryslots scheitert; deshalb sind Slot/Life/nativeZeit/Schadenkette dieser Meldungen UNKNOWN, statt per Normalisierung erfunden. Telefrag beweist keinen navgesteuerten Teleport; Selfblast keinen geplanten Sprung oder Lavatod. Keine konkrete Lava-/Gefahren-/Spezialübergangsabnahme.

Der lange HP−20-Fall ist **Global1/Originalobserver**, nicht einer der acht Botclients. Nur `vanilla_plus_overlap` enthält diesen Slot;4271 von4540 Gameplaybeobachtungen zeigen HP−20, Render3, denselben Spawn0,750000119. Mapping A[0,2,3,4]/B[5,6,7,8]/Original[1] ist geprüft. Der deklarierte Originalinputplan enthält nur normales Pause/Resume und ausdrücklich keine periodische Observereingabe. Ohne Respawninput ist dessen lange Leichenphase kein Botrespawnregressionsbeleg. Listenindex und nativer `slot` werden nicht gleichgesetzt.

Alle vier Logs frisch NOATIME gehasht, jeweils0SYNCBAD/0Too-many-bad-syncs/0geprüfte Crashmarker. Root bestätigt15:49:50.823891UTC640 Dateien/0Absenzen/vier normale Closes, beide Snapshotzeiten sowie beendete Rollen/Units/Display und vier freie Locks. Separater äußerer Monitor690 Samples: CPUmax61,068702%, RAMminimum2500366336B, Disk8699506688B, größter Abstand1,003598s,0Errors/Signale/Retry, KindExit0/reaped. Innerer581-Samplemonitor hat eine46,160383s-Startlücke. Keine allgemeine Dauerstabilitäts- oder Ressourcenqualifikation aus diesen Intervallmessungen.

## Reproduktion und unveränderte Fehlergrenzen

Neuer exakter Caseadapter `tools/audit_trouble031_closed.py`, SHA `3c9dbc5c800fdf757dde1e8bab390a00b4b08002c4111c86acdf39d31188a64b`, verwendet unveränderten korrigierten Hole-Commonbody `475ddc0a9ea17020873e6733964b3d93abdb8c3a8005e6871fe338db466e0f0e`. Neun reine Case-/Pfad-/Map-/Statusliterale, vollständige Sourceinverse; transformierter Body `2b6e4213506df45bc619cc27bebf461f3ccf28c890dc651a6e1ae6a5026aee27`. Tatsächlich importierte fünf V3-/Canonical-/Firehelper wurden vollständig bytegleich zu den gepinnten archivierten Sources geprüft. Lifehelper und SourceJoin-AST bleiben gleich. Keine Readerlogik/Gates/Clockfusion geändert.

Echtes altes Casebinding-RED (eine Assertionfail), danach drei neue pure Tests PASS; final drei PASS0,048s. Kommando: `PYTHONDONTWRITEBYTECODE=1 nice -n 15 python3 -m unittest discover -s tools -p test_trouble031_closed_reader.py -v`. Kein alter Rawreplay. Audit: `PYTHONDONTWRITEBYTECODE=1 nice -n 15 python3 tools/audit_trouble031_closed.py`, ausschließlich gegen den exakten geschlossenen Case und frischen privaten OUT. Nach Root-Komprimierung ist vorher explizites Rehydrieren über Root's gepinnten Storagehelper nötig; kein stiller gzip-/Rawfallback.

Vorscan nurstat,121882649B schwere Inputs; finale tatsächliche Readerinputs123741506B<128MiB, jeder Stream<64MiB, jeder schwere Raw genau einmal gelesen. Private Outputs `/srv/tse-trouble031-closed-audit-evidence-20261115`,4122685B<5MiB, exklusiv0600. Ein Write wurde korrekt durch die8GiB+64MiB-Floorprüfung blockiert; erst nach Rootreservefreigabe wurden ausschließlich gehaltene RAM-Ableitungen fortgesetzt, kein Raw wieder geöffnet. Der interaktive Diagnose-NameError `collections` vor dessen Import änderte keine Daten/Nenner. Alle Rawhandles und Pythonreader regulär beendet, Exit0.

Kanonischer `complete-final-receipt.json` SHA `d527cce1e888980f2be7b6ca2e3257d572c50c6a62b9ac3342b7f12f6f7ab21b` bindet sechs vollständige Outputs. `reader-adaptation.json` SHA `08558c42be1be83e115a738b422274efee1b42f14ead3e6d0f9f0d2f16e536f0` bindet Case-/Bodyinverse. Die zusätzliche `focus-and-passive-original.json` SHA `9a390974450063cff9e5f23cdba5a5c0be14b2f4769fac2dcedc18a7acda79cb` enthält ausschließlich RAM-Nenner und Importbytegleichheit. Ihr privater Reproduktionsschritt `.codex/evidence/trouble031-closed/final-focus-ram.py` SHA `d68cb67d9fb2aa87155ca2097b9bdcd036dd221131ec27d17782e717ab2c4e9a` wird erst nach dem eigentlichen Audit im gehaltenen `STATE` ausgeführt. Frühere `final-receipt`/`source-custody-addendum` bleiben ausdrücklich Metadatencheckpoints, keine Umwertung alter Fehler. Keine Rohidentitäten oder Retailbytes veröffentlicht.
