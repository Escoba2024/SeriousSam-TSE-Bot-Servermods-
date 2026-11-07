# Exportpaket

## Öffentliche Dokumentationsfassung
Berichte, Matrix (41 Bereiche), Einstellungen (119 Zuweisungen), Waffen (30 Einträge), NAV-Aggregate/Hashes, Quellfunktionsindex (133 lexikalisch erkannte Definitionen), Dateiinventar, Konsolen-/Hotkeydeklarationen und Analysewerkzeuge. Commands sind nur Quelltextdaten, nicht ausgeführte Administrationsaktionen.

## Vollständiges privates Analysepaket
Zusätzlich reference/ mit unveränderten ausgewählten Originalquellen und allen neun NAV-Dateien; exports/<Map>.json, .points.csv und .edges.csv. JSON erhält FLOAT32-Werte verlustfrei in Zahlenrepräsentation, alle Slots/IDs/Links/Flags/Lockorigin-/Polygonfelder. CSV ist eine ergänzende tabellarische Sicht; JSON ist das vollständige Datenschema. Keine erfundenen Wege, Waffentypen oder Itempositionen.

## Reproduktion und Grenzen
fetch_reference.py lädt nur die mit Commit und SHA256 gepinnten öffentlichen Referenzen, validiert vorhandene Dateien und überschreibt sie nicht. export_analysis.py prüft das Referenzmanifest, liest alle neun Dateien vor Ausgabe und verweigert vorhandene Ziele. export_rules.py extrahiert Originaltabellen und validiert Anzahl/IDs. Keine Installation oder Spielsteuerung.
Die übernommenen Parserfunktionen walk_subset/to_graph_text bleiben als historische Hilfen erhalten, werden vom vollständigen Analyseexport NICHT verwendet. Sie sind keine 1:1-Konvertierung. Ältere Kommentare in diesen Hilfen zur NAV-Lizenz sind keine abgeschlossene Rechteklärung; ARCHITECTURE.md ist die aktuelle Einordnung.

## Bedien-/Lifecycle-Inventur
BotModMain initialisiert Navmesh, Modelle und Netzpatch, lädt beim GameStart eine NAV und räumt bei Cleanup Graph/Botliste. Fehlendes NAV wird protokolliert, nicht automatisch durch eine neue vollständige Karte ersetzt. Botnamen/-skins sind Listen; sie sind keine Personality-KI. Gedankenanzeige und NAV-Overlay dienen Debugging/Editing. Scripts/Game_Startup.ini setzt Standardlevel und CecilBots-Modname; Hotkeys rufen Mod-/NAV-Funktionen auf. Diese Lifecycle-/UI-/Netzbefehle werden nicht auf die produktive Clientarchitektur übertragen. Vollständige zugängliche Deklarationen mit Datei/Zeile stehen in commands.json; weitere Botdefinitionen im function-index.
