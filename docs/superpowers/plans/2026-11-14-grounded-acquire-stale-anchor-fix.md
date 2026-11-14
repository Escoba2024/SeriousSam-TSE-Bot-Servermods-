# GroundedReplan: frischen Hint nach veraltetem Acquire-Anker übernehmen

> Ausführung durch a4_diagnosis mit executing-plans, TDD und verification-before-completion. Keine Delegation.

**Goal:** Den belegten falschen `unreachable_hold`-Abbruch verhindern, wenn nach ausgefallenem Scan ein aktuell gültiger Bodenhint vom gehaltenen hohen Anker abweicht.

**Architecture:** Bestehenden `BotCecilGroundedReplan` minimal ändern: Anker-Gleichheit nicht mehr als separate alte Hintbedingung verlangen. Sämtliche frischen Eligibility-/Support-/Geschwindigkeits-/Höhen-/LOS-/Graphprüfungen bleiben erhalten. Erst nach erfolgreicher Reachabilityprüfung wird der Anker zusammen mit dem bestehenden Navigatorreset übernommen. Keine neue Zustandsmaschine.

**Tech Stack:** Tatsächliche Produktionskörper im vorhandenen SDK107-C++14-Brückenharness, normale und ASan/UBSan-Portableprüfungen.

**Spec:** Rootfreigabe; `docs/reports/2026-11-14-grounded-acquire-handshake-sdk107-repro.md` mit 3274 Checks/2 RED. Nativeursache weiterhin unbewiesen.

## Grenzen und Reviewfokus

- Source-/Hopidentität, Locks, Specials, Gravity, WorldBase-/Entityidentität, Speed, Höhe, LOS, Rayreserve und gerichtete Erreichbarkeit unverändert.
- Kandidat erst bei erfolgreichem Replan übernehmen; fehlgeschlagener frischer Check darf den gehaltenen Anker nicht ändern.
- Kein `acquiredAnchor`-/Zeitstempel, synthetisches Reached, Floorstempel, Radius-, Holdzeit- oder Zieldeadlinegrant.
- Bestehender Fall18 der alten Guardmatrix erwartete noch das abgelöste pauschale Staleanchor-Veto. Ihn ausdrücklich als positiven Staleanchor-Fall führen; die übrigen Guardfälle erhalten. Neue Retainedanchor-Vetos getrennt ergänzen.
- Kein DLL-/Native-/Deployvorgang und kein Stärke-/A4-/Retail-PASS. Nur zukünftiger Kandidatenquellstand.

## Aufgaben

- [x] Ausgangszustand 3274/2 RED erneut nachweisen.
- [x] Vor Produktionsänderung zusätzliche echte adversariale Guardfälle mit behaltenem hohen Anker schreiben: aktueller Block/Lock/LOS/Budget/Support/Velocity/Graph-/Kontextverlust bleibt Veto und unveränderter Anker.
- [x] Erfolgsfälle prüfen: frischer Anker wird erst bei echtem Reset gesetzt, keine synthetischen Acquisition-/Floorwerte; ursprünglicher Radius bleibt Voraussetzung für nächsten Edgefortschritt.
- [x] Minimalen Quellfix implementieren und normale vollständige SDK107-Brücke GREEN führen.
- [x] Relevante Parent-/Header-/SDK-Prüfungen und vollständige SDK-Brücke ASan/UBSan seriell ausführen; keine breite neue Testschleife.
- [x] Quell-/Testdiff, RED/GREEN, genaue Pins/Kommandos/Grenzen dokumentieren, sauber committen, Jobs beendet melden.

Abschluss: ursprünglicher3274/2RED, erweiterter3431/5RED; final3440/0normal
undASan/UBSan sowie12C++/4Python-ParentprüfungenPASS. ZwischenFAIL3435/1
als alterAnchorproxyFall25 identifiziert und erhalten; legitimerAlternativhint
positiv plus tatsächlichesAllHints-Höhenveto. Nativeursache weiterhin unbewiesen.
