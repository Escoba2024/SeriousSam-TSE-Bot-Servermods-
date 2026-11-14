# Eigene Win32-IA32-Instruktionsmethodenprobe

Nur Root baut und startet; derzeit statische, deaktivierte Vorbereitung.
Der eigene native Prüfling ist ein Kernel32-only-PE ohne Retaildateien und
ohne TSE-Aufrufe. MSVC-x86-Wrapper und vorhandener Buildhelper wurden gelesen,
nicht ausgeführt. GCC-/ELF-/x64-Ergebnisse ersetzen keine IA32-Wine-Methode.

## Ablauf je ausdrücklich gewähltem Einzelmodus

Root verwendet drei getrennte eigene Prozesse: `baseline`,
`historical-object`, `function-probe`. Kein automatischer Mehrfachlauf.
Der Parent importiert Frida nicht. Er hält einen exklusiven Methodenlock,
bindet Code-/EXE-/Prefix-/Prozess-/Start-/Namespaceidentitäten und reicht
an einen frischen Exec-Worker allein dessen IPC-Socket weiter.

Der Prüfling meldet READY und wartet auf `R` aus seinem eigenen stdin-Pipe.
Nach optionalem Attach an genau zwei eigene exportierte Midpoints gibt der
Parent `R` frei. Native Aufrufer prüfen Saved-EDI=12345678 und den tatsächlichen
Argumentwert 11223344 XOR 01020304=10203040. Der Saved-Midpoint wird per JMP
mit ESP=EBP−13C erreicht; oben liegt gesichertes EDI. Der Argumentmidpoint wird
ebenfalls per JMP erreicht, oben liegt Argument1. Acht NOPs ermöglichen eine
Instruktionsprobe ohne Relokation einer eigentlichen CALL-Anweisung.

Alle geprüften nativen Frames kehren zurück. Danach meldet der Prüfling
WAIT_CLEANUP samt tatsächlichen Ergebnissen und führt die Sites nie wieder aus.
Der Host prüft diese Nachricht sowie Callback-Idle, hängt die Hooks ab,
vergleicht vollständige eigene Codebereiche mit dem gepinnten PE und lässt
erst danach Scriptunload/Sessiondetach zu. Dann `Q`, normales ExitProcess(0),
belegtes Prozessende und zuletzt Ende des eigenen Exec-Workers.

Fridaoperationen bleiben vollständig im Worker. Parent-IPC benötigt feste
Arm-/Snapshot-/Closefristen und sticky Fehler; jede Phase schreibt private
Quittungen. Ein Blocker darf normales `Q`/Prozesscleanup nicht verhindern.
Ein nur eigener Worker darf erst nach belegtem Ende des Prüflings beendet
werden. Keine Signale an fremde Prozesse, kein globales wineserver-kill.

## Bewertung

Baseline und Funktionsprobe benötigen echte unveränderte native Werte und
vollständige Cleanup-/Byte-/Prozessbelege. Die historische Objektform zählt nur
bei tatsächlich beobachteter Sentinel-/Argumentverletzung als reproduzierte
Negativkontrolle; ein Crash, fehlender Datensatz oder Cleanupfehler zählt nie.
Bleiben die Werte unverändert, lautet die Kontrolle ausdrücklich
CONTROL_NOT_REPRODUCED. Kein Kontrollbefund ist ein Retail-/A1-/A3-PASS.

## Voraussetzungen und Grenzen

Root erstellt eine neue isolierte Methodenumgebung und initialisiert ihren
eigenen Wineprefix vor dem Fenster. Der existierende Buildprefix wird nur mit
seinem vorhandenen exklusiven Lock benutzt; er ist kein Runtimeprefix.
Compiler-/SDK-/Wine-/Fridaquellen und ein fertiger PE-Build müssen neu gepinnt
werden. Vor Start sind eigener PID/Start, exakter EXE-Mappinginode, CWD,
Prefix und Namespace zu prüfen; alte Prozessnamen genügen nicht.

Offline umgesetzt: begrenzter Methodencontroller, frischer Exec-Worker,
14 Policy-/Controller-/Paketfälle, zehn geerbte Proxyfälle und sieben JS-Fälle
bestanden. Root hat PE-Build und Disassembly geprüft. Offen bleiben finaler
unabhängiger Review, konsistent gepinnte Root-Freeze, alle drei getrennten
nativen Methodenbelege und jede anschließende Retailqualifikation.

## Root-Buildvorlage, ausdrücklich nicht ausgeführt

Bestehende Wrapper: `/srv/tse-msvc-20261021/bin/x86/cl` und `link`;
MSVC14.44.35207, SDK10.0.19041.0 laut gelesenem `msvcenv.sh`.
Root muss den vorhandenen Buildlock und freien Buildprefix zuerst prüfen.
In einer neuen eigenen Quellkopie sind folgende Argumentlisten vorgesehen:

