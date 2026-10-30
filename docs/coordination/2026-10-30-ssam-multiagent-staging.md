# ssam.ai – Drei OpenCode-Agenten: Staging und Betriebsvoraussetzungen

Stand: 2026-10-30. Der Benutzer möchte M1, M2 und M3 parallel entwickeln und aus ChatGPT überwachen.

## Bestandsaufnahme

- Das live verbundene ssam.ai System Control verweigert bei laufendem M1 bereits den zweiten Start: Existing OpenCode task ... still running.
- Die produktive MCP-Implementation ist aktuell ein Single-Task-Launcher. Ihre Source liegt unter /opt/ssam-system-control und ist über das freigegebene read-only-MCP nicht einsehbar.
- Remote Desktop Commander ist online, aber das Toolkontingent beträgt 0 %. Kein autorisierter Schreibzugriff auf diese Installation aus dem aktuellen Chat.
- Aktive externe M1-Task-ID: 12042155c1bdfc84b04ed0c3, ursprüngliche Runner-PID 3039. Eigenständiger Worktree /home/opencode-tse/workspaces/ssam-m1-agent-20261030.
- Die OpenCode-Aufträge M2 und M3 sind als GitHub-Issues #83 und #84 vorgemerkt; noch keine eigenen OpenCode-Task-IDs.

## Dieser PR: tatsächlich implementierter Umfang

- Standalone-Python-Controller unter tools/ssam_multiagent/manager.py; noch nicht auf Ubuntu installiert und nicht an den bestehenden MCP-Server angebunden.
- Bis zu drei Slots M1/M2/M3 mit eigenem Git-Worktree, eigenem Branch, fest gepinnter Quelle (SHA) und eigener Task-ID.
- Start verweigert, wenn Ziel-Worktree bereits vorhanden ist, Quell-SHA nicht passt, Slot belegt ist, ein Status ungeklärt ist oder Systemreserve unterschritten wird.
- Schutz des bestehenden M1-Worktrees; weder M1 stoppen noch zurücksetzen noch blind übernehmen.
- Task-Registry mit PID + /proc-Startticks, Modell, Branch, SHA, Started/Finished, Exitcode; private Logdateien und Promptdateien mit Besitzerrechten.
- JSON-Statusabfrage über das CLI und begrenzte Logabfrage für autorisierte lokale Benutzer.
- Keine öffentlichen Serverstarts und keine native Runtime-Automatisierung.

## Technische Grenzen und Sicherheitsentscheidung

- Die bestehende OpenCode-Task-Sperre im produktiven Backend wurde NICHT entfernt.
- Der derzeit laufende M1-Task ist extern und wird von diesem neuen Controller NICHT automatisch verwaltet. ChatGPT muss ihn weiter über das bestehende ssam-MCP abfragen.
- M2/M3 sind auch nach Veröffentlichung dieses PR nicht automatisch gestartet. GitHub-Commit ist weder Installation noch Deployment.
- Eine echte drei-Agenten-Abnahme setzt ein geprüftes Ubuntu-Deployment, neue MCP-Tools und eine Ressourcen-/Native-Runtime-Koordination voraus.
- Alle nativen Spieltests müssen über eine exklusive global abgestimmte Runtime-Lease abgesichert werden. Diese Durchsetzung in sämtlichen bestehenden Testharnessen fehlt noch.
- Die 8-Bot/120-Minuten-Abnahme für M1 ist auf Nutzerwunsch zurückgestellt; die öffentliche Instanz darf nicht unaufgefordert aktiviert werden.
- Bei geändertem PR-Head scheitert ein Start bewusst mit einer SHA-Prüfung statt still auf neuen Code umzuschalten.

## Noch zu implementierende MCP-Integration (nur an geprüfter Originalquelle)

1. start_opencode_agent(slot, prompt, model): exakt M1/M2/M3 validieren, Slot-Ownership, PIDs, Worktree und Quell-SHA prüfen, ohne freie Shell oder freie Pfadangabe von Chat.
2. list_opencode_agents(): drei Slots und alle laufenden eigenen/externen Legacy-Tasks samt PID, Task-ID, Modell, Branch, letztem Update und Status darstellen.
3. get_opencode_agent(slot, task_id, log_lines): autorisierte private Logs serverseitig begrenzen/redigieren.
4. Native-Lock und Ressourcenlimits vor privaten Retail-Tests durchsetzen; M2 gegenüber M1 priorisieren, M1-8-Bot-Dauerlauf bleibt ausgesetzt.
5. Staging-Tests, vorhandene MCP-Tools und Tunnel abgleichen, kontrolliertes Deployment mit Backup/Rollback, anschließende Live-Drei-Agenten-Abnahme.

## Reproduzierbare Befehle (erst nach kontrollierter Installation auf Ubuntu als opencode-tse)

    python3 /opt/ssam-multiagent/manager.py status
    python3 /opt/ssam-multiagent/manager.py start M2 --prompt-file /opt/ssam-multiagent/prompts/M2.txt
    python3 /opt/ssam-multiagent/manager.py start M3 --prompt-file /opt/ssam-multiagent/prompts/M3.txt
    python3 /opt/ssam-multiagent/manager.py logs TASK_ID --lines 50

## Abnahmematrix

| Prüfung | Ist-Zustand |
|---|---|
| Entwurf und CLI-Quellcode | Commit/PR erstellt |
| Offline-Test mit drei Fake-Prozessen | CI 5/5 PASS (https://github.com/Escoba2024/SeriousSam-TSE-Bot-Servermods-/actions/runs/41083921944) |
| PID-Reuse, Worktree-Schutz | Tests vorhanden, Ausführung offen |
| Deployment auf Ubuntu | NICHT ERFOLGT |
| Drei native OpenCode-Prozesse | NICHT NACHGEWIESEN |
| ChatGPT-MCP-Tool für drei Slots | NICHT IMPLEMENTIERT |
| M1 nicht unterbrochen | Bei letzter Live-Abfrage aktiv; erneut kontrollieren |

## Nächster Schritt

Mit neu verfügbarem autorisiertem Ubuntu-Schreibzugriff die wirklichen server.py/runner.py prüfen und diesen separaten Controller nach Tests als schmale, rückwärtskompatible Ergänzung integrieren. Bis dahin keine Sicherheitsmechanismen umgehen und den laufenden M1-Task nicht verändern.