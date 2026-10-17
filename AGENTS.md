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

## Retail-1.07-Sync-Befund (17.10.2026, echte Ghidra-Dekompilation)

- [Verifizierter Sync-Bericht](docs/reports/2026-10-17-retail107-sync-check-investigation.md) **vor Arbeit an `Too many bad syncs` lesen**: Originale `Engine.dll` SHA256 `B79BF8BB3927FE4F8F252E141D721AE5C738DF02218F0ECC12DA5C1AFBCB534F`. GhidraMCP fand Handler `FUN_601A2D10`, Xrefs auf `SYNCBAD` und `Too many bad syncs` sowie CRC-Vergleich/Reset/Counter-Inkrement/Disconnect. Tatsächlicher Retail-Grenzwert **10** bei `0x602A7EB4` (Ghidra Memory `0a 00 00 00`, live gelesener Konfigurationswert einer unveränderten Binärdatei).
- **Zwei reale fehlgeschlagene Tests vom 10.10. belegt:** `eight-hour` SYNCBAD 1→10 bei Tick 83,40–92,40 + Disconnect; `eight-combat-only` SYNCBAD 1→10 bei Tick 23,50–37,15 + Disconnect. Nicht mit separat bestandenen Acht-Bot-Stunden verwechseln.
- Neuer portabler [`tools/analyze_sync_log.py`](tools/analyze_sync_log.py) liefert JSON-Auswertung von SYNCBAD/OK und Disconnects; auf beiden Originalen verifiziert. Logrohdaten sind privat auf Shadow, **nicht** veröffentlichen.
- Der Kickmechanismus ist belegt; die **eigentliche Ursache der unterschiedlichen Sync-Checksums ist weiterhin unbekannt**. Keine Scheinlösung durch `ser_iKickOnSyncBad=0`; zuerst ersten abweichenden Tick und tatsächlich betroffene Action-/Simulation-/State-Werte isoliert messen, vollständige neue Native-Abnahme nach einem Fix.

## Externe Tests und Release-Abgrenzung – 17.10.2026

- **Nicht** aus historischen `SYNCBAD`-Logs auf eine generelle Instabilität der qualifizierten `61DC...`-DLL schließen: die echte lokale 8-Bot-KI-Stunde (3697 s) ist für genau diesen Kandidaten bestanden. Mehrere Hetzner-1-Bot-/stationärer-Vanilla-Kontrollen sind ebenfalls **begrenzt** bestanden. Der aktive Drei-Spieler-Hetzner-Versuch hat 242 erfolgreiche Queries/2431,74 s mit zunehmenden Frags, aber **keine abschließende Stundenabnahme**. Siehe [Vergleichsmatrix im Retail-Sync-Bericht](docs/reports/2026-10-17-retail107-sync-check-investigation.md).
- Für einen neuen isolierten Vanilla-Test **vor jedem Start** [`tools/Test-TSEExternalVanillaPreflight.ps1`](tools/Test-TSEExternalVanillaPreflight.ps1) verwenden: SHA256 von vier Originalkomponenten + Prozessbelegung + frische GameSpy-UDP-Antwort mit **genau einem erwarteten Bot** und korrektem Port/Version. `canStart=false` bedeutet **nicht starten**. Ein `READY_AT_CHECK_TIME` gilt nur zum Prüfzeitpunkt; vor tatsächlichem Start nochmals prüfen und fortlaufend überwachen. Einen zusätzlich anwesenden externen Spieler **nicht** entfernen, ersetzen oder ungefragt in instrumentierte Tests einbeziehen.
- Reproduzierbare [acht bestandene Offline-Preflight-Checks](tools/Test-TSEExternalVanillaPreflight.Tests.ps1); Fixture-Mode liefert stets `canStart=false` und darf nie als Runtime-Freigabe gelten. Der historische private Lowrender-Preflight hatte einen bestätigten PowerShell-`@(...ConvertFrom-Json)`-Arrayfehler und wurde mit Live-Statusprüfung korrigiert. Die vier Vanilla-Dateien waren nie verschwunden.
- Alter `poc/scripts/Test-RetailJoin.ps1`-Harness **ersetzt** die aktive BotClient-`GameMP.dll`, sichert sie zwar vorab, **restauriert sie aber nicht automatisch**. Nie einen anderen Kandidaten darüber testen, solange keine eigenständige sichere Restore-Hülle existiert. Backup-/Restore-Fleet-Ablauf aus `poc/LOCAL-RELEASE.md` bevorzugen. Gegenwärtige qualifizierte Originale und DLLs unangetastet lassen.
- Die experimentelle Ground-Lookahead-DLL besitzt weiterhin **keine** native Freigabe. Die kurzen deaktivierten/probe-only-Kontrollen bestanden, aber beim aktiven 600-s-Retry wurden `Too many bad syncs`-Disconnects im Clientlog festgestellt. Keine Ground-Features in die qualifizierte DLL übernehmen, bevor Ursache und native Regression geklärt sind.

## Hetzner-Lowrender-Vanilla-Kontrolllauf 17.10.2026

- **Neu nachgewiesen:** [Echter Retail-1.07-WAN-Observer-Test](docs/reports/2026-10-17-hetzner-lowrender-vanilla-control.md), **155,93 Sekunden**, 31/31 gültige Statusabfragen, 29/31 mit zwei Spielern, echter Client-`joined`-Log, keine beobachtete `Too many bad syncs`-Meldung. Ergebnis **PASS_LIMITED** für Vanilla-Join/Statuskontinuität – **kein** aktiver Input, keine serverseitige CRC-Vergleichs- oder Stundenabnahme.
- Eigener temporärer Clientprozess ordnungsgemäß lokal entfernt; ursprüngliche Observer-Log-/INI-Inhalte und DLL-Hashes sind erhalten. Nach **erzwungenem** `Stop-Process -Force` stand der Observer zunächst als `ghost` in der Hetzner-Spielerliste, bis die Live-Abfrage wieder die ursprüngliche **Ein-Bot-Population** bestätigte. **Nächster Test muss Graceful-`Quit`/WM_CLOSE vor Force belegen** und remote Post-Exit-Belegung prüfen; anderen Spielern niemals den Slot entziehen.
- Automatische Gameplay-Eingaben sind **nicht** belegt: PID-gebundener Windows-Fokusversuch ergab `focused=false; actions=none`. Bei zukünftigen KI-/Combat-Gates nur echte Gameplay-Belege anerkennen.
- Rohlogs, Profile, GUI-Daten und Testskript bleiben lokal auf Shadow unter `.codex/evidence/hetzner-lowrender-vanilla-isolated-20261017-025403` / `.codex/evidence/mcp-toolchain-20261017`. **Nicht** in öffentliches Git committen.

## Einstieg

- [Repository-README und aktuelle Abnahme](README.md)
- [Vollständige Toolmatrix, letzte Installationsprotokolle und Routingregeln](docs/decisions/2026-10-17-tse-ai-tools-mcp-policy.md)
- [Cloud-Aufgaben #4](https://github.com/Escoba2024/SeriousSam-TSE-Bot-Servermods-/issues/4)
- [Shadow-/Hetzner-Aufgaben #5](https://github.com/Escoba2024/SeriousSam-TSE-Bot-Servermods-/issues/5)
