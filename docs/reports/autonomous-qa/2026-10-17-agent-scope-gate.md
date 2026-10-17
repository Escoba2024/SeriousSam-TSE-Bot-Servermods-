# A03 / #25 – Offline-Git-Scope-Gate für autonome KI-Agenten

Datum: 17.10.2026. Auftrag: [GitHub-Issue #25](https://github.com/Escoba2024/SeriousSam-TSE-Bot-Servermods-/issues/25); Koordinations-/Freigabequelle: [Issue #18](https://github.com/Escoba2024/SeriousSam-TSE-Bot-Servermods-/issues/18).

## Zweck

Der eigenständige `tools/autonomous-qa/check_agent_scope.py` prüft alle von einer Branch-Basis abweichenden Dateipfade (committed sowie staged, unstaged und untracked) gegen **ausdrücklich als Verzeichnisse** freigegebene Pfadpräfixe. Ein verweigerter Pfad führt zu Exit **2**, technische Fehler wie fehlende Git-Basis oder unklarer Worktree zu Exit **3**. Nur Exit **0** ist ein bestandener Pfad-Check.

Im Issue #25 ist ausschließlich `tools/autonomous-qa/**` und `docs/reports/autonomous-qa/**` für neue Schreibänderungen genehmigt. Andere Quellen, insbesondere Engine.dll, GameMP.dll, Supervisor, aktive Test-/Spieldateien und `docs/coordination/**`, bleiben ausgenommen.

## Nachweisbare lokale Tests (Shadow, Windows / Python 3.12)

```powershell
cd C:\Users\Shadow\Documents\SeriousSam-TSE-Worktrees\agent-A03-25-autonomous-qa
C:\Users\Shadow\AppData\Local\Programs\Python\Python312\python.exe -B -m unittest discover -s tools/autonomous-qa -p test_*.py -v
```

Ergebnis am 17.10.2026: **12/12 PASS, Exit 0**. Die Tests verwenden ausschließlich temporär angelegte, synthetische Git-Repositories. Geprüft wurden u.a. neue/staged/committed Dateien, Umbenennungen samt Originalpfad, Directory-Lookalikes, kritische fremde Pfade und ungültige Base-Referenzen.

## Beabsichtigter Integrationsaufruf

```powershell
python -B tools/autonomous-qa/check_agent_scope.py --repo . --base origin/main --allow tools/autonomous-qa/ --allow docs/reports/autonomous-qa/
```

Der `--base`-Ref muss zur tatsächlichen Pull-Request-Basis passen. Für gestapelte PRs kann `origin/main` eine zu breite Dateimenge abdecken; dann wird sicher abgelehnt, bis A00 die korrekte Merge-Basis bestimmt hat.

## Schutz und Grenzen

- Prüft Git-Pfade, nicht den Besitz eines lebenden Laufzeitprozesses. Kein atomarer GitHub-Lease- oder Runtime-Lock.
- Der Aufruf ist **kein automatischer Commit-/Push-Blocker**, solange CI/Supervisor ihn nicht tatsächlich vor einem Push erzwingt. Für eine spätere Integration sind A00-Dateiclaim und Code-Review erforderlich.
- Änderungen außerhalb des überprüften Git-Repos, ausgeführte Programme, Secrets und bereits publizierte Remote-Änderungen werden nicht nachgewiesen.
- Es wird keine Native-Retail-, Bot-Join-, SYNCBAD-, WAN- oder Langzeitabnahme behauptet.
- Kein Server-/DLL-/Runtime-Eingriff. Keine bestehenden Agenten-Dateien verändert.
