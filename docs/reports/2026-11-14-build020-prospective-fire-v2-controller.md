# Deaktivierter prospektiver A4-Feuerobserver V2

Status: **nur offline vorbereitet, kein nativer Start**. Kandidat bleibt exakt
Build020/DLL `094ec8edbedd5e63d8e4eb03fcce70518283b22440e5f80ba4c2482ff81fe6c0`.
Der alte Build020-Lauf bleibt FAIL. Root allein reviewed, friert ein, startet
und verändert die isolierte Runtime.

Neues Paket: `/srv/tse-a4-fire020-v2-controller-20261114`.
Manifest: `86662c479b4a0928ba140fc8437ac7ea8f8683a9145dc9e69204606aa316329f`.
Beide Runtimegates bleiben falsch. Eigener Dienstpräfix
`ssam-a4-fire020-v2-20261114`, Evidencepräfix `a4-fire020-v2-`.
Der private reproduzierbare Vorbereiter liegt unter
`/srv/tse-a4-fire-v2-prepare-20261114.py`; er verweigert ein vorhandenes Ziel.
Das aktuelle Paket darf erst nach gesondertem Root-Freeze gestartet werden.

Die vorhandene `adapter_policy.py` bleibt vollständig bytegleich. Der
[Launcher-Diff](milestone-a-20261114/build020-prospective-fire-v2-runtime.diff)
ergänzt einen reinen Policyimport, annotiert ausschließlich ohnehin akzeptierte
Originalserver-Inventarsamples mit Phase/PID-Start/Source-Logoffsets und übergibt
den bestehenden Abschlussbeleg an den neuen Feuerpolicy. Die native
Readerimplementierung, Inode-/Modul-/Hostpins, Sperren, Population, Samplingraten,
Roundbedingungen Serious3/120+120+120 Sekunden, 480-s-Cap, Ressourcen-,
Bewegungs-, Respawn-, Score-, Fehler- und Restoregates bleiben unverändert.

Der bestehende Ablauf leert `phase_rows` unmittelbar am alten Rundenende,
bevor der nächste frühe Reader scharf wird. Die frühen Samples wurden bereits
durch `PhaseInventory.add` gegen die tatsächliche neue Map und Prozessidentität
geprüft; ihre neue Annotation verwendet exakt `capture.epoch.log_offsets`.
Normale Samples verwenden die danach tatsächlich übernommenen `phase_offsets`.
Die spätere Neunspieler-Registry erhält denselben Schlüssel. V2 verwirft jede
abweichende Phase, PID-Startidentität, Originalhashes, Doppelreadkennzeichnung
oder Sourceepoch. Diese Annotation ersetzt keine geerbten Host-/Modulpins.

V2 entfernt ausschließlich die autoritative Verwendung des sekündlichen
`fire_action_rows`-Samplegates. Das Feld bleibt als Diagnose erhalten. Alle
anderen bisherigen fehlenden Aktivitätsbelege bleiben Fehler. Zusätzlich
verlangt V2 pro Slotphase tatsächlich Originalserver-FIRE/current-owned/ammo
mit Sourcecounterwachstum im eindeutig gebundenen Leben sowie tatsächlich
beobachteten Useful-Besitzübergang derselben Welt/Entity/Life. Keine EPS- oder
Aktivitätslockerung; die konservative vollständige printf-Rundungsprüfung des
separaten Archivaudits wird unverändert wiederverwendet. V2 setzt niemals
`qualified` oder `functional_pass` auf wahr und beweist weder Treffer noch Schaden.

Fokussierte Offlineprüfung: **87 Tests, null Fehler**, ausgeführt ausdrücklich
über neun benannte Module im neuen Paket. Darin enthalten: 65 geerbte Checks,
13 Archivauditfälle und neun neue V2-/Epochfälle. Der erste Entwurf hängte den
Wrapper an den Adapter an; dessen vorhandener Bytevergleich schlug einmal fehl.
Der Adapter wurde daraufhin vollständig unverändert übernommen, die Ergänzung
beschränkt sich auf den Launcher. Das erste deaktivierte Paket bleibt privat
als `tse-a4-fire020-v2-first-offline-fail-20261114` erhalten.

67 Runtimeabhängigkeiten und 75 Buildquell-/Overlaypins wurden frisch geprüft;
64 der65 geerbten Runtimeabhängigkeiten bleiben bytegleich, einzig der Launcher
ändert sich. Alle neun benannten Testmodule benötigen zusammen unter einer
Sekunde auf dem überprüften Host; keine breite Discovery oder Builds.

Ein separater [Offline-Replaybeleg](milestone-a-20261114/build020-prospective-fire-v2-offline-replay.json)
wendet V2 mit **ausdrücklich synthetisch nachgetragenen Epochannotationen** auf
die archivierten Samples an. Alle24 Slotphasen haben die stärkeren Beobachtungen;
das ändert den damaligen Controller, seine FAIL-Quittung oder die native
Qualifikation nicht. Der [Paketbeleg](milestone-a-20261114/build020-prospective-fire-v2-controller.json)
enthält konkrete Hashes und Testgrenzen.

Nächster Schritt: unabhängiger Root-Review der beiden neuen Policys, des
minimalen Launcherdiffs, der frühen/normalen Epochbindung und aller Pins.
Danach ausschließlich Root-Freeze, frischer Preflight und ein separat
bezeichneter prospektiver Lauf. Der terminale Build020-Watchdog bleibt bis zu
einem echten passenden nativen Ereignis ohne positiven Laufzeitnachweis.
