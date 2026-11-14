# Build022: geschlossene Healthphasenbeobachtung

Ein600s-RedStation-Fenster, gleicher20FPS-Observer: PASS_LIMITED bleibt
Beobachtungsstatus, kein A4-Abschluss. Quelle ist ausschließlich der geschlossene
Arm `nav20-022-root-redstation-20261114-205823`, Build022/DLL28028e44…;
keine alten komprimierten Vergleichsarme geöffnet und keine Tests/Runtime gestartet.

## Was die neue Phase tatsächlich tat

25periodische `health_connector_proposal=1`-Zeilen bilden12beobachtete
Itemversuche. Neun Zeilen in fünf Versuchen liegen klar außerhalb des originalen
Navradius. Dort bleibt `hop==goal`, `nav_travel=0`; alle25Zeilen melden
nach bestehender SafeMotion `floor=1` und positiven finalen `move` (0.10 oder1).
Die Zustandszeile folgt im tatsächlichen Driver auf Compose/Finiteprüfung und
`SetAction`. Das beweist den lokalen Vorschlags-/Emissionspfad, keine isolierte
serverseitige Verarbeitung dieses einzelnen Inputs. Positionen ändern sich;
die unabhängigen Servermemorybeobachtungen bestätigen ausgewählte Positionen,
Bewegung und HP, aber keine atomare Callback- oder kausale Einzelitemquittung.

| Rolle:Local / Generation | Item / Nav | Proposal-Ticks | Außerhalb / Radius | Folgendes Goalende |
| --- | --- | --- | --- | --- |
| A:2 /6 |368 /60 |1520–1540 |0 /3m |unavailable1542 |
| A:1 /11 |293 /53 |5940–5960 |2 /2m (7.16–7.72m) |unavailable5973 |
| A:3 /26 |286 /55 |11100–11120 |2 /2m (3.65–4.72m) |unavailable11131 |
| A:2 /31 |347 /95 |12040–12080 |0 /10m |unavailable12097 |
| B:2 /6 |345 /66 |540–560 |0 /3m |unavailable561 |
| B:1 /12 |285 /55 |1940–2000 |3 /2m (6.11–7.77m) |unavailable2004 |
| B:1 /15 |347 /95 |4400 |0 /10m |death4416 |
| B:2 /16 |259 /181 |5220 |0 /2m |unavailable5224 |
| B:2 /16 |286 /55 |5860–5880 |1 /2m (3.90m) |unavailable5883 |
| B:2 /16 |287 /55 |5900–5920 |1 /2m (4.71m) |death5930 |
| B:3 /22 |347 /95 |8080–8120 |0 /10m |unavailable8130 |
| B:3 /25 |345 /66 |10620 |0 /3m |unavailable10625 |

Besonders B:1/12 zeigt dieselbe gewöhnliche Nav55→Health285-Geometrie wie
der SDK107-Reproducer: von(-51.651,-5.992,-7.255) beiTick1940 innerhalbRadius2
zu(-53.257,-5.992,-11.666) bei1960 und(-49.899,-5.992,-12.301) bei2000
bleibt der Itemconnector aktiv. Source-HP bleibt41; tatsächlicher Heilerfolg ist
für diesen Versuch nicht belegt. Der frühere beobachtete40→41-Anstieg erfolgte
bereits vor der Auswahl dieses Items und wird ihm nicht zugeschrieben.

Tatsächliche positive HPänderungen sind getrennt belegt, beispielsweise:

- A:1/11: Serverreadserial6754→6757, GameTime289.502838→289.652802,
  HP74→75 beiPosition(-51.800,-5.998,36.548), naheZiel293. Letzte
  außerhalbRadius geloggte Proposal5960 entspricht einer beobachteten
  Serverposition bei288.952972. Danach beendet sich Goal293 als unavailable.
- A:3/26: serial12649→12652,547.339905→547.439880, HP10.808090→11.808090,
  Position(-50.024,-5.998,-2.567), naheZiel286; danach Sourcegoal gewechselt.
