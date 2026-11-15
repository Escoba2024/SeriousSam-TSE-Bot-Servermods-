# Reset031: 24 aktive Slotphasen, Versorgung weiterhin unvollständig

Der geschlossene Fall `a4-reset031-diag1-v3-root-20261115-130242` bestätigt die bestehenden24 Aktivitätsgates, erklärt aber keine vollständige A4-Abnahme. Der Originalstatus bleibt `PASS_LIMITED_BOT_RESET_FRESH_OBSERVER_REVIEW_REQUIRED`, Result-SHA `848c701b029969d4431b92a39add588eabd0bfac7fc68271ec4b7200fd136fc0`. Drei RedStation-Phasen/zwei normale Resets wurden in425,430967s beobachtet; Hard2/8DEMON3/Original30FPS/diag1, Build031-DLL `5c5c21d651f5513bcba4c1c3cc8ddc6495fbfbe7cdbbee506c70853bd15bbb0b`. Gameplayquellen wurden hierfür nicht geändert. Die früheren030-/024-Fehler bleiben bestehen; das unterschiedliche Diagnosefenster ist kein kausaler Verbesserungsvergleich.

Root bestätigte643Dateien/5Absenzen/beide Namespaces/vier normale Closes und ruhende Rollen/Units/Displays/Sperren. Der unabhängige geschlossene Audit hashte zusätzlich alle vier finalen Logs:0SYNCBAD und0Too-many-bad-syncs-Meldungen. Das ersetzt nicht Root's Restorezeitpunkt/-umfang.

## Unveränderter Nenner

Die gepinnten ResetV3-/Epoch-/Attempt-/Decimal-/Lifehelper wurden wiederverwendet.5251 Messversuche enthalten128 tatsächliche verworfene Reads.5120 erfolgreiche Gameplayframes und drei getrennte Smokeproben bleiben erhalten; kanonische Botgruppen und Overlap werden weiterhin getrennt behandelt. Frühe `early-botA/B`-Hüllen werden als ihre tatsächlichen gebundenen Gameplaygruppen validiert.

|Phase|Leben|links/rechts zensiert|Tod beobachtet|Usefulbesitz-Leben|echte Inventargewinne|
|---|---:|---:|---:|---:|---:|
|0|48|42/8|40|18|23|
|1|49|35/7|42|21|24|
|2|48|41/7|41|24|28|

Insgesamt145Leben,63 mit beobachtetem Usefulbesitz und75 echte Inventargewinne. Zwei Leben haben widersprüchliche positive Nach-Tod-Proben; der Lebenshelper verlängert daraus keine Alivezeit. Zwei weitere Leben wurden nur als Leiche beobachtet. Nichtbeobachtete Übergänge bleiben unbekannt.

Alle24 Slotphasen, jeweils kanonischer Nenner. FIRE bedeutet strikt gebundenes sampled Native-Ranged-FIREflag mit Same-Life-Sourcecountergrowth; kein Waffenfunktions-, Treffer- oder Schaden-ACK.

|Phase|lokal|global|Leben|Usefulbesitz|Gains|FIREflag|
|---|---|---:|---:|---:|---:|---:|
|0|A:0|0|9|2|2|14|
|0|A:1|2|6|1|2|31|
|0|A:2|3|6|3|4|38|
|0|A:3|4|7|3|4|109|
|0|B:0|5|5|3|5|59|
|0|B:1|6|2|1|1|286|
|0|B:2|7|7|4|4|89|
|0|B:3|8|6|1|1|2|
|1|A:0|1|8|4|3|69|
|1|A:1|3|5|4|6|87|
|1|A:2|5|4|2|2|48|
|1|A:3|7|7|2|3|36|
|1|B:0|0|9|2|2|2|
|1|B:1|2|2|2|3|148|
|1|B:2|4|6|2|2|20|
|1|B:3|6|8|3|3|45|
|2|A:0|0|5|4|4|110|
|2|A:1|1|7|3|3|29|
|2|A:2|3|6|3|4|48|
|2|A:3|4|7|3|3|10|
|2|B:0|2|6|3|4|83|
|2|B:1|5|7|2|4|81|
|2|B:2|6|5|4|4|27|
|2|B:3|7|5|2|2|2|

## Vollständige neue Custodyzählung

