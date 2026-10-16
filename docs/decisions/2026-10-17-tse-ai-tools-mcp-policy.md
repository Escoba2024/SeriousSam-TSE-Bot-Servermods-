# TSE 1.07 – KI-Toolchain, MCP-Entscheidungen und Einsatzregeln

**Entscheidung vom 17.10.2026.** Gilt für alle weiteren Entwicklungs-, Debugging-, Test-, Cloud-, Shadow- und Hetzner-Schritte. Statusangaben zur Installation stammen aus den Übergabe-/Installationsprotokollen vom 16.–17.10.2026 und sind **keine neue Live-Prüfung**. Vor kritischen Einsätzen Verbindung und tatsächliche Toolfunktion erneut prüfen.

## Projektziel und unverhandelbare Abnahme

Serious Sam The Second Encounter **Retail 1.07**: Bots sind reguläre Netzwerkspieler über getrennte modifizierte BotClient-Prozesse. Vanilla-Client und Dedicated-Server bleiben unverändert. Referenzquelle Serious Engine **1.10** ist keine verifizierte ABI-/CRC-/Protokollidentität mit Retail 1.07. Die bekannte native Abnahme/DLL SHA256 `61DC27E0E7B80BADCF9AE705C30FCA88EDD3935737715DFFFF59E90C26F1FEF9` bleibt unangetastet; neue Binaries erhalten eine eigene Abnahme. Für jede Aussage klar unterscheiden: Codeprüfung, MCP-Smoke-Test, Prozess-/Join-Test, Sync-Stabilität, Retail-Abnahme, externe Listung, Dauerbetrieb.

**Priorität am 17.10.** Offene `Too many bad syncs`-Fälle/Vanilla-Langzeit-Synchronisierung und unabhängige externe Browser-/333networks-Abnahme vor 12/16-Bot-Skalierung, UI-Klonen oder Kosmetik. Es gibt teils kurzfristig bestandene native Join-/Linux-Bot-Belege, aber keine pauschale Dauer-/24/7-Freigabe.

## Toolauswahl pro Arbeitsart

