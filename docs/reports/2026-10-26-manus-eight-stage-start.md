# ssam.ai – Start der privaten Acht-Bot-Dauerprüfung

**Stand:** 26.10.2026, 07:17 Uhr deutscher Zeit (CET).

## Belastbarer aktueller Status

Der private Acht-Bot-Dauerlauf wurde am **26.10.2026 um 07:16:27 Uhr CET** tatsächlich gestartet. Die direkt gestartete native Outer-Steuerung ist PID `449844`; die neue übergeordnete Prüfhülle überwacht sie identitätsgebunden. Ein frischer Host-Guard-Receipt bestätigt `MONITORING`. Beim ersten Startabgleich lag die volle Botpopulation noch nicht als finaler Receipt vor; weder acht gleichzeitig spielende Bots noch eine bestandene Dauerabnahme werden hier vorweggenommen.

- Native Scope: isolierter Netzwerknamespace mit Retail 1.07 unter Wine.
- DLL-Kandidat unverändert: `7dc961c880e0ed68ead13ed4e8299a025be71e05619de36c437c756e964334bf`.
- Geplantes Messfenster: **7.680 Sekunden / 128 Minuten**.
- Formale Mindestanforderung: **7.200 Sekunden / 120 Minuten ununterbrochen volle Population**.
- Originaler Session-Runner und seine fünf im Producer-Receipt gepinnten Quellen: unverändert.
- Öffentliche Runtime: bleibt deaktiviert; kein Deployment, Push oder öffentliche Veröffentlichung.
- Kanonischer Matrixstatus: bleibt `BLOCKED`, bis die tatsächlichen nativen Ergebnisse geprüft sind.

Das Messende ist vorläufig ungefähr **09:25–09:30 Uhr CET** zu erwarten. Die genaue Zeit wird erst aus dem tatsächlichen nativen Messstart berechnet; anschließendes Drain, Cleanup und die formale Auswertung sind zusätzlich erforderlich. Das ist keine Garantie eines erfolgreichen Ergebnisses oder eines Projektabschlusses.

## Welche Sicherungen vor dem Start umgesetzt wurden

Die neue Prüfhülle verwendet genau eine feste Outer-Invocation. Sie bietet keinen Parameter zur direkten Auswahl des internen `--inner`-Modus, eines anderen Kandidaten oder eines anderen Runtime-Pfades.

Alle Pin-Prüfungen werfen explizite Fehler und bleiben unter `python -O` wirksam. Zusätzlich zur unveränderten Producer-Inventur wird eine separate Stage-Policy und Input-Sidecar geprüft. Die Live-Abhängigkeitsprüfung identifizierte acht lokale Python-Module der ursprünglichen Qualifikation; einschließlich des eigenen PID-Helpers und `Phase1HumanAI.ini` sind **zehn zusätzliche Input-Pins** verbindlich. Die tatsächlichen Pfade des PID-Helpers und des zusätzlich importierten `gaming_names.py` wurden vor dem Start korrigiert. Historische Policy und Testbelege wurden nicht überschrieben.

Die Abnahmelogik wird vor ihrem Import gegen ihren Hash geprüft. Der native Python-Unterprozess wird ausdrücklich ohne aktivierte Optimierung gestartet, damit auch die Schutzprüfungen des unveränderten ursprünglichen Harness nicht durch ein geerbtes `PYTHONOPTIMIZE` entfallen.

Die übergeordnete Steuerung bindet ihren direkt gestarteten Prozess mit dem bestehenden PID-/Startgeneration-/pidfd-Helper. Bei einem eigenen Abbruch fordert sie über dessen pidfd `SIGINT` an, damit der ursprüngliche Outer-Runner seinen regulären Abort-/Cleanup-Pfad verwenden kann. Es werden keine fremden oder lediglich bei einer Inventur entdeckten PIDs signalisiert.

Startup, Messung, konfigurationsabhängiges Drain und konservative Cleanup-/Finalisierungsbudgets ergeben für die reale Konfiguration **9.124 Sekunden maximale Gesamtzeit**. Guard- und Result-Heartbeats werden nach der begrenzten Startphase auf Frische und Fortschritt geprüft. Die Drain-Gnade kann nicht durch stagnierende Messzeit beliebig verlängert werden. Bereits vom Producer begonnenes Fail-Cleanup wird nicht durch ein zweites Abbruchsignal gestört; ein final sichtbarer Receipt erhält nur ein eng begrenztes Prozessende-Fenster.

Nach Ende des direkt gestarteten Prozesses erfolgt eine unabhängige, ausschließlich lesende Inventur von cgroup, Prozessen und Mounts. Nicht beweisbar abgeschlossenes Cleanup führt zu einer persistenten `HOLD`-Datei und verhindert einen weiteren Start dieser Prüfhülle. Es gibt keinen automatischen Retry und keine automatische Promotion.

