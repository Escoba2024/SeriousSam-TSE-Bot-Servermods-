# Cecil-Transfer: aktueller Quellstand 046

Quelle `c298cf241b514b28f6d28e815bb5718a5a1d3d6c`, Tree `dba553b039a8a4dd10de27168f37671a1da48d84`, DLL `b148ae2e9ccfb337a6311bd81c4cdedafb9eac5d48bbb31126673eec51554816`. Alle 41 Originalbereiche sind an 109 aktuelle Quellanker und 14 Dateihashes gebunden. 33 Bereiche sind implementiert, eine vorhandene Human-LOS ist adaptiert, vier Architekturteile sind ausgeschlossen und zwei Bereiche liegen außerhalb des FFA-Scope. Das beschreibt Quellintegration, keine vollständige Originalmod-Laufzeitparität.

Die tatsächlichen 046-Ergebnisse stehen im [Native-Bericht](2026-11-10-candidate046-native-results.md): Supply-P95 und Hole-Stillstand/Spawnaktivität scheitern; Skulls hat trotz erfüllter numerischer Grenzen offene Routenkontexte. Von 151 aktuellen gesundheitskorrelierten Respawnpaaren folgt kein Respawn-PASS, weil eine Aktivitätsgrenze verletzt ist. Nicht gemessene Gates bleiben offen.

Die unveränderlichen 045- und 039-Referenzen bleiben in der [maschinenlesbaren Matrix](transfer-status.json) erhalten. Frühere native Resultate werden nicht übertragen. GPL-Attribution, die begründete Patcher-/CPOL-Architekturgrenze und das Veröffentlichungsverbot für originale NAV-/Retail-Daten bleiben bestehen.

