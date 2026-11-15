# Original-Respawn030: frische Ownershipbelege pro Rollenread

Der geschlossene F2-Control scheiterte vor Input im ersten zusätzlichen
`_sample` der bereits konstruierten MethodWindow, beim zweiten
`native_roles`-Aufruf: `NAI.capture_ownership` schreibt seinen absichtlich
exklusiven Beleg `natural-ai-ownership.json`. Der initiale Methodframe hatte
bereits denselben Pfad belegt. Fall17:30:07 und alle älteren Pakete/FAILs bleiben
unverändert; dies ist ein eigener Integrationsfehler, keine Readinessursache.

Die neue ausschließlich RP-eigene `OwnershipReads`-Hülle umfasst den Initialframe
und alle Folgeproben. Jeder Callback bekommt ein frisches0700-Verzeichnis unter
`respawn-role-reads/0001..1024`. Die tatsächliche allgemeine NAI-Capturequelle,
ihre Hash-/GMS-/Log-/Rollenprüfungen und O_EXCL0600-private_json bleiben gleich.
Es gibt keinen gecachten Ownershipbeleg. Der Callback schreibt seinen neuen
Beleg auch bei einem tatsächlichen Validatorfehler wie bisher im finally.

Das gemeinsame Readbudget ist1024 einschließlich Initialframe. Die
Receiptpayloads zusammen sind auf3MiB begrenzt, exakt zweimal das bereits
bestehende Einzelmaximum1536KiB. Vor jedem Callback muss das volle unveränderte
Einzelmaximum verfügbar sein; danach zählt die tatsächliche Dateigröße. Dieser
konservative Vorbehalt kann vor1024 abbrechen. Der kleine zusätzliche
Attemptindex ist ebenfalls auf1024Einträge begrenzt, mit Fehlerstrings≤256Zeichen.
Keine Verzeichnisscans oder zusätzlichen Spiel-/Sourceabfragen; nur fstat des
bekannten neuen Belegs. Die echte absolute parent_started+85-Frist wird vor
und nach Callback/Dateiarbeit geprüft. .2s-Framefrische und2s-Nachread-ACK bleiben
unverändert; Dateiarbeit zählt mit. Capturefehler bleiben primär, ergänzende
Custody-/Deadlinefehler bleiben sichtbar und sticky.

Der erste echte RED führt die transformierte tatsächliche native_roles-Closure
und unveränderte capture_ownership/private_json zweimal aus; der zweite Call
reproduziert FileExistsError. Sechs weitere REDs zeigen die fehlende begrenzte
Hülle. GREEN umfasst34 fokussierte Tests (0,664s). Ein zusätzlicher
Integrationstest verbindet den Initialframe plus zwei weitere Rollenreads mit
wirklicher NativeContext.input_frame-AST, einem reinen Byte-Fakereader,
RP._sample, strikter Policy und Replica-Bindung. MayRespawn/buttons werden
weiter doppelt gelesen. Ein frisches falsches Log bleibt fatal und sein neuer
Beleg erhalten; verspätete .2s-Probe bleibt fatal. Kein Prozess-/ABI-/Retailnachweis.

Weitere Gegenfälle prüfen gemeinsamen1024-Zähler, konservative Bytevorabgrenze,
absolute Vor-/Nachfrist, fehlenden Beleg, bereits vorhandenes Namespace,
Primärfehler bei zusätzlichem Custodyfehler, erhaltenes Receipt bei Guardfehler
und sticky Nachfolgesperre. Ganze vier Quelldateiinversen bleiben aktiv; die
allgemeine NAI-Quelle unterscheidet sich gegenüber D-v4 nicht.

Private Logs liegen unter `/srv/tse-original-respawn-colt-evidence-20261115`:
`v5-double-capture-red.log`, `v5-bounds-red.log`,
`v5-fresh-reads-first-green.log`, `v5-focused-first-full-green.log`.
Ein vorheriger falscher Writer-CWD suchte tools/tools und startete anschließend
einen noch nicht angelegten Testnamen; dies ist ein Aufruffehler im Tooltranskript,
kein Verhaltens-RED. Die authentischen RED/GREEN-Dateien wurden0600/O_EXCL angelegt.

Frischer D-v5: `/srv/tse-a1-original-respawn-fixedtarget030-v5-disabled-20261115`,
1662009Bytes; Manifest6ca287db33640b859b2854df19dfd1acd78b6b4f91ab2fc3879b1d8d2a33a9a7,
Runner72363872da3253d5dbf02457380e9df53b3b323fe781196d4e38167b34fe9199,
Nested8abe9d4bd7a9299d930568c62060532e419e06d8daed56dc742dcb6c307fab4f.
280/77/14Pinwerte vollständig mit NOATIME/NOFOLLOW geprüft; vier ganze Inversen,
allgemeine NAI-Capturequelle/Reader/alter Method/Core und Gatefingerprints
unverändert. Gegenüber D-v4 acht Dateideltas inklusive vier eigener Quellen,
Runner, unusedCollectorPRIVATE und zwei Manifeste;135Dateien bytegleich.
Private ausführbare Prüfquelle `verify-v5-disabled.py`; finaleQuittung
`disabled-v5-final-receipt.json` SHA
bbed8048c5fb0fbd4a07efa47dcdf3c1923e1332aa8d11a182c2d6a24f3648f1
im oben genannten Evidenceverzeichnis. Sourcecommit1f6188b; dieser Abschluss
ändert ausschließlich Dokumentation. F2 Result0bf78d6047f41c4dd4407d5deb37fec86934674ac776ebdacbf6fe0cea0b6b6c
bleibt FAIL; D-v4 und alle älteren Pakete bleiben unverändert.
Keine Gates aktiviert, kein Native/Build/Livezugriff. Root allein reviewed,
integriert, friert ein und entscheidet über einen neuen Kontrollfall. Kein
FirstState-/Botopfer-/Aim-/Gain-/A1-PASS aus dieser Sourcekorrektur.
