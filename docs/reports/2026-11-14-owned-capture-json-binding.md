# Capturebindung: belegter JSON-Typfehler

Status: **OFFLINE_FIX_ONLY**, keine native Capture-/Syncabnahme. Claim `a4_diagnosis`, isolierter Branch `codex/20261114-owned-capture-json-binding` ab Rootplan `f78a1fd`; Main allein integriert und verändert Runtime. Der frühere Reset-Worktree bleibt unverändert.

Der eigene Rootversuch `145119` scheiterte vor Release und vor tcpdump. Result `ae048d5fc51fa6bd564d7cf891a5681c16a644366bdb77b956394765e454fd75` bleibt FAIL; PCAP 0 Bytes, somit kein Syncbeleg. Root meldete alle vier Rollen normal geschlossen und unabhängigen Restore von 640 Dateien plus vier Schlusslogs/Metadaten/PIDs/Display bestanden. Keine neuen Laufzeitaktionen wurden für diese Fehlerbehebung durchgeführt.

`socket_rows` liefert `(Port, Inode)`-Tupel. `observe_roles` übernahm diese Tupel unverändert in `ports`. Der Parent schreibt seine Bindung als JSON; der frische Exec-Helfer liest daraus Listen von Listen und vergleicht sie mit erneut gelesenen Tupeln. Python bewertet gleiche Werte in Tupel und Liste als ungleich. Der bisherige Helpertest ersetzte den Leser vollständig durch einen Mock und prüfte diese echte Übergabe nicht.

Die einzige geänderte Runtimezeile stellt `ports` bereits an seiner Quelle als Listen von Listen dar. Parser, Reihenfolge und Werte bleiben erhalten; vollständiger Setupvergleich, PID-/Start-/CWD-/Cgroup-/NetNS-/FD-Guards und Capture-/Host-/Gameplaygrenzen bleiben unverändert. Es gibt keine Toleranz, Ausnahmeregel oder Neuübernahme der erwarteten Bindung.

Der neue Regressionstest führt den tatsächlichen `/proc`-FD-/UDP-Fixturleser, den exklusiven JSON-Writer und den unveränderten `owned_capture_exec.main()`-Vergleich aus. Vor der Korrektur wurde erst der Tupel-/Listenunterschied und danach der konkrete Helperfehler `roles changed before capture exec` beobachtet. Nach der Korrektur erreicht der Test den ausdrücklich gemockten Exec-Endpunkt. Geänderte Ports, Inodes, PID und Namespace scheitern weiterhin vor Exec und vor einer Ownerquittung. Es wird kein Prozess, Capture oder Namespace gestartet/verändert.

Gezielter Abschlussbefehl aus `tools/`:

```sh
python3 -m unittest test_owned_sync_capture test_prepare_owned_sync_capture test_analyze_retail_sync_pcap test_prepare_owned_capture_json_binding -v
```

**37/37 PASS, 0,438 s**: bisherige 35 Fälle, ein echter Reader-/JSON-/Helper-Grenztest und ein neuer Pakettest. Der Pakettest prüft die frische Ableitung vom unveränderten deaktivierten Autorenpaket, sämtliche Pins und exakt zwei geänderte vorhandene Dateien: Libraryzeile und Regressionstest. Der zusätzliche Builder bleibt ein Offlinewerkzeug außerhalb des Runtimepakets.

Neues deaktiviertes Paket: `/srv/tse-owned-sync018-json-binding-disabled-20261114`; Manifest `dbf38d5df34c33831342209f767fdf28bfac58b1561dc24ee26dde17466e9fb8`, 69 Runtime-/61 Source-/40 Pythonpins. Parentmanifest `4e0a565fde1f040c95dbea89932b6511d6671cee5aa01bf02053dc56fb2a8e35`. Alle drei Ausführungsgates bleiben `False`, alle Qualifikationsflags `False`. Alte Pakete, Freezes und fehlgeschlagene Nativebelege wurden nicht geändert.

Nächster Schritt: unabhängiger Quell-/Paketreview, neue Rootcopy, frischer exklusiver Preflight und gegebenenfalls genau ein ausdrücklicher Rootlauf. Capturefähigkeit, tatsächliche vollständige 600-Sekunden-Abdeckung und Syncvergleich bleiben offen; kein automatischer Retry und kein unbeaufsichtigter Auftrag laufen.
