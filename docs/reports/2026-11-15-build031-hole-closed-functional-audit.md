# Hole031: bewegte Kämpfe auf allen acht Slots, Versorgungslücken bleiben

Der einzelne geschlossene Hole-Fall `nav20-031-hole-root-hole-20261115-141204` zeigt auf allen acht eigenen Bots tatsächliche native Positionsänderungen, Useful-Inventargewinne und native Fernfeuerflags mit Same-Life-Sourcecounterwachstum. Er liefert einen begrenzten Hole-Funktionsbeleg, keine vollständige A4-Abnahme: zwei Leben bleiben trotz Bewegung79,43s beziehungsweise57,85s ohne Usefulbesitz. Die entscheidenden Spezialübergänge und Pickupverursacher sind weiterhin nicht vollständig kausal belegt. Kein Gameplayfix oder neuer Nativefall folgt aus diesem Audit.

Originalstatus bleibt `PASS_LIMITED_REACQUIRE_DIAGNOSTIC_OBSERVATION_ONLY`, Result-SHA `7e581f512eaf9717221d18eeb9b5091e11ed72d83b8960d282858c3bc00262a4`. Beobachtung600,144620s, Build031 `5c5c21d651f5513bcba4c1c3cc8ddc6495fbfbe7cdbbee506c70853bd15bbb0b`, Hole/Hard2/achtDEMON3/Original20FPS/DIAG1. Keine neue Laufzeit oder Änderungen an Kandidat, Nav, Harness oder Livebestand. A bleibt offen; B nicht begonnen.

## Ganzer unveränderter Nenner

Der unveränderte V3-/Attempt-/Canonical-/Lifevertrag validiert alle Hüllen einschließlich Overlap und drei getrennten Smokeproben. Rawgruppen BotA4508/BotB4523/Overlap4533; jeweils eine Smokeprobe.14037 Messversuche enthalten473 fehlgeschlagene Reads. Kein Messfehler wurde zu Gameplay umetikettiert. Alle erfolgreichen kanonischen Rows bleiben in ihrer tatsächlichen Readreihenfolge; kein SameTick-BestRow und keine SourceTick/20-Clockfusion.

206 beobachtete eigene Leben:154 mit Usefulbesitz,204 echte Useful-Maskengewinne,199 beobachtete Tode,123 links- und7 rechtszensierte Leben. Drei Leben besitzen nur Leichenproben; eines hat widersprüchliche Alive-Nach-Tod-Proben, die keine Alivezeit verlängern. Anfangs-/Endlücken bleiben offen.

|lokal|global|Leben|Usefulbesitz|Gains|gebundene Fernfeuerflags|max.1m-Stationarität s|
|---|---:|---:|---:|---:|---:|---:|
|A:0|0|32|23|29|420|1,600098|
|A:1|2|27|18|26|303|2,199493|
|A:2|3|26|19|20|244|2,149475|
|A:3|4|24|17|22|299|2,350143|
|B:0|5|30|19|25|291|2,399414|
|B:1|6|23|19|30|505|2,050008|
|B:2|7|23|22|30|427|1,549622|
|B:3|8|21|17|22|354|1,549976|

2843 gebundene Fernfeuerflagproben sind sampled Player-/Weaponzustände mit demselben unveränderten Sourcecounter-/Lifevertrag; kein Schuss-, Treffer- oder Schaden-ACK. Je Slot liegen etwa5,99–6,51km beobachtete Positionschords vor, ausschließlich mit bestehendem0,5s-Gapfilter. Das ist keine integrierte Weglänge: Teleport-/Gap-/Richtungswechsel werden nicht zur kontinuierlichen Route erfunden. Die größte exakte gleiche Position plus ausschließlich Nulltranslation beträgt1,950007s. Die beobachtete World-Y-Spanne reicht insgesamt−15,99855 bis66,73791; daraus allein folgt keine erfolgreiche Höhen-, Bouncer- oder Gefahrenroute.

## Längste NoUseful-Leben: überwiegend Messerbewegung zu wechselnden Zielen