- B:2/16: serial6821→6824,292.352142→292.502106, HP1.565918→2.565918,
  Position(-50.715,-5.999,-2.121), naheZiel286. Der nachfolgende Goal287-Versuch
  beginnt bereits mit dem erhöhten HPwert; derselbe HPanstieg wird nicht doppelt gezählt.

Diese Anstiege zeigen reale Heilung im Umfeld ausgeübter Connectorphasen,
beweisen ohne Itemevent-/Pickupquittung jedoch keine exklusive Zuordnung zum
jeweiligen Ziel. `unavailable` allein bedeutet keinen Pickup. Sparse
WeaponObserver-Clockwerte können Zielgrenzen weit einklammern oder einen Rand
vermissen; breite Kontextfenster sind privat ausdrücklich markiert und keine
Goal-/Pickupbeweise. Policytick/20 wird niemals als NativeGameTime eingesetzt.
Die25Zeilen sind sparse Momentaufnahmen, keine vollständige Phasenhistorie.

## Separate offene A4-Lücke: gesperrter Ausgangsanker

A:0 hat während des GESAMTEN Arms keine aktive Healthproposal; weder das späte
lange unbewaffnete Leben (Generation27) noch die frühe Stationarität überlappt
mit der Healthphase. Die bisherige Root-Allstreammetrik9.999847s bleibt erhalten;
kanonische BotA-Gruppe allein ergibt39.549683→49.399532=9.849850s mit anderer
Beobachtungsmenge. Beide beschreiben dieselbe frühe räumliche Episode.

Source-Ticks980–1160/Generation5: Position(63.150,.381,-79.827), move/strafe0,
floor1,nav1,hop−1, zunächstgewöhnlichesGoal15 ohne Item, anschließendGoal182
mit Armor260 (kind3). Beide Navpunkte habenFlags0,important/lock/next−1;
Nav182 ist Slot182/stabileID184 und darf nicht als Slot184 gelesen werden.
Unmittelbar davor endet bei968 die Interaktion anNav138/importantEntity401 mit
`not_usable`. Nav138 liegt(63,1,-75), Radius2; der Bot steht danach≈4.87m entfernt.

Der tatsächliche Code liefert einen engen, stark gestützten Mechanismus:
`BotCecilFinishImportant` (BotSupplyNative.h1080–1088) setzt ohne Nextslot
avoidNode138 bis now+10. `BotCecilLocks` (537–563) sperrt diesen Knoten, solange
kein importantGoal anliegt. `CecilNavigator.Update` (cecil_motion.h121–123)
verweigert den gesperrten Ausgangsanker außerhalb seiner Ankunftsgeometrie und
liefert hop−1/neutral. Beobachtetes Warten bis1160 und erneute Bewegung bei1180
passen zum unveränderten10s-Policyintervall nach968. Der konkrete blocked-/avoid-
Zweig ist nativ nicht direkt geloggt; ein echter SDK107-Reproducer ist erforderlich,
bevor ein Fix entschieden wird. Dies ist kein Healthregressionsnachweis und kein
belegtes legitimes Lock-/Powerup-/Kampfwarten. In dieser Episode vis0,target−1,
owned15,current/wantedKnife1,fire0,shots109konstant; kein MotionProbe-Reject
für A:0 im fraglichen Abschnitt. Eine physische Safetyverweigerung ist unbelegt.
Eine volle verhaltenstreue ursprüngliche Cecil-Parität wird hier nicht behauptet.

Private vollständige Zeilen-/Entity-/Generation-/Item-/Hop-/Position-/HPquittung:
`.codex/evidence/health022/closed-review.json` im Reviewworktree, SHA
`367483263d3a3acab06735821ea4e5756529909e49873f088c3c0cced5180725`. Analysequellen/Versionen und Rohbelegpins sind darin enthalten.
Keine privaten Spieleridentitäten oder Retaildaten werden veröffentlicht.
