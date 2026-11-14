# A3: bestehende Schadensfenster getrennt geprüft

Status: **OFFLINE_COMPONENT_AUDIT**, keine A3-/Stärkefreigabe. Claim `a4_diagnosis`, Branch `codex/20261114-a3-partial-damage-audit` ab Root `24766e5`. Implementiert den [geprüften Plan](../superpowers/plans/2026-11-14-a3-partial-inventory-damage-audit.md). Keine neue Native-, Frida-, Display- oder Netzwerkaktion, kein Retail-/DLL-Build und keine neue Agentendelegation. Root allein integriert und veröffentlicht.

## Ergebnis vorhandener Rawbelege

Beide bereits geschlossenen 120-Sekunden-Fenster bestehen die vollständigen unveränderten Damage-/Attributions-/Lethal-/Serverkillprüfungen, Originalbyte-/Close-/Restore-/Initial-/Config-/PID-/Hard-/Hostvoraussetzungen. Die konditionsbezogenen Hashes sind identisch: `9b9fd8b3854f510784d70280e913629ff21fcd62adf268ddcffc1a6984f76ffd`. Das behebt keinen historischen Analyzer-Fail und behauptet keine vollständige Waffenversorgungsbilanz.

| Vorhandenes Fenster | Neuer Komponentenstatus | Damage-Records | Known-Foreign / Corpse / Self / Unattributed / Outside | Beobachtete Botleben | Unbeobachtete Sourceleben |
|---|---|---:|---|---:|---:|
| pair12/swap0,154843 | CLOSED_DAMAGE_COMPONENT_ONLY | 244 | 136 / 93 / 10 / 5 / 0 | 32 | 0 |
| pair12/swap1,155849 | PARTIAL_INVENTORY_REPORT | 207 | 95 / 98 / 6 / 8 / 0 | 25 | 1 UNKNOWN |

Das einzige nicht beobachtete Sourceleben ist botA/local1, Generation9, Clientlogzeile1891/Driver-Tick2614. Sein Server-Spawnclock, seine Zugehörigkeit zum Gameplayfenster, seine Versorgung und seine Dauer bleiben `null/UNKNOWN`; es geht in keinen Lebens-/Versorgungsnenner ein. Das vollständige gemeinsame Lebensprefix und der einzelne offene letzte Sourcezyklus bestehen den strikten Zähler-/Generation-/Entity-/Death-/Pickupabgleich. Die beiden tatsächlich beobachteten abgeschlossenen local1-Leben ohne brauchbaren Waffenbesitz bleiben negativ.

Die bereits vorhandenen direkten Schadensbeobachtungen sind nicht einheitlich zugunsten derselben Stufe:

| Swap | STARK→MITTEL: lethal / an Vor-Treffer-HP begrenzter Schaden | MITTEL→STARK: lethal / begrenzter Schaden |
|---|---|---|
| 0 | 13 / 1482.9115600585938 | 3 / 304.33132553100586 |
| 1 | 5 / 817.6288146972656 | 6 / 542.9914245605469 |

Insbesondere hat STARK im zweiten Fenster weniger direkte tödliche Treffer verursacht. **Keine Aussage „STARK hat beide Fenster gewonnen“** und kein allgemeiner Stärkenachweis. Die Daten gelten für die aufgezeichneten zwei kurzen MITTEL/STARK-Bedingungen mit stationärem Originalclient. DEMON-Vergleich, menschliches Niveau, Dauerstabilität und vollständige Versorgung sind damit nicht abgeschlossen.

## Erhaltene Prüfungen und neuer Berichtstyp

`a3_closed_damage_components.py` lädt ausschließlich die hashgepinnte historische eigene Pythonquelle `analyze-direct020.py` (`4187020d0ceda1284bcaac3df9ccf98b251ec25863ae6947bd0aa6d96d33464a`). Sechs Prüfkörper werden ohne geänderte AST-Knoten in Funktionen mit expliziten Eingaben und Rückgaben abgeleitet: Preconditions/Initial, beobachtete Memoryleben, bestehender einzelner Lebensabgleich, vollständiger Damage-/Serverkillblock, Host/Kosten und identische Bedingungen. Nur diese bekannte eigene Quelle wird als Offline-Python kompiliert; Logs und Evidencewerte werden nie als Code ausgeführt. Zusätzlich sind sämtliche tatsächlich importierten Policyhilfen, Controller-/Worker-/Collector-/Hookquellen und das konkrete Parentmanifest gepinnt. Die alten Dateien `analyze-direct020.py`, `a3_compare_direct_closed.py`, Nativecontroller und Hooks bleiben bytegleich.

