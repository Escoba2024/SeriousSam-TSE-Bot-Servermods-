# Skulls026: Diagnosebelege vorhanden, Funktionsabnahme weiter offen

Der geschlossene Diagnosefall belegt für alle acht Bots Bewegung, Respawns,
brauchbare Inventargewinne und native Fernfeueranforderungen. Eine Skulls-
Freigabe folgt daraus nicht: das längste beobachtete Leben ohne brauchbare
Zusatzwaffe dauert52,303s. Ein bereits bewaffneter Bot bleibt24,494s innerhalb
einer1m-Ankersphäre; davon16,546s bei exakt gleicher Position und Nulltranslation.
Reacquire akzeptiert dort wiederholt Vorschläge, während vorhandene spätere
Sicherheitsproben Wand-/Bodennormalenvetos zeigen. Vorschlag ist kein Ausweg.

Originalstatus `PASS_LIMITED_REACQUIRE_DIAGNOSTIC_OBSERVATION_ONLY` bleibt
unverändert. Kein früherer FAIL wird umgewertet. Keine Promotion, A4/A offen,
B nicht begonnen; aktueller Livebestand unberührt.

## Beleg und vollständiger Nenner

Privater Fall `nav20-026-skulls-root-skulls-20261115-030720`,600,098757519s,
Hard2, acht DEMON3, Original20FPS, Diagnostics1. Resultat-SHA256
`8bf66066a6736c6505d707644e0924a14562a8b0961f4f1d7723d54754b04100`;
DLL `2c9a238191b9642bf7f9613f01a461cf711f97fe62e581bdd7c93b5f58a9bcdd`.
Alle vier tatsächlich geschlossenen Rollenlogs frisch gehasht:

| Rolle | Closed-Log SHA256 |
| --- | --- |
| Dedicated | `14e28f3af3aa50c7f211e51be07a505ad88e36668f0ec293bc7153228204181d` |
| Botgruppe A | `6b8e6ae24609a741c176b3eadda4222a16fd675a84c82c9834dade42e00b5fc6` |
| Botgruppe B | `17dac2044e1b7ef05d92d86480846e68f59893327e23f15faa9111cd9d9fadc9` |
| Original | `eb2b65fa8a63ca91f9b14793b00d9c99ac6feac7b2277e74b137b29984a67b64` |

Die unveränderten reinen Funktionen aus `navigation_life_summary.py` validieren
alle V3-Hüllen, festen Gruppen, Prozess-/Welt-/Epoch-/Slotbindungen und sämtliche
14043 Leseversuche.515 fehlgeschlagene Reads bleiben erhalten und zählen nicht
als Gameplay. Kanonische Gameplaygruppen:4497/4519 Beobachtungen;4509 Overlap-
Beobachtungen und drei Pausensmokes bleiben getrennt. Der alte CLI verlangt einen
anderen Statusnamen; der private Einstieg prüft ausdrücklich den tatsächlichen
Diagnose-Status und verwendet dieselben Validierungsfunktionen. Keine Umbenennung.

188 Leben,180 beobachtete Tode,90 Leben mit Usefulbesitz,111 tatsächliche
Useful-Maskengewinne;133 links-/8 rechtszensiert,0 Alive-after-dead-Mehrdeutigkeiten.
Alle188 Leben sind über Rolle/local, Registry-Slot/Entity, Sourcegeneration und
vollständig innenliegende gedruckte Nativezeitintervalle eindeutig gebunden.
194 SourceSpawns insgesamt; sechs weitere ohne passenden Native-Lebenszeugen
bleiben UNKNOWN. Kein SourceTick/20-Abgleich, keine Lebensverlängerung durch Tail.

## Alle acht Slots

„Feuerflags“ verlangen beobachtete brauchbare aktuelle/besessene Waffe, Munition,
`fire_requested` und Firebutton vor dem ersten beobachteten Tod. Sie belegen
Aktionsanforderungen, keine Weaponcalls, Treffer, Damage oder lebensgenauen Kills.
Gewinne verlangen strikt spätere NativegameTicks im gleichen lebenden Zustand.

| Rolle/local → Slot | Leben/Tode | Usefulleben/Gewinne | Feuerflags | Längstes nieUseful-Leben | Max. kanonische1m-Episode |
| --- | ---: | ---: | ---: | ---: | ---: |
| A0 →0 |28/27|10/11|327|52,303s|1,800s|
| A1 →2 |25/24|11/12|307|49,988s|2,150s|
| A2 →3 |29/28|11/12|290|42,740s|1,550s|
| A3 →4 |17/16|11/19|626|31,542s|2,949s|
| B0 →5 |18/17|8/11|653|43,689s|24,494s|
| B1 →6 |21/20|13/15|478|34,051s|5,600s|
| B2 →7 |22/21|13/15|303|22,994s|1,950s|
| B3 →8 |28/27|13/16|443|45,153s|7,900s|