**A:1/global2, Sourcegeneration28**, Spawn479,8063659668, erste/letzte Aliveprobe479,8563537598..559,2869873047, Tod559,4369506836:79,4306335s ohne Usefulbesitz.590 Aliveproben enthalten530-mal Knife1 und60-mal Colt2; keine trägt ein natives FIREbit.886,138m beobachtete Chords und maximal2,199493s innerhalb1m widerlegen einen durchgängig stehenden Bot.79 SourceStatezeilen enthalten72-mal Knife/fire0/vis0, siebenmal Colt/fire0/vis0 und zweimal Colt/fire0/vis1. Alle75 admittierten Pickerbatches sind `normal_done`;73 stoppen bereits am bestehenden Ziel, zwei führen den Normalpicker aus. Alle75 Same-call-Arbitrationen nehmen Supplybewegung. Das ist weder ein dauernder Colt-Fernkampf noch ein Bewegungs-ACK jeder einzelnen Submission.

Die tatsächliche Waffenzielkette lautet419/W8→450/W9→673/W8, dann Health436,442/W5→418/W7→673/W8→688/W5→450/W9→419/W8→442/W5. Acht Zielenden sind `unavailable` (sieben Waffen/Health436), einmal `unreachable` für442, zuletzt Tod. Eine Änderung418→673 besitzt keinen dazwischen protokollierten GoalEnd und wird nicht als Timeout erfunden. Waffen-Unavailability zeigt die bereits bekannte Render5-/Respawn-/Maske0-Semantik; wer aufnahm, bleibt unbekannt.

Der GroundReplan bei Sourcezeile18511/Tick10453 verbindet Source116→Hop62, frischen Anchor17 und Item673 mit dieser tatsächlichen Life. Das vollständige WPO-Zeitintervall liegt bei513,5481565..513,9480595; keine Tick/20-Ableitung. Bei19343 folgt ein `no_hop_progress`-Checkpoint Source0/Hop1/Goal35, best_distance23,605844/current_distance25,972950. Replan/Recovery bedeuten keinen nachgewiesenen Itemkontakt. Kein enger neuer Ursachenbeweis für eine Verhaltensänderung ist daraus gegeben.

**B:3/global8, Generation10**, Spawn156,4049377441, letzte Aliveprobe214,2584686279, Tod214,3584747314:57,8535309s ohne Usefulbesitz.388 Knife-/45 Coltproben; nur drei Coltproben mit nativem FIREbit.60 SourceStatezeilen besitzen sämtlich fire0, drei davon Colt/vis1.514,772m Chords, maximale1m-Stationarität0,750046s.54 `normal_done` und ein `no_anchor`,53 von55 Supplyarbitrationen genommen. Zwei Checkpoints Source51/Hop50/Goal35 beziehungsweise40 protokollieren fehlenden Hopfortschritt. Sechs Waffenenden sind `unavailable`, der letzte Zielversuch endet mit Tod. Die Distanz der drei Coltflagproben und echte Schusswirkung sind nicht belegt; daraus wird kein dauerhaftes Fernkampfverhalten abgeleitet.

Weitere lange NoUseful-Leben: A:3/global4 bei Spawn307,0485534668 mit30,892456s, A:1/global2 bei287,8532409668 mit25,043884s und dessen Anfangsleben bei2,6499986649 mit22,049911s. Alle206 Leben samt Zensierung/Geometrie stehen privat, nicht nur die erfolgreichen.

## Picker, Recovery, Spezialbewegung und tatsächliche Todesmeldungen

Die unveränderte031-Grammatik validiert4351 Decision-,4351 Origin-,2414 Attempt- und4351 Arbitrationzeilen. Kein deklarierter Attempt fehlt, kein Formatfault/Overflow.4351 ganze Batches:4184 `normal_done`,167 `no_anchor`;4292 eindeutig Source-Lifebound,59 UNKNOWN. Attempts:2219 `no_choice`,143 `committed`,37 `visibility`,15 `no_hint_or_probe`. Nichtausgewertete Knownbits und gedrosselte1Hz-Lücken bleiben UNKNOWN; ein fehlender Kandidat ist kein abgelehnter Kandidat.

