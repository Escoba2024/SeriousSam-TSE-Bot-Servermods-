# Historischer Cecil-Transferreview:41 Bereiche, Quellstand c6662dac/Build016

Dieser Bericht bleibt ein historischer Review des unten gepinnten Stands. Die aktuelle Matrix wurde inzwischen auf Normal038 fortgeschrieben: [aktuelle Übernahmematrix](transfer-status.md), [native038-Ergebnisse](2026-11-09-candidate038-native-results.md). Seine alten JSON-Hashes und Snapshotangaben werden nicht als aktueller Matrixzustand ausgegeben.

Geprüfter Quellpin: **`c6662dac40a4d344667222f7cb6abd0b8eb5341c`**, Tree `f264127e4d26883cc94021b5dadd759a85b5dff5`. Der Review bestätigt die Zuordnung aller 41 Originalbereiche und die vorhandenen Adapter. Er bestätigt **keine vollständige Cecil-Verhaltensgleichheit und keine native Freigabe**. Build016 hat zum vorgegebenen Berichtsstand ausschließlich kurze Supply-/Hole-Versuche begonnen; daraus wird kein bestandenes Gate abgeleitet.

Geltungsbereich bleiben die fünf Fragmatch-Karten Red Station, Yodeller, Skulls, Little Trouble und Hole sowie sechs Instanzen einschließlich Entwicklung. Normale BotClient-Netzwerkspieler, unveränderte Dedicated-/Engine-/Entities-Komponenten und die eingefrorenen [Qualifikationskriterien](qualification.md) bleiben maßgeblich.

## Herkunft und Beleggrenzen

- Original: DreamyCecil/CecilBotMod `953b477e53fdc5a5d84c8ae8d759c84fdf6c973c`.
- Ursprungsmatrix: `docs/research/cecilbot-analysis/exports/transfer-matrix.csv` im getrennten Analysecommit `24b8c8cd46f44781c84f97fd348fb9d1df155646`. Alle **41 Zeilen, Kategorien und sämtliche eingebetteten Originalfelder** stimmen mit [transfer-status.json](transfer-status.json) überein. Kein Codeverweis dieser JSON fehlt im geprüften Quellpin.
- Die deklarierte Matrix-SHA256 `43f5f6c81d91edddbc3e3ebaf05d0ac4e66b5881d7eddb65a383b9f13dad2407` bezeichnet die CRLF-Serialisierung. Der Git-Blob mit LF hat SHA256 `c8bb1b009b228ce89e79754273d6b07240973ccb329aadd190534fcd93b533e8`. Ausschließlich LF→CRLF reproduziert den deklarierten Hash; es liegt kein inhaltlicher Zeilenverlust vor.
- Die geprüfte Transfer-JSON hat SHA256 `7863347577f8e7defa23427ffc6fd259cd6a50728c7a565565b90507853c626f` und bleibt bewusst ein **df1ca40/Build010-Snapshot**. Ihre PASS-Angaben und Build010-Felder werden hier nicht auf c6662dac/016 umetikettiert. JSON und bestehender Plan wurden nicht geändert.
- Dieser Review umfasst Quellen, Testquellen und versionierte Berichte. Er startet weder Tests noch Runtimeprozesse. Die Offline-Spalte benennt vorhandene Prüfungen und den dokumentierten früheren Beleg; sie behauptet keinen hier neu ausgeführten c6662dac-Testlauf. Stubs, Headerverträge und Sanitizer ersetzen keine Retail-1.07-ABI-, CRC-, Kollisions- oder Netzabnahme.

## Leseschlüssel

**I** = Adapter implementiert; **V** = vorhandener Human-Pfad mit bewusster Adaption; **O** = Abnahme offen; **A** = architektonisch ausgeschlossen; **N/A** = für den vereinbarten FFA-Umfang nicht erforderlich. Native **OPEN** gilt für den finalen Kandidaten, auch wenn ältere Hashes begrenzte Einzelbelege besitzen.

