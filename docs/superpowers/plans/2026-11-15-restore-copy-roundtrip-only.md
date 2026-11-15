# Historische Restorekopie: reine reversible Verpackungsvorbereitung

Owner a4_diagnosis, eigener Branch. Nur neue helper/test/plan/report/claim-Dateien.
Keine Original-Restorekopie lesen, kein echtes Archiv oder Target erstellen,
keine Runtime/Prozess-/Cgroup-/Signal-/Driveoperation, keine Löschfunktion.
Tests verwenden ausschließlich frische TemporaryDirectory-Fixtures.

Vorhandene Roothelfer wurden gelesen, nicht ausgeführt. record/apply bewahren
weder atime noch xattrs (apply setzt atime=mtime); alte Archive materialisieren
Symlinks bewusst nicht und die Skripte enthalten Prozessscan/Löschen. Das reicht
für diesen neuen Vertrag nicht. Wiederverwendet wird das kleine Muster
Manifest+Dateihash+metadatenanwenden+vollständigverifizieren, kein Retire-Code.

Neue kleine API inventory(exact_root), pack(exact_root,fresh_archive),
restore(archive,fresh_target,expected_archive_sha256). Rootcaller ist allein für
Ownership,4Locks, Sourcebounds,8GiB-Floor und doppelte externe Rücklesung zuständig.
Kein CLI/Defaultpfad/automatisches Ausführen.

Sourcewalk FD-gebunden und NOATIME auch fürDirs; nur regularFiles/Dirs,
keine Symlinks/Hardlinks/Specials/.git. Sparsefiles konservativ abweisen via
SEEK_HOLE (fehlende Unterstützung ebenfallsFAIL), nicht still verflachen.
Manifest speichert Dateien+Dirs UID/GID/mode/atime_ns/mtime_ns/alleXattrs opaque.
Capabilities/ACLs sind ebenso Xattrs; Lesen/Schreiben/Exaktvergleich muss gelingen,
sonstFAIL. chown→mode→xattrs→timestamps, beiDirs bottom-up. Keine ctime/inode-
Rekonstruktion behaupten. FrischesArchiv O_EXCL0600; Payload/hash/Manifest prüfen.
FrischesRestoreziel; manuelle sichere Pfade, keine tar.extractall. Fehler lassen
höchstens ein explizit unvollständiges frisches Artefakt, nie Erfolg oder Deletion.

TDD: Metadaten-/xattr-roundtrip (atime!=mtime), Link/Special/.git/Sparseveto,
Manipulation/Pfadangriff, fresh-only/keinSourceinside, Xattrfailclosed und
Sourcewalk-NOATIME. Nur Tmpfixtures, tatsächliche OS-Datei-/Tarrekonstruktion.

Zusatz nach Root-Kapazitätsbefund: optionaler reserve(nbytes)-Callback vor JEDEM
unbuffered tatsächlich gepackten Write (auch gzip Header/Footer). Caller prüft
realen Freiraum >= 8GiB+64MiB+Writegröße+eigene kleine Reserve. False/Exception
bleibt sticky, Footer darf danach nicht weiterschreiben. Ohne Callback behauptet
die reine API keine Freiraumsicherung. Kein festes niedrigeres Ersatzlimit.

Status: 12 gezielte Tmp-Fixturetests PASS (0,041s). Initial sechs explizite
API-fehlt-REDs; Reserve-BEHAVIOR-RED zwei Fehler (alter Kern schrieb unadmittiert),
danach GREEN; zusätzlicher GNU-Sparse-Member-BEHAVIOR-RED, danach strikt abgewiesen.
Positiver tatsächlicher ACL-/Capability-/andererOwner-Roundtrip belegt. Keine
Original-Restorekopie gelesen/gepackt/restauriert oder entfernt; Rootreview offen.