```text
cl /nologo /c /Od /GS- /GR- /EHs-c- /Zl /Oy- /W4 win32_instruction_probe.cpp /Fowin32_instruction_probe.obj
link /NOLOGO /MACHINE:X86 /SUBSYSTEM:CONSOLE /NODEFAULTLIB /ENTRY:ProbeEntry /BASE:0x400000 /FIXED /DYNAMICBASE:NO /OPT:NOREF /DEF:win32_instruction_probe.def /OUT:win32_instruction_probe.exe /MAP:win32_instruction_probe.map win32_instruction_probe.obj kernel32.lib
```

Das ist keine geprüfte Buildquittung. Root muss MSVC-/PE-/Export-/Disassembly-
Ergebnisse prüfen und eventuelle Compiler-/Linkerfehler als solche festhalten.
Die zwei unverdeckten NOP-Midpoints, ihre kompletten Funktionsbereiche und
alle Erwartungswerte werden aus dem tatsächlich erzeugten PE gepinnt.

Root hat zwei tatsächliche Linkerfehler separat erhalten: der unnötige cdecl-
Export `ProbeEntry=_ProbeEntry` wurde doppelt dekoriert; nach dessen Entfernung
suchte `/ENTRY:_ProbeEntry` weiterhin `__ProbeEntry`. Die eng korrigierte Vorlage
exportiert nur zwei stdcall-Midpoints und verwendet `/ENTRY:ProbeEntry`.
Root meldete anschließend den dritten Build tatsächlich bestanden:
`/srv/tse-win32-instruction-method-build-entryfix-20261114`, EXE3584B,
SHA256`c90e6d57ee787bc4ccc6a0cb6eae703cfe6e3fc6112d6ba0c628d4a488de6c0f`.
Die Offlinepaketierung prüft diesen tatsächlichen PE-Hash, beide Export-RVAs
1000/1070 und vollständigen17/14-Byte-Bodies vor jeder Übernahme.
Kein eigener Compiler-/Linkerlauf durch diesen Agenten.

## Präzise Callbackphase

Frida17.26.2 `guminterceptor.c` ruft den Listener zuerst auf und ersetzt erst
danach den vermeintlichen Returnslot. Beide instrumentierten Modi müssen daher
im Callback die ursprünglichen Stackwerte12345678/11223344 zeigen. Aus einem
unveränderten Entrywert folgt keine native Erhaltung nach Callbackrückkehr.
Die Policy verlangt echte native Endwerte zusätzlich zu genau saved/arguments,
derselben positiven Thread-ID und dem sourcebelegten Saved-Callback-EDI.
Der Argument-Callback-EDI wird lediglich als IA32-Zahl validiert, da die Quelle
dort keinen bestimmten EDI-Wert festlegt.

Frida-mainModule wird unter Wine nicht mit dem PE gleichgesetzt. Der Host
prüft PID/Start/CWD/Prefix/Namespace und Mappingpfad/-inode/-device der eigenen
EXE. JS liest am hostgebundenen0x400000 passiv MZ/PE/IA32/PE32 sowie die beiden
vollständigen Bodyguards. Keine Laufzeitfunktion oder Spielzustandswrite.

## 12:42 UTC: belegter eigener Stdinfehler und enger Fix

Erste Baseline geschlossen FAIL vor Methodenaufruf: READY, Mappingabsent, Exit10, kein Frida. Rootdiagnose mit ausschließlich zusätzlicher GetLastError-Ausgabe belegt READY→STDIN_PEEK_FAILED/00000032(50 ERROR_NOT_SUPPORTED laut installiertem Winerror.h),Exit10. Quelle und eigener Diagnosebuild bleiben separat erhalten; keine Retailaussage.

Enger Fix: ReadFile genau eines R-/Q-Bytes in einem eigenen Leserthread. Hauptthread wartet mit WaitForSingleObject höchstens unveränderte15Sekunden. Bei abgeschlossenem ReaderThreadhandle schließen und tatsächliches Readresult/Byte prüfen. Bei Timeout/Waitfehler normalen eigenen ExitProcess(12) auslösen, damit weder Thread noch Stackreferenz weiterleben. Kein TerminateThread/Cancel oder fremder Prozesszugriff; neue Kernel32-Imports sind eigenes CreateThread/WaitForSingleObject/CloseHandle. Keine Änderung an zwei Midpoints/EDI/Argumenten/Frida/Raten/Anforderungen. Vor Rootneubuild statische enge Regression; Nativebaseline ist der eigentliche GREEN-Nachweis. Neue Quelle/DLLfreiePE/Packages getrennt pinnen, alte FAILs/Builds unverändert. Nach drei geschlossenen Methodenfällen eigenen quieszenten reproduzierbaren Wineprefix abbauen und Platzreserve zurückgewinnen.
