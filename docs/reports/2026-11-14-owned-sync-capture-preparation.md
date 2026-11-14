# Deaktivierter eigener Build018-Syncpaketversuch

Status: **OFFLINE_PREPARATION_ONLY**, keine Runtime-, Capture-, WAN- oder Stabilitätsabnahme. Claim: `a4_diagnosis`, Branch `codex/20261114-owned-sync-pcap`; ausschließlich diese neuen Capture-/Builder-/Testdateien. Main allein integriert, friert ein und startet. Der unterbrochene Reset-Worktree bleibt unverändert erhalten.

## Herkunft und fester Versuch

Plan: [Owned-Sync-Packet-Capture](../superpowers/plans/2026-11-14-owned-sync-packet-capture.md), Root `cb35182`. Parent ist der geprüfte Hard-Singlemap-Controller mit geordneten Memorybeobachtungen, Manifest `56f4c319551459d5c7a201d82ee75f03641232ec33d29eca7e2f86b71390fb65`. Ein neuer deaktivierter Fork verwendet ausdrücklich Build018: Quellcommit `1802fb3f0720b53feb032abfe2c2a83407bfea6e`, DLL `6db89204e33dc7d76ecdfed68055d2b75bde4950475793a57101fd0cefcb8e4a`, Buildmanifest `f4212443317b58b04808bd42d084e6a3286e458af2c0dbcfb276aa3bca931c2e`.

Genau Yodeller, Hard2, Diagnostik0, 600 Sekunden, acht eigene Bots und ein stationärer unveränderter Originalclient. Parent-Host-/Join-/Pause-/Dateitransaktions-/Rollenclose-/Aktivitäts-/Fehlergates bleiben erhalten. Fehlende Aktivität bleibt FAIL. V2/V3-/Hard-/Canonical-/Host-/Transaction-Dateien sind bytegleich. AST-Vergleich bestätigt unveränderte Inventory-, Query-, Probe-, Pauseprobe-, Sleep- und Pause-Inputaufrufe des Gameplaycontrollers. Keine Frida-Hooks, neuen Gameplayinputs, zusätzlichen Inventoryreads oder Netzwerkregeländerungen.

## Capture und Grenzen

Vor dem Release der fertigen Neuner-Pausenbarriere werden für alle vier eigenen Hauptprozesse PID/Start, Rollen-CWD, Kommando, systemd-Cgroup und gemeinsame private NetNS gebunden. Clientports stammen ausschließlich aus dem Schnitt ihrer tatsächlichen Socket-FDinodes mit der jeweiligen UDP-Tabelle. Serverports sind exakt 27850/27851; jeder Client muss genau einen exklusiven IPv4-Port besitzen. Mehrdeutigkeit, Wiederverwendung, Namespacewechsel, IPv6 und Hostnamespace scheitern hart. Während der bisherigen Modulprüfung wird diese Bindung erneut geprüft; deren zusätzliche Hostkosten sind nativ noch offen.

Ein frischer Exec-Helfer schreibt vor `nsenter` eine exklusive private PID-/Start-/Gruppenquittung und setzt RLIMIT_FSIZE. GNU `timeout` begrenzt seinen eigenen neuen Prozessgruppenbaum unabhängig auf 640 Sekunden, tcpdump auf 250000 Pakete, die Datei auf 64 MiB. Capture ausschließlich private Server-NetNS, `lo`, UDP27850; keine Rotation. Startbereit erst nach exakt gebundenem tcpdump-Kommando/Namespace, gültigem PCAP-Header und Listeningmeldung innerhalb fünf Sekunden im pausierten Zustand. Diese tatsächliche Exec-/NetNS-/CAP-Fähigkeit ist noch nicht nativ qualifiziert.

Reguläres SIGINT und höchstens zehn Sekunden Wait geschehen vor irgendeinem Rollenclose. Bei Timeout folgen ausschließlich im eindeutig eigenen Capturebaum TERM/KILL mit je drei Sekunden Wait; dies bleibt FAIL. Ein teilweise erfolgreicher Popen behält sofort seinen Handle. Vorzeitig beendete Supervisoren überspringen die Prüfung eines dokumentierten noch laufenden eigenen Capturekindes nicht. Cleanupfehler bleiben sticky; Roh-PCAP, stderr, Hash, Rollenbindung und drei Vergleiche werden unabhängig voneinander soweit möglich erhalten. Anschließend läuft der geerbte normale Rollen-/Datei-Cleanup weiter. Keine Spielrolle wird forciert beendet.

Der vorhandene unveränderte Auditor vergleicht explizit A↔B, A↔Original und B↔Original. Fehlende Paare, Drops, unsupported Transport oder Widersprüche erlauben keinen Protokoll-PASS. Ergebnisse betreffen nur die beobachteten Retail-Synccheckpakete und gegebenenfalls `first_differing_SAMPLED_synccheck`; weder erster 20-Hz-Simulationstick noch vollständige Simulationsgleichheit sind belegt. Der vorangehende Joinhandshake ist nicht erfasst. Keine Folgerung über öffentliche/externe Teilnehmer oder die Incidentursache. Rawpakete, Adressen und Retaildateien bleiben privat.

## Offlineprüfung und Handoff

RED wurde vor Implementierung an fehlenden Capture-/Buildermodulen und später an fehlenden Cleanup-/Exec-Übergangspfaden beobachtet. Abschließender gezielter Befehl aus `tools/`:

```sh
python3 -m unittest test_owned_sync_capture test_prepare_owned_sync_capture test_analyze_retail_sync_pcap -v
```

**35/35 PASS, 0,330 s:** 17 neue Library-/Builderfälle plus 18 unveränderte Auditorfälle. Tatsächliche `/proc`-Lesefunktionen werden mit isolierten Dateifixtures geprüft, Exec/Signale/Prozesse mit Mocks. Diese Tests starten keine Capture- oder Spielprozesse und beweisen keine native Capability. Kein Compiler/Frida/tcpdump/Netzwerkmutationsaufruf erfolgte.

Privates deaktiviertes Paket: `/srv/tse-owned-sync018-yodeller-disabled-20261114`, Manifest `4e0a565fde1f040c95dbea89932b6511d6671cee5aa01bf02053dc56fb2a8e35`, 69 Runtimepins. Builder prüft Parent- und Build018-Manifest, tatsächliche DLL und Quell-/Overlaypins; auch Capturebinaries sind gepinnt. Alle drei Codegates bleiben `False`. `owned-capture-parent.diff` und Paket-Handoff sind privat enthalten.

Nächster Schritt: unabhängiger Quell-/Paketreview und neuer Root-Freeze mit exklusiven Ressourcen/Preflight. Danach höchstens ein ausdrücklich gestarteter eigener Versuch; kein Retry oder unbeaufsichtigter Auftrag ist angelegt. Bei Native-Fenster ruhen sämtliche eigenen Tests, Generatoren und Leser. Ein späteres Root-Ergebnis und unabhängige Restoreprüfung fehlen weiterhin.
