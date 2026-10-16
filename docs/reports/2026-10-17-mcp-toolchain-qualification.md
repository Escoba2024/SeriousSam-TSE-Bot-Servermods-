# 17.10.2026 – REA/GhidraMCP/Frida Toolchain-Gate auf Shadow

## Kurzurteil

**TEILWEISE BESTANDEN – Werkzeugnachweis, keine neue Serious-Sam-Runtime-Abnahme.**
Shadow-Gerät `SHADOW-P9FLKL5K` via Remote Desktop Commander online. Die vorhandenen Codex-Sitzungen, Retail-Installationen und qualifizierten DLLs wurden nicht absichtlich beendet/ersetzt. Lokal ist `main` noch auf `f4a1a33` (mit untracked `error.log`), während GitHub aktuellere Dokumente besitzt; keinen gewaltsamen Sync/Merge ausgeführt.

| Gate | Stand 17.10. | Tatsächlicher Beleg / Grenze |
|---|---|---|
| REA 6.5.0 | **PASS (Scope-Doctor)** | `npx.cmd -y rea-agents@6.5.0 doctor --client codex --provider ghidra --skill --format json` mit `GHIDRA_INSTALL_DIR` und `JAVA_HOME`: `healthy=true`, `environment_healthy=true`; Skill v42 (207 Tools), Codex-Registrierung und Ghidra 12.1.4/JDK 21 validiert. Ein **unspezifischer Audit-Wide-Doctor** ohne die beiden Umgebungsvariablen meldet fälschlich für den beabsichtigten Scope fehlende Analyseprovider; das ist kein Beweis eines defekten Codex-Scopes. |
| GhidraMCP 2.0 / Ghidra 12.1.4 | **PASS (echte Headless-Binäranalyse)** | `pyghidra 3.1.0` in ausschließlich `GhidraMCP/.venv` ergänzt. Über Python-MCP-Client `stdio` den `ghidra-mcp.exe --headless` mit bestehendem GhidraMCP-JAR, eigenem Projekt und rechtmäßig vorhandener **unveränderter Retail-Server-DLL** gestartet. `get_program_info`, `search_functions_by_name`, `list_exports` und `decompile_function` ohne Toolfehler. Echte `GAME_Create`-Dekompilation nachgewiesen, Adresse `6084FE20`. Es ist ein Python-MCP-Client-Gate, **kein Codex-agentischer GUI-/MCP-E2E-Nachweis**. |
| Frida 17.24.0 / Frida-MCP 0.1.1 | **PASS (Frida-Python-Smoke, begrenzt)** | Testprozes `python.exe` nur lokal temporär gestartet, Frida `attach`, JavaScript-Hooks `kernel32!Sleep`, `kernelbase!Sleep`, `ntdll!NtDelayExecution`, drei Ereignisse durch **expliziten NativeFunction-Selbstaufruf im Testprozess**, `script.unload`, `detach`, Prozess beendet, Exit 0. **Nicht** nachgewiesen: natürlich auftretende Zielprogramm-Hooks, Frida **MCP**-Toolcall, TSE-instrumentierter Vanilla-Kontrolllauf, Laufzeit-Overhead. Frühere Versuche ohne Selbstaufruf hatten null beobachtete Treffer trotz erfolgreicher Injektion. |
| Codex-MCP-Registrierung | **PASS (konfiguriert, nicht alle live getestet)** | `codex.cmd mcp list`: `rea`, `ghidra`, `frida` jeweils `enabled`. `codex.ps1` wird von lokaler ExecutionPolicy blockiert; `codex.cmd` funktioniert. |
| GhidraMCP GUI auf :8080 | **BLOCKIERT durch Portkonflikt** | `http://127.0.0.1:8080/` gibt HTML-`<title>tunnel-client</title>` zurück, Listener-PID 1824 = `C:\Users\Shadow\Projects\gmx-mcp\tools\tunnel-client\bin\tunnel-client.exe`. Codex-Ghidra-MCP-Registration zeigt `--ghidra-server http://127.0.0.1:8080/` und ist deshalb für GUI-Backend **nicht verwendbar**, obwohl `enabled` steht. GMX-Dienst wurde nicht gestoppt/umkonfiguriert. Headless-MCP verwendet einen eigenen ephemeren localhost-Port. |
| TSE Retail-Runtime/Sync | **UNGETESTET** | Kein Bot-Lauf, kein `Too many bad syncs`-Tracing, keine neue DLL, keine 60min-/24/7-, Masterserver-, externe Browser- oder Join-Freigabe. |

## Hash-bezogene Fakten

