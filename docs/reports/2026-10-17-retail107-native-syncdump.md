# Retail 1.07: nativer Sync-Dump-Pfad – statischer Nachweis und sicherer Vergleich

**Stand:** 17.10.2026 · **Scope:** Originale Retail-1.07-`Engine.dll`, unverändert. Kein laufendes Spiel gestartet oder verändert.

## Qualifizierte Grundlage

- Originalserver `Engine.dll`: SHA256 `B79BF8BB3927FE4F8F252E141D721AE5C738DF02218F0ECC12DA5C1AFBCB534F`
- PE x86, Ghidra 12.1.4 / GhidraMCP 2.0 im separaten privaten Projekt `tse-syncdump-verify-20261017`; 10.668 Funktionen erkannt.
- Der belegte BotClient-Kandidat `61DC27E0E7B80BADCF9AE705C30FCA88EDD3935737715DFFFF59E90C26F1FEF9` wurde nicht angetastet.
- Statische Xrefs und tatsächliche Dekompilation, **keine native Laufzeitabnahme**. Private Ghidra-Daten bleiben auf Shadow außerhalb von Git.

## Tatsächliche Retail-1.07-Funktionskette

1. `CNetworkLibrary::Init` bei `0x601965F0` registriert den Shell-Schalter `user INDEX cli_bDumpSync;` (String `0x602A8F74`) mit der Datenadresse **`0x602CD6EC`**. Derselbe Init-Pfad registriert `cli_bDumpSyncEachTick` auf `0x602CD6F0` und `ser_iExtensiveSyncCheck`; letzteres allein belegt noch keine sicheren Runtime-Werte.
2. `CSessionState::SessionStateLoop` bei `0x601A8020` liest **`0x602CD6EC`** bei `0x601A85AE`, setzt den Wert bei `0x601A85C1` zurück und erzeugt mittels `CTFileStream::Create_t` die Datei **`temp\\syncdump.txt`** (String-Xrefs `0x601A85D7` und `0x601A85ED`).
3. Der Dump-Pfad ruft `ChecksumForSync`, formatiert eine CRC-Ausgabe und schreibt die zugehörigen Sync-Daten; String `CRC: 0x%08X` bei `0x602AB588` hat einen Xref im Loop bei `0x601A868F`.
4. Die explizit dekompilierte Funktion `CSessionState::DumpSyncToFile_t` bei **`0x601A7FC0`** ruft `ChecksumForSync`, gibt `CRC: 0x%08X` aus (Xref `0x601A7FFB`) und ruft `DumpSync_t`. Der Loop referenziert außerdem den Erfolgstext `Sync data dumped to '%s'` bei `0x601A86AD`.
5. Es wurden keine entsprechenden fertigen `temp\\syncdump.txt`-Dateien in den geprüften bestehenden vier lokalen Retail-Installationsverzeichnissen vorgefunden. Es wurde **kein** Laufzeitversuch ausgeführt.

**Bewertung:** Der eingebaute **One-shot-Sync-Dump-Pfad ist in Retail 1.07 statisch bestätigt**. Ob ein konkret isolierter BotClient/Server per Shell `cli_bDumpSync=1` einen gültigen Dump schreibt, muss noch nativ bestätigt werden. `cli_bDumpSyncEachTick` ist als Symbol belegt, aber seine konkrete Funktion im Retail-Release **nicht** bestätigt; insbesondere den DEBUG-Zweig aus Serious Engine 1.10 nicht ohne Nachweis auf Retail 1.07 übertragen.

## Zusatzbefund: Was der Retail-Action-CRC wirklich prüft

Eine weitere **echte Retail-1.07-Dekompilation plus x86-Disassembly** grenzt den Sync-Check genauer ein:

- `CPlayerAction::ChecksumForSync` bei `0x6019EC10` liest an `0x6019EC21` per `MOV CL, byte ptr [EAX + ESI*1]` jeweils ein Byte aus der **aktuellen CPlayerAction-Basisadresse plus Index**. `INC EAX` bei `0x6019EC36`, `CMP EAX,0x4` bei `0x6019EC37` und `JC` bei `0x6019EC3C` belegen **genau vier aufeinanderfolgende Bytes pro Action-Checksum-Aufruf**.
- `CSessionState::ChecksumForSync` bei `0x601A5B10` ruft für jeden aktiven Spieler die Action-Checksum zweimal auf und verarbeitet zusätzlich weitere Session-/Spieler-/Entity-Zustände. Deshalb bedeutet der Vier-Byte-Befund **nicht**, dass der gesamte Netzwerk-Sync nur acht Bytes prüft.
- Die separate Serious-Engine-1.10-Referenz besitzt in `NetworkMessage.cpp` die auffällige Stelle `CRC_AddBlock(ulCRC, (UBYTE*)this, sizeof(this));`; der tatsächlich dekompilierte Retail-x86-Code **belegt unabhängig** die Vier-Byte-Grenze. Diese Beobachtung ist keine bestätigte CRC-Divergenzursache.
- Konsequenz für die Snapshot-Auswertung: Die vollständigen gedruckten Action-Felder dürfen nicht mit dem tatsächlich allein durch **diese** Checksum-Methode abgedeckten Bytebereich verwechselt werden. Abweichungen können außerdem über Entity-CRC relevant sein, ohne dass diese statische Teilanalyse die komplette Feldabhängigkeit nachweist.

