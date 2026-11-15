# Ein Reset-Diagnosefenster: Picker → Erreichbarkeit → Arbitration

Nur Quellenplan, kein Implementierungs-/Nativeauftrag. Ausgangspunkt ist
Build030, Quellcommit `7aedcdb21f7180b9abfeed2ea9e8bbbf5553564e`, privater Baum
`/srv/tse-milestone-a-build-030-20261115/Sources/Game/`. Dessen Manifest nennt
BotSupplyNative.h `777d196e44d21dc8ac1e5b0cce8fb54247833d7665ef9329ca64f50d97676504`,
BotDriver.cpp `7af47d87aaaf4c51ebaca6f65d628cfec3c2544419be07e39b65e52b370eb386`.
Das sind hier gelesene Manifestpins, kein erneuter vollständiger Closure-Scan.
Das tatsächliche Resetdefizit (Phase1 botA:1 fünf Leben ohne Useful) wird nicht
aus der Quellenhypothese erklärt oder als bestanden umetikettiert.

## Vorhandene Rohbelege und genaue Lücken

* Header 771–850: `CecilSupplyDiagCandidate/Selection/Connector` bezeugen den
  **mapped** Erstwaffen-Fallback einschließlich Kosten, vorhandener Ownerquittung,
  Auswahlversuchen und tatsächlichem Connector. Sie instrumentieren nicht den
  vorgeschalteten normalen Picker. Die Returns 773–775 liegen vor diagDue:
  kein Goal-/Cooldown-/Enemy-/Search-/HasRanged-Negativbeleg aus fehlender Zeile.
* Header 851–897: normaler Picker; stille erste Anchorakquisition, 8192er
  Entityscan/128er Snapshot, ReadItem-/Rejection-/128-Distanz-/Nahkampffilter,
  `CecilChooseItem`, Sichtprobe und Item-Nearest/direkte Pfaddistanz. `CecilGoal`
  bezeugt nur erfolgreichen Commit. Fehlende Goalzeile beweist keinen dieser
  konkreten Ablehnungsgründe. `cecil_rules.h` 288–343 trennt typed need,
  erlaubte Waffen, Sicht-/Reachabilitybits, Suchradius und Gegnerdistanz.
* Header 661–675/1857–1884: `Unavailable` betrifft bereits gehaltenes Ziel,
  mit tatsächlichem ReadItem-Grund oder `typed_need`, PickedMask/Hidden usw.
  Header 1905–1909 liest ein frisch gewähltes Ziel erneut; diese zweite
  `unavailable`-Stelle hat bisher keinen solchen Reasonbeleg. 1Hz-Throttling
  bleibt eine Messgrenze, keine vollständige Ereignisliste.
* Header 550–581: `BotSupplyNearest` gibt bei keinem geometrischen Kandidaten,
  erfolgloser bestehender Probe oder aufgebrauchtem Budget jeweils -1 zurück.
  Vorhandenes ReacquireDecision (975–1040) bezeugt einen anderen Recoverypfad;
  dessen Hints/Support dürfen nicht zur normalen Nearest-Abfrage umgedeutet werden.
* Driver 1453–1477 und `driver_final_decision.h`: vorhandenes DriverFinalV1
  enthält echte Supplyproposalbits, tatsächlich ausgewertete Waffenpräsenz,
  Arbitration, SafeMotion und Submit. Es ist nur tick%20 zugelassen; der Scan
  läuft ab spawnabhängigem scanTick, deshalb nicht zwingend am selben Tick wie
  ein Pickercommit. Eine spätere Zeile schließt diese Same-call-Lücke nicht.

## Kleinste prospektive passive Ergänzung, vor dem einzigen Fenster

Neue DIAG1-only feste Scalarquittung, kein Gameplayfix. Rootreview/SDK-Nachweis
und ein neuer Build wären erforderlich; keine bestehenden Build030-Pakete ändern.
Kein zusätzlicher Enginegetter, Entitylookup, Cast, Dijkstra/Nearest, RNG, Input
oder anderer Simulations-/Goal-/Radius-/Budget-/Deadlinezustand. Keine erneute
Auswertung einer vorher kurzgeschlossenen Bedingung für das Protokoll.

