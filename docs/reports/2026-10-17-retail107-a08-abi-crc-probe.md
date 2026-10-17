# A08 / Agent A1 – Retail 1.07 Engine/GameMP: statische ABI-/CRC-Vorprüfung

**Datum:** 17.10.2026 · **Ticket:** #9 · **Koordination:** #18 · **Branch:** agent/A08/9-retail-abi-crc
**Freigabe:** A00, Issue #18: GRANTED_WRITE_ONLY für diesen Bericht und die zwei neuen A08-Tools. Keine GHIDRA_TSE_PROJECT-, SHADOW_RETAIL-, SHADOW_GAME_FILES-, Hetzner- oder Frida-Laufzeitfreigabe.

## Kurzbefund

Eine neue, rein lesende Windows-PE32-Analyse der **vier tatsächlichen Retail-/qualifizierten Dateien** ergibt: Sämtliche in den zwei GameMP.dll namentlich importierten Engine- und EntitiesMP-Symbole sind im jeweiligen Originalexport vorhanden. Beide GameMP.dll exportieren GAME_Create und verwenden beim Eintritt in GAME_Create den Maschinenbefehl PUSH 0x2FCC unmittelbar vor einem CALL (gleiche beobachtete Allokationskonstante, **kein** Beweis gleichen Feldlayouts).

**Damit wurde kein offensichtlicher fehlender Engine-/Entities-Import oder unterschiedlicher GAME_Create-Allokationswert in diesem Kandidaten nachgewiesen. Die eigentliche CRC-Divergenzursache bleibt offen.** Die Unterschiede der Engine-Importfunktionen und der MSVC-Laufzeit sind reale, aber derzeit nicht kausale ABI-Prüfansätze.

## Hashes der unveränderten Retail-Dateien

| Objekt | SHA256 | Größe |
|---|---|---:|
| Original Server Engine.dll | B79BF8BB3927FE4F8F252E141D721AE5C738DF02218F0ECC12DA5C1AFBCB534F | 2.138.170 B |
| Original Server GameMP.dll | 1C41DA35B3FC47378C407B770E1BD1DCC2B7E6BF676C140586BC6035461D4208 | 213.050 B |
| Qualifizierte BotClient GameMP.dll | 61DC27E0E7B80BADCF9AE705C30FCA88EDD3935737715DFFFF59E90C26F1FEF9 | 222.720 B |
| Original Server EntitiesMP.dll | 7F595F2A7FC96A978B3467983E8F17C70D827F17A5F4EE887F9C7A1F20B1D350 | 2.355.266 B |

Alle vier Hashes am 17.10. auf Shadow frisch berechnet. PE-Maschine x86 / PE32. Engine.dll der geprüften Server- und BotClient-Installationen SHA-identisch. Kein Binär- oder Prozesszustand verändert.

## Gemessene Import-/ABI-Eigenschaften

| Merkmal | Original GameMP | Bot GameMP |
|---|---:|---:|
| Exporte | 1: GAME_Create | 1: GAME_Create |
| Image Base | 0x60840000 | 0x10000000 |
| GAME_Create RVA | 0x0000FE20 | 0x00015B70 |
| PUSH 0x2FCC in ersten 48 Codebytes | ja, Offset 6 | ja, Offset 1 |
| Namentliche Engine.dll-Importe | 253 | 254 |
| Engine-Importe nicht im Originalexport | **0** | **0** |
| EntitiesMP.dll-Importe | 11 | 13 |
| Entities-Importe nicht im Originalexport | **0** | **0** |

Die Original-Engine besitzt **3.189** namentliche Exporte, EntitiesMP **2.614**. 14 Engine-Imports sind nur im Bot vorhanden, 13 nur im Original-GameMP. Im Bot zusätzlich unter anderem CPlayerAction::Clear und CTimer::GetHighPrecisionTimer. Das Original importiert MSVCRT.dll, der Bot VCRUNTIME140.dll und verschiedene api-ms-win-crt-* DLLs. Image-Base- und CRT-Unterschiede allein beweisen keine CRC-Abweichung.

Binärbeleg GAME_Create (erster Abschnitt): original 55 8B EC 51 53 56 68 CC 2F 00 00 E8; Bot 53 68 CC 2F 00 00 E8. 0x2FCC = **12.236 Bytes**. Gleiche Allokationskonstante beweist weder identische VTable/Feld-Offsets noch denselben Action- oder Sessionzustand.

## Wiederholbarer Offline-Test

Neue Datei tools/a08_retail_crc_probe.py: dependency-freier Read-only-PE32-Parser für MZ-/PE-Signatur, File-backed RVA, Export-/Import-Tabellen mit Namen und Ordinals, vier qualifizierte SHA256-Gates und GAME_Create-Allokationsmarker. Der Parser produziert JSON auf stdout; er schreibt keine Dateien, ändert keine DLL und öffnet keine laufenden Spielprozesse.

- **PASS_STATIC_PE_LINKAGE / Exit 0:** alle vier bekannten SHA256, PE32, GAME_Create, Anfangs-Allokationsmarker und benannten Engine-/Entities-Importe auflösbar.
- **FAIL_STATIC_PE_LINKAGE / Exit 1:** mindestens ein statischer Check scheitert.
- **ERROR_STATIC_PE / Exit 2:** beschädigte oder fehlende Eingabe/PE-Fehler.
- Parameter --allow-other-hashes ausschließlich für separate Testkopien; damit ist eine Retail-Qualifizierung ausdrücklich aufgehoben.
- Keine Aussage über Loader-DLL-Suchpfade, dynamisches GetProcAddress, echte ABI-Klassenlayouts, x87-/CRT-Simulation, CRC-Gleichheit oder die Laufzeit.

