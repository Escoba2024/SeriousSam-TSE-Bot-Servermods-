# Eigene IA32-Instruktionsmethode: deaktivierte Vorbereitung

Der minimale Fünf-Midpoint-Fix ist separat committed als
`1bbd3a658cd2b00cedb9edbfb97b94a9573eed78`: vier A1- und ein A3-Midpoint
registrieren echte Funktionsprobes. Die zwei tatsächlichen A1-Funktionseintritte
und Original-ReceiveDamage behalten ihre gepaarten Listener. Registrierungs-
regressionen zeigten jeweils erwartetes RED (Objekt statt Funktion), danach
31 A1-Node- und sieben A3-VM-Fälle GREEN. Sites, Callbackbody, Grenzen,
Zeiträume, Inputs und Abnahmekriterien wurden nicht verändert.

## Vorbereiteter Methodenstand

Privates Autorenpaket:
`/srv/tse-win32-instruction-method-final-20261114`

Manifest-SHA256:
`e3769b2fdc6ef7970909bc2aaf6348d6b9b6c98eeaeb3d327a7bb97bcd6d877e`.

19 Runtimepins, Code-/Manifestgate false, keine Prefixkopie und kein nativer
Methodenlauf durch diesen Agenten. Der Quellbuilder kopiert ausschließlich
eigene Quellen und die tatsächlich von Root gebaute eigene EXE; keine Retail-
Datei. Frida17.26.2, Python, Winewrapper und Root-Buildmanifest werden gepinnt.

Root baute erfolgreich die MSVC-IA32-/Kernel32-only-EXE, SHA256
`c90e6d57ee787bc4ccc6a0cb6eae703cfe6e3fc6112d6ba0c628d4a488de6c0f`.
Zwei vorangegangene tatsächliche Linker-FAILs bleiben erhalten: unnötiger
cdecl-Entryexport und anschließend doppelt dekorierter `/ENTRY:_ProbeEntry`.
Die korrigierte DEF exportiert nur zwei Midpoints; `/ENTRY:ProbeEntry` linkte.
RVA1000/17B und1070/14B samt acht NOPs werden aus dem echten PE gegengeprüft.
Build-Erfolg ist kein nativer Methodenbeleg.

## Sicherheit und Aussagegrenze

Je Aufruf genau ein Modus: baseline, historical-object oder function-probe.
Kein automatischer Dreierlauf und kein Retry. Der fridafreie Parent startet
ausschließlich die gepinnte eigene EXE im quieszenten eigenen win64-Prefix.
Fridaoperationen laufen im frischen Exec-Worker mit IPCfristen3s/100ms/2s.
Nur dessen Socket wird vererbt. PID/Start, Lockinode und tatsächliche eigene
EXE-Mapping-/Prefix-/CWD-/Namespacebindungen bleiben erforderlich.

Der native Prüfling liefert tatsächliche Saved-EDI- und Argumentergebnisse und
meldet nach Rückkehr aller Testframes WAIT_CLEANUP. Erst dann Callback-Idle,
Hookdetach, vollständiger eigener Bodybytevergleich, Unload und Sessiondetach.
Fehler bleiben sticky und verhindern eine positive Bewertung. Sicher belegte
Bereinigung wird bei Message-/Callbackfehlern trotzdem versucht. Der Parent
sendet unabhängig vom Worker das normale Q und wartet auf echtes Prozessende.
Nur danach darf er seinen nach PID/Start geprüften Popen-Worker beenden.
Kein Signal an die native EXE oder fremde Prozesse, kein wineserver-kill.

Frida ersetzt den Returnslot erst nach onEnter. Deshalb müssen BEIDE
instrumentierten Modi im Entry die ursprünglichen Stackwerte belegen.
Die Policy bindet zusätzlich beide Site-Records, dieselbe positive Thread-ID
und sourcebelegten Saved-Callback-EDI. Der erwartete historische Kontrollfehler
verlangt eine echte native Endwertverletzung und vollständiges Cleanup; Crash,
fehlende oder falsche Kontexte zählen nicht. Unveränderte historische Endwerte
führen ausdrücklich zu CONTROL_NOT_REPRODUCED.

Der Controller verlangt vor Runtime mindestens8GiB frei. Root hat einen eigenen
win64-Prefix initialisiert und dessen Quieszenz bestätigt; er wird hier nicht
angefasst oder kopiert. Nach allen drei geschlossenen Modi soll Root die
reproduzierbare eigene Prefixkopie nach gesicherten Quittungen und bestätigter
Quieszenz entfernen. Keine neue Archivierung in dieser knappen Platzphase.

## Offlineprüfung

14 Methoden-Policy-/Controller-/Paketfälle, zehn bereits vorhandene echte
Proxy-/Childfälle und sieben JS-VM-Fälle bestanden:31 einzigartige gezielte
Methodenchecks. Ein eigener frischer Python-Testchild simulierte Blockierung
und endete; keine Frida-, Wine-, Compiler- oder TSE-Ausführung durch den Agenten.
Methodenpolicy, Controller, Paketbuilder und JS hatten vorher tatsächliches
fehlende-Implementierung-RED. Zusätzliche kontextlose Records wurden zunächst
fälschlich akzeptiert; eigenständiges RED führte zur strikten Contextprüfung.
Eine zwischenzeitlich falsche Annahme zum Zeitpunkt der Returnslotersetzung
wurde anhand des vollständigen offiziellen Core-Quellcodes mit RED/GREEN
korrigiert. Eine Baseline-Fixture hatte fälschlich zwei Callbackcounts statt0;
nur die Fixture wurde berichtigt. Keine verlorenen FAILs als PASS bezeichnet.