1. **Pickerentscheidung am tatsächlichen Aufruf.** Local/tick, vorhandenes
   actor/generation, entry/exit anchor/goal/item, searchAfter/goalSince/deadline,
   scan/follow/flight-Kontext und ausgewertete Guardbitmap+erster Returngrund.
   Gemeinsame Inputs nur kopieren, wenn der Originalpfad sie schon erzeugte:
   owned/usable/HP/armor/enemy_distance, Search/Visibility/AllowedWeapons und
   Suchradien. Bei Anchor-return bleiben spätere Inputs ausdrücklich unbekannt.
   `BotCecilReadItem` kann seinen vorhandenen optionalen Reasonausgang beim
   **gleichen** Aufruf füllen; kein zweiter Read. Scan-Zähler/Snapshotgrenze und
   aggregierte echte Ausschlusszähler, keine Behauptung eines vollständigen
   Kandidatenpools aus einer begrenzten Detailausgabe. Nach bestehendem
   `CecilChooseItem` dessen tatsächlichen Index und das gewählte Snapshotitem
   kopieren; typisierte Feindistanz-/Rankinggründe ggf. offline aus genau diesen
   Inputs, nie aus späteren Spielerwerten berechnen.
2. **Höchstens acht bestehende Versuche.** Itemid/kind/weapon, ausgewertete
   Branchbitmap, Budget vorher/nachher, tatsächliche Visibilityresultate,
   tatsächlicher Nearest-Rückgabewert und die ohnehin geprüfte gerichtete
   Pfaddistanz/Finitebit; Commit/Reject/Deferred mit Originalgrund unterscheiden.
   Für die maximal drei Nearest-Hints nur bereits berechnete slots/distances und
   Resultate der ohnehin aufgerufenen Clear-Proben kopieren. `validProbe` am
   vorhandenen Clear-Aufruf darf nur vorhandene Wahrheitswerte ausgeben:
   false bedeutet UNKNOWN/unvollständig, nicht automatisch blocked. Geometry
   ohne Hint, Budgetveto, ungültige Probe, tatsächliches blocked/clear und
   leerer Segmentfall werden getrennt. Keine zusätzliche SCecilSupplyCastDetail-
   Hitmetadatenabfrage einführen: dessen GetRenderType/GetPhysicsFlags wären
   bei normalen bisherigen Aufrufen zusätzliche Enginecalls.
3. **Commit bis Arbitration am selben Tick.** Die neue Quittung muss die echte
   Supplyrückgabe plus die tatsächlich ausgewerteten Lazy-Guardoperanden von
   Driver1453–1477 bis zur unveränderten finalen Action erhalten. Supply gewählt,
   sichtbarer Kampf übernimmt, Traversal/UseControl oder urgentes Item werden
   durch tatsächlichen Branch bezeugt; bloßes vis/goal aus späterem CecilState
   genügt nicht. Bestehende DriverFinal-Ausgaben wiederverwenden, aber für einen
   zugelassenen Pickerbatch auch den betreffenden Tick bezeugen, ohne vorzeitig
   zusätzliche Player-/Waffenreads oder neue Arbitrationauswertung. Sonst bleibt
   Arbitration UNKNOWN und der neue Messvertrag wäre nicht erfüllt. Submit ist
   weiterhin kein ACK-/Physicsbeweis. Zweiten ReadItem-Return1905–1909 mit seinem
   bereits ermittelten Reason an dieselbe Quittung binden.