Die neue `a3_partial_inventory.py` erlaubt ausschließlich einen belegten offenen letzten Sourcezyklus nach einem vollständigen beobachteten Lebensprefix. Fehlende innere Lebenszyklen, mehrere Zusatzspawns, abgeschlossene unbeobachtete Zyklen, Zähler-/Generation-/Entity-/Slot-/PID-/Clockwidersprüche und unpassende Death-/Pickupevidenz bleiben FAIL. Ein unbekannter Suffix wird nicht abgeschnitten oder als Erfolg/Null ergänzt. Bei fehlerhafter Lebensrekonstruktion bleibt der Gesamtbericht `FAIL_INVENTORY_RECONCILIATION`; eine unabhängig bestandene Schadenskomponente kann darin separat erhalten bleiben.

`audit_a3_closed_damage_partial.py` erzeugt ein eigenes `SSAM_A3_CLOSED_DAMAGE_COMPONENT_V1` mit `damage_component`/`inventory_component`. Pflichtflags bleiben `qualified=false`, `a3_accepted=false`, `tier_strength_accepted=false`, `closed_compare_eligible=false`. Keine Legacy-Top-Levelstruktur `damage`, `lives` oder `direct_condition_sha256`; Übergabe an den alten Vollvergleich scheitert im Test. Ausgaben werden exklusiv neu angelegt und können alte Raw-/Result-/FAIL-Dateien nicht überschreiben. Der neue gemeinsame Eingang verlangt außerdem ausdrücklich alle vier tatsächlichen Schlusslogeinträge; dies ergänzt die konkrete Vierrollenbehauptung, ohne den übernommenen Prüfblock zu ändern. Unbekannte Source-locals werden vor jeder Filterung abgewiesen. Jeder Bericht bindet auch die drei neuen Toolquellen über ihre SHA256.

## Prüfung und reproduzierbare Artefakte

RED zuerst bei fehlendem Auditor/Extraktor/Suffixvalidator; danach GREEN mit synthetischen geschlossenen Dateifixtures. Der zusätzliche Vier-Schlusslogs-Gegenfall zeigte konkret RED (fehlender Eintrag wurde noch akzeptiert), dann GREEN mit striktem Eingangsgate. AST-Gleichheit wird **unabhängig anhand der gepinnten historischen Quellzeilenspannen** geprüft, nicht nur gegen die Produktions-Extraktionsfunktion selbst. Gegenfälle verändern echte Fixturedateien und durchlaufen die übernommenen Originalchecks: Restore/Closes, Initialreferenz, Hardquery, Registry/Pointer/PID/Slot, Damagefolge/-Leben/-Tick/NaN, Zeitfenster, Attribution, Serverkills, Ressourcen sowie die Lebens-/Source-Innenlücken. Tests starten keine Spiel-/Fridaprozesse.

```sh
cd tools
env TSE_A3_DIRECT_PACKAGE=/srv/tse-a3-instruction-probe-root-frozen-20261114 python3 -m unittest test_a3_partial_damage_audit test_a3_direct_tiers test_a3_direct_compare_closed test_a3_direct_closed_fixture test_a3_direct_behavior -v
```

**31/31 PASS,2.148s**, keine Skips: 17 neue Methoden mit adversarialen Unterfällen plus14 bestehende strikte Kohorten-/Vollvergleichs-/Analyzer-/Verhaltensprüfungen. Ein weiterer konkreter RED→GREEN-Gegenfall sichert ab, dass Source-locals außerhalb0..3 nicht stillschweigend herausgefiltert werden; auch die neue Toolquellbindung wurde vor Ergänzung als fehlend belegt. Die beiden realen Archive wurden anschließend ausschließlich offline neu gelesen; keine neue tatsächliche Spielsituation wurde erzeugt.

Privates Autoren-Reviewpaket `/srv/tse-a3-partial-damage-audit-reviewed-final-20261114`, Manifest `6f0a36b103c6c6d5d8e67a4a7c87fe081ee1a4abc41f0336ca2f2e7de8204d2a`, neun frisch geprüfte Artefaktpins einschließlich fünf Quell-/Testdateien, lesbarer abgeleiteter Prüfkörper, AST-Zeuge und zweier Komponentenberichte. Die Rohlogs/Spieleridentitäten wurden nicht veröffentlicht. Ergebnisdateien:

- swap0-Bericht SHA256 `d0d8a2e3f90ae81f4325b998eb15facaed4b87a0f62e1295c6cc82dcb1fbef13`.
- swap1-Bericht SHA256 `57659d0d40a4f1b9cbf023981ca6152570fb9341299c670faf47d9366bb8e3c0`.

Reproduktion aus dem Repository, jeweils mit einem **neuen** Ausgabepfad:

```sh
python3 tools/audit_a3_closed_damage_partial.py /srv/tse-milestone-a-evidence-20261111/direct020-hard-probe-root-pair12-swap1-20261114-155849 --output /private/new-partial-report.json
```

Grenze: Die Fehlbehauptung identischer Lebensmengen ist im neuen Bericht aufgehoben, die fehlende Lebensbeobachtung selbst bleibt fehlend. Alter Analyzer-Fail und alte Vollvergleichsartefakte bleiben erhalten. Rootreview ist noch offen; daraus folgt kein neuer Runtimeauftrag und keine automatische Wiederholung bereits vorhandener nativer Fenster.
