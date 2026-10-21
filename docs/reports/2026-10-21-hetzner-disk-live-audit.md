# Hetzner 21.10.2026 – Live- und Speicherinventur (read-only)

## Umfang und Zeitpunkt
Unabhängige Prüfung auf autorisiertem RDC-Gerät `ubuntu-4gb-nbg1-2`, 21.10.2026 ab 14:06 UTC. Nur Leseoperationen; weder Spielprozess, systemd-Dienst noch Originalbinaries/Installationen geändert. Externe GameSpy-Queries sowie `ps`, `ss`, `df`, `du`, `findmnt`, `lsof`, Manifest-Hashprüfung.

## Verifizierter Produktionsstand
- PR #45 merged, `main=fdfc46eae8ba5557af427c1b36fc91b0d95aec37`.
- `CURRENT_PUBLIC.json` zeigt `eight-115115-z44oq5ua`, Build04 DLL SHA256 `7fc94a39c3f5d9516f262d9e4d04a5cf38e6eb5ae3482976c32c952a99d30835`.
- Lebende Linux-PIDs zum Zeitpunkt der Prüfung: Server124818, BotA124882, BotB124950; CWDs liegen in `/srv/tse-integration-public-20261021/eight-115115-z44oq5ua`. Laufzeit >2h20m.
- Spiel/Query-Ports `25600` und `25601` belegt durch laufende öffentliche Flotte. Zwei aktuelle GameSpy-UDP-Statusantworten auf `91.99.75.33:25601` mit `numplayers=8`, `maxplayers=16`, Yodeller, Fragmatch; exakte acht profilierte BOT-Namen vorhanden, `problems=[]`.
- Sechs Live-Overlay-Mounts: `server`, `prefix-server`, `botA`, `prefix-botA`, `botB`, `prefix-botB` im Laufverzeichnis. **Alle schützen, nicht unmounten.**
- `nr_throttled=0` im öffentlichen cgroup-Snapshot; dies ist keine 24/7-Lastaussage.

## Disk-/Backupstand
| Position | Beobachtung |
|---|---:|
| Rootfilesystem | 38 GiB nominal |
| Frei | 1,828,040,704 Bytes, ca. 1.7 GiB |
| Auslastung | 96 % |
| RAM verfügbar | ca. 2472 MiB |
| `/srv` | ca. 28 GB |
| `/srv/tse-wine-runtime-20261020` | ca. 20 GB |
| `/srv/tse-msvc-20261021` | ca. 2.9 GB |
| `/srv/tse-cpu-opt-candidates-20261021` | ca. 2.2 GB |
| `/srv/tse-build-wine-20261021` | ca. 1.3 GB |

- Große historische Wine-Kopien: `scale-staging-20261020` ~4.4G, `yodeller-20261020-0925` ~3.8G, `fortress-20261020-0920` ~3.2G, `onebot-20261020-0905` ~3.2G. Keine dieser vier liegt auf dem aktuell verifizierten Live-Overlay-Mountpfad; **das beweist nicht**, dass die Verzeichnisse für weitere Reproduktion/Recovery verzichtbar sind.
- Die ursprüngliche `public-eight-20261020-2140`-Vorlage sowie `install/vanilla` werden im derzeitigen öffentlichen Start-Runbook ausdrücklich referenziert: **nicht löschen oder verschieben**.
- Historische Datei `yodeller-20261020-0925/bot/SeriousSam.log` ca. 0.5 GiB; `lsof` fand beim Snapshot keinen offenen Dateideskriptor. Keine Änderung/Kompression/Entfernung erfolgte.
- Die laufenden aktuellen Bot-Logs waren jeweils nur etwa 4.3–4.8 MB; Logrotation bleibt dennoch unqualifiziert.
- Rückfallarchiv `/srv/tse-public-backup-20261021/previous-runtime.tar`: 10,823,680 Bytes; frisch gemessener SHA256 entspricht `manifest.json.archive_sha256`. Manifest status `PASS_BYTE_FOR_BYTE_RESTORE`, 415 Dateien als byteidentisch restauriert dokumentiert. Dieses Archiv ebenfalls **nicht entfernen**.

## Sicherheitsfazit und Arbeitsstand
**P0:** Ein früheres Vollkopieren einer Retail/Wine-Installation ist bei nur 1.8GB freiem Platz nicht vertretbar. Kein zusätzlicher Server- oder 16-Bot-Lasttest auf dem aktuellen Speicherstand. Schutz der laufenden öffentlichen Flotte hat Vorrang.

Es wurde kein dedicated Systemd-Autostart für TSE/Wine/Bots in `systemctl list-unit-files` gefunden. Die laufenden Prozesse haben ParentPID1 und sind nicht gleichbedeutend mit getesteter Neustart-/Reboot-Automatik.

**Nächster Schritt:** Für jede historische Kopie tatsächliche Skript-/Recovery-Referenzen und Hashes bestimmen, Archiv-/Restoreprobe mit eigenem Fixture, erst danach selektive sichere Archivierung/Kompression und optionales kontrolliertes Freigeben. Ziel `df -B1 /` >=8GiB freie Bytes ohne geänderten Originalbestand oder Produktionsunterbrechung. Bei fehlender gefahrloser Möglichkeit: `BLOCKED_NEEDS_STORAGE`.

Nach Platzreserve: disk-/PID-/CWD-fail-closed Healthchecks und isolierter Reboot-Supervisor; erst danach zwei getrennte Acht-Bot-Server mit humanen Plätzen und echter Stundenabnahme.

**Nicht erfolgt:** keine Dateien gelöscht, keine historischen Logs komprimiert, kein Service eingerichtet, kein Testserver/Bot zusätzlich gestartet, keine Laufzeitprozesse beendet, kein neuer Build.