| Tool | Letzter dokumentierter Status | Einsatz in TSE | Verbindliche Regel |
|---|---|---|---|
| **Codex CLI auf Shadow** | Gestartet/benutzt, GPT-6.1 Sol High; bestehende Prozesse möglich | Umsetzung, C++-Fehlerbehebung, Bot-KI, Supervisor, Buildskripte, Regressionen | Standard-Codeagent; laufende Session nicht unterbrechen, Branches/PRs und Regressionen dokumentieren. |
| **Codex Cloud** | Cloud-Umgebung/Cloud-Lauf am 16.10. nicht bestätigt | Source-Review, portable Tests, unabhängiges QA, PR-Review | Nur bei tatsächlich verfügbarer Cloud-Umgebung; niemals Cloud-Test als Retail-Windows- oder native TSE-Abnahme ausgeben. Issue #4. |
| **Remote Desktop Commander (RDC) + Shadow** | Verbindung/Fernsteuerung zuletzt bestätigt | Windows-x86-Build, Debugger/Ghidra starten, Retail-Join, Observer, Engine-/GPU-/Dauertests | Standardzugang für echte lokale Tests; private Runtime-Daten auf Shadow, nicht ins öffentliche Git. Issue #5. |
| **Hetzner-Server** | Query-/Direktverbindung in Teiltests nachgewiesen; öffentliche Listung/Dauerbetrieb offen | Wine/Linux/Dedicated/Bot-Host, externe UDP- und Stabilitätstests | Getrennte, reproduzierbare Host- und Clientproben; niemals UDP-Query mit Masterserver-Listung gleichsetzen. |
| **REA / rea-agents 6.5.0** | Installiert, Codex-MCP + Skill, `doctor` healthy und Test-EXE analysiert | **Priorität A:** gezielte Querverfolgung nativer Retail-1.07-Binaries, Spiel-/DLL-Initialisierung, Netz-/Join-/Sync-Pfade | Bei ungeklärten Binärfunktionen oder 1.07/1.10-Abweichungen einsetzen; Findings mit Adresse, Datei-Hash, Toolversion, Beleg und Unsicherheit festhalten. Nicht als automatischen Beweis deuten. |
| **Ghidra 12.1.4 + GhidraMCP 2.0** | Installiert, MCP in Codex aktiviert, **30 MCP-Tools** im Smoke-Test erkannt. Echter TSE-E2E-Lauf nicht nachgewiesen | **Priorität A:** Decompilation, Cross-References, Callgraphen, Klassen, VTables, ABI, Sync-Funktionsvergleich | Vor Nutzung Ghidra starten, unveränderte Binärkopie laden, Ghidra-Plugin/API und MCP-Verbindung verifizieren; nur Analyse/Annotation, Änderungen erst separat nach Review. |
| **Frida 17.24.0 + Frida MCP 0.1.1** | Installiert, MCP in Codex aktiviert, **13 Tools** im Smoke-Test geprüft. Live-Hook an TSE noch nicht nachgewiesen | **Priorität A bei Runtime-Unklarheit:** gezielte Prozess-Hooks, Funktions-/API-Tracing, Argumente/Aufrufzahlen, Session-/Speicherbeobachtung gegen reproduzierbaren `bad syncs`-Fehler | Nur eigene autorisierte, isolierte Testprozesse; möglichst read-only/passive Hooks, keine unkontrollierten Schreib-/Replace-Aktionen, keine dauerhafte Produktionsinstrumentierung; uninstrumentierte Kontrollprobe und rückstandsfreies Detach. |
| **GitHub (Connector + Repo)** | Verbunden, Repo `Escoba2024/SeriousSam-TSE-Bot-Servermods-` zugänglich | **Pflicht:** Source-of-Truth für Code, Issues, PRs, Entscheidungslog, reproduzierbare Tests | Branch/Commit/PR vermerken; keine Zugangsdaten, Retail-Binaries, private Profile/rohe Logs oder unfreigegebenen Artefakte hochladen. |
| **Google Drive + Notion** | Google Drive/Notion in bisherigen Projektübergaben als aktualisiert dokumentiert; Notion-Zugriff via Connector möglich | Statusboards, Roadmap, Handoffs, Forschungsübersichten, Reviewboard | Ergänzende Projektübersicht; technische Akzeptanzwerte bleiben in versionierten Repo-Berichten maßgeblich; Synchronisierung als eigene Aktion kennzeichnen. |
| **AI App Cloner 2.0.0 / `clone-app`** | Skill auf Shadow in Codex registriert; Web-Demo/Tests bestanden | **Priorität C:** höchstens später mobile React-Native/Expo-Status- oder Monitoring-App als eigenes Projekt | **Nicht** für Bot-KI, Retail-DLL, 3D-Engine oder native Server einsetzen. Screenshot→Expo-Prozess ist kein C++-/Protokoll-Reversing. Erfordert für visuelle Differenzprüfung Browserautomation. |
| **UI-TARS Desktop** | Installation auf Shadow **nicht bestätigt** (nur angefragt) | **Priorität C/optional:** GUI-Automation bei Ghidra, Debugger, Explorer, Testdialogen | Erst Installation, Modellanbindung und Single-Monitor-Test nachweisen; RDC/Skripte bevorzugen; kein unkontrolliertes Klicken in produktive Server, keine Garantie für unbeaufsichtigte Robustheit. |
| **GMX MCP** | Testzugriff/Draft/Anhangsvorschau protokolliert; echter Versand teils ungetestet, Onlinezustand fluktuierte | Dokumentversand auf expliziten Auftrag | Nicht Bestandteil von Runtime, Debugging oder automatischer TSE-QA; Freigabe vor Versand, keine Secrets exportieren. |
| **Blender 5.2.3 / Runway** | Blender vom Nutzer als installiert genannt; Runway verfügbar/getestet im Kreativkontext, keine TSE-Laufzeittests | Visualisierungen/Demo-Videos, allenfalls spätere Assets | Keine Priorität vor den technischen Abnahmen; keine Bot-Engine- oder Sync-Diagnose durch Render-Tools. |

