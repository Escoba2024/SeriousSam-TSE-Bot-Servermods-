# Aktueller Frida-Python-Werkzeugnachweis

Für die offene A1-Eingabediagnose wurde der bereits vorhandene Frida-Python-Zugang auf demselben Host frisch geprüft. Keine Installation, kein zusätzlicher Dienst, kein RDC-/MCP-Aufruf und kein Zugriff auf TSE-Prozesse. Die vorhandenen Quoten- und Berechtigungsgrenzen bleiben unverändert.

Frida17.26.2 liegt in `/srv/tse-frida-probe-20261111/lib/python3.12/site-packages`. Ein eigener ELF64-Testprozess ruft eine einfache reine Funktion100Hz auf. Der eigene Python-Unterprozess führt Attach/CreateScript/Load, Interceptor-Callbacks, RPC-Arm/Drain/Stop, Unload und Detach aus. Der äußere eigene Supervisor begrenzt die Workerzeit und besitzt ausschließlich seinen eigenen Testprozess.

Ergebnis:99 echte Enter-/Leavepaare, keine Rückgabewertabweichung, Detach/Unload bestanden. Instrumentierter und uninstrumentierter Prozess endeten beide regulär mit Ergebnis45150. Kontrolle3,037s, instrumentiert3,077s; gemessene Kindprozess-CPU0,0078s gegenüber0,2505s einschließlich des nur instrumentiert gestarteten Pythonworkers. Das ist keine isolierte Callbackkostenmessung.

Der erste Versuch an einem8Byte-Prolog scheiterte bei Interceptor.attach. Dieser FAIL ist erhalten. Eine getrennt kompilierte Variante mit O0-Prolog bestand den Methodentest; daraus folgt keine allgemeine Aussage über die genaue Ursache des ersten Fehlers.

Reproduzierbare Quellen unter `poc/experiments/milestone-a-20261114/frida-method-smoke/`; rohe lokale Quellen/Binaries, Disassemblierung und gehashte Quittungen unter `/srv/tse-frida-method-smoke-20261114`. Bereinigte Quittungen unter `docs/reports/milestone-a-20261114/frida-method-*.json`.

**Grenzen:** nur lokaler Python-/ELF64-Methodentest. Keine Frida-MCP-Qualifikation, keine Wine-/Retail107-ABI-Abnahme, kein qualifizierter Originalinputcollector, kein A1-Schadensnachweis. Vor einem eigenen Retaildiagnosefenster bleiben Collector-/Supervisorreview, tatsächliche Originalbindung, uninstrumentierte Vergleichsprobe, Overheadmessung, normale Closes und verifizierter Restore erforderlich.
