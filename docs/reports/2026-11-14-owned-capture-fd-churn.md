# Capture-FD-Churn: enger Offlinefix

Status: **OFFLINE_FIX_ONLY**, keine neue Runtime- oder Syncabnahme. Claim `a4_diagnosis`, Branch `codex/20261114-owned-capture-fd-churn` ab Rootplan `7fd2180`. Root allein integriert und verändert Runtime; frühere Resetarbeiten bleiben erhalten.

## Ausgang und belegte Ursache

Der geschlossene eigene Lauf150433 bleibt **FAIL**, Result `75eb5fa3333f7962463f58df98030336f3e5538e038094689b20f14cd783880e`. Einer der zwei vorhandenen `/proc/PID/fd`-Scans listete einen Deskriptor, der beim folgenden `readlink` bereits geschlossen war. Eine Liste von FD-Namen garantiert deren fortdauernde Existenz nicht; dies belegt keinen Rollencrash.

Root meldete normales Captureende Exit0, 58088 Pakete, 0 Drops sowie für alle drei Rollenpaare je456 passende beobachtete Syncchecks ohne Unterschiede/fehlende/unsupported/fragmentierte/konfliktierende Paare. Das sind begrenzte Paketevidenzen; der Versuch erreichte seine vollständigen600Sekunden nicht und wird nicht umetikettiert. Alle vier Rollen wurden normal geschlossen, Root640Dateien/4Schlusslogs/Metadaten/PIDs/DisplayRestore bestanden. Diese Rohbelege und alten Freezes bleiben unverändert privat.

## Änderung und Fail-closed-Grenze

Die einzige geänderte Runtimefunktion bleibt `observe_roles`: ausschließlich `FileNotFoundError` beim einzelnen bereits vorgesehenen `readlink` in jedem der zwei vorhandenen Scans wird übersprungen. Es gibt weder einen weiteren Scan noch Retry, zusätzlichen Prozessread, Sleep oder Rebaseline. Alle anderen Fehler bleiben hart. UDP-Parsing, vollständige Port-/Socketinode-/PID-/Start-/CWD-/Cgroup-/Namespacebindung, JSON-Vergleich, Capture-/Host-/Gameplaygrenzen, Eingaben und Rollenclose bleiben unverändert.

Ein im ersten Scan verschwundener erwarteter UDP-FD führt weiterhin zur fehlenden Rollenportbindung. Im zweiten Scan fehlt sein bereits ausgewählter Inode und der unveränderte Gegencheck scheitert. Ein ersetzter noch existierender UDP-Inode beziehungsweise ein geänderter Port wird spätestens im vollständigen erwarteten Bindungsvergleich vor Exec abgewiesen. Diese Korrektur löst einen Beobachtungsfehler, nicht die unbekannte Ursache öffentlicher Syncabweichungen.

## RED→GREEN und Paket

Zwei neue Tests führten den tatsächlichen FD-/UDP-Fixturleser aus und löschten einen aufgelisteten Nicht-UDP-FD unmittelbar vor dem ersten beziehungsweise zweiten `readlink`. Beide lieferten vor Änderung den erwarteten `FileNotFoundError` an FD46. Nach Änderung bleibt die vollständige Bindung identisch; die Tests zählen weiterhin exakt zwei vorhandene Scans. Gegenfälle für verschwundenen UDP-FD in beiden Scans, tatsächliche Port-/Inode-/PID-/Namespaceänderungen sowie PermissionError und sonstigen OSError bleiben FAIL vor Exec.

```sh
cd tools
python3 -m unittest test_owned_sync_capture test_prepare_owned_sync_capture test_analyze_retail_sync_pcap test_prepare_owned_capture_json_binding test_owned_capture_fd_churn test_prepare_owned_capture_fd_churn -v
```

**48/48 PASS, 0,605 s:** bisherige37Fälle, neun FD-Gegenfälle, ein neues Paketgate und ein zusätzliches historisches Builder-Ablehnungsgate. Der ursprüngliche JSON-Builder bleibt absichtlich auf seine damalige Einzeilenänderung begrenzt: sein historischer Pakettest liest nun ausdrücklich den unveränderten JSON-Autorenstand, während ein zusätzlicher Test seine Ablehnung weiterer Runtimeänderungen belegt. Der neue FD-Builder prüft exakt seine eigenen beiden readlink-Catches gegen diesen Parent. Keine breite Discovery, Compiler, Frida, tcpdump, Runtime-/Display-/Netzwerkaktionen.

Neuer deaktivierter Fork `/srv/tse-owned-sync018-fd-churn-disabled-20261114` aus JSON-Autorenmanifest `dbf38d5df34c33831342209f767fdf28bfac58b1561dc24ee26dde17466e9fb8`. Manifest `3c30151507cf336cd3e23522828de5f3392552f594334e7bb61841846b13851d`, 69 Runtime-/62 Source-/41 Pythonpins. Gegenüber diesem Parent ändert sich ausschließlich die Library und es kommt eine Offline-Regressionsdatei hinzu; alle anderen vorhandenen Payloads sind bytegleich. Der private `HANDOFF-capture.json` enthält dieselben Pins. Drei Ausführungsgates und sämtliche Qualifikationsflags bleiben False. Neue Runtimefreigabe wird dadurch nicht erteilt.

Nächster Schritt: unabhängiger enger Quell-/Paketreview. Root entscheidet einen gesondert begründeten nächsten Diagnoseversuch; **keine automatische weitere600s-Wiederholung**. Keine unbeaufsichtigte Arbeit läuft.

## Optionales späteres eigenes Latenzexperiment – nur Design

Vor einem getrennten Netemversuch müssten Root und ein geprüfter Controller die eigenen NetNS-Inode-/PID-/Start-/Veth-/Interfacezuordnungen unmittelbar frisch binden, alle fremden/Hostinterfaces ausschließen und die tatsächliche Capability in einem eigenen Wegwerfnamespace qualifizieren. Werkzeugpräsenz ist dafür kein Nachweis. Baseline-qdisc und bestehende Filter müssten vollständig privat erfasst und exakte Wiederherstellung samt Gegenprüfung belegt werden; keine pauschale Root-qdisc-Löschung oder Hoständerung. Ein endlicher, exklusiv gesperrter Controller müsste Timeout/Signal/Teilstart unabhängig zurücknehmen können und Cleanupfehler dauerhaft FAIL halten. Kontroll- und Latenzbedingungen müssten vor Ergebnissen feststehen, denselben Kandidaten/Own-Rollenbestand verwenden und alle Paket-/Ressourcen-/Gameplaygates behalten. Erst ein gesonderter Plan könnte das autorisieren und die feste Eingriffsgrenze bestimmen. Ein solcher Test wäre ausschließlich ein eigener simulierter Latenzfall und keine WAN-/Stabilitätsabnahme. Für diesen Entwurf wurden keine `tc`-/`unshare`-/Netzaufrufe ausgeführt.