Quellkürzel beziehen sich auf `poc/candidates/redstation-supply-20261107/`:
**N** [cecil_nav_data.h](../../../poc/candidates/redstation-supply-20261107/cecil_nav_data.h), **M** [cecil_motion.h](../../../poc/candidates/redstation-supply-20261107/cecil_motion.h), **B** [BotSupplyNative.h](../../../poc/candidates/redstation-supply-20261107/BotSupplyNative.h), **D** [BotDriver.cpp](../../../poc/candidates/redstation-supply-20261107/BotDriver.cpp), **H** [bot_human.h](../../../poc/candidates/redstation-supply-20261107/bot_human.h), **P** [bot_perception.h](../../../poc/candidates/redstation-supply-20261107/bot_perception.h), **R** [cecil_rules.h](../../../poc/candidates/redstation-supply-20261107/cecil_rules.h), **I** [BotCecilItems.h](../../../poc/candidates/redstation-supply-20261107/BotCecilItems.h), **F** [cecil_frame.h](../../../poc/candidates/redstation-supply-20261107/cecil_frame.h), **W** [bot_weapon_input.h](../../../poc/candidates/redstation-supply-20261107/bot_weapon_input.h).

Die Offline-Kürzel entsprechen den Evidence-IDs der Transfer-JSON: NAV, MOTION, FRAME, HEAD_BODY, BRIDGE, ACTION, HUMAN, INTEGRATION, ITEMS, RULES, SUPPLY und EXPORT. **Δ** markiert seit df1ca40 geänderte Adapter samt vorhandenen neuen Regressionsfällen; der alte PASS allein deckt diese Änderungen nicht ab. „Teilw.“ bleibt die bewusst begrenzte ursprüngliche Einstufung. EXPORT ist ein gesondert gepinnter historischer Tabellenbeleg.

## Vollständige Zuordnung

