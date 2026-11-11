# 250 zusätzliche Namen für Meilenstein A2

Der bestehende Pool enthielt **208**, nicht 100 Namen. Alle Einträge bleiben
unverändert und in derselben Reihenfolge erhalten. Der vollständige Pool enthält
jetzt **458** Namen. Genau 250 zusätzliche, fiktive sichtbare Aliasse kollidieren
weder untereinander noch mit dem Altbestand nach Formatentfernung und
Groß-/Kleinschreibungsnormalisierung. 25 Ergänzungen tragen Clan-Tags, 25
dezente Zahlensuffixe; die übrigen Kategorien umfassen kurze Aliasse, Leetspeak,
Bewegung, Technik, Natur, Astronomie und spielerische Wortkombinationen.

`poc/scripts/GamingNicknames.baseline.json` erhält die ursprünglichen Dateibytes
aus dem Namenspool des AI2-Worktrees. SHA256:
`cdd04932790ed8ba0d06cffd524c9cd11fadd4b370de11cb02d95303caa13b26`.
`GamingNicknames.additions.source.json` enthält die einmal redaktionell erzeugten
250 Aliasse. `GamingNicknames.json` bleibt eine Liste einfacher Namen für die
vorhandene Poolarchitektur. `GamingNicknames.additions.json` ergänzt getrennte
Namens-IDs und geeignete native Darstellungen. Die Metadaten binden Dateien,
Zahlen, Limits und den festgeschriebenen Seed **20261111**. Die Stilwahl basiert
auf SHA256 und ist unabhängig von Python-Zufallszahlengeneratorversionen.

Die Ergänzungen enthalten 147 unformatierte Namen, 45 mit Farbe, 26 mit
Farbe/Fettschrift, 25 mit Farbe/Kursivschrift und sieben mit beiden Schriftstilen.
Die längste Ergänzung hat 15 sichtbare Zeichen beziehungsweise 30 ASCII-Bytes
einschließlich Formatierung. Es gilt weiterhin die konservative Projektregel
von höchstens 22 sichtbaren Zeichen und 32 Rohbytes; das ist keine behauptete
Engine-Puffergrenze. JSON-/Konsoleninjektion, Steuerzeichen, Anführungszeichen,
Backslashes und unvollständige Formatcodes werden verworfen. Stile werden
explizit geschlossen; formatierte Namen enden mit `^r`.

## Originalparser und bewusste Formatgrenze

Die historische echte Retail-Prüfung vom 25.10.2026 verwendete die originale
Engine-DLL mit SHA256
`b79bf8bb3927fe4f8f252e141d721ae5c738df02218f0ecc12da5c1afbcb534f`.
Die Exporte `CTString::Undecorated` (RVA `0x7120`) und `LengthNaked`
(RVA `0x70e0`, Imagebase `0x600c0000`) akzeptierten `^cRRGGBB`, `^b/^B`,
`^i/^I`, `^r` und Kombinationen. Die bereinigten neun Resultate mit
Quell-/Berichtshash sind in `GamingNicknames.parser-evidence.json` erhalten.
Die Herkunft ist Commit `710b059d8441e4b949d5251d0b25d8d25eb47342`,
`docs/reports/2026-10-25-bot-ai2-results.json`, Feld `original_decoder`;
der damalige reproduzierbare Aufrufcode heißt `tools/probe_retail_namecodes.cpp`.
Die aktuelle Dev-Konfiguration enthält zusätzlich tatsächlich verwendete
Farb-/Bold-/Italic-Namen; ihre bloße Präsenz ist keine neue Renderingprüfung.

**Flash/Blink wird nicht erzeugt.** Die originale Engine dekodierte
`^f3NIGHT^F^r` zu `IGHT`; bei nachfolgender Farbe verlor sie ebenfalls ein Byte.
Die Ergänzungen enthalten daher null Flash-Namen, statt vermeintlich
unterstützte Syntax zu erfinden. Für Flash-Wünsche steht der einfache
`nickname` als Ersatzdarstellung bereit. Bei der rein lesenden Vorprüfung
enthielten vier vorhandene Red-Station-Profile dennoch Flashcodes. Dieser
Legacy-Befund wird nicht durch Ändern bestehender Profile kaschiert.

