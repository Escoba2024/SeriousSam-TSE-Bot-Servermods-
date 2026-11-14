# Begrenzte Original107-LocalSource-Beobachtung

Status: statische Offlineableitung, **keine native Retail-/ABIqualifikation**.
REA/Ghidra haben gemäß Toolpolicy Priorität. Die aktuell angebotenen Tools
enthalten jedoch keinen REA-/Ghidra-/Frida-MCP-Zugang; eine gezielte Metadaten-
suche ergab0 passende Einträge. Im lokalen PATH waren ghidra, ghidra_tse,
analyzeHeadless, rea und rea-agents nicht auflösbar. Das beweist keine globale
Nichtinstallation. Kein Backend gestartet, keine neue Verbindung/Identität,
kein RDC-Aufruf und insbesondere kein ghidra:8080-Zugriff. Historischer
Shadow-Ghidranachweis bleibt ein anderer Host-/Toolbeleg.

Als begrenzte Alternative wurde das legal vorhandene unveränderte
`vanilla/Bin/GameMP.dll` mit GNU objdump2.42 passiv disassembliert.
SHA256 `1c41da35b3fc47378c407b770e1bd1dcc2b7e6bf676c140586bc6035461d4208`,
PE32 bevorzugte Basis60840000. Kein Compiler/Spielprozess/Hook/Write.

Der TimerHandler-Localplayerdurchlauf enthält konkret:

| Original-VA / RVA | Relocationfreie Bytes | Datenfluss |
|---|---|---|
|6085127d /1127d|`8d9fa40f0000833b00`|EBX=&game.localSource0 bei Game+FA4; nicht-null prüfen|
|60851297 /11297|`8b138d73048b02`|EDX=*(EBX); EAX=*(EDX), erster DWORD des tatsächlichen Sourceobjekts|
|6085132f /1132f|`81c30c08000083f804`|nächster lokaler Sourcezeiger nach80C Bytes, vier Locals|

Der folgende Store bei608512a4 publiziert EAX an6086c280. Der geprüfte
vorhandene Game.cpp-TimerHandlerquellpfad nennt dieses Feld
`ctl_iCurrentPlayer = gm_lpLocalPlayers[iPlayer].lp_pplsPlayerSource->pls_Index`.
Dieser Quellname ist Gegenprüfung des **sichtbaren Originaldatenflusses**,
kein alleiniger1.10-Layoutbeweis. Der Original-Gamepointer-RVA2FBA4 wird
bereits im vorhandenen hash-/codegepinnten A1-Controlsreader verwendet.
Alle drei neuen Codeguards sind von relocationhaltigen Stores/Imports getrennt.

Neue reine Snapshotfunktion liest genau diese vier Sourcezeiger und den
ersten signed DWORD jedes vorhandenen Sourceobjekts, verlangt Range0..15
und ausschließlich local0→global8. Code, Gamepointer, Sourcezeiger und Index
werden zweimal unverändert gelesen; auch das ist keine atomare Beobachtung.
Der Wrapper nutzt den vorhandenen OwnOriginal-InventoryReader mit dessen
PID/Start/CWD/Dateisignatur/Hash/Base/Lesebereich-/Originalfingerprintguards.
Es gibt keine zusätzlichen Funktionsaufrufe im Spiel oder Hooks.

Root muss den ersten tatsächlichen Read vor600s ausdrücklich gegen eigenen
Original-PID/Start/Module, neue UDPverbindung, Query9, Server- und Original-
Sessiontabellen sowie unveränderte Botzuordnung0–7 gegenprüfen. Jede
Index-/Code-/Pointer-/Provenienzabweichung bleibt FAIL; keine ABIgrenze
lockern, lokale Reihenfolge annehmen oder Slot8 als Querykomplement erfinden.
Diese statischen Instruktionen beweisen weder Retail-Runtimeverträglichkeit
noch die unbekannte Syncursache. Eine spätere echte REA/Ghidra-/Nativeprüfung
ist als eigener Tool-/Abnahmebeleg zu dokumentieren.