| ID | Originalbereich / Kategorie | Code und aktuelle Umsetzung / Grenze | Offline-Bezug | Native final |
|---|---|---|---|---|
| T01 | NAV-Dateien / A | I, N/B: vollständiger Parser; Map-/NAV-CRC-Bindung, keine eigene Kartengenerierung. | NAV | OPEN |
| T02 | Punktstruktur / B | I, N: Position, Radius, Flags, IDs, gerichtete Links, Important/Next/Lock bleiben erhalten; Pointer werden IDs/Slots. | NAV | OPEN |
| T03 | Gerichtete Verbindungen / B | I, N: ursprüngliche Richtung und vollständige Punktmenge; keine erfundenen Rückkanten. | NAV | OPEN |
| T04 | Punktradien / B | I, M: ursprüngliche Radien und gravitationsbezogene Ankunft. Tatsächliche Stockwerks-/Landeerkennung offen. | MOTION Δ, FRAME, BRIDGE Δ | OPEN |
| T05 | A*-Suche / C | I, N: bewusst Dijkstra/h=0 einschließlich Nullkosten und Locks; keine identische A*-Routenwahl behauptet. | NAV | OPEN |
| T06 | Nächster Navpunkt / C | I, B: begrenzte Sicht-/Höhenanker; gültige committed edge bleibt in Fluglücken erhalten. Neue physisch geprüfte Wiederannäherung ist noch keine erworbene NAV-Verbindung. | BRIDGE Δ, FRAME | OPEN |
| T07 | Important-Ziele / C | I, B/M: gewichtete Important-/Next-Ketten und geprüfte Entityreferenzen. Reale Bedienbarkeit/Kettenwirkung offen. | NAV, MOTION Δ, BRIDGE Δ | OPEN |
| T08 | Switch-/Marker-Events / E | I, B/D: normale USE-Press/Release-Actions und read-only Markeranker; kein SendToTarget/EET_TRIGGER-Ersatz. | BRIDGE Δ, ACTION Δ | OPEN |
| T09 | Locks / C | I, B/N: Placement-Snapshots; fehlende Entities sperren. Physische Locks und zeitweilige Meidung getrennt, Aktualisierung auch außerhalb gewöhnlicher Ankerdeckung. | NAV, BRIDGE Δ | OPEN |
| T10 | Teleport / C | I, N/M/B: gerichtete Nullkosten-NAV-Kanten; echte Trigger müssen durch Bewegung erreicht werden. Flag oder große Ortsdifferenz beweist keinen Teleporter. | NAV, MOTION Δ, BRIDGE Δ | OPEN |
| T11 | Jump/Crouch/Override / C | I, M/B/D: normale Walk/Jump/Crouch-Intents, Pulsabstand und finale Schutzprüfung. Flug-/Neutralbesitz korrigiert; Absprung, Kopffreiheit und Landung bleiben native Prüfungen. | MOTION Δ, BRIDGE Δ, ACTION Δ | OPEN |
| T12 | Auto-NAV-Generierung / D | N/A: gepinnte Daten für fünf Karten vorhanden. Allgemeine Generierung neuer Karten ist nicht implementiert. | N/A | N/A |
| T13 | NAV-Editor/Netzbefehle / E | A: kein Cecil-Editor und keine eigenen Editornachrichten im Vanilla-Netzverkehr. | N/A | AUSGESCHLOSSEN |
| T14 | Per-Bot Pfadzustand / C | I, B/D/H/P: getrennte Slotzustände und Lifecycle-Resets. Flugcommitment und Bewegungseigentum ersetzen keine Mehrprozess-/Rejoin-Abnahme. | BRIDGE Δ, HUMAN, INTEGRATION | OPEN |
| T15 | Stuck-Erkennung / B | I, M/B: Fortschritt/Holds/Meidung; zusätzliche Wiederannäherung mit festem Versuchslimit. Native Idle-Verletzungen älterer Kandidaten bleiben Fehler. | MOTION Δ, BRIDGE Δ | OPEN |
| T16 | Recovery-Bewegung / C | I, B/D/M: eine finale Recovery; neue Annäherung mit höchstens drei sichtbaren Originalpunkten, 6s Versuch/Backoff und 0,3-Achsengrenze. Keine Sackgassenfreiheitsgarantie. | BRIDGE Δ, FRAME, ACTION Δ | OPEN |
| T17 | Abgrundvermeidung / C | I, B/D: originales bAvoidPits bleibt maßgeblich; read-only 5/10m-Proben statt mutierendem 16m-WouldFall. Boden-Reacquisition verlangt zusätzlich stets tatsächliche Unterstützung. | BRIDGE Δ, ACTION Δ | OPEN |
| T18 | Schwimmen/Gravitation / D | I, F/M/B/D/H/P: Körper-/Gravitationsbasis und normale 3D-Swim-Actions; neue langsame Wasser-Reacquisition. Inversion und echte Wasserübergänge nicht aus Basisfixtures ableiten. | FRAME, HEAD_BODY, MOTION Δ, BRIDGE Δ, ACTION Δ, HUMAN | OPEN |
| T19 | Follow-Verhalten / C | I, B/D: eingefrorene Wahrnehmungsposition, ID/Generation/Ablauf; kein allwissendes Follow oder Coop-Catch-up. | BRIDGE Δ, HUMAN | OPEN |
| T20 | Gegnerauswahl / C | I, H/P: Cecil-Priorität auf freigegebenen Human-Beobachtungen, stabile Slots und Ziel-CD. Bewusste Reihenfolgenadaption. | HUMAN | OPEN |
| T21 | Team-/Monsterauswahl / C | I teilweise, D/P: Teamfilter und leere FFA-Teams vorhanden; Monster/Templates/Coop nicht Teil des Fünf-FFA-Umfangs. | INTEGRATION | OPEN, FFA-Anteil |
| T22 | Sichtprüfung / C | V, D/B/P: budgetierte Sicht und gespeicherte Weltpositionen; TT_COLLISIONBOX statt original TT_NONE. Modell-/Portal-/Gravity-Wirkung offen. | Teilw.: HUMAN, BRIDGE Δ, HEAD_BODY | OPEN |
| T23 | Zielgedächtnis/Timer / B | I, H/P/D: konsistente Beobachtung, Löschung bei Tod/Identitätswechsel; verdeckte Positionen bleiben eingefroren. | HUMAN, INTEGRATION | OPEN |
| T24 | Waffentabellen / A | I, R: 30 Originalzeilen einschließlich NONE; Scores sind keine gemessenen DPS. Coop-Daten nicht im FFA-Pfad qualifiziert. | RULES, EXPORT historisch | OPEN, Runtime-Nutzung |
| T25 | Waffenbewertung / B | I, R/I/bot_loadout.h: Besitz, Munition, Range und Double-Colt; Human-Hysterese bleibt bewusst erhalten. | RULES, ITEMS, INTEGRATION | OPEN |
| T26 | Waffenwechsel / C | I, W/D: ein Retail-Gruppenpuls nach Arbitration; aktuelle/gewünschte/entschiedene Waffe müssen zum Feuer passen. Animation/CD getrennt nachweisen. | INTEGRATION, RULES | OPEN |
| T27 | Feuer/Granate/Scope / C | I, R/D: Hold/Release und bestätigter Scopezustand; Actionzähler beweisen weder Projektil, Treffer noch Granatenabwurf. | RULES, HUMAN | OPEN |
| T28 | Aim/Vorhalten / B | I, H/P/F/D/bot_aim.h: Human-Bias/Settling plus Cecil-Grenzen und lokale Kopf-/Körperbasis. Hybrid, keine identische Cecil-Ballistik. | HUMAN, FRAME, HEAD_BODY, ACTION Δ | OPEN |
| T29 | Strafing/Distanz / C | I, H/R/B: Human-Persönlichkeit/Retreat und Cecil-Speed-/Strafe-Gates. Original-Strafingrating bleibt Datenreferenz, nicht identische Bewegungsformel. | HUMAN, EXPORT historisch, BRIDGE Δ | OPEN |
| T30 | Itempriorität / C | I, R/B: typisierte Bedarfsprüfung, rotierendes Kandidatenfenster und zusätzlicher gemappter Waffenweg für ungerüstete Bots; vertikale Präferenz ist eine bewusste Erweiterung. | RULES, BRIDGE Δ | OPEN |
| T31 | Itemkandidaten/LOS / C | I, I/B: Klasse/Masken/Hidden/Generation und geprüfte Konnektoren. Besitzgewinn, Zielmasken und Despawn getrennt; kein universeller ReceiveItem-Erfolgsbeweis. | ITEMS, RULES, BRIDGE Δ | OPEN |
| T32 | Reisemesser / B | I, R/D: erst nach >2s ohne Sichtkontakt, unabhängig vom Bewegungs-Override. Reale Travel↔Combat-Animation offen. | INTEGRATION | OPEN |
| T33 | Respawn / C | I, D/B: normale Fire-Flanken, Presetdelay und zuvor angehängte Source. Neue genaue Spawn/Death-Logs ergänzen die Messung; dead/respawns=0 ist Vorlauf, kein gescheiterter Spawn. | Teilw.: BRIDGE Δ, HUMAN, INTEGRATION | OPEN |
| T34 | Schwierigkeiten / A | I, R/H/D: vier originale Presets getrennt von Human-Skillstufen; Speed/Strafe/Jump/Pit angebunden. Darstellungsfelder sind keine KI-Abnahme. | RULES, EXPORT historisch, HUMAN, BRIDGE Δ | OPEN, aktive Werte |
| T35 | Configserialisierung / E | I, R/B: versioniertes Textschema statt raw sizeof(struct); Schema 1 wählt Preset, keine beliebigen Feldüberschreibungen. | RULES, EXPORT historisch | OPEN, Runtime-Laden |
| T36 | Controller als Modul / D | I, B/D/H/R/M: enginefreie Regeln mit read-only Snapshots und einer finalen Action-Komposition; kein Original-Entitycontroller als Drop-in. | HUMAN, BRIDGE Δ, INTEGRATION | OPEN |
| T37 | PlayerBot/EntitiesMP / E | A: keine PlayerBot-Subclass, kein ersetzter Dedicated-/Entities-Pfad; Originalhashes separat vor/nach Betrieb prüfen. | N/A | AUSGESCHLOSSEN |
| T38 | Netzpatch/Patcher / E | A: keine Cecil-Custommessage49, CPOL-Patcher oder Detours in diesem Adapter. | N/A | AUSGESCHLOSSEN |
| T39 | Lernen/Teamtaktik / U | N/A: im gepinnten Original kein entsprechendes Subsystem belegt; keine erfundene Transferlücke. | N/A | N/A |
| T40 | Native Gleichwertigkeit/Last / U | O: Build-/Messwerkzeuge sind vorhanden; weder Codeumfang noch kurze Beobachtungen erfüllen die eingefrorenen Runtime-Gates. | Teilw.; Gatewerkzeuge, keine Abnahme | OPEN |
| T41 | Coop-Catch-up-Teleport / E | A: kein autoritatives pen->Teleport. Getrennt von regulärem Follow und durch Bewegung ausgelösten NAV-Triggern. | N/A | AUSGESCHLOSSEN |

