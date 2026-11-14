# Vollständige Hostmessung um einen eigenen Controller

> REQUIRED: executing-plans, TDD und eigene Rootdateiclaims. Bestehende Nativecontroller und ihre Ergebnisse bleiben unverändert.

**Goal:** Die tatsächlich beobachtete47s-Startlücke bei künftigen Tests durch eine unabhängige äußere Messschleife vermeiden.
**Architecture:** Vorhandenes `observe-mapreset-resources.py`-Prinzip wiederverwenden: Root startet genau einen eigenen gepinnten Pythoncontroller und beobachtet ihn bis zum tatsächlichen Ende. Im äußeren Prozess alle1s ausschließlich /proc/stat, MemAvailable und freien Datenträger lesen; keine Threads, weiteren Dienste oder Eingriffe in Spielprozesse. Der native Controller behält seine eigenen Abbruch-, Lock-, Cleanup- und Restorepflichten.
**Tech Stack:** Pythonstandardbibliothek, unverändert übernommene bestehende HostBudget-Auswertung.
**Spec:** A5/B-Ressourcenauftrag: mindestens25Prozent CPUreserve,1,5GiB verfügbarer RAM,8GiB frei; keine Umwertung alter Messlücken.

## Entscheidungen und Grenzen

Rootentscheidung innerhalb des ausdrücklich autonomen Auftrags: äußere Beobachtung
statt neuem Thread/IPC im Nativecontroller. Sie nutzt die vorhandene eigene
Popen-/Wartehülle und verändert keine Gameplaybedingungen. Ein Thread würde
neue Lifecycle-/Sperrpfade im bisher geprüften Controller schaffen.

- Nur neue Rootdateien `tools/observe_owned_host_budget.py`,
  `tools/test_observe_owned_host_budget.py`, Reviewregressionen
  `tools/test_owned_host_journal_failure.py` und bytegleiche Veröffentlichung der
  vorhandenen `host_budget.py`; keine bestehenden Agentendateien beanspruchen.
- Vor und nach Spawn identischer vollständiger SHA des ausdrücklich übergebenen
  eigenen Pythonquellpfads; private neue0700/O_EXCL-Evidence, PIDstartgeneration.
- Vor Spawn ein Hostbaselinewert, nach tatsächlichem Exit ein Endwert; alle
  übrigen Samples Zielabstand1s. Keine Clockinterpolation/Peakbehauptung.
- CPU/RAM/Diskgrenzen bleiben exakt75Prozent/1610612736/8589934592Bytes.
- Messfehler/Verletzungen sticky erhalten, bis der eigene Controller selbst
  beendet ist; die Messhülle killt keine Spiel-, Helper- oder Parentprozesse.
- Keine automatische Neuauflage; Rückgabestatus getrennt von nativer Abnahme.
  Keine Overall-/Stabilitäts-/Budgetqualifikation allein aus beobachteten Werten.
- Nativecontroller darf seinen eigenen Lifecycle nicht an diese reine Beobachtung
  delegieren. Keine allgemeine Remoteausführungs-/Kontrollschnittstelle.

## Aufgaben

- [x] Vorhandenen HostBudget-Quellhash und Wrapperprinzip frisch prüfen.
- [x] RED: neuer Observer fehlt; echte eigene kurzlebige Pythonquelle muss vom
  Baselinewert bis nach Exit beobachtet werden, während der Hauptpfad blockiert.
- [x] RED: falscher Pin startet keinen Child; nichtneues Ziel wird nicht
  überschrieben; Verletzung und fehlgeschlagener Child werden nicht PASS;
  gemessene Ressourcenfehler bleiben trotz späterer guter Samples erhalten.
- [x] Minimalen Observer implementieren: `observe(source:Path, expected_sha:str,
  directory:Path) -> dict`, nur Pythonquelle ohne Argumente, kein Shellstart.
  Bestehende HostBudgetklasse bytegleich verwenden, Fehlerjournal erhalten.
- [x] Gezielt GREEN, bestehende Budgettests begrenzt übernehmen; tatsächlicher
  eigener Child-/PID-/Log-/Reapbeleg ohne Xserver/TSE/Wine/Frida.
- [x] Unabhängig reviewen; Root erst danach vor künftiger Nativequalifikation
  einsetzen. Alte Resultate/Controller/PASSflags bleiben unberührt.

Reviewfokus: Baseline vorChild, Endprobe nachExit, PIDreuse, nach Spawn veränderter
Quellpfad, Popenfehler, Hostlesefehler/CPUverletzung, neue Ausgabepfade und kein
versehentliches Prozesssignal. Keine neue Lücken-/Budgettoleranz einführen.

EineReviewfixrunde190be3e nach echtemRED,13/13PASS. ErsterNativeeinsatzweiteroffen.
