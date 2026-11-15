# A1 nach005628: fehlende Cursorgrenze und normale Keyboardalternative

Status: reine Architektur-/Quellenbewertung, keine Umsetzung oder weitere
Runtime. Geschlossener vollständiger Datenaudit in
`docs/reports/2026-11-15-a1-xres-closed-005628-data-audit.md`; dessen FAIL bleibt
unverändert. Der unveränderte Pixelkalibrierpfad zeigte über mehrere getrennte
Läufe wechselnden Verbrauch. Einen weiteren gleichartigen uninstrumentierten
Kalibrierversuch rechtfertigt dieser Befund nicht.

## Kleinste fehlende Messgrenze

Vorhanden: originale GetCursorPos-/SetCursorPos-Returnquittungen, vollständige
ausgewählte X11-Requests/Replies mit eigener PIDzuordnung und tatsächliche
native Winkel-ACKs. Fehlend: **welcher originale Get/Set-Aufruf verwendete welchen
Winecursorzustand beziehungsweise erzeugte welchen konkreten Xclientrequest?**
Die InputIDs257/259 haben keinen X11-Sequenzanker. Receipt-/JS-/Xserverzeiten
werden nicht zur scheinbar exakten Zuordnung umgerechnet.

Lokal vorgefunden: Wine/libwine9.0~repack-4build3. `/usr/src` ist leer;
`/usr/share/doc/{wine,libwine}` enthalten Dokumentation, aber keine benötigten
C-Funktionsquellen. Kein `/usr/lib/debug/.build-id` vorhanden. Die statisch
gelesene installierte i386-Unixdatei
`/usr/lib/i386-linux-gnu/wine/i386-unix/winex11.so`, SHA256
`a82d317ae74e0e8c31defdec9fac10738eeb9d18e0c683de0dfebe98cdc549bc`,
importiert XQueryPointer/XWarpPointer/XFlush/XSync. Die dynamische Symboltabelle
liefert keine benannten internen X11DRV_Get/SetCursorPos-Funktionen. Diese Imports
belegen keine ausgeführte Cache-/Treiberverzweigung.

Wine9.0-Primärquellen liefern konkrete mögliche Grenzen:

- [`dlls/win32u/input.c`, Zeilen677–733](https://github.com/wine-mirror/wine/blob/wine-9.0/dlls/win32u/input.c#L677):
  get_cursor_pos liest einen Wine-Servercursorwert; ein Treiberquery folgt erst
  bei entsprechend altem last_change. SetCursorPos reicht einen erfolgreichen
  Serveraufruf nur bei geänderter Position an den Treiber weiter.
- [`dlls/winex11.drv/mouse.c`, Zeilen1272–1317](https://github.com/wine-mirror/wine/blob/wine-9.0/dlls/winex11.drv/mouse.c#L1272):
  Treiber-GetCursorPos verwendet XQueryPointer; Treiber-SetCursorPos erzeugt einen
  Warp mit anschließendem Flush. Das ist ein upstreamQuellbefund, keine
  bytegenaue Qualifikation des installierten Ubuntu-Builds oder Runtimeursache.

Die kleinste unterscheidende nächste Messung wäre daher eine passive per-Aufruf-
Quittung **vorhandener** Get/Set-Ausführung im eigenen Prozess: Cachewert und
last_change/gewählter Treiberzweig beim Get; prev/new und tatsächlicher
Treiberaufruf beim Set; beim tatsächlich erreichten Xlibpfad dieselbe Verbindung
und deren natürliche Requestsequence. Keine zusätzlich ausgelöste Query, kein
Flush/Warp/Messagepump als Intervention und keine neue Eingabe. Erst diese
Grenze könnte zeigen, ob der zweite Read einen Server-/Winecachewert wiedergibt,
der Driver schon geantwortet hatte oder die Recenterweitergabe noch ausstand.

Das ist noch kein fertiger sicherer Hookplan: installierte Funktionskörper,
Dispatcher-/Prototypen und Branchstellen müssen zuerst anhand passender
Distributionsquelle/Bytes oder eigener Methodenqualifikation gebunden werden.
Ohne diese Zuordnung lautet das Ergebnis MISSING_BOUNDARY, nicht Wine-Bug.
Erst ein begrenzter eigener Wegwerfprozess-Reproducer, danach gegebenenfalls ein
separat geprüfter minimaler Originalfall; keine autonomen Folgefenster. Zusätzliche
Hooks/Overhead oder eine neue Uhrheuristik dürfen den fehlenden Beleg nicht ersetzen.

## Alternative: normales Keyboardlook mit Geometrie-ACK

Eine konkrete lokale Grundlage existiert in der archivierten unveränderten
Originaldatei `controls-profile-before.ctl`, SHA256
`5d525c46993be88d45941fe14f4638fa001ba9583d1151a27d6df9129d9b9d9b`:
Turn Left/Right haben Key1/Key2=None; Look Up/Down sind auf Mouse Button4/5
gelegt. Ihre Press-/Releasekommandos setzen die vier ctl_bTurnLeft/Right/Up/Down-
Werte auf1/0. Die unveränderte RetailEntitiesMP.dll mit SHA256
`7f595f2a7fc96a978b3467983e8f17c70d827f17a5f4ee887f9c7a1f20b1d350`
enthält tatsächlich deren vier `user INDEX`-Shelldeklarationen. Kein lediglich
aus OpenSource1.10 angenommener Variablenname. Statisch nicht bewiesen ist hier
der vollständige native Button→Pitch/Yaw-Datenfluss oder dessen Winkelgranularität.

Ein eigener reversibler Originalprofilversuch könnte ausschließlich diese
vorhandenen Aktionen auf freie normale Tasten legen. Zwei begrenzte Gegenrichtungen
pro Achse, echte Down/Up- und Neutralquittung, korrektes Profil/Fokus/PID/Life,
nativer kumulativer Achsen-/Viewpoint-ACK und anschließende unveränderte
Geometrieprüfung wären ein prüfbarer Vorbereitungsweg. Er benötigt eine neue
explizite Inputscope-/Methodenentscheidung; bisherige Maus-Pixelgainprüfung darf
nicht heimlich umgangen oder deren FAIL grün umetikettiert werden.

Weder die bestehende ACK-/EPS-/Geometrietoleranz noch Deadline, Inputholdgrenze
oder Aktionsbudget werden dadurch automatisch größer. Ist der kleinste echte
Keyimpuls für die vorhandene Winkelgenauigkeit zu grob oder lässt sich Release
nicht nachweisen, scheitert diese Alternative. Ein erfolgreicher geometrischer
Vorbereitungsweg wäre ein neuer begrenzter Nachweis und kein Beweis reparierter
Mausverarbeitung, `input_once`, Respawnschaden oder vollständiger A1-Abnahme.

Entscheidung jetzt: Datenaudit abschließen, beide Optionen Root zur Auswahl
vorlegen; keine neue Implementierung, Hookregistrierung, Profileingriffe,
Paketeinstallation oder Methode durch diesen Agenten.