Alle acht zeigen nichtnull Sourcebewegungsaktionen und Sichtkontakte.139
SourcePickup-Zeilen in gebundenen Sourceleben sind erhalten,137 mit passendem
Native-Maskenwechselintervall; zwei ohne diesen Zeugen bleiben UNKNOWN. Kein
Itemcallback oder Aufnehmer wird ergänzt. Die Stillstandsmetrik erhält alle
kanonischen Reads, auch gleiche Simulationsticks: Ankersphäre≤1m, nicht fallende
Tickabstände≤0,5s. Reine deskriptive Auditmetrik, kein kontinuierlicher Beweis.
Die geerbte ALLSTREAM-Metrik bleibt separat und ist keine kanonische Lebensmessung.

## Neue Reacquire-Beobachtungen

871 Closed-Log-Zeilen sind einer eigenen Source-Entity/Generation zugeordnet.
852 haben ihr ganzes auf neun Dezimalstellen gedrucktes Nativezeitintervall
innerhalb des gebundenen beobachteten Lebens.19 Boundary-/Tail-Zeilen zählen
nicht als solche Gameplayereignisse.1Hz-Drosselung bedeutet keine Volltrace.

| Tatsächlicher Returngrund | Closed-Log vollständig | Innerhalb beobachtetem Leben |
| --- | ---: | ---: |
| `accepted_proposal` |326|322|
| `context_only` |375|362|
| `support_motion_guard` |110|109|
| `hints_exhausted` |29|29|
| `no_candidate_after_filters` |22|21|
| `support_geometry_rejected` |9|9|

Alle drei Hintplätze jeder Zeile bleiben erhalten:2178 `unattempted`,328 durch
bereits ausgeführte Casts `clear`,107 `blocked`;0 `probe_unknown` beobachtet.
Unversuchte Felder bleiben UNKNOWN. Keine Budgetdeferred-Zeile beobachtet;
wegen Drosselung ist das keine allgemeine Budgetfreiheit.9 verifizierte
Supportprüfungen enthalten auch die vorhandene Normale. Die neun Geometryreturns
haben Segmentlängen≈0,3m und Hitdistanzen0,392952–0,4m, außerhalb der unveränderten
0,25–0,30m-Grenze. Ihre Normalenauswertung wurde nicht erreicht: Default0 ist kein
Messwert.18 der22 `no_candidate_after_filters` stammen aus Aircontext; vier haben
weiterhin `local_point=1`. Keine pauschale Aussage „keine Navgeometrie“: vollständige
Triedbits-/Backoff-/Lockfiltergründe fehlen. Keine Guardaufweitung ist begründet.

## Lange NoUseful-Leben

Slot0/Generation13: Spawn115.95247650146484, lebend beobachtet116.05248260498047
bis168.3556671142578,52,303184509277344s bis beobachtetem Tod, Owned stets3.
Zielkette: Weapon8/Nav177 → Timeout; Weapon7/Nav208 → unavailable mit
`render_type`/Render5; Weapon12/Nav1 → unreachable; Weapon9/Nav0 → Tod.
Terminalzeilen protokollieren mehrfach178→177 mit wechselnden Höhen/Positionen,
keinen erfolgreichen Erwerb. Ursprüngliche Zieldeadlines bleiben erhalten.
Sieben lebensgebundene Decisions: drei Motionguards, zwei akzeptierte Vorschläge,
einmal erschöpfte Hints, einmal keine Kandidaten nach Filtern. Ein dauerhafter
Reacquireblock ist nicht belegt. Auch Slot2/Generation28 (49,988s) zeigt wiederholte
Weapon8-Terminalannäherungen178→177 bis Timeout. Die genaue Ursache der erfolglosen
Aufnahme ist hier nicht vollständig bestimmt.

Slot0/Generation29 berührt die frühere Kante129→248 erneut: `no_hop_progress`
beendet sie korrekt. Danach ist Hint129 tatsächlich LOS-blockiert, Hint132 clear/
accepted. Nativepositionen liegen später im ursprünglichen unverschobenen Radius
von132 (Native545.3403930664062). Bewegung aus dem Bereich ist beobachtet, aber
kein Waffenpickup in diesem46,739s-Leben; kein kausaler Fixbeweis gegenüber024.

Slot8/Generation12:45,153s NoUseful. Zwei direkt gebundene Supportgeometryreturns,
danach wiederholt gültige blocked-Casts für221/152/162 beziehungsweise153/222.
Acht Entscheidungen liegen in seiner7,900s-Episode geringer Ortsänderung.
Recovery-/Inputvorschläge liefern keinen belegten erfolgreichen Ausweg vor dem Tod.

Vollständiges Closed-Log:268 typedUnavailable-Zeilen, davon260 `render_type`,
sieben `missing_entity`,eine `typed_need`.265 liegen in Sourcegenerationen mit
Native-Lebensbindung, drei nur im weiteren Tail. Bei versteckten Waffen sind
Render5 und gültige Waffenmetadaten beobachtet. Aufnehmer und jederzeit tatsächlich
erreichbare Alternativen bleiben UNKNOWN; normale konkurrierende Aufnahme wird
nicht als KI-Defekt ausgegeben.

