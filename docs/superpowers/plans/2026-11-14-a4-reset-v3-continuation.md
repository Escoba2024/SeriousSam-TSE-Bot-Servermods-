# A4-Reset-V3: isolierte Fortsetzung

Root-Auftrag, Basis eb4a8c1. Ausschließlich Offlinearbeit; Root integriert, friert ein und führt native Tests aus. Der fremde pausierte Worktree `/srv/tse-a4-epoch-reset-v3-20261114` bleibt unverändert. Seine vier Dateipins sind separat inventarisiert.

1. Die fehlenden Builder-/Reader-Brücken mit fokussierten Regressionen zunächst rot beobachten. Vorhandene Epochtests übernehmen, keine breite Discovery.
2. Den unveränderten V3-Kern aus Autorenparent a4568cbe… wiederverwenden. Nur dessen Gruppenwrapper von Phase0 auf die bereits vom V2-Kern unterstützten Phasen0/1/2 erweitern. Ein `PhaseReads`-Adapter um genau die drei vorhandenen Inventory-Aufrufstellen legt pro echter Epoche vor dem ersten Read Gruppencontract, Versuchsjournal und Serien fest; kein weiterer nativer Read.
3. Die bestehende018-Rotation und ihre echten Begin1/2/3-, Uhrreset-, Sourceoffset-, persistenten PID-/Start-, Entity-/World- und frühen8→späten9-Registryprüfungen erhalten. Phase1/2 binden zusätzlich die tatsächlich bestätigte `PhaseInventory`-Quittung an Registry/Contract. Gleiche Pointer gelten nicht als Resetbeweis. Die ursprünglichen19/50/480s- und120Wall+Game-Grenzen bleiben bestehen.
4. Die komplette Hard2-Regelprüfung mit ausschließlich phasenabhängigem Zeitlimit2/2/0 an bestehende Sessionreads hängen. Query-Transportleere nur in bisherigen Startup-/Wartezuständen als nicht bereit behandeln; jedes gültige Query weiter strikt Hard.
5. Sämtliche erfolgreichen Gameplayreads einschließlich früher Acht-Bot-Reads müssen im unveränderten geordneten V3-Auditor enthalten sein. Gescheiterte Reads bleiben im begrenzten Journal; Original-Frischspawn-/Erstzustandsschaden und Weaponfunktionscalls bleiben unbewiesen. 24Slotphasen und zwei echte Resets sind das Ziel eines späteren Rootlaufs, kein Ergebnis des Paketbaus.
6. Deaktivierten frischen Fork mit Parent-, Quell-, Overlay-, Runtime- und vollständigen Paketpins bauen. Vorherige Pakete nicht verändern. Fokussierte Negativfälle, unveränderte Sleep/Input-/Readeranzahl und Cleanup nachweisen; Commit und Reviewhandoff. Kein Runtime-/Build-/Live-/Pushschritt.

Terminal-Watchdog: fehlender nativer positiver Fall bleibt separat `NOT_EXERCISED`. Historische FAILs bleiben FAIL. CPU75%, RAM1,5GiB, Disk8GiB und die vorhandenen Ressourcen-/Sync-/Restoregates werden nicht verändert.