Unveränderte Retail-Server-`GameMP.dll`:
- Pfad: `.codex/retail/TSE-Server/Bin/GameMP.dll` (nur privat auf Shadow)
- **SHA256:** `1C41DA35B3FC47378C407B770E1BD1DCC2B7E6BF676C140586BC6035461D4208`
- **Dateigröße:** 213050 Bytes
- Ghidra identifiziert PE x86 32-bit, Image Base `60840000`, 1221 Funktionen / 280 externe Funktionen.
- `GAME_Create`: `6084FE20`, Export und Dekompilation belegt; bei der Anlage wird unter anderem ein Objekt mit `operator_new(0x2fcc)` allokiert und `CNetworkProvider::CNetworkProvider` aufgerufen. **Dies ist zunächst ein struktureller Binärbefund, kein Hinweis auf den aktuellen Sync-Rootcause.**
- Originale `TSE-Server`- und `TSE-Observer`-`GameMP.dll` weisen laut lokaler Hashprüfung denselben SHA256 auf.
- Vorhandene qualifizierte Bot-DLL `.codex/retail/TSE-BotClient/Bin/GameMP.dll` entsprach per SHA256-Präfix dem dokumentierten `61DC27E0E7B80BAD...`-Kandidaten. Bestehende qualifizierte Binärdateien nicht überschrieben.

## Reproduktionshinweise / private Testbelege

- Shadow-privat (Git ignoriert): `.codex/evidence/mcp-toolchain-20261017/ghidra_headless_probe.py` und `frida_smoke.py`. Keine Retail-Binaries, Spielinhalte, Zugangsdaten, Session-Tokens oder Rohlogs nach GitHub hochgeladen.
- Ghidra-Projekt: `C:\Users\Shadow\Documents\AI-Research-Tools\ghidra-workspaces\tse-toolchain-20261017` (außerhalb des Git-Repository).
- **Achtung Pfadregel:** Ghidra/PyGhidra `ProjectLocator` verweigerte ein Ghidra-Projekt unter dem Pfadsegment `.codex` mit `Path element starting with '.' is not permitted`. Mit separatem Projektpfad ohne führenden Punkt **behoben**.
- `python -m pip show frida frida-mcp` unter `AI-Research-Tools\frida-mcp\.venv` meldet 17.24.0 / 0.1.1.
- Frida-Smoke-Test meldete `attached=true`, `hook_hits=3`, `errors=[]`, `pass=true`, `self_test_complete`, nachfolgende Aufräumroutine beendet nur den selbst gestarteten Testprozess.
- Anmerkung: Eine nachgelagerte isolierte Erprobung der **Frida-MCP-Clientliste** konnte in diesem Durchlauf nicht ausgeführt werden; daher Frida-MCP-E2E **offen**, auch wenn die Registrierung sichtbar ist.

## Anschlusskonfiguration nach dem Test

Nach erfolgreichem Python-MCP-Headless-Test wurde **zusätzlich** die globale Codex-MCP-Registrierung `ghidra_tse` eingerichtet (`codex.cmd mcp add ghidra_tse`) und mit `codex.cmd mcp get ghidra_tse` geprüft: **enabled=true**, Transport `stdio`, Backend `ghidra-mcp.exe --headless`, originale Retail-Server-`GameMP.dll`, eigenes Ghidra-Projekt außerhalb des Repositorys, JAR der installierten Erweiterung und die nötigen Java/Ghidra-Umgebungsvariablen. Sie ist die bevorzugte Ghidra-Registrierung für neue TSE-Agentensitzungen; die ältere `ghidra`-GUI-Konfiguration auf dem vom GMX-Tunnel belegten Port **nicht** verwenden. Bestehende laufende Codex-Prozesse/Sitzungen wurden nicht neu gestartet. **Grenze:** Registrierung und separates MCP-E2E sind belegt; ein *Codex-Agent selbst*, der über `ghidra_tse` die Dekomposition startet, wurde noch nicht live getestet.

## Verbindliche Folgemaßnahmen

1. **Ghidra-Integration für Codex reparieren, ohne GMX zu unterbrechen**: für GUI-Plugin dedizierten freien Port wählen und dort Backend starten, `codex ghidra` darauf konfigurieren; oder speziell einen separaten **Headless-MCP-Server** mit fixem eigenem Projekt/Testbinary registrieren. Kein Produktiv-Codex-MCP auf den GMX-HTML-Port zeigen lassen.
2. **REA**: gezielte Retail-1.07-ABI-/CRC-/Sync-Hypothese an einem tatsächlich reproduzierten Problem analysieren. Statische `GAME_Create`-Dekomposition nicht als Sync-Kausalbeleg ausgeben.
3. **Frida MCP**: zunächst MCP-Toolcall/Attach/Detachment an eigenem Testprozess nachweisen. Für TSE nur minimal-invasive read-only-Hooks auf isolierten Testprozessen, mit nicht instrumentiertem Kontrolllauf und Leistungsmessung. Kein Produktionsserver-Hooking.
4. **Priorität**: `Too many bad syncs` / ursprüngliche Vanilla-Synchronität und externe Serverbrowser-/UDP-Nachweise vor 12/16-Bot-Skalierung.
5. **Git-Synchronisierung**: keine laufenden Codex-Worktrees und lokalen untracked Dateien überschreiben; bei nächstem kontrollierten Agenten-/Worktree-Start `AGENTS.md` und die Toolentscheidungsdatei aus GitHub einbeziehen. Dieses Dokument ersetzt keine frische Prüfung.

Siehe [Toolentscheidung](../decisions/2026-10-17-tse-ai-tools-mcp-policy.md) und [Issue #9](https://github.com/Escoba2024/SeriousSam-TSE-Bot-Servermods-/issues/9).
