# Geschlossene Build020-Belege und aktueller Flottenpunkt

Delta026 enthält den geschlossenen Build020-A4-FAIL, den eingefrorenen Controller, die experimentelle DLL und den Quellbundle bis `27761b0a424527d658282ada0ec5500325784091`. Die Archivkopie der Feueranalyse dient ausschließlich der nachträglichen Prüfung; sie qualifiziert den alten Lauf nicht neu. Noch laufende A1-Collectorarbeit ist nicht enthalten.

- Archiv: `delta026-build020-a4-closed-observer-audit.tar.gz`, 9554820 Bytes.
- SHA256: `84d689d8aa04f08c3a1512d9799c68227b963eb1b5964e8bd2d455117dbb44cf`.
- Separater Dateirestore: 860 reguläre Dateien / 76467630 Bytes, Hash sowie Modus/UID/GID geprüft. Kein nativer Gesamtarchiv-Restorestart.
- Bestehender privater Drive-Projektordner, Datei-ID `1YIwz7T_TL4O1wgFS4yTkAPISgF5CyCdU`: vollständiger Rückdownload mit identischer Größe und SHA256 bestanden.
- Freier Datenträger nach lokaler Rekonstruktion: 11204259840 Bytes; Mindestgrenze 8 GiB eingehalten.

Die frische Flottenprüfung um 09:51:48 UTC zeigt auf allen sechs Instanzen acht eigene Bots und keine ungeklärten Teilnehmer. Der native Respawnschutzwert ist jeweils 0; dies ist ausdrücklich kein Schadensnachweis für A1. Alle aktuellen Botprozesslogs haben 0 SYNCBAD, Syncdisconnects, Crash-, InvalidAction- und Joinfehler. Skulls hat im länger laufenden Serverlog weiterhin die bereits anhand des identischen Vorrollout-Prefix belegten historischen 11 SYNCBAD und einen Disconnect; diese sind keine neu nachgewiesene Build018-Regression.

Build018 bleibt auf allen Instanzen live. Dev und Red Station laufen mit Hard2; die übrigen vier nach dem dokumentierten Yodeller-FAIL weiter mit Serious3. A ist unvollständig, B unimplementiert. Es läuft kein neuer nativer Labtest und keine automatische Flottenänderung.
