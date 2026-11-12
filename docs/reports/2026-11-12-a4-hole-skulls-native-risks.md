# A4 Hole und Skulls: konkrete native Risiken vor Kandidat013

Status: **offene Funktionsabnahme**, unabhängige Auswertung erhaltener 048-Belege und aktueller 013-Quellen. Kein neuer Prozess, Hook oder Harness wurde ausgeführt oder geändert. Der RedStation-Kandidat013 besitzt keine daraus ableitbare Hole-/Skulls-Abnahme. Alte Dateien namens `013-hole-functional` in der historischen 048-Evidenz gehören zu einer anderen Nummerierung.

## Bindung und Vergleichsbasis

| Karte | Weltpfad | World-CRC | Nav-CRC | Knoten | Pfadhash, kein Datei-CRC |
|---|---|---|---|---:|---|
| Hole | `Levels\LevelsMP\Deathmatch\Hole.wld` | `582bd040` | `d7cac057` | 139 | `1ad627d0` |
| Skulls | `Levels\LevelsMP\Deathmatch\WeGotSkullsNBonesToo.wld` | `42d03dd2` | `70b554dd` | 296 | `9b573405` |

Die NAV-Metadaten wurden aus den erhaltenen Fixture-Dateien gelesen. Vergleichskandidat048: DLL `ec820d0461313c41fec2b477f57109310d3c71a77b4423955ac69f3807566530`, Quelle `4d04ab4ad190a0f6cd078d96f5416e0eea9e1da0`. Die privaten Belege liegen unter `tse-cecil-gate8-20261109/evidence/candidate048-{hole,skulls}-preserved` und `048-{hole,skulls}-functional`; hier stehen nur bereinigte Befunde und überprüfbare Zeilenreferenzen.

Hole lief 600.007804 s, Skulls 600.005876 s, jeweils mit 595 Samples und acht Bots. 81 beziehungsweise 71 gesundheitskorrelierte Tod-/Respawn-Paare und steigende Frags belegen Aktivität, **keine funktionierende Route**. Die größte als unerklärt stationär klassifizierte Dauer betrug nur 2.023 beziehungsweise 5.046 s; bewegte Schleifen bleiben dabei unsichtbar.

## Priorität 1: bewegte Routenschleifen bis zum ursprünglichen Timeout

**Hole, botA local2, Generation11:** Waffenitem417, Zielslot65, Auswahl bei Tick9221 (botA.log:6403); anschließend 45 Zustandszeilen von9240 bis10120 über44 s. Alle sind STAND/NAV1, 43 zeigen Quelle0→Hop1. Der Spieler legt rund139.66 m innerhalb eines6.70×2.84×7.73-m-Bereichs zurück; Schusszähler259 bleibt konstant. Sechs Checkpoints betreffen wieder Quelle0→1, Zeiten469.05,476.05,483.05,491.05,498.05,504.05 (Zeilen6484/6611/6708/6836/6916/6993). Entfernung zu Hop1 bleibt ungefähr21–28 m. Erst Tick10121 beendet das Item wegen Timeout (7020), danach Auswahl442 (7021). Beide Zwischenknoten0/1 sind gewöhnliche, ungesperrte Knoten ohne wichtiges Item.

**Skulls, botA local0, Generation9:** Waffenitem917, Zielslot271, Auswahl10445 (7520), ursprüngliche Frist556.551. Alle26 Zustände10620–11120 über25 s zeigen STAND/NAV1, Quelle129→Hop248, nie Sichtkontakt; Schusszähler238 bleibt konstant. Kleinste beobachtete Hopdistanz11.69 m; Timeout11132 (7957). Es gibt hier keinen Checkpoint, dessen Voraussetzungen nicht durchgehend gegeben waren. NAV-Slot248 hat stabile ID250; Zielslot271 hat ID273. Slot und stabile ID dürfen nicht verwechselt werden.

013 hat einen passiven Item-Transit-Abbruch nach10 s ohne ausreichenden Fortschritt, mit .75-m-Verbesserungsschwelle, identischem gerichteten Zwischenabschnitt und unveränderter ursprünglicher Frist. Ein Checkpoint-Rückweg zum ursprünglichen Quellknoten darf die Uhr nicht erneuern. Der Parameter `accepted` von `BotCecilItemTransitFailed` erhält tatsächlich `useReacquire`/Driver-NAV-Besitz **vor** dem abschließenden SafeMotion-Ergebnis. Daher beweist `floor=0` oder `floor=2` allein keinen Uhrreset. NAV-Verlust, fehlender aktueller Punkt oder andere ungültige Kontexte können die Berechtigung dagegen unterbrechen. Einsekündige Zustandszeilen beweisen keine lückenlose .25-s-Frische.

Entscheidend sind gleiche Lebens-/Item-/Quell-/Hop-/Versuchsidentität, beste Entfernung, tatsächliches Erreichen, wiederholte Checkpoints sowie `CecilItemTransitEnd` und anschließend ein anderes zulässiges Ziel mit echtem Inventarerwerb. Terminale Itemknoten und besondere Kanten sind bewusst ausgenommen; deren Fehler werden durch diesen Watchdog nicht automatisch gelöst.

