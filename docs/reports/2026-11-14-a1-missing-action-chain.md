# A1: fehlende Action-Kette und minimale passive Ergänzung

Die konkrete geschlossene Original-Timerbedingung ist mit den bisherigen Datensätzen **nicht bewiesen**. InputEnable-/Fokusverlust allein und eine geraten falsche statische CreateAction-Adresse erklären den Befund nicht. Zwei getrennte Fehlschläge bleiben erhalten:

| Fenster | Ergebnis und Grenze |
|---|---|
| Uninstrumentierte Gegenkontrolle `a1-input-trace-20261114-102107` | FAIL nach6 Eingaben, CP5,332976s: positiver Pitchimpuls+12px ergab−6°/Gain−0,5; entgegengesetzter−12px ergab+3°/Gain−0,25. Beide physischen ACK-Ebenen stimmen überein. Das Verdopplungsproblem existiert somit auch ohne Collector. Kein Fire. |
| Instrumentiert `a1-input-trace-20261114-102311` | FAIL vor CP/Eingaben:21 vollständige GetInput-Records, jeweils Caller60851241; Median50ms, erster bis letzter997ms.0 Action-Records/abgeschlossene Sequenzen/Warmupskips/Faults/Drops; sämtliche rohen Cursorbewegungen0. Arm-IPC2,254s einschließlich Attach/Load und unverändertem maximalem Warmup. Originalbytes restauriert, Worker gereapt, normale Rollenbereinigung. Keine erfolgreiche Hookkette oder A1-Abnahme. |

Private Basis beider Fenster: `/srv/tse-milestone-a-evidence-20261111`. Ergebnisdatei der Kontrolle SHA256 `67c024d2f66b652cc8f657eedeb38e373f5a76f0d6001154329b25c190fc1445`; instrumentiertes Ergebnis `97d586152cea08b3cb03b2285ea44101b6817360b75b5191d4c53e256ca80c45`; vollständiger privater Trace `c0c744a8ed252cce13a5ae21d626fb951b58cb1ca7f7405a0a869f4d9aba53c2`. Keine Rohidentitäten oder Retailbytes werden hier veröffentlicht. Root hat normale Closes und664 Datei-/9 Abwesenheitsprüfungen unabhängig bestätigt.

## Aufrufpfad: belegt und weiterhin unbekannt

SDK107 `/srv/tse-sdk-20261021/Sources/Game/Game.cpp`: GameHandleTimer747, GetInput768, nachgeschaltete Bedingung771, CreateAction793. GetInput(FALSE) liegt **vor** `gm_bGameOn && !IsPaused() && !GetLocalPause()`. Vor GetInput prüft der Timer bereits InputEnabled und MenuOn. Der beobachtete Rückkehrcaller60851241 belegt diesen konkreten Timerzweig. Die weiterhin gebundene LocalPlayerSource war bei allen bisherigen Callbackprüfungen vorhanden.

Der tatsächliche Runner setzt und prüft beide eigenen Fensterfokusse bereits vor Arm (`run_dual.py`407/411). Es gibt hier kein erst im ersten `act` ausgeführtes Endpoint.prepare. Ein Einfluss von Fokus auf eine nachgeschaltete LocalPause wäre weiterhin denkbar, ist aber nicht aufgezeichnet oder bewiesen. Kein neuer Fokus-/Recenter-/Gameplayimpuls wird deshalb eingeführt.

Original-Timerdisassemblierung privat unter `/srv/tse-a1-colt-pitch-analysis-20261112/evidence/Game-input-call-6085123b.asm.txt` und `Game-TimerAction.asm.txt`: nach Rückkehr60851241 prüft der Code Game+F54, ruft IsPaused bei60851256 und GetLocalPause bei6085126C, prüft die Source und ruft CreateAction virtuell bei608512F8, Rückkehr608512FB. Die einzige statische Referenz auf60850470 steht in CControls-Vtable6086156C, Slot+20 bei6086158C. Der tatsächliche Runtime-Vptr und die nachgeschalteten Game-/Pause-/Globalwerte wurden bisher **nicht** erfasst. Damit ist auch deren tatsächliche Branchentscheidung offen.

