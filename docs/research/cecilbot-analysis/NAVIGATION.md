# Navigation, Wegpunkte und Red Station

## Datenmodell und Dateiformat

PathFinding/Navmesh.cpp:38–115, PathPoint.cpp:58–182, PathPolygon.cpp:40–81 sind die Formatquelle. Aktuelles Format: BNMV, Version 6, Generated-BOOL32, nächste Punkt-ID, Punktanzahl. Die neun Dateien sind alle Version 6, generated=false. Ältere Leserpfade BNM1/NMP4 und Versionen 4/5 existieren im Original; der Exporter akzeptiert bewusst nur die vorhandene Version 6.

Punkt: stabile ID, FLOAT3D-Position, Radius, Flags, Important-Entity-ID, Next-Important-**Slot**, Lock-Entity-ID, optional ursprüngliche Lockplatzierung (Position und Winkel), gerichtete Zielslots, optional Polygon. Links verweisen auf Arrayindizes, nicht IDs. Red Station enthält Lücken in IDs; eine Gleichsetzung würde falsche Verbindungen erzeugen.

Flags: WALK=1, JUMP=2, CROUCH=4, OVERRIDE=8, UNREACHABLE=16, TELEPORT=32, IMPORTANT=64. WALK bedeutet langsames Laufen ab dem Punkt; OVERRIDE aktiviert Punktanweisungen bereits vor Ankunft. UNREACHABLE ist eine Bewegungs-/Annäherungsanweisung und kein pauschales Löschen des Knotens aus dem Graphen. Wichtigkeits-Entity und IMPORTANT-Flag sind unabhängige Felder. PPO1 enthält drei Vektoren; PPO2 eine variable Zahl. Alle neun tatsächlichen Dateien enthalten keine Polygone, der Parser erhält dennoch das Format für synthetische Tests.

Koordinaten bleiben unverändert im Serious-Engine-Weltraum (x,y,z); gewöhnliche Gravitation ist -Y. Es werden weder Meterkalibrierung noch Kartenbildtransformation erfunden. Der Dateinamenshash ist ein Hash des Levelpfads (CTFileName::GetHash), **kein Hash des Karteninhalts**. Kartenidentität ist damit noch nicht ausreichend abgesichert.

## Exportierte Karten

| Datei / Karte | Punkte | Gerichtete Links | Schwache Komponenten | Größte starke Komponente |
|---|---:|---:|---:|---:|
| DM_LittleTrouble | 110 | 412 | 1 | 103 |
| DM_TheLostTomb | 111 | 367 | 1 | 104 |
| DesertTemple | 282 | 1215 | 1 | 268 |
| Fortress | 158 | 514 | 1 | 158 |
| Hole | 139 | 443 | 1 | 134 |
| KuntaKinte | 335 | 1602 | 1 | 327 |
| RedStation | 193 | 879 | 1 | 188 |
| WeGotSkullsNBonesToo | 296 | 1124 | 1 | 268 |
| Yodeller | 111 | 485 | 1 | 98 |

Komponenten sind reine Graphstatistik ohne dynamische Locks, Kollisionskörper oder Laufbarkeit. Eine schwach verbundene Karte ist nicht von jedem Punkt aus in jede Richtung erreichbar. KuntaKinte/DesertTemple/Skulls überschreiten bereits die 256-Punkte-Grenze bestehender ssam-Graphen; nicht stillschweigend abschneiden.

## Red Station

Datei: RedStation_5AF1A276.nav; SHA256 70e2839587b0f14c024ef978579133e84eed594a3cbbd0fa1f1db98d99aa37c6.

193 Punkte, 879 gerichtete Links, 338 reziproke Kantenpaare und 203 einseitige Links. Eine starke Komponente umfasst 188 Punkte, fünf weitere sind Einzelpunkte. Zehn Punkte besitzen JUMP, acht OVERRIDE, einer TELEPORT, einer Lock-Entity; acht Important-Entity-Referenzen. IMPORTANT-Flag ist nullmal gesetzt. Es gibt keine Polygonflächen, kein exportiertes Covermodell und keine gespeicherten vollständigen Kampfrouten.

Spezialfälle:

- Slot 2 / ID 2 referenziert Lock-Entity 9 samt ursprünglicher Platzierung. PathPoint::IsLocked vergleicht aktuelle Position/Winkel zur Referenz (>0,1). Fehlende Entity wird im Original wie kein Lock behandelt; für unseren Adapter muss der Umgang mit unbekannten Entitäten ausdrücklich festgelegt werden.
- Slot 12 / ID 12 hat Flags 42 = JUMP|OVERRIDE|TELEPORT und einen gerichteten Ausgang zu Slot 34. Das ist kein Beweis, dass der existierende Client genau diese Bewegung bereits ausführen kann.
- Important-Entities: Slot/ID 34/34→243, 59/59→375, 71/71→311, 119/119→348, 128/128→248, 138/139→401, 175/177→544, 176/178→267. **Kein Waffentyp steht in der NAV-Datei.** Punktposition ist auch nicht automatisch Itemposition. Erst ein zulässiger nativer Entitysnapshot kann diese IDs benennen.

Vollständige Koordinaten, Lockorigin und alle Kanten sind im privaten JSON/CSV erhalten. Die öffentliche Fassung benennt Struktur und Referenzen ohne eine neue Verteilungsfreigabe für Kartendaten zu behaupten.

## Tatsächlicher Algorithmus