## Reproduzierbarer Offline-Vergleich

`tools/compare_sync_dumps.py` vergleicht zwei bereits vorhandene, vollständige Sync-Dump-Snapshots:

```powershell
python tools/compare_sync_dumps.py --server "PFAD_ZUM_SERVER_SYNC_DUMP" --client "PFAD_ZUM_CLIENT_SYNC_DUMP"
```

- Beide Snapshots müssen dieselben Werte für **Level, Sequence und Tick** enthalten; unterschiedliche Werte führen strikt zu `UNALIGNED` ohne Zustandsvergleich.
- CRC-Gleichheit/-Ungleichheit und positionsbasierte Unterschiede des ausgegebenen Zustands werden getrennt gemeldet. Das ist keine automatische Rekonstruktion des **ersten tatsächlich divergenten Ticks**.
- Der Report enthält keine Rohwerte der Spieler oder Entitys. Unterschiedliche Zeilen werden nur mit erlaubten Feldnamen, Zeilenindex und ggf. verkürztem SHA256-Fingerprint für zugelassene technische Felder ausgewiesen. Unbekannte Daten und Spielernamen erhalten weder Rohwerte noch Hashes. Original-Snapshots bleiben privat.
- Für Snapshot-Vergleiche ist dies ein **syntaktischer Textvergleich**, kein Engine-ABI-Beweis. Unterschiedliche Ausgabeformatierung und nicht ausgedruckte CRC-Eingaben bleiben mögliche Grenzen.
- CLI-Exitcodes: `0` = gleich und ausrichtbar; `3` = ausrichtbar, aber verschieden; `2` = ungültig/nicht ausrichtbar.
- Elf synthetische Python-3.12-Unittests (inkl. Datenschutz, Fehlformate, Sequence/Tick-Mismatch und CLI-Codes): **11/11 PASS**. `git diff --check` ohne Beanstandung.

## Nächste isolierte native Messung

1. Vor Start bestehende Shadow-/Hetzner-Prozesse, echte Serverbelegung, autorisierte Testinstanz, Original-Hashes und Spielversion prüfen. **Keine** bestehende fremde Partie unterbrechen. Qualifizierte Bot-DLL nicht ersetzen.
2. Zwei isolierte Retail-Prozesskopien mit gleicher Karte, gleichem `ser_iExtensiveSyncCheck` und dokumentierten Laufzeitparametern nutzen; gegen unveränderte Baseline messen. Standard-Kickgrenzwert nicht verändern.
3. Im jeweils eigenen Prozess den registrierten Shell-Schalter `cli_bDumpSync` **einmalig** aktivieren, erzeugte `temp\\syncdump.txt` sofort privat archivieren und die Ausgaben inklusive `Level`, `Sequence`, `Tick`, `CRC` prüfen. Keine bestehende Datei im Produktiv- oder Shared-Verzeichnis überschreiben.
4. Nur bei **identischem Sequence/Tick/Level** die beiden Dumps vergleichen; wenn zeitlich versetzt, Ergebnis `UNALIGNED` dokumentieren, keine künstliche Gleichsetzung oder Tick-Nachbearbeitung.
5. Bei reproduzierbarem CRC-Unterschied den ersten **beobachteten** Fehlvergleich und beteiligte Felder verfolgen. Falls die One-shot-Dumps nicht exakt ausrichtbar sind, erst dann passive, eng begrenzte Hook-/Breakpoint-Diagnose an einer privaten Testkopie erwägen, jeweils mit uninstrumentierter Baseline.

**Nicht erreicht:** kein aktueller first-divergence-Nachweis, kein neuer Retail-Sync-Fix, kein zusätzlicher nativer Join, keine 60-Minuten-/24-7-Freigabe, kein Frida-TSE-Runtime-Test.