## Originalbindung und Art der Gegenprüfung

Alle VAs sind bevorzugte Dateiadressen. Live gilt ausschließlich geladene gebundene Modulbasis+RVA mit Relokationsprüfung. Original Engine-SHA256 `b79bf8bb3927fe4f8f252e141d721ae5c738df02218f0ecc12da5c1afbcb534f`, bevorzugte Basis600C0000; GameMP `1c41da35b3fc47378c407b770e1bd1dcc2b7e6bf676c140586bc6035461d4208`, Basis60840000.

| Funktion/Struktur | VA / RVA | Statische Gegenprüfung |
|---|---|---|
| InputEnabled | 600CB020 / B020 | Originalexport; Getter liest Input+4 |
| IsPaused | 6019AB60 / DAB60 | Originalexport, Game-IAT2129C, vollständige29Byte mit Relokation; Null-Network/globaler Guard≠0 ergibt1, sonst Session+20→Wort+A8 |
| GetLocalPause | 6019AC30 / DAC30 | Originalexport, Game-IAT21298, vollständige26Byte mit Relokation; derselbe Fallback, sonst Network+854 |
| GameHandleTimer-Prolog | 608511A0 /111A0 | Original59Byte; ECX-Game wird im vom Aufgerufenen zu erhaltenden EDI gehalten |
| CControls-Vtable | 6086156C /2156C | Original36Byte/9Relokationen; Slot+20 zeigt60850470 |
| Original-Timercaller | 60851231 /11231 | Bereits vorhandene214Byte, GetInput-/Game-/Pause-/Source-/Actionpfad und Characteroffset bleiben gebunden |

Die neuen Getter-/Vtablebefunde stammen aus direkten PE-Export-/IAT-/Opcodeprüfungen der hashgeprüften Originaldateien und dem SDK-Aufrufpfad. Der Generator wiederholt Export-/IAT-/Vtable-Gegenprüfungen. `probe_retail_pause.py` bindet IsPaused/Session+A8 bereits separat; dieser vorhandene Reader bezeichnet seinen Wert ausdrücklich als rohes Pausewort ohne den globalen Fallback. Hier wird dieser Fallback zusätzlich sichtbar gemacht.

Aktuelle Toolprüfung: ALL_TOOLS enthält0 REA/Ghidra-/Reverse-Engineering-Werkzeuge; `ghidra`, `analyzeHeadless`, `java`, `rea` sind im PATH nicht vorhanden, unter `/opt` wurde kein entsprechendes Installationsverzeichnis beobachtet. Historische Shadowqualifikation wird nicht übertragen. Es wurde weder der falsche8080-Eintrag aufgerufen noch Ghidra gestartet. Insbesondere ist GetLocalPause+854 eine hier dokumentierte statische Original-Opcode-/Exportgegenprüfung, **keine Ghidra-Dekompilation und kein nativer ABI-Nachweis**.

## Minimaler deaktivierter Quellstand

`timer_guard_entry` und `timer_guard_return` ergänzen ausschließlich bereits vorhandene GetInput-Records. Sie lesen CallerGame/EDI, GameOn/MenuOn, InputEnabled, gebundene Source, Network/globalen Getterguard, Sessionpointer/Pausewort, LocalPausewort, Controls-Vptr und tatsächliches virtuelles Ziel. Abgeleitete Getterergebnisse berücksichtigen die Originalfallbacks. `derived_create_action_gate_open` beschreibt nur diese beobachteten Werte; `actual_branch_proven=false` verhindert die Gleichsetzung mit einer tatsächlich ausgeführten Branchentscheidung. Andere Threads könnten Werte zwischen Snapshot und Originalprüfung ändern.

