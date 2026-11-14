# Getrennter eigener XRecord-Methodenbeleg

**Goal:** Tatsächliche RECORD-/XTEST-Fähigkeit und begrenzte Core-Request-/
Motionaufzeichnung auf einem eigenen Wegwerfdisplay prüfen. Keine TSE-
Integration und keine vollständige X11-/XI2-/Cursorcachequalifikation.
**Architecture:** Root besitzt ein neues Xvfb und zwei eigene Exec-Kinder:
Recorder mit ausschließlich eigenen Steuer-/Datenverbindungen und ein
Methodentreiber für bekannte normale Xlib-/XTest-Operationen. Xlib bleibt
in den begrenzten Kindern. Keine Paketinstallation/Bibliotheksersetzung.

Primärbelege und Grenzen stehen in
`docs/reports/2026-11-14-a1-xrecord-inventory-method-design.md`.
Autorenarbeit bleibt offline; Root allein startet und schließt Methodenprozesse.

- [ ] In eigenem Worktree reine Parser-/Struktur-/Protokoll-/Lifecycletests
  vorbereiten. Während fremder Rootmessfenster ausschließlich Testtext und
  Design schreiben; keinerlei Tests, Scans, Generatoren oder Xlibaufrufe.
- [ ] Nach geschlossenem Rootfenster diese Tests RED ausführen, dann kleinste
  deaktivierte ctypes-Bindung aus geprüften offiziellen Headern implementieren.
  Native Strukturgrößen und Wireformat getrennt; dynamische Extensionopcodes,
  Endianness, 4-Byte-data_len, Kategorien und Längen streng behandeln.
- [ ] RECORD und XTEST-Version, StartOfData und ausgewählte Ranges tatsächlich
  erfordern. Core QueryPointer38/Antwort, WarpPointer41, XTEST-FakeInput2 sowie
  Core-Motiongeräte- und zugestellte Motionereignisse separat erfassen.
  Kein GenericEvent-/XI2-Vollständigkeitsclaim. Nicht abgedeckte oder unbekannte
  Daten ausdrücklich zählen; malformed/überlang/Overflow bleibt FAIL.
- [ ] Limits vor Ausführung: Recorderhöchstlauf15s,1024Records/2MiBGesamt,
  maximal16384Bytes je Record, Arm3s, Stop3s; Treiberoperationen je2s,
  gesamter Methodencontroller30s plus geordnete Cleanupfristen5s je Kind/Display.
  Frische Exec-Kinder/PID-Start-/argv-/Displaybindung; IPCtimeout stickyFAIL.
  Keine unbeschränkten Xlibaufrufe im rollenbesitzenden Parent.
- [ ] Root prüft/friert ein, belegt exklusive Methodensperre und einen freien
  eigenen Displayplatz (vorgesehen167; bei Belegung FAIL). Nur Xvfb-nolisten-tcp,
 800×600. Andere Displays und alle Wine-/Frida-/TSE-Prozesse bleiben unberührt.
- [ ] Bekannte Methodenfolge: Treiber verbindet/initiiert Zentrum400,300 vor
  Recorderarm; genau eine+12relative XTest-Anfrage, methodeneigene QueryPointer-
  Bestätigung412,300; anschließend genau ein Warp400,300 mit eigener Bestätigung.
  Jeweils tatsächliche Request-/Motionbelege abwarten, begrenzt und ohne Retry.
  device/delivered-Kopien niemals als zwei Bewegungen addieren; Clientbasis
  ist kein PID, eigene Clientbindung nur durch tatsächlichen Beleg.
- [ ] Normal Disable/EndOfData/FreeData/FreeContext/Verbindungsclose sowie
  eigene Kind- und Displayenden prüfen. Timeout darf ausschließlich präzise
  eigene Methodenkinder aufräumen und bleibt FAIL. Alle Rohrecords privat,
  vollständige Dateihashes und Ressourcenkosten erfassen.
- [ ] Maximaler Erfolg `PASS_METHOD_PARTIAL_CORE_REQUESTS_ONLY`; kein A1-,
  Steuerungs-, vollständiger XI2-/X11- oder Retail-PASS. Erst danach eigener
  neuer Rootplan für einen passiven TSE-Beleg, ohne neue Gameplayeingaben oder
  Pointerabfragen und mit klarer Beobachtereffektkontrolle.

Server-/Host-/JS-Zeiten bleiben getrennt. Requests beweisen keine erfolgte
Pointerposition; fehlende Coreereignisse beweisen keine Abwesenheit von XI2.
Der A1-Gainfehler bleibt FAIL und seine Toleranz wird nicht verändert.
