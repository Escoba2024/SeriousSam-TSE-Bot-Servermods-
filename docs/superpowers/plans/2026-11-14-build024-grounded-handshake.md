# Build024: frischen Bodenhint nach veraltetem Anker nativ prüfen

> executing-plans; Root integriert, baut und verändert allein die Runtime.

**Ziel:** Den SDK-reproduzierten falschen GroundedReplan-Abbruch eng korrigieren
und mit einem neuen Retailkandidaten tatsächlich prüfen. Gemischte Liveflotte
bleibt gemäß letzter Nutzerentscheidung erhalten, bis Verbesserung belegt ist.

**Architektur:** Unveränderte aktuelle Sicht-/Support-/Geschwindigkeits-/Höhen-/
Sperr-/Graphprüfungen bestimmen einen frischen Hint. Erst nach erfolgreicher
Prüfung ersetzt er den gehaltenen Anker; Navigatorreset verlangt anschließend
weiter die ursprüngliche Radiusankunft. Keine künstliche Waffenaufnahme,
Acquisition-/Arrival-/Floorfreigabe oder erneuerte Zieldeadline.

**Technik:** Bestehende SDK107-Brücke und ASan/UBSan, bestehender gepinnter
MSVC/Wine-x86-Builder, neuer Build-/Evidence-/Paketnamespace, reguläre eigene
Retailprozesse auf isoliertem Port27850. Dedicated/Original bleiben original.

**Spezifikation:** Gesamtauftrag A3/A4/A5, geschlossene023-600/180-Diagnosen,
SDK-Reproduktion3274/2 und neuer enger Fixplan des A4-Workers.

- [x] Workerfinalisierung prüfen; vollständiger Produktionsdiff und geänderte
  Testerwartungen nach belegtem RED, verbleibende Sicherheitsvetos unabhängig
  lesen. Reine SDK-/Sanitizerchecks sind keine Retailabnahme.
- [x] Getrennte saubere Commits integrieren; relevanten Source-/Testpins
  nachhashen. Vollständigen normalen SDK-Lauf am integrierten Stand prüfen.
- [x] Neues024-Verzeichnis mit bestehendem Builder unter Build-/Runtime-Lock,
  frischen Quieszenz-/Prefix-/Datenträgerprüfungen erstellen. Quellcommit/tree,
  sämtliche Quellen, PE32-x86, DLL und Manifest erfassen. qualified=false.
- [x] Bestehendes deaktiviertes023-Red600-Paket ausschließlich auf echte024-
  Herkunft und getrennte Namespaces retargeten. Bedingungen unverändert:
  Hard, acht DEMON, Original20FPS, diag0,600s, keine automatische Wiederholung.
  Exakten reversiblen Delta und tatsächliche DLL-/Quellenpins prüfen; Rootfreeze.
- [ ] Neue Quellen veröffentlichen, Remote tatsächlich fetchen/tree vergleichen;
  geschlossene neue Belege und Wiederherstellung privat Drive-sichern/rücklesen.
- [ ] Nach frischer Belegungs-/Ressourcen-/Sperrprüfung genau ein eigenes024-
  Redfenster mit unabhängiger äußerer Hostbeobachtung starten. Keine gleichzeitige
  Kompilierung/Archive/andere Native; Public und Dev unverändert.
- [ ] Alle Rollen regulär schließen, exakt gebundene Module/Map/Bots prüfen;
  Fehlerdifferenzen, Bewegung, Leben, Waffenbesitz/-aufnahme, natives Feuer,
  Schaden/Kills und tatsächliche GroundReplan-/Radius-/Zielketten auswerten.
  Null beobachtete neue GroundReplans sind kein Wirksamkeitsnachweis des Fixes.
- [ ] Geschlossene Dateiinhalte/Metadaten/Absenzen/Logs/Prozessgenerationen und
  Displaycleanup unabhängig prüfen. Fehlgeschlagene Prüfungen erhalten.
- [ ] Nächsten Schritt aus echten Daten entscheiden: konkreter weiterer Fix,
  verbleibende Karten-/A3-/A1-Abnahmen oder begründete Devpromotion. Keine bloße
  höhere Buildnummer oder erfolgreiche Kompilierung als Fortschrittsbeleg.

Reviewfokus: alternative gültige Bodenhints trotz alter Anchorfixture;
veraltete/ungültige Support- und Sperrzustände; unveränderte Zielzeit und
Radiusankunft; begrenztes Querybudget; Nativeunbekannte nicht nachträglich als
SDK-Eingaben behaupten. Formal1/4/8-Bot-Stunden bleiben offen und beginnen erst
für einen dazu geeigneten Kandidaten. A offen, B nicht begonnen.


15.11.2026,00:23UTC: Red600 tatsächlich geschlossen (Resultc6bcb9ae), Rootrestore640+4PASS und685äußereHostproben. Vollständige native Wirkungsanalyse noch offen; keinePromotion. Siehe geschlossenen Build024-Bericht. Neue024-Rohdaten benötigen058,057sicherte nur Vorbereitung.
