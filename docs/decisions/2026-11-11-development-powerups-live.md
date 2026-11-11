# Development: selektive Power-ups live ausgerollt am 11.11.2026

Der Nutzer hat nach den isolierten Tests ausdrücklich angewiesen: „Starte neu egal ob human Player da ist und Rolle das aus“. Damit war die Unterbrechung des zusätzlich anwesenden Dev-Spielers für diesen Neustart genehmigt. Der vorherige Belegungsstopp ist für diesen Auftrag aufgehoben; die fünf Produktionsinstanzen bleiben geschützt.

Auf ausschließlich `91.99.75.33:25650`, Red Station, wurde die bereits isoliert geprüfte Server-GameMP-DLL `fe4a77bd1eae15a25cfeb67cf5dfdd6643cba59661f2ca3e99467a9fb15b06e0` installiert und `dev_bRemoveDamageAndInvisibility=1` gesetzt. Es gab keinen Rebuild. Beide Botprozesse verwenden weiterhin exakt Cecil048 `ec820d0461313c41fec2b477f57109310d3c71a77b4423955ac69f3807566530`.

Vorher wurden aktuelle Prozesse und Dateien inventarisiert, exklusive Flotten-/Runtime-Locks gehalten und Original-Server-DLL sowie Kartenkonfiguration separat gesichert. Beide eigenen Botprozesse wurden normal per PID-gebundener Fensterschließung beendet, danach Dedicated per SIGINT; kein Force-Fallback. Die drei neuen nativen Prozessidentitäten unterscheiden sich nachweisbar von den vorherigen. Der zusätzliche Spieler wurde durch den ausdrücklich genehmigten Serverneustart getrennt; menschliche Clientprozesse wurden nicht gesteuert.

Die tatsächliche geladene GameMP-DLL wurde für Server und beide Botprozesse anhand Pfad, Device/Inode und Datei-Hash geprüft. Alle acht Bots sind mit ihren Gaming-Namen RustyRailgun, Vortex, QuadFever, KleerIntent, UnReaL, SleepyShrapnel, ToxicWaste und xXx_D3MON_xXx verbunden; die Farbcodes bleiben in den Profilen erhalten. Alle 36 geschützten Profil-/NAV-Dateien sind bytegleich. Originale Engine-, Entities- und Dedicated-EXE sowie sämtliche geprüften Bot-Einstellungen bleiben erhalten.

Die echte Serverzählung für Red Station zeigt vor dem Filter Invisibility=1 und Damage=1, anschließend `removed=2` und beide Bestände 0. Andere Power-up-Typen sind auf dieser Karte nicht vorhanden. Die Auswahl anderer Typen wurde in den vorherigen portablen Tests geprüft; es wird kein zusätzlicher nativer Kartenfall behauptet.

Nach dem Wiederanlauf wurden **180,618427 Sekunden mit 179 gültigen Statusabfragen** beobachtet. Acht eigene Bots blieben verbunden; in den aktuellen Server-/Clientlogs wurden keine SYNCBAD-, Bad-Sync-Disconnect-, CRC-, Join- oder fatalen Laufzeitfehler gefunden. Alle fünf Produktionsinstanzen behielten ihre Prozessidentitäten und geprüften Binär-/Konfigurationspins. Das Ergebnis ist ein begrenzter Live-Rollout-Nachweis, `qualified=false`, keine native Windows-, Stunden-, Rotations- oder 24/7-Abnahme und keine vollständige Cecil048-Produktionsfreigabe.

Private Ergebnisdatei-SHA256: `3d9ce05638a5dce4572df9c5310d98b3fd3474afb5a413a23d5b4748cddcccdc`. Abschluss: 11.11.2026, 18:27:58 UTC. Rohlogs, Profile, Spielerinformationen und Binärdateien bleiben privat.

Der zusätzliche private Rollback-Stand `20261111T182403Z-cecil048-dev-powerup-server-delta` enthält alte und installierte Serverdateien, tatsächliches Kandidatenmanifest, isolierten Testbeleg und Rollout-Ergebnis. Alle inventarisierten Dateien wurden nach dem Kopieren vollständig nachgehasht. Die vollständige Cecil048-Sicherung, das Farbnamen-Delta und der zuvor vorbereitete Kandidatenstand bleiben erhalten. Ein tatsächlicher Restore ist weiterhin ungetestet.

[Isolierte Kompatibilitätsprüfung und Quell-Pins](../reports/2026-11-11-dev-selective-powerups.md) · [Gaming-Namen und ursprüngliche Recherche](2026-11-11-development-names-and-powerups.md)
