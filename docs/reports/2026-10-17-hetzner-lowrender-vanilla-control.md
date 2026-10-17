# 17.10.2026 – Echter externer Vanilla-Observer an Hetzner-Lowrender (Retail 1.07)

## Ergebnis

**PASS_LIMITED_155S_VANILLA_JOIN_AND_QUERY** – echte Retail-Vanilla-Sitzung mit vorbestehendem **einen Bot** auf einem separaten Hetzner-Lowrender-Testserver. Dies ist **kein** aktiver Kampf- oder 60-Minuten-/24/7-/CRC-Vergleichs-PASS und ersetzt keine anderen qualifizierten Release-Tests.

| Gate | Beobachtung | Urteil |
|---|---|---|
| Berechtigter isolierter Startzustand | Unmittelbarer Live-UDP-Preflight `READY_AT_CHECK_TIME`: TSE 1.07, 1/16 Plätze mit genau erwartetem Bot; vier originale Observer-Binärdateien exakt gegen vorher gesichertes SHA256-Manifest | PASS |
| Echter Vanilla-Beitritt | Unveränderter Windows-`SeriousSam.exe` im getrennten `TSE-WineObserver`-Profil; Game-Log zeigt `Sending statedelta request`, `Sending CRC request`, `joined` | PASS |
| Externer GameSpy-Status während des Laufs | **31/31** gültige UDP-Statusabfragen, **29/31** mit genau 2 Spielern. Erste zwei Abfragen noch vor abgeschlossenem Join; **0** Queryfehler und **0** dritte Spieler im Intervall | PASS im beobachteten Fenster |
| Geplante Laufzeit | **155,93 s**, vollständig bis zum Laufzeitende. Eigener Observer-Prozess blieb währenddessen aktiv. | PASS_LIMITED |
| Kontrollierte aktive Eingaben | Zusätzlicher einmaliger Sicherheitsversuch mit PID-/Fenster-Eigentümerkontrolle; Windows gewährte **keinen Fokus**, deshalb ausdrücklich **0 Maus-/Tastatureingaben** | OFFEN – **kein aktiver Combat-Test** |
| Client-Sync-Log | Erhaltener Log zeigt Join, kein `Too many bad syncs` und keine dokumentierte Disconnect-Meldung bis zum kontrollierten Ende | PASS_LIMITED – **Server-SYNCCHECK-CRC nicht erhoben** |
| Observer-DLL unverändert | SHA256 vor/nach exakt `1C41DA35B3FC47378C407B770E1BD1DCC2B7E6BF676C140586BC6035461D4208` | PASS |
| Anderer qualifizierter Bot-Client unverändert | `TSE-BotClient/Bin/GameMP.dll` nach dem Versuch weiterhin `61DC27E0E7B80BADCF9AE705C30FCA88EDD3935737715DFFFF59E90C26F1FEF9` | PASS |
| Lokale Wiederherstellung | Der eigene Test-PID ist beendet; ursprüngliches Observer-Log und `Scripts/PersistentSymbols.ini` nach dem Versuch SHA256-identisch mit den vorher gesicherten Versionen | PASS |
| Server-Spielerabbau | Server führte nach erzwungenem Ende **vorübergehend** den Observer weiterhin in der Query. Unabhängige wiederholte Live-Abfrage weist am **17.10.2026 00:58:47 UTC** wieder **nur den ursprünglichen einzelnen Bot** nach | PASS für schließlich wiederhergestellte Belegung; verzögerter Logout als **Verbesserungspunkt** |

## Konkrete Testdaten