Feste Speicher-/Ausgabeschranken: höchstens ein vollständiger Pickerbatch je
Bot/Quellsekunde (1Hz), maximal acht Attemptrecords plus eine Summary;
je Attempt maximal drei Hintresultate. Vorgeschlagen maximal 1024 Byte pro
Attempt und Summary, also maximal 9216 neue Pickerbytes/Batch plus höchstens
2048 Byte für eine zusätzlich zugelassene vorhandene DriverFinal-Zeile. Diese
Schranke kommt zur bereits bestehenden DIAG1-Ausgabe hinzu, nicht an deren Stelle.
Tatsächlichen Formatworstcase
im SDK beweisen, kein stiller Truncationserfolg. Ein unterdrückter Batch oder
unbekannter Wert bleibt als solcher sichtbar. Logger/diagnostische Clocks dürfen
keine Entscheidung speisen. DIAG1-Overhead ist neue Messbedingung.

## Offline-Nachweis vor Rootfreigabe

Echter vorhandener SDK107-Body/Harness, keine Algorithmusnachbildung. Zuerst
Behavior-RED: normaler erreichbarer Goalcommit bzw. normale LOS-/Budgetablehnung
haben im Parent keine getypte Same-call-Pickerquittung, mapped dagegen schon.
Dann Paare DIAG0/DIAG1: identische Zustände, Aktionen, Engine-/Ray-/RNG-Abfragen
und Callreihenfolge; nur Text und diagnostische Speicherung dürfen differieren.
Adversarien: alle tatsächlich frühen Guards, Snapshotlimit, ReadItem-Ausfälle,
fehlender Entity, clear/blocked/unknown/empty, Nearest ohne Geometrie versus
fehlendes Raybudget, endliche/unendliche Pfaddistanz, Attempt8, Goalverlust im
zweiten Read, Ownerquittung unbekannt versus qualifiziert, Reset/Death/rejoin,
Same-tick-Arbitration beider Pfade, Lazy-Guard-Auswertungsbitmap und Formatlimit.
Whole-body-Inversen/alle bisherigen produktiven Guards bleiben nachweisbar.

## Genau ein zukünftiges Rootfenster

Nach separater Source-/Pin-/Build-/Freezereview **ein** privater Resetfall auf
Red Station→Red Station→Red Station, bestehendes 480s-Cap/2 echte normale
Rundenwechsel/2-2-0-Minutenregeln/Hard2/acht DEMON3 plus unveränderten Original.
FPS wie tatsächlicher Reset030-Parent (Original30/30), keine Übertragung aus
Nav20. Nur DIAG1 und die passive neue Quittung sind neue Bedingungen. Alle
bestehenden Ressourcen-, Query-, Epoch-/Life-, Error-, Close-/Restoregrenzen
unverändert; kein automatischer Retry, keine zusätzliche Abnahmeschleife.

Alle acht Slots/alle drei Epochen separat als Nenner. Local→Process/PIDstart→
Registry→actor/generation→SourceSpawn/WPO→NativeLife strikt verbinden; Source-
tick nicht durch Division in Nativezeit übersetzen. V3-Readserial/Attempts und
Zensierung bleiben unverändert. Für jedes lange NoUseful-Leben: tatsächlicher
Pickerreturn → Kandidat/Reachabilityversuch → Goal/Endgrund → gleichzeitige
Arbitration → beobachtete Position/echter Inventargewinn. Distanz allein belegt
keine Erreichbarkeit, Proposal keine Bewegung, Frags keinen Pickup.

Widerlegung ist möglich: erreichbare klare Waffenwahl mit tatsächlich
übernommener Versorgung, aber ohne Annäherung/Gain zeigt auf einen späteren
Pfad; ausschließlich belegte Filter-/Budget-/Geometrieveto ohne Commit zeigt auf
die jeweilige Akquisition; expliziter Combat-Branch mit vorhandenem Itemproposal
trennt Arbitration. Legitime konkurrierende Aufnahme ist von Pickerfehlern
getrennt zu halten. Reproduziert sich das Defizit nicht oder fehlt die genaue
Kustodie, lautet das Ergebnis UNKNOWN/Beobachtung, nicht Fix oder A4-PASS.
Alte Reset030-FAILs bleiben bestehen; kein Ranking, keine Promotion, A offen/B
nicht begonnen. Danach Rootentscheid aufgrund der echten Ursache, kein weiterer
automatischer Lauf.
