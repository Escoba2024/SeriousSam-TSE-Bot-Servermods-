# Build030 Skulls: geschlossener Audit, keine A4-Abnahme

030 liefert weiterhin lange Leben ohne beobachtete Usefulwaffe und belegten
Stillstand. Die alte bewegte267→112-W9-Holdepisode wurde nicht positiv
wiederholt. Zwei `unreachable_hold`-Abbrüche sind vorhanden; die zugehörigen
letzten Sourcepositionen und nativen SameLife-Beobachtungen sind stationär.
Das beweist weder einen erneuten falschen Bewegungsabbruch noch bereits die
native Wirksamkeit der Korrektur.

Fall: `nav20-030-skulls-root-skulls-20261115-095027`, Ergebnis-SHA256
`c24b74021283a228719600c27ebe75db605de908a4aa6fff0912ab1afd508d1d`.
DLL `bf70585708cb5cc0d0d62416b641c1df758c90b8cdbd062a04dccecca2a29412`.
Der Originalstatus bleibt `PASS_LIMITED_REACQUIRE_DIAGNOSTIC_OBSERVATION_ONLY`:
600,074206s, Skulls/Hard2/8DEMON/Profile7/Original20FPS/diag1.
Originalslot1 ist kein KI-Slot. Die Botzuordnung bleibt A=[0,2,3,4], B=[5,6,7,8].
Root prüfte vier normale Closes, vier saubere Logs mit0SYNCBAD/Disconnects
und640Dateien/NS-Metadaten, Rollen/Units/Displays/Sperren nach dem Fall.
Dieser spätere Audit ersetzt weder den Restorezeitpunkt noch dessen Scope.

Die vier vorhandenen Reader wurden exakt von029 retargetet und jeweils einmal
ausgeführt, anschließend der bestehende DriverFinal-Auditor mit unveränderter
Logik. Ganze Sourceinversen liegen vor. Alle fehlgeschlagenen Reads,
Source-only-Tails und unbekannten Clockzuordnungen bleiben erhalten.029 wurde
nicht restauriert oder erneut ausgewertet: nur kleiner Handoff und ein auf
20MiB begrenzter gzip-Read der vorhandenen17,56MB-Ergebnisquittung wurden
verwendet, deren ursprünglicher Hash geprüft wurde.

| Gleicher Nenner/Definition |029|030|
| --- | ---: | ---: |
| Beobachtete Botleben |238|192|
| Beobachtete Tode |230|184|
| Links-/rechtszensierte Leben |158/8|124/8|
| Alive-after-dead-ambige Leben |3|1|
| Alle Readattempts / fehlgeschlagen |14058/567|14007/529|
| Leben mit Usefulbesitz |97|101|
| Strikte Usefulbitgewinne |116|119|
| Kanonische Native-FIREflag-Beobachtungen |3303|3308|
| Längste beobachtete NoUseful-Spanne |48,688s rechtszensiert|50,003s bis beobachtetem Tod, linkszensiert|
| Maximaler1m-Aufenthalt |2,700s|9,251s|
| Exakt gleiche Position plus Nulltranslation |2,450s|7,750s|
| DriverFinal-Zeilen |5036|5064|
| Exakt Source-Life-gebundene Driverzeilen |4902|4967|
| Driverzeilen mit ganzer SameTick-Nativeclock |229|288|

Diese einzelnen600s-Fenster mit unterschiedlichen Lebens-/Waffenverläufen
sind kein Duell.169gegen218Server-Killzeilen begründen keine Überlegenheit
oder Regression. Auch3308FIREflag-Beobachtungen sind keine Waffenfunktions-
oder Schadensnachweise. Roots strengere Flag-plus-SameLife-Sourcegrowth-
Auswertung zählt3298; das ist ein zusätzlicher, anderer Nenner.

030 umfasst13478erfolgreiche Readgruppen einschließlich3Paused-Smokes:
4504A,4476B,4498Overlap. Gameplay-only sind es13475, davon8978kanonische
A/B-Gruppen;4497Overlap-Gruppen bleiben separat validiert. Alle192nativen
Leben sind eindeutig an Sourcegenerationen gebunden;195Sourcegenerationen
insgesamt enthalten3ohne nativen Lebenszeugen. Von5064Driverzeilen bleiben
48ohne SourceSpawnbindung und49Source-only.4776haben keine akzeptierte
ganze SameTick-Nativeclock. Jede `map_known=0`-Zeile bleibt aktuellMapUNKNOWN;
Baseline-Map-Pin und gleiche Generation ersetzen diesen Nachweis nicht.