## Bewaffneter Stillstand: Proposal und finale Sicherheit getrennt

Slot5/Generation20, Spawn483.2555236816406:520.196533203125–544.6905517578125,
185 kanonische lebende Reads in der1m-Ankersphäre, Owned67,HP25,84 strikte
Fernfeueranforderungen.528.1445922851562–544.6905517578125:125 Reads mit exakt
gleicher Position/Nulltranslation,16,54595947265625s. Ein bewaffneter Stillstandsfall.

24 akzeptierte Reacquirevorschläge betreffen116/95/88, gemessene Höhen≈5m und
clear LOS; eine Zeile ist `hints_exhausted`. Im zugehörigen Sourceordnungsfenster
stehen16 MotionProbezeilen: neun primäre `WallHit`,sieben `UnsupportedNormal`.
Letzte Ablehnungsmetadaten zeigen unter anderem Wandnormal(−1,0,0) und Support
0,3976<0,5. Nur eine MotionProbezeile besitzt einen vorhandenen Nativezeitzeugen
am exakt gleichen SourceTick vollständig innerhalb der Episode; die übrigen sind
Sourceordnungs-/Lebenskontext. PlayerObserve zeigt nichtnull Input/Desired bei
Velocity0. Also reale Sicherheitsvetos und erfolglose Bewegung, aber keine
Call-ID-Verbindung jedes gedrosselten Proposals zur finalen Aktion desselben Calls.

Kleinster entscheidender Zusatz vor einem gezielten SDK-Reproducer wäre eine
aufrufgenaue Call-ID/Ownership-Verbindung Proposal → Arbitration → finaler
SafeMotion/Probe-Ausgang und die tatsächlich erreichten ContactFloor-Guards.
Kein pauschales Ignorieren von Wänden oder schwachen Bodennormalen. Nicht implementiert.

Ein lebensgebundenes GroundReplan (A0/Generation22):179→181 auf155, Ziel118 bleibt.
Vorheriger Stateanker155 und nachfolgender155 sind beobachtet, der neue stale-
anchor-Zweig somit nicht bewiesen. Am genauen Replantick fehlt ein vorhandener
Nativezeitzeuge. Außerdem13 Hopcheckpoints/sechs ItemTransitEnds; kein
ImportantOriginRecovery. Kein Zähler ersetzt Radiusankunft, Aufnahme oder Damage.

## Reproduktion und Grenzen

Eigener WT `/srv/tse-build026-skulls-closed-audit-20261115` ab `b28e972`. Nur dieser
neue öffentliche Bericht; private Reader/Receipts ohne veröffentlichte Rohidentitäten
oder Retailbytes. Skulls024-Reader mit dokumentierten Herkunfts-/Statuskonstanten
wiederverwendet. Keine048/018/020-Vergleichsraws oder komprimierten Red/Trouble gelesen.

```sh
nice -n 15 python3 -B .codex/evidence/skulls026/life-summary.py
nice -n 15 python3 -B .codex/evidence/skulls026/analyze.py
nice -n 15 python3 -B .codex/evidence/skulls026/decisions.py
nice -n 15 python3 -B .codex/evidence/skulls026/followup.py
```

Alle vier Schritte gehören zum Rezept, kein nachträglicher Metadatenfinalizer.
Private Vollquittung `final-receipt.json`, SHA256
`298253fda7c3b4f29cde23b8c3840a7b8a30d5ddb046b47c3f847cc080acb9cf`;
sie pinnt Reader/Eingaben/Closed-Logs/Quellverträge und verweist auf alle188 Leben/
871 Entscheidungen. LifeSummary-SHA256
`eae6f9e605cc3b95f88be3b09fc2e82bcfc3c963651e9e5610b1b6ad4a526756`;
Voll-Lebensquittung `bd1ee4370ace933890bbb6124c072cdf53b0a4df27d47a76fdbf23ef6c9da115`;
Decisionquittung `f02f38622448d7e9016b3728bdf2d6f3b4431bf00908340af75fd3ea045d46f5`.

Root meldete unabhängig640 Dateien/vier Closed-Logs samt PID-/Unit-/Display- und
Lockrestore PASS,0 neue Sync-/Disconnectfehler. Äußerer Hostobserver:688 Samples,
CPUmax63,265306%,RAMmin2470592512Bytes,Diskmin8774942720Bytes,max1,002606sLücke,
0 Verletzungen. Der innere Controller hatte eine48,967s-Startlücke und behauptet
keinen vollständigen Budgetpass. Kein Ersatz für formale1-/4-/8-Bot-Dauergates,
WAN-/Humanabnahme, vollständige Cecilparität oder A1-Erstzustandsschaden.

Der frühere242,491s-NoUseful-Fall tritt in diesem anderen Diagnosefenster nicht
erneut auf. Diagnostics1, andere Ereignisverläufe und ein einzelnes Fenster
liefern keinen Verbesserungs-/Regressionskausalbeweis oder Buildranking.
Keine Tests, Compiler, neuen Nativeprozesse, Fixes oder Harnessänderungen durch Audit.
