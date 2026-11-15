# Skulls024: Funktionsabnahme offen, konkrete Versorgungs-/Recoverylücke

Der geschlossene600s-Lauf zeigt Bewegung, Waffenbeschaffung, Respawns und native
Fernfeueranforderungen für alle acht Bots. Eine Kartenfreigabe ist trotzdem
nicht belegt: Slot0 verbringt ein beobachtetes Leben von242,491s ohne brauchbare
Zusatzwaffe und bleibt nach einem korrekt protokollierten Routenabbruch in einem
kleinen Bereich hängen. Wiederholte Recoverybewegungen beheben die Lage im
Beobachtungsfenster nicht. Die genaue Reacquire-Ursache bleibt UNKNOWN.

Der ursprüngliche Controllerstatus
`PASS_LIMITED_A4_OBSERVATION_FUNCTIONAL_REVIEW_REQUIRED` bleibt unverändert.
Diese unabhängige Funktionsprüfung erteilt keine Skulls-/A4-Freigabe und ändert
keinen früheren FAIL. Kein Livewechsel, A offen, B nicht begonnen.

## Beleg und Nenner

Privater geschlossener Lauf:
`nav20-024-skulls-root-skulls-20261115-010531`,600.110787308s.
Resultat-SHA256
`b22aba0aa29eb8e16ec6ddc9121813ccaafc3ac8adace9731074802595ac7376`.
Build024/DLL
`192169fe8396bfe1fb9c49419657b9146120c64eb3ac15095ac50a6f8659753c`;
Hard2, achtDEMON3 und Original20FPS-Startvorlage,Diagnostics0.

Unveränderte `tools/navigation_life_summary.py` einschließlich aller V3-Hüllen,
festen Gruppen, Prozess-/Welt-/Slotbindungen und vollständigen Versuchslisten
unabhängig ausgeführt:192Leben,95mit Usefulbesitz,113echte Useful-Maskengewinne,
186beobachteteTode,96linkszensiert,6rechtszensiert,4mit konservativ abgetrennten
Alive-after-dead-Beobachtungen. Deren spätere Alivewerte verlängern kein Leben.
14040Leseversuche,541protokollierte fehlgeschlagene Reads bleiben erhalten;
keine fehlgeschlagene Messung zählt als Gameplaybeleg.

LifeSummary-SHA256
`00f5b0522182fdca819dee2262d2f5b2ec4c8028291defc61cf4ca666c67c2b1`.
Die kanonischen Gameplaygruppen enthalten4486/4508Samples;4502Overlap-Samples
bleiben Rohdaten und sind keine alternative Auswahl für diesen Audit.

Alle192Nativeleben wurden eindeutig einer SourceSpawn-Generation zugeordnet:
Rolle/Local→tatsächlicherSlot→Entity/World/Epoch sowie vollständig innerhalb
liegende gedruckte Nativezeitintervalle. Vollständige Closed-Logs enthalten201
SourceSpawns;9weitere Generationen ohne passenden beobachteten Native-Lebens-
zeugen bleiben UNKNOWN, überwiegend im nachgelagerten Source-only-Tail.
Dieser Tail erweitert das Nativefenster nicht. Kein SourceTick/20-Zeitabgleich.

## Alle acht Slots

„Feuerflag“ verlangt tatsächlich beobachtete brauchbare aktuelle und besessene
Waffe, Munition, natives `fire_requested` und Firebutton. Das ist eine native
Aktionsanforderung, kein nachgewiesener Weaponcall, Treffer oder Schaden.
Inventargewinne verlangen strikt spätere NativegameTicks innerhalb desselben
lebenden Zustands vor dem ersten beobachteten Tod.

| Rolle/local → Slot | Leben/Tode | Leben mitUseful | Useful-Gewinne | Strikte native Feuerflags | Längstes Leben ohneUseful, beobachtet |
|---|---:|---:|---:|---:|---:|
|A0 →0|21/20|10|10|176|242,491s, rechtszensiert|
|A1 →2|36/35|17|20|287|24,294s|
|A2 →3|31/30|11|11|197|26,643s|
|A3 →4|23/22|14|18|477|31,550s|
|B0 →5|22/21|8|12|608|30,752s|
|B1 →6|14/14|8|11|350|49,044s|
|B2 →7|24/23|14|16|396|25,144s|
|B3 →8|21/21|13|15|471|46,239s|

Alle acht besitzen zudem nichtnull Sourcebewegungen, Sichtkontakt-/Feuerzustände
und die bereits im unveränderten V3 belegte Source-Shotcountersteigerung in
passenden Leben. Diese verschiedenen Belege werden nicht zu einem Schadens-
oder Killnachweis vermischt.140SourcePickup-Zeilen sind einzeln erhalten;
138haben passende Native-Maskenwechsel-Zeitintervalle,2bleiben ohne solchen
Intervallzeugen. Kein nichtbeobachteter Pickup wird ergänzt. Itemcallback-
Identität sowie lebensgenau zugeordneter Schaden/Abschuss bleiben UNKNOWN.

