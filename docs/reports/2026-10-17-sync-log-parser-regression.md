# TSE Retail 1.07: portable Sync-Log-Parser-Regressionen

**Datum:** 17.10.2026. **Agent:** ChatGPT/RDC, unabhängiger Worktree `codex/chatgpt-sync-log-regressions-20261017`.

## Umfang

- Ausschließlich `tools/analyze_sync_log.py`, dessen neue `unittest`-Datei und dieser Bericht.
- Keine Änderung von Retail-Binaries, Bot-DLL, Supervisor, Dedicated-Server, Ports, GameSpy, Server- oder Clientprozessen.
- Vollständig synthetische Fixture-Logs; kein privater Rohlog im Git.

## Reproduzierbarer Befehl

Vom Repository-Root mit Python 3.12:

```powershell
python -m unittest discover -s tools -p test_analyze_sync_log.py -v
```

## Befund und Korrektur

Der bisherige Tick-Ausdruck `[\\d.]+` akzeptierte unzulässige Zahlen wie `12..3`. In `SYNCBAD` führte dies bei `float(tick)` zum reproduzierten `ValueError`; `SYNCOK` konnte falsch gekürzte Ticks erkennen. Der Tick-Matcher erlaubt jetzt nur die belegte dezimale Schreibweise mit höchstens einem Punkt und verwirft fehlerhafte Felder, ohne den Audit abzubrechen. Das ist Parser-Härtung, keine Aussage über Engine-Netzwerk-/Sync-Stabilität.

Sieben portable Tests decken interleavte Clients, bestätigte Disconnects, Counter-Reset-Segmente, reine Textmeldungen, beschädigte Ticks, CLI-JSON, fehlende Eingabedateien und leere Logs ab. **Ergebnis: 7/7 PASS**, Python 3.12 auf Shadow, `git diff --check` ohne Meldungen.

## Read-only-Kontrolllauf mit archivierten Fehlerlogs

Der neue Parser wurde zusätzlich auf zwei bereits privat archivierten Shadow-Retail-Logs vom 10.10.2026 ausgeführt. Die aggregierten Resultate bleiben exakt wie zuvor dokumentiert: je **10 SYNCBAD** und **1 expliziter Disconnect**; keine Synchronisations-OK-Meldung in diesen beiden Proben. Nur Aggregate wurden verglichen; keine privaten Logzeilen veröffentlicht und kein laufender Prozess beeinflusst.

## Grenzen

Kein neuer nativer TSE-Test, keine neue Server-Sync-Abnahme und keine Ursache für die bisherige CRC-Divergenz gefunden. Für Issue #5 bleiben kontrollierte Native-/Vanilla-Abnahmen erforderlich. Bei Zusammenführung die Tests bei Parseränderungen weiterhin ausführen.