Keine zusätzlichen Hooks, NativeFunction-/Getteraufrufe, Eingaben, Writes oder Einstellungen. Der Collector kann weiterhin erst nach einer tatsächlich vollständigen gebundenen Input-/Actionsequenz freigeben. Warmup1s, Queue256, Callcap4096, TTL90s, IPCfristen, CP/RD/ACK/Gain/EPS, alle normalen Eingaben und die Firegrenze bleiben unverändert. Neue Guardmetadaten werden vor Listenerinstallation verlangt. Die bisherigen fünf vollständigen Originalregionen werden um fünf rein statische Regionen ergänzt; sechs Callbacksites bleiben gleich. Die Auswirkungen zusätzlicher Lese-/Serialisierungsarbeit sind noch nativ zu messen.

Separates neues Authorpaket: `/srv/tse-a1-input-trace-timer-guard-library-20261114`; Manifest SHA256 `2e2a7981ee349eda407983746bc22787bb273b34b75aa0a057122f454b12f3ea`,15 Quellen-/externe Pins korrekt. Guardmetadaten SHA256 `2f4b494cbb4796727c821b7f6a4d3a5ab921ded5e9bf620dd5476f6765746936`. Code- und Manifestgate false. Alte Library bleibt `d509b72c…`, alte Root-Freeze `2e3bf79b…` unverändert; kein alter privater Controller oder Freeze wurde geändert. Kein eigener Prozess läuft.

Root muss eine gesonderte neue Kopie erstellen und PRIVATE, GUARDS_SHA, Librarymanifest, collector_source und sämtliche transitiven Pins konsistent retargeten. Die neue Quelle liegt in `/srv/tse-a1-timer-guard-record-20261114`, nicht im alten Proposalworktree. Dessen neue authored Librarypfade sind beim Freeze ebenfalls zu remappen/deduplizieren. Erst unabhängiger Review und frischer Preflight erlauben einen getrennten Rootstart; dieser Branch startet keinen Versuch oder Retry.

## Gezielte Offlineprüfung

Neue JS-Fälle gegen3c22eaf RED (fehlende Metadatensperre), anschließend GREEN. Ein erster Durchlauf mit neuem Code zeigte einen unvollständigen synthetischen Pointer im alten Nested-Test; die Fixture wurde auf ihren tatsächlichen Pointertyp berichtigt, keine Produktbedingung gelockert. Danach28 JS-Modelle GREEN: offene/jeweils geschlossene Game-/Pauseguards, Null-Networkfallback, abweichendes virtuelles Ziel, unveränderte Warmup-/Thread-/Drop-/Quieszenzfehler.11 Host-/Originaldateiprüfungen GREEN inklusive tatsächlich reproduzierter zehn Guardregionen, sechsSites und Export-/IAT-/Vtablebindung. Zusätzlich9 Worker-/Scope-,10 unveränderte CP-/Controller- und12 Analyzerfälle GREEN; insgesamt70 gezielte Offlinefälle. Keine breite Discovery, kein Compiler, Fridaimport, Attach oder TSE-Start. Sämtliche Tests erst nach Roots expliziter Ressourcenfreigabe nach dem A4-Fenster.

```sh
node tools/test_a1_input_trace_callbacks.js
TSE_A1_INPUT_PRIVATE=/srv/tse-a1-input-trace-timer-guard-library-20261114 python3 -m unittest discover -s tools -p test_a1_original_input_collector.py
python3 -m unittest discover -s tools -p test_a1_input_worker.py
TSE_A1_TRACE_PACKAGE=/srv/tse-a1-input-trace-preparation-20261114 python3 -m unittest discover -s tools -p test_a1_trace_preparation.py
python3 -m unittest discover -s tools -p test_analyze_original_input_trace.py
```

Ausstehend: unabhängiger Quellen-/Freeze-Review, tatsächliche beobachtete Timerguards, vollständige OriginalActionkette, passende Kosten-/Gegenkontrolle. Ohne diese Werte bleibt die konkrete Ursache des fehlenden Actionpfads offen. Ohne vollständigen Input-/Actiontrace bleibt auch der verdoppelte Pitch-/Yaw-Gain ungeklärt; beide historischen FAILs und A1 bleiben offen.
