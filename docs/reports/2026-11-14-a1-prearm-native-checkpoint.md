# A1 Prearm-XTest: Bibliotheksguard passiert, Gain weiter FAIL

Das einzige Original-NoFire-Fenster222350 bleibt **FAIL**:
`opposite normal look does not reproduce body response: action gain`.
ResultSHA `957d68ce2f306d89dc0839ffd1abcd7d613c92b16aed64f459f91fb4ea72a446`.

XTestQueryExtension2.2 und XSync liefen vor Recorderarm auf derselben Verbindung.
Alle vier tatsächlichen Calls verbrauchten jeweils genau einen Request:
32→33(Rel+12),46→47(KeyDown),50→51(KeyUp),64→65(Rel−12).
Die drei ausgeführten Eingabephasen wurden freigegeben; Input-bis-Release
0,131603/0,165562/0,149011s bleibt unter unverändertem350ms-Limit.
Vorbereitungszeiten sind darin ausdrücklich nicht als gehaltene Eingabe enthalten.
Die früheren Cold5-Fehlschläge bleiben FAIL; dies ist deren neue begrenzte
Abgrenzung, keine nachträgliche Umwertung und keine A1-Schadensabnahme.

Der geschlossene Trace enthält152Records/43816B, vier gebundene Emissionen,
vierDevice- und vierDelivered-Motionrecords.130Queryrecords und zweiWarp-
Requests bleiben nicht dem Originalprozess zugeordnet. ZweiCoreunknowns bleiben
in dessenZähler erhalten; derAdapter typisiert diese separat alsNoncursor-
Key-XTEST.0Malformed/Drop, alle152Records freigegeben, RecorderExit0/noForce.
RawSHA `2507870424b2410e7f751d9a1f46e41dbfa4ffa42a8b94fc293db017160ce2ef`.
Keine Behauptung über vollständigesXI2, Geräteursprung oder gleicheX-/JS-/Hostuhren.

Collector bestätigt Originalbyteswiederherstellung; eigener Reader nachCleanup
perSIGTERM beendet/reaped. Drei reguläre Rollencloses, Root664Dateiinhalte/
Eigentum/Modus/Dateimengen+achtAbsenzen+dreiSchlussloghashes und verschwundene
Displays unabhängigPASS_RESTORE. Keine neuen Schlusslog-Sync-/Crash-/Joinfehler.
CPU-Intervallmaximum71,321696%, RAMMinimum2811039744B, DiskMinimum10375831552B;
26,809067sMesslücke, keineformaleBudgetabnahme.

Die vollständige Input→Action→ACK/Body-/RECORD-Zuordnung folgt als eigener
Datenreview. Kein erneuter Nativeversuch ohne konkreten daraus abgeleiteten
Prüfgrund; keine Lockerung vonGain/ACK/EPS/Fristen. A1offen, Aoffen, Bnichtbegonnen.
PrivateBelege: E/a1-xtest-preparation-20261114-222350 und RootEV/
`a1-xtest-preparation-closed-summary.json` SHA
`858dffe89c5a98b38ab27cdfd4592b6eaed8b4584438afb2972fb992e9ad9e79`.
NeueRaws benötigenDelta054; vorherigeQuellen/Freeze/Parent liegenvollgeprüftin053.
