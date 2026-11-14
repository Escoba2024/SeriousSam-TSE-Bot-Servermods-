# Tatsächlicher A1-Modulvergleichsfehler

Der einzelne passive Originalclient-NoFire-Versuch vom 14.11.2026, 13:31 UTC, bleibt **FAIL** vor jeder Gameplayeingabe. Die neue Fehlerquittung wurde wie geplant aus den bereits gelesenen Daten erzeugt; keine zusätzlichen Prozess-/Speicherreads und keine Akzeptanzausnahme.

Betroffen ist `Engine.dll` des eigenen Originalclients. Dateisignatur, Device/Inode, Basisadresse und SHA256 entsprechen dem gebundenen Original. Die vorherige Mappingzeile `600c0000–600fe000`, Rechte `r-xp`, Dateioffset `0` wurde durch drei Zeilen ersetzt:

| Bereich | Rechte | Dateioffset |
|---|---|---|
| 600c0000–600cd000 | r-xp | 0 |
| 600cd000–600ce000 | r-xp | d000 |
| 600ce000–600fe000 | r-xp | e000 |

Alle drei Zeilen zeigen dieselbe Datei und dasselbe Device/Inode. Die übrigen Modulzeilen sind unverändert. Die aufgeteilten Bereiche decken exakt dieselben Adressen mit denselben Rechten und Dateioffsets ab. Die bestehende Prüfung vergleicht jedoch rohe Zeilenlisten und verwirft bereits diese andere Aufteilung. Der Archivbefund belegt die Aufteilung; ihre konkrete interne Ursache ist damit nicht direkt gemessen.

Nächster Schritt ist eine unabhängige Diagnose und ein prospektiv überprüftes Design für exakte Bereichsgleichheit. Keine pauschale Ausnahme für Frida, kein neuer Basisstand nach Attach, keine Zulassung verschwundener Seiten oder geänderter Rechte/Dateioffsets/Identitäten. Vorherige FAILs bleiben FAIL.

Der Versuch erfasste sechs Tracerecords, aber null Gameplayeingaben; keine Gain-/ACK-/Schadensfreigabe. Vollständiger Originalbytevergleich, Script-Unload und Session-Detach wurden bestätigt. Anschließend alle drei Rollen regulär geschlossen, beide Displays und der eigene Worker beendet. Unabhängiger Rootrestore: 664 Dateien, acht erwartete Absenzen, drei Schlussloghashes und Eigentümer-/Modusmetadaten bestanden. Der Worker wurde erst nach Prozessende aufgeräumt; `sticky_failure=false` betrifft ausschließlich seinen RPC-Lifecycle und ändert den Gesamtstatus FAIL nicht.

Private Evidenz `/srv/tse-milestone-a-evidence-20261111/a1-mapping-failure-20261114-133108`; Ergebnis-SHA256 `d2755f6d65122a3f27dfee577c9539cb7a4224cb1ed6e46eb99209668ac5d239`. Die private Fehlerquittung enthält vollständige gebundene Mappingdaten und hat Modus 0600. Vier Hostmessungen mit CPUmaximum 64,159 %, mindestens 2.915.569.664 Bytes RAM und 9.361.510.400 Bytes Datenträger sind lediglich kurze Beobachtungen; kein Dauerbudgetnachweis.
