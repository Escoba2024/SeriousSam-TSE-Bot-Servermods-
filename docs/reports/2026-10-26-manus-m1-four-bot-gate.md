# ssam.ai – M1: Vier-Bot-Dauerabnahme

**Stand:** 26.10.2026, 06:58 Uhr deutscher Zeit (CET).
**Ergebnis:** `DURATION_RECEIPTS_ACCEPTED` für den Vier-Bot-Wiederholungslauf. **M1 und M1–M4 sind noch nicht vollständig abgenommen.**

## Verifizierte Ergebnisse

| Prüfkriterium | Ergebnis |
|---|---|
| Nativer Runner | `PASS_LIMITED_SESSION_LIFECYCLE` |
| Scope | `ISOLATED_NETNS_RETAIL_WINE` |
| Exakter GameMP-Kandidat | `7dc961c880e0ed68ead13ed4e8299a025be71e05619de36c437c756e964334bf` |
| Angeforderte Messzeit | 3.840 Sekunden |
| Ununterbrochene volle Population, formal geprüft | **3.762,066 Sekunden**, erforderlich: 3.600 |
| Original-Retail-Gegenstelle | Unveränderter, stationärer Vanilla-Observer vorhanden |
| Telemetrie | Alle vier Bots `ACTIVE_OK`, median 20 Hz, je über 3.600 Sekunden bestätigte Spielzeit |
| Vollständige Sync-Logprüfung | Alle erforderlichen Server-/Clientlogs vorhanden, keine Treffer für `SYNCBAD`, `Too many bad syncs` oder `CRC check failed` |
| Host-Guard | `FINISHED`, Exitcode 0, kein Guard-Fehler |
| Neue CPU-Drosselungsperioden | 0 |
| Host-CPU-Maximum in Guard-Proben | 75,730 % |
| Niedrigste verfügbare RAM-Reserve | 1.748,125 MiB |
| Niedrigste freie Disk-Reserve | 8,3976 GiB |
| Cleanup | Alle Bots geleert, keine Cleanup-Fehler, alle Mounts erfolgreich abgebaut; unabhängiger Prozess-/Mount-/cgroup-Abgleich sauber |
| Öffentliche Runtime | Weiterhin ausdrücklich deaktiviert; keine Veröffentlichung oder Aktivierung |

Die unveränderte, source-gepinnte Funktion `m1_duration_acceptance.evaluate_runtime` hat den Lauf direkt auf Hetzner aus seinen finalen Receipts bewertet. Sie hat außerdem die vorhandene Ein-Bot-Abnahme erneut bestätigt: 3.699,61 Sekunden kontinuierliche volle Population. Beide Ergebnisse enthalten `m1_complete=false`.

## Abgrenzung zum vorherigen fehlgeschlagenen Lauf

Der vorherige Vier-Bot-Lauf wurde bei ungefähr 3.463 Sekunden vom Host-Guard beendet. Die letzten drei CPU-Proben überschritten dessen unveränderte 85-%-Grenze. RAM und Disk lagen zu diesem Zeitpunkt oberhalb der Mindestreserve. Die unmittelbare Abbruchbedingung ist belegt; welcher Prozess die damalige Mehrlast verursachte, ist nicht eindeutig attribuiert.

Der Wiederholungslauf verwendet dieselbe DLL und dieselben gepinnten Harness-Quellen. Es wurde **kein Bot-/Engine-Fix vorgenommen und kein Schutz-Gate abgeschwächt**. Sein Erfolg beweist nicht die Ursache oder endgültige Behebung historischer Cecil-P1-Sync-Fehler.

## Incident beim vorbereitenden Teststart

Ein fehlerhafter eigener Shell-Wrapper schrieb seine PID versehentlich in `tools/qualify_bot_sessions.py` des Cecil-Guard-Worktrees. Dadurch waren nachfolgende Startversuche lautlos beendet, ohne eine native Runtime oder einen neuen Evidence-Root anzulegen. Ein Exitcode 0 dieser Versuche war ausdrücklich kein Test-PASS.

Die beschädigte Datei wurde privat als Incident-Artefakt gesichert. Danach wurde ausschließlich diese Datei aus dem vorhandenen Cecil-Guard-HEAD `a5d93e71b4e7ff38fb4c2ce513df2cef95c086d6` bytegleich wiederhergestellt; erwarteter und erneut verifizierter SHA256:

`a6cc7b2205d3243ec932123d71293454880ab15526e1a63192cb0bba96859034`

Parser-Smoke und der anschließend tatsächlich gestartete vollständige native Wiederholungslauf bestätigen die Wiederherstellung. Die ursprüngliche ACL wurde ebenfalls wiederhergestellt. Qualifizierte DLLs, historische Testbelege und öffentliche Gameserver wurden durch den Incident nicht überschrieben.

## Nächste Schritte

1. Privaten Acht-Bot-Lauf mit unverändertem Kandidaten, Source-Pins und Schutz-Gates durchführen: geplantes Messfenster 7.680 Sekunden, erforderliche kontinuierliche volle Population mindestens 7.200 Sekunden.
2. Nur bei formal akzeptierter kompletter 1/4/8-Matrix die kandidatengebundenen Client- und Server-Recovery-Prüfungen starten.
3. Danach M1 gegen Masterplan und tatsächliche native Belege unabhängig abschließend prüfen. Historische Sync-Ursache und Einschränkungen explizit ausweisen.
4. M2 Combat, M3 Navigation und M4 Sessions erst nach bestandenem M1-Gate in die native Feature-Abnahme übernehmen. Offline-Source-Reviews dürfen parallel stattfinden, ohne den Hetzner-Test zu belasten.

## Belegidentität

- Eigenständiger Entwicklungszweig: `agent/manus/20261026-m1-m4-lead`, Basis `8a620c71507fc54ff81c9e1579855a9e29e65818`.
- Privater Lauf: `tse-session-qualification-master-m1-four-hour-r2-20261026`.
- Abnahmelogik SHA256: `10b3309b0d7fbac04375cd3ab1a8391b9dcf06590de9f799520b2a012a39b1e2`.
- Bounded Receipt Reader SHA256: `c159917c0ae6bbcd6e4db0b5437f74686b7d518687246816e5ff0743c139dc7e`.
- Private Rohlogs, Spieleridentitäten, Retail-Binaries und Spieldaten bleiben auf Hetzner und werden nicht mit diesem Bericht veröffentlicht.

## Fortsetzung – 26.10.2026, 07:05 Uhr CET

Der Acht-Bot-Lauf ist **noch nicht gestartet**. Ein unabhängiges Review der neuen Fortschritts-/Startsteuerung identifizierte Risiken bei Source-Pins, Abbruch/Cleanup, maximaler Laufzeit und veralteten Guard-/Result-Receipts. Die Steuerung wird vor ihrem Einsatz in getrennten lokalen Dateien abgesichert und portabel getestet. Der gepinnte ursprüngliche Session-Runner wird dafür nicht verändert; die vorhandenen Ein-/Vier-Bot-Belege bleiben erhalten.

Die Recovery-Matrixprüfung akzeptierte bisher ausschließlich den ursprünglichen Vier-Bot-Root, dessen Lauf fehlgeschlagen war. Eine eng begrenzte Änderung im eigenen Entwicklungs-Worktree ergänzt nun genau den formal akzeptierten `four-hour-r2`-Root. Vier neue Regressionstests reproduzierten die fehlende Zulassung zunächst RED und bestanden nach der Korrektur GREEN. Zusammen mit den vorhandenen Recovery-Gate-Tests sind **21/21 Tests sowohl lokal als auch auf Hetzner bestanden**. Andere Retry-Namen, falsche Kandidaten, verkürzte Dauer und unvollständige/gesperrte Matrizen bleiben abgewiesen. Direkte native Receipt-Revalidierung bleibt verpflichtend. Das kanonische Matrix-Statusfile bleibt unverändert `BLOCKED`; kein Recovery-Test wurde gestartet.

Unabhängige Offline-Reviews haben konkrete M2-/M3-Source- und Testlücken identifiziert. Sie wurden nur in lokalen Kopien ausgeführt und sind keine Feature-Integration oder native Abnahme. Die belastbare native Integration muss nach M1 auf dem tatsächlichen gepinnten Buildquellstand aufsetzen; ein historischer Release-Ordner ist nicht automatisch identisch mit dem aktuellen Cecil-/Human-AI-Kandidaten.