## Test- und Vorgängernachweise

**16/16 portable Regressionstests** der finalen Prüfhülle bestanden sowohl mit normalem Python als auch unter `python -O`, lokal und auf Hetzner. Sie verwenden temporäre Dateien und simulierte Prozesse; diese Ergebnisse sind keine native Retail-Abnahme.

Vor dem tatsächlichen Start wurde rein lesend auf Hetzner geprüft:

1. frischer Runtime-Pfad und keine bereits übernommenen Stage-Receipts;
2. vollständige zusätzliche Input-Pins, Konfigurations- und Manifest-Hashes;
3. unveränderte frühere Testbelege;
4. erneute formale Ein-/Vier-Bot-Dauerbewertung: jeweils `DURATION_RECEIPTS_ACCEPTED`;
5. freie Host-Ressourcen und keine bereits laufenden Retail-Spiel-/Qualifikationsprozesse.

Die separat umgesetzte Recovery-Root-Korrektur lässt ausschließlich den bereits formal akzeptierten `four-hour-r2`-Root zusätzlich zu. Sie ist mit **21/21 Regressionen** lokal und auf Hetzner bestanden und als lokaler Sicherungscommit `3e7e6a0316ae615a3c914bc2430072ed8b4671e8` im eigenen Zweig gesichert. Kandidat-, Dauer-, vollständige-Matrix- und direkte native Revalidierungsgates bleiben erhalten.

## Verbleibende Grenzen und nächste Schritte

Das ursprüngliche Harness hat für fremde direkte CLI-Aufrufer weiterhin einen internen `--inner`-Einstieg. Diese neue, feste Invocation erreicht ihn nicht direkt. Die ursprüngliche Outer-Quelle enthält außerdem weiterhin ihr eigenes 180-Sekunden-Warten auf einen abbrechenden Inner-Prozess. Die neue Prüfhülle kann nicht nachträglich das globale Lock eines bereits beendeten ursprünglichen Outer-Prozesses halten; sie hält jedoch ihre eigene Serialisierung durch die unabhängige Inventur und sperrt weitere eigene Starts bei ungeklärtem Restzustand. Diese Quellhärtungen bleiben getrennte Arbeiten, nicht heimlich geänderte Bedingungen dieser Dauerabnahme.

Nach dem Lauf werden vollständige Population/Zeit, Telemetrie, Sync-Logs, Guard, CPU-Drosselung, Artefaktidentität und Cleanup formal ausgewertet. **Nur bei tatsächlich akzeptierter kompletter Dauer-Matrix** folgt die kandidatengebundene Client-/Server-Recovery-Prüfung. M1 wird erst nach diesen Belegen und Abschlussreview abgenommen. M2 Combat, M3 Navigation und M4 Sessions bleiben bis dahin von einer nativen Feature-Promotion ausgeschlossen; ihre Offline-Reviews liegen vor.

## Source-Identität der neuen Steuerung

- `run_eight_duration_hardened.py`: SHA256 `05791333839b2d82cb69a235af75f0302c50e8556dad79ae1832e95eb488a1c3`.
- `test_eight_duration_hardened.py`: SHA256 `a0ea9648871dac7b6399806f5705f9b4cc0b258ba5d8f5e3a41515fb71509d2c`.
- separate private Stage-Policy: SHA256 `9e76b236c0dd92bd58cd48b5638eade95d8974a23dd81f1c24924f700fa0cdbd`.
- eigener Zweig: `agent/manus/20261026-m1-m4-lead`.

Private Rohlogs, Botidentitäten, Retail-Binaries, Spieldaten und SSH-Zugangsmaterial bleiben auf ihren autorisierten Geräten und werden nicht mit diesem Bericht veröffentlicht.

## Frischer Startabgleich – 07:18:06 Uhr CET

Der native Receipt bestätigt jetzt `MEASURING` mit 62,374 Sekunden gemessener Laufzeit. Aus Receipt-Zeitstempel und Laufzeit ergibt sich das voraussichtliche Messende **09:25:02 Uhr CET**. Die Bots befanden sich beim Abgleich noch in der gestaffelten Join-Phase; `peak_playing=3` ist noch keine volle Acht-Bot-Population. Der Host-Guard war frisch und `MONITORING` (zuletzt rund 52,7 % Host-CPU und 1.838 MiB verfügbare RAM-Reserve). Die endgültige Prüfung bleibt vom vollständigen Lauf, anschließenden Cleanup und den formalen Receipts abhängig.
