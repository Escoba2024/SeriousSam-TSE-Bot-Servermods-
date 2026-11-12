# Delta020 – enges Re-Review der zwei Sicherheitskorrekturen

**Ergebnis: READY, 0 Critical / 0 Important für die unten gepinnte Revision.** Beide ursprünglichen Befunde sind im tatsächlichen Hauptskript geschlossen. Der ursprüngliche Bericht REVIEW.md bleibt unverändert erhalten.

## 1. Quelldatei zwischen Hash und Archivlesen

Der Helper öffnet reguläre Quellen mit O_NOFOLLOW und prüft Pfad und geöffneten FD anhand von Device, Inode, Größe, Typ/Modus, UID/GID, mtime_ns und ctime_ns. Diese Prüfungen stehen vor und nach dem initialen Hashlesen und vor und nach tar.addfile. Das Hashlesen ist auf die bekannte Dateigröße und 1-MiB-Chunks begrenzt; ein angehängtes Byte wird ebenfalls abgewiesen. Symlinks behalten getrennte Typ-/Zielprüfungen.

Das Hauptskript verwendet tatsächlich snapshot_record und archive_file und prüft sämtliche aufgenommenen Quellen nochmals nach Archivierung und nach dem vollständigen Restore. HEAD, Git-Refs und sauberes Arbeitsverzeichnis werden im Archivablauf erneut geprüft. Damit kann der zuvor reproduzierte unbemerkte Präfix-Export nicht mehr als erfolgreicher unveränderter Snapshot durchlaufen.

## 2. Plattenreserve einschließlich Git-Bundle

ReserveWriter prüft vor jedem Schreibaufruf den benötigten Platz plus Allokationsblock sowie nach dem Schreiben die Reserve. Die Grenze beträgt 8 GiB plus 16 MiB Marge. Er ist an allen wesentlichen Datenpfaden angeschlossen: tatsächlicher Git-Bundle-stdout, gzip-Dateiobjekt, entpackte Restore-Dateien und exklusiv neu erzeugtes Abschlussreceipt.

Vor Archivierung wird ein konservativer Speicherbedarf für Archiv UND vollständigen separaten Restore verlangt; vor Restore wird der Restbedarf erneut geprüft. Elternverzeichnisse erhalten eine eigene Kapazitätsprüfung. Das Hauptskript begrenzt die angenommene Allokationsblockgröße mit statvfs; der Helper begrenzt die Pfadlänge für seinen Metadaten-Overhead. Bundle-Fehler brechen ab und beenden den eigenen Git-Prozess. Es bleibt bei den vorgegebenen ruhenden Schreibern und Roots externer CPUQuota25%-Startbedingung.

## Nachweise gelesen und geprüft

- Tatsächliche alte Archiv-AST-Schleife: zwei echte Assertion-Fehler für Append nach Indexaufnahme und Append während Archivlesen, Exit 1.
- Neue Testquelle und kompletter GREEN-Log: 9/9 erfolgreich, 0,037 s. Die Fälle prüfen außerdem Dateiaustausch, Symlinkwechsel, Metadatenänderung, unveränderte Datei, Reserve vor Write, Kapazitätsgrenze und ein echtes separat verifiziertes temporäres Git-Bundle.
- Helper, Hauptskript, Diff, Tests und beide Logs stimmen nach Rekonstruktion des terminalen LF mit den vorgegebenen SHA-256-Pins überein.
- Kein eigener Testprozess, kein Projektarchiv und kein nativer Lauf wurde gestartet. Der bestehende Testnachweis wurde geprüft, nicht als eigener Lauf ausgegeben.
- Separater Restore mit exklusiver Dateianlage, Größenprüfung, Streaming- und Reread-Hash sowie Mode/UID/GID/mtime-Verifikation bleibt erhalten. Symlinks werden weiter nur indexiert; Hardlinks werden als reguläre Einzelkopien archiviert.
- native_launch_from_restore=false und drive_uploaded=false bleiben unverändert. Das Review ist keine Behauptung einer bereits erfolgreichen Sicherung, nativen Wiederherstellung oder eines Drive-Roundtrips.

## Gepinnte Revision

| Bestandteil | SHA-256 |
|---|---|
| backup020_safety.py | e1de9664e26d5fe21b47ebca43a3b8c272c1eb682d2dbb6956ced2d6d4265195 |
| backup-completion020.py | caa50a75d7bb19c25b82718034f9a84e2d1e0dfe8834cb870150c74d62a9be1c |
| backup020-safety-correction.diff | 15c4407ed472a6de728e4f000209b7b29973432e5c3ef6ee7bb83c29d4842fdb |
| test_backup020_safety.py | d0738daa27e1dda8449d5a874909812b62e17bc84a7ac83753e7f22ac1925f3b |
| backup020-safety-red.log | 96d250ded0fbd35600d46e916f9d23ef5171f31fbb964ef6538dfeea5c80b837 |
| backup020-safety-green.log | a8d13f732f58679ad11bf4efd9b90667d4803bd14c4d0086df9496b91733e682 |

Die Dateien liegen unter /srv/tse-milestone-a-continuation-evidence-20261112. Exakte Einbaustellen stehen in rereview-result.json. REVIEW.md mit SHA 4c0b42acd78d547e132097da00aab6b225997efc2c34988043410df52a4d1b53 bleibt der unveränderte ursprüngliche 0-Critical/2-Important-Befund.

Root kann nach endgültiger Scope-Aktivierung und seinen bereits festgelegten Voraussetzungen fortfahren: abgeschlossener V3-Lauf, abgeschlossene Reviews, alle Writer idle, sauberer gepinnter Root-HEAD, Runtime-Lock/Quieszenz sowie bestätigte sechs Runtimeidentitäten. Dieses Re-Review fügt keine neue Untersuchungsachse oder Runtime-Freigabe hinzu. Worker anschließend idle.
