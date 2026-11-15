# Neue Fixture-Zeitstempelrestoration, alte Grenzen bleiben sichtbar

Der tatsächliche alte Transactionparent hat SHA256
`6fd1825b1bfda8713b8669f01ea3ab4cb5747c2084c338575fb0b0dbbf5c5dfb`.
Snapshotdateien enthalten nur Backupreferenz, Hash, UID, GID und Mode.
write_bytes erzeugt neue Backup-/Restoretimestamps; alte Originalzeiten wurden
nicht gespeichert. Ein realer temporärer Dateilauf mit absichtlich alten Zeiten
reproduziert restored=true bei verändertem mtime. Alte Hash-/Rechtebelege
bleiben erhalten, werden aber ausdrücklich nicht um Zeitnachweise erweitert.
Die aktuelle schreibfreie Prüfung fand640Fixturedateien ohne Extendedattrs.

Die neue reine Source-Transformation ergänzt genau zwei Fragmente: vorhandenes
stat liefert atime_ns/mtime_ns VOR dem Snapshotread. Nach sämtlichen bisherigen
Restoredaten-/Rechteprüfungen setzt os.utime beide gespeicherten Zeiten; ein
anschließendes stat muss beide exakt bestätigen. Fehlende Rechte, fehlgeschlagene
Zeitsetzung und sogar lautlos falsch gesetzte Zeiten verhindern den Pass.
Unabhängige restliche Dateien werden weiterhin restauriert; Absenz-/Treecleanup,
Quieszenz, Symlink-/Hash-/Eigentümer-/Modeguards bleiben bytegleich.
Die vollständige inverse Quelle muss exakt den Parenthash ergeben.

Echter fehlendes-Modul-RED bei gleichzeitig reproduzierter Altquelllücke;
7Tests0,024s GREEN; mit unabhängigem O_NOATIME-Hashread und Symlinkgegenfall
**8Tests0,029s PASS**. Hashprüfung mit O_NOATIME verhindert, dass die unabhängige
Prüfung selbst die frisch restaurierte atime verändert. Kein stiller Fallback
auf einen gewöhnlichen Read. Tatsächliche temporäre Dateitests prüfen beide
Nanosekundenwerte, alten Fehler, kaputtes Backup, Zeitsetterfehler mit weiterem
Restore, falsche Zeitsetzung, Absenz, Sourceinverse und unabhängigen Read.

Keine alten gefrorenen Pakete geändert, keine Native- oder Liveausführung.
Vor einem neuen029/A1-Lauf: unabhängiger Review, gezielter deaktivierter
Metadatenfork und komplette Source-/Dependencyprüfung, Rootfreeze/Vollsicherung.
Kein rückwirkender Zeitstempel-/vollständiger Metadatenpass für alte Versuche.
