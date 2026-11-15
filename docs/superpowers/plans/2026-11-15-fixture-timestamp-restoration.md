# Fixture-Restoration: Zeitstempel nachweisbar erhalten

Root-Claim: neue tools/file_transaction_timestamp_patch.py,
tools/test_file_transaction_timestamp_patch.py und zugehöriger Bericht/Plan.
Keine Überschneidung mit A1-Worker oder029-Basiscontroller.

Befund: Der unveränderte FileTransaction-Parent6fd1825b… speichert nur
Hash/UID/GID/Mode. Backup und Restore verwenden write_bytes; frühere Berichte
beweisen keine erhaltenen atime/mtime. Aktuelle640Fixturedateien haben keine
Extendedattrs. Historische Originalzeiten lassen sich daraus nicht rekonstruieren.

1. Tatsächliche alte Klasse mit realen temporären Dateien und absichtlich alten
   nanosekundengenauen Zeiten ausführen. Fehlenden Zeitbeleg als RED erhalten.
2. Exakte reine Quelltransformation: atime_ns/mtime_ns aus bestehendem stat vor
   Snapshotread speichern; nach vollständiger ursprünglicher Hash-/Rechteprüfung
   bei Restore beide Zeiten setzen und explizit erneut stat-prüfen. Keine Änderung
   von Quieszenz, Quellen, Dateilisten, Fehlerfortsetzung oder bisherigen Guards.
3. Gegenfälle: mehrere Dateien, neue/gelöschte Dateien, kaputter Backuphash,
   Zeitsetterfehler mit unabhängiger weiterer Restoration, ganze Quellinverse.
4. Engen unabhängigen Review; neue deaktivierte Forks der fertigen029/A1-Pakete.
   Alte Pakete und FAILs bleiben unangetastet. Root prüft künftige Fixturehashes
   mit O_NOATIME, damit die unabhängige Prüfung die restaurierte atime erhält.
   Vollständige Pins/Backup vor neuer Nativeausführung.

Zwischenstand: reale Altquelllücke reproduziert; zwei exakte Sourcefragmente,
8Tests0,029sPASS. Unabhängiger Review und beide deaktivierten Forks ausstehend.
