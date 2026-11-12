# Build017: längerer Red-Station-Resettest

Stand: 12.11.2026 18:11:36 CET.

**Begrenzt bestanden: alle 24 Slotphasen erfüllen die unveränderten Aktivitätsanforderungen.** Das neue Fenster `165124` beobachtete tatsächlich 423.836349 Sekunden, durchlief zwei normale Neustarts derselben Red-Station-Karte und endete mit normalem Schließen sämtlicher Rollen sowie exakt geprüftem Dateirestore. Es ist keine vollständige A4- oder Releaseabnahme.

## Vorab festgelegter Versuch

Die unveränderte Build017-DLL lief mit derselben Navigation, denselben Profilen, Seeds und Waffenregeln. Die beiden ersten Runden hatten je zwei Minuten Zeitlimit; die dritte Runde mindestens 120 Sekunden Echtzeit und Spielzeit. Die Beobachtung war vorab auf 480 Sekunden begrenzt. Alle fünf Aktivitätsfelder je Slotphase sowie zusätzliche Respawn-, Score- und Fremdkillbedingungen blieben erhalten. Es gab keinen erfolgsabhängigen Abbruch, keine automatische Wiederholung und keine nachträgliche Wertung des Cleanup-Tails.

Das Prüfprogramm wurde unabhängig geprüft: 65 gezielte Autorenprüfungen und zehn ergänzende Gegenfälle an den tatsächlichen Abschlussanweisungen. Ein reproduzierter veralteter Abschlusszeitwert wurde durch dieselbe vorhandene Zeit-/Identitätsprüfung an den betroffenen Grenzen geschlossen. Die bisherigen Schutzgrenzen und alle übrigen Runtime-Dateien blieben erhalten.

## Vollständige Lebensnenner

| Runde | Vollständige Slotphasen | Beobachtete Botleben | Beobachtete HP-Tode | Leben mit beobachteter nützlicher Waffenaufnahme | Native Fernfeuerproben |
| --- | ---: | ---: | ---: | ---: | ---: |
| 1 | 8/8 | 54 | 46 | 19 | 580 |
| 2 | 8/8 | 61 | 53 | 16 | 468 |
| 3 | 8/8 | 63 | 56 | 20 | 515 |

Alle **178 Leben**, auch kurze, gestorbene und am Rand unvollständig beobachtete Leben, bleiben in den privaten Originaldaten erhalten. Die Feuerwerte sind wiederholte Zustandsproben, keine Zahl unabhängiger Schüsse oder Treffer. Die Auswertung aller Erwerbszeiten und der längeren erfolglosen Lebensabschnitte läuft separat. Dass alle Slots innerhalb einer längeren festen Beobachtung aktiv wurden, beweist keine neue Verbesserung des unveränderten Gameplays.

## Abschluss und Ressourcen

Vier Rollen wurden normal geschlossen. Root prüfte danach alle vier Labverzeichnisse auf tatsächliche Prozessfreiheit, beide Displays auf Abwesenheit, vier geschlossene Logdateien erneut per Hash sowie **643 wiederhergestellte Dateien und fünf wieder abwesende Pfade**. Keine Fehler und keine abschließenden Ablehnungsgründe. Der Wrapper endete mit Exit 0 nach 488,69 Sekunden einschließlich Start und Cleanup.

Höchster gemessener CPU-Intervallwert: 57,3201 %. Kleinster beobachteter verfügbarer RAM: 1.894.895.616 Bytes; freier Speicher: 14.925.201.408 Bytes. Größte Abtastlücke während des Spiels: 2,3703 Sekunden, einschließlich Start 47,4961 Sekunden. Diese Intervallwerte beweisen keine ungemessenen Spitzen oder Langzeitstabilität; `budget_pass_claim` bleibt false.

## Grenzen und nächste Arbeit

Die früheren 300-Sekunden-Protokolle behalten ihre FAIL-Ergebnisse. Der längere Folgeversuch ersetzt sie nicht rückwirkend. Die vorherige Analyse ordnete 18 Waffenzielverluste konkurrierenden Aufnahmen zu; sie bewies keine optimale Waffenbeschaffung und isolierte keinen zu reparierenden Source- oder NAVdefekt.

Dieser neue Befund betrifft Red → Red → Red. Ein Wechsel auf eine andere Karte und zurück, die vollständige Navigations-/Gefahrenabnahme, übrige Cecil-Karten und die Produktions-Whitelist bleiben offen. Der Originalobserver wurde an den vorgesehenen Grenzen normal neu gestartet; dies ist kein bestandener automatischer Vanilla-Rejoin. Die globalen Felder `functional_pass`, `map_reset_proven`, `original_auto_rejoin_proven` und `qualified` bleiben entsprechend false.

Parallel beginnen die unabhängig geprüften Build017-Vergleiche mit der bisherigen öffentlichen DLL: ein uninstrumentierter Kontrolllauf, anschließend MITTEL/STARK/DEMON mit beiden Startbelegungen, jeweils 120 Sekunden. Die ebenfalls unabhängig geprüfte normale Colt-Vorbereitung bleibt ein separater A1-Schritt und keine First-State-Abnahme.

[Maschinenlesbare Zusammenfassung](milestone-a-20261112/a4-build017-extended-reset.json). Private Originale: `/srv/tse-milestone-a-evidence-20261111/a4-reset017-extended-20261112-165124`; Root-Postflight: `/srv/tse-milestone-a-continuation-evidence-20261112/a4-build017-extended-root-postflight.json`.