Navmesh.cpp:590–721 FindNextPoint: A* mit linearer Suche des besten Openknotens, pro Suche aufgebauten CPathPoint-Objekten, euklidischer Distanzheuristik, gesperrten Punkten als Ausschluss und Backtracking zum nächsten Schritt. Geschlossene Knoten werden nicht neu geöffnet. Bei TELEPORT am Ausgangspunkt sind Kantenkosten null. **Die euklidische Heuristik ist bei solchen Nullkosten-Teleports nicht allgemein zulässig; optimale Routen sind damit nicht garantiert.** Ein auf h=0 umgestellter Dijkstra wäre eine dokumentierte Verhaltenskorrektur, keine unveränderte Übernahme.

BotFunctions.cpp:32–107 sucht den nächsten Punkt mit horizontaler/vertikaler Distanz und Radiusbezug, aber ohne allgemeine Sicht-/Erreichbarkeitsgarantie. Die Suche hat eine initiale Grenze von 1000. Stockwerk-/Colliderprüfung muss an unserer bereits vorhandenen Anchorprüfung anknüpfen.

BotMovement.cpp:34–226 entscheidet zwischen Follow-, Item-, Gegner- und Important-Zielen, prüft Ankunft mit Punktradius und Gravitybezug und plant bei fehlendem Punkt, Timer oder Bewegungsstillstand neu. Important-Ziele können weitere Important-Punkte verketten. Die Navigation ist prozedurale Zustandslogik, kein externes Behavior-Tree-Asset.

UseImportantEntity (BotFunctions.cpp:134–161) sendet unter anderem EET_TRIGGER an Switches, verarbeitet MovingBrush/Marker. Diese direkte Engineeventauslösung ist kein regulärer Vanilla-Clientbefehl. Wo Berühren/Use/Bewegung genügt, darf ein Actionadapter verwendet werden; sonst Punkt als nicht unterstützt sperren und dokumentieren.

## Bewegung, Hindernisse, Recovery

CastBotRay (BotFunctions.cpp:164–182) nutzt Engine-CCastRay, ignoriert Modelle und behandelt transparente Portale/physische Flags spezifisch. CastRayFlags (SandboxCommon.cpp:173–206) setzt Rayflags und prüft Sektoren/Welt; daraus folgt keine Mutation von Brushflags. Ein allgemeines LOS-Ergebnis ist nicht automatisch derselbe Kollisionsbeweis.

NoPosChange (BotMovement.cpp:25–32) und die Bewegungslogik erkennen Stillstand, ändern Richtung und planen neu. Das ist begrenzte lokale Recovery, keine allgemeine Garantie gegen Sackgassen. Strafe, JUMP/CROUCH/OVERRIDE und Fallenbehandlung benötigen den jeweiligen Ziel-/Boden-/Kollisionskontext. Automatischer Sprung fehlt aktuell an unserem tatsächlichen Ausgabepfad.

CheckPit (BotMovement.cpp:341–371) verändert temporär en_vNextPosition und en_fStepDnHeight=16, ruft WouldFallInNextPosition und restauriert die Felder. Das ist **kein rein lesender Sensor**. AvoidPits prüft Alternativrichtungen ±45° beziehungsweise rückwärts. bAvoidPits ist im Konstruktor standardmäßig FALSE. Für unsere Architektur nur read-only FloorProbes/Kollisionsadapter verwenden; Gleichwertigkeit separat testen.

Generierung (Navmesh.cpp:238–382; NavMeshGenerator.es:53–88): flache Brushpolygone, ausgenommene Passable-/Fieldbrushes, Zentren/Edges, Zusammenführung naher Punkte und geometrische Verknüpfung. FlatPolygon nimmt feste Abwärtsgravitation sowie Reibungs-/Winkelgrenzen an. Die Generatorroutine ist kein vollständiger Clearance-/Sprungsolver; die Wiki empfiehlt manuelle Bearbeitung gegenüber bloßer Autoverknüpfung. Zur Nutzung vorhandener Red-Station-Daten ist Laufzeitgenerierung nicht erforderlich.

Schwimmen, komplexe Lift-/Teleport-/Sprungfolgen und dynamische Türen bleiben native Prüfpflicht. Keine belastbare allgemeine Hindernisumgehung oder Taktik wird aus einem Flag allein abgeleitet.

## Vergleich mit aktuellem Supply-Graph

Der aktuelle Graph speichert höchstens 256 Punkte, 24 Nachbarn und symmetrische Links. Der vorhandene konservative Cecil-Kandidat hat 172 Punkte / 279 ungerichtete Kanten, entfernt Spezial-/Entitypunkte und einseitige Verbindungen und zerfällt in 18 Komponenten (größte 105). Das ist eine bewusst reduzierte Teilmenge, **keine 1:1-Navigation**.

Der bisher gemessene 236-Punkte-Graph und der 172-Punkte-Kandidat sind verschiedene Datensätze. Beide nicht mit dem vollständigen 193-Punkte-Original verwechseln. Vollständige Wiederverwendung braucht gerichtete Links, Radius/Flags, Entity-/Lockadapter und geprüfte Actions; nicht mehr zufällige Wegpunkte.

## Reproduktion

```bash
cd docs/research/cecilbot-analysis
python3 scripts/fetch_reference.py
python3 -m unittest discover -s scripts -p 'test_*.py' -v
python3 scripts/export_analysis.py reference /tmp/cecil-export-new
```

Der Exporter verweigert ein vorhandenes Zielverzeichnis, validiert Indizes und endliche Zahlen und prüft vor Ausgabe alle neun binären Rundläufe. Kein Installer, kein Zugriff auf laufende Spiele.
