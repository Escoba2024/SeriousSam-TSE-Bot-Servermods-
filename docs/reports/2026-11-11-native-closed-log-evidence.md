# Abschließende native Rollenlogs nach normalem Schließen

Der neue portable Helfer `tools/native_closed_log_evidence.py` archiviert die
erhaltenen Rollenlogs erst nach der vom Controller bestätigten normalen
Schließung. Er prüft genau die archivierten Bytes auf SYNCBAD, Sync-Kicks,
CRC-Fehler, bekannte Crashmeldungen, CecilInvalidAction und Joinfehler.
Dadurch gehen Meldungen, die erst beim Schließen geschrieben werden, in die
abschließende Bewertung ein. Er startet, untersucht oder steuert keine Prozesse.

`archive_closed_role_logs` erhält explizit `role_roots`, `source_logs`,
`archive_logs`, `cleanup` und `expected_roles`. Alle vier Zuordnungen müssen
genau dieselben erwarteten Rollen enthalten. `cleanup[role]['closed'] is True`
ist eine Vertrauensgrenze: Der aufrufende Controller muss normalen Close,
Prozessidentität und Prozessende selbst nachweisen. Die aufgelösten Quelllogs
müssen unmittelbar im jeweils rollennamigen Verzeichnis liegen. Falsche Rollen,
fehlende oder leere Logs, gemeinsam verwendete Inodes, veränderte Quelldateien,
überlange Logs und Kopierfehler verhindern die Annahme. Archive entstehen
exklusiv und werden zurückgelesen; vorhandene Dateien werden nicht ersetzt.

Integration nach allen normalen Close- und Prozessende-Prüfungen:

```python
post = archive_closed_role_logs(
    role_roots={r: R / r for r in roles},
    source_logs={r: R / r / (
        'Dedicated_BotTest.log' if r == 'server' else 'SeriousSam.log'
    ) for r in roles},
    archive_logs={r: E / (r + '-closed.log') for r in roles},
    cleanup=records,
    expected_roles=roles,
)
report['post_close_logs'] = dataclasses.asdict(post)
if not post.accepted:
    report['errors'].extend('post-close ' + reason for reason in post.reasons)
# Anschließend vorhandene finale Bewertungslogik ausführen und Ergebnis sichern.
```

Die Ausgabe enthält SHA256, Dateigröße und Fundstellen als Zeilennummern,
keine Spielernamen oder Logzeilen. Die privaten Archive bleiben privat.
`accepted` bezeichnet ausschließlich diesen Logvollständigkeits- und
Fehlermustercheck; es ist keine Gameplay-, Stunden-, First-State- oder
Releaseabnahme. Ein normales Disconnect ohne Syncfehler gilt hier nicht als
Sync-Kick. Nicht erkannte Fehlerformulierungen bleiben eine Analysegrenze.

Gezielte RED/GREEN-Entwicklung: Der anfängliche Stub scheiterte an den
geforderten Fehler- und Archivierungsfällen; abschließend bestanden 16 Tests:

```sh
python3 -m unittest discover -s tools -p 'test_native_closed_log_evidence.py' -v
```

Die Tests enthalten insbesondere erst während Close ergänztes SYNCBAD samt
Kick, Crash/InvalidAction/CRC, fehlende Logs, falsche Rollen, Symlink-/Hardlink-
Verwechslungen, Kopierfehler und sauberen normalen Close. Dies sind portable
Datei-Fixtures, kein neuer nativer Lauf. Frühere Versuche behalten exakt ihren
dokumentierten Prüfzeitpunkt vor Close; diese Änderung liefert keine
rückwirkende Nach-Close-Abnahme.