| ID | Bereich | Quellstatus | Begrenzter aktueller 046-Befund |
| --- | --- | --- | --- |
| T01 | NAV-Dateien | IMPLEMENTIERT | Exakte map-/NAV-gepinnte Loads für Supply-Red und zwei Kartenfenster beobachtet; weitere Karten und vollständige Traversierung offen. |
| T02 | Punktstruktur | IMPLEMENTIERT | Originalpunkte in Checkpoint-/Patrol-Kontexten korreliert; Sonderpunktwirkung nicht vollständig belegt. |
| T03 | Gerichtete Verbindungen | IMPLEMENTIERT | Skulls hält zwei gleiche Hops152/32s ohne wirksame Zielannäherung; Hole weitere Routenfragen. Keine vollständige gerichtete Traversierungsfreigabe. |
| T04 | Punktradien | IMPLEMENTIERT | Begrenzte ursprüngliche Hop-/Ankerfortschritte beobachtet; Hint52 ist keine Radiusankunft oder abgeschlossene Zielerreichung. |
| T05 | A*-Suche | IMPLEMENTIERT | Vorbereitete Suffixprüfung portabel geprüft; zwei alternative Erwerbe und drei echte Ausschöpfungsfehler nativ erhalten, keine globale Suchparität. |
| T06 | Nächster Navpunkt | IMPLEMENTIERT | Hole: zwei gewöhnliche Erwerbe von Originalpunkt52 mit physischem Fortschritt im selben Zielkontext; drei ausgeschöpfte Versuche und offene lange Routen bleiben erhalten. |
| T07 | Important-Ziele | IMPLEMENTIERT | Item-/Important-Kontexte beobachtet; vollständige native Wirkung der Important-/Next-Slot-Ketten offen. |
| T08 | Switch-/Marker-Events | IMPLEMENTIERT | Hole protokolliert Interaktionsabsichten; tatsächliche USE-Wirkung oder ausgelöster Engine-Event nicht vollständig nachgewiesen. |
| T09 | Locks | IMPLEMENTIERT | Hole-Lock-Snapshots und ein Approach-Tag erfasst; keine pauschale erfolgreiche Lock-/Lift-Traversierung daraus. |
| T10 | Teleport | IMPLEMENTIERT | Teleportflags oder späte Positionssprünge ersetzen keine geprüfte Entry-/Exit-/Entity-Kette. |
| T11 | Jump/Crouch/Override | IMPLEMENTIERT | Vollständige finale Jump-/Crouch-/Override-Eingabe mit physischer Folge bleibt offen. |
| T12 | Auto-NAV-Generierung | NICHT_ANWENDBAR_5_FFA_MAPS | Bewusst außerhalb des gepinnten Architektur-/FFA-Scope; kein nativer Implementierungs- oder Paritätskredit. |
| T13 | NAV-Editor/Netzbefehle | ARCHITEKTONISCH_AUSGESCHLOSSEN | Bewusst außerhalb des gepinnten Architektur-/FFA-Scope; kein nativer Implementierungs- oder Paritätskredit. |
| T14 | Per-Bot Pfadzustand | IMPLEMENTIERT | 151 tatsächliche Health-Death-/Folgegeneration-Paare über zwei Karten; In-Process-Map-/Rejoin-/Recovery-Gates nicht gelaufen. |
| T15 | Stuck-Erkennung | IMPLEMENTIERT | Skulls152/32s ineffektive Hop-Kontexte; Hole31,291447s unbegründeter Stillstand trotz numerischer Aktivität anderer Slots. |
| T16 | Recovery-Bewegung | IMPLEMENTIERT | Zwei begrenzte alternative Erwerbe mit Fortschritt; drei ausgeschöpfte Versuche, offene Routen und Hole-Spawnaktivität32,1s verhindern Freigabe. |
| T17 | Abgrundvermeidung | IMPLEMENTIERT | Patrol verlangt im Code aktuelle statische Referenz sowie Wand/Boden auch bei Pit-Policy0; SafeMotion-Rückgabewert ist kein direkter Floor-Cast-Beleg. |
| T18 | Schwimmen/Gravitation | IMPLEMENTIERT | PST_FALL ist kein Flüssigkeitszustand; vollständige Schwimm-/Gravitationsfolgen und autonome Wiederaufnahme nicht abgeschlossen. |
| T19 | Follow-Verhalten | IMPLEMENTIERT | Combat-/Target-Kontexte liegen vor; Follow-/Gedächtnis-/Erreichbarkeitsvertrag nicht vollständig abgenommen. |
| T20 | Gegnerauswahl | IMPLEMENTIERT | Alle acht zeigen in beiden Karten positive Scoreänderungen und Feueraktivität; keine vollständige Reaktions-/Cooldown-Abnahme. |
| T21 | Team-/Monsterauswahl | IMPLEMENTIERT | Native Beobachtungen betreffen FFA; Team-/Monster-/Coop-Parität wird nicht behauptet. |
| T22 | Sichtprüfung | BEREITS_VORHANDEN_OFFLINE_GEPRUEFT | Bestehende LOS-/Querypfade und begrenzte Beobachtungen; keine Gleichsetzung mit originalem Ray-Verhalten. |
| T23 | Zielgedächtnis/Timer | IMPLEMENTIERT | Sicht-/Zielproben sind vorhanden; vollständige Gedächtnisablauf-/Identitätsmessung bleibt offen. |
| T24 | Waffentabellen | IMPLEMENTIERT | Typisierte Waffenbesitzwechsel vorhanden; die Pflichtfünfergruppe3/8/9/11/14 ist nicht vollständig nativ abgenommen. |
| T25 | Waffenbewertung | IMPLEMENTIERT | Begrenzte Auswahl-/Besitz-/Current-Belege; vollständige Nahbereichs-/Dwell-/Bewertungsabnahme fehlt. |
| T26 | Waffenwechsel | IMPLEMENTIERT | Strenger Observer bleibt lesend und zeitlich unqualifiziert. Nur echte unzensierte046-Ketten können zählen; keine frühere Policy-Opportunity oder angenommene Clock-Gleichheit. |
| T27 | Feuer/Granate/Scope | IMPLEMENTIERT | Emittierte Feueraktionen und Scoreänderungen beobachtet; komplette Granaten-/Scope-/Sicherheitsdistanzprüfung und genaue Trefferzuordnung offen. |
| T28 | Aim/Vorhalten | IMPLEMENTIERT | Native Winkel-/Combat-Proben ersetzen keine vollständige Vorhalte-/Trefferprüfung. |
| T29 | Strafing/Distanz | IMPLEMENTIERT | Bewegung und Strafing beobachtet; Kreiseln oder seitliche Ausweichaktionen sind kein Hop-Fortschritt. |
| T30 | Itempriorität | IMPLEMENTIERT | Zehn feste Erstziele10/10, aber zehn feste Initialleben Median9,9s/P9530,5s überschreiten unverändert30s; tatsächlicher Nichtkohorten-Timeout erhalten. |
| T31 | Itemkandidaten/LOS | IMPLEMENTIERT | Zehn ausgewählte Ziele typisiert korreliert; alle26 Waffenstarts25korreliert+1Timeout und alle34Goalstarts erhalten. Keine pauschale Pickupreichweite. |
| T32 | Reisemesser | IMPLEMENTIERT | Reisemesser-/Arbitrations- und Sichtungsverzögerung nicht vollständig nativ adjudiziert. |
| T33 | Respawn | IMPLEMENTIERT | 151 unterschiedliche046-Health-Paare belegt (64Skulls+87Hole), Death→Spawn max1,9s. HoleB2 benötigt nach Spawn32,1s bis Aktivität statt höchstens5s; kein Respawn-Gesamt-PASS. |
| T34 | Schwierigkeiten | IMPLEMENTIERT | Gepinnter aktueller Preset gemessen; nicht alle Schwierigkeiten nativ abgenommen. |
| T35 | Configserialisierung | IMPLEMENTIERT | Supply17 Schutzpins und Postrun289Pins erhalten; keine vollständige Invalid-/Konfigurationsmatrix nativ abgenommen. |
| T36 | Controller als Modul | IMPLEMENTIERT | Build-/PID-/Start-/Inputbindung begrenzt geprüft; Supply/Hole fehlen, Skulls-Routen offen. Kein All6-Rollout. |
| T37 | PlayerBot/EntitiesMP | ARCHITEKTONISCH_AUSGESCHLOSSEN | Bewusst außerhalb des gepinnten Architektur-/FFA-Scope; kein nativer Implementierungs- oder Paritätskredit. |
| T38 | Netzpatch/Patcher | ARCHITEKTONISCH_AUSGESCHLOSSEN | Bewusst außerhalb des gepinnten Architektur-/FFA-Scope; kein nativer Implementierungs- oder Paritätskredit. |
| T39 | Lernen/Teamtaktik | NICHT_ANWENDBAR_5_FFA_MAPS | Bewusst außerhalb des gepinnten Architektur-/FFA-Scope; kein nativer Implementierungs- oder Paritätskredit. |
| T40 | Native Gleichwertigkeit/Last | OFFEN | Supply-P95 und Hole-Stillstand/Spawnaktivität scheitern. Drei weitere Karten, Stunden, Retail046, Ressourcen, Rotation, Recovery und Flotte nicht durchgeführt. |
| T41 | Coop-Catch-up-Teleport | ARCHITEKTONISCH_AUSGESCHLOSSEN | Bewusst außerhalb des gepinnten Architektur-/FFA-Scope; kein nativer Implementierungs- oder Paritätskredit. |

Die verbleibenden Nachweise jeder Zeile sind in `remaining_native_evidence` konkret benannt. T33 trennt ausdrücklich Death→Spawn (tatsächlicher Presetdelay plus 5 s, hier 6 s) von Aktivität höchstens 5 s **nach Spawn**. Die zusätzliche vorbereitete Suffixsuche und die LOS-Arbeit bleiben im gemeinsamen Strahlenbudget, sind aber ohne neue Messung kein CPU-/RSS-Nachweis.

Die getrennte 047-Änderung an passiver Hop-Beobachtung ist kein Bestandteil dieser 046-DLL und erhält aus diesen Läufen keinen Kredit. Main hat die sechs finalen Dateien einschließlich aller 41 Bereiche, 109 Quellanker, Build-/Native-Bindungen und unveränderten historischen Anhänge geprüft. Die Veröffentlichung führt Main getrennt aus.