```sh
cd tools
python3 -m unittest test_win32_instruction_probe_policy test_win32_instruction_probe_controller test_prepare_win32_instruction_method test_original_damage_worker -v
node test_win32_instruction_probe.js
```

Diese gezielte Suite prüft den begrenzten Vorbereitungsscope. Eine breite
Discovery ist vom Hauptagenten zum Schutz exklusiver nativer Fenster untersagt.
Kein Offlinefall qualifiziert tatsächliche IA32-/Wine-/Frida-Methoden oder Retail.

Offline-Reproduktion in einen frischen eigenen Pfad:

```sh
python3 tools/prepare_win32_instruction_method.py --destination /ABSOLUTER/NEUER/PFAD
```

Root muss nach unabhängigem Review seine eigene Kopie einfrieren, sämtliche
internen Runtimepins konsistent umadressieren, Controller-Codegate und Manifest
gemeinsam umstellen und frischen Platz-/Prefix-/Lock-/Prozesspreflight durchführen.
Sein bereits eigener initialisierter Prefix darf beim Dateifreeze erhalten
bleiben; der Autorenbuilder benötigt dagegen einen frischen Pfad.

Erst anschließend je ein Rootaufruf:
`python3 win32_instruction_probe_controller.py --mode MODE`.
Methodenbelege, neue deaktivierte A1-/A3-Forks und jede spätere Retailabnahme
bleiben ausstehend. Alle bisherigen A1-/A4-FAILs bleiben unverändert.

## Fortsetzung: eigener stdin-Transportfehler und enger Fix

Der erste Root-Baselinelauf blieb FAIL: READY, anschließend fehlende/mehrdeutige
EXE-Bindung und Programmende10; kein Frida-Worker, keine Methodenqualifikation.
Root bestätigte die Ursache in einer getrennten eigenen Diagnose ohne Frida/TSE:
`PeekNamedPipe` scheiterte am vererbten stdin-Handle mit Win32-Code50
(`ERROR_NOT_SUPPORTED`). Alte Builds, Pakete und fehlgeschlagene Quittungen bleiben
unverändert. Der belegte Fixplan steht im angehängten Abschnitt des Methodenplans.

Commit `f29fb2bfddee6912bbe3cda25d6103d1357c0c21` ersetzt ausschließlich den
stdin-Befehlsleser: Ein eigener Thread liest mit `ReadFile` genau ein Byte. Der
Hauptthread wartet unverändert höchstens15000ms. Erst nach bestätigtem Threadende
schließt er dessen Handle und prüft tatsächlichen IO-Erfolg, Bytezahl und R/Q.
Timeout oder WAIT_FAILED beendet nur das eigene Programm mit `ExitProcess(12)`;
kein Rücksprung mit lebendem Thread und Stackreferenz, keine Threadterminierung
oder Fremdsignale. Zwei Midpoints, Eingaben und Ergebniswerte bleiben unverändert.

Vier Tests führen den echten begrenzten `command`-Quellrumpf mit gestubbten
Win32-API-Ergebnissen aus. Vor Implementierung viermal RED, danach GREEN:
Erfolg, CreateThread-Fehler, Timeout/WAIT_FAILED und EOF/IO-/Byte-/Handlefehler.
Das ist ein Quell-Controlflow-Modell, kein kompilierter oder nativer Threadbeleg.
Der Pakettest blieb vor Retarget wegen abweichender tatsächlicher C++-Quellhashes
FAIL; nach strengem Retarget bestanden18 gezielte Pythonfälle und sieben JS-VM-
Fälle. Kein Compiler/Wine/Frida durch den Autor.

Root baute die neue eigene Quelle erfolgreich separat:
`/srv/tse-win32-instruction-method-build-stdin-fixed-20261114/manifest.json`.
C++ SHA256 `551f1672d96996d23d3a05f7149f1b1216cdb9fb10cf64368170e878d96b0f09`;
EXE3584B SHA256 `4305c136f460f6fec4ff8b6ccb9419394514e2cee808b5ab5865b12b59f5acf4`.
Die beiden tatsächlichen Exportkörper bleiben RVA1000/17B und1070/14B.
Neues Autorenpaket (kein Prefix kopiert):
`/srv/tse-win32-instruction-method-stdin-fixed-final-20261114`, Manifest
`708d771447ad94927501225e52f65f53bbe11fa848e7a01bd56e2d19b89ea17b`,20Pins.
Controller/JS/Policy/Worker sind bytegleich zum vorigen Autorenpaket; alle Gates
bleiben deaktiviert. Neuer Root-Freeze, exklusiver Prefixmove, frischer Platz-
und Prozesspreflight sowie zuerst eine echte neue Baseline bleiben erforderlich.
Bis zu deren Abschluss keine instrumentierte Methodenqualifikation; Retail offen.

```sh
cd tools
python3 -m unittest test_win32_command_reader test_prepare_win32_instruction_method test_win32_instruction_probe_policy test_win32_instruction_probe_controller -v
node test_win32_instruction_probe.js
```
