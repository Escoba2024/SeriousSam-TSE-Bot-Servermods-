# Speicherreserve durch geprüfte eigene Restore-Testkopien

Am15.11.2026 wurden ausschließlich sechs alte eigene Rekonstruktionen der
Delta011/012/013/015/016/017-Sicherungen entfernt. Originalarchive, lokale frühere
Drive-Rücklesedateien, Drivekopien, Mischrollback051, qualifizierte DLLs und
laufende oder fremde Ressourcen wurden erhalten. Keine Produktivdatei wurde
verändert.

Vor jeder Entfernung prüfte Root exklusiv die vier technischen Sperren,
fehlende Prozess-CWD-/FD-/Mappingverwendung, sichere relative Pfade, fehlende
externe Hardlinks, beide vollständigen Archivhashes sowie jede Datei gegen
Archivindex, vollständigen Tar-Payload und aktuelle Kopie. Ein neues privates
Manifest erhält exakt die tatsächlich vorhandenen Metadaten dieser entbehrlichen
Testkopie; es ergänzt keine angeblich historisch geprüften Originalmetadaten.

Anschließend wurden alle sechs Kopien aus den unveränderten Archiven wirklich
neu rekonstruiert. **31.321 reguläre Dateien mit insgesamt2.252.459.190Bytes**
wurden vollständig zurückgelesen und auf SHA256, UID, GID, Modus und Nanosekunden-
mtime geprüft. Vierzehn historische Symlinkeinträge blieben indiziert, ohne
absolute Wine-Verknüpfungen zu materialisieren. Erst nach bestandenem Test wurde
jeweils diese neue temporäre Kopie entfernt.

Der freie Speicher betrug danach11.000.229.888Bytes; die achtGiB-Untergrenze und
interne Reserve wurden während der tatsächlichen Rekonstruktionen eingehalten.
Dies schafft ungefähr2,36GB physische Reserve. Laufende Logs verbrauchen weiter
Platz; der Wert ist eine Momentaufnahme, keine dauerhafte Budgetgarantie.

Private Belege im Root-Belegordner:
`six-retired-restore-copies-summary.json`, sechs
`retired-deltaNNN-full-reconstruction-receipt.json`, sechs exakte
`retired-deltaNNN-tempcopy-metadata.json` und ausführbare
`retire-and-test-restore-deltaNNN-copy.py`.
Jeder Helfer kann mit `--restore-only` eine neue Testkopie aus erhaltenem Archiv
und Metadatenoverlay rekonstruieren; er überschreibt keine vorhandenen Pfade.
Die Originalarchivnamen und konkreten Drive-IDs stehen in den privaten Manifesten.

Dies ist eine vollständige Dateirekonstruktionsprüfung der entbehrlichen Kopien,
kein Start einer gesamten Retail-Runtime aus einem Restore und kein A5-Pass.