Alle536 Reacquirezeilen bleiben erhalten:240 context_only,179 accepted_proposal,23 hints_exhausted,11 no_candidate_after_filters,75 support_motion_guard,8 support_geometry_rejected.530 sind Source-Lifebound, sechs nicht;514 besitzen zusätzlich ein vollständig innerhalb der Alive-Life liegendes natives Print-Zeitintervall. Bei den Geometryablehnungen existieren tatsächliche Segment-/Hitlocals, beispielsweise length0,299999/hit_distance0,399999, aber support_normal_known0. Der Normalwert0 ist dort kein gemessener senkrechter Boden. Akzeptierte Vorschläge bleiben von tatsächlicher Bewegung/Ankunft/Pickup getrennt.

Zwei GroundReplans und21 Hopcheckpoints sind vollständig gezählt. Die neun Flightbegin-Zeilen haben neun Enden mit `reason=context`; das ist kein erfolgreich abgeschlossener Navflug. Flug nach Explosion, Nav-Jumppad, Teleporttrigger, Höhenroute und Gefahrenüberquerung sind ohne entsprechende durchgehende Ursache-/Aktions-/Physicskette nicht gleichgesetzt. Konkrete Lava-/Bouncer-/Teleporter-Abnahme bleibt offen.

Die unveränderten Originalserver-Consolevorlagen aus SDK107 `Player.es:913–980` liefern tatsächlich172 Playerkillmeldungen:124 `poured lead`,39 Fremd-Blast, sechs Cannon, drei Telefrag.24 explizite Selfblast-, eine Suicide- und neun unspezifische `passed away`-Meldungen werden getrennt gezählt. Der allgemeine Blastregex würde auch Selfblast treffen; dieser eindeutige Selbstfall wird deshalb ausschließlich als Selfblast klassifiziert. Keine explizite Burning-/Drowning-/Abyssmeldung in diesen passenden Vorlagen. Die drei Telefragmeldungen beweisen keinen botgesteuerten Teleporterweg; die neun generischen anderen Todesmeldungen keinen Lavatod. Peerlogkopien werden nicht zum Servernenner addiert. Namen sind in Query und Console nicht exakt gleich gebunden; die streng exakte Zuordnung liefert deshalb UNKNOWN für Slot/Life. Keine Normalisierung oder fehlende Damage-/Bulletkette wurde erfunden. Queryfrags bleiben Nettoscore, kein Ersatz für diese Todesmeldungen oder Schaden-ACK.

## Ressourcen, Restore und Beleggrenzen

Alle vier geschlossenen Logs frisch gehasht:0SYNCBAD/0Too-many-bad-syncs/0geprüfte Crashmarker. Root bestätigt unabhängig14:23:40UTC640 Dateien/0Absenzen/beide Snapshot-Nanosekunden/vier normale Closes sowie beendete Rollen/Units/Display und vier freie Sperren. Dies ist Root's Restorebeleg, keine erneut ausgeführte Restoreprüfung dieses Readers.

Innerer Hostmonitor:582 Samples, CPUmax53,7879%, verfügbarer RAM mindestens2503798784B, Disk8935489536B; seine47,8399s-Startlücke bleibt offen. Der separate äußere Monitor deckt die Kindlaufzeit mit687 Samples ab: CPUmax63,4271%, RAMminimum2467700736B, Disk8881451008B, größte Lücke1,003317s,0Errors,0Signale/0Retries, KindExit0/reaped. Das sind gemessene Intervalle unter unveränderten75%/1,5GiB/8GiB-Schranken, kein pauschaler Budget-/Dauerstabilitätspass.

## Ein Durchlauf und reproduzierbare kleine Outputs

Vorscan ausschließlich stat.64MiB je Stream/128MiB gesamter Readerinput wurden vorab wegen56,245MB Inventory,43,328MB Sessionhealth und16,819MB Botclosedlogs begründet. Tatsächliche Readerinputs121036445B, kein zweiter schwerer Rawread; spätere Ableitungen aus gehaltenem RAM. Alle fünf tatsächlich ausgeführten V3-/Canonical-/Firehelper wurden vollständig bytegleich zu den archivierten gepinnten Sources geprüft; Lifehelper-SHA `6f4a2f150368ddddefb530afa2b40ba210a3d648dc6b323fe41430bbb4b9b65c`, unveränderter SourceJoin-AST-Präfix `c28dfa1cbe1713e08a5dfe65026badf364f60c845546accbac9cf35f49788011`.