## Versorgung und Bewegung aller acht Bots

`Pickup+Bitzeuge` zählt Source-Pickupzeilen mit tatsächlichem nativen
Besitzbitzeugen, einschließlich nicht als Useful gewerteter Waffen. Diese
136Zeilen aus138Source-Pickups sind deshalb nicht mit119Usefulbitgewinnen
gleichzusetzen. Jede der acht Rollen hat unabhängig davon echte Usefulgewinne.

| Slot | Leben / linkszensiert | Usefulleben / Bitgewinne | Pickup+Bitzeuge | längste NoUseful-Spanne | max.1m-Aufenthalt |
| --- | ---: | ---: | ---: | ---: | ---: |
|0|34/20|13/13|14|47,388s|1,000s|
|2|21/14|9/13|15|50,003s|2,200s|
|3|28/15|12/14|17|26,902s|2,650s|
|4|25/19|14/17|20|16,396s|6,750s|
|5|23/15|16/19|21|27,493s|8,000s|
|6|26/18|15/17|19|37,491s|2,150s|
|7|18/12|10/12|14|34,991s|1,900s|
|8|17/11|12/14|16|32,802s|9,251s|

Die längste NoUseful-Spanne gehört A1/g8, NativeSpawn70,84972381591797 bis
beobachtetem Tod nach50,0030517578125s. Sie ist linkszensiert; lückenlose
Abwesenheit jeder Waffe wird nicht behauptet. Die gesampelte Polyline beträgt
≈917,83m, kein50s-Stehen. Gehaltene Ziele wechseln zwischen Item1025/W9,
917/W13,1027/W12,1459/W0,965/W7, erneut1025,964/W8 und1027. Die ersten sieben
Versuche enden als `unavailable`, der letzte mit Tod; sechs archivierte
Unavailable-Diagnosen nennen `render_type`. Ein fremder Pickup-Akteur oder
die Ursache des Versteckens ist UNKNOWN. Es gibt hier keinen Holdabbruch.

Die52SameLife-Driverzeilen dieser Episode zeigen42mal supplyActive,
16mal sichtbares Ziel,20Knife-Reiseanwendungen,52WeaponPoll und50FirePoll.
48SafeMotion-Ergebnisse sindStatus1,2Status2 und2nicht aufgerufen.
Nur2Zeilen haben zusätzlich eine ganze SameTick-Nativeclock. Das beschreibt
tatsächliche Entscheidungen, keine lückenlose kausale Erklärung sämtlicher
Waffenwege. Weaponenum1 ist Knife,2Colt; die alte Colt-Verwechslung gilt nicht.

## Zwei Holdabbrüche und die alte267→112-Episode

B1/g21, Spawn428,7688293457031, Item964/W8, Source265→Hop267:
GoalStartTick8598, `unreachable_hold` Tick8790. Die letzten Sourcepositionen
bei8760und8780 sind identisch(-6,897,-28,496,-51,868). Nativer SameLife-Zeuge:
15Reads,436,5669250488281–438,4164733886719, exakt gleiche Position und
Nulltranslation über1,84954833984375s.

B1/g28, Spawn527,1448364257812, Item1027/W12, Source188→Hop19:
GoalStartTick10566, Ende10755. Position bei10720und10740 identisch
(25,436,-26,619,42,759). Nativer Zeuge:15Reads,
534,7429809570312–536,6925048828125, exakt gleiche Position und Nulltranslation
über1,94952392578125s. An beiden GoalEndticks fehlt eine eigene Nativeclock;
keine SourceTick-/Walltime-Interpolation macht daraus einen exakten2s-Beweis.

Insgesamt gibt es7SourceStates267→112. Nur eine hat Item1025/W9 und diese
ist noch nichtneutral. Die weiteren Zustände betreffen Ziele ohne Item.
Die frühere029-A0/g32-W9-Höhensequenz ist damit im030Fenster nicht positiv
beobachtet. Gleiche lokale Nummer oder Generation über zwei getrennte Runs
bedeutet ausdrücklich nicht dieselbe Lebens-/Map-/Prozessidentität.

