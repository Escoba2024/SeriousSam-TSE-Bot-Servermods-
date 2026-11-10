# Cecil-Transfer: aktueller Quellstand047

Quelle `d47bcf76d20aede8a24fdb462308f187e3604e57`, Tree `21176801c5ab0583131ecf86adc3a268919a9599`, DLL `1f80eca362ab0fd414f2cf6c24abff3cf4606f94f9786a1611e2824f49aa089e`. Alle41 Originalbereiche sind an127 aktuelle Quellanker-Vorkommen und14 Dateihashes gebunden (87 verschiedene Positionen). Die94 Zeilenanker und15 übernommenen046-Grenzen ergeben109; sechs separat geführte Entrypoints sowie elf neue047-Grenzanker und ein zusätzlicher Observer-Aufruf ergänzen127. Originalkategorien und erforderliche Schnittstellen bleiben unverändert:33 implementiert, eine vorhandene Human-LOS adaptiert, vier Architekturteile ausgeschlossen und zwei Bereiche außerhalb des FFA-Scope. Das ist keine vollständige Originalmod-Laufzeitparität.

Der [aktuelle Native-Bericht](2026-11-10-candidate047-native-results.md) trennt genuineSupply-onlyPASS von beiden funktional offenen Kartenfenstern.165 aktuelle strenge Health-Paare erfüllen beobachtete Zähl-/Timinggrenzen nur innerhalb dieser Fenster. Keine047-Stunden, Retail-, Ressourcen-, Rotations-, Wiederanlauf- oder Flottenprüfung ist gestartet. Frühere039-/045-/046-Ergebnisse bleiben in der [maschinenlesbaren Matrix](transfer-status.json) historische Belege, ohne047-Kredit.

