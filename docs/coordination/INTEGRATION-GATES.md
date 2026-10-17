# A00 – Integrations- und Abnahmegates

Für **jedes** vorgeschlagene Merge separat prüfen und im PR dokumentieren:

1. **Identität und Kollision:** Claim + A00 GRANTED + Handoff vorhanden; Commit-SHA und Basis sind bestimmt; Dateien gegen **alle** offenen PRs abgeglichen; kein fremder Worktree/Branch überschrieben; bei Konflikt serialisieren.
2. **Diff und Sicherheitsgrenzen:** `git diff --check`, unabhängiges Review, nur freigegebene Paths; kein Retail-Binary, private Rohlogs, Tokens, Spieler-ID oder Buildoutput. Provenance und 1.07/1.10-Abgrenzung prüfen.
3. **Portable Gate:** exakte Versions-/Befehl-/Testergebnisse; neue Tests auf dem Fehlerfall RED und anschließend GREEN, relevante Alttests. GitHub-Status nur dann behaupten, wenn wirklich auslesbar.
4. **Windows-Gate:** Windows + PowerShell 5.1/7 sofern betroffen; Prozesstreue, PID + Startzeit, Locks, Cleanup, Fehlerabbruch, WOW64 und restore; Linux-SKIP != PASS.
5. **Retail-Gate:** autorisierter separater Retail-1.07-Client, native DLL-Hashes, Join/Action/CRC/Sync und Kontrolllauf; `61DC27E0E7B80BADCF9AE705C30FCA88EDD3935737715DFFFF59E90C26F1FEF9` **nicht** überschreiben; alle neuen Binaries unabhängig qualifizieren.
6. **WAN-/Dauergate:** Direkt-IP, UDP-Query, 333networks/Master, In-Game-Browser, 60-min/24h werden **getrennt** belegt. Kein vorzeitiger Produktiv-/Skalierungs-PASS.
7. **Merge-Freigabe:** A00 vermerkt `READY_FOR_MERGE` mit SHA, PR, Konfliktplan, bestandenem jeweils **für diesen Änderungstyp** erforderlichen Gate. Ohne dokumentierte Freigabe PR bleibt Draft/ungemerged. Nach Merge erneut Status- und Workspace-Inventur.

## Bekannte Reihenfolge am 17.10.2026

- **Supervisor, überlappend:** #3, #7, #8, #10, #11 sind Entwicklungs-/Vorstufen; #12 konsolidiert, #13 baut auf #12. **Nur ein** geprüfter Integrationskandidat nach W1/W2 und Merge-Base-Review; Vorstufen nicht blind zusätzlich übernehmen.
- **Separate Pfade:** #14, #16, #17 können **unabhängig reviewed** werden, aber Konflikte im Zielbranch bleiben möglich.
- **Publikationsrunner:** #15 und #12 ändern `tools/Test-Publication.ps1`: vor Merge diff3/gezielte Rebase in **eigenem** Integrationsworktree, danach volle portable und Windows-Checks.
- Keine automatische Merge-Freigabe aus einem PR-Status „checks passed“, wenn relevante native Gates nicht abgedeckt sind.