## Flottenweite Zuteilung und Betriebsgrenze

`tools/gaming_names.py` liefert ausschließlich eine Offline-Zuteilung.
Stabile Bot-IDs werden vom Betreiber übergeben, beispielsweise
`redstation:botA:0`; sie sind unabhängig von Name, Format, Namens-ID und
Retail-Spieler-GUID. Bestehende Zuordnungen werden bei erneuter Übergabe
unverändert erhalten. Der Allocator prüft normalisierte aktive Namen über die
gesamte Flotte, sortiert Bot-IDs deterministisch und bricht bei Namensmangel oder
einer bestehenden Kollision vollständig ab. Er setzt keine Profile und startet
keine Prozesse. Einzelbot-Sitzungssteuerung aus Meilenstein B wird nicht eingeführt.

Aktive fremde Anzeigenamen sind ausschließlich Ausschlussdaten. Sie müssen
unsere Richtlinien für neu erzeugte Namen nicht erfüllen; Länge, Unicode,
Sonderzeichen und Rand-Leerzeichen führen deshalb nicht zu einer Umbenennung
oder Ablehnung des Spielers. Bekannte Formatcodes werden entfernt und
Rand-Leerzeichen konservativ normalisiert. Unbekannte Formatcodes einschließlich
Flash werden nicht geraten: dafür sind die tatsächlich dekodierten Namen aus
der aktuellen Serverabfrage zu verwenden.

Vor der Anwendung muss Main unter dem exklusiven Deployment-Lock eine frische
Abfrage aller Instanzen durchführen, die vollständige Flotte gemeinsam
zuordnen und die Bot-IDs/Zuordnungen privat persistieren. Bei `existing` dürfen
die eigenen bereits gebundenen Namen nicht zugleich als fremd belegt übergeben
werden; neue fremde Kollisionen führen zu einem Fehler. Parallel getrennt
berechnete Vorschläge sind keine Kollisionsgarantie. Die Query ist zudem nur
eine Momentaufnahme, weshalb nach tatsächlichem Join erneut zu prüfen ist.

```bash
python3 -B tools/gaming_names.py
python3 -B -m unittest discover -s tools -p test_gaming_names.py
python3 -B tools/gaming_names.py --request /private/fleet-name-request.json
```

Die Request-Datei enthält `bot_ids`, `occupied_names` und optional `existing`
als vorige vollständige Zuteilung. JSON-Ausgabe erfolgt auf stdout und wird
vom Betreiber privat gespeichert. `--generate` erzeugt die drei abgeleiteten
Repository-Dateien aus den fixierten Eingaben neu; keine Runtime-Datei wird
dadurch verändert. Vor jeder Zuteilung wird das gesamte Bundle gegen die
festgeschriebenen Eingaben geprüft.

## Nachweis und offener Rest

Portable Prüfungen decken Originaldecoder-Beispielfälle, Flash-Ablehnung,
Kollisionen durch Großschreibung/Formatierung, Längen-/Injection-Grenzen,
stabile Flotten-IDs, belegte Namen, Erschöpfung, CLI-Ausgabe, Manipulation und
byteidentische Reproduktion ab. Der erste Testlauf scheiterte wie erwartet
vor Implementierung; der externe Anzeigename mit Rand-Leerzeichen wurde als
eigener Fehlerfall vor der Korrektur reproduziert.

Eine zusätzliche lesende Probe erzeugte einen kollisionsfreien Vorschlag für
48 Bot-IDs unter Ausschluss von 50 aktuell per lokaler GameSpy-Abfrage
gemeldeten Spielernamen. Die privaten Namen und Zuordnungen stehen nur in der
privaten Evidence-Ablage. Das ist keine Installation und keine Zusage über
spätere Namen oder externe Masterlist-Caches.

**Neue native Darstellung jeder verwendeten Formatart und externe Query-Abnahme
der Ergänzungen bleiben OPEN.** Die historische Parserprüfung wird nicht als
neue Runtime-Abnahme ausgegeben. A2 ist quellseitig vorbereitet; aktive
Namen, Spieler-GUIDs und Laufzeitprofile wurden nicht geändert.
