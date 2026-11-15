# Reversible Verpackung einer expliziten Restorekopie – Sourcevorbereitung

Neuer reiner Pythonhelfer `tools/restore_copy_roundtrip.py` stellt drei explizite
APIs bereit: `inventory(exact_root)`, `pack(exact_root,fresh_archive,reserve=...)`
und `restore(archive,fresh_target,expected_archive_sha256)`. Kein CLI, kein
historischer Defaultpfad, keine Prozess-/Runtime-/Drive- oder Löschfunktion.
Die bestehenden Root-Retirehelfer wurden nur gelesen: Ihr Muster
Manifest/Hash/Apply/Verify wurde wiederverwendet, deren fehlende atime-/Xattr-
Sicherung und enthaltene Lösch-/Prozesssteuerung erfüllen diesen Vertrag nicht.

Die FD-gebundene Inventur liest Dateien und Verzeichnisse mit NOATIME/NOFOLLOW;
reguläre Dateien müssen genau einen Link haben. Symlinks, Specials, `.git`,
Sparsefiles und fehlende SEEK_HOLE-Unterstützung werden abgewiesen. Datei- und
Verzeichnisrecords enthalten Bytes/SHA sowie UID/GID/mode/atime_ns/mtime_ns und
alle Xattrs als opake Hexbytes. ACLs/Capabilities sind enthalten; jeder nicht
lesbare/setzbare oder abweichende Wert verhindert Erfolg. Ctime/Inodes werden
nicht als rekonstruierbar ausgegeben. Sourceänderungen während der Inventur
oder Verpackung verhindern Erfolg.

Archive werden ausschließlich neu mit O_EXCL/0600 erstellt, vollständig gegen
Manifest/Payload/SHA geprüft und manuell in ein frisches Ziel rekonstruiert.
Kein `extractall`; nur exakt indizierte reguläre Nonsparse-Member, sichere relative
Pfade und passende Datenhashes. Zielmetadaten werden nach chown/mode/Xattrs und
abschließend den ursprünglichen Nanosekundenzeiten angewandt, Verzeichnisse von
unten nach oben. Volle anschließende NOATIME-Inventur muss identisch sein.
Ein Fehler lässt höchstens das neue unvollständige Artefakt zur Callerklärung;
es gibt keinen automatischen Aufräum- oder Retirepfad.

Der optionale `reserve(nbytes)`-Callback läuft vor jedem tatsächlichen
unbuffered gepackten Schreibblock einschließlich gzip-Header/Footer. Nur genau
`True` lässt ihn zu. Ablehnung/Exception ist sticky; auch spätere Footerwrites
bleiben gesperrt. Rootcaller prüft den tatsächlichen Freiraum gegen
8GiB+64MiB+Writegröße+eigene kleine Reserve, besitzt Ownership/Locks/Sourcebounds
und verifiziert später Drive und zwei vollständige Restores. Ohne Callback
behauptet der Helfer keine Kapazitätssicherung. Es gibt keine atomare Reservierung
gegen fremde gleichzeitige Schreiber oder Stromausfall-Durabilitätsqualifikation.

`python3 -m unittest tools.test_restore_copy_roundtrip -v` bestand mit zwölf
Tests in 0,041s. Nur kleine TemporaryDirectory-Fixtures wurden tatsächlich
gepackt/restauriert. Positiv belegt: unterschiedliche atime/mtime, Dateinamen und
Binärbytes, leere Dateien/Dirs, UID/GID65534, user-Xattrs, echte POSIX-Access-/
Default-ACL und security.capability. Negativ: bestehende Ziele, Archiv im Source,
Link/FIFO/.git/Sparse, fehlende Hole-Unterstützung, Xattrfehler, Sourcechurn,
falscher Archivhash, Pfadtraversal, Payloadkorruption, Hardlink- und GNU-Sparse-
Member sowie verweigerter/fehlgeschlagener Reservecheck. Zugelassene Chunkgrößen
summieren sich exakt zur tatsächlichen Archivgröße einschließlich Footer.

Die erste Runde hatte sechs explizite API-fehlt-Fehler. Der Zusatz zur Reserve
hatte zwei echte Behavior-REDs: Der damalige Kern schrieb ohne Callbackprüfung
erfolgreich. Ein gesonderter Behavior-RED zeigte anfangs akzeptierten leeren
GNU-Sparse-Member; der Parser verlangt jetzt REGTYPE und `sparse is None`.
Diese historischen Logs bleiben privat unter
`.codex/evidence/restore-copy-roundtrip/`. Kein Gesamtprojekttest/Nativebuild,
keine historische Restorekopie, kein echtes Projektarchiv und keine Runtime
wurden angefasst. Dieser Stand ist Vorbereitung für Rootreview, keine
Erlaubnis zur Löschung und kein bereits extern verifiziertes Backup.