## Prioritätsfall Slot0

Source A0/Generation26 ist eindeutig an NativeSpawn358.1360778808594 gebunden.
1804lebende Nativebeobachtungen reichen von358.1860656738281 bis
600.6768798828125:242.49081420898438s, links- und rechtszensiert.
Owned bleibt3, keine Usefulwaffe, kein Inventargewinn und kein natives Fernfeuer.
HP85 sind ab360.2355651855469 bis600.6768798828125 in1789Beobachtungen erhalten
(240.44131469726562s). Daraus wird weder Schadensimmunität noch eine unbekannte
Schadensursache abgeleitet.

Die Sourcezielkette ist ein Waffen13-Ziel an Nav271. Beobachtete Route:
13→90→121→122→128→129→248. Nav121 hat Flags10, die übrigen hier genannten
Punkte Flags0; spezielle Übergangsparität ist damit nicht nachgewiesen.
Die entscheidende Zwischenkante129→248 ist tatsächlich verlinkt:

- Nav129: Position(−36,−71.5,8),Radius4, keine Important-/Lock-/Nextbindung.
- Nav248: Position(−56,−63.5,8),Radius2, ebenfalls gewöhnlich; Zielkante hat8m
 Höhenunterschied. Ob die konkrete Weltgeometrie hier einen passierbaren Weg
 liefert, ist ohne tatsächlichen Cast-/Bewegungsbefund nicht bewiesen.

`botA.log`/Closed-Log Zeile5684 protokolliert
`CecilItemTransitEnd`, Source129/Hop248, `since=379.750`, `time=389.750`,
`best_distance=12.552368`, `reason=no_hop_progress`. Das ist der bestehende
10s/0.75m-Watchdog, kein Zieldeadline-Timeout und kein erfolgreicher Übergang.
Diese Zeiten bleiben Source-Policyzeiten. Die ursprüngliche Zieldeadline400.394
wurde dadurch nicht verlängert.

Von der folgenden SourceState-Zeile5688/tick7800 bis zum Snapshotende zeigen221
Zustände Goal0/Goal−1,Anchor−1,Navsource−1/Hop−1.58davon enthalten Bewegung
oder Strafing,0Sichtkontakt; Shotcounter bleibt534. Im Snapshot71`stall`- und
93`escape`-Recoveryzeilen, im vollständigen Sourceleben einschließlich Tail
79/103. Recoveryvorschläge und tatsächlich beobachtete Positionsänderungen
bleiben getrennt; diese Zahlen beweisen keinen erfolgreichen Ausweg.
Ein echter früher Wallprobe-Beleg bei tick7520 meldet Hit/Normal auf der
Zwischenroute. Er beweist keine durchgehende LOS-Sperre aller späteren Hints.

Die kanonischen Nativepositionen bleiben von368.8834533691406 bis
600.6768798828125 während231.79342651367188s/1724Beobachtungen in der Box
X[−51.4987,−41.9833],Y[−71.9974,−69.5869],Z[11.3205,17.9985].
Die aufsummierten beobachteten Verbindungslinien ergeben213.812m bei7.164m
Endpunktabstand. Das beschreibt örtliche Wiederkehr, keine kontinuierlich
vermessene Laufstrecke oder formal geschlossene Routenschleife. Die Definition
„je Achse höchstens10m, alle aufeinanderfolgenden bekannten NoUseful-Reads,
GameTicklücken höchstens0.5s“ ist eine reine Auditmetrik, keine neue Abnahme-
oder Gameplaytoleranz. Keine günstigen Samples werden ausgewählt.

## Stillstand und andere lange Leben

Eine≤1m-Ankersphäre ist kein absoluter Stillstand. Alle kanonischen Reads
werden erhalten, auch unterschiedliche Beobachtungen desselben GameTicks.
Zusätzlich wird exakt gleiche Position bei Translation(0,0,0) getrennt gemessen.

| Slot | Längste kanonische≤1m-Episode | Exakte Position/Nulltranslation | Unveränderte alte ALLSTREAM-Metrik |
|---|---:|---:|---:|
|0|10,098s|3,499s|11,647s|
|2|2,549s|2,299s|2,549s|
|3|1,050s|0,400s|0,800s|
|4|7,498s|7,248s|7,498s|
|5|2,550s|2,350s|2,550s|
|6|2,550s|2,300s|2,550s|
|7|2,650s|2,450s|2,650s|
|8|2,550s|2,300s|2,550s|

Die ALLSTREAM-Metrik verarbeitet zusätzlich Overlap und überspringt dort bereits
gezählte Life/Ticks. Sie bleibt getrennt; Unterschiede sind keine nachträgliche
Verbesserungs-/Regressionsbewertung. Insbesondere ist Slot0 nicht242s absolut
stationär. Auch die7,248s-Episode vonSlot4 ist tatsächliche Bewegungsarmut;
absichtliches Warten gegenüber unerwünschtem Stillstand ist damit noch nicht
ursächlich unterschieden.

