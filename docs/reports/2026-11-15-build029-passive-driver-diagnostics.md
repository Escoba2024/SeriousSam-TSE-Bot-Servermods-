# Build029: gebauter Diagnosekandidat, noch kein Gameplay-Pass

Quellcommit `7dfda985fe547cf6496cc18aaa713568fafcc9fa`, Baum
`a8aa60561d0c642346eaac4f6784e85eb0546427`.
DLL SHA256 `a043de1e0fc647d2805c20ea01e9f52eada3fdaa0b55caad8be6df5302ded971`,
451584Bytes. Buildmanifest
`aed7a9325b1cfe3af3cb77ca897901e48236de83d9b5ff0bb5d48eab23e046a9`.
15MSVC-Übersetzungen und Link erfolgreich; Root hat48Quellen/29Overlaydateien
plus Manifest/DLL vollständig gegen79tatsächliche Hashwerte geprüft.

Gegenüber028 sind nur BotDriver.cpp und der neue reine Receipt-/Formatheader
anders; der028Supplyheader bleibt bytegleich. Keine beabsichtigte Gameplayänderung.
Die neue Diagnose erfasst im selben Aufruf Navigationsempfehlung, tatsächliche
Arbitration, bestehende Waffenwahl-/Fire-Pollwerte, SafeMotion-Ein-/Ausgaben
und exakt das an SetAction übergebene Translation-/Rotation-/View-/Buttonargument.
Sie läuft nur mit Diagnose1 am bisherigen20-Tick-Termin. Alte Diag0-Ausgaben
und ihre Takte bleiben erhalten. Eingangsmodus/Cacheziel und Nachmodus sind
getrennt, ebenso nicht betretene Supplyblöcke und Ready=false.

Rootreview schloss vier fehlende Angaben vor dem Build: echte LastButtons aus
dem einen vorhandenen Pollargument, Arbitrationflags, PreSupply-Feuer-/Aimmodus
und Cacheziel sowie getrennte Block-/Ready-/Callzustände. Die vollständige
exakte Driverinverse rekonstruiert028/027 mit SHAebb2c4cc694ebdc1ee8f9e2e1aa88a2cb587afae5adc649bfcae84ff244c6c55.
Root9gezielte Tests0,323s PASS:14tatsächlich extrahierte Driverfälle,28Werte
Diag0/1gleich,12Driver-Mutanten und unveränderter.5Safetygegenfall.
Erster Rootaufruf scheiterte an fehlendem PYTHONPATHfür ein bestehendes
Testmodul; Fehlerlog separat erhalten, korrigierter Aufruf vollständig grün.
Keine Produktionstoleranz wurde geändert. Frühere Author-Stubcompilefehler
bleiben ebenfalls erhalten. Der ältere Action-ASan-PASS liegt vor den vier
Metadatenkorrekturen und wird nicht als aktueller Gesamttest übertragen.

Zeilenformat %.17g; kompilierter Extremfall1207Bytes, unabhängige konservative
NUL-Grenze1394<2048. Keine zusätzliche Engineabfrage, Ray-, RNG-, Clock- oder
Polloperation. Tatsächliche Laufzeitkosten bleiben im nächsten Spieltest zu messen.
CachedMapPin ist ausdrücklich kein aktueller Mapnachweis; MapKnown=false.
Generation-/Actorwechsel bedeutet UNKNOWN, fehlende/nicht gesampelte Aufrufe
werden nicht interpoliert. Ein SetAction-Argument beweist keinen ACK, Treffer
oder tatsächlich ausgeführte Bewegung.

Nächster Fall: genau ein neuer isolierter Skulls600-Diagnoselauf, erst nach
Controllerreview/Freeze/Vollsicherung. Der Retargetcontroller wird separat
vorbereitet; er erhält die eng geprüfte Cgroup-Exitkorrektur und ein begrenztes
privates Cleanupfehlerprotokoll. Kein Autoretry, kein Rollout, A bleibt offen.