## Bewaffneter Stillstand trotz nichtneutralem Submit

B0/g11/Slot5, Spawn135,60366821289062, besitzt während der längsten
bewaffneten EpisodeUsefulwaffen:8,00048828125s im1m-Nenner und
7,7504730224609375s exakt gleiche Position/Nulltranslation.
Zwei DriverFinal-Aufrufe sind durch vollständig enthaltene native
Dezimalintervalle exakt in diese Episode gebunden:

| SourceTick / Nativeclock | SafeStatus | Tatsächliches Submitargument(x,y,z) |
| --- | ---: | --- |
|3260 /161,905273438|2|(3.991624116897583,0,0.2587241232395172)|
|3340 /165,905517578|2|(2.1213202476501465,0,-2.1213202476501465)|

In diesen beiden Aufrufen wird der Wunsch nicht zuNull verworfen.
Submit ist trotzdem kein NativeACK und kein erfolgreicher Escape. Aus den
gesicherten Daten folgt keine konkrete Physik-/Kollisionsursache. Vorhandene
Recovery-Vorschläge oder Sourcezeilen allein werden nicht als Bewegung
umetikettiert.0GroundReplan-Zeilen bleiben0;191lebens-/clockgebundene
accepted-Proposals sind ebenfalls keine191erfolgreichen Recoveries.

570Candidate-/312Selection-Zeilen enthalten174/35gültige lokale
Ownerreceipts. Deren bestehende Clock-/Cost-/Progress-/Deadlineprüfungen
bestanden. Fehlender Ownerbeleg bedeutet weiter UNKNOWN, nicht freies Item.
Itementity und Spielerentity werden getrennt gehalten.

## Ressourcen, Lesefehler und Reproduktion

Roots gehashte äußere Beobachtung umfasst689Samples: CPUmax62,5954%,
RAMmin2440642560B,Diskmin8959688704B,maxGap1,002868s. Status ist
`PASS_HOST_OBSERVATION_ONLY`, `budget_pass_claim=false`, keine Funktionsfreigabe.
Die geerbte innere Beobachtung bleibt mit582Samples,48,5058s-Startupgap und
1,2123s-Gameplaygap ebenfalls ausdrücklich ohne Gesamtbudget-PASS.

Im nachgelagerten Audit gab es einen offengelegten Leseschutzfehler:
`analyze.py` stellte zwei anfängliche externe Navreads aufNOATIME um, übersah
aber den dritten Abschlussread `nav_sha256=sha(nav)`. Betroffen war ausschließlich
die private Assetdatei außerhalbFixtureRoot, nach Roots Native-Restore.
Ohne vorherigen atime-Pin ist eine Änderung UNKNOWN. Es gab keine
Metadatenkorrektur und keinen Fullreaderretry. Ausgeführte Quelle/Outputs
bleiben erhalten; die zusätzliche exakte NoAtime-Quellkorrektur liegt separat
unausgeführt vor. Der Nativefall und frühere Restoreaussagen werden nicht
nachträglich ersetzt. Eine reine Vergleichsmaske wurde ebenfalls auf den
tatsächlich importierten Usefulwert0x3df8 korrigiert; dieselben sechs
bewaffneten Fälle bleiben, ohne Wiederholung eines Fullreaders.

Die private vollständige Reader-/Pin-/Vergleichsquittung liegt unter
`/srv/tse-build030-skulls-closed-audit-evidence-20261115`.
`comparison-and-focus-receipt-v2.json` SHA256
`211ef4a488d6f87e69d29cc09a533a7691608baa856f07361068fc2b666dd477`;
DriverFinalquittung `13f2a1123c259791ba17e6f6ed88db13a5ea5e0933fdb90e218b0132a98ee59a`.
Die öffentlichen DriverFinal-Regeln sind in
`tools/audit_build030_driver_final.py` mit exakter029-Inverse nachvollziehbar.
Keine C++-Änderung, Testsuite, Windowsbuild, zusätzliche Native oder Liveaktion
erfolgte. **Keine A4-Abnahme und keine Promotion.**