## Priorität 2: Hole-Flüssigkeit und getrennte Fallzustände

Der Logschlüssel `liquid` ist der originale PlayerState: **0 STAND, 1 CROUCH, 2 SWIM, 3 DIVE, 4 FALL** (SDK107 Player.es:62–66). `immersion=1` kommt auch bei STAND vor und ist allein kein Wasserbeweis. `floor` ist das SafeMotion-Ergebnis0/1/2, kein Bodenkontakt. `support_ref` ist eine Referenzidentität, keine Klassenbestimmung.

Hole enthält394 lebende DIVE- und36 SWIM-Zustände, verteilt auf51 beobachtete zusammenhängende Flüssigkeitsepisoden. Drei konkrete längste DIVE-Episoden enden mit beobachtetem Tod:

| Rolle/local/Generation | Ticks und Dauer | Zustandsbelege | Folge |
|---|---|---|---|
| botA/2/9 |7020–8240,61 s|5031–5744: HP100→20; zuletzt `level_swim=1`, NAV0, Viewpitch−2.008312, UP0|8260, Zeile5761: HP0 |
| botB/0/11 |7160–8280,56 s|4898–5457: HP60→5.3; zuletzt `level_swim=1`, NAV0, Viewpitch−.766957, UP0|8300,5466: HP−74.7 |
| botA/1/14 |8160–9120,48 s|5682–6316: HP100→100; zuletzt `level_swim=1`, NAV0, Viewpitch .195915, UP0|9140,6326: HP−51.4 |

Das belegt lange Flüssigkeitsaufenthalte bis zum Tod, **nicht die Todesursache**; Ertrinken oder Suizid darf daraus nicht behauptet werden. Skulls hat590 FALL-Zustände, aber keine beobachtete SWIM-/DIVE-Episode. Dieser Lauf qualifiziert keine Skulls-Flüssigkeitsfunktion.

Die bestehende SwimMotion-Ausrichtung und eng begrenzte Liquid-Achsenprüfung sind gegenüber048 im Kern unverändert. Die Achsenprüfung erzeugt keine neue UP-Absicht; die Ausrichtung kann Vorwärtsbewegung zurückhalten. Neue Messungen müssen tatsächliche Eintritts-/Austrittszustände2/3→0/1 im selben Leben, Position, aktuelle Translation, Referenz, Gravitation, Blick-/Eingabe-/Kompositionspitch und NAV-Besitz verbinden. Tod und Fensterende sind getrennte Fehler-/Zensierungsfälle. FALL4 und veränderte Gravitation dürfen nicht als Flüssigkeit gezählt werden.

## Priorität 3: Teleport, Sprung, Respawn und Mapreset richtig nachweisen

Hole hat keine mit TELEPORT32 annotierten NAV-Knoten; Skulls hat die Slots221–224. Ein Flag beweist weder eine originale Entityklasse noch einen erfolgreichen Teleport. RedStation-Knoten12 ist das konkrete Gegenbeispiel: TELEPORT-Metadaten können mit einem realen Bouncer-Aufruf zusammentreffen. Erforderlich sind belegter Eingang, gleicher Spieler und gleiche Lebensuhr, beobachteter passender Ausgang und anschließender legaler Fortschritt. Eine UP-Aktion, Flag oder Positionsänderung allein reicht nicht.

013 enthält allgemein geänderte Item-Retention, Connector-Segmentendprüfung und begrenztes Beenden verwaister Flugkanten. Seine neuen Sprung- und versiegelten Flugausnahmen sind jedoch an exakte RedStation-Welt/NAV-Metadaten gebunden und dürfen auf Hole/Skulls keine Wirkung haben. Keine zusätzliche Verallgemeinerung wird vorgeschlagen.

Vor einem neuen Lauf sind tatsächlicher DLL-Hash, kanonische Konfiguration, reale Attach-Zuordnung und beide CecilLoad-Marker mit Welt/Nav-CRC/Knotenzahl abzugleichen. Alle beobachteten Leben zählen einschließlich erfolglos verstorbener und am Ende zensierter Leben; Waffenbesitz, aktuelle Waffe und Feueranforderung sind getrennte Nachweise. Frags sind kein Ersatz für Erwerb, Bewegung oder funktionalen Kartentest.

Geplant sind600-s-Fenster für Hole/Skulls, zunächst120 s RedStation und300 s für die weiteren Karten nach eigenem Preflight. Jeder Lauf kann nur tatsächlich ausgeübte Funktionen belegen. Mehrere getrennte Starts auf festen Karten beweisen keinen Mapreset; die152 alten Respawn-Paare qualifizieren weder013-Respawns noch einen Kartenwechsel. Post-close-Sync-/Crash-/InvalidAction-Prüfung und normale Cleanup-Belege bleiben Pflicht. Keine A4-Gesamtfreigabe aus Queryzahlen oder diesen Analysen.