Die beiden gesamten geschlossenen Botlogs enthalten3044 Decision-,3044 Origin-,1356 Attempt- und3044 Arbitrationzeilen. Alle vier Schemas wurden strikt auf vollständige Felder, Typen/Tuplelängen, Known/Truth-Bitmaps, maximal acht lückenlose Attempts und drei Hintslots geprüft. Kein Formatfault, Overflow oder fehlender deklarierter Attempt.23,998649MB eindeutige Sourceeingaben wurden berücksichtigt; die tatsächlichen Autorleseoperationen mit dem erklärten zusätzlichen Closed-Logpass umfassen36,549211MB, unter dem vorab festgelegten64MiB-Gesamtbudget und32MiB je Log. Keine alten Fälle wurden erneut ausgewertet.

2667 Batches liegen in den tatsächlichen archivierten Gameplayphasen.377 weitere Batches aus Bootstrap/Endpause/Tail bleiben vollständig gezählt, aber UNKNOWN für Nativegameplay.2651 aktive Batches besitzen eine eindeutige Sourcegeneration→Native-Spawn-Bindung mit vorhandenem SourceSpawn;16 bleiben UNKNOWN.2218 haben zusätzlich ein vollständig enthaltenes WPO-Zeitintervall. Keine Tick/20-Interpolation oder RotationBaseline-Respawnannahme wird verwendet. Die1Hz-Drosselung ist keine vollständige Pickeraufrufliste.

Von1124 aktiven Attempts sind952 `no_choice`,73 `committed`,75 `visibility`,23 `no_hint_or_probe` und einer `unreachable_path`. Die75 Visibilityablehnungen besitzen tatsächlich ProbeCode5, nicht bloß ein UNKNOWN/FALSE. Der einzelne Dijkstrapfad ist `pathKnown=1,inf`; dessen Rohtext bleibt erhalten und wird nicht als malformierte oder berechenbare Geometrie behandelt. Nichtausgeführte ProbeCode0-Hints bleiben UNKNOWN.

## Längstes NoUseful-Leben: kein no_anchor-Mehrheitsfall

Phase0 A:1/global2, Native-Spawn0,9000001549720764:313 gültige Aliveproben von0,9500001668930054 bis50,349517822265625, also49,399517655s ohne Usefulbesitz. Alle313 besitzen ausschließlich Mask3;246 zeigen Knife1,67 Colt2. Die native Bewegung ist groß:783,110m direkte beobachtete Positionschords bei unverändertem0,5s-Gaplimit, maximal0,950004s innerhalb der1m-Stationaritätssphäre. Das ist keine tatsächliche integrierte Weglänge oder durchgängige Route.

Die46 admittierten Batches sind sämtlich `normal_done`, keiner `no_anchor`. In40 stoppt der Normalpicker bereits an vorhandenem Itemziel (`gates=(1,0)`); die gemappte Suche stoppt entsprechend am bestehenden Ziel (`mapped=(1,1)`). Sechs tatsächliche normale Scans enthalten zusammen2644 Readversuche,2368 Readablehnungen,210 entfernte Items und61 `CecilChooseItem(single)`-Filter; kein Rejectcache-/Close-enemy-Filter. Vier Scans finden keine normale Wahl, zwei committen Health. Ein vorhandenes Ziel ist hier keine neu bewiesene Blockade; die Sourcebelege zeigen tatsächliches Retainverhalten.

Alle46 Eingaben haben owned/usable3/3, ItemSearch/Visibility aktiviert, AllowedWeapons−1 und Radien Weapon16/Health32/Armor16/Ammo16. Enemy ist45-mal1000 und einmal6,5431; letzteres verursacht in den sechs beobachteten Scans keinen Closefilter. Die61 Singlefilter besitzen keine individuelle Kandidaten-ID/-Ablehnungsursache. Daraus lässt sich keine bessere erreichbare normale Waffe konstruieren.

Die gemappte Waffenkette ist544/W9→248/W11→243/W7→267/W12→248/W11. Die vier abgeschlossenen Waffenziele enden ausdrücklich `unavailable`, jeweils mit `render_type`/Render5. Ein Timeout oder unendliche Replanfreigabe ist damit nicht belegt. Wer das Item aufgenommen oder dessen Darstellung geändert hat, ist UNKNOWN.

Vorhandene DIAG1-Mapped-Custody macht die beobachteten Auswahlzeitpunkte genauer: SourceTick200 enthält sechs vollständig emittierte gültige Kandidaten; W9 hat den kleinsten protokollierten Score196,548788. Tick395 besitzt drei Kandidaten, gewählt W11;421 nur W7;908 keinen;928 nur den bereits von lokalem Peer0 qualifiziert verfolgten W12;1100 zwei, gewählt W11. Alle fünf tatsächlichen gemappten Connectorprüfungen sind valid/clear. Die Wahl des einzigen contestedW12 bei928 ist gerade der bestehende Fallback und keine pauschale Sperre. Ein Counterfactual, dass die Präferenz diesen langen Zustand verursacht habe, ist dadurch nicht bewiesen.

