# Passiver CPU-Domänenhelfer, Source-only

`tools/owned_cpu_domains.py` liest ausschließlich übergebene PID+Startticks und
exakte absolute Cgrouppfade. Ownership ist eine Voraussetzung des Rootcallers,
kein vom Helper entdeckter oder erfundener Beleg. Kein Loop/Thread, Schreiben,
Prozessstart, Signal, Frida, Discovery oder Fallback; keine Guardgrenzenänderung.

`sample(epoch, processes, cgroups, clock_hz, ...)` liest je PID zweimal stat,
mit `rsplit(') ',1)`, und bindet beide PID/Startticks. Es verwendet nur utime/stime,
niemals cutime/cstime. Cgroup-dev/inode vor/nach einem `cpu.stat` müssen passen;
diese Metadaten sowie der gelesene Text bleiben auch bei Fehlern verfügbar.
Fehlende/reused/rekreierte/kaputte Quellen und rückläufige Counters sind UNKNOWN,
niemals künstliche Nullwerte. Gültige unabhängige Quellen bleiben auswertbar.
Ungültige Callerparameter scheitern vor Quellenreads.

`delta(before,after)` bindet Epoch/Hz/Identitäten und nicht überlappende endliche
monotone Samplegrenzen. Da Reads kein atomarer Snapshot sind, liefert es pro
Domäne CPU-Sekunden und Kernäquivalent-RANGE mit konservativer Zeitspanne:
`after.begin-before.end` bis `after.end-before.begin`. Überlappende oder ungültige
Zeiten und Counterrückgänge sind UNKNOWN. Prozess und Cgroup können dieselbe
Arbeit enthalten: kein Summenfeld, keine HostCPU%-Ableitung oder Hostpass.
Ein gültiger tatsächlich unveränderter Counter kann korrekt null Delta haben;
UNKNOWN wird dadurch nicht zu null umgedeutet.

Sechs gezielte FakeFS-Tests PASS/0.005s. Zunächst sechs explizite Assertions auf die
noch nicht vorhandene neue API FAIL, keine Importfehler. Der erste Implementations-
lauf hatte einen falschen Testvariablennamen und einen exakten Floatvergleich;
separater Log erhalten, Fixtures korrigiert, keine Produktionsgrenze gelockert.
Fälle: erlaubte Reads/domänenseparate echte Counter ohne Kinderzeiten, PIDreuse/
fehlendesEnde, Cgroupwechsel innerhalb/zwischen Samples, Missing-/EIO-
artige Lesefehler, malformed/oversized/negative Counters, nonfinite/reverse/
überlappende Zeiten, Epoch/Hz und verbotene Callerpfade. Alle Tests verwenden
nur FakeFS; keine tatsächlichen /proc-/Cgroup-/Runtimebelege daraus ableiten.

Reproduktion: `nice -n 15 python3 -m unittest tools.test_owned_cpu_domains`.
Private Logs/Pins: `.codex/evidence/owned-cpu-domains/` im Autorenworktree.
Der synchrone Helper ist kein Watchdog und behauptet keine harte Readlatenz.
Root muss den prospektiven Wrapper, eigene Prozessbindungen, Samplingkosten,
private Archivierung und identische Control-/Traceintegration separat prüfen.

Rootreview-Korrektur: Geräte-/Inodewerte vor Verwendung exakt int (keinbool), dev0≤v<2^64 undino0<v<2^64. Neuer FakeFS-Gegenfall zuvor9Fehler/1TestRED, danach gesamte7TestsPASS0,005s. Original6Tests/Autorevidenz bleiben erhalten. Kein nachgewiesenerKernel-/Nativefehler, keineNativeausführung.