## Entscheidungsbaum für den nächsten Agenten

1. **Reiner Code-/Test-/Reviewfehler** → Codex CLI/Cloud + GitHub. Portable Tests dokumentieren. Kein nativer PASS ohne Retail-Lauf.
2. **Binärfunktion unklar, 1.07 vs. 1.10, ABI/CRC, Decompilation** → **REA + GhidraMCP** auf Shadow; zuerst Tool- und Plugin-E2E-Smoke, dann isolierte statische Analyse. Binaries nur aus legalem lokalem Bestand, nicht committen.
3. **Laufender Prozess, `Too many bad syncs`, Join-Disconnect, Timing, Aktionserfassung** → **Frida MCP + native Windows-/Wine-Tests via RDC**; Baseline mit/ohne Instrumentierung und Vergleich zu Serverlogs. REA/Ghidra bei daraus gewonnenen Adressen nachschalten.
4. **GPU-/Retail-/Vanilla-Observer-/Mehrprozess- oder externe Netzwerk-Abnahme** → Shadow/Hetzner mit RDC, definierten Zeitfenstern/Hashes und getrennten Belegen. Erst nach stabiler Sync-Baseline skalieren.
5. **GUI-Handgriffe** → RDC/Skripte; UI-TARS nur als optionales, erst zu prüfendes Hilfsmittel.
6. **UI- oder Präsentationswunsch** → optional App Cloner/Blender/Runway, als **separate** Arbeit, nie als Ersatz für technische Funktionen.
7. **Projektkommunikation** → GitHub maßgeblich; Drive/Notion ergänzen, GMX nur auf Auftrag.

## Qualitäts- und Sicherheitsregeln

- Keine vorhandenen qualifizierten DLLs, gespeicherten Retail-Installationen oder laufenden Codex-/Observer-/Dedicated-Tests ohne Backup und explizite technische Notwendigkeit überschreiben/abbrechen.
- Vor Toolausführung: Verfügbarkeit, konkrete Version, MCP-Registrierung, laufende Prozesse, Zielbinary-SHA256 und Berechtigung dokumentieren.
- Für Ghidra/REA: Belege aus sauberem Analyseprojekt, Funktion/Adresse, Referenzversion und Gegenprüfung. **Serious-Engine-1.10-Quelltext nur als Hypothesenhilfe für 1.07.**
- Für Frida: funktionierende Baseline, möglichst minimale Hooks, Performance-Effekt messen, keine Echtzeitdaten/Hashes in öffentlichem Repo; aus Logs nur bereinigte Erkenntnisse.
- Ein Smoke-Test von 30/13 MCP-Tools bestätigt die Werkzeugschnittstelle, **nicht** eine bestandene Analyse oder ein durchlaufendes TSE-Szenario.
- Nicht alle MCPs permanent gleichzeitig aktivieren; nach Diagnosebedarf gezielt wählen, Messstörungen vermeiden.
- Jeder Folgeagent liest dieses Dokument und `AGENTS.md` vor neuer relevanter Arbeit und aktualisiert Entscheidungen bei belegten Änderungen.

## Quellen zu Fähigkeiten (keine Beweise lokaler Installationen)

- REA: https://github.com/morluto/rea
- GhidraMCP v2: https://github.com/MartijnvanPraag/GhidraMCP
- Frida MCP: https://github.com/neeetman/frida-mcp ; Frida: https://frida.re/docs/
- AI App Cloner: https://github.com/Birkenpapier/ai-app-cloner
- UI-TARS Desktop: https://github.com/bytedance/UI-TARS-desktop
- Serious Engine 1.10 (Referenz mit Versionsvorbehalt): https://github.com/Croteam-official/Serious-Engine

## Nachweisstatus dieser Änderung

Dieses Dokument protokolliert eine **Toolauswahl- und Arbeitsentscheidung**. Keine neue TSE-1.07-Binäranalyse, kein neuer Frida-Hook, keine native Abnahme und keine neue UI-TARS-Installation wurden hier durchgeführt.