Die zwei admittierten normalen Healthcommits368/345 besitzen tatsächlich Probe6(clear), gewählte Nearestpunkte60/66 und endliche Pfadkosten6,731456/12,769968. Weitere Healthziele369/370 entstehen zwischen den1Hz-Batches. Alle vier enden später `render_type`/Render5. Vier native+10HP-Übergänge25→35→45→55→65 sind beobachtet; eine exakte Item-Pickupfunktionszuordnung fehlt. Healthproposal, HP-Zunahme und spezifischer Itempickup werden daher getrennt ausgewiesen.

Same-call Supplyarbitration wird45-mal genommen. Beim einzigen anderen Batch1028 ist Gate1 (`supply.active||ownsMovement`) falsch, weitere Gates nicht ausgewertet; dennoch liegt ein anderer nichtneutraler endgültiger Submit vor. Kein belegter Ziel-Sichtkontakt-/Combatveto wird daraus erfunden. Alle46 Submits bleiben von tatsächlichem Bewegungs-ACK und Itemaufnahme getrennt.

## Weitere Grenzen und Reproduzierbarkeit

Weitere lange NoUseful-Alivefenster sind31,451920s (Phase1 B:0),29,649570s (Phase2 A:1),25,701569s (Phase1 B:2),25,251534s (Phase2 B:1) und25,099617s (Phase2 B:3). Alle145 Leben, Zensierungen und24 Slotphasen stehen privat. Das größte kanonische1m-Stationaritätsfenster beträgt1,950119s; exakt gleiche Position plus ausschließlich Nulltranslation höchstens1,800110s. Beobachtungslücken bleiben erhalten; ein physikalischer Dauerstillstand oder eine kontinuierliche Schleife wird nicht behauptet.

Der erste zusätzliche Readercheck setzte Decision.refresh fälschlich dem späteren Arbitration.refresh gleich. Der tatsächliche Sourcepfad aktualisiert den Goalrefresh dazwischen. Dieser Fehlreader ist dokumentiert; beide Werte bleiben getrennt. Alle Inventarframes sowie Phase0 wurden im Offline-RAM gehalten, daher kein zweiter Inventarread. Zusätzlich wurde ein portabler Readerfehler durch echtes RED korrigiert: eine nichtneutrale Anfangsprobe darf keine Nulltranslationsdauer eröffnen. Kanonische Geometrie steht abschließend in `canonical-final-receipt-v2.json`; frühere Checkpointdateien sind nicht deren Ersatz. Ein kopierter Skalarzähler des RAM-Fortsetzungsframes war veraltet; tatsächliche IO-Zähler und eindeutige Inputgrößen sind im Erratum getrennt berichtigt.

Parser-RED: der alte tatsächliche Sourcefilter verwirft alle vier neuen Tags, insgesamt fünf Assertionsfehler. Abschließend sieben fokussierte Parser-/Batch-/Nonfinite-/Geometriechecks PASS0,026s. Keine Engine-/Runtime-/DLL-/Navänderung, keine neue Nativeprobe.

Neue öffentliche Quellen: `tools/picker_custody_audit.py`, `tools/audit_reset031_picker_closed.py`, `tools/test_picker_custody_audit.py`. Reproduktion liest ausschließlich den exakt gepinnten geschlossenen Fall und verlangt ein frisches privates Ziel (`OUT`); keine Runtimecontrollerimporte oder zusätzlichen Eingaben. Private Vollbelege liegen unter `/srv/tse-reset031-picker-closed-audit-evidence-20261115`, insgesamt4,372MB, mit5MiB-Kappe und8GiB+64MiB-Reserve vor jedem Write. Finaler kanonischer Receipt-SHA: `d14c561071ee738469871b64394e140105da606f7a117a77d74b6a31b254b201`.

Eine bessere alternative Waffenroute, der genaue Verursacher der Item-Unavailability und lückenlose Entscheidungen während der1Hz-Lücken bleiben unbelegt. Der Fall liefert keinen hinreichenden Ursachenbeleg für eine Verhaltensänderung oder weitere blinde Nativewiederholung. A bleibt offen; B ist nicht begonnen.
