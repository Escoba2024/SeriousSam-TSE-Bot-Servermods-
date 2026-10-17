# Retail TSE 1.07 – Nachweis zum Fehler „Too many bad syncs“
**Datum:** 17.10.2026 (Europe/Berlin) · **Ergebnis:** Server-Sync-Abbruchmechanismus im echten Retail-Binärcode bestätigt. Ursache der CRC-Divergenz **offen**.

## Unveränderte untersuchte Dateien

- Retail-Server: `.codex/retail/TSE-Server/Bin/Engine.dll`, 2.138.170 Bytes
- SHA256: `B79BF8BB3927FE4F8F252E141D721AE5C738DF02218F0ECC12DA5C1AFBCB534F`
- Retail-Observer-`Engine.dll`: identischer SHA256-Wert.
- PE, x86 32 Bit, Image Base `0x600C0000`, Ghidra 12.1.4: 10.668 erkannte Funktionen.
- **Weder Engine.dll noch GameMP.dll, Bot-Profile, Dedicated-Konfigurationen oder laufende Spielprozesse verändert.**

## Nachgewiesene Retail-1.07-Funktionskette (GhidraMCP-Headless)

1. Der String `Too many bad syncs` liegt an `0x602AADA0`, sein Xref an `0x601A3550` in `FUN_601A2D10`.
2. `SYNCBAD` an `0x602AAD64` hat Xref `0x601A3511`, `SYNCOK` an `0x602AADB8` hat Xref `0x601A35BD` – ebenfalls in `FUN_601A2D10`. `SYNCLATE` und `SYNCEARLY` werden im selben Handler referenziert.
3. Funktionsanfang `0x601A2D10`, Funktionsende `0x601A407F`, 4.976 Bytes. Im Dekompilat ist der relevante Message-Case `0x13`; `CNetworkMessage::Read(..., 0x10)` liest den Sync-Block. Die 1.10-Referenz benennt die Struktur `CSyncCheck`; die genaue 1.07-Strukturlayout-Gleichheit ist nicht gesondert ABI-verifiziert.
4. Die dekompilierte Prüfstrecke vergleicht zunächst `local_40 == local_28` und anschließend `local_44 == local_2c`. Bei bestandenem zweiten Vergleich setzt sie den zählerartigen Session-Wert auf **0**. Bei Abweichung inkrementiert sie ihn, schreibt optional `SYNCBAD` und vergleicht gegen `DAT_602A7EB4`.
5. Der tatsächliche initialisierte **Retail-Grenzwert ist 10**, nicht bloß ein aus 1.10 übernommener Wert: GhidraMCP `read_memory(0x602A7EB4,8)` meldet `0a 00 00 00 01 00 00 00`, und Xrefs auf `0x602A7EB4` kommen aus `0x601A353A` (**READ**, Handler) sowie `0x60196DF0` (`CNetworkLibrary::Init`). Sobald der Sync-Fehlerzähler mindestens diesen Wert erreicht, ruft der Handler den Disconnect-Pfad mit der Meldung `Too many bad syncs` auf.
6. `ser_iKickOnSyncBad` ist in Retail 1.07 als Konfigurationssymbol (`user INDEX...`) vorhanden; der Speichereintrag wird in `CNetworkLibrary::Init` referenziert. Auch `ser_bReportSyncBad`, `ser_bReportSyncOK`, `ser_bReportSyncLate` und `ser_bReportSyncEarly` wurden in der echten DLL gefunden.

**Vergleich zur Engine-1.10-Referenz:** `.codex/SeriousEngine-reference-20261010/Sources/Engine/Network/Server.cpp` Zeilen 1381–1455 vergleicht `sc_iLevel` und `sc_ulCRC` für denselben Tick, setzt bei korrektem CRC den Counter zurück und kickt nach `ser_iKickOnSyncBad`. `Network.cpp` Zeilen 95–107 enthält dort den Default 10 und Sync-Check-Frequenz 1,0s. Retail 1.07 bestätigt den Vergleich-/Zähler-/Kick-Pfad und den Wert 10 unabhängig; die Bezeichner der beiden verglichenen Felder bleiben bis zur vollständigen Layoutvalidierung aus der 1.10-Referenz abgeleitet.

## Echte Logbelege zu fehlerhaften Testläufen

- `.codex/evidence/shadow-20261010/local-release/eight-hour/retail/TSE-Server-Dedicated_BotTest.log`: zehn aufeinanderfolgende `SYNCBAD`-Meldungen für den Client `127.0.0.1` von Sequence 1689 / Tick **83,40** (`bad 1`) bis Sequence 1869 / Tick **92,40** (`bad 10`) und danach **`Client ... ordered to disconnect: Too many bad syncs`**.
- `.codex/evidence/shadow-20261010/local-release/eight-combat-only/retail/TSE-Server-Dedicated_BotTest.log`: Zähler **1 bis 10** zwischen Tick **23,50** und **37,15**. Auch hier anhaltende CRC-Divergenz; explizite Trennungsmeldung nicht Bestandteil des geprüften Ausschnitts.
- `.codex/evidence/hetzner-native-crt-control-20261016/bot-previous.log`: tatsächliches `Disconnected: Too many bad syncs` um Bot-Tick 15400; weitere Bot-Meldungen nach Disconnect beweisen **keine** fortbestehende korrekte Server-Synchronisierung.
- `.codex/evidence/hetzner-vanilla-isolated-20261016-222317/previous-SeriousSam.log`: `Disconnected: Too many bad syncs` nach Gameplay-Meldungen mit Bot/human player. Der Logname „vanilla isolated“ allein beweist nicht die vollständigen Client-/Binary-Bedingungen.