| ID | Bereich | Quellstatus | Begrenzter aktueller047-Befund |
| --- | --- | --- | --- |
| T01 | NAV-Dateien | IMPLEMENTIERT | Supply-Red und beide vollständigen Kartenfenster laden die aktuellen map-/NAV-CRC-gepinnten Originalgraphen. Die drei übrigen Karten und vollständige Traversierung sind nicht gemessen. |
| T02 | Punktstruktur | IMPLEMENTIERT | Originale Slot-/Radius-/Flag-/Entity-Metadaten sind in aktuellen Checkpoint-/Patrol-Verläufen korreliert. Vollständige Wirkung aller Sonderpunkte bleibt offen. |
| T03 | Gerichtete Verbindungen | IMPLEMENTIERT | Skulls zeigt169s wechselnde gewöhnliche Hops zum Important-Ziel150; Hole behält weitere Item-/Important-/Liquid-Routen offen. Summierter Weltweg ersetzt keinen gerichteten Zielfortschritt. |
| T04 | Punktradien | IMPLEMENTIERT | HoleA2g7 erreicht Original69r2 gesampelt; A2g13 hat frischen Erwerb und anschließende Original-Navigator-Fortsetzung, aber keine1Hz-Inside-Radius-Probe. Kein Radius-/Trigger-Paritätskredit. |
| T05 | A*-Suche | IMPLEMENTIERT | Hole hat zwei tatsächliche gewöhnliche alternative Erwerbe, einen Todeszensor und einen Ausschöpfungsfehler. Gerichtete Suffixprüfung ist portabel belegt; keine globale Suchparität. |
| T06 | Nächster Navpunkt | IMPLEMENTIERT | HoleA2g7/g13 melden frische gewöhnliche Erfassung von69 und zeigen autonome physische Folge plus NAV-Fortsetzung im selben Leben. Hint52 bleibt todeszensiert; B0 scheitert ausdrücklich. |
| T07 | Important-Ziele | IMPLEMENTIERT | Skulls-Ziel150 bindet original Armor1770; der globale Important-Guard schützt auch gewöhnliche Zwischenkanten. Hole zeigt weitere entfernte Important-Ziele ohne wirksame Zwischenfortsetzung. Terminal-/Next-Ketten nicht vollständig belegt. |
| T08 | Switch-/Marker-Events | IMPLEMENTIERT | Vorhandene Interaktions-/USE-Pfade sind kein vollständiger Nachweis eines tatsächlich ausgelösten Switch-/Marker-Engine-Events. Keine neue Wirkungsfreigabe. |
| T09 | Locks | IMPLEMENTIERT | Native Lock-/Referenzkontexte sind vorhanden; weder geloggter Zustand noch kurzer Approach beweist vollständige erfolgreiche Lock-/Lift-Traversierung. |
| T10 | Teleport | IMPLEMENTIERT | Skulls-Ziel224 hat TELEPORT32, nicht IMPORTANT64. Sein eigener30s-Kontext bleibt getrennt offen; weder Positionstransition noch Flag allein beweist Entry-/Exit-/Triggerkette. |
| T11 | Jump/Crouch/Override | IMPLEMENTIERT | Jump-/Override-Metadaten und tatsächliche vertikale Bewegung sind vorhanden; vollständige finale Jump-/Crouch-/Override-Eingabe mit eindeutiger physischer Ursache nicht abgenommen. |
| T12 | Auto-NAV-Generierung | NICHT_ANWENDBAR_5_FFA_MAPS | Außerhalb des erklärten gepinnten FFA-Scope; kein nativer Implementierungs- oder Paritätskredit. |
| T13 | NAV-Editor/Netzbefehle | ARCHITEKTONISCH_AUSGESCHLOSSEN | Editor-/Netzbefehle sind architektonisch ausgeschlossen; kein nativer Implementierungs- oder Paritätskredit. |
| T14 | Per-Bot Pfadzustand | IMPLEMENTIERT | 165 unterschiedliche gesundheitskorrelierte Folgegeneration-Paare in aktuellen Skulls/Hole-Fenstern, normale Abschlüsse. In-Process-Mapwechsel/Rejoin/Recovery nicht gemessen. |
| T15 | Stuck-Erkennung | IMPLEMENTIERT | Skulls5/Hole34 Checkpoints; begrenzte echte Fortsetzungen stehen tatsächlichen169s- und weiteren Item-/Important-/Liquid-Schleifen gegenüber. Numerische Stillstandsgrenzen allein lösen diese Routen nicht. |
| T16 | Recovery-Bewegung | IMPLEMENTIERT | Hole vier Alternativversuche: zwei frische gewöhnliche Erwerbe mit autonomer physischer/NAV-Folge, ein Todeszensor, ein echter Ausschöpfungsfehler. Keine pauschale Recovery-Wirkung. |
| T17 | Abgrundvermeidung | IMPLEMENTIERT | Aktuelle Alternativbewegung bleibt statisch/Wall/Floor-pflichtig, auch bei gewöhnlicher Policy0. SafeMotion-Status oder erfolgreiche Bewegung ist kein direkter vollständiger Floor-Cast-Nachweis. |
| T18 | Schwimmen/Gravitation | IMPLEMENTIERT | HoleDIVE-Ziel105/hop85 und Important-Ziel64/hop86 bleiben hinsichtlich wirksamer Annäherung offen. PassiveFALL-Historie ist weder Schwimm- noch aktuelle Bodenfreigabe. |
| T19 | Follow-Verhalten | IMPLEMENTIERT | Combat-/Target-Kontexte liegen vor; vollständiger Follow-/Gedächtnis-/Erreichbarkeitsvertrag ist nicht nativ abgenommen. |
| T20 | Gegnerauswahl | IMPLEMENTIERT | Alle acht Bots zeigen in beiden aktuellen Karten positive Scoreänderungen und Feueraktivität. Kein vollständiger Reaktions-/Cooldown-/Trefferzuordnungsnachweis. |
| T21 | Team-/Monsterauswahl | IMPLEMENTIERT | Die tatsächlichen Fenster betreffen FFA; Team-/Monster-/Coop-Parität wird nicht behauptet. |
| T22 | Sichtprüfung | BEREITS_VORHANDEN_OFFLINE_GEPRUEFT | Aktuelle LOS-/Raypfade und native Sichtproben sind vorhanden; keine Gleichsetzung mit vollständigem Original-Ray-Verhalten. |
| T23 | Zielgedächtnis/Timer | IMPLEMENTIERT | Aktuelle Sicht-/Zielproben ersetzen keine vollständige Lebens-/Identitäts-/Gedächtnisablaufmessung. |
| T24 | Waffentabellen | IMPLEMENTIERT | Aktuelle typisierte Waffenbesitzwechsel sind vorhanden; Pflichtfünfergruppe3/8/9/11/14 ist nicht vollständig als geordnete native Pickup-/Auswahl-/Current-Kette abgenommen. |
| T25 | Waffenbewertung | IMPLEMENTIERT | Begrenzte Besitz-/Desired-/Wanted-/Current-Proben, aber vollständige Nahbereichs-/Dwell-/Bewertungsabnahme fehlt. |
| T26 | Waffenwechsel | IMPLEMENTIERT | Strenger Waffenobserver und neuer Player-Observer bleiben lesend. Vollständige unzensierte Wechselkette, Opportunity/CD/Dwell und native Zeitdomänen sind getrennt; Player-Snapshot ist kein Anwendungs-/Kameraursachenbeweis. |
| T27 | Feuer/Granate/Scope | IMPLEMENTIERT | Emittierte Feueraktionen und Scoreänderungen sind beobachtet; keine Shot=Hit-Behauptung, vollständige Granaten-/Scope-/Explosivsicherheitsprüfung offen. |
| T28 | Aim/Vorhalten | IMPLEMENTIERT | Aktuelle Winkel-/Combat-Proben ersetzen keine vollständige Vorhalte-/Trefferprüfung. |
| T29 | Strafing/Distanz | IMPLEMENTIERT | Bewegung und Strafing sind tatsächlich beobachtet;169s-Zielkreiseln und weitere Weltwegzyklen werden nicht zu Hop-Fortschritt erklärt. |
| T30 | Itempriorität | IMPLEMENTIERT | Supplyv20: feste erste zehn Ziele9/10, feste zehn Initialleben Median8,375s/P9512,45s. Ein echter Kohorten-Timeout bleibt erhalten; genuineSupply-onlyPASS, keine Gesamtfreigabe. |
| T31 | Itemkandidaten/LOS | IMPLEMENTIERT | Alle26 Waffenstarts:23 typisiert/lifecycle-/bit-/GoalEnd-/räumlich korroborierte Erwerbe,1 echter Timeout,2 rechtszensierte Nichtkohortenversuche. Alle31Goalstarts bleiben erhalten; keine universelle Pickupreichweite. |
| T32 | Reisemesser | IMPLEMENTIERT | Reisemesser-Arbitration und Sichtungsverzögerung sind nicht vollständig nativ adjudiziert. |
| T33 | Respawn | IMPLEMENTIERT | 165 strenge aktuelle Health-Paare:63Skulls+102Hole; beobachtete Death→Spawn- und Aktivität≤5s NACHSpawn-Grenzen erfüllt. Kein globaler Lebenszyklus-/Karten-/Dauer-PASS. |
| T34 | Schwierigkeiten | IMPLEMENTIERT | Aktueller gepinnter Preset gemessen; nicht alle Schwierigkeiten nativ abgenommen. |
| T35 | Configserialisierung | IMPLEMENTIERT | Supply17 Schutzpins und Postrun289 Quieszenz-Pins erhalten; keine vollständige Invalid-/Serialisierungs-/Konfigurationsmatrix nativ abgenommen. |
| T36 | Controller als Modul | IMPLEMENTIERT | Aktueller Source/Tree/DLL/Manifest/PID-Start/Load/Map und normale Abschlüsse gebunden. Beide Karten bleiben funktional routeOPEN; kein All6-Rollout. |
| T37 | PlayerBot/EntitiesMP | ARCHITEKTONISCH_AUSGESCHLOSSEN | Normale Spieler-/Action-Schnittstelle statt originaler PlayerBot-Entityklasse; Player-Observer ist lesend, keine Engine-/Entity-Subclass- oder Kameraänderung. |
| T38 | Netzpatch/Patcher | ARCHITEKTONISCH_AUSGESCHLOSSEN | Netzpatch/Patcher ist bewusst ausgeschlossen; keine fremde Klasse/Netzpatch-Runtimeparität behauptet. |
| T39 | Lernen/Teamtaktik | NICHT_ANWENDBAR_5_FFA_MAPS | Lernen/Teamtaktik liegt außerhalb des erklärten FFA-Scope; kein nativer Implementierungs- oder Paritätskredit. |
| T40 | Native Gleichwertigkeit/Last | OFFEN | Supply-onlyPASS und begrenzte600s-/Health-Nachweise; beide KartenrouteOPEN, drei weitere Karten, Retail047, Stunden, CPU/RSS, Rotation, Recovery und Flotte nicht durchgeführt. |
| T41 | Coop-Catch-up-Teleport | ARCHITEKTONISCH_AUSGESCHLOSSEN | Coop-Catch-up-Teleport ist bewusst ausgeschlossen; kein nativer Implementierungs- oder Paritätskredit. |

T33 trennt Aktivität höchstens5s **nach Spawn** von Death→Spawn spätestens tatsächlicher Presetverzögerung+5s (hier default6s). Der neue Player-Observer beweist weder die Anwendung einer Action noch eine Kameraursache. Currentstatic-/STAND-/frischeNearestLOS-Freigaben bleiben von passiverFALL-/STUCK-Historie getrennt. Zusätzliche Recovery-Aktivierungen und Diagnoseformatierung sind ohne Ressourcenfenster kein CPU-/RSS-Nachweis.

GPL-Attribution, Patcher-/CPOL-Architekturgrenze und der Schutz originaler NAV-/Retail-Daten gelten weiter. Originalmod-Runtime bleibt ein konkreter zusätzlicher Toolchain-/Entities-Buildauftrag, nicht ein erfundener externer Blocker. Die separate048-Important-Transitkorrektur ist nicht Bestandteil dieser047-DLL; portable RED/GREEN-Prüfung ist kein neuer nativer Erfolg.