Zuordnung: **33 implementierte Bereiche, ein vorhandener adaptierter Human-Bereich, ein offener Abnahmebereich, vier Architektur-Ausschlüsse und zwei N/A-Bereiche = 41**. T21 enthält zusätzlich bewusst nicht übernommene Coop-/Monsteranteile. Dies ist eine Umfangsbilanz, keine Erfolgsquote.

## Änderungen und konkrete offene Punkte

Seit df1ca40 ändern sich im nativen Overlay hauptsächlich D, B und M. Der geprüfte Stand enthält neutrale Actions auf Ablehnungspfaden, Kandidatenfilter vor dem begrenzten Itemsnapshot, gerichtetes Routencommitment, gemappte Waffenakquisition mit festen Deadlines, Flug-/Neutralbesitz sowie begrenzte physische NAV-Wiederannäherung. Die [Entscheidung vom 09.11.](../../decisions/2026-11-09-cecil-resume-rollout.md) dokumentiert Anlass und Testgrenzen; neue Fälle liegen in `test_cecil_action_native.py`, `test_cecil_motion.cpp` und `test_cecil_native_bridge.py`.

Die echten Hindernisse sind **Qualifikationslücken und zuvor beobachtete Verhaltensfehler**, keine unbelegte technische Unmöglichkeit: 013 verfehlte den prospektiven Supplytest, 014 verlor während einer Ballistikkante die Bewegungsführung, 015 zeigte weiter eine unbestätigte Waffenroute und verletzte auf Hole die Idle-Grenze. Die c6662dac-Korrekturen adressieren diese Befunde, ihre native Wirksamkeit bleibt für 016 offen. Ein gestarteter kurzer Versuch oder ein neuer PE32-Build schließt keinen dieser Punkte.

