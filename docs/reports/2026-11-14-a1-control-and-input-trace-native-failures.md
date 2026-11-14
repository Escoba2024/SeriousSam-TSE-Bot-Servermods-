# A1: echte Kontrollprobe und unvollständige passive Inputkette

Beide begrenzten NoFire-Fenster sind geschlossen und bleiben **FAIL**. Keine Feueraktion, kein Schadensnachweis, keine A1-Abnahme. Build018 bleibt auf allen sechs Instanzen live.

## Uninstrumentierte Kontrolle

`a1-input-trace-20261114-102107`, Modus `uninstrumented-control`, ohne Frida-Worker/Attach. Nach sechs unveränderten Kalibrierinputs bricht CP nach5,332976s ab: `opposite pitch gain does not reproduce`. Der normale+12px-Pitchimpuls ergibt−6°/−0,5°jePixel, der−12px-Impuls+3°/−0,25°jePixel. Die tatsächlichen Server-/Client-ACKs zeigen dieselben jeweiligen physischen Deltas. Der Fehler tritt somit auch ohne Collector auf; eine genaue Ursache ist damit nicht bewiesen.

Maximal beobachtete Host-CPU64,406780%, verfügbarerRAM mindestens3051192320Bytes, Disk10962825216Bytes, sieben Ressourcenproben. Die26,977s-Startlücke bleibt ausgewiesen; dies ist kein formaler Ressourcen-/Dauernachweis. Result-SHA256 `67c024d2f66b652cc8f657eedeb38e373f5a76f0d6001154329b25c190fc1445`.

## Instrumentierte Vergleichsdiagnose

`a1-input-trace-20261114-102311`, Modus `instrumented-trace`. Sechs Listener wurden tatsächlich installiert.21 echte GetInput-Records wurden beobachtet, mit Cursor-/Recenter-/Controlsbelegen und echter Timer-TID1376528; null Action-Records, null vollständige Input-/Actionsequenzen, null Faults/Drops. Die enge Warmupbindung wurde nicht erreicht. Der Controller bricht deshalb **vor jeder Gameplay-Eingabe** ab; der Arm-IPC-Aufruf endete nach2,254470s innerhalb der unveränderten3s-Frist.

Stop/Quieszenz/Detach und vollständiger Originalbytevergleich meldeten Erfolg, null Game-State-Writes. WorkerPID1376710 wurde erst nach normalem Rollenschluss/Quieszenz beendet und gereapt. Der−15-Workerexit ist die dokumentierte Terminierung des eigenen Pythonworkers, kein erzwungener Spielclientclose. Result-SHA256 `97d586152cea08b3cb03b2285ea44101b6817360b75b5191d4c53e256ca80c45`.

Maximal beobachtete Host-CPU48,292919%, verfügbarerRAM mindestens3052953600Bytes, Disk10937020416Bytes, drei Ressourcenproben mit26,617s-Startlücke. Wegen fehlender gemeinsamer vollständiger Eingabesequenz lässt sich daraus kein gültiger Collector-Overheadfaktor oder Reproduktion des Pitchfehlers unter Instrumentierung berechnen. Original-GetInput-Beobachtung und Cleanup sind belegt; die Action-ABI/-Callbackkette bleibt unqualifiziert.

## Wiederherstellung und nächster Schritt

Je Fenster drei eigene Spielrollen und zwei Displays regulär geschlossen; Schlusslogs akzeptiert. Root prüfte unabhängig jeweils664Dateihashes samt Modus/UID/GID, neun ursprüngliche Abwesenheiten und drei Schlussloghashes. Alle gebundenen Rollen-/Display-PIDs und der Collectorworker sind beendet. Originalpreflight10:25:54UTC bestätigt freie vier Labrollen/Displays, beide Locks erwerbbar, CPU37,82%, verfügbarerRAM3651624960Bytes, Disk10916106240Bytes. Keine neue Runtime gestartet.

Die konkrete nächste Analyse prüft den tatsächlichen Original-Timer-/Actionpfad und die vorhandene Fokusvorbereitung: Fokus als Ursache ist bislang eine Hypothese. Keine längere Warmupfrist, keine Gain-/ACK-/EPS-Lockerung und kein blindes Wiederholen. Neue Eingabe- oder Hookänderungen benötigen belegte Ursache, fokussierte Regression und eine getrennte neue Frozenkopie. Beide jetzigen FAILs bleiben erhalten. Rohdaten/Originalguards bleiben privat und benötigen den nächsten Sicherungsnachtrag.