Ein enger Readerfehler wurde mit tatsächlichem RED belegt: die erste Ereignisauswahl ließ die realen `CecilGoal`-/`CecilGoalEnd`-/GoalBudget-/Support-/Motiontags aus. Fünf Assertionsfailures, anschließend zwei neue pure Tests PASS; die Ergänzung verwendet ausschließlich bereits gehaltene Logs. Lebens-/Raw-/Fire-/Picker-Nenner änderten sich nicht. Ein interaktiver Fortsetzungsschritt benötigte explizites `__file__`, nachdem Python−i es entfernt hatte; der NameError führte zu keinem erneuten Rawread. Frühere Metadatencheckpoints bleiben getrennt erhalten.

Neue öffentliche Sources: `tools/audit_hole031_closed.py`, `tools/test_hole031_closed_reader.py`. Reproduktion nur gegen diesen geschlossenen Case in frischem privatem OUT: Modul importieren, `OUT` auf ein neues Ziel setzen, `main()` aufrufen. Kein Controllerimport, kein Runtimezugriff. Reader-SHA `0bafb00a21d47a9289d05fb280ba80c3f449fe32425e3292041803dcc70a39a7`. Private Outputs `/srv/tse-hole031-closed-audit-evidence-20261115`, zusammen4375582B unter5MiB, pro Write8GiB+64MiB-Reserve/exklusiv0600. Kanonischer Abschlussreceipt `complete-final-receipt.json`, SHA `a43cb6f74e3cbd67bc20d7cb2a4f889be81db8c3a5653e78fce2217f68d7080d`; er bindet sechs kanonische Outputs. `source-custody-final.json` hat SHA `7f39027f7c98f22660771721ea466d511623aa05d19a95fcd1177048a84f1083`. Die alten `final-receipt.json`/`source-custody-addendum.json` sind explizit nicht die abschließende Custody.

Hole ist somit mehr als nur geladene Nav: alle acht Bots bewegen sich, erwerben Usefulwaffen und besitzen gebundene Fernfeuerflags. Lange Versorgungsdefizite, konkrete Spezialübergänge und vollständige Schaden-/Pickupkausalität bleiben offen. Keine Rangfolge gegenüber048/018 auf anderen Karten, keine Kausalwirkung des Diagnosebuilds und keine Produktionspromotion werden behauptet.

Nach Abschluss des Rohdatenlaufs fand der eigene Keyreview einen weiteren engen Readerguardfehler: der Missing-Arbitration-Abgleich verglich `(local,actor,generation,tick)` mit dem tatsächlichen DriverFinal-Key `(local,tick,actor,generation)`. Ein Test führt den tatsächlichen alten Ausdruck aus und liefert echtes RED; nach der einzigen Ausdruckskorrektur drei pure Tests PASS0,005s. Alle4351 tatsächlichen Batches besitzen bereits ihre4351 eindeutigen Arbitrationszeilen, deshalb verändert diese zusätzliche Vetoabsicherung keinen Fallnenner oder erhobene Beobachtung. Kein Raw wurde nochmals gelesen. Die ausgeführte Readerfassung `0bafb00a…` bleibt privat als `.codex/evidence/hole031-closed/reader-as-run.py` erhalten; die korrigierte öffentliche Source hat SHA `475ddc0a9ea17020873e6733964b3d93abdb8c3a8005e6871fe338db466e0f0e`. Private `invocation-key-correction.json` hält genauen Vorher-/Nachhertext und vollständige Dateiinverse fest. Der bestehende Abschlussreceipt bindet weiterhin die tatsächlich gelaufene alte Fassung; ein neuer Source-Replay hätte folglich andere Readerhash-Metadaten und wird nicht als bereits bytegleich ausgeführt behauptet.
