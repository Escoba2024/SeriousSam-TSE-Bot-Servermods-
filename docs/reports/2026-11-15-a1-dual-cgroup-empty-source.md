# A1: zwei exakte cgroup-empty-Quellen

Der neue reine Transform `tools/a1_dual_cgroup_exit_patch.py` akzeptiert genau
die zwei vorhandenen A1-Monitor-Backends. Er ersetzt ausschließlich `empty()`
durch den bereits geprüften Root-Methodenkörper: `cgroup.procs` zuerst lesen;
nur `FileNotFoundError` mit exakt diesem Dateinamen erlaubt eine anschließende
Existenzprüfung. Bei Wiedererscheinen bleibt das Ergebnis **nicht leer**.
Andere Dateinamen, fehlender Dateiname, EACCES und EIO werden weitergeworfen.

| Variante | SHA256 vorher | SHA256 nach reinem Transform |
|---|---|---|
| outer strict_backend.py | fb759339e7de8b31dd0fc490a0f3152be78a00d9e13f0ecb39443bc7cf7f8c1c | 4cbbc678539401bef6df22f321b8d031ec837af7a24fa729b96c350df7ae3f9b |
| nested vendor/colt/strict_backend.py | 13394a9cb3a69d081f9071861d36a5663367995e4b62c00738d6c4e869ef121a | a1c94e45db07b8764566d545e934648e432476f3a8032637827920e72c6500f7 |

Für beide Varianten ist die vollständige inverse Quelle bytegleich. Alle
Bytes außerhalb des einen Methodenkörpers bleiben erhalten; der übrige AST
einschließlich PID-/ready-/identity-/quiescent-Pfaden ist unverändert. Ein
`pid=None` am Testbesitzer wird weder aufgerufen noch als Leerheitsbeleg benutzt.
`BEFORE` und `AFTER` entsprechen exakt dem unveränderten Root-Helfer
`native_cgroup_exit_patch.py`, SHA256
`bd4eece1b033da99a94da1ac53e2ba415929bf6b33005924735d40a98948f119`.

Die Tests kompilieren nur die tatsächlich aus den SHA-gepinnten Quellen
extrahierte Methode. Gegen unveränderte Parents entstand echtes RED: sechs
Lesereihenfolge-Assertions und vier FileNotFoundError-Unterfälle scheiterten,
darunter reales Tempfile-Unlink. Kein Import-/Setupfehler. Nach Transform:

```sh
nice -n 15 python3 -m unittest tools.test_a1_dual_cgroup_exit_patch
```

**5 Tests PASS, 0,115 s**: beide Parents, verschwundene/leere/belegte Datei,
Wiedererscheinen, reale Unlink-Race, falscher/fehlender Fehlerdateiname,
Permission/EIO einschließlich zweiter Existenzprüfung, None-PID sowie
Fremdquellen-/Fremdänderungsablehnung und vollständige Inversen.

Private Logs und exklusive 0600-Quittung liegen im isolierten Worktree unter
`.codex/evidence/a1-dual-cgroup-empty/`. Quittung SHA256:
`5a3e388b881c724fa65a2c1a134536fd1cbaef6e7cb5fd49279e35200199fac5`.

Kein Paket erzeugt, keine Runtime gestartet und keine Metadaten-/Timestamp-
oder Nativequalifikation. Der portable Racebeleg erklärt nicht rückwirkend
den konkreten historischen ON-Fehler. Root integriert und entscheidet eine
spätere eigenständige Paketableitung.