Reproduktionskommandos (Shadow / Python 3.12.10):

~~~powershell
$py = 'C:\Users\Shadow\AppData\Local\Programs\Python\Python312\python.exe'
$wt = 'C:\Users\Shadow\Documents\SeriousSam-TSE-Worktrees\agent-A08-9-retail-abi-crc'
$retail = 'C:\Users\Shadow\Documents\SeriousSam-TSE-Bot-Servermods-\.codex\retail'
& $py -B "$wt\tools\a08_retail_crc_probe.py" --engine "$retail\TSE-Server\Bin\Engine.dll" --retail-game "$retail\TSE-Server\Bin\GameMP.dll" --bot-game "$retail\TSE-BotClient\Bin\GameMP.dll" --entities "$retail\TSE-Server\Bin\EntitiesMP.dll"
& $py -B "$wt\tools\test_a08_retail_crc_probe.py"
~~~

**Tatsächlich gemessen:** Binaries PASS_STATIC_PE_LINKAGE, Exit 0; vier SHA-Gates true; 0 unerfüllte benannte Engine-/Entities-Importe. **16/16 In-Memory-Python-Regressionen PASS in 0,003 s**, Exit 0. Negativtests prüfen fehlende MZ/PE-Magic, PE32+-Ablehnung, kaputte RVA/Importe, fehlenden Export, fehlendes Importsymbol, falsche Allokationskonstante und strikte Qualifikationshashes. Plattform Windows, Python 3.12.10.

## CRC-Prüfgrenze und nächster gezielter Fehler-Test

Die in PR #21 bereits separat belegte echte Retail-1.07-Ghidra-Dekompilation weist für CPlayerAction::ChecksumForSync an **0x6019EC10** einen **Vier-Byte-Lese-/CRC-Loop** nach, während CSessionState::ChecksumForSync bei **0x601A5B10** weitere Action-/Session-/Entity-Zustände prüft. Die begrenzte Abdeckung der einzelnen Action-Methode ist ein belegter technischer Prüfgrenzenbefund, **nicht** die nachgewiesene Root-Cause eines aktuellen Bad-Sync-Disconnects. Es wäre nicht vanilla-kompatibel begründet, die Methode eigenmächtig auf sizeof(*this) zu ändern.

**Gezielter nativer Folgetest, ausdrücklich erst nach zusätzlicher A00-Freigabe:**

1. Isolierte Server-/Vanilla-/qualifizierte BotClient-Testkopien, exakte vier Hashes, gleiche Map und Settings, getrennte Profile/Ports; **un-instrumentierte Baseline** mit kontrolliertem aktiven Gameplay, kein geteiltes Runtime-Labor. Keine Änderung von ser_iKickOnSyncBad.
2. Nach Genehmigung x86-kompatible, eng begrenzte passive Messung im tatsächlichen Retail-Sync-Handler **FUN_601A2D10** (statische RVA 0x000E2D10). Geladene Modulbasis vorher prüfen. Bei erstem CRC-/Level-Mismatch Tick/Sequence, die zwei tatsächlich verglichenen 32-Bit-Werte und Prozess-/Binary-Kontext erfassen; Feldnamen aus Engine 1.10 erst nach ABI-Beleg verwenden.
3. Kontrolliert die vier von CPlayerAction::ChecksumForSync verarbeiteten Bytes und die weiteren CSessionState::ChecksumForSync-Teile untersuchen (RVA 0x000DEC10 bzw. 0x000E5B10). **Ersten** auseinanderlaufenden Action-/Session-/Entity-Input beweisen, statt alle späteren SYNCBAD-Fälle nur zu zählen.
4. Frida nur nach separater GHIDRA-/SHADOW- bzw. Instrumentierungsfreigabe im privaten, selbst kontrollierten x86-Prozess; Hook-Overhead in µs/Aufruf, Kontrolllauf ohne Hook, kontrolliertes Detach und Cleanup belegen. Nur dann nach Ursachenfamilie unterscheiden: ABI/Feldlayout, Action-Tick, deterministische Simulation/CRT oder Reihenfolge.
5. **A04-Handoff:** Fehleradresse, erster vergleichbarer Tick/Sequence, betroffene CRC-Inputklasse, vier Hashes, Instrumentierungs-Kennzahlen. Keine Änderung von A04-Parsern oder fremden Dumps, keine privaten Spieler-/Rohlogs veröffentlichen.

## Klare Abgrenzung

- **Nicht freigegeben, nicht gestartet:** GHIDRA_TSE_PROJECT, REA, Frida-TSE, SHADOW_RETAIL, SHADOW_GAME_FILES, HETZNER_RUNTIME.
- **Nicht erreicht:** konkrete neue CRC-Root-Cause, Runtime-Binär-Hook, neuer Bot-Build, Action-Sync-Fix, native Retail-/60-Min-/WAN-Abnahme.
- Kein Edit an tools/analyze_sync_log.py, tools/compare_sync_dumps.py, Spiel-Dateien oder fremden Agenten-Branches/Prozessen.
- Dieser Bericht ist ein reproduzierbares **statisches** A08-Testergebnis und eine sichere Eingrenzung, kein fehlerbehebender Gameplay-Patch.