Für die nächste Übergabe erforderlich:

1. Zuerst den festen Einzelbot-Supplykohortentest mit vollständigem frischem Log abschließen: erste zehn tatsächlich gewählte aufnehmbare Waffenziele, mindestens neun belegte Erreichungen; mindestens zehn Spawnbeobachtungen, Pickup-Median ≤15s und P95 ≤30s. Fehlversuche, Vorlaufzustände, Threatabbrüche und Zensierung sichtbar halten; Ownership-Gewinn, Zielidentität, Nähe und ursprüngliche Pickupsemantik gemeinsam bewerten.
2. Neue vollständige 1/4/8-Bot-Läufe ≥3600/3600/7200s auf **demselben finalen DLL-Hash**, anschließend normaler kontrollierter Wiederanlauf. Waffen-/Scope-/Explosivdistanz-, 100-Todesfälle-/Respawn-, alle fünf Map-/Sonderflag- und unveränderte Ressourcenbedingungen getrennt nachweisen. Alte Hashes, Bewegungsabsichten und UDP-Antworten ersetzen diese Belege nicht.
3. Original-Retail-Gameplay mit Originalkomponenten und dem finalen Kandidaten belegen. Frühere begrenzte Wine-Beobachtungen bleiben eigene Belege; sie werden weder als Windows-Abnahme noch als allgemeine WAN-/GPU-/Dauerqualifikation ausgegeben. Fehlendes Windows allein wird nach dem ausdrücklich autorisierten Wine-Fortsetzen nicht zum erfundenen externen Blocker.
4. Erst nach belegten Gates Release-Manifest und Main-Review, dann serieller Rollout mit Backup/Restore und anschließender gleichzeitiger 15-min-Flottenprüfung aller sechs Instanzen. Dieser Quellenreview stellt keine technische Rolloutfreigabe aus.

## Veröffentlichung und Erhalt

GPL-2.0-Herkunft und Copyrightvermerke der adaptierten Cecil-Quellen bleiben erhalten. Der separat im Original enthaltene CPOL-1.02-Patcher gehört zum ausgeschlossenen T38; er wird durch die GPL-Dateiverweise nicht in den zulässigen Portumfang einbezogen. Im geprüften flachen Overlay sind keine Patcher-Pakete, NAV-/WLD-Dateien oder Retail-DLL/EXE enthalten.

Weiterhin keine privaten NAV-Koordinaten/-Dateien, Retail-Binaries, Rohlogs, Profile, Tokens oder privaten Konfigurationen veröffentlichen. Öffentliche Nachweise bleiben bereinigte Berichte, Quellpins, Hashes und reproduzierbare Kommandos. Dieser Commit ergänzt ausschließlich diesen Bericht; bestehende Transfer-JSON, Plan, Quellcode und Runtime bleiben unverändert.
