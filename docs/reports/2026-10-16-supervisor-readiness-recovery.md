# Supervisor: Bereitschaft nach einem Disconnect wiederherstellen

Ausgangspunkt: Supervisor-Branch `11b57e74c8f990e631822dc6b1472a6a1918c7ea` / PR #3. Ein bereits erfolgreich beigetretener Client konnte später die Verbindung verlieren und trotzdem als Prozess weiterlaufen. `Test-PopulationNativeReady` erkannte den Fehler korrekt, doch die zuvor gelöschte Join-Deadline wurde nicht erneut gesetzt. Der Controller blockierte weitere Starts unbegrenzt, ohne die getrennte Gruppe zu ersetzen.

Die Korrektur setzt bei späterem Bereitschaftsverlust erneut die bestehende 45-Sekunden-Frist, einmal pro zusammenhängendem Ausfall. Wiederhergestellte Bereitschaft hebt sie auf. Bei Ablauf greift der vorhandene identitätsgeprüfte Stop mit anschließendem Cooldown. `ObserveOnly` steuert keine Prozesse und setzt keine neue Frist. Ereignis: `ReadinessLost`. Keine Änderungen an GameMP, Engine, Entities oder qualifizierter DLL.

## Prüfung am 16.10.2026

- Neuer Regressionstest mit echten PowerShell-Kindprozessen und tatsächlichem Retail-Join-/BotDriver-/Disconnect-Logformat: vor der Änderung reproduzierbar FAIL (`Disconnected live client was not recovered within bounded readiness timeout`).
- Nach der Änderung PASS: dauerhaft getrennter, noch laufender Client wird innerhalb der Frist ersetzt (zwei Starts); kurzer Bereitschaftsverlust wird aufgehoben (ein Start).
- Voller portabler PowerShell-Scope: 23 Suiten PASS auf Shadow/PowerShell 7.6.6, einschließlich CLI-/UDP-/Prozessidentitätsadapter und neuer Regression. Wie im bestehenden Test-Publication-Runner bleiben RetailCleanup (benötigt eigenen Spieltest) und lokale Paketfixtures (benötigen qualifizierte SDK-Artefakte) ausgenommen.
- Unveränderte Python-Fixtures aus frisch extrahiertem Git-Archiv von `11b57e7` separat auf Linux: 25 + 9 + 10 = 44 Tests PASS. Verify-SourceProvenance: alle 13 veröffentlichten Quellen und exakte Original-Captures PASS.
- Der bestehende kombinierte Runner wurde wegen fehlender Python-Laufzeit auf Shadow nicht als ein einzelner Aufruf ausgeführt. Die beiden Teile wurden getrennt geprüft. Kein neuer nativer Supervisor-Spiel-Lifecycle oder 24/7-Test aus dieser Regression ableiten.

Private Rohbelege: Shadow `.codex/evidence/supervisor-readiness-recovery-20261016/full-regression/`. Neue echte Spieleläufe zur unabhängigen Wine-Sync-Untersuchung sind getrennte Tests, keine Supervisor-Abnahme. Merge und weitere native Recovery-/Race-/Controllerausfall-Prüfungen bleiben eigene Gates.