**Wichtige Trennung:** Die genannten konkreten fehlgeschlagenen Runs dürfen nicht mit anderen, separat abgenommenen stabilen Acht-Bot-/Stunden-Läufen verwechselt werden. Ein Ordnername `eight-hour` oder eine Laufzeitangabe ist kein eigenständiger PASS.

## Priorisierte technische Hypothesen (noch keine Root-Cause-Bestätigung)

1. Server und (Bot-)Client verarbeiten reguläre Actions oder deren Sequenz-/Tick-Zuordnung unterschiedlich.
2. Unterschiedliche Simulation/ABI/Float-/Random-/Entity-Zustände führen trotz formal korrekter Join/CRC zu divergierendem Sync-CRC.
3. Wine-/Host-Timing, Action-Buffer oder Paket-Reihenfolge könnten die Divergenz begünstigen; Netzwerk-Latenz allein ist **nicht** als CRC-Fehlerursache bewiesen.
4. Die 1.10-Referenz prüft u.a. Sequence, Level, Pause, Player-Actions und Player-Entitys im Sync-CRC (`SessionState.cpp` Zeilen 765–812); welche Felder tatsächlich bei Retail-1.07 für den Fall abweichen, ist **offen**.

## Nächster reproduzierbarer Prüfauftrag

1. Bewährte DLL `61DC27E0E7B80BADCF9AE705C30FCA88EDD3935737715DFFFF59E90C26F1FEF9` und Originale unverändert lassen. Test auf **separaten privaten Kopien** mit Hashes ausführen. Keine Änderung im Produktiv-Host.
2. Kontrollmatrix mit exakt derselben Version, Map, Netzwerkparameter und Laufzeit: Vanilla-/Server-Baseline, isoliert ein BotClient, anschließend Variation Combat/Navigation, dann mehrere Bots – jede Stufe mit **nicht instrumentierter** Kontrollprobe.
3. Pro Server-/Client-Lauf `SYNCBAD`-Starttick, Sequence, fortlaufenden Zähler, `SYNCOK`-Reset, Map-/Join-/Leave-Ereignisse, Action-Ticks, Binary-Hashes, Prozessumgebung und Port erfassen. `ser_bReportSyncBad` auf isoliertem Testserver zur Beobachtung nutzen, eventuell `ser_bReportSyncOK` nur kurzfristig mit Loggrößen-/Performancekontrolle. **`ser_iKickOnSyncBad` nicht herunterregeln oder deaktivieren, um vermeintlich stabile Runs zu erzeugen**.
4. Auf Shadow/Wine nach separatem Frida-MCP-Test nur minimal passive, x86-kompatible Hooks an der **geladenen** Engine verwenden. Statischer Handler-RVA: `0x601A2D10 - 0x600C0000 = 0x000E2D10`; nach Runtime-ASLR den Modul-Load-Base-Wert neu bestimmen. Nur nach isoliertem Baseline-Test.
5. Den **ersten** divergenten Tick und das betroffene Sync-Feld anhand eines kontrollierten Client-Server-Logvergleichs isolieren; erst dann mögliche BotDriver-/Action- oder Engine-spezifische Korrektur vorschlagen. Eine korrigierte DLL muss anschließend komplett neu nativ abgenommen werden.

## Verifizierbare private Rohbelege / Toolausführung

- `.codex/evidence/mcp-toolchain-20261017/engine_sync_probe.py`: Headless-GhidraMCP, String-/Xref-/Hashprüfung.
- `engine_sync_static_107.json`: Suchbegriffe, Adressen und Xrefs (privat, nicht committen).
- `engine_sync_decompile.py` und `retail_sync_handler_decompilation.private.txt`: originale Funktionsanalyse (privat).
- `engine_sync_handler_mcp_107.json`: vollständige relevante MCP-Toolantworten (privat).
- `engine_sync_defaults.py`: Default- und Xref-Gegenprüfung in Ghidra.
- Ghidra-Projekt außerhalb des Git-Repos: `C:\Users\Shadow\Documents\AI-Research-Tools\ghidra-workspaces\tse-engine-sync-20261017`.

**Kein Codefix, keine neue native Runtime-Abnahme, kein Frida-TSE-Live-Hook und keine öffentliche 333networks-/Browser-Freigabe wurden in diesem Schritt durchgeführt.** Siehe [allgemeinen Toolchain-Bericht](2026-10-17-mcp-toolchain-qualification.md) und [AGENTS.md](../../AGENTS.md).
