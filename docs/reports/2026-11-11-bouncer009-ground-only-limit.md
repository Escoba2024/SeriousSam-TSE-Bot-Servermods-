# Build009: erster Sprung unterdrückt, späterer Anflug weiter ohne Padkontakt

Das vollständig geschlossene Fenster `arena009hook2-checked-swap1-trial-1-230743` bestätigt die Ausführung der engen Bodenregel, aber keinen erfolgreichen Bouncer234-Anflug. Beobachtungsdauer120,0395s, vier Rollen geschlossen, errors leer und alle vier Logs ohne SYNCBAD/Disconnect. Der Hook war über das gesamte120037,5ms-Fenster installiert:0 passende234-Aufrufe,46 andere Padaufrufe,0 unzugeordnete Spieler,0 Fehler/Verluste; Detach und Originalkörper-Wiederherstellung sind protokolliert. Dies ist beobachtete Listener-Abdeckung und kein Beweis vollständiger Spielereigniserfassung.

Die [JSON-Beilage](2026-11-11-bouncer009-ground-only-limit.json) enthält Quellhashes und die15 echten aufeinanderfolgenden Diagnoseaktionen. Kandidat009 ist hier physisch botA. Tatsächliche Attachzeile200 ordnet local2 dem globalen Slot3 zu; Diagnoseentity567/generation5 bestätigt die Identität. Messgruppenlabels werden hierfür nicht verwendet.

| Tick | Tatsächlicher Befund | BotA-Logzeile |
|---|---|---:|
|1368|Update7→8 nach8→12; Roh-UP1, finale Action-UP0, Support54. Bodenregel wirkt.|1494|
|1370–1372|Weiter8→12; Support0, weiterhin State0/STAND; UP0.|1497–1499|
|1373|Gleiche Kante; Roh-UP1 und finale Action-UP11 bei Support0/STAND.|1500|
|1374|Support193, vertikale Geschwindigkeit−2,318; aktuelle Action-UP0.|1501|
|1375|Support0, vertikale Geschwindigkeit+14,300; aktuelle Action-UP0.|1502|
|1378|Erneut finale Action-UP11 bei Support0, gleicher8→12-Anflug.|1505|
|1381|Reichweitenentscheidung erreicht12 und schaltet nach34, während Support0 und Höhe2,9375 über Knoten12 liegen.|1513|

Goalentity243 und ursprüngliche Deadline73,235883 bleiben über diese15 Aktionen gleich. Das zeitlich versetzte erneute UP-Kommando vor dem beobachteten Kontakt ist eine konkrete Lücke der nur bei vorhandener Bodenreferenz wirkenden009-Unterdrückung. Die Reihenfolge passt zu nachgelagerter normaler Action-/Physikausführung; sie allein ist kein instrumentierter Beweis, welche Engine-Instruktion die spätere Geschwindigkeit setzt. Sie belegt insbesondere keine entfernte Supportprüfung im Original-Bouncer: dessen234-Funktion wurde gar nicht passend aufgerufen.

Es gibt drei begrenzte Diagnosefenster mit je120 Zeilen: local0/g6 beginnt bereits12→34 bei967, local1/g6 ebenfalls12→34 bei1031, local2/g5 enthält den vollständigen oben gezeigten Übergang ab1368. Die ersten beiden Fenster besitzen hier keine zuvor erfasste8→12-Umschaltaktion. Die begrenzte Diagnose ist kein vollständiger Nenner aller möglichen Anflüge oder Leben. Aus0 Padaufrufen darf kein allgemeiner Defekt sämtlicher Kanten abgeleitet werden.

Ein möglicher010-Fix wird separat überprüft und benötigt eigene Native-Abnahme.009 erhält hier keine Gameplay-Erfolgsfreigabe; Radius-/Zielankunft und erfolgreiche Minigunaufnahme bleiben für diesen konkreten Anflug unbelegt. Analyse ausschließlich aus abgeschlossenen Artefakten, ohne Runtimezugriff oder Quelländerung.


## Ergänzung: tatsächliche Herkunft der anderen beiden Anflüge

Die Herkunft bleibt nicht allein wegen des begrenzten Diagnosefensters unbekannt: frühere periodische CecilState-Zeilen belegen bei local0/g6 die Folge9→10→11 und bei Tick960 bereits11→12 mit Support194 (Zeile910). Local1/g6 folgt ebenfalls9→10→11; bei1020 noch10→11 mit Support194 (Zeile1020), bei1031 erstmals dicht protokolliert bereits12→34. Für beide spricht damit konkrete Routenevidenz gegen eine Herkunft über8→12.

Native Inventarmessungen bestätigen bei denselben Entity-IDs und jeweils zweitem Leben den frühen Aufstieg:565 steigt zwischen Spieltick38,94969 (vY2,28076, Support vorhanden) und39,09969 (vY16,82647, Support0) deutlich auf.566 zeigt zwischen42,19964 (vY2,28076, Support vorhanden) und42,34964 (vY15,32647, Support0) dieselbe Art Bewegungsübergang. Die Beilage enthält die vorausgehenden und nachfolgenden Proben einschließlich Lebenszeitbezug. Native Sessionzeit und BotDriver-Tickzeit sind verschiedene Uhren und wurden nicht ungeprüft gleichgesetzt.

Diese Befunde belegen zwei weitere tatsächliche Fehlanflüge ohne passenden234-Aufruf und einen vorherigen Aufwärtsimpuls. Die verursachende finale UP-Aktion am11→12-Übergang fehlt jedoch in der dichten Aufzeichnung. Eine identische Ursache wie bei local2 ist damit plausibel, aber nicht bewiesen; daraus folgt keine genehmigte11→12-Verhaltensregel.

Der kleinste zusätzliche Discriminator ist im ohnehin anstehenden010-Test ein früherer **rein diagnostischer** Start des vorhandenen Approachfensters für11→12, einschließlich des vorigen Hops11. Die bestehenden Felder Roh-UP, finale Action, Support und ursprüngliches Update reichen zur Unterscheidung aus. Zusätzliche Hooks, Rays oder eine vorweggenommene Gameplayregel sind dafür nicht erforderlich.
