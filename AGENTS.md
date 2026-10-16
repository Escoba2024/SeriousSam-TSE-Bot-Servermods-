# Arbeitsanweisungen für KI-Agenten – Serious Sam TSE Classic 1.07

**Verbindlich vor TSE-Projektarbeit:** [Toolchain- und MCP-Entscheidungen vom 17.10.2026](docs/decisions/2026-10-17-tse-ai-tools-mcp-policy.md) lesen und anwenden. Diese Richtlinie gilt für Codex CLI, Codex Cloud, ChatGPT/RDC und beteiligte Analyseagenten. Sie ersetzt keine tatsächliche Prüfung der lokalen Toolverfügbarkeit.

## Ziel und Qualität

- **Vanilla-kompatible TSE-Retail-1.07-BotClients**: Bots als normale Netzwerkspieler; unveränderte menschliche Clients und Dedicated Server.
- **Serious Engine Open Source 1.10 != Retail 1.07** hinsichtlich ABI, Engine, Binär- und Netzwerkschnittstellen, bis speziell nachgewiesen.
- Bestehenden qualifizierten Retail-Kandidaten schützen (siehe README.md und Phase-3-Bericht). Jeder Rebuild ist ein neuer Kandidat ohne automatische Runtime-Abnahme.
- Sauber unterscheiden: statische Analyse, MCP-Smoke, portabler Unit-Test, Windows-Build, native Retail-Abnahme, Join, Sync-Langzeitstabilität, externer Browser, 24/7. Nichts als bestanden melden, was nicht getestet wurde.
- Offene Sync-Probleme (u.a. `Too many bad syncs`) und externe Sichtbarkeit haben Vorrang vor Bot-Skalierung/UI-Kosmetik.

## Werkzeuge bedarfsorientiert verwenden

1. **Codex CLI / Codex Cloud**: Code, Review, Regressionen und portable Tests. Cloud kann echte Retail-Windows-Prozess-/Vanilla-/GPU-/Hetzner-Abnahmen nicht ersetzen. GitHub-Issue #4 beachten.
2. **RDC + Shadow / Hetzner**: native Windows/Wine/Linux-/Mehrprozess-/Vanilla-/Netzwerktests, nachvollziehbare Logs und SHA256. Vor Veränderungen laufende Tests, bestehende Prozesse und Backups prüfen. Issue #5 beachten.
3. **REA + GhidraMCP**: verwenden, wenn Retail-1.07-Binärfunktionen, ABI/CRC, GameMP oder CPlayerAction-/Join-/Sync-Pfade nicht aus Quellcode/Logs belegbar sind. Vor Einsatz Ghidra-Session/Plugin/MCP gegen Testbinary verifizieren; Erkenntnisse mit Funktionsadresse, Datei-Hash und Gegenprüfung festhalten.
4. **Frida MCP**: verwenden, wenn ein reproduzierbares Laufzeitproblem im eigenen, autorisierten TSE-Prozess vorliegt. Minimale passive Hooks bevorzugen, uninstrumentierte Kontrollprobe und Performancekosten erfassen; keine riskante Speicheränderung oder Manipulation des produktiven Servers.
5. **GitHub**: Code + technische Berichte sind maßgeblich. Branches/PRs/Issues und Testkommandos nachvollziehbar führen. Keine privaten Rohlogs, Tokens, Konfigurationen, Retail-Binaries oder urheberrechtlich geschützte Spieldaten veröffentlichen.
6. **Drive/Notion**: zusätzliche Projektübersicht und Übergaben, nicht Ersatz für reproduzierbare versionierte Testbelege.
7. **UI-TARS Desktop**: bislang nicht als installiert bestätigt; nur optional für GUI-Automation nach erfolgreichem Einrichtungstest. RDC/Skripte bevorzugen.
8. **AI App Cloner (React Native/Expo)**, **Blender**, **Runway**, **GMX MCP**: keine Werkzeuge für Bot-Kernlogik, GameMP-Binary, Netzwerk-Sync oder native Abnahme. Nur bei explizitem separatem UI-/Darstellungs-/Versandbedarf.

Nicht alle MCP-Server ohne Diagnosebedarf gleichzeitig betreiben. Vor jeder Schlussfolgerung Tool-Smoke-Test von echtem TSE-End-to-End-Nachweis trennen. Neue Einsatzentscheidungen und überprüfte Statusänderungen in `docs/decisions/` dokumentieren, nicht stillschweigend als neue Fakten behandeln.

## Shadow-Werkzeugnachweis 17.10.2026 (vor Toolnutzung lesen)

- [Echter Qualifikationsbericht REA/GhidraMCP/Frida](docs/reports/2026-10-17-mcp-toolchain-qualification.md) dokumentiert **bestanden**: REA-Doctor im korrekten Codex-/Ghidra-Scope; GhidraMCP-Headless über Python-MCP mit Import, Export, Funktionssuche und `GAME_Create`-Dekompilation an originaler Retail-DLL (SHA256 `1C41DA35B3FC47378C407B770E1BD1DCC2B7E6BF676C140586BC6035461D4208`); Frida-Python-Hook-Selbsttest auf eigenem Wegwerfprozess. **Noch nicht bestanden:** Codex→Ghidra GUI-E2E, REA-Sync-Hypothese, Frida-MCP-Toolcall und TSE-Runtime-Hook.
- **Portkonflikt!** Codex-`ghidra` ist derzeit auf `http://127.0.0.1:8080/` registriert, aber dort lauscht der GMX-`tunnel-client`, nicht Ghidra. Diesen Dienst **nicht** stoppen. Für neue TSE-Sitzungen **`ghidra_tse`** verwenden: seit 17.10.2026 zusätzlich global als `stdio`-Headless-MCP mit separatem Analyseprojekt und originaler Retail-Server-DLL registriert und mit `codex.cmd mcp get ghidra_tse` geprüft. Den fehlerhaften GUI-Eintrag **`ghidra` auf :8080 nicht aufrufen**, bis sein Backend separat korrigiert ist. `enabled` bei `codex mcp list` allein ist keine erfolgreiche Backend-Verbindung; ein echter Codex-Agentenaufruf über `ghidra_tse` steht weiterhin aus: Ein isolierter Codex-v0.163.0-Test mit `--sandbox read-only`/`approval: never` sah den MCP-Eintrag, bekam aber `MCP tool call requires approval, but approval policy is never`. Für die nächste echte Diagnose eine eingeschränkte, **autorisierte** MCP-Freigabe konfigurieren; keine Sicherheitsumgehung, nicht wiederholt Testagenten starten. Den funktionierenden unabhängigen Python-MCP-Headless-Nachweis als Referenz verwenden.
- Ghidra-Projektverzeichnisse nicht unter dem Pfadsegment `.codex` anlegen; PyGhidra verweigert Punkte am Anfang eines Projektpfadsegments. Private Analyse liegt auf Shadow außerhalb des Git-Repository. Keine Runtime-/Dauerfreigabe aus statischen Analysen ableiten.

## Einstieg

- [Repository-README und aktuelle Abnahme](README.md)
- [Vollständige Toolmatrix, letzte Installationsprotokolle und Routingregeln](docs/decisions/2026-10-17-tse-ai-tools-mcp-policy.md)
- [Cloud-Aufgaben #4](https://github.com/Escoba2024/SeriousSam-TSE-Bot-Servermods-/issues/4)
- [Shadow-/Hetzner-Aufgaben #5](https://github.com/Escoba2024/SeriousSam-TSE-Bot-Servermods-/issues/5)