Weitere lange NoUseful-Leben: Slot6/Spawn236.20980834960938 erreicht49,044s;
Slot8/Spawn502.5508117675781 erreicht46,239s und dessen vorheriges Leben ab
461.7607727050781 erreicht39,040s. Die beiden erstgenannten enthalten ebenfalls
`no_hop_progress` auf einer Waffen13-Zielkette, danach weitere Zielwechsel.
Im dritten stehen `unavailable`, `unreachable` und ein Hopcheckpoint vor dem Tod.
Alle Lebensketten sind privat vollständig erhalten; Diagnostics0 liefert keinen
nachträglich erfundenen typedUnavailable-Grund oder konkurrierenden Aufnehmer.

## Replan, Ursache und nächste entscheidende Beobachtung

0`CecilGroundReplan` in beiden Snapshot-, Final- und vollständigen Closed-Logs.
Der neue Stale-anchor-Zweig ist hier nicht nativ ausgeübt.7gebundene
ItemTransitEnds und12Hopcheckpoints sind einzeln lebensgebunden erhalten;
0ImportantOriginRecovery-Vorschläge,3Healthconnector-Vorschlagszustände sind
kein Pickup-/Routingerfolg.

Der letzte Slot0-Punkt liegt geometrisch12,216m von248 und14,026m von129
entfernt. Das erklärt allein keine fehlende Wiederaufnahme: `BotSupplyNearest`
prüft zwar12m/Height3, aber `BotCecilReacquire` kann innerhalb32m/Height8
weitere Hints testen; farHint gilt nur bei geometrisch fehlender lokaler Auswahl.
Er behält6s-/Retry6s-Regeln, drei Kandidaten und die bestehenden Budget-/LOS-/
Support-/Lockguards. Deren tatsächlich gewählter Rückkehrgrund ist hier nicht
protokolliert. Weder Höhen-/Radienaufweitung noch ignorierte Locks sind begründet.

Kleinster sinnvoller zusätzlicher passiver Beleg vor einem kausalen Fix:
Reacquire-Rückkehrstatus (Support/Metadaten/Context-only/Budgetdeferred/keine
geometrischen Kandidaten/LOSrejected/accepted), tatsächlich betrachteter Hint
und Raybudget vorher/nachher, mit Entity/Generation und tatsächlicher Nativezeit.
LOSresultat nur aus einem ohnehin ausgeführten Cast. Keine neuen Casts,
Schwellen, Inputs oder Deadlinefreigaben. Dieser Vorschlag ist nicht implementiert.

## Reproduktion, Ressourcen und Grenzen

Eigener Audit-WT `/srv/tse-build024-skulls-closed-audit-20261115`.
Keine Tests/Compiler/Spiel-/Display-/Frida-/Netzprozesse gestartet, keine
Gameplay-/Harnessänderung. Reproduktion ausschließlich an geschlossenen Daten:

```bash
PYTHONPATH=tools nice -n 15 python3 -B tools/navigation_life_summary.py /srv/tse-milestone-a-evidence-20261111/nav20-024-skulls-root-skulls-20261115-010531 > .codex/evidence/skulls024/life-summary.json
nice -n 15 python3 -B .codex/evidence/skulls024/analyze.py
nice -n 15 python3 -B .codex/evidence/skulls024/enrich.py
```

Private vollständige Lebens-/Slot-/Event-/Readserialquittung:
`extended-receipt.json`, SHA256
`c78c4bdb661bbc0e16bcfd44c939d3bd22e7de4870459464f13106edf62d4fe5`.
Die beiden Readerhashes, sämtliche Rawinputhashes und der unveränderte
LifeSummaryhash stehen darin; kein zusätzlicher Metadatenfinalizer nötig.
Zwischenquittung `complete-receipt.json` SHA256
`65546be44f9da35e3d3dc90f7eb39e152ce97ea71f1355e900d18e2e97c447a7`.
Rohlogs/Spieleridentitäten/Retaildaten bleiben privat.

Root meldete unabhängig640Dateien/0Absenzen/vierClosed-Logs und Unit-/Display-
Restore PASS,0neueBAD/Disconnects. Äußerer Hostobserver:683Samples,
max1.002483sLücke,CPUmax63.4271%,RAMmin2520137728Bytes,
Diskmin9047359488Bytes,0Budgetverletzungen. Das ersetzt weder die obige
Funktionsbewertung noch formale Dauer-/WAN-/Human-/Cecilparitätsabnahmen.

Skulls bleibt funktional offen; Ursache und sichere Behebung der belegten
Versorgungs-/Recoverylücke erfordern den gezielten nächsten Befund. Kein Loaded-
only-/Frag-only-PASS, kein Rollout aus diesem Audit.