- Remote-Kontrollhost **Shadow**, getrennte originale Retail-Installation `.codex/retail/TSE-WineObserver`.
- Ziel: gesonderte Hetzner-Lowrender-Instanz (Game-Port **25630**, GameSpy-Query **25631**); Zugangsdaten/Host-/Spieleridentitäten nicht im öffentlichen Bericht.
- Start: **2026-10-17T00:54:04.8039469Z**, Dauer **155,92976 s**.
- 31 Abfragen in ungefähr 5-s-Schritten; 29 Samples mit zwei Spielern, 2 während Start/Join nur mit dem ursprünglichen Bot.
- Verbindungsüberprüfung per **echtem Original-1.07-Clientlog plus unabhängigen UDP-Statusabfragen**, nicht bloß UDP-Ping.
- Im beobachteten Zeitfenster keine zusätzliche fremde dritte Person; preflight hatte unmittelbar zuvor vier verifizierte Originalhashes.
- Der Test wurde **nicht** in eine laufende aktive Partie mit einem anderen Spieler hineingestartet.

## Wichtige Cleanup-Erkenntnis

Der private einmalige Testwrapper stoppte den **eigenen** Client-PID mittels `Stop-Process -Force`. Das beendet die lokale Anwendung, sendet aber offenbar **keinen regulären In-Game-Disconnect**. Der Server zeigte den Spieler beim späteren Poll am **00:57:47 UTC** noch an. Eine zweite unabhängige Beobachtungsserie (7 Polls im Abstand von rund 10 s) zeigte am **00:58:47 UTC** erstmals wieder **1/16**. Der exakte serverseitige Disconnect-Zeitpunkt wurde nicht gemessen.

**Für neue Tests:** Selbst gestartete Clients möglichst zuerst über regulären `/Quit()`-/WM_CLOSE-Pfad mit kontrollierter Wartezeit beenden; nur bei tatsächlichem Hänger auf Force-Termination zurückfallen. Die serverseitige Population muss nach jedem Test unabhängig auf den ursprünglichen Zustand geprüft werden. *Zwei Spieler nach Ende des Clientprozesses beweisen nicht eine noch laufende lokale Sitzung.* Keine fremden Spieler oder produktiven Dienste kicken.

## Evidenz (privat auf Shadow, NICHT in GitHub hochladen)

`.codex/evidence/hetzner-lowrender-vanilla-isolated-20261017-025403/`

- `preflight.json`, `run.json`, `samples.jsonl`, `summary.json`
- `observer-after.log` sowie Sicherung/Wiederherstellung der vorherigen Log-/INI-Werte
- `pulse.jsonl`: `focused=false`, `actions=none` (kein fingierter Active-Input-Beleg)
- `post-exit-server-observation.jsonl`: Wiederherstellung der Ein-Bot-Belegung mit Zeitstempeln

Die temporäre Testhülle ist privat unter `.codex/evidence/mcp-toolchain-20261017/run-vanilla-lowrender-control.ps1` abgelegt. Sie ist **kein** freigegebenes Produktions-/Multi-Server-Startskript.

## Weitere Gates (noch offen)

1. Echte aktive Bot-/Vanilla-Interaktion auf einem **isolierten** Hetzner-Testserver (mit eigenem gezielt kontrollierbarem Eingabefenster), inklusive sichtbarer Actions/Kills/Respawns.
2. Server-seitige `SYNCBAD`-/`SYNCOK`-/`SYNCCHECK`-Logs sowie korrespondierende **erste** divergente Tick-/Sequence-/CRC-Werte aufbewahren; ohne diese Belege kein CRC-Root-Cause-Fix.
3. Sicheres **graceful client quit** plus maximal begrenzter Server-Rejoin-/Leave-Timeout als feste neue Abnahmebedingung.
4. Unabhängige 60-Minuten-Zwei-/Mehrclient-Beobachtung und anschließend getrennte 6-/24-Stunden-Soaks. Die lokal qualifizierte `61DC`-KI-Stunde bleibt eigenständig bestanden; dies ist ein zusätzlicher **155-s-WAN-Vanilla-Test**, keine Erweiterung auf eine Produktionsfreigabe.

Siehe [verbindliche Agentenanweisungen](../../AGENTS.md), [read-only Preflight](../../tools/Test-TSEExternalVanillaPreflight.ps1) und [Retail-Synchronisationsbericht](2026-10-17-retail107-sync-check-investigation.md).
